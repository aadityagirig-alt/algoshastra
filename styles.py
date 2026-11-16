"""Themes, CSS and the logo."""

THEMES = {
    "Dark": dict(bg="#0a0a1f", surface="#13132e", text="#e9e9ff", muted="#9d9dc9", a1="#7c3aed", a2="#2563eb", glow="#22d3ee", border="#2b2b5c", pyg="dracula"),
    "Light": dict(bg="#f5f3ff", surface="#ffffff", text="#1a1a3a", muted="#5d5d88", a1="#7c3aed", a2="#2563eb", glow="#0ea5e9", border="#d9d4ff", pyg="default"),
    "Cyberpunk": dict(bg="#090012", surface="#190a2d", text="#f6eaff", muted="#c9a0ff", a1="#ff2bd6", a2="#00e5ff", glow="#fcee0a", border="#52208a", pyg="monokai"),
}

LOGO_SVG = """<svg width="48" height="48" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#c026d3"/></linearGradient><filter id="gl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><path d="M32 4 56 13v18c0 15-10 25-24 29C18 56 8 46 8 31V13z" fill="rgba(124,58,237,.22)" stroke="url(#lg)" stroke-width="3" stroke-linejoin="round" filter="url(#gl)"/><g fill="none" stroke="url(#lg)" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" filter="url(#gl)"><path d="M25 24 17 32l8 8"/><path d="M39 24l8 8-8 8"/><path d="M35 22 29 42"/></g></svg>"""


def build_css(t: dict, font_px: int) -> str:
    root = f":root{{--bg:{t['bg']};--sf:{t['surface']};--tx:{t['text']};--mu:{t['muted']};--a1:{t['a1']};--a2:{t['a2']};--gl:{t['glow']};--bd:{t['border']};--fs:{font_px}px}}"
    return "<style>@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@400;600;700;800&display=swap');" + root + """
html,body,.stApp{font-family:'Sora',sans-serif;color:var(--tx)}
.stApp{background:radial-gradient(900px 500px at 8% -10%,color-mix(in srgb,var(--a1) 28%,transparent),transparent),radial-gradient(800px 500px at 100% 0%,color-mix(in srgb,var(--a2) 24%,transparent),transparent),var(--bg)}
header[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:1.6rem;max-width:1400px}
h1,h2,h3,p,label,span,li{color:var(--tx)}
.brand{display:flex;align-items:center;gap:14px}
.brand b{font-size:1.65rem;font-weight:800;letter-spacing:-.02em;background:linear-gradient(90deg,var(--gl),var(--a1) 60%,var(--a2));-webkit-background-clip:text;color:transparent}
.brand small{display:block;color:var(--mu);font-size:.8rem;margin-top:-2px}
.ptitle{display:flex;align-items:center;gap:8px;font-weight:700;margin:.4rem 0 .5rem}
.dot{width:10px;height:10px;border-radius:50%;background:var(--gl);box-shadow:0 0 10px var(--gl)}
textarea{font-family:'JetBrains Mono',monospace!important;font-size:var(--fs)!important;background:var(--sf)!important;color:var(--tx)!important;border:1px solid var(--bd)!important;border-radius:12px!important;line-height:1.55!important}
textarea:focus{border-color:var(--a1)!important;box-shadow:0 0 0 2px color-mix(in srgb,var(--a1) 45%,transparent)!important}
.codebox{font-family:'JetBrains Mono',monospace;border:1px solid var(--bd);border-radius:12px;padding:.8rem 1rem;height:420px;overflow:auto;box-shadow:0 0 28px -12px var(--a1)}
.codebox pre{margin:0!important;font-family:inherit!important;font-size:inherit!important;background:transparent!important;line-height:1.55!important}
.stButton>button[kind="primary"]{width:100%;height:3.3rem;border:0;border-radius:14px;font-weight:700;font-size:1.05rem;color:#fff;background:linear-gradient(110deg,var(--a1),var(--a2),var(--gl),var(--a1));background-size:260% 100%;animation:flow 6s linear infinite;box-shadow:0 8px 30px -8px var(--a1);transition:transform .15s,box-shadow .15s}
.stButton>button[kind="primary"]:hover{transform:translateY(-2px);box-shadow:0 12px 36px -6px var(--a2)}
.stButton>button[kind="primary"] p{color:#fff}
@keyframes flow{to{background-position:260% 0}}
.stButton>button:not([kind="primary"]),.stDownloadButton>button,[data-testid="stPopover"]>button{background:var(--sf);color:var(--tx);border:1px solid var(--bd);border-radius:12px}
.loader{border:1px solid var(--bd);background:var(--sf);border-radius:14px;padding:1.1rem 1.3rem;margin:.8rem 0}
.loader .bar{height:6px;border-radius:6px;margin-top:.7rem;background:linear-gradient(90deg,transparent,var(--gl),var(--a1),transparent);background-size:50% 100%;background-repeat:no-repeat;animation:sweep 1.2s ease-in-out infinite;background-color:var(--bd)}
@keyframes sweep{from{background-position:-60% 0}to{background-position:160% 0}}
.metric{background:var(--sf);border:1px solid var(--bd);border-radius:14px;padding:1rem 1.1rem;position:relative;overflow:hidden}
.metric:before{content:"";position:absolute;inset:0 auto 0 0;width:4px;background:var(--c)}
.metric .k{color:var(--mu);font-size:.82rem}
.metric .v{font-family:'JetBrains Mono',monospace;font-size:1.65rem;font-weight:600;color:var(--c);margin:.15rem 0}
.metric .n{color:var(--mu);font-size:.78rem;line-height:1.35}
.sec{font-weight:700;font-size:1.15rem;margin:1.6rem 0 .7rem}
.bug{display:flex;gap:12px;background:var(--sf);border:1px solid var(--bd);border-left:4px solid var(--c);border-radius:12px;padding:.8rem 1rem;margin-bottom:.6rem}
.bug .t{font-weight:700}.bug .d{color:var(--mu);font-size:.9rem;margin-top:2px}
.tag{font-size:.7rem;font-weight:700;padding:2px 8px;border-radius:99px;background:var(--c);color:#111;height:fit-content}
.ok{border:1px solid #16a34a;background:rgba(22,163,74,.12);border-radius:12px;padding:.8rem 1rem}
.logic{background:var(--sf);border:1px solid var(--bd);border-radius:14px;padding:1rem 1.2rem;line-height:1.65}
.chip{display:inline-block;padding:3px 12px;border-radius:99px;font-size:.78rem;font-weight:600;background:linear-gradient(90deg,var(--a1),var(--a2));color:#fff}
</style>"""
