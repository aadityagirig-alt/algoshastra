"""AlgoShastra: C++ DSA Optimizer — run with: streamlit run app.py"""
import html
import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import CppLexer
from pygments.styles import get_all_styles, get_style_by_name

from gemini_client import GeminiError, analyze_code
try:
    from report import build_pdf
except ImportError:  # reportlab not installed yet
    build_pdf = None
from verify import have_gpp, verify_and_benchmark
from styles import LOGO_SVG, THEMES, build_css

st.set_page_config(page_title="AlgoShastra", page_icon="🛡️", layout="wide")

SAMPLE = """#include <vector>
using namespace std;

// Two Sum — brute force
vector<int> twoSum(vector<int>& nums, int target) {
    for (int i = 0; i < nums.size(); i++) {
        for (int j = i + 1; j < nums.size(); j++) {
            if (nums[i] + nums[j] == target) return {i, j};
        }
    }
    return {};
}
"""
SYNTAX = [s for s in ["dracula", "monokai", "github-dark", "one-dark", "solarized-dark", "nord", "default"] if s in set(get_all_styles())]
SEV = {"high": "#ef4444", "medium": "#f59e0b", "low": "#38bdf8"}

st.session_state.setdefault("theme", "Dark")
st.session_state.setdefault("syntax", "dracula")
st.session_state.setdefault("font", 14)
st.session_state.setdefault("code", SAMPLE)

# ---------- header + customize ----------
left, right = st.columns([6, 1.3])
with left:
    st.markdown(f'<div class="brand">{LOGO_SVG}<div><b>AlgoShastra</b><small>C++ DSA Optimizer · brute force in, optimal out</small></div></div>', unsafe_allow_html=True)
with right:
    with st.popover("⚙️ Customize", use_container_width=True):
        st.selectbox("UI theme", list(THEMES), key="theme")
        st.selectbox("Code highlighting", SYNTAX, key="syntax")
        st.slider("Editor font size (px)", 11, 22, key="font")

theme = THEMES[st.session_state.theme]
st.markdown(build_css(theme, st.session_state.font), unsafe_allow_html=True)


def code_box(code: str) -> str:
    style = get_style_by_name(st.session_state.syntax)
    body = highlight(code, CppLexer(), HtmlFormatter(style=st.session_state.syntax, noclasses=True))
    return f'<div class="codebox" style="background:{style.background_color};font-size:{st.session_state.font}px">{body}</div>'


def metric(icon, label, value, note, color):
    return f'<div class="metric" style="--c:{color}"><div class="k">{icon} {label}</div><div class="v">{html.escape(value)}</div><div class="n">{html.escape(note)}</div></div>'


def copy_button(code: str):
    """One-click copy of the whole optimized code (clipboard API with a fallback)."""
    payload = json.dumps(code).replace("</", "<\\/")
    components.html(
        f"""<style>body{{margin:0}}button{{width:100%;height:42px;border:0;border-radius:12px;font:600 14px sans-serif;color:#fff;cursor:pointer;background:linear-gradient(110deg,{theme['a1']},{theme['a2']});box-shadow:0 6px 20px -8px {theme['a1']}}}button:active{{transform:scale(.98)}}</style>
<button id="b">📋 Copy optimized code</button>
<script>const code={payload};const b=document.getElementById("b");
function fb(){{const t=document.createElement("textarea");t.value=code;document.body.appendChild(t);t.select();document.execCommand("copy");t.remove();}}
b.onclick=async()=>{{try{{await navigator.clipboard.writeText(code);}}catch(e){{fb();}}b.textContent="✅ Copied!";setTimeout(()=>b.textContent="📋 Copy optimized code",1800);}};</script>""",
        height=46,
    )


# ---------- split editor ----------
st.write("")
c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown('<div class="ptitle"><span class="dot"></span>Original code</div>', unsafe_allow_html=True)
    st.text_area("Original C++", key="code", height=420, label_visibility="collapsed")
result = st.session_state.get("result")
with c2:
    st.markdown('<div class="ptitle"><span class="dot" style="background:#a855f7;box-shadow:0 0 10px #a855f7"></span>Optimized code</div>', unsafe_allow_html=True)
    slot = st.empty()
    if result:
        slot.html(code_box(result["optimized_code"]))
        copy_button(result["optimized_code"])
    else:
        slot.html(code_box("// Your optimized solution appears here.\n// Paste brute-force C++ on the left, then press Analyze & Optimize."))

st.write("")
go = st.button("✨ Analyze & Optimize", type="primary", use_container_width=True)

if go:
    code = st.session_state.code.strip()
    if not code:
        st.warning("Paste some C++ code first.")
    elif len(code) > 12000:
        st.warning("Code is too long. Keep it under 12,000 characters.")
    else:
        ph = st.empty()
        ph.markdown('<div class="loader"><b>🛡️ Analyzing complexity, hunting bugs, optimizing…</b><div class="bar"></div></div>', unsafe_allow_html=True)
        try:
            res = analyze_code(code)
            res["_original"] = code
            st.session_state.result = res
            st.session_state.pop("bench", None)
            st.session_state.setdefault("history", []).append(res)
        except GeminiError as e:
            st.session_state.pop("result", None)
            ph.empty()
            st.error(str(e))
        else:
            st.rerun()

