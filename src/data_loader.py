"""
Chargement des données depuis l'API Open Agenda
"""
import requests
import json
import os
from datetime import datetime, timedelta
from tqdm import tqdm
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    OPENAGENDA_API_KEY,
    OPENAGENDA_MAX_EVENTS,
    DATA_RAW_PATH
)

# Configuration Lille
AGENDA_UID = 57621068  # Ville de Lille
BASE_URL = "https://api.openagenda.com/v2"

def get_date_range():
    """Retourne les dates pour filtrer les événements (moins d'un an)"""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    return (
        one_year_ago.strftime("%Y-%m-%d"),
        today.strftime("%Y-%m-%d")
    )

def fetch_events(size=100, after=None):
    """
    Récupère une page d'événements depuis l'API Open Agenda
    """
    date_min, date_max = get_date_range()
    
    headers = {"key": OPENAGENDA_API_KEY}
    
    params = {
        "size": size,
        "lang": "fr",
        "timings[gte]": date_min,
        "timings[lte]": date_max,
    }
    
    # Pagination
    if after:
        params["after"] = after
    
    url = f"{BASE_URL}/agendas/{AGENDA_UID}/events"
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Erreur API: {response.status_code} - {response.text}")
    
    return response.json()

def extract_event_data(event):
    """
    Extrait les informations utiles d'un événement
    """
    # Description en français
    description = ""
    if event.get("description"):
        description = event["description"].get("fr", "")
    
    # Titre en français
    title = ""
    if event.get("title"):
        title = event["title"].get("fr", "")
    
    # Dates
    first_timing = event.get("firstTiming", {})
    last_timing = event.get("lastTiming", {})
    
    # Localisation
    location = event.get("location", {})
    
    # Keywords
    keywords = event.get("keywords", {})
    keywords_fr = keywords.get("fr", []) if keywords else []
    
    return {
        "uid": event.get("uid"),
        "title": title,
        "description": description,
        "date_debut": first_timing.get("begin", ""),
        "date_fin": last_timing.get("end", ""),
        "lieu": location.get("name", ""),
        "adresse": location.get("address", ""),
        "ville": location.get("city", "Lille"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "tarifs": event.get("tarifs", ""),
        "keywords": keywords_fr,
        "slug": event.get("slug", ""),
        "url": f"https://openagenda.com/ville-de-lille/events/{event.get('slug', '')}"
    }

def load_all_events():
    """
    Charge tous les événements avec pagination
    """
    all_events = []
    after = None
    page = 1
    
    print(f"🔄 Chargement des événements de Lille...")
    date_min, date_max = get_date_range()
    print(f"📅 Période : {date_min} → {date_max}")
    
    while len(all_events) < OPENAGENDA_MAX_EVENTS:
        print(f"📄 Page {page}...")
        
        data = fetch_events(size=100, after=after)
        events = data.get("events", [])
        
        if not events:
            print("✅ Plus d'événements disponibles.")
            break
        
        # Extraire les données utiles
        for event in events:
            extracted = extract_event_data(event)
            # Garder uniquement les événements avec titre et description
            if extracted["title"] and extracted["description"]:
                all_events.append(extracted)
        
        print(f"   → {len(all_events)} événements récupérés au total")
        
        # Pagination
        after = data.get("after")
        if not after:
            print("✅ Fin de la pagination.")
            break
        
        page += 1
    
    return all_events

def save_events(events):
    """
    Sauvegarde les événements en JSON
    """
    os.makedirs(DATA_RAW_PATH, exist_ok=True)
    filepath = os.path.join(DATA_RAW_PATH, "events_lille.json")
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    
    print(f"💾 {len(events)} événements sauvegardés dans {filepath}")
    return filepath

if __name__ == "__main__":
    # Charger et sauvegarder les événements
    events = load_all_events()
    filepath = save_events(events)
    
    # Afficher un exemple
    if events:
        print("\n📋 Exemple d'événement récupéré :")
        print(json.dumps(events[0], ensure_ascii=False, indent=2))