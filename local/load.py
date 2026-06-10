import os
import json
import psycopg2
from glob import glob
from datetime import datetime
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

def get_db_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )

def create_tables():
    """DDL: Data Definition Language. Run once to create schema.
    Concept: Schema-on-Write = DB needs structure before data
    """
    ddl = """
    CREATE TABLE IF NOT EXISTS raw_weather (
        id SERIAL PRIMARY KEY,
        city VARCHAR(100),
        country VARCHAR(10),
        temp_c NUMERIC(5,2),
        humidity INT,
        weather_main VARCHAR(50),
        ts_utc TIMESTAMP,
        ingested_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(city, ts_utc) -- Prevents duplicate rows
    );
    """
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
    logging.info("Tables created")

def load_file(filepath: str):
    with open(filepath) as f:
        data = json.load(f)

    row = {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temp_c": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather_main": data["weather"][0]["main"],
        "ts_utc": datetime.utcfromtimestamp(data["dt"])
    }

    # Concept: UPSERT = Insert or Update if exists. Makes pipeline idempotent
    sql = """
    INSERT INTO raw_weather (city, country, temp_c, humidity, weather_main, ts_utc)
    VALUES (%(city)s, %(country)s, %(temp_c)s, %(humidity)s, %(weather_main)s, %(ts_utc)s)
    ON CONFLICT (city, ts_utc) DO UPDATE SET
        temp_c = EXCLUDED.temp_c,
        humidity = EXCLUDED.humidity,
        ingested_at = NOW();
    """
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, row)
    logging.info(f"Loaded {row['city']}")

if __name__ == "__main__":
    create_tables()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    for file in glob(f"data/raw/dt={today}/*.json"):
        load_file(file)