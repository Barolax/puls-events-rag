"""
Tests unitaires - Validation des données événements
"""
import json
import os
import sys
import pytest
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_RAW_PATH, DATA_PROCESSED_PATH

# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def raw_events():
    """Charge les événements bruts"""
    filepath = os.path.join(DATA_RAW_PATH, "events_lille.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def processed_documents():
    """Charge les documents traités"""
    filepath = os.path.join(DATA_PROCESSED_PATH, "documents_lille.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# ========================================
# TESTS - DONNÉES BRUTES
# ========================================

def test_raw_events_not_empty(raw_events):
    """Vérifie que des événements ont bien été récupérés"""
    assert len(raw_events) > 0, "Aucun événement récupéré !"
    print(f"✅ {len(raw_events)} événements récupérés")

def test_raw_events_have_required_fields(raw_events):
    """Vérifie que chaque événement a les champs obligatoires"""
    required_fields = ["uid", "title", "date_debut", "ville"]
    for event in raw_events:
        for field in required_fields:
            assert field in event, f"Champ '{field}' manquant dans l'événement {event.get('uid')}"
    print(f"✅ Tous les champs obligatoires sont présents")

def test_events_are_in_lille(raw_events):
    """Vérifie que les événements sont bien à Lille"""
    non_lille = []
    for event in raw_events:
        ville = event.get("ville", "").lower()
        if ville and ville != "lille":
            non_lille.append({
                "uid": event.get("uid"),
                "ville": event.get("ville"),
                "title": event.get("title")
            })

    # On tolère 10% d'événements hors Lille (événements régionaux)
    tolerance = len(raw_events) * 0.10
    assert len(non_lille) <= tolerance, (
        f"{len(non_lille)} événements hors Lille trouvés "
        f"(tolérance : {int(tolerance)})"
    )
    print(f"✅ {len(raw_events) - len(non_lille)}/{len(raw_events)} événements à Lille")

def test_events_dates_are_valid(raw_events):
    """Vérifie que les dates sont valides"""
    invalid_dates = []
    for event in raw_events:
        date_str = event.get("date_debut", "")
        if date_str:
            try:
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                invalid_dates.append(event.get("uid"))

    assert len(invalid_dates) == 0, (
        f"Dates invalides pour les événements : {invalid_dates}"
    )
    print(f"✅ Toutes les dates sont valides")

def test_events_within_one_year(raw_events):
    """
    Vérifie que les événements sont dans la plage d'un an
    (passé ou futur selon la configuration)
    """
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    one_year_later = today + timedelta(days=365)

    out_of_range = []
    for event in raw_events:
        date_str = event.get("date_debut", "")
        if not date_str:
            continue
        try:
            event_date = datetime.fromisoformat(
                date_str.replace('Z', '+00:00')
            ).replace(tzinfo=None)

            if event_date < one_year_ago or event_date > one_year_later:
                out_of_range.append({
                    "uid": event.get("uid"),
                    "title": event.get("title"),
                    "date": date_str
                })
        except ValueError:
            continue

    assert len(out_of_range) == 0, (
        f"{len(out_of_range)} événements hors plage d'un an : "
        f"{out_of_range[:3]}"
    )
    print(f"✅ Tous les événements sont dans la plage d'un an")

# ========================================
# TESTS - DOCUMENTS TRAITÉS
# ========================================

def test_processed_documents_not_empty(processed_documents):
    """Vérifie que des documents ont été générés"""
    assert len(processed_documents) > 0, "Aucun document traité !"
    print(f"✅ {len(processed_documents)} documents traités")

def test_processed_documents_have_text(processed_documents):
    """Vérifie que chaque document a un texte non vide"""
    empty_texts = []
    for doc in processed_documents:
        if not doc.get("text") or len(doc["text"]) < 20:
            empty_texts.append(doc.get("uid"))

    assert len(empty_texts) == 0, (
        f"Documents avec texte vide ou trop court : {empty_texts}"
    )
    print(f"✅ Tous les documents ont un texte valide")

def test_processed_documents_have_metadata(processed_documents):
    """Vérifie que chaque document a des métadonnées"""
    required_metadata = ["title", "ville"]
    for doc in processed_documents:
        metadata = doc.get("metadata", {})
        for field in required_metadata:
            assert field in metadata, (
                f"Métadonnée '{field}' manquante dans le document {doc.get('uid')}"
            )
    print(f"✅ Toutes les métadonnées sont présentes")

def test_no_duplicate_events(raw_events):
    """Vérifie qu'il n'y a pas de doublons"""
    uids = [event.get("uid") for event in raw_events]
    unique_uids = set(uids)
    assert len(uids) == len(unique_uids), (
        f"{len(uids) - len(unique_uids)} événements en doublon détectés !"
    )
    print(f"✅ Aucun doublon détecté")