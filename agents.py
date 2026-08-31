"""
agents.py
---------
Builds the two competing "player" agents on top of the Agno agent framework,
each backed by a different LLM. Also defines the "Referee" — a rule-based
(non-LLM) component that validates moves and applies them to the GameState.

Design note on the referee:
LLMs are unreliable at *enforcing* game rules with 100% consistency (they can
occasionally propose an illegal move or mis-read the board). Rather than
trusting a third LLM to police the other two, the referee here is deterministic
Python code (see game_engine.py) — it always agrees on what's legal. This
keeps the game fair and prevents an "invalid move" from silently corrupting
game state. The player *agents* are still the ones doing the strategic
thinking; the referee only validates + retries.
"""

import json
import re
import time
from dataclasses import dataclass
from typing import Optional

from game_engine import GameState


PLAYER_INSTRUCTIONS = """\
You are Player {symbol} in a game of Tic-Tac-Toe against Player {opponent}.

Board positions are numbered 0-8, left to right, top to bottom:
 0 | 1 | 2
 -----------
 3 | 4 | 5
 -----------
 6 | 7 | 8

Rules:
- You may only place your mark ({symbol}) on a position that is still a
  number (i.e. empty). Positions already containing "X" or "O" are taken.
- Think about blocking your opponent's winning lines and building your own.
- Respond with ONLY a single JSON object, no markdown fences, no extra text:
  {{"move": <integer 0-8>, "reasoning": "<one short sentence>"}}
"""


@dataclass
class ModelChoice:
    provider: str   # "openai" | "anthropic" | "google" | "groq"
    model_id: str
    label: str      # display name for the UI


AVAILABLE_MODELS = [
    ModelChoice("openai", "gpt-4o", "GPT-4o (OpenAI)"),
    ModelChoice("openai", "o3-mini", "GPT-o3-mini (OpenAI)"),
    ModelChoice("anthropic", "claude-sonnet-4-6", "Claude Sonnet (Anthropic)"),
    ModelChoice("google", "gemini-2.0-flash", "Gemini 2.0 Flash (Google)"),
    ModelChoice("groq", "llama-3.3-70b-versatile", "Llama 3.3 70B (Groq)"),
]


def _build_model(choice: ModelChoice):
    """Instantiate the correct Agno model wrapper for the chosen provider."""
    if choice.provider == "openai":
        from agno.models.openai import OpenAIChat
        return OpenAIChat(id=choice.model_id)
    if choice.provider == "anthropic":
        from agno.models.anthropic import Claude
        return Claude(id=choice.model_id)
    if choice.provider == "google":
        from agno.models.google import Gemini
        return Gemini(id=choice.model_id)
    if choice.provider == "groq":
        from agno.models.groq import Groq
        return Groq(id=choice.model_id)
    raise ValueError(f"Unknown provider: {choice.provider}")


def create_player_agent(symbol: str, opponent_symbol: str, choice: ModelChoice):
    """Create an Agno Agent that plays as `symbol`."""
    from agno.agent import Agent

    return Agent(
        name=f"Player {symbol} ({choice.label})",
        model=_build_model(choice),
        instructions=PLAYER_INSTRUCTIONS.format(symbol=symbol, opponent=opponent_symbol),
        markdown=False,
    )


def _extract_json(text: str) -> dict:
    """Best-effort extraction of a JSON object from an LLM response."""
    text = text.strip()
    # Strip markdown fences if the model added them anyway
    text = re.sub(r"^```(json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in response: {text!r}")
    return json.loads(match.group(0))


def get_agent_move(agent, game_state: GameState, symbol: str, max_retries: int = 3) -> dict:
    """
    Ask the agent for a move, validate it against the referee (GameState),
    and retry with corrective feedback if the move is illegal or unparsable.

    Returns: {"position": int, "reasoning": str, "duration_s": float, "raw": str}
    """
    board_str = game_state.board_to_string()
    prompt = f"Current board:\n{board_str}\n\nIt is your turn ({symbol}). What is your move?"

    last_error = None
    for attempt in range(1, max_retries + 1):
        start = time.time()
        response = agent.run(prompt)
        duration = time.time() - start
        raw_text = response.content if hasattr(response, "content") else str(response)

        try:
            parsed = _extract_json(raw_text)
            position = int(parsed["move"])
            reasoning = str(parsed.get("reasoning", "")).strip()
        except Exception as e:
            last_error = f"Could not parse a move from your response ({e}). Reply with ONLY the JSON object."
            prompt = f"{last_error}\nCurrent board:\n{board_str}\nYour turn ({symbol})."
            continue

        if not game_state.is_valid_move(position):
            last_error = f"Position {position} is illegal (occupied or out of range 0-8)."
            prompt = (
                f"{last_error} Legal positions right now: {game_state.available_moves()}.\n"
                f"Current board:\n{board_str}\nYour turn ({symbol}). Reply with ONLY the JSON object."
            )
            continue

        return {
            "position": position,
            "reasoning": reasoning or "(no reasoning given)",
            "duration_s": duration,
            "raw": raw_text,
        }

    # Fallback: after exhausting retries, pick the first available legal move
    # so the game can still proceed instead of crashing.
    fallback_pos = game_state.available_moves()[0]
    return {
        "position": fallback_pos,
        "reasoning": f"(fallback move after {max_retries} invalid attempts: {last_error})",
        "duration_s": 0.0,
        "raw": "",
    }