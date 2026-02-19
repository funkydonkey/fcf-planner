"""
ExplainerAgent - explains forecasts in human-readable language.

Translates complex forecast data into clear summaries for management,
highlighting key drivers, assumptions, risks, and confidence levels.
"""

import config
from agents import Runner, Agent, trace
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
import json

load_dotenv()


class ForecastExplanation(BaseModel):
    summary: str = Field(description="2-3 sentence summary of the forecast")
    key_drivers: List[str] = Field(description="Key drivers affecting the forecast")
    assumptions: List[str] = Field(description="Assumptions made in the forecast")
    risks: List[str] = Field(description="Risk factors")
    confidence_level: str = Field(description="Confidence level: high, medium, or low")
    recommendation: str = Field(description="Final recommendation for management")


class ExplainerAgent:
    """AI agent that explains forecasts in simple language for management."""

    def __init__(self):
        self.agent = Agent(
            name="forecast_explainer",
            model=config.FORECAST_MODEL,
            tools=[],
            instructions="""
            You are a financial consultant explaining complex forecasts
            in simple language for management.

            Your tasks:
            1. Summarize forecast in 2-3 sentences
            2. Highlight key change drivers
            3. List main assumptions
            4. Warn about risks
            5. Assess confidence level (high/medium/low)
            6. Give final recommendation

            Use simple language, specific numbers and percentages.
            Respond in English.
            """,
            output_type=ForecastExplanation,
        )

    async def explain_forecast(
        self,
        forecast_data: dict,
        drivers: dict,
        historical_context: dict,
    ) -> ForecastExplanation:
        """Explain a forecast in simple language for management."""
        message = f"""
Explain this cash flow forecast for management:

FORECAST DATA:
{json.dumps(forecast_data, ensure_ascii=False, indent=2)}

CURRENT DRIVERS:
- DSO: {drivers.get('dso_days', 'N/A')} days
- DPO: {drivers.get('dpo_days', 'N/A')} days
- DIO: {drivers.get('dio_days', 'N/A')} days

HISTORICAL CONTEXT:
{json.dumps(historical_context, ensure_ascii=False, indent=2)}

Provide a clear explanation with specific numbers, risk assessment, and recommendation.
"""

        with trace("explain_forecast"):
            result = await Runner.run(self.agent, message)

        return result.final_output


def explain_forecast_sync(
    forecast_data: dict,
    drivers: dict,
    historical_context: dict,
) -> ForecastExplanation:
    """Synchronous wrapper for ExplainerAgent.explain_forecast()."""
    import asyncio

    agent = ExplainerAgent()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(
        agent.explain_forecast(forecast_data, drivers, historical_context)
    )