# ---------- results ----------
if result:
    o, n = result["original"], result["optimized"]
    st.markdown(f'<div class="sec">📊 Complexity report <span class="chip">{html.escape(result.get("technique", "Optimized"))}</span></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cards = [
        ("⏱️", "Time · original", o["time"], o.get("explanation", ""), "#f43f5e"),
        ("⚡", "Time · optimized", n["time"], n.get("explanation", ""), "#22c55e"),
        ("💾", "Space · original", o["space"], "", "#f59e0b"),
        ("🧠", "Space · optimized", n["space"], "", "#38bdf8"),
    ]
    for col, c in zip(cols, cards):
        col.markdown(metric(*c), unsafe_allow_html=True)

    st.markdown('<div class="sec">🐞 Identified bugs & edge cases</div>', unsafe_allow_html=True)
    if result["bugs"]:
        for b in result["bugs"]:
            sev = str(b.get("severity", "low")).lower()
            st.markdown(f'<div class="bug" style="--c:{SEV.get(sev, SEV["low"])}"><span class="tag">{html.escape(sev.upper())}</span><div><div class="t">⚠️ {html.escape(b.get("title", ""))}</div><div class="d">{html.escape(b.get("detail", ""))}</div></div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ok">✅ No bugs or edge-case risks found.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec">🧩 Why the optimized version is faster</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="logic">{html.escape(result["logic"])}</div>', unsafe_allow_html=True)
    st.write("")
    st.download_button("⬇️ Download optimized.cpp", result["optimized_code"], "optimized.cpp", "text/x-c++src")

    st.markdown('<div class="sec">🧪 Verify & benchmark</div>', unsafe_allow_html=True)
    if not have_gpp():
        st.warning("g++ was not found on this PC. Install MinGW-w64 (Windows) or build-essential (Linux), restart VS Code, and this section will work.")
    else:
        st.caption("Compiles both versions with g++ -O2 and runs them locally (6 s limit per run).")
        if st.button("▶️ Compile, compare & benchmark"):
            with st.spinner("Compiling both versions and timing them…"):
                st.session_state.bench = verify_and_benchmark(result["_original"], result["optimized_code"], result.get("harness", ""))
        b = st.session_state.get("bench")
        if b and b["error"]:
            st.error("Compile error. Check the message below.")
            st.code(b["error"])
        elif b:
            if b["match"] is False:
                st.markdown('<div class="bug" style="--c:#ef4444"><span class="tag">MISMATCH</span><div><div class="t">Outputs differ</div><div class="d">The optimized version printed something different. Review it before using.</div></div></div>', unsafe_allow_html=True)
            elif b["match"]:
                st.markdown('<div class="ok">✅ Both versions print identical output on every test size.</div>', unsafe_allow_html=True)
            else:
                st.info("Could not compare outputs (the original timed out).")
            df = pd.DataFrame(b["rows"])
            both = df.dropna()
            if not both.empty:
                last = both.iloc[-1]
                x = last.original_ms / max(last.optimized_ms, 0.01)
                st.markdown(metric("🚀", f"Speedup at n = {int(last.n)}" if last.n else "Speedup", f"{x:.1f}×", f"{last.original_ms:.1f} ms → {last.optimized_ms:.1f} ms", "#22c55e"), unsafe_allow_html=True)
            if len(df) > 1:
                st.line_chart(df.set_index("n")[["original_ms", "optimized_ms"]], x_label="input size n", y_label="time (ms)")
                st.caption("Empty points mean that run hit the time limit.")
            st.dataframe(df.rename(columns={"original_ms": "original (ms)", "optimized_ms": "optimized (ms)"}), hide_index=True)

    st.markdown('<div class="sec">📄 PDF report</div>', unsafe_allow_html=True)
    if build_pdf is None:
        st.info("To enable the PDF report, run:  python -m pip install reportlab  and restart the app.")
    else:
        try:
            st.download_button("📄 Download PDF report", build_pdf(result, st.session_state.get("bench")), "algoshastra_report.pdf", "application/pdf")
        except Exception as e:
            st.error(f"Could not build the PDF: {e}")

# ---------- history ----------
def load_history(i):
    r = st.session_state.history[i]
    st.session_state.result, st.session_state.code = r, r["_original"]
    st.session_state.pop("bench", None)


if st.session_state.get("history"):
    with st.expander("🕘 History (this session)"):
        for i in reversed(range(len(st.session_state.history))):
            r = st.session_state.history[i]
            a, b2 = st.columns([5, 1])
            a.markdown(f"**{r.get('problem', 'Analysis')}** · {r['original']['time']} → {r['optimized']['time']}")
            b2.button("Load", key=f"h{i}", on_click=load_history, args=(i,))
