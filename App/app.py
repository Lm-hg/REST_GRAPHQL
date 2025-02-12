from flask import Flask, request, render_template, jsonify, make_response, flash, redirect,url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from bd import db, meteoCity
import requests
from bson import ObjectId
app = Flask(__name__)
app.secret_key = 'ma key'
app.config['JWT_SECRET_KEY'] = 'data'
app.config["JWT_TOKEN_LOCATION"] = ["cookies"] 
jwt = JWTManager(app)

utilisateur = db["users"]
favorite_cities = db["favoriteCity"]

@app.route('/')
def index():

  weather_data = meteoCity()

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
      utilisateur.insert_one(user)
      return 'Inscription reussi'
    else:
        return "Les mots de passe ne sont pas identiques"

@app.route('/login', methods = ['POST'])
def login():


    weather_data = meteoCity()
    email = request.form['email']
    password = request.form['password']

    exist_user =  utilisateur.find_one({"email": email})
    if exist_user and check_password_hash(exist_user["password"], password):
      access_token = create_access_token(identity=email)
      response = make_response(render_template('index.html', weather_data=weather_data))
      response.set_cookie('access_token_cookie', access_token) #expire dans une heure , max_age=3600
      return response
    else:
      return jsonify({"message": "Mot de passe ou email incorrect"}), 401
    

@app.route('/search', methods=['GET'])
def search():
    exist = False
    villes = []
    query = request.args.get('city')
    cities = ["Paris", "Juvisy-sur-orge", "New York", "Tokyo", "Berlin", "Lyon", "Marseille"]
    for city in cities:
        if city == query:
          exist = True
          url = f"https://wttr.in/{city}?format=%C+%t&lang=fr"
          response = requests.get(url)
          villes.append({"city": city, "weather": response.text})
          break

    if exist:
      return render_template('index.html', weather_data=villes)
    else:
        return " Ville non trouvée ou mal écrite"

@app.route('/protected', methods=['GET'])
@jwt_required()  # Vérifie automatiquement le token JWT
def protected():
    user = get_jwt_identity()
    return jsonify({"message": f"Bienvenue {user}!"}), 200


#on ajoute une nouvelle ville dans les favoris
@app.route('/addFavorite', methods=['GET'])
@jwt_required(locations=["cookies"])  
def add_city():
    mesVilles = meteoCity()
    ville = request.args.get('city')

    if not ville:
        flash("Aucune ville spécifiée.", "error")
        return redirect(url_for('index'))

    user_email = get_jwt_identity()
    if not user_email:
        flash("Vous devez être connecté pour ajouter une ville aux favoris.", "error")
        return redirect(url_for('connexion'))  # Redirige vers la connexion

    user = utilisateur.find_one({"email": user_email})
    if not user:
        flash("Utilisateur introuvable.", "error")
        return redirect(url_for('connexion'))

    user_id = user["_id"]

    # Vérifier si la ville est déjà ajoutée par cet utilisateur
    if favorite_cities.find_one({"id_user": ObjectId(user_id), "ville": ville}):
        flash("Cette ville est déjà dans vos favoris.", "info")
        return redirect(url_for('index'))

    # Ajouter la ville aux favoris
    favorite_cities.insert_one({"id_user": ObjectId(user_id), "ville": ville})
    flash("Ville ajoutée aux favoris avec succès.", "success")

    return render_template("index.html", weather_data=mesVilles)


#l'utilisateur connecté accède à son espace personnel où il retrouvera ses villes favorites
@app.route('/favorite')
@jwt_required()  
def favorite():
  villes_data = []
  user_email = get_jwt_identity()
  user = utilisateur.find_one({"email":user_email})
  id = user["_id"]
  villesFavorites = favorite_cities.find({"id_user":ObjectId(id)})
  for city in villesFavorites:
     villes_data.append(city['ville'])
  weather_data = []
  for city in villes_data:
    url = f"https://wttr.in/{city}?format=%C+%t&lang=fr"
    response = requests.get(url)
    weather_data.append({"city": city, "weather": response.text})

  return render_template('favorites.html', weather_data=weather_data, connected_user = user_email)

@jwt.unauthorized_loader
def custom_unauthorized_response(err):
    flash("Vous devez être connecté pour accéder à cette page.", "error")
    return redirect(url_for('connexion'))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


# from flask import Flask
# from flask_graphql import GraphQLView
# from graph import schema

# # Création de l'application Flask
# app = Flask(__name__)

# app.add_url_rule("/graphql", view_func=GraphQLView.as_view(
#    "graphql",
#    schema=schema,
#    graphiql=True  # Interface GraphiQL activée
# ))

# if __name__ == "__main__":
#    app.run(debug=True)