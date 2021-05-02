"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from api.models import db, User, Bird_Capture, Audio_Favorite
from api.routes import api
from api.admin import setup_admin
from api.service import Service
#from models import Person

# JWT EXTENDED
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

# database condiguration
if os.getenv("DATABASE_URL") is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = os.environ.get('JW_TOKEN')  # File safe on .env file in the root.
jwt = JWTManager(app)

MIGRATE = Migrate(app, db)
db.init_app(app)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# ------------------------------------------ Users Endpoints ------------------------------------------

# Endpoint for validating parameters and decide if return token.
@app.route("/login", methods=["POST"])
def create_token():
    email = request.json.get("email")
    password = request.json.get("password")
    # Query your User table with username and password
    user = User.query.filter_by(email=email, password=password).first()
    if user is None:
        # The user was not found on the database
        return jsonify({"msg": "Bad email or password"}), 401
    
    # create a new token with the user id inside
    access_token = create_access_token(identity=user.id)

    response_body = {
        "access_token": access_token,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "bio": user.bio
    }

    return jsonify(response_body)

# Endpoint for registering a new user.
@app.route('/register', methods=['POST'])
def add_user():
    # Take the data passed from the front request an turn it into JSON
    request_body = request.get_json()

    # ----- USER ON DATABASE VALIDATION -----
    # Get the parameter to validate
    email = request_body["email"]

    # Validating that email doesn't already exist on database
    user = User.query.filter_by(email=email).first()

    # If user doesn't exist on database then create a new instance
    if user is None:

        # Build a new instance of User, passing the parameters from the request.body
        user = User(first_name=request_body["first_name"], last_name=request_body["last_name"], email=request_body["email"], password=request_body["password"], bio=request_body["bio"])

        # Append the the instance into the database session of the API
        db.session.add(user)
        db.session.commit()

        # Return a response with sucessful status
        response_body = {
            "msg": "POST /register response. Registration succesfully done."
        }

        return jsonify(response_body), 200


    # Return a client error response and a comment indicating duplication of email is imposible.
    return jsonify({"msg": "POST /register response. Email already exist on database."}), 401

    
# Endpoint for returning all users.
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():

    # Get a list with all the users serialized.
    users = User.getAll()

    # Return the list of registered users.
    return jsonify(users), 200

# Endpoint for returning data for an specific user.
@app.route('/user/<int:id>', methods=['GET'])
@jwt_required()
def get_single_user(id):
    user = User.query.get(id)

    if user is None:
        raise APIException('User not found', status_code=404)

    return jsonify(user.serialize()), 200

# ------------------------------------------ Bird Captures Endpoints ------------------------------------------

# Endpoint for returning all the captures from all the users.
@app.route('/bird_captures/public', methods=['GET'])
@jwt_required()
def get_public_captures():

    response_body = {
        "msg": "Hello, this is your GET /captures response "
    }

    # Access the identity of the current user with get_jwt_identity
    public_captures = Service.get_public_captures()
    return jsonify(public_captures), 200

# Endpoint for returning all the captures in the private journal for every user.
@app.route('/bird_captures', methods=['GET'])
@jwt_required()
def get_user_captures():
    
    response_body = {
        "msg": "Hello, this is your GET /captures response "
    }

    # Access the identity of the current user with get_jwt_identity
    current_user_id = get_jwt_identity()
    user_captures = Service.get_user_captures(current_user_id)
    return jsonify(user_captures), 200

# Endpoint for adding a bird capture to the private journal
@app.route('/bird_captures', methods=['POST'])
@jwt_required()
def add_capture():

    # current_user_id = get_jwt_identity()
    request_body = request.get_json()
    bird_capture = Bird_Capture(en=request_body["en"], cnt=request_body["cnt"], loc=request_body["loc"], time=request_body["time"], rmk=request_body["rmk"], privacy=request_body["privacy"], user_id=request_body["user_id"])

    # Append the the instance into the database session of the API
    db.session.add(bird_capture)
    db.session.commit()

    # Return a response with sucessful status
    response_body = {
        "msg": "POST /bird_captures response. Bird capture added succesfully."
    }

    return jsonify(response_body), 200

# ------------------------------------------ Favorites Endpoints ------------------------------------------

# Endpoint for getting all the favorites of the current user.
@app.route('/favorites', methods=['GET'])
@jwt_required()
def get_audio_favorites():
    
    # Access the identity of the current user with get_jwt_identity
    current_user_id = get_jwt_identity()
    all_favorites = Service.get_favorites(current_user_id)
    return jsonify(all_favorites), 200

# Endpoint for adding a favorite to the current user personal list.
@app.route('/favorites', methods=['POST'])
@jwt_required()
def add_audio_favorite():

    request_body = request.get_json()
    # define an instance of Favorite
    audio_favorite = Audio_Favorite(en=request_body["en"], cnt=request_body["cnt"], loc=request_body["loc"], time=request_body["time"], url_sound=request_body["url_sound"], user_id=request_body["user_id"])
    # save it on the database table for Favorites
    db.session.add(audio_favorite)
    db.session.commit()
    
    return jsonify(request_body), 200

@app.route('/favorites/<int:position>', methods=['DELETE'])
@jwt_required()
def delete_favorite(position):
    audio_favorite = Audio_Favorite.query.filter_by(id=position).first()
    # favorite = Favorite.query.get(position)

    if audio_favorite is None:
        raise APIException('Favorite not found', status_code=404)

    db.session.delete(audio_favorite)
    db.session.commit()
    response_body = {
         "msg": "Favorite deleted successful",
    }
    return jsonify(response_body), 200

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
