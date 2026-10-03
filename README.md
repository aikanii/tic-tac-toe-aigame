<div align="center">

# 🎮 Agent X vs Agent O: Tic-Tac-Toe

**Two LLM-powered agents play Tic-Tac-Toe against each other in a Streamlit UI.**

Built on the [Agno](https://github.com/agno-agi/agno) agent framework. Pick a different model for each side (GPT-4o, Claude, Gemini, Llama 3, and more) and watch them compete.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Agno](https://img.shields.io/badge/Agno-Agent%20Framework-6C47FF?style=flat-square)
![LLM](https://img.shields.io/badge/LLM-Multi--provider-lightgrey?style=flat-square)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Extending the Project](#extending-the-project)

---

## Overview

Each player is an independent Agno `Agent` wired to its own model. On every turn the current agent is prompted for a move and replies in JSON. The reply is parsed and validated, and if the move is malformed or illegal, the agent is retried with corrective feedback.

The Streamlit app lets you:

- Choose a model for **Player X** and **Player O**
- Watch the game play out automatically, or step through one move at a time
- Review every move with the agent's stated reasoning and a board snapshot
- Compare performance (move counts and average think-time per player)

---

## Architecture

| Component | File | Role |
| --- | --- | --- |
| **Game engine** | `game_engine.py` | Pure Python board state, legal-move checking, and win/draw detection. No LLM involved; this is the deterministic "referee." |
| **Agents** | `agents.py` | Builds one Agno `Agent` per player, each wired to a different model. Prompts the current agent for a move, parses its JSON reply, and retries with corrective feedback if the move is malformed or illegal. |
| **UI** | `app.py` | Streamlit app with model pickers, board rendering, move history, live status, and the auto-play loop. |

### Design Decision: A Deterministic Referee

> [!NOTE]
> The referee is intentionally **not** an LLM. An LLM asked to "validate" a move can occasionally be wrong. Using deterministic code for legality checks guarantees the game state is never corrupted, while the two player agents still do all the strategic thinking.

---

## Getting Started

### Installation

```bash
cd ai_tic_tac_toe_agent
pip install -r requirements.txt
cp .env.example .env
```

### Configuration

Edit `.env` and add the API key(s) for the models you want to use.

> [!TIP]
> You only need keys for the models you actually pick in the sidebar. For example, if both players use Claude, you only need `ANTHROPIC_API_KEY`.

### Run

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501).

---

## Usage

1. Pick a model for **Player X** and **Player O** in the sidebar.
2. Click **Start / Resume**.
3. Watch the game play out automatically. Toggle **Auto-play** off to step through manually; each rerun advances one move.
4. Expand **Move history** to see every move with the agent's stated reasoning and the board snapshot at that point.
5. Expand **Performance stats** for move counts and average think-time per player.
6. Click **Reset** to clear the board and start a new match. You can change models before clicking Start again.

---

## Extending the Project

| Goal | How |
| --- | --- |
| **Add a model** | Append a `ModelChoice(...)` to `AVAILABLE_MODELS` in `agents.py`, and make sure `_build_model` handles its provider. |
| **Change the strategy prompt** | Edit `PLAYER_INSTRUCTIONS` in `agents.py`. |
| **Persist match results** | `game_engine.GameState.history` is a plain list of `Move` dataclasses, so it is easy to serialize to JSON or CSV after each game. |
