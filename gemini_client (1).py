"""Backend: loads the key from .env and asks Gemini for a structured JSON analysis."""
import json, os, re, time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # reads .env — the key never appears in code or the UI


class GeminiError(Exception):
    pass


SYSTEM_PROMPT = """You are AlgoShastra, a senior competitive-programming coach and C++ performance engineer.
Given brute-force C++ code you must:
1. Determine the exact time and space complexity of the ORIGINAL code (Big-O, in terms of the input variables).
2. Find real bugs and edge cases: overflow, out-of-bounds, empty input, duplicates, negative numbers, uninitialised variables, UB.
3. Write the best practical optimized C++17 solution (right data structure / algorithm, e.g. hash map, two pointers, DP, sorting, binary search, heap).
   It must keep the same function signature and behaviour, compile without errors, and include brief comments.
4. State the optimized code's complexity, and explain the key insight in plain language.
5. Test harness. If the ORIGINAL code has NO main(): "harness" must be a C++ `int main(int argc, char** argv)` that reads
   n = argc>1 ? atoi(argv[1]) : 100, builds a deterministic valid input of size n (fixed-seed mt19937) that is the WORST CASE for the brute-force version (e.g. the only valid answer sits at the very end, or none exists), so timing differences are visible,
   calls the function by its exact name, and prints ONE line that is identical for every correct answer (a validity check or checksum,
   never raw indices when several answers are valid). Then neither "optimized_code" nor the original may contain main().
   If the original already has main(), set "harness" to "" and keep main() in "optimized_code" with identical output.
Respond with ONLY a JSON object, no markdown fences, matching exactly this schema:
{
  "problem": "one-line description of what the code does",
  "original":  {"time": "O(...)", "space": "O(...)", "explanation": "why"},
  "optimized": {"time": "O(...)", "space": "O(...)", "explanation": "why"},
  "technique": "short name, e.g. Hash Map, Two Pointers",
  "bugs": [{"severity": "high|medium|low", "title": "short", "detail": "what breaks and when"}],
  "logic": "step-by-step reasoning (3-6 sentences) of how the optimization works",
  "optimized_code": "complete C++ source as a single string",
  "harness": "C++ main() for testing, or empty string"
}
If the input is not valid C++ or not an algorithm, still return the schema, put the issue in "bugs", and return the code unchanged."""


def _client() -> genai.Client:
    key = os.getenv("GEMINI_API_KEY")
    if not key or key == "your_key_here":
        raise GeminiError("GEMINI_API_KEY is missing. Copy .env.example to .env and add your key.")
    return genai.Client(api_key=key)


RETRY_WORDS = ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "overloaded", "high demand")


def _call(client, model: str, prompt: str) -> str:
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    return resp.text or ""


def analyze_code(cpp_code: str) -> dict:
    prompt = f"Analyze and optimize this C++ code:\n\n```cpp\n{cpp_code}\n```"
    client = _client()  # keep a reference so it is not closed early
    models = [os.getenv("GEMINI_MODEL", "gemini-3.8-flash")]
    if os.getenv("GEMINI_FALLBACK_MODEL"):
        models.append(os.getenv("GEMINI_FALLBACK_MODEL"))

    text, last_err = None, None
    for model in models:
        for attempt in range(4):  # retry busy-server errors with backoff: 2s, 4s, 8s
            try:
                text = _call(client, model, prompt)
                break
            except Exception as e:
                last_err = e
                if not any(w in str(e) for w in RETRY_WORDS):
                    raise GeminiError(f"Gemini API error: {e}")
                time.sleep(2 ** (attempt + 1))
        if text is not None:
            break
    if text is None:
        raise GeminiError(f"Gemini is busy right now. Please try again in a minute. ({last_err})")

    try:
        data = json.loads(re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip())
    except json.JSONDecodeError:
        raise GeminiError("Gemini returned malformed JSON. Please try again.")
    for k in ("original", "optimized", "bugs", "logic", "optimized_code"):
        if k not in data:
            raise GeminiError(f"Response is missing '{k}'. Please try again.")
    return data
