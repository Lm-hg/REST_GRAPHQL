from flask import Flask, request, render_template, jsonify, make_response, flash, redirect,url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from bd import db, meteoCity
import requests
import os
from bson import ObjectId
app = Flask(__name__)
app.secret_key = 'ma key'
app.config['JWT_SECRET_KEY'] = 'data'
app.config["JWT_TOKEN_LOCATION"] = ["cookies"] 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=3600)
jwt = JWTManager(app)
 #collection contenant les utilisateurs
utilisateur = db["users"]
#collection contenant les villes mises dans les favoris des utilisateurs
favorite_cities = db["favoriteCity"]

# l'accueil
@app.route('/')
def index():
  token = request.cookies.get("access_token_cookie")
  weather_data = meteoCity()

  return render_template('index.html', weather_data=weather_data, token=token)

#l'inscription, pour ajouter un nouvel utilisateur dans utilisateur (part1/ le formulaire)
@app.route('/inscription')
def inscription():
   return render_template('signup.html')

#connexion pour accéder à sa page personne (part1/ le formulaire)
@app.route('/connexion')
def connexion():
   return render_template('signin.html')

#inscription (part2/récupération des données du formulaire et stockage dans la base de données)
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
      return redirect(url_for('connexion'))
    else:
        return "Les mots de passe ne sont pas identiques"
    
#connexion (part2/ on récupère les données de l'utilisateur ensuite on vérifie s'il est dans la base de données ensuite on crée un token et on le stocke dans les cookies)
@app.route('/login', methods = ['POST'])
def login():


    email = request.form['email']
    password = request.form['password']

    exist_user =  utilisateur.find_one({"email": email})
    if exist_user and check_password_hash(exist_user["password"], password):
      access_token = create_access_token(identity=email, expires_delta=timedelta(seconds=3600))
      response = make_response(redirect(url_for('index')))
      response.set_cookie('access_token_cookie', access_token, max_age=3600) #expire dans une heure , 
      return response
    else:
      return jsonify({"message": "Mot de passe ou email incorrect"}), 401
    
#on recherche une ville 
@app.route('/search', methods=['GET'])
def search():
    token = request.cookies.get("access_token_cookie")
    exist = False
    villes = []
    query = request.args.get('city')
    cities = ["Paris", "New York", "Tokyo", "Berlin", "Lyon", "Marseille", "Montreuil", "Maronne", "Madrid", "Rome",
          "Sydney", "Vancouver", "Los Angeles", "Amsterdam", "Londres", "Bruxelles", "Toronto", "Barcelone", "Milan", "Prague"]
    for city in cities:
        if city.lower() == query.lower():
          exist = True
          url = f"https://wttr.in/{city}?format=%C+%t&lang=fr"
          response = requests.get(url)
          villes.append({"city": city, "weather": response.text})
          break

    if exist:
      return render_template('index.html', weather_data=villes, token=token)
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

    return redirect(url_for('index'))

@jwt.unauthorized_loader
def custom_unauthorized_response(err):
    flash("Vous devez être connecté pour accéder à cette page.", "error")
    return redirect(url_for('connexion'))

#l'utilisateur connecté accède à son espace personnel où il retrouvera ses villes favorites
@app.route('/favorite')
@jwt_required(locations=["cookies"])  
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

#redirection vers la page de connexion si le token a expire ou n'existe pas si on essaye d'accéder à une page sécurisée

# Gestion globale des tokens expirés
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    flash("Votre session a expiré. Veuillez vous reconnecter.", "error")
    return redirect(url_for('connexion'))

# Gestion des tokens invalides
@jwt.invalid_token_loader
def invalid_token_callback(reason):
    flash("Token invalide. Veuillez vous reconnecter.", "error")
    return redirect(url_for('connexion'))

# Gestion des accès sans token
@jwt.unauthorized_loader
def missing_token_callback(reason):
    flash("Vous devez être connecté pour accéder à cette page.", "error")
    return redirect(url_for('connexion'))

#supprimer une ville dans les favoris
@app.route('/deleteCity', methods=['GET'])
@jwt_required(locations=["cookies"])  
def delete_city():
    ville = request.args.get('city')
    weather_data = []
    if not ville:
        flash("Aucune ville spécifiée.", "error")
        return redirect(url_for('index'))

    user_email = get_jwt_identity()
    if not user_email:
        flash("Vous devez être connecté pour ajouter une ville aux favoris.", "error")
        return redirect(url_for('connexion'))  # Redirige vers la connexion

    user = utilisateur.find_one({"email": user_email})
    id = user["_id"]
    if not user:
        flash("Utilisateur introuvable.", "error")
        return redirect(url_for('connexion'))

    user_id = user["_id"]
    favorite_cities.delete_one({"id_user": ObjectId(user_id), "ville": ville})

    mesVilles = favorite_cities.find({"id_user":ObjectId(id)})
    for i in mesVilles:
      url = f"https://wttr.in/{i['ville']}?format=%C+%t&lang=fr"
      response = requests.get(url)
      weather_data.append({"city": i["ville"], "weather": response.text})

     # Supprimer la ville des favoris
    flash("Ville supprimée avec succès.", "success")

    return redirect(url_for('favorite'))




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
