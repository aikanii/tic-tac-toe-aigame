"""
theme.py
--------
"Liquid glass" visual theme for the Tic-Tac-Toe app: frosted translucent
panels, slow drifting background blobs, and glowing gradient-stroke marks
for X/O. Pure presentation — no game logic lives here.

Design tokens
-------------
Base       #0a0e1a  (deep navy-black stage)
Glass      rgba(255,255,255,.045) fill / rgba(255,255,255,.09) border
Accent X   #22d3ee -> #6366f1  (cyan -> indigo)
Accent O   #fb7185 -> #f59e0b  (rose -> amber)
Text       #e7ebf3 primary / #8b93a7 muted
Display type: "Space Grotesk"   Body type: "Inter"
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg: #0a0e1a;
    --glass: rgba(255,255,255,0.045);
    --glass-border: rgba(255,255,255,0.09);
    --glass-strong: rgba(255,255,255,0.075);
    --text: #e7ebf3;
    --muted: #8b93a7;
    --x-a: #22d3ee;
    --x-b: #6366f1;
    --o-a: #fb7185;
    --o-b: #f59e0b;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

/* ---- drifting liquid blobs behind everything ---- */
[data-testid="stAppViewContainer"]::before,
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    width: 46vw;
    height: 46vw;
    border-radius: 50%;
    filter: blur(90px);
    z-index: 0;
    opacity: 0.35;
    pointer-events: none;
}
[data-testid="stAppViewContainer"]::before {
    background: radial-gradient(circle, var(--x-a), transparent 70%);
    top: -12vw;
    left: -10vw;
    animation: drift1 26s ease-in-out infinite alternate;
}
[data-testid="stAppViewContainer"]::after {
    background: radial-gradient(circle, var(--o-a), transparent 70%);
    bottom: -14vw;
    right: -8vw;
    animation: drift2 32s ease-in-out infinite alternate;
}
@keyframes drift1 {
    0%   { transform: translate(0, 0) scale(1); }
    100% { transform: translate(6vw, 8vw) scale(1.15); }
}
@keyframes drift2 {
    0%   { transform: translate(0, 0) scale(1); }
    100% { transform: translate(-5vw, -6vw) scale(1.1); }
}

.block-container { position: relative; z-index: 1; padding-top: 2.2rem; max-width: 760px; }

/* ---- headline ---- */
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    font-size: 2.1rem !important;
    background: linear-gradient(90deg, var(--x-a), var(--o-a));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.1rem !important;
}
[data-testid="stCaptionContainer"], .stCaption { color: var(--muted) !important; }

/* ---- generic glass panel look, applied to key containers ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)) !important;
    backdrop-filter: blur(18px);
    border-right: 1px solid var(--glass-border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
}

.liquid-card {
    background: var(--glass);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 28px;
    padding: 1.4rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.06);
    margin-bottom: 1rem;
}

/* ---- status pill ---- */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1.1rem;
    border-radius: 999px;
    background: var(--glass-strong);
    border: 1px solid var(--glass-border);
    font-size: 0.95rem;
    color: var(--text);
}
.status-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: linear-gradient(90deg, var(--x-a), var(--o-a));
    box-shadow: 0 0 10px var(--x-a);
}

/* ---- board grid ---- */
.board-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    width: 100%;
    max-width: 380px;
    margin: 0.6rem auto 0.2rem auto;
}
.cell {
    aspect-ratio: 1 / 1;
    border-radius: 18px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    transition: background 0.4s ease, border-color 0.4s ease, transform 0.2s ease;
}
.cell.win {
    background: rgba(255,255,255,0.09);
    border-color: rgba(255,255,255,0.25);
    animation: pulseWin 1.4s ease-in-out infinite;
}
@keyframes pulseWin {
    0%, 100% { box-shadow: 0 0 0px rgba(255,255,255,0.0); }
    50% { box-shadow: 0 0 26px rgba(255,255,255,0.35); }
}
.cell svg { width: 58%; height: 58%; animation: markIn 0.35s cubic-bezier(.2,.9,.3,1.3); }
@keyframes markIn {
    0% { transform: scale(0.4); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

/* ---- buttons ---- */
.stButton > button {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    background: var(--glass-strong) !important;
    border: 1px solid var(--glass-border) !important;
    color: var(--text) !important;
    border-radius: 14px !important;
    padding: 0.5rem 1rem !important;
    transition: box-shadow 0.25s ease, transform 0.15s ease, border-color 0.25s ease;
}
.stButton > button:hover {
    border-color: rgba(255,255,255,0.3) !important;
    box-shadow: 0 0 18px rgba(99,102,241,0.35);
    transform: translateY(-1px);
}
.stButton > button:disabled {
    opacity: 0.35 !important;
}

/* ---- move history entries ---- */
.move-row {
    border-bottom: 1px solid var(--glass-border);
    padding: 0.55rem 0.1rem;
}
.move-row:last-child { border-bottom: none; }
.move-tag {
    display: inline-block;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.78rem;
    padding: 0.1rem 0.5rem;
    border-radius: 999px;
    margin-right: 0.5rem;
}
.move-tag.x { background: rgba(34,211,238,0.15); color: var(--x-a); }
.move-tag.o { background: rgba(251,113,133,0.15); color: var(--o-a); }
.move-reason { color: var(--muted); font-size: 0.88rem; margin-top: 0.15rem; }

/* ---- expander / misc containers ---- */
[data-testid="stExpander"] {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 18px !important;
    backdrop-filter: blur(14px);
}
[data-testid="stAlert"] {
    background: var(--glass-strong) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 16px !important;
    color: var(--text) !important;
}
</style>
"""


