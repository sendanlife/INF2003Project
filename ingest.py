import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from faker import Faker
from pymongo import MongoClient
from sqlalchemy import create_engine, text

# Initialize Faker and load environment variables
fake = Faker()
load_dotenv()

# --- Database Connections ---
postgres_uri = f"postgresql://postgres:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/project"
pg_engine = create_engine(postgres_uri)

mongo_client = MongoClient(os.getenv('MONGO_URI'))
mongo_db = mongo_client['smart_city_hub']
weather_col = mongo_db['weather_telemetry']
traffic_col = mongo_db['traffic_snapshots']

def seed_postgresql():
    print("Seeding PostgreSQL (Administrative Data)...")
    with pg_engine.begin() as conn:
        # 1. Clear existing data to prevent duplicates (Cascade deletes linked records)
        conn.execute(text("TRUNCATE TABLE maintenance_logs, sensor_nodes, users, zones RESTART IDENTITY CASCADE"))

        # 2. Insert Zones
        regions = ['North', 'South', 'East', 'West', 'Central']
        for i, region in enumerate(regions, start=1):
            conn.execute(text(f"INSERT INTO zones (zone_name, region) VALUES ('Zone {region}', '{region}')"))

        # 3. Insert Users (Technicians & Admins)
        roles = ['Admin', 'Technician']
        for _ in range(5):
            conn.execute(text("""
                INSERT INTO users (full_name, role, email) 
                VALUES (:name, :role, :email)
            """), {"name": fake.name(), "role": random.choice(roles), "email": fake.unique.email()})

        # 4. Insert Sensor Nodes
        sensor_types = ['Weather Station', 'Traffic Camera', 'Air Quality Monitor']
        statuses = ['Active', 'Active', 'Active', 'Maintenance', 'Offline']
        node_ids = []
        for i in range(1, 16):
            node_id = f"SN-2026-{i:03d}"
            node_ids.append(node_id)
            conn.execute(text("""
                INSERT INTO sensor_nodes (node_id, zone_id, sensor_type, latitude, longitude, status, installed_date) 
                VALUES (:node_id, :zone_id, :type, :lat, :lon, :status, :date)
            """), {
                "node_id": node_id, "zone_id": random.randint(1, 5),
                "type": random.choice(sensor_types), 
                "lat": round(random.uniform(1.2, 1.4), 6), "lon": round(random.uniform(103.6, 104.0), 6),
                "status": random.choice(statuses), "date": fake.date_between(start_date='-2y', end_date='today')
            })

        # 5. Insert Maintenance Logs
        for _ in range(10):
            conn.execute(text("""
                INSERT INTO maintenance_logs (node_id, user_id, action_taken, log_date) 
                VALUES (:node_id, :user_id, :action, :date)
            """), {
                "node_id": random.choice(node_ids), "user_id": random.randint(1, 5),
                "action": fake.sentence(nb_words=6),
                "date": fake.date_time_between(start_date='-1m', end_date='now')
            })
    return node_ids

def seed_mongodb(node_ids):
    print("Seeding MongoDB Atlas (Telemetry Data)...")
    weather_col.delete_many({})
    traffic_col.delete_many({})

    weather_payloads = []
    traffic_payloads = []

    # Generate 50 historical telemetry readings for the sensors
    for _ in range(50):
        timestamp = (datetime.utcnow() - timedelta(minutes=random.randint(1, 1000))).isoformat() + "Z"
        
        weather_payloads.append({
            "node_id": random.choice(node_ids),
            "timestamp": timestamp,
            "metrics": {
                "temperature_c": round(random.uniform(26.0, 34.0), 1),
                "humidity_percent": random.randint(60, 95),
                "pm25_concentration": round(random.uniform(10.0, 55.0), 1)
            }
        })
        
        traffic_payloads.append({
            "node_id": random.choice(node_ids),
            "timestamp": timestamp,
            "metrics": {
                "vehicle_count": random.randint(10, 200),
                "average_speed_kmh": round(random.uniform(20.0, 90.0), 1),
                "congestion_level": random.choice(["Low", "Moderate", "Heavy"])
            }
        })

    weather_col.insert_many(weather_payloads)
    traffic_col.insert_many(traffic_payloads)

if __name__ == "__main__":
    generated_nodes = seed_postgresql()
    seed_mongodb(generated_nodes)
    print("Bulk ingestion complete. Databases are fully populated.")