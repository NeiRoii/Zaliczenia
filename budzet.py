import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. KONFIGURACJA STRONY
# ---------------------------------------------------------
st.set_page_config(
    page_title="Budżet 6 Słoików",
    page_icon="💰",
    layout="wide"
)

# ---------------------------------------------------------
# 2. FUNKCJE POMOCNICZE I STYLE
# ---------------------------------------------------------
# Funkcja do stylizacji tytułu na środku
def main_header():
    st.markdown(
        """
        <h1 style='text-align: center; font-size: 3.5rem; margin-bottom: 2rem;'>
            Stwórz swój budżet do zera
        </h1>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# 3. INTERFEJS UŻYTKOWNIKA - SIDEBAR (MOTYW)
# ---------------------------------------------------------
# Streamlit automatycznie wykrywa motyw systemowy, ale tutaj
# dodajemy kontrolę nad wyglądem wykresu, aby pasował do preferencji.
st.sidebar.header("Ustawienia wyglądu")
theme_mode = st.sidebar.radio(
    "Wybierz motyw wykresu:",
    ("Ciemny (Dark)", "Jasny (Light)"),
    index=0  # Domyślnie Ciemny
)

# Mapowanie wyboru na template Plotly
plotly_template = "plotly_dark" if theme_mode == "Ciemny (Dark)" else "plotly_white"

# ---------------------------------------------------------
# 4. GŁÓWNA CZĘŚĆ APLIKACJI
# ---------------------------------------------------------

main_header()

# Kontener na dane wejściowe
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### 💸 Wpisz swój miesięczny dochód (netto)")
    income = st.number_input(
        label="",
        min_value=0.0,
        value=5000.0,
        step=100.0,
        format="%.2f",
        help="Wpisz kwotę, którą dysponujesz w tym miesiącu."
    )

st.markdown("---")

# ---------------------------------------------------------
# 5. LOGIKA OBLICZEŃ (6 SŁOIKÓW)
# ---------------------------------------------------------

# Definicja zasad 6 słoików Harva Ekera
data = {
    "Słoik (Kategoria)": [
        "Wydatki Konieczne (NEC)",
        "Konto Wolności Finansowej (FFA)",
        "Oszczędności Długoterminowe (LTSS)",
        "Edukacja (EDU)",
        "Przyjemności (PLAY)",
        "Pomoc Innym (GIVE)"
    ],
    "Procent": [0.55, 0.10, 0.10, 0.10, 0.10, 0.05],
    "Opis": [
        "Jedzenie, rachunki, czynsz",
        "Inwestycje, pasywny dochód",
        "Wakacje, samochód, dom",
        "Książki, kursy, rozwój",
        "Kino, restauracje, hobby",
        "Charytatywność, prezenty"
    ]
}

# Tworzenie DataFrame
df = pd.DataFrame(data)

# Obliczanie kwot na podstawie wpisanego dochodu
df["Kwota"] = df["Procent"] * income

# Formatowanie wyświetlania procentów (np. 0.55 -> 55%)
df["Udział %"] = (df["Procent"] * 100).astype(int).astype(str) + "%"

# ---------------------------------------------------------
# 6. WYŚWIETLANIE DANYCH (TABELA I WYKRES)
# ---------------------------------------------------------

# Układ: Tabela po lewej, Wykres po prawej (na dużych ekranach)
# Na telefonach ułożą się jedno pod drugim.
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📋 Twój podział budżetu")

    # Wyświetlenie tabeli. Używamy st.dataframe dla ładnego formatowania.
    # Ukrywamy kolumnę "Procent" (surową), pokazujemy sformatowaną "Udział %".
    st.dataframe(
        df[["Słoik (Kategoria)", "Udział %", "Kwota", "Opis"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Kwota": st.column_config.NumberColumn(
                "Kwota (PLN)",
                format="%.2f zł"
            )
        }
    )

    # Podsumowanie
    total_alloc = df["Kwota"].sum()
    st.info(f"Łącznie rozdysponowano: **{total_alloc:.2f} zł**")

with right_col:
    st.subheader("📊 Wizualizacja (Donut Chart)")

    # Tworzenie wykresu Donut za pomocą Plotly Express
    fig = px.pie(
        df,
        values='Kwota',
        names='Słoik (Kategoria)',
        hole=0.5, # To tworzy "dziurę" w środku (Donut)
        title=f'Podział dochodu: {income:.2f} zł',
        template=plotly_template, # Zastosowanie wybranego motywu
        hover_data=['Opis']
    )

    # Dostosowanie wyglądu wykresu
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=False, # Ukrywamy legendę, bo etykiety są na wykresie
        margin=dict(t=50, b=0, l=0, r=0)
    )

    # Wyświetlenie wykresu w Streamlit
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 7. STOPKA / EXPORT
# ---------------------------------------------------------
st.markdown("---")
st.caption("Aplikacja stworzona w Pythonie (Streamlit + Plotly). Metoda budżetowania wg T. Harva Ekera.")