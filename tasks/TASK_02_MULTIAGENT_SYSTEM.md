# 📚 ЗАДАНИЕ 2: Multi-Agent система оптимизации прогноза (AutoGen)

## 🎯 Цель задания

Вы создадите систему из **трех AI-агентов**, которые будут работать вместе для улучшения прогноза cash flow:
1. **Analyst Agent** — анализирует данные и делает первичный прогноз
2. **Critic Agent** — проверяет прогноз и указывает на проблемы
3. **Optimizer Agent** — улучшает прогноз на основе критики

Это классический пример **multi-agent collaboration** с использованием **AutoGen**.

---

## 📖 Теоретическая часть

### Что такое AutoGen?

**AutoGen** — это фреймворк от Microsoft для создания multi-agent систем. Основные концепции:

1. **ConversableAgent** — базовый агент, который может общаться
2. **AssistantAgent** — агент, использующий LLM для задач
3. **UserProxyAgent** — агент, представляющий пользователя
4. **GroupChat** — группа агентов, общающихся между собой
5. **GroupChatManager** — управляет порядком общения агентов

### Пример простой multi-agent системы:

```python
from autogen import AssistantAgent, UserProxyAgent

# Настройка LLM
config = {
    "model": "gpt-4o-mini",
    "api_key": "your-key"
}

# Создаем агента-аналитика
analyst = AssistantAgent(
    name="Analyst",
    system_message="Ты финансовый аналитик. Анализируй данные.",
    llm_config=config
)

# Создаем агента-критика
critic = AssistantAgent(
    name="Critic",
    system_message="Ты критик. Проверяй анализ на ошибки.",
    llm_config=config
)

# Запускаем диалог
user_proxy = UserProxyAgent(name="User", human_input_mode="NEVER")
user_proxy.initiate_chat(analyst, message="Проанализируй эти данные...")
```

---

## 🛠 Ваше задание

Создайте файл `agents/optimization_agent.py` с multi-agent системой.

### Архитектура системы

```
User Input (данные)
    ↓
Analyst Agent (первичный прогноз)
    ↓
Critic Agent (проверка и критика)
    ↓
Optimizer Agent (улучшенный прогноз)
    ↓
Final Result
```

---

## 📝 Пошаговая инструкция

### Шаг 1: Изучите AutoGen v0.6

AutoGen версии 0.6+ использует новый API. Основные отличия:

```python
# Старый способ (v0.4)
analyst.initiate_chat(...)

# Новый способ (v0.6)
from autogen.agentchat import on_messages

@on_messages(...)
async def handle_message(messages):
    # обработка
```

Для нашего проекта используем **упрощенный подход** — последовательные вызовы агентов.

### Шаг 2: Создайте конфигурацию LLM

В файле `agents/optimization_agent.py`:

```python
import config
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

def get_llm_config():
    """Конфигурация LLM для агентов"""
    return {
        "config_list": [{
            "model": config.FORECAST_MODEL,  # gpt-4o-mini
            "api_key": config.OPENAI_API_KEY,
            "temperature": 0.3
        }]
    }
```

### Шаг 3: Создайте трех агентов

```python
def create_agents():
    """Создает трех агентов для multi-agent системы"""

    llm_config = get_llm_config()

    # Агент 1: Аналитик
    analyst = AssistantAgent(
        name="Financial_Analyst",
        system_message="""
        Ты — финансовый аналитик. Твоя задача:
        1. Проанализировать исторические данные cash flow
        2. Выявить тренды (рост, падение, стабильность)
        3. Сделать прогноз на следующий месяц
        4. Обосновать свой прогноз

        Формат ответа:
        - Анализ: [краткое описание трендов]
        - Прогноз: [число]
        - Обоснование: [почему такой прогноз]
        """,
        llm_config=llm_config
    )

    # TODO: Создайте агента "Критик"
    # Подсказка: его задача — проверить прогноз аналитика
    # Он должен:
    # 1. Проверить обоснованность прогноза
    # 2. Найти возможные ошибки
    # 3. Предложить корректировки

    critic = AssistantAgent(
        name="Critic",
        system_message="""
        # TODO: Напишите system_message для критика
        # Он должен критически оценить прогноз
        """,
        llm_config=llm_config
    )

    # TODO: Создайте агента "Оптимизатор"
    # Подсказка: его задача — учесть критику и дать финальный прогноз
    # Он должен:
    # 1. Учесть замечания критика
    # 2. Скорректировать прогноз
    # 3. Дать ФИНАЛЬНОЕ число

    optimizer = AssistantAgent(
        name="Optimizer",
        system_message="""
        # TODO: Напишите system_message для оптимизатора
        """,
        llm_config=llm_config
    )

    return analyst, critic, optimizer
```

