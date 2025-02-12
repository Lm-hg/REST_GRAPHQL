import requests

city = "Paris"
url = f"https://wttr.in/{city}?format=%C+%t"  
response = requests.get(url)
print(response.text)  #
