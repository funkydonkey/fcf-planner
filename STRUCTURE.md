# 📁 Project Structure

Last updated: January 6, 2026

## Directory Tree

```
fcf_planner/
├── 📱 Application Core
│   ├── app.py                      # Streamlit web application
│   ├── config.py                   # Configuration management
│   └── requirements.txt            # Python dependencies
│
├── 🤖 AI Agents
│   ├── ai_agents/
│   │   ├── __init__.py
│   │   ├── forecast_agent.py       # Main forecasting agent (Task 1 - completed)
│   │   └── forecast_analyzer.py    # Statistical analysis (Task 3 - pending)
│
├── 🔧 Core Infrastructure
│   ├── core/
│   │   ├── __init__.py
│   │   ├── io_historical.py        # Data loading (CSV/Excel)
│   │   ├── data_transform.py       # Long ↔ Wide format conversion
│   │   ├── db.py                   # Database operations
│   │   └── models.py               # SQLAlchemy ORM models
│
├── 📊 Data
│   ├── data/
│   │   └── sample_cashflow.csv     # Test dataset
│
├── 🧪 Tests
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_load_cashflow.py   # Data loading tests
│   │   ├── test_interface.py       # Data transformation tests
│   │   ├── test_forecast_full.py   # Full forecast workflow test
│   │   └── test_streamlit_imports.py # Streamlit diagnostic test
│
├── 📚 Documentation
│   ├── README.md                   # Main project documentation
│   ├── CLAUDE.md                   # Claude Code guidance
│   ├── STRUCTURE.md                # This file
│   └── docs/
│       ├── START_HERE.md           # Entry point for new users
│       ├── QUICK_START.md          # 15-minute setup guide
│       ├── PROJECT_OVERVIEW.md     # Architecture overview
│       ├── LEARNING_PATH.md        # Educational roadmap
│       ├── USER_GUIDE.md           # User manual
│       ├── CHANGELOG.md            # Version history
│       └── requirements.md         # Original specification
│
├── 📝 Learning Tasks
│   ├── tasks/
│   │   ├── TASK_01_FORECAST_AGENT.md       # OpenAI Agents SDK (✅ completed)
│   │   ├── TASK_02_MULTIAGENT_SYSTEM.md    # AutoGen multi-agent
│   │   └── TASK_03_ADVANCED_FORECASTING.md # Advanced features
│
├── 🛠️ Scripts & Utilities
│   ├── scripts/
│   │   ├── __init__.py
│   │   ├── main.py                 # CLI entry point
│   │   └── pd_test.ipynb           # Jupyter notebook for experiments
│
└── ⚙️ Configuration Files
    ├── .env.example                # Environment template
    ├── .gitignore                  # Git ignore rules
    └── .python-version             # Python version specification

```

## File Count Summary

- **Python modules**: 15 files
- **Documentation**: 8 markdown files
- **Tests**: 4 test scripts
- **Data**: 1 sample dataset
- **Total directories**: 8

## Key Files Description

### Application Layer
- `app.py` (272 lines) - Two-tab Streamlit interface with file upload, forecast generation, and scenario management

### AI Agents Layer
- `ai_agents/forecast_agent.py` (128 lines) - Async OpenAI Agents SDK implementation
- `ai_agents/forecast_analyzer.py` - Statistical analysis module (to be implemented)

### Core Infrastructure
- `core/io_historical.py` (158 lines) - Dual-format data loader (long/wide CSV/Excel)
- `core/data_transform.py` (123 lines) - Data transformation utilities
- `core/db.py` (152 lines) - SQLAlchemy database operations
- `core/models.py` (45 lines) - ORM models (Scenario, ScenarioLine)

### Configuration
- `config.py` (32 lines) - Environment-based settings
- `.env.example` - Template for API keys and database config

## Import Paths

All tests include path setup for proper module resolution:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

## Running Commands

### Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

### Development
```bash
# Run application
streamlit run app.py

# Run tests
python tests/test_load_cashflow.py
python tests/test_interface.py
python tests/test_forecast_full.py
streamlit run tests/test_streamlit_imports.py
```

## Dependencies

Core dependencies:
- `streamlit==1.52.2` - Web interface
- `pandas==2.3.3` - Data manipulation
- `sqlalchemy==2.0.27` - Database ORM
- `openai>=1.57` - OpenAI API
- `openai-agents>=0.4.2` - Agents framework
- `pyautogen==0.6.0` - Multi-agent system
- `openpyxl==3.1.2` - Excel support
- `python-dotenv==1.0.1` - Environment management

## Database Schema

**scenarios** (header table)
- id (PK)
- created_at
- created_by
- forecast_period
- description

**scenario_lines** (detail table)
- id (PK)
- scenario_id (FK)
- category
- period_date
- forecast_amount
- adjustment_amount
- final_amount

## Data Flow

```
User uploads CSV/Excel
    ↓
io_historical.py parses → long format (date, category, amount)
    ↓
data_transform.py converts → wide format (category × months)
    ↓
app.py displays in editable table
    ↓
User clicks "Calculate Forecast"
    ↓
forecast_agent.py generates AI predictions
    ↓
app.py updates table with forecasts
    ↓
User can adjust manually
    ↓
db.py saves scenario to SQLite
```

## Educational Path

1. **Task 1** (✅ Completed): Basic OpenAI agent forecasting
2. **Task 2** (Pending): AutoGen multi-agent collaboration (Analyst + Critic + Optimizer)
3. **Task 3** (Pending): Advanced forecasting with statistical analysis and confidence metrics

## Notes

- Infrastructure is complete and ready for student implementations
- Tests use relative paths for portability
- All imports work correctly from test subdirectory
- Database file (`cashflow.db`) is gitignored
- Lock files moved to `.venv/` to keep root clean