### Шаг 4: Создайте GroupChat

```python
def optimize_forecast_with_multiagent(historical_data: str, category: str) -> float:
    """
    Использует multi-agent систему для оптимизации прогноза

    Args:
        historical_data: Текстовое представление данных (таблица)
        category: Категория cash flow

    Returns:
        Оптимизированный прогноз (число)
    """

    # Создаем агентов
    analyst, critic, optimizer = create_agents()

    # Создаем user proxy (не будет запрашивать ввод от пользователя)
    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",  # Не запрашивать ввод
        max_consecutive_auto_reply=0,  # Не отвечать автоматически
        code_execution_config=False  # Не выполнять код
    )

    # TODO: Создайте GroupChat с агентами
    # Подсказка: порядок агентов важен
    groupchat = GroupChat(
        agents=[user_proxy, analyst, critic, optimizer],
        messages=[],
        max_round=6  # Максимум 6 раундов диалога
    )

    # Создаем менеджера группового чата
    manager = GroupChatManager(groupchat=groupchat, llm_config=get_llm_config())

    # TODO: Запустите диалог
    # Подсказка: используйте user_proxy.initiate_chat()

    prompt = f"""
    Категория: {category}

    Исторические данные (последние месяцы):
    {historical_data}

    Задача:
    1. Analyst: проанализируй данные и сделай прогноз
    2. Critic: проверь прогноз и укажи на проблемы
    3. Optimizer: учти критику и дай ФИНАЛЬНЫЙ прогноз (только число!)

    Optimizer должен в конце написать: FINAL_FORECAST: [число]
    """

    # Запуск диалога
    user_proxy.initiate_chat(
        manager,
        message=prompt
    )

    # TODO: Извлеките финальный прогноз из истории сообщений
    # Подсказка: последнее сообщение от Optimizer содержит число

    # Получаем все сообщения
    messages = groupchat.messages

    # Ищем финальный прогноз
    final_forecast = None
    for msg in reversed(messages):
        content = msg.get("content", "")
        if "FINAL_FORECAST:" in content:
            # Извлекаем число после "FINAL_FORECAST:"
            import re
            numbers = re.findall(r'FINAL_FORECAST:\s*(-?\d+\.?\d*)', content)
            if numbers:
                final_forecast = float(numbers[0])
                break

    # Если не нашли, берем последнее число в последнем сообщении
    if final_forecast is None:
        import re
        last_content = messages[-1].get("content", "")
        numbers = re.findall(r'-?\d+\.?\d+', last_content)
        if numbers:
            final_forecast = float(numbers[-1])

    return final_forecast if final_forecast else 0.0
```

### Шаг 5: Интегрируйте с основным прогнозом

```python
import pandas as pd

def build_optimized_forecast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Главная функция: строит оптимизированный прогноз с multi-agent системой

    Args:
        df: Исторические данные (date, category, amount)

    Returns:
        DataFrame с прогнозом
    """

    # Подготовка данных (используем код из Задания 1)
    from agents.forecast_agent import prepare_monthly_data

    monthly = prepare_monthly_data(df)

    # Определяем период прогноза
    last_month = monthly['month'].max()
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    last_date = datetime.strptime(last_month, '%Y-%m')
    next_date = last_date + relativedelta(months=1)
    forecast_period = next_date.strftime('%Y-%m')

    # Для каждой категории запускаем multi-agent систему
    categories = monthly['category'].unique()
    results = []

    for cat in categories:
        print(f"\n🤖 Multi-agent оптимизация для: {cat}")

        # Фильтруем данные
        cat_data = monthly[monthly['category'] == cat].copy()
        cat_data = cat_data.tail(config.FORECAST_LOOKBACK_MONTHS)

        # Преобразуем в текст для промпта
        historical_text = cat_data.to_string(index=False)

        # Запускаем multi-agent систему
        try:
            forecast_value = optimize_forecast_with_multiagent(historical_text, cat)
        except Exception as e:
            print(f"❌ Ошибка multi-agent системы: {e}")
            # Fallback на простое среднее
            forecast_value = cat_data['amount'].mean()

        results.append({
            'period': forecast_period,
            'category': cat,
            'forecast_amount': forecast_value,
            'adjustment': 0.0,
            'final_amount': forecast_value
        })

    return pd.DataFrame(results)
```

