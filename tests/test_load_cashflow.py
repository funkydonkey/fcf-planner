"""
Тестирование загрузки нового формата cashflow файла
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.io_historical import load_history_from_file

# Загружаем файл с новым форматом (используем относительный путь)
project_root = Path(__file__).parent.parent
df = load_history_from_file(str(project_root / 'data' / 'sample_cashflow.csv'))

print("\n📊 Первые 10 записей:")
print(df.head(10))

print("\n📊 Последние 10 записей:")
print(df.tail(10))

print("\n📈 Статистика по категориям:")
print(df.groupby('category')['amount'].agg(['count', 'sum', 'mean']))

print("\n📅 Статистика по месяцам:")
print(df.groupby(df['date'].dt.to_period('M'))['amount'].sum())

print("\n✅ Общий cashflow:")
print(f"Total: {df['amount'].sum():,.0f}")
