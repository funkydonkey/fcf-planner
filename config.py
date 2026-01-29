"""
Конфигурация приложения Cash Flow Planner
"""
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
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
# Модель для прогнозирования
FORECAST_MODEL = "gpt-4o-mini"

# Температура для генерации (0 = детерминированный, 1 = креативный)
FORECAST_TEMPERATURE = 0.2
