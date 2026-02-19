# 📋 Техническое Задание: Cash Flow Planner v2.0
## Driver-Based Forecasting с AI

**Версия:** 2.0  
**Дата:** Февраль 2026  
**Автор:** Andrey + Claude  

---

## 1. 🎯 Цель проекта

Развить текущий Cash Flow Planner от простого trend-based прогнозирования к профессиональному **driver-based forecasting** с использованием AI.

### Текущее состояние (v1.0)
- ✅ Загрузка исторических данных (CSV/Excel)
- ✅ Простой AI-прогноз на основе тренда и среднего
- ✅ Ручные корректировки
- ✅ Сохранение сценариев в БД

### Целевое состояние (v2.0)
- 🎯 Ввод финансовых драйверов (DSO, DPO, DIO, Revenue Growth и др.)
- 🎯 Расчёт CCC (Cash Conversion Cycle) 
- 🎯 AI-прогноз с учётом драйверов
- 🎯 Сценарное моделирование (what-if analysis)
- 🎯 Визуализация и объяснение прогноза

---

## 2. 📊 Финансовые драйверы Cash Flow

### 2.1 Основные драйверы Working Capital

```
┌─────────────────────────────────────────────────────────────┐
│                   CASH CONVERSION CYCLE                      │
│                                                              │
│   CCC = DSO + DIO - DPO                                     │
│                                                              │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                │
│   │   DIO   │ +  │   DSO   │ -  │   DPO   │ = CCC          │
│   │ Запасы  │    │ Дебитор │    │ Кредит  │                │
│   └─────────┘    └─────────┘    └─────────┘                │
│                                                              │
│   Чем меньше CCC → тем быстрее деньги возвращаются         │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Полный список драйверов

| Категория | Драйвер | Влияние на Cash Flow |
|-----------|---------|---------------------|
| **Операционные** | Revenue Growth % | ↑ Revenue → ↑ AR → ↓ Cash (временно) |
| | Gross Margin % | ↑ Margin → ↑ Operating Cash |
| | COGS % | ↑ COGS → ↓ Operating Cash |
| **Working Capital** | DSO (дни) | ↑ DSO → ↓ Cash (деньги в дебиторке) |
| | DPO (дни) | ↑ DPO → ↑ Cash (отсрочка платежей) |
| | DIO (дни) | ↑ DIO → ↓ Cash (деньги в запасах) |
| **CapEx** | CapEx % от Revenue | ↑ CapEx → ↓ Cash |
| **Финансовые** | Interest Rate % | ↑ Rate → ↓ Cash (процентные расходы) |
| | Debt Repayment | Погашение долга → ↓ Cash |
| **Сезонность** | Seasonal Factor | Коэффициент по месяцам |

### 2.3 Формулы расчёта Cash Flow

```python
# Operating Cash Flow (Indirect Method)
Operating_CF = Net_Income + Depreciation - Δ_Working_Capital

# Где изменение Working Capital:
Δ_Working_Capital = Δ_AR + Δ_Inventory - Δ_AP

# AR (Accounts Receivable) через DSO:
AR = (Revenue / 365) * DSO

# AP (Accounts Payable) через DPO:
AP = (COGS / 365) * DPO

# Inventory через DIO:
Inventory = (COGS / 365) * DIO

# Free Cash Flow
Free_CF = Operating_CF - CapEx
```

---

## 3. 🏗️ Архитектура системы v2.0

### 3.1 Высокоуровневая архитектура

```
┌────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Загрузка │  │ Драйверы │  │ Сценарии │  │ Дашборд  │      │
│  │  данных  │  │  ввод    │  │  what-if │  │          │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┘
        │             │             │             │
        v             v             v             v
┌────────────────────────────────────────────────────────────────┐
│                      CORE SERVICES                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ DataLoader   │  │ DriverEngine │  │ Forecaster   │         │
│  │              │  │              │  │              │         │
│  │ - CSV/Excel  │  │ - DSO/DPO/DIO│  │ - AI Agent   │         │
│  │ - Validation │  │ - CCC Calc   │  │ - Scenarios  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼─────────────────┼─────────────────┼─────────────────┘
          │                 │                 │
          v                 v                 v
┌────────────────────────────────────────────────────────────────┐
│                         AI LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Multi-Agent System                     │ │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐  │ │
│  │  │ Analyst │ → │ Driver  │ → │Forecast │ → │Explainer│  │ │
│  │  │ Agent   │   │ Agent   │   │ Agent   │   │ Agent   │  │ │
│  │  └─────────┘   └─────────┘   └─────────┘   └─────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
          │
          v
