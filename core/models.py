"""
SQLAlchemy модели для базы данных
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Scenario(Base):
    """Сценарий прогноза cash flow"""
    __tablename__ = 'scenarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String, nullable=False, default="user")
    forecast_period = Column(String, nullable=False)  # например, "2025-12"
    description = Column(String, nullable=True)

    # Связь один-ко-многим со строками сценария
    lines = relationship("ScenarioLine", back_populates="scenario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scenario(id={self.id}, period={self.forecast_period}, created_at={self.created_at})>"


class ScenarioLine(Base):
    """Строка сценария (прогноз по одной категории)"""
    __tablename__ = 'scenario_lines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(Integer, ForeignKey('scenarios.id'), nullable=False)
    category = Column(String, nullable=False)
    period_date = Column(String, nullable=False)  # может быть month или конкретная дата
    forecast_amount = Column(Float, nullable=False)
    adjustment_amount = Column(Float, nullable=False, default=0.0)
    final_amount = Column(Float, nullable=False)

    # Связь многие-к-одному со сценарием
    scenario = relationship("Scenario", back_populates="lines")

    def __repr__(self):
        return f"<ScenarioLine(category={self.category}, final={self.final_amount})>"
