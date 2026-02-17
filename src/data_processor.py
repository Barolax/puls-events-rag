"""
Nettoyage et préparation des données pour la vectorisation
"""
import json
import os
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DATA_RAW_PATH,
    DATA_PROCESSED_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

def load_raw_events():
    """Charge les événements bruts"""
    filepath = os.path.join(DATA_RAW_PATH, "events_lille.json")
    with open(filepath, "r", encoding="utf-8") as f:
        events = json.load(f)
    print(f"📂 {len(events)} événements chargés depuis {filepath}")
    return events

def clean_text(text):
    """Nettoie un texte"""
    if not text:
        return ""
    # Supprimer les liens markdown [texte](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Supprimer les emojis
    text = re.sub(r'[^\w\s\.,;:!?\'\"«»\-\(\)àâäéèêëîïôùûüçœæ]', ' ', text)
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def format_date(date_str):
    """Formate une date ISO en format lisible"""
    if not date_str:
        return "Date non précisée"
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y à %Hh%M")
    except:
        return date_str

def create_event_text(event):
    """
    Crée un texte complet et structuré pour un événement
    C'est ce texte qui sera vectorisé
    """
    parts = []

    # Titre
    if event.get("title"):
        parts.append(f"Événement : {event['title']}")

    # Description
    if event.get("description"):
        desc = clean_text(event["description"])
        if desc:
            parts.append(f"Description : {desc}")

    # Dates
    date_debut = format_date(event.get("date_debut", ""))
    date_fin = format_date(event.get("date_fin", ""))
    if date_debut != "Date non précisée":
        parts.append(f"Date de début : {date_debut}")
    if date_fin != "Date non précisée":
        parts.append(f"Date de fin : {date_fin}")

    # Lieu
    if event.get("lieu"):
        parts.append(f"Lieu : {event['lieu']}")
    if event.get("adresse"):
        parts.append(f"Adresse : {event['adresse']}")
    if event.get("ville"):
        parts.append(f"Ville : {event['ville']}")

    # Tarifs
    if event.get("tarifs"):
        tarif = clean_text(event["tarifs"])
        if tarif:
            parts.append(f"Tarifs : {tarif}")

    # Keywords
    if event.get("keywords"):
        keywords_str = ", ".join(event["keywords"])
        parts.append(f"Catégories : {keywords_str}")

    # URL
    if event.get("url"):
        parts.append(f"Plus d'infos : {event['url']}")

    return "\n".join(parts)

def filter_events(events):
    """
    Filtre les événements invalides
    """
    filtered = []
    removed = 0

    for event in events:
        # Vérifier que l'événement a un titre et une description
        if not event.get("title") or not event.get("description"):
            removed += 1
            continue

        # Vérifier que la description n'est pas trop courte
        desc = clean_text(event.get("description", ""))
        if len(desc) < 20:
            removed += 1
            continue

        filtered.append(event)

    print(f"🧹 {removed} événements supprimés (données insuffisantes)")
    print(f"✅ {len(filtered)} événements conservés")
    return filtered

def process_events(events):
    """
    Traite tous les événements et crée les documents pour la vectorisation
    """
    documents = []

    for event in events:
        # Créer le texte structuré
        text = create_event_text(event)

        if text:
            documents.append({
                "uid": event.get("uid"),
                "text": text,
                "metadata": {
                    "title": event.get("title", ""),
                    "date_debut": event.get("date_debut", ""),
                    "date_fin": event.get("date_fin", ""),
                    "lieu": event.get("lieu", ""),
                    "adresse": event.get("adresse", ""),
                    "ville": event.get("ville", "Lille"),
                    "tarifs": event.get("tarifs", ""),
                    "url": event.get("url", ""),
                    "keywords": event.get("keywords", [])
                }
            })

    return documents

def save_processed_events(documents):
    """Sauvegarde les documents traités"""
    os.makedirs(DATA_PROCESSED_PATH, exist_ok=True)
    filepath = os.path.join(DATA_PROCESSED_PATH, "documents_lille.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    print(f"💾 {len(documents)} documents sauvegardés dans {filepath}")
    return filepath

if __name__ == "__main__":
    # 1. Charger les données brutes
    events = load_raw_events()

    # 2. Filtrer les événements invalides
    events = filter_events(events)

    # 3. Traiter et structurer les données
    documents = process_events(events)

    # 4. Sauvegarder
    filepath = save_processed_events(documents)

    # 5. Afficher un exemple
    if documents:
        print("\n📋 Exemple de document traité :")
        print(documents[0]["text"])