┌────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   SQLite     │  │   Scenarios  │  │   History    │         │
│  │   Database   │  │   Storage    │  │   Cache      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

### 3.2 Структура проекта v2.0

```
fcf_planner/
├── app.py                          # Главное Streamlit приложение
├── config.py                       # Конфигурация
│
├── core/                           # Инфраструктура (существует)
│   ├── io_historical.py            # Загрузка данных
│   ├── data_transform.py           # Трансформации
│   ├── db.py                       # База данных
│   └── models.py                   # SQLAlchemy модели
│
├── drivers/                        # 🆕 НОВЫЙ МОДУЛЬ
│   ├── __init__.py
│   ├── models.py                   # Pydantic модели драйверов
│   ├── calculator.py               # Расчёт DSO/DPO/DIO/CCC
│   ├── validator.py                # Валидация входных данных
│   └── defaults.py                 # Дефолтные значения по индустриям
│
├── forecasting/                    # 🆕 НОВЫЙ МОДУЛЬ
│   ├── __init__.py
│   ├── driver_based.py             # Driver-based прогнозирование
│   ├── scenarios.py                # Сценарное моделирование
│   └── sensitivity.py              # Анализ чувствительности
│
├── ai_agents/                      # AI агенты (расширяем)
│   ├── __init__.py
│   ├── forecast_agent.py           # Существующий агент
│   ├── forecast_analyzer.py        # Статистический анализ
│   ├── driver_agent.py             # 🆕 Анализ драйверов
│   ├── scenario_agent.py           # 🆕 Генерация сценариев
│   └── explainer_agent.py          # 🆕 Объяснение прогнозов
│
├── ui/                             # 🆕 UI компоненты
│   ├── __init__.py
│   ├── driver_input.py             # Формы ввода драйверов
│   ├── scenario_builder.py         # Построитель сценариев
│   └── dashboard.py                # Визуализации
│
└── data/
    ├── sample_cashflow.csv
    └── industry_benchmarks.json    # 🆕 Бенчмарки по индустриям
```

---

## 4. 📝 Модели данных

### 4.1 Pydantic модели драйверов

```python
# drivers/models.py

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class Industry(str, Enum):
    """Индустрии для бенчмарков"""
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"

class WorkingCapitalDrivers(BaseModel):
    """Драйверы оборотного капитала"""
    dso_days: float = Field(ge=0, le=365, description="Days Sales Outstanding")
    dpo_days: float = Field(ge=0, le=365, description="Days Payable Outstanding")
    dio_days: float = Field(ge=0, le=365, description="Days Inventory Outstanding")
    
    @property
    def ccc_days(self) -> float:
        """Cash Conversion Cycle"""
        return self.dso_days + self.dio_days - self.dpo_days

class RevenueDrivers(BaseModel):
    """Драйверы выручки"""
    revenue_growth_pct: float = Field(ge=-100, le=500, description="Рост выручки %")
    gross_margin_pct: float = Field(ge=0, le=100, description="Валовая маржа %")
    seasonality_factors: Optional[List[float]] = Field(
        default=None, 
        description="12 коэффициентов сезонности (по месяцам)"
    )

class CapExDrivers(BaseModel):
    """Драйверы капитальных затрат"""
    capex_pct_of_revenue: float = Field(ge=0, le=100, description="CapEx как % от выручки")
    depreciation_years: int = Field(ge=1, le=40, description="Срок амортизации")

class FinancingDrivers(BaseModel):
    """Финансовые драйверы"""
    interest_rate_pct: float = Field(ge=0, le=50, description="Процентная ставка")
    debt_to_equity: float = Field(ge=0, le=10, description="Долг/Капитал")
    tax_rate_pct: float = Field(ge=0, le=50, description="Ставка налога")

class ForecastDrivers(BaseModel):
    """Полный набор драйверов для прогноза"""
    working_capital: WorkingCapitalDrivers
    revenue: RevenueDrivers
    capex: Optional[CapExDrivers] = None
    financing: Optional[FinancingDrivers] = None
    industry: Optional[Industry] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "working_capital": {
                    "dso_days": 45,
                    "dpo_days": 30,
                    "dio_days": 60
                },
                "revenue": {
                    "revenue_growth_pct": 10,
                    "gross_margin_pct": 35
                }
            }
        }
```

