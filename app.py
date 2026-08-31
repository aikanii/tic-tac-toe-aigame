"""
app.py
------
Streamlit front-end for Agent X vs Agent O: Tic-Tac-Toe.
Two LLM-backed Agno agents take turns; a deterministic referee (game_engine.py)
validates every move. Run with:

    streamlit run app.py
"""

import os
import time

import streamlit as st
from dotenv import load_dotenv

from agents import AVAILABLE_MODELS, create_player_agent, get_agent_move
from game_engine import GameState

load_dotenv()

st.set_page_config(page_title="Agent X vs Agent O", page_icon="🎮", layout="centered")

REQUIRED_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
}


# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
def init_state():
    if "game" not in st.session_state:
        st.session_state.game = GameState()
    if "agent_x" not in st.session_state:
        st.session_state.agent_x = None
    if "agent_o" not in st.session_state:
        st.session_state.agent_o = None
    if "running" not in st.session_state:
        st.session_state.running = False
    if "last_move_info" not in st.session_state:
        st.session_state.last_move_info = None


init_state()


def missing_key_for(choice) -> str | None:
    env_var = REQUIRED_KEYS[choice.provider]
    return None if os.getenv(env_var) else env_var


# --------------------------------------------------------------------------
# Sidebar: model selection & controls
# --------------------------------------------------------------------------
st.sidebar.title("⚙️ Game Setup")

label_to_choice = {m.label: m for m in AVAILABLE_MODELS}

x_label = st.sidebar.selectbox("Player X model", list(label_to_choice.keys()), index=0)
o_label = st.sidebar.selectbox("Player O model", list(label_to_choice.keys()), index=2)

x_choice = label_to_choice[x_label]
o_choice = label_to_choice[o_label]

missing_x = missing_key_for(x_choice)
missing_o = missing_key_for(o_choice)
if missing_x:
    st.sidebar.error(f"Missing {missing_x} for Player X's model.")
if missing_o:
    st.sidebar.error(f"Missing {missing_o} for Player O's model.")

col_a, col_b = st.sidebar.columns(2)
start_clicked = col_a.button("▶️ Start / Resume", use_container_width=True, disabled=bool(missing_x or missing_o))
reset_clicked = col_b.button("🔄 Reset", use_container_width=True)

auto_play = st.sidebar.toggle("Auto-play (no click between moves)", value=True)
move_delay = st.sidebar.slider("Delay between moves (s)", 0.0, 3.0, 0.6, 0.1)

if reset_clicked:
    st.session_state.game.reset()
    st.session_state.agent_x = None
    st.session_state.agent_o = None
    st.session_state.running = False
    st.session_state.last_move_info = None
    st.rerun()

if start_clicked:
    st.session_state.agent_x = create_player_agent("X", "O", x_choice)
    st.session_state.agent_o = create_player_agent("O", "X", o_choice)
    st.session_state.running = True


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.title("🎮 Agent X vs Agent O: Tic-Tac-Toe")
st.caption(f"Player X: **{x_label}**  ·  Player O: **{o_label}**")

game: GameState = st.session_state.game


# --------------------------------------------------------------------------
# Board rendering
# --------------------------------------------------------------------------
def render_board():
    symbol_display = {"X": "❌", "O": "⭕", "": ""}
    winning_cells = set(game.winning_line) if game.winning_line else set()

    for r in range(3):
        cols = st.columns(3, gap="small")
        for c in range(3):
            idx = r * 3 + c
            val = game.board[idx]
            display = symbol_display[val]
            highlight = idx in winning_cells
            style = "background-color:#2ecc71;" if highlight else ""
            cols[c].markdown(
                f"""
                <div style="
                    {style}
                    border:2px solid #444;
                    border-radius:8px;
                    height:90px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:2.2rem;
                ">{display if display else "&nbsp;"}</div>
                """,
                unsafe_allow_html=True,
            )


render_board()

# --------------------------------------------------------------------------
# Status
# --------------------------------------------------------------------------
status_box = st.empty()

if game.winner == "Draw":
    status_box.info("🤝 It's a draw!")
elif game.winner:
    status_box.success(f"🏆 Player {game.winner} wins!")
elif st.session_state.running:
    status_box.info(f"⏳ Player **{game.current_player}**'s turn...")
else:
    status_box.warning("Click **Start / Resume** in the sidebar to begin.")

if st.session_state.last_move_info:
    st.caption(f"💭 {st.session_state.last_move_info}")

# --------------------------------------------------------------------------
# Move history
# --------------------------------------------------------------------------
with st.expander("📜 Move history", expanded=False):
    if not game.history:
        st.write("No moves yet.")
    else:
        for i, move in enumerate(game.history, start=1):
            st.markdown(
                f"**{i}. Player {move.player} → position {move.position}** "
                f"({move.duration_s:.1f}s)\n\n> {move.reasoning}"
            )
            st.text(move.board_after)
            st.divider()

# --------------------------------------------------------------------------
# Performance stats
# --------------------------------------------------------------------------
if game.history:
    with st.expander("📊 Performance stats", expanded=False):
        for symbol in ("X", "O"):
            moves = [m for m in game.history if m.player == symbol]
            if moves:
                avg_time = sum(m.duration_s for m in moves) / len(moves)
                st.write(f"Player {symbol}: {len(moves)} moves, avg {avg_time:.2f}s/move")

# --------------------------------------------------------------------------
# Game loop
# --------------------------------------------------------------------------
if st.session_state.running and not game.is_over():
    agent = st.session_state.agent_x if game.current_player == "X" else st.session_state.agent_o
    symbol = game.current_player

    with st.spinner(f"Player {symbol} is thinking..."):
        result = get_agent_move(agent, game, symbol)

    move = game.apply_move(
        player=symbol,
        position=result["position"],
        reasoning=result["reasoning"],
        duration_s=result["duration_s"],
    )
    st.session_state.last_move_info = f"Player {symbol} played {move.position}: {move.reasoning}"

    if game.is_over():
        st.session_state.running = False

    if auto_play and not game.is_over():
        time.sleep(move_delay)
    st.rerun()