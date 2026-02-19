"""
ScenarioAgent - generates what-if scenarios with AI reasoning.

Suggests realistic scenarios based on current drivers, industry context,
and historical data, with probability estimates and driver adjustments.
"""

import config
from agents import Runner, Agent, trace
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict
import json

load_dotenv()


class ScenarioSuggestion(BaseModel):
    scenario_name: str = Field(description="Short name for the scenario")
    description: str = Field(description="Detailed description")
    driver_adjustments: Dict[str, float] = Field(
        description="Multiplier adjustments, e.g. {'dso_days': 0.85, 'revenue_growth_pct': 1.2}"
    )
    probability: float = Field(description="Estimated probability (0.0 to 1.0)")
    reasoning: str = Field(description="Why this scenario is plausible")


class ScenarioAnalysisResponse(BaseModel):
    scenarios: List[ScenarioSuggestion] = Field(description="Suggested scenarios")
    key_uncertainties: List[str] = Field(description="Key uncertainties")
    recommendation: str = Field(description="Overall recommendation")


class ScenarioAgent:
    """AI agent that suggests what-if scenarios based on driver analysis."""

    def __init__(self):
        self.agent = Agent(
            name="scenario_planner",
            model=config.FORECAST_MODEL,
            tools=[],
            instructions="""
            You are a strategic financial planner specializing in scenario analysis.

            Your tasks:
            1. Suggest 3-4 realistic scenarios based on current drivers
            2. For each scenario, specify driver adjustment multipliers
            3. Estimate probability of each scenario
            4. Justify each scenario
            5. Identify key uncertainties

            Scenario types:
            - Base case - most likely
            - Optimistic (upside) - favorable conditions
            - Pessimistic (downside) - unfavorable conditions
            - Stress - extreme conditions

            Multiplier conventions:
            - 1.0 = no change
            - 0.85 = -15% decrease
            - 1.2 = +20% increase

            Probabilities should sum to approximately 1.0.
            Respond in English with specific numbers.
            """,
            output_type=ScenarioAnalysisResponse,
        )

    async def suggest_scenarios(
        self,
        current_drivers: dict,
        industry: str,
        historical_summary: dict,
    ) -> ScenarioAnalysisResponse:
        """Suggest what-if scenarios based on current state."""
        ccc = (
            current_drivers.get('dso_days', 0)
            + current_drivers.get('dio_days', 0)
            - current_drivers.get('dpo_days', 0)
        )

        message = f"""
Suggest 3-4 realistic scenarios for cash flow planning:

CURRENT DRIVERS:
- DSO: {current_drivers.get('dso_days', 'N/A')} days
- DPO: {current_drivers.get('dpo_days', 'N/A')} days
- DIO: {current_drivers.get('dio_days', 'N/A')} days
- CCC: {ccc} days

INDUSTRY: {industry}

HISTORICAL CONTEXT:
{json.dumps(historical_summary, ensure_ascii=False, indent=2)}

For each scenario specify:
1. Name and description
2. Driver adjustment multipliers
3. Probability (0.0 to 1.0)
4. Reasoning
"""

        with trace("suggest_scenarios"):
            result = await Runner.run(self.agent, message)

        return result.final_output


def suggest_scenarios_sync(
    current_drivers: dict,
    industry: str,
    historical_summary: dict,
) -> ScenarioAnalysisResponse:
    """Synchronous wrapper for ScenarioAgent.suggest_scenarios()."""
    import asyncio

    agent = ScenarioAgent()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(
        agent.suggest_scenarios(current_drivers, industry, historical_summary)
    )