### 4.2 SQLAlchemy модели (расширение)

```python
# core/models.py (добавляем)

class ScenarioDrivers(Base):
    """Драйверы для сценария"""
    __tablename__ = 'scenario_drivers'
    
    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey('scenarios.id'), nullable=False)
    
    # Working Capital
    dso_days = Column(Float, nullable=False)
    dpo_days = Column(Float, nullable=False)
    dio_days = Column(Float, nullable=False)
    ccc_days = Column(Float, nullable=False)  # Расчётное
    
    # Revenue
    revenue_growth_pct = Column(Float, nullable=False)
    gross_margin_pct = Column(Float, nullable=False)
    
    # Optional
    capex_pct = Column(Float, nullable=True)
    interest_rate_pct = Column(Float, nullable=True)
    
    scenario = relationship("Scenario", back_populates="drivers")
```

---

## 5. 🤖 AI Агенты

### 5.1 Архитектура Multi-Agent System

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│              (Координирует работу агентов)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        v                 v                 v
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ ANALYST AGENT │ │ DRIVER AGENT  │ │ EXPLAINER     │
│               │ │               │ │ AGENT         │
│ - Анализ      │ │ - Валидация   │ │               │
│   истории     │ │   драйверов   │ │ - Текстовое   │
│ - Выявление   │ │ - Сравнение   │ │   объяснение  │
│   паттернов   │ │   с бенчмарк. │ │   прогноза    │
│ - Аномалии    │ │ - Рекоменд.   │ │ - Риски       │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          v
                ┌───────────────────┐
                │  FORECAST AGENT   │
                │                   │
                │ - Driver-based    │
                │   расчёты         │
                │ - Сценарии        │
                │ - Monte Carlo     │
                └───────────────────┘
```

### 5.2 Driver Agent (новый)

```python
# ai_agents/driver_agent.py

from agents import Agent, Runner
from pydantic import BaseModel
from typing import List, Optional
import json

class DriverRecommendation(BaseModel):
    """Рекомендация по драйверу"""
    driver_name: str
    current_value: float
    recommended_value: float
    industry_benchmark: float
    impact_on_cashflow: str
    reasoning: str

class DriverAnalysisResponse(BaseModel):
    """Ответ агента анализа драйверов"""
    recommendations: List[DriverRecommendation]
    overall_assessment: str
    risk_factors: List[str]
    opportunities: List[str]

class DriverAgent:
    """
    AI агент для анализа финансовых драйверов
    и сравнения с индустриальными бенчмарками
    """
    
    def __init__(self):
        self.agent = Agent(
            name="driver_analyst",
            model="gpt-4o-mini",
            instructions="""
            Ты - финансовый аналитик, специализирующийся на анализе 
            оборотного капитала и cash flow.
            
            Твои задачи:
            1. Анализировать текущие значения драйверов (DSO, DPO, DIO)
            2. Сравнивать с индустриальными бенчмарками
            3. Выявлять потенциальные проблемы и возможности
            4. Давать конкретные рекомендации по улучшению cash flow
            
            При анализе учитывай:
            - Высокий DSO = деньги застряли в дебиторке
            - Низкий DPO = платим слишком быстро
            - Высокий DIO = слишком много запасов
            - CCC = DSO + DIO - DPO (чем меньше, тем лучше)
            
            Отвечай структурированно с конкретными цифрами.
            """,
            output_type=DriverAnalysisResponse
        )
        
        # Загружаем бенчмарки
        self.benchmarks = self._load_benchmarks()
    
    def _load_benchmarks(self) -> dict:
        """Загрузить индустриальные бенчмарки"""
        return {
            "retail": {"dso": 15, "dpo": 30, "dio": 45},
            "manufacturing": {"dso": 45, "dpo": 40, "dio": 60},
            "services": {"dso": 35, "dpo": 25, "dio": 5},
            "technology": {"dso": 50, "dpo": 35, "dio": 20},
        }
    
    async def analyze_drivers(
        self, 
        drivers: dict, 
        industry: str,
        historical_data: Optional[dict] = None
    ) -> DriverAnalysisResponse:
        """
        Анализ драйверов с рекомендациями
        """
        benchmark = self.benchmarks.get(industry, self.benchmarks["services"])
        
        message = f"""
        Проанализируй текущие драйверы компании и дай рекомендации:
        
        ТЕКУЩИЕ ЗНАЧЕНИЯ:
        - DSO: {drivers['dso_days']} дней
        - DPO: {drivers['dpo_days']} дней  
        - DIO: {drivers['dio_days']} дней
        - CCC: {drivers['dso_days'] + drivers['dio_days'] - drivers['dpo_days']} дней
        
        БЕНЧМАРКИ ДЛЯ ИНДУСТРИИ "{industry}":
        - DSO: {benchmark['dso']} дней
        - DPO: {benchmark['dpo']} дней
        - DIO: {benchmark['dio']} дней
        
        {f"ИСТОРИЧЕСКАЯ ДИНАМИКА: {json.dumps(historical_data)}" if historical_data else ""}
        
        Дай конкретные рекомендации по улучшению каждого драйвера
        и оцени потенциальное влияние на cash flow.
        """
        
        result = await Runner.run(self.agent, message)
        return result.final_output
