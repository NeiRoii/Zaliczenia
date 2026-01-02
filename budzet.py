import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# ---------------------------------------------------------
# 1. KONFIGURACJA STRONY
# ---------------------------------------------------------
st.set_page_config(
    page_title="Budżet 6 Słoików",
    page_icon="💰",
    layout="wide"
)

# ---------------------------------------------------------
# 3. TYTUŁ I DANE WEJŚCIOWE
# ---------------------------------------------------------

st.markdown(
    """
    <h1 style='text-align: center; font-size: 3rem; margin-bottom: 2rem;'>
        Stwórz swój budżet do zera na podstawie zasady 6 słoików
    </h1>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### 💸 Wpisz swój miesięczny dochód (netto)")
    income = st.number_input(
        label="Kwota w PLN",
        min_value=0.0,
        value=4666.0,
        step=100.0,
        format="%.2f",
        help="Wpisz kwotę, którą dysponujesz w tym miesiącu."
    )

st.markdown("---")

# ---------------------------------------------------------
# 4. DANE I KOLORY
# ---------------------------------------------------------

COLOR_MAP = {
    "Wydatki<br>Konieczne (NEC)": "#3366CC",
    "Konto Wolności<br>Finansowej (FFA)": "#109618",
    "Oszczędności<br>Długoterminowe (LTSS)": "#FF9900",
    "Edukacja (EDU)": "#990099",
    "Przyjemności (PLAY)": "#DC3912",
    "Pomoc Innym<br>(GIVE)": "#0099C6"
}

DEFAULT_PERCENTS = [55.0, 10.0, 10.0, 10.0, 10.0, 5.0]
CATEGORIES = list(COLOR_MAP.keys())
DESCRIPTIONS = [
    "Jedzenie, rachunki, czynsz",
    "Inwestycje, pasywny dochód",
    "Wakacje, samochód, dom",
    "Książki, kursy, rozwój",
    "Kino, restauracje, hobby",
    "Charytatywność, prezenty"
]

# ---------------------------------------------------------
# 5. INTERAKTYWNA TABELA
# ---------------------------------------------------------

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📋 Edytuj swój budżet")
    st.caption("Zmieniaj procenty poniżej (możesz używać ułamków). Suma musi wynosić 100%.")

    h1, h2, h3 = st.columns([3, 1.5, 2])
    h1.markdown("**Słoik (Kategoria)**")
    h2.markdown("**Procent %**")
    h3.markdown("**Wyliczona Kwota**")

    st.divider()

    current_percents = []

    for i, category in enumerate(CATEGORIES):
        c1, c2, c3 = st.columns([3, 1.5, 2])

        color = COLOR_MAP[category]
        display_name = category.replace("<br>", " ")

        with c1:
            st.markdown(
                f"<div style='color: {color}; font-weight: bold; padding-top: 10px;'>{display_name}</div>",
                unsafe_allow_html=True
            )
            st.caption(DESCRIPTIONS[i])

        with c2:
            val = st.number_input(
                label="%",
                min_value=0.0,
                max_value=100.0,
                value=float(DEFAULT_PERCENTS[i]),
                step=0.01,
                format="%.2f",
                key=f"input_{i}",
                label_visibility="collapsed"
            )
            current_percents.append(val)

        with c3:
            calc_amount = (val / 100) * income
            st.markdown(
                f"<div style='font-weight: bold; padding-top: 10px; text-align: right;'>{calc_amount:.2f} zł</div>",
                unsafe_allow_html=True
            )

        st.markdown("<hr style='margin: 5px 0'>", unsafe_allow_html=True)

    # Walidacja sumy
    total_percent = round(sum(current_percents), 2)

    if total_percent > 100.00:
        over = round(total_percent - 100.00, 2)
        st.error(f"⛔ **Przekroczono limit!** Suma: {total_percent}%. Usuń {over}%.")
        st.stop()
    elif total_percent < 100.00:
        left = round(100.00 - total_percent, 2)
        st.warning(f"⚠️ Do rozdania: **{left}%**. (Suma: {total_percent}%)")
    else:
        st.success("✅ Budżet idealny (100.00%).")

    # Tworzenie DataFrame
    raw_data = {
        "Słoik": CATEGORIES,
        "Procent": current_percents,
        "Kwota": [(p/100)*income for p in current_percents],
        "Opis": DESCRIPTIONS
    }
    df_raw = pd.DataFrame(raw_data)

    total_alloc = df_raw["Kwota"].sum()
    st.info(f"Łącznie rozdysponowano: **{total_alloc:.2f} zł**")


# ---------------------------------------------------------
# 6. SQL & WIZUALIZACJA
# ---------------------------------------------------------

with col_right:
    st.subheader("📊 Wizualizacja ")

    conn = sqlite3.connect(':memory:')
    df_raw.to_sql('budzet_domowy', conn, index=False, if_exists='replace')

    sql_query = """
        SELECT 
            "Słoik" as Kategoria, 
            Kwota, 
            Opis 
        FROM 
            budzet_domowy
        WHERE 
            Kwota > 0
    """
    df_sql = pd.read_sql(sql_query, conn)

    font_sizes = []
    font_colors = []

    for kategoria in df_sql["Kategoria"]:
        if "FFA" in kategoria or "LTSS" in kategoria:
            font_sizes.append(40)
        else:
            font_sizes.append(20)
        font_colors.append("white")

    fig = px.pie(
        df_sql,
        values='Kwota',
        names='Kategoria',
        hole=0.45,
        title=f'Podział: {income:.2f} zł',
        color='Kategoria',
        color_discrete_map=COLOR_MAP,
        hover_data=['Opis']
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        insidetextorientation='horizontal',
        textfont_size=font_sizes,
        textfont_color=font_colors
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(t=50, b=0, l=0, r=0)
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 7. STOPKA
# ---------------------------------------------------------
st.markdown("---")
st.caption("Aplikacja stworzona w Pythonie. Dane wykresu przetworzone przez SQL (SQLite)."
           "Stworzone na potrzeby zaliczenia przez Piotra Pietrasińskiego i Oliwię Kowalik")