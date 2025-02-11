import requests

# Liste de plusieurs villes
cities = ["Paris", "Juvisy-sur-orge", "New York", "Tokyo", "Berlin"]

# Boucle pour récupérer la météo de chaque ville
for city in cities:
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    print(f"Météo à {city}: {response.text}")
