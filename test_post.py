# Create a temporary file named test_post.py and run it
import requests

url = 'http://127.0.0.1:5000/api/nodes'
payload = {
    "node_id": "SN-LTA-001",
    "zone_id": 1,  # Must match the ID from pgAdmin
    "sensor_type": "Traffic Camera",
    "latitude": 1.3329,
    "longitude": 103.7436,
    "installed_date": "2026-11-07"
}

response = requests.post(url, json=payload)
print(response.json())