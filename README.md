# 🎭 Puls-Events RAG Chatbot

> Chatbot intelligent pour découvrir les événements culturels de Lille utilisant un système RAG (Retrieval Augmented Generation).

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.0-green.svg)](https://langchain.com/)
[![Mistral AI](https://img.shields.io/badge/Mistral-AI-orange.svg)](https://mistral.ai/)

---

## 📋 Description

Ce projet est un **Proof of Concept (POC)** d'un chatbot intelligent capable de :
- 🔍 Rechercher des événements culturels via Open Agenda
- 💬 Répondre aux questions des utilisateurs de manière contextuelle
- 🧠 Maintenir une mémoire conversationnelle
- 🎯 Fournir des recommandations personnalisées

**Score d'évaluation : 93.3%** (14/15 tests réussis)

---

## 🛠️ Technologies utilisées

| Technologie | Rôle |
|------------|------|
| **Mistral AI** | Génération de réponses et embeddings (mistral-large-latest, mistral-embed) |
| **Faiss** | Base de données vectorielle pour la recherche sémantique |
| **LangChain** | Orchestration du système RAG et gestion de la mémoire |
| **Streamlit** | Interface web interactive |
| **Open Agenda API** | Source de données d'événements culturels |
| **Pytest** | Tests unitaires et évaluation |

---

## 📊 Données

- **Source** : Open Agenda - Ville de Lille
- **Période couverte** : Février 2026 - Février 2027
- **Événements récupérés** : 457 événements futurs
- **Documents vectorisés** : 611 documents (avec chunking intelligent)
- **Dimension des vecteurs** : 1024

### Chunking

Le système utilise un découpage intelligent des textes :
- **Taille des chunks** : 500 caractères
- **Chevauchement** : 50 caractères
- **Résultat** : 138 événements découpés en 2-4 chunks

---

## 🚀 Installation

### Prérequis

- Python 3.9+
- Compte Mistral AI ([Créer un compte](https://console.mistral.ai/))
- Compte Open Agenda ([Créer un compte](https://openagenda.com/))

### Étapes

1. **Cloner le repository**
```bash
git clone https://github.com/Barolax/puls-events-rag.git
cd puls-events-rag
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Mac/Linux
# ou
venv\Scripts\activate  # Sur Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**

Créer un fichier `.env` à la racine :
```env
MISTRAL_API_KEY=votre_clé_mistral_ici
OPENAGENDA_API_KEY=votre_clé_openagenda_ici
```

5. **Récupérer et préparer les données**
```bash
python src/data_loader.py
python src/data_processor.py
```

6. **Créer la base vectorielle**
```bash
python -c "
import os, sys, json
sys.path.append('.')
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
from config import MISTRAL_API_KEY, MISTRAL_EMBED_MODEL, DATA_PROCESSED_PATH, VECTOR_STORE_PATH

with open(os.path.join(DATA_PROCESSED_PATH, 'documents_lille.json'), 'r') as f:
    documents = json.load(f)

texts = [doc['text'] for doc in documents]
metadatas = [doc['metadata'] for doc in documents]

embeddings = MistralAIEmbeddings(api_key=MISTRAL_API_KEY, model=MISTRAL_EMBED_MODEL)
vector_store = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
vector_store.save_local(VECTOR_STORE_PATH)
print('✅ Base vectorielle créée !')
"
```

7. **Lancer l'application**
```bash
streamlit run app.py
```

L'interface s'ouvre automatiquement dans votre navigateur sur `http://localhost:8501`

---

## 🧪 Tests

### Tests unitaires
```bash
pytest tests/test_data_validation.py -v
```

**Résultats** : 9/9 tests réussis ✅
- Validation des données (région, dates, formats)
- Vérification de l'intégrité des documents
- Contrôle qualité des métadonnées

### Évaluation du chatbot
```bash
python tests/run_evaluation.py
```

**Score** : 93.3% (14/15 tests réussis) 🎉

Catégories testées :
- Recherche générale et spécifique
- Filtres (gratuit, public, lieu)
- Recherche temporelle
- Mémoire conversationnelle
- Gestion des questions hors contexte

---

## 📁 Structure du projet
```
puls-events-rag/
├── src/
│   ├── data_loader.py          # Récupération données Open Agenda
│   ├── data_processor.py       # Nettoyage et chunking
│   ├── vector_store.py         # Création index Faiss
│   ├── rag_chain.py            # Chaîne RAG LangChain
│   └── chatbot.py              # Logique du chatbot
├── tests/
│   ├── test_data_validation.py # Tests unitaires (9/9)
│   ├── test_dataset.json       # Jeu de données test (15 cas)
│   └── run_evaluation.py       # Évaluation automatique
├── data/
│   ├── raw/                    # Données brutes (457 événements)
│   └── processed/              # Données chunkées (611 documents)
├── vector_store/
│   └── faiss_index/            # Base vectorielle Faiss
├── app.py                      # Interface Streamlit
├── config.py                   # Configuration centralisée
├── requirements.txt            # Dépendances
└── README.md
```

---

## ⚙️ Configuration

Tous les paramètres sont centralisés dans `config.py` :
```python
# Modèle Mistral
MISTRAL_MODEL = "mistral-large-latest"
MISTRAL_EMBED_MODEL = "mistral-embed"
TEMPERATURE = 0.4
MAX_TOKENS = 1000

# RAG
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

# Mémoire conversationnelle
USE_MEMORY = True
MEMORY_WINDOW_SIZE = 5

# Open Agenda
OPENAGENDA_REGION = "Lille"
OPENAGENDA_MAX_EVENTS = 1000
```

---

## 💡 Exemples d'utilisation
```
User: Quels concerts ont lieu à Lille ?
Bot: Voici les concerts à Lille : [liste avec dates, lieux, tarifs]

User: Y a-t-il des expositions gratuites ?
Bot: Oui ! Voici les expositions gratuites : [détails]

User: C'est à quelle heure ?
Bot: [Se souvient de l'exposition] L'exposition est ouverte de 14h à 18h.

User: Quel temps fait-il ?
Bot: Je suis spécialisé dans les événements culturels, pas la météo 😊
```

---

## 🎯 Fonctionnalités

✅ Recherche sémantique avec Faiss (611 vecteurs)  
✅ Chunking intelligent des textes longs  
✅ Filtrage multi-critères (type, date, tarif, public)  
✅ Mémoire conversationnelle (5 derniers échanges)  
✅ Réponses contextuelles en français naturel  
✅ Interface web intuitive (Streamlit)  
✅ Tests unitaires et évaluation automatique  
✅ Gestion des questions hors contexte  

---

## 📈 Performances

| Métrique | Valeur |
|----------|--------|
| **Score d'évaluation** | 93.3% (14/15) |
| **Tests unitaires** | 9/9 réussis |
| **Documents vectorisés** | 611 |

---

## 🔧 Architecture RAG
```
┌─────────────┐
│   Question  │
│ utilisateur │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Vectorisation  │
│  (Mistral AI)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Recherche Faiss │
│  (Top 5 docs)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Génération LLM │
│ + Mémoire (5)   │
│  (Mistral AI)   │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│   Réponse   │
│ contextualisée │
└─────────────┘
```

---

## 📝 Livrables

- ✅ Code source versionné (GitHub)
- ✅ Tests unitaires (9/9 validés)
- ✅ Évaluation chatbot (93.3%)
- ✅ Documentation technique (README)
- ✅ Interface Streamlit fonctionnelle
- ✅ Jeu de données test annoté


