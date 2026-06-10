import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITIES = ["Manila", "Quezon City", "Pasig", "Makati", "Caloocan", "Taguig", "Mandaluyong", "Las Piñas", "Parañaque", "Marikina"]
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def extract_city(city: str) -> dict | None:
    """Call API for 1 city. Returns JSON or None."""
   
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status() # Throws error if status!= 200
        logging.info(f"Extracted {city}")
        return r.json()
    except Exception as e:
        logging.error(f"Failed {city}: {e}")
        return None

def save_raw(data: dict, city: str):
    """Save to data/raw/dt=YYYY-MM-DD/city.json
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    folder = f"data/raw/dt={today}"
    os.makedirs(folder, exist_ok=True)

    path = f"{folder}/{city.replace(' ', '_')}.json"
    with open(path, "w") as f:
        json.dump(data, f)
    logging.info(f"Saved {path}")

if __name__ == "__main__":
    for city in CITIES:
        data = extract_city(city)
        if data:
            save_raw(data, city)