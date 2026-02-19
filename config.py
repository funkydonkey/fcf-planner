"""
Cash Flow Planner application configuration
"""
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# class ConfigParameters:

# === OpenAI Configuration ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# === Database Configuration ===
DB_URL = os.getenv("DB_URL", "sqlite:///cashflow.db")

# === Forecast Configuration ===
FORECAST_LOOKBACK_MONTHS = int(os.getenv("FORECAST_LOOKBACK_MONTHS", "3"))

# === Historical Data Column Names ===
HIST_COL_DATE = os.getenv("HIST_COL_DATE", "date")
HIST_COL_CATEGORY = os.getenv("HIST_COL_CATEGORY", "category")
HIST_COL_AMOUNT = os.getenv("HIST_COL_AMOUNT", "amount")

# === AI Agent Configuration ===
# Model for forecasting
FORECAST_MODEL = "gpt-4o-mini"

# Generation temperature (0 = deterministic, 1 = creative)
FORECAST_TEMPERATURE = 0.2

# === Driver-Based Forecasting Configuration ===
# Default forecast periods (months)
DEFAULT_FORECAST_PERIODS = int(os.getenv("DEFAULT_FORECAST_PERIODS", "12"))

# Monte Carlo simulation count
MONTE_CARLO_SIMULATIONS = int(os.getenv("MONTE_CARLO_SIMULATIONS", "1000"))
