"""Compile original + optimized C++ with g++, compare outputs, and time both at growing input sizes."""
import os, shutil, subprocess, tempfile, time

PRELUDE = "#include <bits/stdc++.h>\nusing namespace std;\n"


def have_gpp() -> bool:
    return shutil.which("g++") is not None


def _build(tmp, name, code, harness):
    src = os.path.join(tmp, name + ".cpp")
    exe = os.path.join(tmp, name + (".exe" if os.name == "nt" else ""))
    with open(src, "w", encoding="utf-8") as f:
        f.write(PRELUDE + code + "\n" + harness)
    r = subprocess.run(["g++", "-O2", "-std=c++17", src, "-o", exe], capture_output=True, text=True, timeout=90)
    return (None, r.stderr[-1500:]) if r.returncode else (exe, "")


def _run(exe, n, timeout):
    t = time.perf_counter()
    try:
        r = subprocess.run([exe, str(n)], capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return None, None
    return r.stdout.strip(), (time.perf_counter() - t) * 1000


def verify_and_benchmark(original, optimized, harness="", sizes=(100, 1000, 5000, 20000, 50000), timeout=6):
    out = {"error": "", "match": None, "rows": []}
    harness = harness or ""
    with tempfile.TemporaryDirectory() as tmp:
        exe_o, e1 = _build(tmp, "orig", original, harness)
        exe_n, e2 = _build(tmp, "opt", optimized, harness)
        if not exe_o or not exe_n:
            out["error"] = ("Original:\n" + e1 if e1 else "") + ("\nOptimized:\n" + e2 if e2 else "")
            return out
        compared, mismatch = 0, False
        for n in (sizes if harness else (0,)):
            so, to = _run(exe_o, n, timeout)
            sn, tn = _run(exe_n, n, timeout)
            if so is not None and sn is not None:
                compared += 1
                mismatch |= so != sn
            out["rows"].append({"n": n, "original_ms": to, "optimized_ms": tn})
        out["match"] = None if not compared else (not mismatch)
    return out
