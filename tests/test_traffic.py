import requests

url = 'http://127.0.0.1:5000/api/telemetry/traffic'
payload = {
    "node_id": "SN-LTA-001",
    "metrics": {
        "vehicle_count": 145,
        "average_speed_kmh": 62.5,
        "congestion_level": "Moderate"
    }
}

response = requests.post(url, json=payload)
print(response.json())