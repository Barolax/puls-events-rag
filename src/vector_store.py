"""
Création et gestion de la base vectorielle Faiss
"""
import json
import os
import sys
import faiss
import numpy as np
import pickle
from tqdm import tqdm
from mistralai import Mistral

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    MISTRAL_API_KEY,
    MISTRAL_EMBED_MODEL,
    DATA_PROCESSED_PATH,
    VECTOR_STORE_PATH
)

# Initialiser le client Mistral
client = Mistral(api_key=MISTRAL_API_KEY)

def load_documents():
    """Charge les documents traités"""
    filepath = os.path.join(DATA_PROCESSED_PATH, "documents_lille.json")
    with open(filepath, "r", encoding="utf-8") as f:
        documents = json.load(f)
    print(f"📂 {len(documents)} documents chargés")
    return documents

def get_embeddings(texts, batch_size=10):
    """
    Génère les embeddings via l'API Mistral
    On envoie les textes par batch pour éviter de dépasser les limites de l'API
    """
    import time
    all_embeddings = []

    for i in tqdm(range(0, len(texts), batch_size), desc="🔄 Génération des embeddings"):
        batch = texts[i:i + batch_size]

        # Retry en cas de rate limit
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.embeddings.create(
                    model=MISTRAL_EMBED_MODEL,
                    inputs=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                break
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    print(f"\n⚠️ Rate limit atteint, pause de {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e

        # Pause entre chaque batch
        time.sleep(1.5)

    return all_embeddings

def create_faiss_index(embeddings):
    """
    Crée un index Faiss à partir des embeddings
    """
    embeddings_array = np.array(embeddings, dtype=np.float32)
    dimension = embeddings_array.shape[1]
    print(f"📐 Dimension des vecteurs : {dimension}")

    # Normaliser les vecteurs (pour la similarité cosinus)
    faiss.normalize_L2(embeddings_array)

    # Créer l'index
    index = faiss.IndexFlatIP(dimension)  # IP = Inner Product (similarité cosinus)
    index.add(embeddings_array)

    print(f"✅ Index Faiss créé avec {index.ntotal} vecteurs")
    return index

def save_vector_store(index, documents):
    """
    Sauvegarde l'index Faiss et les métadonnées
    """
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

    # Sauvegarder l'index Faiss
    index_path = os.path.join(VECTOR_STORE_PATH, "events.index")
    faiss.write_index(index, index_path)
    print(f"💾 Index Faiss sauvegardé : {index_path}")

    # Sauvegarder les métadonnées (pour retrouver les infos des événements)
    metadata_path = os.path.join(VECTOR_STORE_PATH, "metadata.pkl")
    with open(metadata_path, "wb") as f:
        pickle.dump(documents, f)
    print(f"💾 Métadonnées sauvegardées : {metadata_path}")

def load_vector_store():
    """
    Charge l'index Faiss et les métadonnées depuis le disque
    """
    index_path = os.path.join(VECTOR_STORE_PATH, "events.index")
    metadata_path = os.path.join(VECTOR_STORE_PATH, "metadata.pkl")

    index = faiss.read_index(index_path)
    with open(metadata_path, "rb") as f:
        documents = pickle.load(f)

    print(f"✅ Index Faiss chargé : {index.ntotal} vecteurs")
    return index, documents

def search(query, index, documents, top_k=5):
    """
    Recherche les documents les plus similaires à une requête
    """
    # Vectoriser la requête
    response = client.embeddings.create(
        model=MISTRAL_EMBED_MODEL,
        inputs=[query]
    )
    query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
    faiss.normalize_L2(query_embedding)

    # Rechercher dans Faiss
    scores, indices = index.search(query_embedding, top_k)

    # Retourner les documents correspondants
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx != -1:
            results.append({
                "document": documents[idx],
                "score": float(score)
            })

    return results

if __name__ == "__main__":
    # 1. Charger les documents
    documents = load_documents()

    # 2. Extraire les textes
    texts = [doc["text"] for doc in documents]

    # 3. Générer les embeddings
    print(f"\n🚀 Génération des embeddings pour {len(texts)} documents...")
    embeddings = get_embeddings(texts, batch_size=10)

    # 4. Créer l'index Faiss
    print("\n🏗️ Création de l'index Faiss...")
    index = create_faiss_index(embeddings)

    # 5. Sauvegarder
    save_vector_store(index, documents)

    # 6. Test de recherche
    print("\n🧪 Test de recherche...")
    index, documents = load_vector_store()
    results = search("concert de musique à Lille", index, documents, top_k=3)

    print("\n🎯 Résultats pour 'concert de musique à Lille' :")
    for i, result in enumerate(results):
        print(f"\n--- Résultat {i+1} (score: {result['score']:.3f}) ---")
        print(result["document"]["text"][:300])