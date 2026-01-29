"""
Модуль для чтения и нормализации исторических данных cash flow
"""
import pandas as pd
from typing import Union
import config


def load_history_from_file(file_path_or_buffer: Union[str, bytes]) -> pd.DataFrame:
    """
    Загрузка исторических данных из Excel или CSV файла

    Поддерживает два формата:
    1. Старый формат (date, category, amount) - длинный формат
    2. Новый формат (строки=статьи, столбцы=месяцы) - широкий формат

    Args:
        file_path_or_buffer: Путь к файлу или buffer (для Streamlit uploaded file)

    Returns:
        DataFrame с нормализованными колонками: date, category, amount

    Raises:
        ValueError: Если формат файла не поддерживается или данные некорректны
    """

    # Определяем тип файла и читаем
    try:
        # Если это путь к файлу
        if isinstance(file_path_or_buffer, str):
            if file_path_or_buffer.endswith('.csv'):
                df = pd.read_csv(file_path_or_buffer)
            elif file_path_or_buffer.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path_or_buffer)
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {file_path_or_buffer}")

        # Если это buffer (uploaded file из Streamlit)
        else:
            # Попробуем сначала как Excel
            try:
                df = pd.read_excel(file_path_or_buffer)
            except:
                # Если не получилось, пробуем как CSV
                file_path_or_buffer.seek(0)  # Возвращаем указатель в начало
                df = pd.read_csv(file_path_or_buffer)

    except Exception as e:
        raise ValueError(f"Ошибка чтения файла: {str(e)}")

    # Определяем формат файла
    required_cols_old = {
        config.HIST_COL_DATE,
        config.HIST_COL_CATEGORY,
        config.HIST_COL_AMOUNT
    }

    # Проверяем, старый ли это формат (длинный)
    if required_cols_old.issubset(df.columns):
        # Старый формат: date, category, amount
        df = df.rename(columns={
            config.HIST_COL_DATE: 'date',
            config.HIST_COL_CATEGORY: 'category',
            config.HIST_COL_AMOUNT: 'amount'
        })
        df = df[['date', 'category', 'amount']]

        # Приводим типы данных
        try:
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = df['amount'].astype(float)
            df['category'] = df['category'].astype(str)
        except Exception as e:
            raise ValueError(f"Ошибка преобразования типов данных: {str(e)}")

    else:
        # Новый формат: первая колонка = статьи, остальные = месяцы
        # Проверяем, что есть хотя бы 2 колонки
        if len(df.columns) < 2:
            raise ValueError("Файл должен содержать минимум 2 колонки (статья + месяцы)")

        # Первая колонка - это категории
        category_col = df.columns[0]
        month_cols = df.columns[1:]

        # Преобразуем из широкого формата в длинный
        df_long = df.melt(
            id_vars=[category_col],
            value_vars=month_cols,
            var_name='month',
            value_name='amount'
        )

        # Переименовываем колонки
        df_long = df_long.rename(columns={category_col: 'category'})

        # Преобразуем месяцы в даты
        try:
            # Словарь для перевода русских месяцев
            month_map = {
                'Янв': 1, 'Фев': 2, 'Мар': 3, 'Апр': 4, 'Май': 5, 'Июн': 6,
                'Июл': 7, 'Авг': 8, 'Сен': 9, 'Окт': 10, 'Ноя': 11, 'Дек': 12,
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
            }

            # Пытаемся преобразовать напрямую
            try:
                df_long['date'] = pd.to_datetime(df_long['month'], format='%Y-%m')
            except:
                # Если не получилось, используем словарь (для коротких названий месяцев)
                # Предполагаем текущий год
                current_year = pd.Timestamp.now().year
                df_long['date'] = df_long['month'].apply(
                    lambda x: pd.Timestamp(year=current_year, month=month_map.get(x, 1), day=1)
                    if x in month_map else pd.to_datetime(x)
                )

            df_long['amount'] = df_long['amount'].astype(float)
            df_long['category'] = df_long['category'].astype(str)
        except Exception as e:
            raise ValueError(f"Ошибка преобразования месяцев в даты: {str(e)}")

        df = df_long[['date', 'category', 'amount']]

    # Удаляем строки с пустыми значениями
    df = df.dropna()

    # Сортируем по дате
    df = df.sort_values('date').reset_index(drop=True)

    print(f"✅ Загружено {len(df)} записей из периода {df['date'].min()} - {df['date'].max()}")
    print(f"   Категорий: {df['category'].nunique()}")

    return df


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Получить краткую статистику по загруженным данным

    Args:
        df: DataFrame с данными (date, category, amount)

    Returns:
        Словарь со статистикой
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
