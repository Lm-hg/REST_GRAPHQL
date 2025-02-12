from pymongo import MongoClient
import requests

server = "34.251.25.31" # or localhost
username = "ortecusdb"
password = "passdb*2019#"
port = 27017

if server == 'localhost':
    client = MongoClient("mongodb://localhost", username=username,password=password, port=port)
else:
    client = MongoClient(server, username=username,password=password, port=port)

# creation DB
db = client["Modestin_hetic_db"]

# creation collection
# db.users.insert_one({ "name": "Alice Doe", "email": "alice@example.com", "age": 30 })

data = db.users.find({})

for item in data:
    print(item)

def meteoCity():
  cities = ["Paris", "New York", "Tokyo", "Berlin", "Lyon", "Marseille"]
  weather_data = []
  for city in cities:
    url = f"https://wttr.in/{city}?format=%C+%t&lang=fr"
    response = requests.get(url)
    weather_info = response.text.split()  # Divise le texte en deux parties
    
    # On récupère la condition et la température
    condition = weather_info[0]  # ex: "sunny"
    temperature = weather_info[1]  # ex: "25°C"
    
    # On nettoie la température pour enlever le "°C"
    temp_value = temperature.replace('°C', '')  # On garde juste la valeur numérique
    
    # Ajouter les données à la liste
    weather_data.append({
        "city": city,
        "weather": condition,
        "temperature": temp_value  # On ajoute aussi la température sous forme d'entier
    })
  return weather_data

print(meteoCity())