```

### 5.3 Explainer Agent (новый)

```python
# ai_agents/explainer_agent.py

from agents import Agent, Runner
from pydantic import BaseModel
from typing import List

class ForecastExplanation(BaseModel):
    """Объяснение прогноза"""
    summary: str
    key_drivers: List[str]
    assumptions: List[str]
    risks: List[str]
    confidence_level: str  # "high", "medium", "low"
    recommendation: str

class ExplainerAgent:
    """
    AI агент для объяснения прогнозов 
    человекочитаемым языком
    """
    
    def __init__(self):
        self.agent = Agent(
            name="forecast_explainer",
            model="gpt-4o-mini",
            instructions="""
            Ты - финансовый консультант, который объясняет 
            сложные прогнозы простым языком для менеджмента.
            
            Твоя задача:
            1. Резюмировать прогноз в 2-3 предложениях
            2. Выделить ключевые драйверы изменений
            3. Перечислить основные допущения
            4. Предупредить о рисках
            5. Оценить уровень уверенности в прогнозе
            6. Дать итоговую рекомендацию
            
            Используй простой язык без финансового жаргона.
            Приводи конкретные цифры и проценты.
            """,
            output_type=ForecastExplanation
        )
    
    async def explain_forecast(
        self,
        forecast_data: dict,
        drivers: dict,
        historical_context: dict
    ) -> ForecastExplanation:
        """Генерирует объяснение прогноза"""
        
        message = f"""
        Объясни этот прогноз cash flow для руководства:
        
        ПРОГНОЗ:
        {forecast_data}
        
        ИСПОЛЬЗОВАННЫЕ ДРАЙВЕРЫ:
        {drivers}
        
        ИСТОРИЧЕСКИЙ КОНТЕКСТ:
        {historical_context}
        
        Объясни простым языком, что означает этот прогноз,
        какие факторы на него влияют и что нужно учитывать.
        """
        
        result = await Runner.run(self.agent, message)
        return result.final_output
```

---

## 6. 🔢 Алгоритмы расчёта

### 6.1 Driver-Based Cash Flow Calculation

```python
# forecasting/driver_based.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from drivers.models import ForecastDrivers

