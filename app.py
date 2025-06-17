import streamlit as st
import pandas as pd
import os

# Daten einlesen und cachen
@st.cache_data
def load_data():
    df = pd.read_csv("matched_products.csv")
    df.columns = ['client_product', 'iwd_product', 'article_number', 'score']
    return df

df = load_data()

# Fortschritt berechnen
all_client_products = df['client_product'].drop_duplicates().tolist()
total_products = len(all_client_products)

# Lade bestehende Zuordnungen
output_file = "zuordnungen.csv"
if 'matched' not in st.session_state:
    if os.path.exists(output_file):
        matched_df = pd.read_csv(output_file)
        st.session_state.matched = set(matched_df['client_product'].unique())
    else:
        st.session_state.matched = set()

# matched_count wird hier sicher definiert, nachdem matched gesetzt ist
matched_count = len(st.session_state.matched)
progress_percent = matched_count / total_products if total_products > 0 else 0
progress_percent_display = int(progress_percent * 100)

st.markdown(f"**Fortschritt:** {matched_count} von {total_products} Artikeln zugeordnet ({progress_percent_display} %)")
st.progress(progress_percent)

# Lade Index für Navigation
if 'index' not in st.session_state:
    st.session_state.index = 0

# Filtere nur ungematchte Client-Produkte
all_client_products = df['client_product'].unique()
unmatched_products = [p for p in all_client_products if p not in st.session_state.matched]

# Abbruch, wenn alle Produkte erledigt sind
if st.session_state.index >= len(unmatched_products):
    st.success("✅ Alle Produkte wurden zugeordnet.")
    st.stop()
    
# Undo-Button
if st.button("🔙 Letzte Zuordnung rückgängig machen"):
    if os.path.exists(output_file):
        df_existing = pd.read_csv(output_file)
        if len(df_existing) > 0:
            # Letzten Eintrag entfernen
            last_entry = df_existing.iloc[-1]
            last_client_product = last_entry["client_product"]

            df_existing = df_existing.iloc[:-1]  # entferne letzte Zeile
            df_existing.to_csv(output_file, index=False)

            # Session-State anpassen
            st.session_state.matched.discard(last_client_product)
            st.session_state.index = max(0, st.session_state.index - 1)
            st.rerun()
            
# Zeige aktuelles Produkt
current_client_product = unmatched_products[st.session_state.index]
st.markdown(f"### 🔍 **{current_client_product}**")

# Filtere und sortiere passende IWD-Produkte nach Score
filtered = df[df['client_product'] == current_client_product].sort_values(by='score', ascending=False)
iwd_options = [
    f"{row['iwd_product']} (Score: {row['score']:.2f})"
    for _, row in filtered.iterrows()
]
iwd_options.append("❌ Kein Match")

# Auswahlfeld
selected_option = st.radio("Wähle passendes IWD-Produkt:", iwd_options)

# Speichern & weiter
if st.button("✅ Speichern & Weiter"):
    if selected_option == "❌ Kein Match":
        matched_iwd_product = None
    else:
        matched_iwd_product = selected_option.split(" (Score")[0]

    result = {
        "client_product": current_client_product,
        "matched_iwd_product": matched_iwd_product
    }

    result_df = pd.DataFrame([result])
    output_file = "zuordnungen.csv"
    if os.path.exists(output_file):
        existing = pd.read_csv(output_file)
        result_df = pd.concat([existing, result_df], ignore_index=True)

    result_df.to_csv(output_file, index=False)

    # Aktuellen Client-Product als erledigt markieren
    st.session_state.matched.add(current_client_product)
    st.session_state.index += 1
    st.rerun()
