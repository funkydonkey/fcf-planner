"""
SQLAlchemy models for database
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Scenario(Base):
    """Cash flow forecast scenario"""
    __tablename__ = 'scenarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String, nullable=False, default="user")
    forecast_period = Column(String, nullable=False)  # e.g., "2025-12"
    description = Column(String, nullable=True)

    # One-to-many relationship with scenario lines
    lines = relationship("ScenarioLine", back_populates="scenario", cascade="all, delete-orphan")
    # One-to-one relationship with drivers
    drivers = relationship("ScenarioDrivers", back_populates="scenario", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scenario(id={self.id}, period={self.forecast_period}, created_at={self.created_at})>"


class ScenarioLine(Base):
    """Scenario line (forecast for one category)"""
    __tablename__ = 'scenario_lines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(Integer, ForeignKey('scenarios.id'), nullable=False)
    category = Column(String, nullable=False)
    period_date = Column(String, nullable=False)  # can be month or specific date
    forecast_amount = Column(Float, nullable=False)
    adjustment_amount = Column(Float, nullable=False, default=0.0)
    final_amount = Column(Float, nullable=False)

    # Many-to-one relationship with scenario
    scenario = relationship("Scenario", back_populates="lines")

    def __repr__(self):
        return f"<ScenarioLine(category={self.category}, final={self.final_amount})>"


class ScenarioDrivers(Base):
    """Financial drivers saved with a scenario"""
    __tablename__ = 'scenario_drivers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(Integer, ForeignKey('scenarios.id'), nullable=False)

    # Working Capital
    dso_days = Column(Float, nullable=False)
    dpo_days = Column(Float, nullable=False)
    dio_days = Column(Float, nullable=False)
    ccc_days = Column(Float, nullable=False)

    # Revenue
    revenue_growth_pct = Column(Float, nullable=False)
    gross_margin_pct = Column(Float, nullable=False)

    # Optional
    capex_pct = Column(Float, nullable=True)
    interest_rate_pct = Column(Float, nullable=True)
    industry = Column(String, nullable=True)

    scenario = relationship("Scenario", back_populates="drivers")

    def __repr__(self):
        return f"<ScenarioDrivers(scenario_id={self.scenario_id}, ccc={self.ccc_days})>"
