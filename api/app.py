from flask import Flask, jsonify, session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api
from mongoengine import connect, disconnect, get_db
from api.controllers import *  # Import controllers
from api.models import User, Course, Announcement, Week, Module, TestCase, Question, CodeSubmission, ChatHistory  # Import models
from dotenv import load_dotenv
import os
from api.seed_db import seed_database

load_dotenv()
# Initialize Flask app
app = Flask(__name__)

# Enable CORS for specified origins
CORS(app, supports_credentials=True, origins=["https://deepseek-fe.vercel.app", "http://localhost:3000", "*"])

# Configuration
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Ensure this is secure
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "your_default_secret_key")  # Set a secret key for session management

# Initialize extensions
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)

# Disconnect and attempt DB connection
disconnect()
db_status = False

try:
    # Connect to MongoDB
    connect(db="backend", host=os.getenv("MONGO_URI"), alias="default")
    print("DB Connected")  # Print message when connected successfully
    db_status = True
except Exception as e:
    print(f"DB Connection Failed: {e}")  # Print error message if connection fails

# Route to check DB status
@app.route('/db_status', methods=['GET'])
def check_db_status():
    return jsonify({"status": db_status}), 200

@app.route('/')
def home():
    return "Welcome to the Flask API!"

# Register API resources
api.add_resource(Login, '/login')
# api.add_resource(Study, '/study')
api.add_resource(CourseAPI, '/courses', '/course/<course_id>')
api.add_resource(RegisteredCourses, '/registered-courses')
api.add_resource(UsersAPI, '/users', '/user/<user_id>')

# YouTube Transcript API Route
api.add_resource(YouTubeTranscriptAPI, '/transcript')

# Chatbot Interaction Route
api.add_resource(ChatbotInteractionAPI, '/ask-chatbot')

# User Statistics Route
api.add_resource(UserStatisticsAPI, '/stats/<userId>')

# Run Code Route for Testing
api.add_resource(RunCodeAPI, '/run-code')

# Admin Statistics Route
api.add_resource(AdminStatisticsAPI, '/admin-statistics')

# Register Flask routes
app.register_blueprint(course_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    # seed_database()
    app.run(debug=True)
