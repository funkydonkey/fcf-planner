"""
Module for reading and normalizing historical cash flow data
"""
import pandas as pd
from typing import Union
import config


def load_history_from_file(file_path_or_buffer: Union[str, bytes]) -> pd.DataFrame:
    """
    Load historical data from Excel or CSV file

    Supports two formats:
    1. Old format (date, category, amount) - long format
    2. New format (rows=items, columns=months) - wide format

    Args:
        file_path_or_buffer: File path or buffer (for Streamlit uploaded file)

    Returns:
        DataFrame with normalized columns: date, category, amount

    Raises:
        ValueError: If file format is not supported or data is invalid
    """

    # Determine file type and read
    try:
        # If it's a file path
        if isinstance(file_path_or_buffer, str):
            if file_path_or_buffer.endswith('.csv'):
                df = pd.read_csv(file_path_or_buffer)
            elif file_path_or_buffer.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path_or_buffer)
            else:
                raise ValueError(f"Unsupported file format: {file_path_or_buffer}")

        # If it's a buffer (uploaded file from Streamlit)
        else:
            # Try as Excel first
            try:
                df = pd.read_excel(file_path_or_buffer)
            except:
                # If that fails, try as CSV
                file_path_or_buffer.seek(0)  # Return pointer to beginning
                df = pd.read_csv(file_path_or_buffer)

    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")

    # Determine file format
    required_cols_old = {
        config.HIST_COL_DATE,
        config.HIST_COL_CATEGORY,
        config.HIST_COL_AMOUNT
    }

    # Check if this is old format (long)
    if required_cols_old.issubset(df.columns):
        # Old format: date, category, amount
        df = df.rename(columns={
            config.HIST_COL_DATE: 'date',
            config.HIST_COL_CATEGORY: 'category',
            config.HIST_COL_AMOUNT: 'amount'
        })
        df = df[['date', 'category', 'amount']]

        # Convert data types
        try:
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = df['amount'].astype(float)
            df['category'] = df['category'].astype(str)
        except Exception as e:
            raise ValueError(f"Error converting data types: {str(e)}")

    else:
        # New format: first column = items, rest = months
        # Check that there are at least 2 columns
        if len(df.columns) < 2:
            raise ValueError("File must contain at least 2 columns (item + months)")

        # First column is categories
        category_col = df.columns[0]
        month_cols = df.columns[1:]

        # Convert from wide format to long
        df_long = df.melt(
            id_vars=[category_col],
            value_vars=month_cols,
            var_name='month',
            value_name='amount'
        )

        # Rename columns
        df_long = df_long.rename(columns={category_col: 'category'})

        # Convert months to dates
        try:
            # Dictionary for translating Russian and English months
            month_map = {
                'Янв': 1, 'Фев': 2, 'Мар': 3, 'Апр': 4, 'Май': 5, 'Июн': 6,
                'Июл': 7, 'Авг': 8, 'Сен': 9, 'Окт': 10, 'Ноя': 11, 'Дек': 12,
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
            }

            # Try to convert directly
            try:
                df_long['date'] = pd.to_datetime(df_long['month'], format='%Y-%m')
            except:
                # If that fails, use dictionary (for short month names)
                # Assume current year
                current_year = pd.Timestamp.now().year
                df_long['date'] = df_long['month'].apply(
                    lambda x: pd.Timestamp(year=current_year, month=month_map.get(x, 1), day=1)
                    if x in month_map else pd.to_datetime(x)
                )

            df_long['amount'] = df_long['amount'].astype(float)
            df_long['category'] = df_long['category'].astype(str)
        except Exception as e:
            raise ValueError(f"Error converting months to dates: {str(e)}")

        df = df_long[['date', 'category', 'amount']]

    # Remove rows with empty values
    df = df.dropna()

    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)

    print(f"✅ Loaded {len(df)} records from period {df['date'].min()} - {df['date'].max()}")
    print(f"   Categories: {df['category'].nunique()}")

    return df


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Get brief statistics on loaded data

    Args:
        df: DataFrame with data (date, category, amount)

    Returns:
        Dictionary with statistics
    """
    return {
        'total_records': len(df),
        'date_range': {
            'min': df['date'].min(),
            'max': df['date'].max()
        },
        'categories': df['category'].unique().tolist(),
        'total_amount': df['amount'].sum(),
        'months_count': df['date'].dt.to_period('M').nunique()
    }
