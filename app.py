"""
Cash Flow Planner - Streamlit Application
Главное приложение для прогнозирования cash flow
"""
import streamlit as st
import pandas as pd
from io import BytesIO

from core.io_historical import load_history_from_file, get_data_summary
from core.db import init_db, save_scenario, get_scenarios_list, get_scenario_lines
from core.data_transform import pivot_to_wide_format, add_forecast_columns, get_next_month_name

# Инициализация БД при старте
init_db()

# Настройка страницы
st.set_page_config(
    page_title="Cash Flow Planner",
    page_icon="💰",
    layout="wide"
)

# Заголовок
st.title("💰 Cash Flow Planner")
st.markdown("Прогнозирование денежных потоков с помощью AI")

# Создаем табы
tab1, tab2 = st.tabs(["📊 Прогноз", "📜 История"])

# === TAB 1: ПРОГНОЗ ===
with tab1:
    st.header("Загрузка и прогнозирование")

    # Загрузка файла
    uploaded_file = st.file_uploader(
        "Загрузите файл с историческими данными (Excel или CSV)",
        type=['xlsx', 'xls', 'csv']
    )

    if uploaded_file is not None:
        try:
            # Загружаем данные
            with st.spinner("Загрузка данных..."):
                df_history = load_history_from_file(uploaded_file)

            # Показываем статистику
            st.success(f"✅ Загружено {len(df_history)} записей")

            summary = get_data_summary(df_history)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Записей", summary['total_records'])
            with col2:
                st.metric("Категорий", len(summary['categories']))
            with col3:
                st.metric("Месяцев", summary['months_count'])
            with col4:
                st.metric("Сумма", f"{summary['total_amount']:,.0f}")

            # Преобразуем в широкий формат для отображения
            df_wide = pivot_to_wide_format(df_history)

            # Определяем следующий месяц
            next_month = get_next_month_name(df_history)

            # Проверяем, есть ли уже отредактированные данные в session_state
            # (например, после AI прогноза)
            if 'edited_df' in st.session_state and 'last_uploaded_file' in st.session_state:
                # Проверяем, что это тот же файл
                if st.session_state['last_uploaded_file'] == uploaded_file.name:
                    df_display = st.session_state['edited_df']
                else:
                    # Новый файл - создаем новые данные
                    df_display = add_forecast_columns(df_wide, next_month)
                    st.session_state['last_uploaded_file'] = uploaded_file.name
            else:
                # Первая загрузка - добавляем колонки для прогноза
                df_display = add_forecast_columns(df_wide, next_month)
                st.session_state['last_uploaded_file'] = uploaded_file.name

            # Сохраняем в session_state для дальнейшего использования
            st.session_state['df_history'] = df_history
            st.session_state['df_wide'] = df_display
            st.session_state['next_month'] = next_month

            # Показываем таблицу с данными
            st.subheader("📊 Исторические данные и прогноз")

            # Настройка форматирования колонок
            column_config = {
                "category": st.column_config.TextColumn("Статья", width="medium")
            }

            # Форматирование числовых колонок
            for col in df_display.columns:
                if col != 'category':
                    # Прогнозные колонки - редактируемые, остальные - только чтение
                    is_editable = any(x in col for x in ['Прогноз', 'Корректировки'])
                    column_config[col] = st.column_config.NumberColumn(
                        col,
                        format="%.0f",
                        disabled=(not is_editable)
                    )

            # Отображаем редактируемую таблицу
            edited_df = st.data_editor(
                df_display,
                column_config=column_config,
                hide_index=True,
                use_container_width=True,
                key="cashflow_table"
            )

            # Пересчитываем итоговые значения
            total_col = f"{next_month}_Итого"
            forecast_col = f"{next_month}_Прогноз"
            comment_col = f"{next_month}_Комментарии"
            adjustment_col = f"{next_month}_Корректировки"

            edited_df[total_col] = edited_df[forecast_col] + edited_df[adjustment_col]

            # Сохраняем отредактированные данные
            st.session_state['edited_df'] = edited_df

            # Показываем итоги по прогнозному месяцу
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"Σ {next_month} Прогноз", f"{edited_df[forecast_col].sum():,.0f}")
            with col2:
                st.metric(f"Σ {next_month} Корректировки", f"{edited_df[adjustment_col].sum():,.0f}")
            with col3:
                total_sum = edited_df[total_col].sum()
                st.metric(f"Σ {next_month} Итого", f"{total_sum:,.0f}")

            st.divider()

            # Кнопка "Рассчитать прогноз AI"
            if st.button("🔮 Рассчитать прогноз с AI", type="primary", use_container_width=True):
                try:
                    with st.spinner("AI-агент анализирует данные и строит прогноз..."):
                        # Импортируем функцию прогноза
                        from ai_agents.forecast_agent import build_cashflow_forecast

                        # Преобразуем данные в широкий формат для AI агента
                        df_wide_for_forecast = pivot_to_wide_format(df_history)

                        # Строим прогноз (передаем широкий формат)
                        last_month = get_next_month_name(df_history, 'date')
                        forecast_df = build_cashflow_forecast(df_wide_for_forecast, last_month)

                        # forecast_df содержит новую колонку 'ai_forecast' с прогнозами
                        # Создаем обновленный DataFrame на основе df_display
                        updated_df = edited_df.copy()

                        # Обновляем колонку прогноза значениями из AI
                        # Проверяем, что порядок категорий совпадает
                        for idx, category in enumerate(forecast_df['category']):
                            # Находим индекс этой категории в edited_df
                            category_idx = updated_df[updated_df['category'] == category].index
                            if len(category_idx) > 0:
                                updated_df.loc[category_idx[0], forecast_col] = forecast_df.loc[idx, 'ai_forecast']
                                updated_df.loc[category_idx[0], comment_col] = forecast_df.loc[idx, 'ai_comments']

                        # Пересчитываем итого
                        updated_df[total_col] = updated_df[forecast_col] + updated_df[adjustment_col]

                        # Сохраняем обновленные данные
                        st.session_state['edited_df'] = updated_df

                        st.success(f"✅ Прогноз построен! Обновлено {len(forecast_df)} категорий")
                        st.rerun()

                # except ImportError:
                #     st.warning(
                #         "⚠️ Модуль agents/forecast_agent.py не найден. "
                #         "Вы можете вручную заполнить колонку 'Прогноз' или реализовать AI-агента."
                #     )
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    st.error(f"❌ Ошибка при построении прогноза: {str(e)}")
                    with st.expander("Подробности ошибки (для отладки)"):
                        st.code(error_details)

            # Форма сохранения
            with st.form("save_scenario_form"):
                st.subheader("💾 Сохранить сценарий")
                description = st.text_area("Описание сценария (опционально)")

                submitted = st.form_submit_button("Сохранить в БД", type="primary")

                if submitted:
                    try:
                        # Преобразуем широкий формат обратно в длинный для сохранения
                        rows = []
                        for _, row in edited_df.iterrows():
                            rows.append({
                                'category': row['category'],
                                'period_date': next_month,
                                'forecast_amount': row[forecast_col],
                                'adjustment_amount': row[adjustment_col],
                                'final_amount': row[total_col]
                            })

                        # Сохранение
                        scenario_id = save_scenario(
                            forecast_period=next_month,
                            rows=rows,
                            description=description if description else None
                        )

                        st.success(f"✅ Сценарий успешно сохранен! ID: {scenario_id}")

                    except Exception as e:
                        st.error(f"❌ Ошибка при сохранении: {str(e)}")

        except Exception as e:
            st.error(f"❌ Ошибка загрузки файла: {str(e)}")

    else:
        st.info("👆 Загрузите файл для начала работы")

