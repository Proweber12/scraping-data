import requests
import json

username = "Proweber12"

url = f"https://api.github.com/users/{username}/repos"

response = requests.get(url).json()

with open('repos.json', 'w', encoding='utf-8') as f:
    json.dump(response, f, indent=3)

for i in response:
    print(i['name'])