class DriverBasedForecaster:
    """
    Прогнозирование Cash Flow на основе драйверов
    """
    
    def __init__(self, drivers: ForecastDrivers):
        self.drivers = drivers
    
    def forecast_working_capital(
        self, 
        revenue: float, 
        cogs: float
    ) -> Dict[str, float]:
        """
        Расчёт компонентов Working Capital
        
        Args:
            revenue: Выручка за период
            cogs: Себестоимость за период
            
        Returns:
            Dict с AR, AP, Inventory и их изменениями
        """
        wc = self.drivers.working_capital
        
        # Расчёт балансовых статей
        accounts_receivable = (revenue / 365) * wc.dso_days
        accounts_payable = (cogs / 365) * wc.dpo_days
        inventory = (cogs / 365) * wc.dio_days
        
        # Net Working Capital
        nwc = accounts_receivable + inventory - accounts_payable
        
        return {
            "accounts_receivable": accounts_receivable,
            "accounts_payable": accounts_payable,
            "inventory": inventory,
            "net_working_capital": nwc,
            "ccc_days": wc.ccc_days
        }
    
    def forecast_operating_cashflow(
        self,
        revenue: float,
        previous_revenue: float,
        cogs: float,
        previous_cogs: float,
        depreciation: float = 0
    ) -> Dict[str, float]:
        """
        Расчёт Operating Cash Flow (косвенный метод)
        
        OCF = Net Income + Depreciation - Δ Working Capital
        """
        # Текущий и предыдущий Working Capital
        current_wc = self.forecast_working_capital(revenue, cogs)
        previous_wc = self.forecast_working_capital(previous_revenue, previous_cogs)
        
        # Изменение Working Capital
        delta_wc = current_wc["net_working_capital"] - previous_wc["net_working_capital"]
        
        # Net Income (упрощённо)
        gross_profit = revenue * (self.drivers.revenue.gross_margin_pct / 100)
        
        # Operating Cash Flow
        operating_cf = gross_profit + depreciation - delta_wc
        
        return {
            "gross_profit": gross_profit,
            "depreciation": depreciation,
            "delta_working_capital": delta_wc,
            "delta_ar": current_wc["accounts_receivable"] - previous_wc["accounts_receivable"],
            "delta_ap": current_wc["accounts_payable"] - previous_wc["accounts_payable"],
            "delta_inventory": current_wc["inventory"] - previous_wc["inventory"],
            "operating_cashflow": operating_cf
        }
    
    def forecast_free_cashflow(
        self,
        operating_cf: float,
        revenue: float
    ) -> Dict[str, float]:
        """
        Расчёт Free Cash Flow
        
        FCF = Operating CF - CapEx
        """
        if self.drivers.capex:
            capex = revenue * (self.drivers.capex.capex_pct_of_revenue / 100)
        else:
            capex = 0
        
        fcf = operating_cf - capex
        
        return {
            "capex": capex,
            "free_cashflow": fcf
        }
    
    def generate_forecast(
        self,
        historical_data: pd.DataFrame,
        periods: int = 12
    ) -> pd.DataFrame:
        """
        Генерация полного прогноза на N периодов
        
        Args:
            historical_data: DataFrame с историей (revenue, cogs, ...)
            periods: Количество периодов прогноза
            
        Returns:
            DataFrame с прогнозом
        """
        # Базовые значения из последнего периода
        last_revenue = historical_data['revenue'].iloc[-1]
        last_cogs = historical_data['cogs'].iloc[-1] if 'cogs' in historical_data else last_revenue * 0.65
        
        forecasts = []
        
        for i in range(periods):
            # Рост выручки
            growth = 1 + (self.drivers.revenue.revenue_growth_pct / 100) / 12
            revenue = last_revenue * growth
            cogs = revenue * (1 - self.drivers.revenue.gross_margin_pct / 100)
            
            # Сезонность
            if self.drivers.revenue.seasonality_factors:
                month_idx = i % 12
                revenue *= self.drivers.revenue.seasonality_factors[month_idx]
            
            # Working Capital
            wc = self.forecast_working_capital(revenue, cogs)
            
            # Operating CF
            ocf = self.forecast_operating_cashflow(
                revenue, last_revenue,
                cogs, last_cogs,
                depreciation=revenue * 0.02  # ~2% depreciation
            )
            
            # Free CF
            fcf = self.forecast_free_cashflow(ocf["operating_cashflow"], revenue)
            
            forecasts.append({
                "period": i + 1,
                "revenue": revenue,
                "cogs": cogs,
                **wc,
                **ocf,
                **fcf
            })
            
            # Обновляем для следующего периода
            last_revenue = revenue
            last_cogs = cogs
        
        return pd.DataFrame(forecasts)
```

### 6.2 Сценарное моделирование

```python
# forecasting/scenarios.py

from dataclasses import dataclass
from typing import List, Dict
import numpy as np
from drivers.models import ForecastDrivers
from .driver_based import DriverBasedForecaster

@dataclass
class Scenario:
    """Сценарий для моделирования"""
    name: str
    description: str
    drivers: ForecastDrivers
    probability: float = 0.33  # Вероятность сценария

