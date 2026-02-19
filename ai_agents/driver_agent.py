"""
DriverAgent - analyzes financial drivers and compares with industry benchmarks.

Analyzes DSO, DPO, DIO and CCC metrics, compares them against industry
benchmarks, and provides actionable recommendations for cash flow improvement.
"""

import config
from agents import Runner, Agent, trace
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os

load_dotenv()


class DriverRecommendation(BaseModel):
    driver_name: str = Field(description="Name of the driver (DSO, DPO, DIO, etc)")
    current_value: float = Field(description="Current value")
    recommended_value: float = Field(description="Recommended value")
    industry_benchmark: float = Field(description="Industry benchmark value")
    impact_on_cashflow: str = Field(description="Impact description on cash flow")
    reasoning: str = Field(description="Reasoning for recommendation")


class DriverAnalysisResponse(BaseModel):
    recommendations: List[DriverRecommendation] = Field(description="List of recommendations")
    overall_assessment: str = Field(description="Overall assessment")
    risk_factors: List[str] = Field(description="Risk factors identified")
    opportunities: List[str] = Field(description="Opportunities identified")


class DriverAgent:
    """
    AI agent that analyzes financial drivers (DSO, DPO, DIO) and compares
    them with industry benchmarks to provide cash flow improvement recommendations.
    """

    def __init__(self):
        self.agent = Agent(
            name="driver_analyst",
            model=config.FORECAST_MODEL,
            tools=[],
            instructions="""
            You are a financial analyst specializing in working capital and cash flow analysis.

            Your tasks:
            1. Analyze current driver values (DSO, DPO, DIO)
            2. Compare with industry benchmarks
            3. Identify potential problems and opportunities
            4. Give specific recommendations for improving cash flow

            Key principles:
            - High DSO = cash stuck in receivables
            - Low DPO = paying suppliers too quickly
            - High DIO = too much capital in inventory
            - CCC = DSO + DIO - DPO (lower is better)

            Respond in English with specific numbers and actionable advice.
            """,
            output_type=DriverAnalysisResponse,
        )
        self.benchmarks = self._load_benchmarks()

    def _load_benchmarks(self) -> dict:
        """Load industry benchmarks from JSON file."""
        benchmarks_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'industry_benchmarks.json'
        )
        try:
            with open(benchmarks_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "retail": {"dso": 15, "dpo": 30, "dio": 45},
                "manufacturing": {"dso": 45, "dpo": 40, "dio": 60},
                "services": {"dso": 35, "dpo": 25, "dio": 5},
                "technology": {"dso": 50, "dpo": 35, "dio": 20},
                "healthcare": {"dso": 55, "dpo": 35, "dio": 30},
            }

    async def analyze_drivers(
        self,
        drivers: dict,
        industry: str,
        historical_data: Optional[dict] = None,
    ) -> DriverAnalysisResponse:
        """Analyze current financial drivers and provide recommendations."""
        benchmark = self.benchmarks.get(
            industry, self.benchmarks.get("services", {})
        )
        ccc = drivers['dso_days'] + drivers['dio_days'] - drivers['dpo_days']

        message = f"""
Analyze current drivers and provide recommendations:

CURRENT VALUES:
- DSO: {drivers['dso_days']} days
- DPO: {drivers['dpo_days']} days
- DIO: {drivers['dio_days']} days
- CCC: {ccc} days

INDUSTRY BENCHMARKS for "{industry}":
- DSO: {benchmark.get('dso', 'N/A')} days
- DPO: {benchmark.get('dpo', 'N/A')} days
- DIO: {benchmark.get('dio', 'N/A')} days

{f'HISTORICAL CONTEXT: {json.dumps(historical_data, ensure_ascii=False)}' if historical_data else ''}

Give specific recommendations for each driver and estimate potential cash flow impact.
"""

        with trace("analyze_drivers"):
            result = await Runner.run(self.agent, message)

        return result.final_output


def analyze_drivers_sync(
    drivers: dict,
    industry: str,
    historical_data: Optional[dict] = None,
) -> DriverAnalysisResponse:
    """Synchronous wrapper for DriverAgent.analyze_drivers()."""
    import asyncio

    agent = DriverAgent()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(
        agent.analyze_drivers(drivers, industry, historical_data)
    )
