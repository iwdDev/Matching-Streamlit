# # app.py
# import streamlit as st
# import pandas as pd
# from utils.matching import get_top_matches
# import os

# st.set_page_config(layout="wide")

# # Initialize session state
# if 'index' not in st.session_state:
#     st.session_state.index = 0
# if 'matches' not in st.session_state:
#     st.session_state.matches = {}

# # Upload files
# st.sidebar.header("Upload Files")
# client_file = st.sidebar.file_uploader("Upload Client File (.xlsx)", type=["xlsx"])
# your_file = st.sidebar.file_uploader("Upload Your Product Data (.xlsx)", type=["xlsx"])

# if client_file and your_file:
#     client_df = pd.read_excel(client_file)
#     your_df = pd.read_excel(your_file)

#     # Select current product
#     current_idx = st.session_state.index
#     total = len(client_df)

#     st.markdown(f"### Matching Product {current_idx + 1} of {total}")

#     client_product = client_df.iloc[current_idx]
#     client_name = client_product['Artikelbezeichnung']
#     client_price = client_product['Preis KW 22']

#     col1, col2 = st.columns(2)

#     # Left: Client product info
#     with col1:
#         st.subheader("Client Product")
#         st.write(f"**Name:** {client_name}")
#         st.write(f"**Price:** {client_price}")

#     # Right: Matching interface
#     with col2:
#         st.subheader("Suggested Matches")
#         matches = get_top_matches(client_name, client_price, your_df, top_n=5)
#         no_match_option = {
#             'article_number': None,
#             'name': 'No Match',
#             'price': None,
#             'combined_score': 0.0
#         }
#         matches.append(no_match_option)

#         selected = st.radio("Select the best match:",
#                             options=range(len(matches)),
#                             format_func=lambda i: f"{matches[i]['name']} | €{matches[i]['price']} | Score: {matches[i]['combined_score']}" if matches[i]['name'] != 'No Match' else "No Match")

#     # Save selected match in session state
#     if st.button("Save Match"):
#         st.session_state.matches[current_idx] = matches[selected]
#         st.success("Match saved!")

#     # Navigation
#     col_prev, col_next = st.columns(2)
#     with col_prev:
#         if st.button("Previous") and current_idx > 0:
#             st.session_state.index -= 1
#     with col_next:
#         if st.button("Next") and current_idx < total - 1:
#             st.session_state.index += 1

#     # Export results
#     if st.sidebar.button("Export Matched Results"):
#         matched_data = []
#         for idx, match in st.session_state.matches.items():
#             original = client_df.iloc[idx]
#             matched_row = {
#                 'Original_ID': original['Knz'],
#                 'Original_Name': original['Artikelbezeichnung'],
#                 'Original_Price': original['Preis KW 22'],
#                 'Matched_Article_Number': match['article_number'],
#                 'Matched_Name': match['name'],
#                 'Matched_Price': match['price'],
#                 'Score': match['combined_score']
#             }
#             matched_data.append(matched_row)

#         df_matched = pd.DataFrame(matched_data)
#         os.makedirs("results", exist_ok=True)
#         df_matched.to_excel("results/matched_results.xlsx", index=False)
#         st.sidebar.success("Exported to results/matched_results.xlsx")
# app.py
import streamlit as st
import pandas as pd
from utils.matching import get_top_matches
import os

st.set_page_config(layout="wide")

# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'matches' not in st.session_state:
    st.session_state.matches = {}

# Upload files
st.sidebar.header("Upload Files")
client_file = st.sidebar.file_uploader("Upload Client File (.xlsx)", type=["xlsx"])
your_file = st.sidebar.file_uploader("Upload Your OCR Product Data (.xlsx)", type=["xlsx"])

if client_file and your_file:
    client_df = pd.read_excel(client_file)
    your_df = pd.read_excel(your_file)

    # Normalize columns
    your_df.columns = your_df.columns.str.strip().str.lower()
    client_df.columns = client_df.columns.str.strip().str.lower()

    # Select current product
    current_idx = st.session_state.index
    total = len(client_df)

    st.markdown(f"### Matching Product {current_idx + 1} of {total}")

    client_product = client_df.iloc[current_idx]
    client_name = client_product['Artikelbezeichnung']
    # client_article_number = str(client_product.get('article_number', '')).strip()

    col1, col2 = st.columns(2)

    # Left: Client product info
    with col1:
        st.subheader("Client Product")
        st.write(f"**Name:** {client_name}")
        # st.write(f"**Client Article Number:** {client_article_number}")

    # Right: Matching interface
    with col2:
        st.subheader("Suggested Matches")
        matches = get_top_matches(client_name, your_df, top_n=5, source_col='name')

        no_match_option = {
            'article_number': None,
            'name': 'No Match',
            'price': None,
            'combined_score': 0.0
        }
        matches.append(no_match_option)

        selected = st.radio("Select the best match:",
                            options=range(len(matches)),
                            format_func=lambda i: f"{matches[i]['name']} | Score: {matches[i]['combined_score']}" if matches[i]['name'] != 'No Match' else "No Match")

    # Save selected match in session state
    if st.button("Save Match"):
        st.session_state.matches[current_idx] = matches[selected]
        st.success("Match saved!")

    # Navigation
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("Previous") and current_idx > 0:
            st.session_state.index -= 1
    with col_next:
        if st.button("Next") and current_idx < total - 1:
            st.session_state.index += 1

    # Export results
    if st.sidebar.button("Export Matched Results"):
        matched_data = []
        for idx, match in st.session_state.matches.items():
            original = client_df.iloc[idx]
            matched_row = {
                'Original_ID': original['id'] if 'id' in original else '',
                'Original_Name': original['name'],
                'Original_Article_Number': original['article_number'] if 'article_number' in original else '',
                'Matched_Name': match['name'],
                'Score': match['combined_score']
            }
            matched_data.append(matched_row)

        df_matched = pd.DataFrame(matched_data)
        os.makedirs("results", exist_ok=True)
        df_matched.to_excel("results/matched_results.xlsx", index=False)
        st.sidebar.success("Exported to results/matched_results.xlsx")
