"""
Database operations module
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Optional
from datetime import datetime

from core.models import Base, Scenario, ScenarioLine, ScenarioDrivers
import config


# Create engine and session factory
engine = create_engine(config.DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database (create tables)"""
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {config.DB_URL}")


def get_db() -> Session:
    """Get DB session (for context use)"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Closing will be manual


def save_scenario(
    forecast_period: str,
    rows: List[Dict],
    description: Optional[str] = None,
    created_by: str = "user",
    drivers_data: Optional[Dict] = None
) -> int:
    """
    Save scenario to DB (atomically)

    Args:
        forecast_period: Forecast period (e.g., "2025-12")
        rows: List of dictionaries with fields:
            - category
            - period_date
            - forecast_amount
            - adjustment_amount
            - final_amount
        description: Scenario description
        created_by: Who created the scenario
        drivers_data: Optional dict with driver values:
            - dso_days, dpo_days, dio_days, ccc_days
            - revenue_growth_pct, gross_margin_pct
            - capex_pct (optional), interest_rate_pct (optional)
            - industry (optional)

    Returns:
        ID of created scenario
    """
    db = get_db()
    try:
        # Create scenario
        scenario = Scenario(
            created_at=datetime.utcnow(),
            created_by=created_by,
            forecast_period=forecast_period,
            description=description
        )
        db.add(scenario)
        db.flush()  # Get scenario ID

        # Add lines
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

        # Add drivers if provided
        if drivers_data:
            drivers = ScenarioDrivers(
                scenario_id=scenario.id,
                dso_days=drivers_data['dso_days'],
                dpo_days=drivers_data['dpo_days'],
                dio_days=drivers_data['dio_days'],
                ccc_days=drivers_data['ccc_days'],
                revenue_growth_pct=drivers_data['revenue_growth_pct'],
                gross_margin_pct=drivers_data['gross_margin_pct'],
                capex_pct=drivers_data.get('capex_pct'),
                interest_rate_pct=drivers_data.get('interest_rate_pct'),
                industry=drivers_data.get('industry')
            )
            db.add(drivers)

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
    Get list of all scenarios

    Returns:
        List of dictionaries with scenario information
    """
    db = get_db()
    try:
        scenarios = db.query(Scenario).order_by(Scenario.created_at.desc()).all()

        result = []
        for s in scenarios:
            # Calculate sum of final_amount
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
    Get lines of specific scenario

    Args:
        scenario_id: Scenario ID

    Returns:
        List of dictionaries with line data
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


def get_scenario_drivers(scenario_id: int) -> Optional[Dict]:
    """
    Get drivers for a specific scenario

    Args:
        scenario_id: Scenario ID

    Returns:
        Dictionary with driver data or None if no drivers saved
    """
    db = get_db()
    try:
        drivers = db.query(ScenarioDrivers).filter(
            ScenarioDrivers.scenario_id == scenario_id
        ).first()

        if drivers is None:
            return None

        return {
            'dso_days': drivers.dso_days,
            'dpo_days': drivers.dpo_days,
            'dio_days': drivers.dio_days,
            'ccc_days': drivers.ccc_days,
            'revenue_growth_pct': drivers.revenue_growth_pct,
            'gross_margin_pct': drivers.gross_margin_pct,
            'capex_pct': drivers.capex_pct,
            'interest_rate_pct': drivers.interest_rate_pct,
            'industry': drivers.industry
        }

    finally:
        db.close()
