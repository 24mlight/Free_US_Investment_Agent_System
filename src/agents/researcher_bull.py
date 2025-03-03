from langchain_core.messages import HumanMessage
from agents.state import AgentState, show_agent_reasoning, show_workflow_status
import json


def researcher_bull_agent(state: AgentState):
    """Analyzes data from analysts and forms a bullish investment thesis."""
    show_workflow_status("Bull Researcher")
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
    if technical_data.get("signal") == "bullish":
        thesis_points.extend([
            f"Technical analysis indicates bullish trend with {technical_data.get('confidence', 'N/A')} confidence",
            f"Multiple technical indicators showing positive momentum"
        ])
        # Convert percentage string to float
        conf_str = technical_data.get('confidence', '0%').rstrip('%')
        confidence_factors.append(float(conf_str) / 100)

    # Fundamental Analysis Points
    if fundamental_data.get("signal") == "bullish":
        profitability = fundamental_data.get("profitability_signal", {})
        growth = fundamental_data.get("growth_signal", {})
        thesis_points.extend([
            f"Strong fundamental indicators with {fundamental_data.get('confidence', 'N/A')} confidence",
            f"Profitability metrics: {profitability.get('details', 'N/A')}",
            f"Growth metrics: {growth.get('details', 'N/A')}"
        ])
        conf_str = fundamental_data.get('confidence', '0%').rstrip('%')
        confidence_factors.append(float(conf_str) / 100)

    # Sentiment Analysis Points
    if sentiment_data.get("signal") == "bullish":
        thesis_points.extend([
            f"Positive market sentiment with {sentiment_data.get('confidence', 'N/A')} confidence",
            f"Reasoning: {sentiment_data.get('reasoning', 'N/A')}"
        ])
        conf_str = sentiment_data.get('confidence', '0%').rstrip('%')
        confidence_factors.append(float(conf_str) / 100)

    # Valuation Analysis Points
    if valuation_data.get("signal") == "bullish":
        thesis_points.extend([
            f"Attractive valuation with {valuation_data.get('confidence', 'N/A')} confidence",
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
        name="researcher_bull_agent",
    )

    if show_reasoning:
        show_agent_reasoning(message_content, "Bull Researcher")

    show_workflow_status("Bull Researcher", "completed")
    return {
        "messages": state["messages"] + [message],
        "data": state["data"]
    }
