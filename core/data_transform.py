"""
Module for data transformation between long and wide formats
"""
import pandas as pd
from typing import Optional


def pivot_to_wide_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform data from long format (date, category, amount)
    to wide format (rows=categories, columns=months)

    Args:
        df: DataFrame with columns date, category, amount

    Returns:
        DataFrame in wide format (categories × months)
    """
    # Create column with month names (format "Jan 2025")
    df_copy = df.copy()
    df_copy['month_name'] = df_copy['date'].dt.strftime('%b %Y')

    # Month translation dictionary (commented out - keeping English)
    # month_translation = {
    #     'Jan': 'Янв', 'Feb': 'Фев', 'Mar': 'Мар', 'Apr': 'Апр',
    #     'May': 'Май', 'Jun': 'Июн', 'Jul': 'Июл', 'Aug': 'Авг',
    #     'Sep': 'Сен', 'Oct': 'Окт', 'Nov': 'Ноя', 'Dec': 'Дек'
    # }

    # for eng, rus in month_translation.items():
    #     df_copy['month_name'] = df_copy['month_name'].str.replace(eng, rus)

    # Pivot: categories to rows, months to columns
    df_wide = df_copy.pivot_table(
        index='category',
        columns='month_name',
        values='amount',
        aggfunc='sum'
    )

    # Sort columns by date
    # Convert back to dates for sorting
    month_dates = df_copy[['month_name', 'date']].drop_duplicates()
    month_dates = month_dates.sort_values('date')
    sorted_months = month_dates['month_name'].tolist()

    # Reorder columns
    df_wide = df_wide[sorted_months]

    # Reset index to make category a regular column
    df_wide = df_wide.reset_index()

    return df_wide


def add_forecast_columns(
    df_wide: pd.DataFrame,
    next_month_name: str,
    forecast_values: Optional[pd.Series] = None
) -> pd.DataFrame:
    """
    Adds three columns for next month: Forecast, Adjustments, Total

    Args:
        df_wide: DataFrame in wide format (result of pivot_to_wide_format)
        next_month_name: Next month name (e.g., "Nov 2025")
        forecast_values: Optional Series with forecast values for each category

    Returns:
        DataFrame with added forecast columns
    """
    df_result = df_wide.copy()

    # Create composite column names
    forecast_col = f"{next_month_name}_Forecast"
    comment_col = f"{next_month_name}_Comments"
    adjustment_col = f"{next_month_name}_Adjustments"
    total_col = f"{next_month_name}_Total"

    # Add columns
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
    Determines the name of next month after the latest date in data

    Args:
        df: DataFrame with date column
        result: Result type ('string' or 'date')

    Returns:
        String with month name in format "Jan 2025"
    """
    max_date = df['date'].max()
    next_month_date = max_date + pd.DateOffset(months=1)

    month_name = next_month_date.strftime('%b %Y')

    # Translation to Russian (commented out - keeping English)
    # month_translation = {
    #     'Jan': 'Янв', 'Feb': 'Фев', 'Mar': 'Мар', 'Apr': 'Апр',
    #     'May': 'Май', 'Jun': 'Июн', 'Jul': 'Июл', 'Aug': 'Авг',
    #     'Sep': 'Сен', 'Oct': 'Окт', 'Nov': 'Ноя', 'Dec': 'Дек'
    # }

    # for eng, rus in month_translation.items():
    #     month_name = month_name.replace(eng, rus)

    if result == 'string':
        return month_name
    elif result == 'date':
        return max_date
    else:
        return "Specify result type: 'string' or 'date'"
