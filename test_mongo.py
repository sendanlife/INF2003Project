import requests

url = 'http://127.0.0.1:5000/api/telemetry/weather'
payload = {
    "node_id": "SN-LTA-001",
    "location": {"type": "Point", "coordinates": [103.7436, 1.3329]},
    "metrics": {
        "temperature_c": 32.1,
        "humidity_percent": 75,
        "pm25_concentration": 14.2
    }
}

response = requests.post(url, json=payload)
print(response.json())