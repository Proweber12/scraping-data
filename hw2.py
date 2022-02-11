import requests
import json

access_token = "b76f62204439f5ff4e50294ed223a0cc7a27a1b52321772d8cdd817239d50e304a197c7856ade888d8a63"

url = f"https://api.vk.com/method/friends.getOnline?v=5.131&access_token={access_token}"

response = requests.get(url).json()

with open('vk.json', 'w', encoding='utf-8') as f:
    json.dump(response, f, indent=3)