# 🎮 Agent X vs Agent O: Tic-Tac-Toe

Two LLM-powered agents (built on the [Agno](https://github.com/agno-agi/agno) agent
framework) play Tic-Tac-Toe against each other in a Streamlit UI. Pick a different
model for each side (GPT-4o, Claude, Gemini, Llama 3...) and watch them compete.

## How it works

| Component | File | Role |
|---|---|---|
| Game engine | `game_engine.py` | Pure Python board state, legal-move checking, win/draw detection. No LLM involved — this is the deterministic "referee." |
| Agents | `agents.py` | Builds one Agno `Agent` per player, each wired to a different model. Prompts the current agent for a move, parses its JSON reply, and retries with corrective feedback if the move is malformed or illegal. |
| UI | `app.py` | Streamlit app: model pickers, board rendering, move history, live status, auto-play loop. |

**Why the referee isn't itself an LLM:** an LLM asked to "validate" a move can
occasionally be wrong. Using deterministic code for legality checks guarantees the
game state is never corrupted; the two *player* agents are still the ones doing all
the strategic thinking.

## Setup

```bash
cd ai_tic_tac_toe_agent
pip install -r requirements.txt
cp .env.example .env
# then edit .env and add the API key(s) for whichever models you want to use
```

You only need the key(s) for the models you actually pick in the sidebar — e.g. if
both players use Claude, you only need `ANTHROPIC_API_KEY`.

## Run

```bash
streamlit run app.py
```

Then open http://localhost:8501.

1. Pick a model for Player X and Player O in the sidebar.
2. Click **Start / Resume**.
3. Watch the game play out automatically (toggle "Auto-play" off if you'd rather
   step through moves manually — each rerun advances one move).
4. Expand **Move history** to see every move with the agent's stated reasoning
   and the board snapshot at that point.
5. Expand **Performance stats** for move counts and average think-time per player.
6. Click **Reset** to clear the board and start a new match (you can change
   models before clicking Start again).

## Extending it

- Add a model: append a `ModelChoice(...)` to `AVAILABLE_MODELS` in `agents.py`
  and make sure `_build_model` handles its provider.
- Change the strategy prompt: edit `PLAYER_INSTRUCTIONS` in `agents.py`.
- Persist match results: `game_engine.GameState.history` is a plain list of
  `Move` dataclasses — easy to serialize to JSON/CSV after each game.