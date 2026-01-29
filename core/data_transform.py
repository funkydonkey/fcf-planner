"""
Модуль для трансформации данных между длинным и широким форматами
"""
import pandas as pd
from typing import Optional


def pivot_to_wide_format(df: pd.DataFrame) -> pd.DataFrame:
    """.
    Преобразование данных из длинного формата (date, category, amount)
    в широкий формат (строки=категории, столбцы=месяцы)

    Args:
        df: DataFrame с колонками date, category, amount

    Returns:
        DataFrame в широком формате (категории × месяцы)
    """
    # Создаем колонку с названиями месяцев (формат "Янв 2025")
    df_copy = df.copy()
    df_copy['month_name'] = df_copy['date'].dt.strftime('%b %Y')

    # Словарь для перевода английских месяцев на русские (опционально)
    month_translation = {
        'Jan': 'Янв', 'Feb': 'Фев', 'Mar': 'Мар', 'Apr': 'Апр',
        'May': 'Май', 'Jun': 'Июн', 'Jul': 'Июл', 'Aug': 'Авг',
        'Sep': 'Сен', 'Oct': 'Окт', 'Nov': 'Ноя', 'Dec': 'Дек'
    }

    # for eng, rus in month_translation.items():
    #     df_copy['month_name'] = df_copy['month_name'].str.replace(eng, rus)

    # Pivot: категории в строки, месяцы в столбцы
    df_wide = df_copy.pivot_table(
        index='category',
        columns='month_name',
        values='amount',
        aggfunc='sum'
    )

    # Сортируем столбцы по дате
    # Преобразуем обратно в даты для сортировки
    month_dates = df_copy[['month_name', 'date']].drop_duplicates()
    month_dates = month_dates.sort_values('date')
    sorted_months = month_dates['month_name'].tolist()

    # Переупорядочиваем столбцы
    df_wide = df_wide[sorted_months]

    # Сбрасываем индекс, чтобы category стала обычной колонкой
    df_wide = df_wide.reset_index()

    return df_wide


def add_forecast_columns(
    df_wide: pd.DataFrame,
    next_month_name: str,
    forecast_values: Optional[pd.Series] = None
) -> pd.DataFrame:
    """
    Добавляет три колонки для следующего месяца: Прогноз, Корректировки, Итого

    Args:
        df_wide: DataFrame в широком формате (результат pivot_to_wide_format)
        next_month_name: Название следующего месяца (например, "Ноя 2025")
        forecast_values: Опциональный Series с прогнозными значениями для каждой категории

    Returns:
        DataFrame с добавленными колонками для прогноза
    """
    df_result = df_wide.copy()

    # Создаем составные названия колонок
    forecast_col = f"{next_month_name}_Прогноз"
    comment_col = f"{next_month_name}_Комментарии"
    adjustment_col = f"{next_month_name}_Корректировки"
    total_col = f"{next_month_name}_Итого"

    # Добавляем колонки
    if forecast_values is not None:
        df_result[forecast_col] = forecast_values
    else:
        df_result[forecast_col] = 0.0

    df_result[comment_col] = ""

    df_result[adjustment_col] = 0.0
    df_result[total_col] = df_result[forecast_col] + df_result[adjustment_col]

    return df_result


def get_next_month_name(df: pd.DataFrame, result="string") -> str:
    """
    Определяет название следующего месяца после последней даты в данных

    Args:
        df: DataFrame с колонкой date
        result: Тип результата ('string' или 'date')

    Returns:
        Строка с названием месяца в формате "Янв 2025"
    """
    max_date = df['date'].max()
    next_month_date = max_date + pd.DateOffset(months=1)

    month_name = next_month_date.strftime('%b %Y')

    # Перевод на русский
    month_translation = {
        'Jan': 'Янв', 'Feb': 'Фев', 'Mar': 'Мар', 'Apr': 'Апр',
        'May': 'Май', 'Jun': 'Июн', 'Jul': 'Июл', 'Aug': 'Авг',
        'Sep': 'Сен', 'Oct': 'Окт', 'Nov': 'Ноя', 'Dec': 'Дек'
    }

    for eng, rus in month_translation.items():
        month_name = month_name.replace(eng, rus)

    if result == 'string':
        return month_name
    elif result == 'date':
        return max_date
    else:
        return "Specify result type: 'string' or 'date'"