def inject(st):
    """Call once near the top of the app to load the theme."""
    st.markdown(CSS, unsafe_allow_html=True)


def _svg_mark(symbol: str) -> str:
    if symbol == "X":
        return """
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="gx" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#22d3ee"/>
                    <stop offset="100%" stop-color="#6366f1"/>
                </linearGradient>
                <filter id="glowx" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur stdDeviation="3.2" result="blur"/>
                    <feMerge>
                        <feMergeNode in="blur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <line x1="18" y1="18" x2="82" y2="82" stroke="url(#gx)" stroke-width="12" stroke-linecap="round" filter="url(#glowx)"/>
            <line x1="82" y1="18" x2="18" y2="82" stroke="url(#gx)" stroke-width="12" stroke-linecap="round" filter="url(#glowx)"/>
        </svg>
        """
    if symbol == "O":
        return """
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="go" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#fb7185"/>
                    <stop offset="100%" stop-color="#f59e0b"/>
                </linearGradient>
                <filter id="glowo" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur stdDeviation="3.2" result="blur"/>
                    <feMerge>
                        <feMergeNode in="blur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <circle cx="50" cy="50" r="30" fill="none" stroke="url(#go)" stroke-width="12" filter="url(#glowo)"/>
        </svg>
        """
    return ""


def render_board_html(board, winning_cells=None) -> str:
    """Return the full liquid-glass board grid as one HTML block."""
    winning_cells = winning_cells or set()
    cells_html = []
    for idx, val in enumerate(board):
        win_class = " win" if idx in winning_cells else ""
        mark = _svg_mark(val) if val else ""
        cells_html.append(f'<div class="cell{win_class}">{mark}</div>')
    return f'<div class="board-grid">{"".join(cells_html)}</div>'


def status_pill_html(text: str) -> str:
    return f'<div class="status-pill"><span class="status-dot"></span>{text}</div>'


def move_row_html(index: int, player: str, position: int, duration_s: float, reasoning: str) -> str:
    tag_class = "x" if player == "X" else "o"
    return f"""
    <div class="move-row">
        <span class="move-tag {tag_class}">{player}</span>
        <strong>#{index} → position {position}</strong>
        <span style="color:var(--muted); font-size:0.82rem;"> · {duration_s:.1f}s</span>
        <div class="move-reason">{reasoning}</div>
    </div>
    """