# === TAB 2: ИСТОРИЯ ===
with tab2:
    st.header("📜 История сценариев")

    try:
        scenarios = get_scenarios_list()

        if scenarios:
            # Показываем таблицу сценариев
            scenarios_df = pd.DataFrame(scenarios)
            scenarios_df['created_at'] = pd.to_datetime(scenarios_df['created_at'])

            st.dataframe(
                scenarios_df[[
                    'id', 'created_at', 'forecast_period',
                    'description', 'total_final_amount'
                ]],
                column_config={
                    "id": "ID",
                    "created_at": st.column_config.DatetimeColumn("Создан", format="DD.MM.YYYY HH:mm"),
                    "forecast_period": "Период",
                    "description": "Описание",
                    "total_final_amount": st.column_config.NumberColumn("Итого", format="%.2f")
                },
                hide_index=True,
                use_container_width=True
            )

            st.divider()

            # Выбор сценария для просмотра
            scenario_id = st.selectbox(
                "Выберите сценарий для просмотра детализации",
                options=[s['id'] for s in scenarios],
                format_func=lambda x: f"Сценарий #{x} - {next(s['forecast_period'] for s in scenarios if s['id'] == x)}"
            )

            if scenario_id:
                lines = get_scenario_lines(scenario_id)
                if lines:
                    st.subheader(f"Детализация сценария #{scenario_id}")
                    lines_df = pd.DataFrame(lines)
                    st.dataframe(lines_df, use_container_width=True, hide_index=True)

        else:
            st.info("📭 Пока нет сохраненных сценариев")

    except Exception as e:
        st.error(f"❌ Ошибка загрузки истории: {str(e)}")