class ScenarioEngine:
    """
    Движок сценарного моделирования
    """
    
    def __init__(self, base_drivers: ForecastDrivers):
        self.base_drivers = base_drivers
    
    def create_scenarios(self) -> List[Scenario]:
        """
        Создание базовых сценариев: Base, Optimistic, Pessimistic
        """
        scenarios = []
        
        # Base Case
        scenarios.append(Scenario(
            name="Base Case",
            description="Текущие тренды сохраняются",
            drivers=self.base_drivers,
            probability=0.50
        ))
        
        # Optimistic
        optimistic_drivers = self.base_drivers.model_copy(deep=True)
        optimistic_drivers.working_capital.dso_days *= 0.85  # DSO -15%
        optimistic_drivers.working_capital.dpo_days *= 1.1   # DPO +10%
        optimistic_drivers.revenue.revenue_growth_pct *= 1.2 # Growth +20%
        
        scenarios.append(Scenario(
            name="Optimistic",
            description="Улучшение сбора дебиторки, рост продаж",
            drivers=optimistic_drivers,
            probability=0.25
        ))
        
        # Pessimistic
        pessimistic_drivers = self.base_drivers.model_copy(deep=True)
        pessimistic_drivers.working_capital.dso_days *= 1.2   # DSO +20%
        pessimistic_drivers.working_capital.dio_days *= 1.15  # DIO +15%
        pessimistic_drivers.revenue.revenue_growth_pct *= 0.5 # Growth -50%
        
        scenarios.append(Scenario(
            name="Pessimistic",
            description="Ухудшение платежей, замедление роста",
            drivers=pessimistic_drivers,
            probability=0.25
        ))
        
        return scenarios
    
    def run_monte_carlo(
        self, 
        historical_data, 
        n_simulations: int = 1000,
        periods: int = 12
    ) -> Dict:
        """
        Monte Carlo симуляция для оценки распределения outcomes
        
        Returns:
            Dict с percentiles и статистикой
        """
        results = []
        
        for _ in range(n_simulations):
            # Случайные отклонения драйверов
            drivers = self.base_drivers.model_copy(deep=True)
            
            # ±20% случайное отклонение
            drivers.working_capital.dso_days *= np.random.uniform(0.8, 1.2)
            drivers.working_capital.dpo_days *= np.random.uniform(0.8, 1.2)
            drivers.working_capital.dio_days *= np.random.uniform(0.8, 1.2)
            drivers.revenue.revenue_growth_pct *= np.random.uniform(0.5, 1.5)
            
            forecaster = DriverBasedForecaster(drivers)
            forecast = forecaster.generate_forecast(historical_data, periods)
            
            # Сохраняем итоговый FCF
            total_fcf = forecast['free_cashflow'].sum()
            results.append(total_fcf)
        
        results = np.array(results)
        
        return {
            "mean": results.mean(),
            "std": results.std(),
            "p5": np.percentile(results, 5),
            "p25": np.percentile(results, 25),
            "p50": np.percentile(results, 50),
            "p75": np.percentile(results, 75),
            "p95": np.percentile(results, 95),
            "min": results.min(),
            "max": results.max()
        }
```

---

## 7. 🖥️ UI Компоненты

### 7.1 Форма ввода драйверов

```python
# ui/driver_input.py

import streamlit as st
from drivers.models import (
    WorkingCapitalDrivers, 
    RevenueDrivers, 
    Industry,
    ForecastDrivers
)

def render_driver_input_form() -> ForecastDrivers:
    """
    Streamlit форма для ввода драйверов
    """
    st.subheader("📊 Финансовые драйверы")
    
    # Выбор индустрии (для бенчмарков)
    industry = st.selectbox(
        "Индустрия",
        options=[i.value for i in Industry],
        help="Выберите индустрию для сравнения с бенчмарками"
    )
    
    # Working Capital Drivers
    st.markdown("### 💰 Оборотный капитал")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dso = st.number_input(
            "DSO (дней)",
            min_value=0.0,
            max_value=365.0,
            value=45.0,
            help="Days Sales Outstanding - среднее время сбора дебиторки"
        )
    
    with col2:
        dpo = st.number_input(
            "DPO (дней)",
            min_value=0.0,
            max_value=365.0,
            value=30.0,
            help="Days Payable Outstanding - среднее время оплаты поставщикам"
        )
    
    with col3:
        dio = st.number_input(
            "DIO (дней)",
            min_value=0.0,
            max_value=365.0,
            value=60.0,
            help="Days Inventory Outstanding - среднее время хранения запасов"
        )
    
    # Показываем рассчитанный CCC
    ccc = dso + dio - dpo
    st.metric(
        "Cash Conversion Cycle (CCC)", 
        f"{ccc:.0f} дней",
        help="CCC = DSO + DIO - DPO. Чем меньше, тем лучше."
    )
    
    # Revenue Drivers
    st.markdown("### 📈 Выручка")
    
    col1, col2 = st.columns(2)
    
    with col1:
        revenue_growth = st.number_input(
            "Рост выручки (%)",
            min_value=-100.0,
            max_value=500.0,
            value=10.0,
            help="Ожидаемый годовой рост выручки"
        )
    
    with col2:
        gross_margin = st.number_input(
            "Валовая маржа (%)",
            min_value=0.0,
            max_value=100.0,
            value=35.0,
            help="Валовая прибыль / Выручка"
        )
    
    # CapEx (опционально)
    with st.expander("⚙️ CapEx (опционально)"):
        capex_pct = st.number_input(
            "CapEx (% от выручки)",
            min_value=0.0,
            max_value=100.0,
            value=5.0
        )
    
    # Собираем модель
    drivers = ForecastDrivers(
        working_capital=WorkingCapitalDrivers(
            dso_days=dso,
            dpo_days=dpo,
            dio_days=dio
        ),
        revenue=RevenueDrivers(
            revenue_growth_pct=revenue_growth,
            gross_margin_pct=gross_margin
        ),
        industry=Industry(industry)
    )
    
    return drivers
