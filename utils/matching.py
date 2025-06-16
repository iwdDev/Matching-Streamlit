# # matching.py (Place this in utils/ directory)
# import pandas as pd
# import numpy as np
# import re
# import torch
# from sentence_transformers import SentenceTransformer
# import faiss
# import difflib

# model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# # Preprocessing function
# def preprocess(text):
#     text = str(text).lower()
#     text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
#     return text.strip()

# # String similarity
# def calculate_word_similarity(text1, text2):
#     return difflib.SequenceMatcher(None, text1, text2).ratio()

# # Generate embeddings
# def generate_embeddings(texts):
#     texts = [preprocess(t) for t in texts]
#     embeddings = model.encode(texts, convert_to_tensor=True)
#     embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
#     return embeddings.cpu().numpy()

# # Match logic
# def get_top_matches(client_product, your_df, top_n=5):
#     your_names = your_df['name'].astype(str).tolist()
#     your_prices = your_df['price'].astype(float).tolist()

#     client_name_proc = preprocess(client_product)
#     your_names_proc = [preprocess(x) for x in your_names]

#     # Embeddings
#     client_embedding = generate_embeddings([client_name_proc])
#     your_embeddings = generate_embeddings(your_names_proc)

#     index = faiss.IndexFlatIP(client_embedding.shape[1])
#     index.add(your_embeddings)

#     distances, indices = index.search(client_embedding, k=top_n)
#     results = []
#     for i, idx in enumerate(indices[0]):
#         faiss_sim = distances[0][i]
#         name_sim = calculate_word_similarity(client_name_proc, your_names_proc[idx])
#         # price_diff = 1 - abs(float(client_price) - your_prices[idx]) / (float(client_price) + 1e-5)
#         # combined = 0.5 * faiss_sim + 0.3 * name_sim + 0.2 * price_diff
#         combined = 0.6 * faiss_sim + 0.4 * name_sim
#         results.append({
#             'article_number': your_df.iloc[idx]['article_number'],
#             'name': your_df.iloc[idx]['name'],
#             'price': your_df.iloc[idx]['price'],
#             'combined_score': round(combined, 3)
#         })
#     return sorted(results, key=lambda x: -x['combined_score'])



# matching.py (Place in utils/)
import pandas as pd
import numpy as np
import re
import torch
from sentence_transformers import SentenceTransformer
import faiss
import difflib

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def preprocess(text):
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\\s]", "", text)
    return text.strip()

def calculate_word_similarity(text1, text2):
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def generate_embeddings(texts):
    texts = [preprocess(t) for t in texts]
    embeddings = model.encode(texts, convert_to_tensor=True)
    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
    return embeddings.cpu().numpy()
def get_top_matches(client_product, your_df, top_n=5, source_col='name'):
    import re, torch, difflib
    from sentence_transformers import SentenceTransformer
    import faiss

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def preprocess(text):
        text = str(text).lower()
        text = re.sub(r"[^a-zA-Z0-9\\s]", "", text)
        return text.strip()

    def calculate_word_similarity(text1, text2):
        return difflib.SequenceMatcher(None, text1, text2).ratio()

    def generate_embeddings(texts):
        texts = [preprocess(t) for t in texts]
        embeddings = model.encode(texts, convert_to_tensor=True)
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        return embeddings.cpu().numpy()

    your_names = your_df[source_col].astype(str).tolist()
    your_names_proc = [preprocess(x) for x in your_names]
    client_name_proc = preprocess(client_product)

    client_embedding = generate_embeddings([client_name_proc])
    your_embeddings = generate_embeddings(your_names_proc)

    index = faiss.IndexFlatIP(client_embedding.shape[1])
    index.add(your_embeddings)

    distances, indices = index.search(client_embedding, k=top_n)
    results = []
    for i, idx in enumerate(indices[0]):
        faiss_sim = distances[0][i]
        name_sim = calculate_word_similarity(client_name_proc, your_names_proc[idx])
        combined = 0.6 * faiss_sim + 0.4 * name_sim

        results.append({
            'name': your_df.iloc[idx][source_col],
            'price': your_df.iloc[idx].get('preis', 'N/A'),
            'combined_score': round(combined, 3)
        })
    return sorted(results, key=lambda x: -x['combined_score'])
