"""
Модуль работы с базой данных
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Optional
from datetime import datetime

from core.models import Base, Scenario, ScenarioLine
import config


# Создаем engine и session factory
engine = create_engine(config.DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Инициализация базы данных (создание таблиц)"""
    Base.metadata.create_all(bind=engine)
    print(f"✅ База данных инициализирована: {config.DB_URL}")


def get_db() -> Session:
    """Получить сессию БД (для использования в контексте)"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Закрытие будет вручную


def save_scenario(
    forecast_period: str,
    rows: List[Dict],
    description: Optional[str] = None,
    created_by: str = "user"
) -> int:
    """
    Сохранить сценарий в БД (атомарно)

    Args:
        forecast_period: Период прогноза (например, "2025-12")
        rows: Список словарей с полями:
            - category
            - period_date
            - forecast_amount
            - adjustment_amount
            - final_amount
        description: Описание сценария
        created_by: Кто создал сценарий

    Returns:
        ID созданного сценария
    """
    db = get_db()
    try:
        # Создаем сценарий
        scenario = Scenario(
            created_at=datetime.utcnow(),
            created_by=created_by,
            forecast_period=forecast_period,
            description=description
        )
        db.add(scenario)
        db.flush()  # Получаем ID сценария

        # Добавляем строки
        for row in rows:
            line = ScenarioLine(
                scenario_id=scenario.id,
                category=row['category'],
                period_date=row['period_date'],
                forecast_amount=row['forecast_amount'],
                adjustment_amount=row['adjustment_amount'],
                final_amount=row['final_amount']
            )
            db.add(line)

        db.commit()
        scenario_id = scenario.id
        return scenario_id

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_scenarios_list() -> List[Dict]:
    """
    Получить список всех сценариев

    Returns:
        Список словарей с информацией о сценариях
    """
    db = get_db()
    try:
        scenarios = db.query(Scenario).order_by(Scenario.created_at.desc()).all()

        result = []
        for s in scenarios:
            # Считаем сумму final_amount
            total_final = sum(line.final_amount for line in s.lines)

            result.append({
                'id': s.id,
                'created_at': s.created_at,
                'forecast_period': s.forecast_period,
                'description': s.description or "",
                'created_by': s.created_by,
                'total_final_amount': total_final
            })

        return result

    finally:
        db.close()


def get_scenario_lines(scenario_id: int) -> List[Dict]:
    """
    Получить строки конкретного сценария

    Args:
        scenario_id: ID сценария

    Returns:
        Список словарей с данными строк
    """
    db = get_db()
    try:
        lines = db.query(ScenarioLine).filter(
            ScenarioLine.scenario_id == scenario_id
        ).all()

        result = []
        for line in lines:
            result.append({
                'category': line.category,
                'period_date': line.period_date,
                'forecast_amount': line.forecast_amount,
                'adjustment_amount': line.adjustment_amount,
                'final_amount': line.final_amount
            })

        return result

    finally:
        db.close()
