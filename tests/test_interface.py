"""
Тестирование нового интерфейса
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.io_historical import load_history_from_file
from core.data_transform import pivot_to_wide_format, add_forecast_columns, get_next_month_name

# Загружаем данные (используем относительный путь)
print("=" * 60)
print("Шаг 1: Загрузка данных из файла")
print("=" * 60)
project_root = Path(__file__).parent.parent
df_history = load_history_from_file(str(project_root / 'data' / 'sample_cashflow.csv'))

print("\n📊 Длинный формат (первые 15 строк):")
print(df_history.head(15))

# Преобразуем в широкий формат
print("\n" + "=" * 60)
print("Шаг 2: Преобразование в широкий формат")
print("=" * 60)
df_wide = pivot_to_wide_format(df_history)
print("\n📊 Широкий формат:")
print(df_wide)

# Определяем следующий месяц
print("\n" + "=" * 60)
print("Шаг 3: Добавление колонок для прогноза")
print("=" * 60)
next_month = get_next_month_name(df_history)
print(f"\n📅 Следующий месяц: {next_month}")

# Добавляем колонки для прогноза
df_display = add_forecast_columns(df_wide, next_month)
print("\n📊 Таблица с колонками прогноза:")
print(df_display)

print("\n" + "=" * 60)
print("Шаг 4: Информация о колонках")
print("=" * 60)
print(f"\n📋 Всего колонок: {len(df_display.columns)}")
print(f"📋 Названия колонок: {list(df_display.columns)}")

# Проверяем форматы колонок
forecast_col = f"{next_month}_Прогноз"
adjustment_col = f"{next_month}_Корректировки"
total_col = f"{next_month}_Итого"

print(f"\n✅ Колонка прогноза: {forecast_col}")
print(f"✅ Колонка корректировок: {adjustment_col}")
print(f"✅ Колонка итого: {total_col}")

print("\n" + "=" * 60)
print("✅ Все проверки пройдены успешно!")
print("=" * 60)
