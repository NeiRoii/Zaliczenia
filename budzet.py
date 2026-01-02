import streamlit as st
import pandas as pd
import plotly.express as px


# 1. KONFIGURACJA STRONY

st.set_page_config(
    page_title="Budżet 6 Słoików",
    page_icon="💰",
    layout="wide"
)


# 2. TYTUŁ I DANE WEJŚCIOWE


st.markdown(
    """
    <h1 style='text-align: center; font-size: 3.5rem; margin-bottom: 2rem;'>
        Stwórz swój budżet do zera
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


# 3. DANE I KOLORY


COLOR_MAP = {
    "Wydatki<br>Konieczne (NEC)": "#3366CC",
    "Konto Wolności<br>Finansowej (FFA)": "#109618",
    "Oszczędności<br>Długoterminowe (LTSS)": "#FF9900",
    "Edukacja (EDU)": "#990099",
    "Przyjemności (PLAY)": "#DC3912",
    "Pomoc Innym<br>(GIVE)": "#0099C6"
}

# Domyślne wartości procentowe
DEFAULT_PERCENTS = [50, 15, 12, 12, 10, 1]
CATEGORIES = list(COLOR_MAP.keys())
DESCRIPTIONS = [
    "Jedzenie, rachunki, czynsz",
    "Inwestycje, pasywny dochód",
    "Wakacje, samochód, dom",
    "Książki, kursy, rozwój",
    "Kino, restauracje, hobby",
    "Charytatywność, prezenty"
]


# 4. INTERAKTYWNA TABELA (WŁASNA IMPLEMENTACJA)


col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📋 Edytuj swój budżet")
    st.caption("Zmieniaj procenty poniżej. Suma musi wynosić 100%.")

    # Tworzymy nagłówki naszej "tabeli"
    h1, h2, h3 = st.columns([3, 1.5, 2])
    h1.markdown("**Słoik (Kategoria)**")
    h2.markdown("**Procent %**")
    h3.markdown("**Wyliczona Kwota**")

    st.divider() # Linia oddzielająca nagłówek

    # --- PĘTLA TWORZĄCA WIERSZE ---
    current_percents = []

    # Iterujemy przez wszystkie kategorie, aby stworzyć wiersze
    for i, category in enumerate(CATEGORIES):
        c1, c2, c3 = st.columns([3, 1.5, 2])

        # Kolor tekstu pobieramy z mapy
        color = COLOR_MAP[category]
        # Usuwamy <br> z nazwy do wyświetlania w linii (żeby nie łamało w tabeli dziwnie)
        display_name = category.replace("<br>", " ")

        # KOLUMNA 1: Kolorowa nazwa słoika
        with c1:
            st.markdown(
                f"<div style='color: {color}; font-weight: bold; padding-top: 10px;'>{display_name}</div>",
                unsafe_allow_html=True
            )
            # Mały opis pod spodem
            st.caption(DESCRIPTIONS[i])

        # KOLUMNA 2: Input do wpisywania procentów
        with c2:
            val = st.number_input(
                label="%",
                min_value=0,
                max_value=100,
                value=DEFAULT_PERCENTS[i],
                step=1,
                key=f"input_{i}", # Unikalny klucz dla każdego pola
                label_visibility="collapsed" # Ukrywamy etykietę "Procent", bo jest w nagłówku
            )
            current_percents.append(val)

        # KOLUMNA 3: Podgląd kwoty "na żywo" dla tego wiersza
        with c3:
            calc_amount = (val / 100) * income
            st.markdown(
                f"<div style='font-weight: bold; padding-top: 10px; text-align: right;'>{calc_amount:.2f} zł</div>",
                unsafe_allow_html=True
            )

        st.markdown("<hr style='margin: 5px 0'>", unsafe_allow_html=True) # Cienka linia między wierszami

    # --- LOGIKA BLOKADY I SUMOWANIA ---
    total_percent = sum(current_percents)

    if total_percent > 100:
        over = total_percent - 100
        st.error(f"⛔ **Przekroczono limit!** Suma: {total_percent}%. Usuń {over}%.")
        st.stop()
    elif total_percent < 100:
        left = 100 - total_percent
        st.warning(f"⚠️ Do rozdania: **{left}%**. (Suma: {total_percent}%)")
    else:
        st.success("✅ Budżet idealny (100%).")

    # Tworzymy DataFrame wynikowy potrzebny do wykresu
    final_data = {
        "Słoik (Kategoria)": CATEGORIES,
        "Procent": current_percents,
        "Kwota": [(p/100)*income for p in current_percents],
        "Opis": DESCRIPTIONS
    }
    final_df = pd.DataFrame(final_data)
    final_df["Udział %"] = final_df["Procent"].astype(str) + "%"

    total_alloc = final_df["Kwota"].sum()
    st.info(f"Łącznie rozdysponowano: **{total_alloc:.2f} zł**")



# 5. WIZUALIZACJA (WYKRES)


with col_right:
    st.subheader("📊 Wizualizacja")

    font_sizes = []
    font_colors = []

    for kategoria in final_df["Słoik (Kategoria)"]:
        if "FFA" in kategoria or "LTSS" in kategoria:
            font_sizes.append(40)
        else:
            font_sizes.append(20)
        font_colors.append("white")

    fig = px.pie(
        final_df,
        values='Kwota',
        names='Słoik (Kategoria)',
        hole=0.45,
        title=f'Podział: {income:.2f} zł',
        color='Słoik (Kategoria)',
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


# 6. STOPKA

st.markdown("---")
st.caption("Aplikacja stworzona w Pythonie (Streamlit + Plotly)."
           "Stworzone na potrzeby zaliczenia przez Piotr Pietrasińskiego i Oliwię Kowalik")
