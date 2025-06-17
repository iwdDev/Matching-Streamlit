import pandas as pd

df = pd.read_excel('matched_products.xlsx')
df.to_csv('matched_products.csv', index=False)