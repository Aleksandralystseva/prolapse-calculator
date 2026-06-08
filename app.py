import streamlit as st
import math

# Заголовок и описание
st.set_page_config(page_title="Калькулятор для оценки индивидуального риска пролапса тазовых органов", page_icon="🩺")
st.title("🩺 Калькулятор для оценки индивидуального риска пролапса тазовых органов")
st.markdown("""
Этот инструмент рассчитывает вероятность **латерального** и **апикального** пролапса 
на основе данных пациентки. Введите значения в поля ниже и нажмите кнопку **"Рассчитать"**.
""")

# Разделитель
st.markdown("---")

# Поля ввода
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Возраст (лет)", min_value=28, max_value=90, value=50, step=1)
    menopause = st.number_input("Длительность постменопаузы (лет)", min_value=0, max_value=45, value=5, step=1)
    bmi = st.number_input("Индекс массы тела (кг/м²)", min_value=15.0, max_value=50.0, value=25.0, step=0.1)
    parity = st.number_input("Количество родов", min_value=0, max_value=10, value=2, step=1)

with col2:
    hernia = st.selectbox("Грыжи другой локализации", ["Нет", "Есть"])
    varicosis = st.selectbox("Варикозная болезнь", ["Нет", "Есть"])
    hyster = st.selectbox("Гистерэктомия в анамнезе", ["Нет", "Есть"])
    macrosomia = st.selectbox("Крупный плод в анамнезе (>4000 г)", ["Нет", "Есть"])
    constipation = st.selectbox("Хронические запоры", ["Нет", "Есть"])
    sui = st.selectbox("Стрессовое недержание мочи", ["Нет", "Есть"])
    diabetes = st.selectbox("Сахарный диабет", ["Нет", "Есть"])

# Преобразование ответов в 0/1
hernia = 1 if hernia == "Есть" else 0
varicosis = 1 if varicosis == "Есть" else 0
hyster = 1 if hyster == "Есть" else 0
macrosomia = 1 if macrosomia == "Есть" else 0
constipation = 1 if constipation == "Есть" else 0
sui = 1 if sui == "Есть" else 0
diabetes = 1 if diabetes == "Есть" else 0

# Кнопка расчета
if st.button("🔍 Рассчитать риск"):
    # ======================
    # Модель латерального ПТО
    # ======================
    Z_lat = (3.41307
             - 0.10400 * age
             - 0.00924 * bmi
             + 0.40834 * parity
             + 2.61323 * macrosomia
             + 3.13523 * constipation
             + 2.41201 * sui)
    prob_lat = 1 / (1 + math.exp(-Z_lat))

    # ======================
    # Модель апикального ПТО
    # ======================
    Z_api = (-4.2704
             + 0.8588 * (menopause / 5)   # пересчет на 5-летние интервалы
             + 0.0623 * bmi
             + 0.3294 * hernia
             + 0.4033 * varicosis
             + 0.7193 * hyster
             - 0.2904 * diabetes)
    prob_api = 1 / (1 + math.exp(-Z_api))

    # Функция интерпретации риска
    def risk_level(prob):
        if prob < 0.15:
            return "🟢 Низкий", "Рекомендуется плановое наблюдение."
        elif prob < 0.30:
            return "🟡 Умеренный", "Рекомендуется консультация гинеколога, контроль в динамике."
        else:
            return "🔴 Высокий", "Показано углубленное обследование и решение вопроса о профилактических мероприятиях."

    level_lat, rec_lat = risk_level(prob_lat)
    level_api, rec_api = risk_level(prob_api)

    # Вывод результатов
    st.markdown("---")
    st.subheader("Результаты расчета")

    col_res1, col_res2 = st.columns(2)

    with col_res1:
        st.markdown(f"### Латеральный ПТО")
        st.metric("Вероятность", f"{prob_lat*100:.1f}%")
        st.markdown(f"**Уровень риска:** {level_lat}")
        st.caption(rec_lat)

    with col_res2:
        st.markdown(f"### Апикальный ПТО")
        st.metric("Вероятность", f"{prob_api*100:.1f}%")
        st.markdown(f"**Уровень риска:** {level_api}")
        st.caption(rec_api)

    # Дополнительные рекомендации
    st.markdown("---")
    st.subheader("Рекомендации")
    if prob_lat > 0.3 and prob_api > 0.3:
        st.warning("⚠️ Высокий риск обеих форм ПТО. Рекомендована консультация урогинеколога, "
                   "комплексное обследование (УЗИ, POP-Q), обсуждение хирургической профилактики.")
    elif prob_lat > 0.3:
        st.info("🔵 Преобладает риск латерального ПТО. Основное внимание – коррекция запоров, "
                "снижение физических нагрузок, упражнения Кегеля, контроль недержания мочи.")
    elif prob_api > 0.3:
        st.info("🟣 Преобладает риск апикального ПТО. Рекомендовано наблюдение гинеколога, "
                "оценка менопаузального статуса, при планировании гистерэктомии – "
                "рассмотреть профилактическую фиксацию купола влагалища.")
    else:
        st.success("✅ Риск обеих форм низкий. Продолжение стандартного наблюдения.")

st.markdown("---")
st.caption("Модели основаны на данных ретроспективного исследования (n=306). "
           "Апикальная модель не включает артериальную гипертензию из-за эффекта подавления.")