---

## ✅ Критерии выполнения

Ваш код должен:

1. ✅ Создавать трех агентов с разными ролями
2. ✅ Организовывать GroupChat между агентами
3. ✅ Запускать последовательный диалог (Analyst → Critic → Optimizer)
4. ✅ Извлекать финальный прогноз из диалога
5. ✅ Обрабатывать ошибки (fallback на простое среднее)

---

## 🧪 Тестирование

Создайте файл `test_multiagent.py`:

```python
from core.io_historical import load_history_from_file
from agents.optimization_agent import build_optimized_forecast

# Загружаем данные
df = load_history_from_file('data/sample_cashflow.csv')

# Строим оптимизированный прогноз
forecast = build_optimized_forecast(df)

print("=" * 50)
print("MULTI-AGENT ОПТИМИЗИРОВАННЫЙ ПРОГНОЗ")
print("=" * 50)
print(forecast)
print("=" * 50)
print(f"Итоговый прогноз: {forecast['final_amount'].sum():,.2f}")
```

Запустите:
```bash
python test_multiagent.py
```

---

## 💡 Подсказки

### Как работает GroupChat:

```python
# Агенты общаются по очереди
groupchat = GroupChat(
    agents=[user, agent1, agent2, agent3],
    messages=[],
    max_round=6  # максимум 6 сообщений
)

# Менеджер управляет очередью
manager = GroupChatManager(groupchat=groupchat, llm_config=config)

# Запускаем от имени user
user.initiate_chat(manager, message="...")
```

### Как извлечь результат:

```python
# Все сообщения доступны в groupchat.messages
for msg in groupchat.messages:
    print(f"{msg['role']}: {msg['content']}")

# Последнее сообщение:
last_message = groupchat.messages[-1]['content']
```

### System messages для агентов:

**Critic:**
```
Ты — критик финансовых прогнозов. Твоя задача:
1. Проверить прогноз аналитика
2. Найти слабые места в обосновании
3. Указать на риски (сезонность, выбросы, малый sample size)
4. Предложить корректировки

Будь конструктивным, но критичным.
```

**Optimizer:**
```
Ты — оптимизатор. Твоя задача:
1. Изучить прогноз аналитика
2. Учесть критику от критика
3. Скорректировать прогноз
4. Дать ФИНАЛЬНОЕ число

В конце обязательно напиши: FINAL_FORECAST: [число]
```

---

## 🎓 Что вы изучите

1. ✅ Создание multi-agent систем с AutoGen
2. ✅ Организация группового чата между агентами
3. ✅ Извлечение структурированных данных из диалога
4. ✅ Обработка ошибок в multi-agent системах
5. ✅ Комбинирование разных подходов к AI

---

## 🔥 Дополнительные улучшения (опционально)

Если хотите усложнить:

### 1. Добавьте Data Validator Agent

```python
validator = AssistantAgent(
    name="Validator",
    system_message="Проверяй качество исторических данных (выбросы, пропуски)"
)
```

### 2. Сохраните диалог агентов

```python
# Сохраните всю историю диалога
conversation_log = "\n\n".join([
    f"{msg['name']}: {msg['content']}"
    for msg in groupchat.messages
])

with open(f"logs/conversation_{category}.txt", "w") as f:
    f.write(conversation_log)
```

### 3. Визуализируйте процесс

```python
import streamlit as st

# В Streamlit показывайте диалог в реальном времени
with st.expander("💬 Диалог агентов"):
    for msg in groupchat.messages:
        st.markdown(f"**{msg['name']}:** {msg['content']}")
```

---

## 📚 Дополнительные материалы

- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [AutoGen GroupChat Example](https://github.com/microsoft/autogen/blob/main/notebook/agentchat_groupchat.ipynb)
- [Multi-Agent Patterns](https://www.microsoft.com/en-us/research/publication/autogen-enabling-next-gen-llm-applications-via-multi-agent-conversation/)

---

## 🚀 Что дальше?

После выполнения Задания 2:
- У вас будет полноценная multi-agent система
- Вы сможете сравнить результаты простого агента (Задание 1) vs multi-agent (Задание 2)
- Можно добавить переключатель в UI: "Простой прогноз" vs "Multi-agent оптимизация"

---

**Удачи с multi-agent системой!** 🤖🤖🤖
