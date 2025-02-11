from flask import Flask, request, render_template, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from flask_pymongo import PyMongo
import requests
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'data'
jwt = JWTManager(app)
app.secret_key = 'any random string'
app.config["MONGO_URI"] = "mongodb://localhost:27017/MyMeteo" 
mongo = PyMongo(app)

cities = ["Paris", "Juvisy-sur-orge", "New York", "Tokyo", "Berlin", "Lyon"]

@app.route('/')
def index():

  weather_data = []
  for city in cities:
      url = f"https://wttr.in/{city}?format=%C+%t&lang=fr"
      response = requests.get(url)
      weather_data.append({"city": city, "weather": response.text})
  return render_template('index.html', weather_data=weather_data)
@app.route('/inscription')
def inscription():
   return render_template('signup.html')
@app.route('/connexion')
def connexion():
   return render_template('signin.html')
@app.route('/register', methods = ['POST'])
def register():
    
    nom = request.form['name']
    email = request.form['email']
    password = request.form["password"]
    Cpassword = request.form['Cpassword']
    hashed_password = generate_password_hash(password)
    if Cpassword == password:
      user = {
      "nom": nom,
      "email": email,
      "password": hashed_password
      }
      mongo.db.users.insert_one(user)
      return 'Inscription reussi'
    else:
        return "Les mots de passe ne sont pas identiques"

@app.route('/login', methods = ['POST'])
def login():

    weather_data = []
    for city in cities:
        url = f"https://wttr.in/{city}?format=%C+%t&lang=fr"
        response = requests.get(url)
        weather_data.append({"city": city, "weather": response.text})

    email = request.form['email']
    password = request.form['password']

    exist_user =  mongo.db.users.find_one({"email": email})
    if exist_user and check_password_hash(exist_user["password"], password):
      access_token = create_access_token(identity=email)
      response = make_response(render_template('index.html', weather_data=weather_data))
      response.set_cookie('access_token', access_token, httponly=True, secure=True)
      return response
    else:
      return jsonify({"message": "Mot de passe ou email incorrect"}), 401
    

@app.route('/search', methods=['GET'])
def search():
#ici, on développera comment faire une recherche
  return 'hello'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)