from datetime import datetime, timedelta
import argparse
from agents.valuation import valuation_agent
from agents.state import AgentState
from agents.sentiment import sentiment_agent
from agents.risk_manager import risk_management_agent
from agents.technicals import technical_analyst_agent
from agents.portfolio_manager import portfolio_management_agent
from agents.market_data import market_data_agent
from agents.fundamentals import fundamentals_agent
from agents.researcher_bull import researcher_bull_agent
from agents.researcher_bear import researcher_bear_agent
from agents.debate_room import debate_room_agent
from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件中的环境变量


##### Run the Hedge Fund #####
def run_hedge_fund(ticker: str, start_date: str, end_date: str, portfolio: dict, show_reasoning: bool = False, num_of_news: int = 5):
    final_state = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Make a trading decision based on the provided data.",
                )
            ],
            "data": {
                "ticker": ticker,
                "portfolio": portfolio,
                "start_date": start_date,
                "end_date": end_date,
                "num_of_news": num_of_news,
            },
            "metadata": {
                "show_reasoning": show_reasoning,
            }
        },
    )
    return final_state["messages"][-1].content


# Define the new workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("market_data_agent", market_data_agent)
workflow.add_node("technical_analyst_agent", technical_analyst_agent)
workflow.add_node("fundamentals_agent", fundamentals_agent)
workflow.add_node("sentiment_agent", sentiment_agent)
workflow.add_node("valuation_agent", valuation_agent)
workflow.add_node("researcher_bull_agent", researcher_bull_agent)
workflow.add_node("researcher_bear_agent", researcher_bear_agent)
workflow.add_node("debate_room_agent", debate_room_agent)
workflow.add_node("risk_management_agent", risk_management_agent)
workflow.add_node("portfolio_management_agent", portfolio_management_agent)

# Define the workflow
workflow.set_entry_point("market_data_agent")

# Market Data to Analysts
workflow.add_edge("market_data_agent", "technical_analyst_agent")
workflow.add_edge("market_data_agent", "fundamentals_agent")
workflow.add_edge("market_data_agent", "sentiment_agent")
workflow.add_edge("market_data_agent", "valuation_agent")

# Analysts to Researchers
workflow.add_edge("technical_analyst_agent", "researcher_bull_agent")
workflow.add_edge("fundamentals_agent", "researcher_bull_agent")
workflow.add_edge("sentiment_agent", "researcher_bull_agent")
workflow.add_edge("valuation_agent", "researcher_bull_agent")

workflow.add_edge("technical_analyst_agent", "researcher_bear_agent")
workflow.add_edge("fundamentals_agent", "researcher_bear_agent")
workflow.add_edge("sentiment_agent", "researcher_bear_agent")
workflow.add_edge("valuation_agent", "researcher_bear_agent")

# Researchers to Debate Room
workflow.add_edge("researcher_bull_agent", "debate_room_agent")
workflow.add_edge("researcher_bear_agent", "debate_room_agent")

# Debate Room to Risk Management
workflow.add_edge("debate_room_agent", "risk_management_agent")

# Risk Management to Portfolio Management
workflow.add_edge("risk_management_agent", "portfolio_management_agent")
workflow.add_edge("portfolio_management_agent", END)

app = workflow.compile()

# Add this at the bottom of the file
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run the hedge fund trading system')
    parser.add_argument('--ticker', type=str, required=True,
                        help='Stock ticker symbol')
    parser.add_argument('--start-date', type=str,
                        help='Start date (YYYY-MM-DD). Defaults to 3 months before end date')
    parser.add_argument('--end-date', type=str,
                        help='End date (YYYY-MM-DD). Defaults to today')
    parser.add_argument('--show-reasoning', action='store_true',
                        help='Show reasoning from each agent')
    parser.add_argument('--initial-capital', type=float, default=100000.0,
                        help='Initial cash amount (default: 100,000)')
    parser.add_argument('--num-of-news', type=int, default=5,
                        help='Number of news articles to analyze for sentiment (default: 5)')

    args = parser.parse_args()

    # Set default dates if not provided
    if not args.end_date:
        args.end_date = datetime.now().strftime('%Y-%m-%d')

    if not args.start_date:
        # Default to 3 months before end date using timedelta
        end_date_obj = datetime.strptime(args.end_date, '%Y-%m-%d')
        start_date_obj = end_date_obj - \
            timedelta(days=90)  # Approximately 3 months
        args.start_date = start_date_obj.strftime('%Y-%m-%d')

    # Validate dates if provided
    if args.start_date:
        try:
            datetime.strptime(args.start_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Start date must be in YYYY-MM-DD format")

    if args.end_date:
        try:
            datetime.strptime(args.end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("End date must be in YYYY-MM-DD format")

    # Validate num_of_news
    if args.num_of_news < 1:
        raise ValueError("Number of news articles must be at least 1")
    if args.num_of_news > 100:
        raise ValueError("Number of news articles cannot exceed 100")

    # Configure portfolio with initial capital
    portfolio = {
        "cash": args.initial_capital,
        "stock": 0  # No initial stock position
    }

    result = run_hedge_fund(
        ticker=args.ticker,
        start_date=args.start_date,
        end_date=args.end_date,
        portfolio=portfolio,
        show_reasoning=args.show_reasoning,
        num_of_news=args.num_of_news
    )
    print("\nFinal Result:")
    print(result)
