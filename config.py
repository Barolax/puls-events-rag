"""
Configuration centralisée du projet Puls-Events RAG
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# ========================================
# API CONFIGURATION
# ========================================
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENAGENDA_API_KEY = os.getenv("OPENAGENDA_API_KEY")

# ========================================
# MISTRAL MODEL CONFIGURATION
# ========================================
MISTRAL_MODEL = "mistral-large-latest"
MISTRAL_EMBED_MODEL = "mistral-embed"

# Model Parameters
TEMPERATURE = 0.4
MAX_TOKENS = 1000
TOP_P = 0.9

# ========================================
# RAG CONFIGURATION
# ========================================
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

# ========================================
# MEMORY CONFIGURATION
# ========================================
USE_MEMORY = True
MEMORY_WINDOW_SIZE = 5

# ========================================
# OPENAGENDA CONFIGURATION
# ========================================
OPENAGENDA_REGION = "Lyon"
OPENAGENDA_MAX_EVENTS = 1000

# ========================================
# PATHS
# ========================================
DATA_RAW_PATH = "data/raw/"
DATA_PROCESSED_PATH = "data/processed/"
VECTOR_STORE_PATH = "vector_store/faiss_index/"

# ========================================
# VALIDATION
# ========================================
def validate_config():
    """Valider que la configuration est complète"""
    if not MISTRAL_API_KEY:
        raise ValueError("❌ MISTRAL_API_KEY manquante dans le fichier .env")
    if not OPENAGENDA_API_KEY:
        raise ValueError("❌ OPENAGENDA_API_KEY manquante dans le fichier .env")
    print("✅ Configuration validée avec succès")

if __name__ == "__main__":
    validate_config()