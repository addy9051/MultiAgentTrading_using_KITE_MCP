"""
Graph Conditions — Routing functions for the LangGraph conditional edges.

These functions determine whether debate/discussion loops should continue
or terminate and hand off to the next stage.
"""

from models.trading_state import TradingState


def should_continue_debate(state: TradingState) -> str:
    """
    Decide whether the bull/bear debate should continue.

    Returns the name of the next node:
    - "bull_researcher" to continue the debate loop
    - "research_arbiter" to end debate and judge
    """
    debate_round = state.get("debate_round", 0)
    max_rounds = state.get("metadata", {}).get("max_debate_rounds", 2) if state.get("metadata") else 2

    if debate_round < max_rounds * 2:  # Each round has both bull and bear speaking
        # Alternate: after bear speaks, send back to bull (if under limit)
        # After bull speaks, send to bear
        history = state.get("debate_history", [])
        if history:
            last_speaker = history[-1].get("speaker", "")
            if last_speaker == "bull":
                return "bear_researcher"
            elif last_speaker == "bear" and debate_round < max_rounds * 2:
                return "bull_researcher"

        return "bull_researcher"

    return "research_arbiter"


def should_continue_risk_discussion(state: TradingState) -> str:
    """
    Decide whether the risk panel discussion should continue.

    Returns the name of the next node:
    - Next risk panelist in rotation
    - "risk_arbiter" to end and judge
    """
    risk_round = state.get("risk_discussion_round", 0)
    max_rounds = state.get("metadata", {}).get("max_risk_discussion_rounds", 2) if state.get("metadata") else 2
    total_max = max_rounds * 3  # 3 panelists per round

    if risk_round >= total_max:
        return "risk_arbiter"

    # Rotate: hawk → dove → owl → hawk → dove → owl → ...
    rotation = ["risk_hawk", "risk_dove", "risk_owl"]
    next_idx = risk_round % 3
    return rotation[next_idx]


def after_bull(state: TradingState) -> str:
    """Route after bull researcher: always go to bear."""
    return "bear_researcher"


def after_bear(state: TradingState) -> str:
    """Route after bear researcher: check if debate should continue."""
    debate_round = state.get("debate_round", 0)
    max_rounds = state.get("metadata", {}).get("max_debate_rounds", 2) if state.get("metadata") else 2

    # Each full round = bull + bear, so debate_round counts each speaker
    # If we've completed enough full rounds, go to arbiter
    if debate_round >= max_rounds * 2:
        return "research_arbiter"
    return "bull_researcher"


def after_risk_panelist(state: TradingState) -> str:
    """Route after any risk panelist: continue rotation or go to arbiter."""
    risk_round = state.get("risk_discussion_round", 0)
    max_rounds = state.get("metadata", {}).get("max_risk_discussion_rounds", 2) if state.get("metadata") else 2
    total_max = max_rounds * 3

    if risk_round >= total_max:
        return "risk_arbiter"

    rotation = ["risk_hawk", "risk_dove", "risk_owl"]
    next_idx = risk_round % 3
    return rotation[next_idx]
