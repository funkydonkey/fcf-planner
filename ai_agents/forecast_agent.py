import config
from agents import Runner, Agent, trace
from dotenv import load_dotenv
import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Any
from .forecast_analyzer import analyze_historical_data

load_dotenv()

class ForecastAgentResponse(BaseModel):
    amount: float = Field(description="Forecasted amount")
    justification: str = Field(description="Justification of forecast")

class ForecastAgent:
    """
    AI agent that generates forecasts based on given dataframe with historical data
    """
    def __init__(self):
        """
        Agent initialization

        """
        self.agent =  Agent(
        name="forecast_agent",
        model=config.FORECAST_MODEL,
        tools=[],
        instructions="""
        You are a financial planner. 
        You are given a dataframe with historical data of cash flow. 
        You need to generate a forecast for the next month. 
        You should return only forecasted amount and justification of your forecast.
        """,
        output_type=ForecastAgentResponse
    )
        
    async def build_cashflow_forecast(self, df: pd.DataFrame, last_period:  Any) -> pd.DataFrame:
        """
        Generates forecast for next month across all categories

        Args:
            df: DataFrame with data (category, month, amount)
            last_period: last month

        Returns:
            DataFrame with forecast:
            - period: forecast period (e.g., "2024-12")
            - category: category
            - forecast_amount: AI forecast
            - adjustment: 0 (default)
            - final_amount: = forecast_amount
        """

        # # Old version
        # month_cols = [col for col in df.columns if '_' not in str(col) and col != 'category']

        # month_dates = pd.to_datetime(month_cols, errors='coerce')

        # filtered_indicies = [i for i, date in enumerate(month_dates) if date < last_period]

        # fitered_months = [month_cols[i] for i in filtered_indicies]

        # df_filtered = df[['category'] + fitered_months]

        # Create a new column for forecasts
        forecasts = []
        comments = []

        for index, row in df.iterrows():
            category = row['category']
            # Extract all numeric values (excluding category column)
            values = [v for k, v in row.items() if k != 'category']
            prepared_values = analyze_historical_data(values)

            # Create a text message for the AI agent
            message = f"""
Category: {category}
Historical values with analysis: {prepared_values}

Based on this historical cash flow data, and additional statistical data 
povieded from preliminary analysis, provide a numerical forecast for the next period.
Return ONLY the number, without any currency symbols, text or explanation.
"""

            with trace("make_forecast"):
                result = await Runner.run(
                    self.agent,
                    message
                )

            # Parse the result
            try:
                forecast_value = float(result.final_output.amount.strip())
            except (ValueError, AttributeError):
                # If parsing fails, use the last value as fallback
                forecast_value = values[-1] if values else 0

            forecasts.append(forecast_value)
            comments.append(result.final_output.justification)

        # Add forecast column to dataframe
        df['ai_forecast'] = forecasts
        df['ai_comments'] = comments

        return df


# Standalone function for easy import from app.py
def build_cashflow_forecast(df: pd.DataFrame, last_period: Any) -> pd.DataFrame:
    """
    Wrapper function to build cash flow forecast using ForecastAgent.

    Args:
        df: DataFrame with historical data
        last_period: Last period date

    Returns:
        DataFrame with forecast column populated
    """
    import asyncio

    agent = ForecastAgent()

    # Run async function in sync context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(agent.build_cashflow_forecast(df, last_period))

            



            
        
        