from langchain_core.messages import HumanMessage
from agents.state import AgentState, show_agent_reasoning, show_workflow_status
import json
import ast


def debate_room_agent(state: AgentState):
    """Facilitates debate between bull and bear researchers to reach a balanced conclusion."""
    show_workflow_status("Debate Room")
    show_reasoning = state["metadata"]["show_reasoning"]

    # Fetch messages from researchers
    bull_message = next(
        msg for msg in state["messages"] if msg.name == "researcher_bull_agent")
    bear_message = next(
        msg for msg in state["messages"] if msg.name == "researcher_bear_agent")

    try:
        bull_thesis = json.loads(bull_message.content)
        bear_thesis = json.loads(bear_message.content)
    except Exception as e:
        bull_thesis = ast.literal_eval(bull_message.content)
        bear_thesis = ast.literal_eval(bear_message.content)

    # Compare confidence levels
    bull_confidence = bull_thesis["confidence"]
    bear_confidence = bear_thesis["confidence"]

    # Analyze debate points
    debate_summary = []

    # Add bull thesis points if any
    if bull_thesis["thesis_points"]:
        debate_summary.append("\nBullish Arguments:")
        for point in bull_thesis["thesis_points"]:
            debate_summary.append(f"+ {point}")
    else:
        debate_summary.append("\nNo strong bullish arguments presented.")

    # Add bear thesis points if any
    if bear_thesis["thesis_points"]:
        debate_summary.append("\nBearish Arguments:")
        for point in bear_thesis["thesis_points"]:
            debate_summary.append(f"- {point}")
    else:
        debate_summary.append("\nNo strong bearish arguments presented.")

    # Determine final recommendation
    confidence_diff = bull_confidence - bear_confidence

    if len(bull_thesis["thesis_points"]) == 0 and len(bear_thesis["thesis_points"]) == 0:
        # No strong arguments on either side
        final_signal = "neutral"
        reasoning = "Insufficient evidence for a strong directional view"
        confidence = 0.5  # Low confidence due to lack of evidence
    elif abs(confidence_diff) < 0.1:  # Close debate
        final_signal = "neutral"
        reasoning = "Balanced debate with strong arguments on both sides"
        confidence = max(bull_confidence, bear_confidence)
    elif confidence_diff > 0:  # Bull wins
        final_signal = "bullish"
        reasoning = "Bullish arguments more convincing"
        confidence = bull_confidence
    else:  # Bear wins
        final_signal = "bearish"
        reasoning = "Bearish arguments more convincing"
        confidence = bear_confidence

    message_content = {
        "signal": final_signal,
        # Format as percentage string to match other agents
        "confidence": f"{confidence:.0%}",
        "bull_confidence": f"{bull_confidence:.0%}",
        "bear_confidence": f"{bear_confidence:.0%}",
        "debate_summary": debate_summary,
        "reasoning": reasoning
    }

    message = HumanMessage(
        content=json.dumps(message_content),
        name="debate_room_agent",
    )

    if show_reasoning:
        show_agent_reasoning(message_content, "Debate Room")

    show_workflow_status("Debate Room", "completed")
    return {
        "messages": state["messages"] + [message],
        "data": {
            **state["data"],
            "debate_analysis": message_content
        }
    }
