import pandas as pd
import time
from utils.matching import get_top_matches

# === Configuration ===
CLIENT_FILE = "client_products.xlsx"
IWD_FILE = "iwd_products.xlsx"
OUTPUT_FILE = "matched_products.xlsx"
SOURCE_COL = 'name'  # Column to match against in iwd_df
TOP_N = 5

# === Load Data ===
print("🔄 Loading Excel files...")
client_df = pd.read_excel(CLIENT_FILE)
iwd_df = pd.read_excel(IWD_FILE)

# Normalize columns
client_df.columns = client_df.columns.str.strip().str.lower()
iwd_df.columns = iwd_df.columns.str.strip().str.lower()

if SOURCE_COL not in iwd_df.columns:
    raise ValueError(f"'{SOURCE_COL}' column not found in IWD products.")

print(f"✅ Loaded {len(client_df)} client products and {len(iwd_df)} IWD products.\n")

# === Match Each Client Product ===
results = []
start_time = time.time()

for idx, row in client_df.iterrows():
    client_product = row['artikelbezeichnung']
    print(f"🔍 Matching product {idx + 1}/{len(client_df)}: '{client_product}'")

    match_start = time.time()
    matches = get_top_matches(client_product, iwd_df, top_n=TOP_N, source_col=SOURCE_COL)
    match_duration = time.time() - match_start

    for match in matches:
        results.append({
            'client_product': client_product,
            'iwd_product': match['name'],
            'article_number': match['article_number'],
            'combined_score': match['combined_score']
        })

    print(f"   ✔ Found {len(matches)} matches in {match_duration:.2f}s")

total_duration = time.time() - start_time

# === Save Results ===
df_results = pd.DataFrame(results)
df_results.to_excel(OUTPUT_FILE, index=False)

print("\n📁 Matching complete.")
print(f"💾 Results saved to: {OUTPUT_FILE}")
print(f"🕒 Total time: {total_duration:.2f}s for {len(client_df)} products")
