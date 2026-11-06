import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from sqlalchemy import text

# 1. Load environment variables from the .env file
load_dotenv()

# 2. Initialize Flask and enable CORS for React Native
app = Flask(__name__)
CORS(app)

# 3. PostgreSQL Setup (Local)
postgres_password = os.getenv('POSTGRES_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{postgres_password}@localhost:5432/project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 4. MongoDB Setup (Cloud)
mongo_uri = os.getenv('MONGO_URI')
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client['smart_city_hub']
weather_collection = mongo_db['weather_telemetry']
traffic_collection = mongo_db['traffic_snapshots']

# --- API ENDPOINTS ---

@app.route('/', methods=['GET'])
def home():
    return "Smart City Environmental Monitoring Hub API is running."

@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        db.session.execute(text('SELECT 1'))
        sql_status = "Connected to local PostgreSQL"
    except Exception as e:
        sql_status = f"Failed: {str(e)}"

    try:
        mongo_client.admin.command('ping')
        nosql_status = "Connected to MongoDB Atlas"
    except Exception as e:
        nosql_status = f"Failed: {str(e)}"

    return jsonify({"postgresql_admin_db": sql_status, "mongodb_telemetry_db": nosql_status})

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    try:
        result = db.session.execute(text('SELECT * FROM sensor_nodes')).mappings().all()
        nodes = [dict(row) for row in result]
        return jsonify(nodes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/nodes', methods=['POST'])
def add_node():
    data = request.json
    new_node = text("""
        INSERT INTO sensor_nodes (node_id, zone_id, sensor_type, latitude, longitude, installed_date) 
        VALUES (:node_id, :zone_id, :sensor_type, :lat, :lon, :date)
    """)
    try:
        db.session.execute(new_node, {
            'node_id': data['node_id'], 
            'zone_id': data['zone_id'], 
            'sensor_type': data['sensor_type'], 
            'lat': data['latitude'], 
            'lon': data['longitude'], 
            'date': data['installed_date']
        })
        db.session.commit()
        return jsonify({"message": f"Node {data['node_id']} added to PostgreSQL successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/api/telemetry/weather', methods=['POST'])
def add_weather_data():
    data = request.json
    data['timestamp'] = datetime.utcnow().isoformat() + "Z"
    try:
        weather_collection.insert_one(data)
        return jsonify({"message": f"Weather data for {data.get('node_id')} recorded in MongoDB Atlas"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/telemetry/weather', methods=['GET'])
def get_weather_data():
    try:
        results = list(weather_collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(50))
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)