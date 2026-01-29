import pandas as pd 
import numpy as np
from typing import List, Dict

def calculate_trend(values: List[float]) -> str:
    """
    Определяет тренд в данных

    Args:
        values: Список исторических значений (от старых к новым)

    Returns:
        Одно из: "сильный рост", "умеренный рост", "стабильность",
                 "умеренное снижение", "сильное снижение"
    """
    if len(values) < 2:
        return "недостаточно данных"
    
    changes = [(values[i] - values[i-1]) / abs(values[i-1]) * 100
               for i in range(1, len(values)) if values[i-1] != 0]

    avg_change = np.mean(changes) if changes else 0

    if avg_change > 15:
        return "signuficant growth"
    elif avg_change > 0:
        return "moderate growth"
    elif avg_change < 0:
        return "moderate decrease"
    else:
        return "signuficant decrease"
    
def calculate_volatility(values: List[float]) -> str:
    """
    Определяет волатильность (стабильность) данных

    Args:
        values: Список исторических значений

    Returns:
        Одно из: "высокая", "средняя", "низкая"
    """

    if len(values) < 2:
        return "недостаточно данных"
    
    std_dev = np.std(values)

    mean_val = np.mean(values)

    cv = (std_dev / abs(mean_val) * 100) if mean_val != 0 else 0

    if cv > 20:
        return "high"
    elif cv > 10:
        return "medium"
    else:
        return "low"
    

def analyze_historical_data(values: List[float]) -> Dict:
    """
    Комплексный анализ исторических данных

    Args:
        values: Список исторических значений

    Returns:
        Словарь с аналитикой:
        {
            'trend': str,
            'volatility': str,
            'mean': float,
            'std_dev': float,
            'min': float,
            'max': float,
            'last_value': float
        }
    """
    analysis = {
        'trend': calculate_trend(values),
        'volatility': calculate_volatility(values),
        'mean': np.mean(values),
        'std_dev': np.std(values),
        'min': np.min(values),
        'max': np.max(values),
        # 'last_value': values[-1] if values else None,
        'values': values
    }

    return analysis