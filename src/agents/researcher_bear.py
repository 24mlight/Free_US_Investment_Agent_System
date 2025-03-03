from langchain_core.messages import HumanMessage
from agents.state import AgentState, show_agent_reasoning, show_workflow_status
import json


def researcher_bear_agent(state: AgentState):
    """Analyzes data from analysts and forms a bearish investment thesis."""
    show_workflow_status("Bear Researcher")
    show_reasoning = state["metadata"]["show_reasoning"]

    # Collect messages from analysts
    technical_message = next(
        msg for msg in state["messages"] if msg.name == "technical_analyst_agent")
    fundamental_message = next(
        msg for msg in state["messages"] if msg.name == "fundamentals_agent")
    sentiment_message = next(
        msg for msg in state["messages"] if msg.name == "sentiment_agent")
    valuation_message = next(
        msg for msg in state["messages"] if msg.name == "valuation_agent")

    # Parse analyst messages
    technical_data = json.loads(technical_message.content)
    fundamental_data = json.loads(fundamental_message.content)
    sentiment_data = json.loads(sentiment_message.content)
    valuation_data = json.loads(valuation_message.content)

    # Initialize thesis points and confidence tracking
    thesis_points = []
    confidence_factors = []

    # Technical Analysis Points
    if technical_data.get("signal") == "bearish":
        thesis_points.extend([
            f"Technical analysis indicates bearish trend with {technical_data.get('confidence', 'N/A')} confidence",
            f"Multiple technical indicators showing negative momentum"
        ])
        # Convert percentage string to float
        conf_str = technical_data.get('confidence', '0%').rstrip('%')
        confidence_factors.append(float(conf_str) / 100)

    # Fundamental Analysis Points
    if fundamental_data.get("signal") == "bearish":
        profitability = fundamental_data.get("profitability_signal", {})
        growth = fundamental_data.get("growth_signal", {})
        thesis_points.extend([
            f"Weak fundamental indicators with {fundamental_data.get('confidence', 'N/A')} confidence",
            f"Profitability concerns: {profitability.get('details', 'N/A')}",
            f"Growth challenges: {growth.get('details', 'N/A')}"
        ])
        conf_str = fundamental_data.get('confidence', '0%').rstrip('%')
        confidence_factors.append(float(conf_str) / 100)

    # Sentiment Analysis Points
    if sentiment_data.get("signal") == "bearish":
        thesis_points.extend([
            f"Negative market sentiment with {sentiment_data.get('confidence', 'N/A')} confidence",
            f"Reasoning: {sentiment_data.get('reasoning', 'N/A')}"
        ])
        conf_str = sentiment_data.get('confidence', '0%').rstrip('%')
        confidence_factors.append(float(conf_str) / 100)

    # Valuation Analysis Points
    if valuation_data.get("signal") == "bearish":
        thesis_points.extend([
            f"Concerning valuation with {valuation_data.get('confidence', 'N/A')} confidence",
            f"DCF Analysis: {valuation_data.get('dcf_analysis', 'N/A')}",
            f"Owner Earnings Analysis: {valuation_data.get('owner_earnings_analysis', 'N/A')}"
        ])
        conf_str = valuation_data.get('confidence', '0%').rstrip('%')
        confidence_factors.append(float(conf_str) / 100)

    # Calculate overall confidence
    confidence = sum(confidence_factors) / \
        len(confidence_factors) if confidence_factors else 0.0

    # Prepare message content
    message_content = {
        "thesis_points": thesis_points,
        "confidence": confidence,
        "supporting_data": {
            "technical": technical_data,
            "fundamental": fundamental_data,
            "sentiment": sentiment_data,
            "valuation": valuation_data
        }
    }

    message = HumanMessage(
        content=json.dumps(message_content),
        name="researcher_bear_agent",
    )

    if show_reasoning:
        show_agent_reasoning(message_content, "Bear Researcher")

    show_workflow_status("Bear Researcher", "completed")
    return {
        "messages": state["messages"] + [message],
        "data": state["data"]
    }