```

### 7.2 Дашборд визуализации

```python
# ui/dashboard.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_cashflow_dashboard(forecast_df: pd.DataFrame):
    """
    Дашборд с визуализацией прогноза Cash Flow
    """
    st.subheader("📊 Прогноз Cash Flow")
    
    # Waterfall Chart для Operating CF
    fig_waterfall = go.Figure(go.Waterfall(
        name="Operating Cash Flow",
        orientation="v",
        x=["Валовая прибыль", "Амортизация", "Δ Дебиторка", 
           "Δ Кредиторка", "Δ Запасы", "Operating CF"],
        y=[
            forecast_df['gross_profit'].sum(),
            forecast_df['depreciation'].sum(),
            -forecast_df['delta_ar'].sum(),
            forecast_df['delta_ap'].sum(),
            -forecast_df['delta_inventory'].sum(),
            0  # Total
        ],
        measure=["relative", "relative", "relative", 
                 "relative", "relative", "total"],
        connector={"line": {"color": "rgb(63, 63, 63)"}}
    ))
    
    fig_waterfall.update_layout(
        title="Формирование Operating Cash Flow",
        showlegend=False
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Line Chart: Revenue vs Cash Flow
    fig_lines = go.Figure()
    
    fig_lines.add_trace(go.Scatter(
        x=forecast_df['period'],
        y=forecast_df['revenue'],
        name="Выручка",
        line=dict(color='blue')
    ))
    
    fig_lines.add_trace(go.Scatter(
        x=forecast_df['period'],
        y=forecast_df['operating_cashflow'],
        name="Operating CF",
        line=dict(color='green')
    ))
    
    fig_lines.add_trace(go.Scatter(
        x=forecast_df['period'],
        y=forecast_df['free_cashflow'],
        name="Free CF",
        line=dict(color='orange')
    ))
    
    fig_lines.update_layout(
        title="Динамика Cash Flow",
        xaxis_title="Период",
        yaxis_title="Сумма"
    )
    
    st.plotly_chart(fig_lines, use_container_width=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Σ Operating CF",
            f"{forecast_df['operating_cashflow'].sum():,.0f}"
        )
    
    with col2:
        st.metric(
            "Σ Free CF",
            f"{forecast_df['free_cashflow'].sum():,.0f}"
        )
    
    with col3:
        st.metric(
            "Avg CCC",
            f"{forecast_df['ccc_days'].mean():.1f} дней"
        )
    
    with col4:
        conversion = (forecast_df['free_cashflow'].sum() / 
                     forecast_df['revenue'].sum() * 100)
        st.metric(
            "FCF/Revenue",
            f"{conversion:.1f}%"
        )


def render_scenario_comparison(scenarios_results: dict):
    """
    Сравнение сценариев
    """
    st.subheader("🎯 Сценарное моделирование")
    
    # Bar chart сравнения
    names = list(scenarios_results.keys())
    values = [r['total_fcf'] for r in scenarios_results.values()]
    
    fig = px.bar(
        x=names,
        y=values,
        title="Free Cash Flow по сценариям",
        labels={"x": "Сценарий", "y": "Free Cash Flow"}
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_monte_carlo_results(mc_results: dict):
    """
    Визуализация результатов Monte Carlo
    """
    st.subheader("🎲 Monte Carlo симуляция")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Среднее значение FCF", f"{mc_results['mean']:,.0f}")
        st.metric("Стандартное отклонение", f"{mc_results['std']:,.0f}")
    
    with col2:
        st.metric("5-й перцентиль (worst case)", f"{mc_results['p5']:,.0f}")
        st.metric("95-й перцентиль (best case)", f"{mc_results['p95']:,.0f}")
    
    # Confidence interval
    st.info(f"""
    📊 С 90% уверенностью FCF будет в диапазоне:
    **{mc_results['p5']:,.0f}** — **{mc_results['p95']:,.0f}**
    """)
```

---

## 8. 🗓️ План реализации

### Phase 1: MVP драйверов (2-3 недели)

| Задача | Приоритет | Сложность | Срок |
|--------|-----------|-----------|------|
| Pydantic модели драйверов | 🔴 High | ⭐⭐ | 2 дня |
| UI форма ввода драйверов | 🔴 High | ⭐⭐ | 3 дня |
| Калькулятор WC (DSO/DPO/DIO/CCC) | 🔴 High | ⭐⭐ | 2 дня |
| Driver-based forecaster | 🔴 High | ⭐⭐⭐ | 4 дня |
| Интеграция в app.py | 🔴 High | ⭐⭐ | 2 дня |
| Тестирование | 🔴 High | ⭐⭐ | 2 дня |

**Результат Phase 1:** Можно вводить драйверы и получать прогноз

### Phase 2: AI агенты (2-3 недели)

| Задача | Приоритет | Сложность | Срок |
|--------|-----------|-----------|------|
| Driver Agent (анализ драйверов) | 🟡 Medium | ⭐⭐⭐ | 4 дня |
| Explainer Agent (объяснения) | 🟡 Medium | ⭐⭐ | 3 дня |
| Industry benchmarks JSON | 🟡 Medium | ⭐ | 1 день |
| AI рекомендации в UI | 🟡 Medium | ⭐⭐ | 3 дня |
| Тестирование AI | 🟡 Medium | ⭐⭐ | 2 дня |

**Результат Phase 2:** AI анализирует драйверы и даёт рекомендации

### Phase 3: Сценарии (2 недели)

| Задача | Приоритет | Сложность | Срок |
|--------|-----------|-----------|------|
| Scenario Engine | 🟢 Low | ⭐⭐⭐ | 3 дня |
| Monte Carlo симуляция | 🟢 Low | ⭐⭐⭐ | 3 дня |
| UI сценариев | 🟢 Low | ⭐⭐ | 3 дня |
| Dashboard визуализации | 🟢 Low | ⭐⭐ | 3 дня |

**Результат Phase 3:** Полнофункциональный продукт

---

## 9. 📚 Учебные материалы

### Что изучить по ходу разработки

1. **Working Capital Management**
   - [Wall Street Prep - Working Capital](https://www.wallstreetprep.com/knowledge/working-capital/)
   - [Investopedia - Cash Conversion Cycle](https://www.investopedia.com/terms/c/cashconversioncycle.asp)

2. **Driver-Based Planning**
   - [FP&A Trends - Driver-Based Forecasting](https://fpa-trends.com/)
   - Книга: "Financial Planning & Analysis and Performance Management" - Jack Alexander

3. **Python для финансов**
   - [Pandas для финансовых данных](https://pandas.pydata.org/docs/user_guide/timeseries.html)
   - [Plotly для финансовых графиков](https://plotly.com/python/financial-charts/)

4. **AI/ML для прогнозирования**
   - [Prophet от Meta](https://facebook.github.io/prophet/)
   - [XGBoost для временных рядов](https://xgboost.readthedocs.io/)

---

## 10. ✅ Критерии успеха

### MVP (Phase 1)
- [ ] Пользователь может ввести DSO, DPO, DIO
- [ ] Система рассчитывает CCC
- [ ] Прогноз Cash Flow учитывает драйверы
- [ ] Результат сохраняется в БД

### Full Product (Phase 3)
- [ ] AI даёт рекомендации по улучшению драйверов
- [ ] Сравнение с индустриальными бенчмарками
- [ ] What-if сценарии (Optimistic/Base/Pessimistic)
- [ ] Monte Carlo для оценки рисков
- [ ] Понятные визуализации
- [ ] Текстовое объяснение прогноза

---

*Документ создан: Февраль 2026*
*Версия: 2.0-draft*