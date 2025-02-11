from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api
from mongoengine import connect, disconnect, get_db
from datetime import datetime
from api.controllers import *  # Import controllers
from api.models import User, Course, Announcement, Week, Module, TestCase, Question, Test  # Import models
from dotenv import load_dotenv
import os
from api.seed_db import seed_database

load_dotenv()
# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

# Initialize extensions
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)

disconnect()

try:
    # Connect to MongoDB
    connect(db="backend", host=os.getenv("MONGO_URI"), alias="default")
    print("DB Connected")  # Print message when connected successfully
except Exception as e:
    print(f"DB Connection Failed: {e}")  # Print error message if connection fails

# Route to check DB status
@app.route('/db_status', methods=['GET'])
def check_db_status():
    try:
        # Try to get database to check connection
        get_db("default")
        return jsonify({"status": "connected", "message": "Database is connected"}), 200
    except Exception as e:
        return jsonify({"status": "disconnected", "message": f"Database connection failed: {str(e)}"}), 500

@app.route('/')
def home():
    return "Welcome to the Flask API!"

# Register API resources
api.add_resource(Login, '/login')
api.add_resource(Study, '/study')
api.add_resource(CourseAPI, '/course')
api.add_resource(Test, '/test')

# Register Flask routes
app.register_blueprint(course_bp)

# if __name__ == '__main__':
# #     # seed_database()
#     app.run(debug=True)
