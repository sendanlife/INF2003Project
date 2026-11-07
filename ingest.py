import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from faker import Faker
from pymongo import MongoClient
from sqlalchemy import create_engine, text

# 1. Initialize Faker (to generate realistic dummy data like names and emails) 
# and load our secure environment variables so passwords stay hidden.
fake = Faker()
load_dotenv()

# ==========================================
# --- Database Connections ---
# ==========================================

# 2. Connect to the local PostgreSQL database using SQLAlchemy.
# This engine will handle our structured SQL commands.
postgres_uri = f"postgresql://postgres:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/project"
pg_engine = create_engine(postgres_uri)

# 3. Connect to the cloud MongoDB Atlas database.
# This connects directly to our NoSQL document collections.
mongo_client = MongoClient(os.getenv('MONGO_URI'))
mongo_db = mongo_client['smart_city_hub']
weather_col = mongo_db['weather_telemetry']
traffic_col = mongo_db['traffic_snapshots']

def seed_postgresql():
    print("Seeding PostgreSQL (Administrative Data)...")
    with pg_engine.begin() as conn:
        # 4. Clear existing data so we don't get duplicates if we run this twice. 
        # 'CASCADE' ensures we delete linked foreign key records automatically 
        # so we don't hit strict SQL constraint errors.
        conn.execute(text("TRUNCATE TABLE maintenance_logs, sensor_nodes, users, zones RESTART IDENTITY CASCADE"))

        # 5. Insert Dummy Zones (The physical areas our sensors live in)
        regions = ['North', 'South', 'East', 'West', 'Central']
        for i, region in enumerate(regions, start=1):
            conn.execute(text(f"INSERT INTO zones (zone_name, region) VALUES ('Zone {region}', '{region}')"))

        # 6. Insert Dummy Users (Using Faker for realistic names and emails)
        roles = ['Admin', 'Technician']
        for _ in range(5):
            conn.execute(text("""
                INSERT INTO users (full_name, role, email) 
                VALUES (:name, :role, :email)
            """), {"name": fake.name(), "role": random.choice(roles), "email": fake.unique.email()})

        # 7. Insert Dummy Sensor Nodes (The actual IoT hardware)
        sensor_types = ['Weather Station', 'Traffic Camera', 'Air Quality Monitor']
        statuses = ['Active', 'Active', 'Active', 'Maintenance', 'Offline']
        node_ids = []
        for i in range(1, 16):
            node_id = f"SN-2026-{i:03d}"
            node_ids.append(node_id) # Save the ID so we can link it to the NoSQL data later!
            
            # Using parameterized queries (:node_id, :lat, etc.) for safe SQL insertion
            conn.execute(text("""
                INSERT INTO sensor_nodes (node_id, zone_id, sensor_type, latitude, longitude, status, installed_date) 
                VALUES (:node_id, :zone_id, :type, :lat, :lon, :status, :date)
            """), {
                "node_id": node_id, "zone_id": random.randint(1, 5),
                "type": random.choice(sensor_types), 
                "lat": round(random.uniform(1.2, 1.4), 6), "lon": round(random.uniform(103.6, 104.0), 6),
                "status": random.choice(statuses), "date": fake.date_between(start_date='-2y', end_date='today')
            })

        # 8. Insert Dummy Maintenance Logs (Linked directly to the sensor nodes and technicians)
        for _ in range(10):
            conn.execute(text("""
                INSERT INTO maintenance_logs (node_id, user_id, action_taken, log_date) 
                VALUES (:node_id, :user_id, :action, :date)
            """), {
                "node_id": random.choice(node_ids), "user_id": random.randint(1, 5),
                "action": fake.sentence(nb_words=6), # Generates the random dummy text we saw on the app
                "date": fake.date_time_between(start_date='-1m', end_date='now')
            })
            
    # We return the list of generated node IDs so MongoDB knows exactly which sensors exist
    return node_ids

def seed_mongodb(node_ids):
    print("Seeding MongoDB Atlas (Telemetry Data)...")
    
    # 9. Clear existing NoSQL collections
    weather_col.delete_many({})
    traffic_col.delete_many({})

    weather_payloads = []
    traffic_payloads = []

    # 10. Generate 50 historical telemetry readings for the sensors
    for _ in range(50):
        # Create a randomized timestamp from the past 1000 minutes
        timestamp = (datetime.utcnow() - timedelta(minutes=random.randint(1, 1000))).isoformat() + "Z"
        
        # 11. Build the flexible NoSQL Document Schema for Weather
        weather_payloads.append({
            "node_id": random.choice(node_ids), # Links perfectly to a node created in PostgreSQL
            "timestamp": timestamp,
            "metrics": {
                "temperature_c": round(random.uniform(26.0, 34.0), 1),
                "humidity_percent": random.randint(60, 95),
                "pm25_concentration": round(random.uniform(10.0, 55.0), 1)
            }
        })
        
        # 12. Build the flexible NoSQL Document Schema for Traffic
        traffic_payloads.append({
            "node_id": random.choice(node_ids),
            "timestamp": timestamp,
            "metrics": {
                "vehicle_count": random.randint(10, 200),
                "average_speed_kmh": round(random.uniform(20.0, 90.0), 1),
                "congestion_level": random.choice(["Low", "Moderate", "Heavy"])
            }
        })

    # 13. Bulk insert the lists of JSON documents into MongoDB Atlas in one fast transaction
    weather_col.insert_many(weather_payloads)
    traffic_col.insert_many(traffic_payloads)

if __name__ == "__main__":
    # First, generate the strict SQL data and get the list of created hardware IDs
    generated_nodes = seed_postgresql()
    # Second, pass those IDs to MongoDB so the NoSQL telemetry matches the hardware exactly
    seed_mongodb(generated_nodes)
    print("Bulk ingestion complete. Databases are fully populated.")