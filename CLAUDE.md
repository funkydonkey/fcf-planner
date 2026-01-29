# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an educational project for learning **OpenAI Agents SDK** and **AutoGen** through building a cash flow forecasting application. The project uses a Streamlit web interface with SQLite database and AI-powered forecasting agents.

## Key Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add OPENAI_API_KEY
```

### Running the Application
```bash
# Start Streamlit app (serves on http://localhost:8501)
streamlit run app.py
```

### Testing
```bash
# Test forecast agent
python test_forecast_full.py

# Test data loading
python test_load_cashflow.py

# Test Streamlit imports
python test_streamlit_imports.py
```

## Architecture Overview

### Core Design Pattern

The project follows a **separation of concerns** pattern where infrastructure is ready-made and students implement only the AI agents:

```
User uploads file → core/io_historical.py parses data
                 → app.py displays in Streamlit
                 → User clicks "Calculate forecast"
                 → ai_agents/forecast_agent.py generates predictions
                 → app.py shows results in editable table
                 → core/db.py saves scenario to SQLite
```

### Module Responsibilities

**`core/` - Infrastructure (Complete)**
- `io_historical.py`: Loads CSV/Excel files in two formats:
  - Long format: `date, category, amount` (one row per transaction)
  - Wide format: `category` + month columns (pivoted by month)
  - Auto-detects format and normalizes to long format
  - Handles Russian/English month names
- `data_transform.py`: Converts between long/wide formats
  - `pivot_to_wide_format()`: Transforms data for display
  - `add_forecast_columns()`: Adds forecast columns to wide format
  - `get_next_month_name()`: Calculates next month for forecasting
- `db.py`: SQLAlchemy database operations
  - `save_scenario()`: Atomic transaction with scenario + lines
  - `get_scenarios_list()`: Returns all scenarios with totals
  - `get_scenario_lines()`: Returns detail lines for a scenario
- `models.py`: SQLAlchemy ORM models
  - `Scenario`: Header table (id, created_at, forecast_period, description)
  - `ScenarioLine`: Detail table (category, forecast_amount, adjustment_amount, final_amount)
  - One-to-many relationship with cascade delete

**`ai_agents/` - AI Implementation (Student work)**
- `forecast_agent.py`: OpenAI Agents SDK implementation
  - Uses `ForecastAgent` class with async `build_cashflow_forecast()` method
  - Processes each category row-by-row from wide format DataFrame
  - Returns same DataFrame with `ai_forecast` column added
  - Wrapper function handles async/sync conversion for Streamlit compatibility
  - Currently implemented using OpenAI Agents SDK (not plain API)

**`app.py` - Streamlit Application**
- Two-tab interface: "Прогноз" (Forecast) and "История" (History)
- File upload → auto-detection of format
- Displays data in wide format with editable forecast columns
- "Рассчитать прогноз с AI" button calls `ai_agents.forecast_agent.build_cashflow_forecast()`
- Session state management to preserve edits across reruns
- Form-based scenario saving with description

### Data Flow Details

**Wide Format Structure:**
```
category | Jan 2025 | Feb 2025 | ... | Dec 2025_Прогноз | Dec 2025_Корректировки | Dec 2025_Итого
---------|----------|----------|-----|------------------|------------------------|----------------
Revenue  | 1000000  | 1100000  | ... | 1200000          | 0                      | 1200000
```

**AI Agent Expected Behavior:**
- Input: Wide format DataFrame with historical month columns + category column
- Processing: For each row (category), extract values, send to AI for forecast
- Output: Same DataFrame with new `ai_forecast` column populated
- The `app.py` then copies `ai_forecast` → `{next_month}_Прогноз` column

**Session State Management:**
- `st.session_state['df_history']`: Original long-format data from file
- `st.session_state['df_wide']`: Wide-format display data
- `st.session_state['edited_df']`: User-edited version after forecast/manual changes
- `st.session_state['last_uploaded_file']`: Filename for change detection
- `st.session_state['next_month']`: Calculated forecast period name

### Important Implementation Notes

1. **Async/Sync Bridge**: The `forecast_agent.py` uses async OpenAI Agents SDK but provides sync wrapper for Streamlit:
   ```python
   async def build_cashflow_forecast(...)  # Async implementation
   def build_cashflow_forecast(...)        # Sync wrapper using asyncio.run_until_complete()
   ```

2. **DataFrame Column Detection**: AI agent extracts numeric columns by filtering `k != 'category'`:
   ```python
   values = [v for k, v in row.items() if k != 'category']
   ```

3. **Error Handling Philosophy**:
   - File loading errors → show user-friendly message with details in expander
   - AI forecast errors → show traceback in expander for debugging
   - Missing modules → warn about missing implementation (commented out)

4. **Database Transactions**: `save_scenario()` uses flush() to get scenario ID before adding lines, with rollback on any error

5. **Month Name Translation**: Russian month names used in UI:
   - `data_transform.py` handles Янв/Фев/Мар etc.
   - `io_historical.py` auto-detects and parses both English/Russian

## Configuration

**Environment Variables (`.env`):**
- `OPENAI_API_KEY`: Required for AI forecasting
- `DB_URL`: Database connection (default: `sqlite:///cashflow.db`)
- `FORECAST_LOOKBACK_MONTHS`: How many historical months to analyze (default: 3)
- `HIST_COL_DATE`, `HIST_COL_CATEGORY`, `HIST_COL_AMOUNT`: Column name mappings for long-format files

**Python Config (`config.py`):**
- `FORECAST_MODEL`: Default "gpt-4o-mini"
- `FORECAST_TEMPERATURE`: Default 0.2 (deterministic)
- Uses `python-dotenv` for .env loading

## Dependencies

Key packages (from `requirements.txt`):
- `streamlit==1.52.2`: Web interface
- `pandas==2.3.3`: Data manipulation
- `openpyxl==3.1.2`: Excel file support
- `sqlalchemy==2.0.27`: Database ORM
- `openai>=1.57`: OpenAI API client
- `openai-agents>=0.4.2`: OpenAI Agents SDK (newer framework)
- `pyautogen==0.6.0`: Multi-agent framework (for Task 2)
- `python-dotenv==1.0.1`: Environment variable management

## Educational Context

This is a learning project with two tasks for students:

**Task 1** (`tasks/TASK_01_FORECAST_AGENT.md`): Implement basic OpenAI agent for forecasting
- Already completed in current codebase
- Uses OpenAI Agents SDK with `ForecastAgent` class

**Task 2** (`tasks/TASK_02_MULTIAGENT_SYSTEM.md`): Create multi-agent system with AutoGen
- Three agents: Analyst, Critic, Optimizer
- GroupChat pattern for agent collaboration
- Not yet implemented

When working on this project, remember that the infrastructure is intentionally complete so students focus only on AI agent implementation. The `core/` module should not need modifications for the basic learning tasks.
