from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api
from mongoengine import connect, disconnect
from datetime import datetime
from api.controllers import *  # Import controllers
from api.models import User, Course, Announcement, Week, Module, TestCase, Question  # Import models
from dotenv import load_dotenv
import os

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
# Connect to MongoDB
connect(db="backend", host=os.getenv("MONGO_URI"), alias="default")


# Register API resources
api.add_resource(Login, '/login')
api.add_resource(Study, '/study')
api.add_resource(CourseAPI, '/course')

# Register Flask routes
app.register_blueprint(course_bp)

# Function to seed dummy data
def seed_database():
    with app.app_context():
        print("Seeding database with dummy data...")

        # Clear existing data
        User.objects.delete()
        Course.objects.delete()
        Announcement.objects.delete()
        Week.objects.delete()
        Module.objects.delete()

        # Create a sample user
        hashed_password = bcrypt.generate_password_hash("password123").decode('utf-8')
        user1 = User(
            username="admin",
            password=hashed_password,
            role="admin",
            email="admin@example.com",
            name="Admin User"
        )
        user1.save()

        # Create a sample course
        course1 = Course(
            CourseName="Introduction to Flask",
            CourseDescription="Learn Flask from scratch.",
            StartDate=datetime(2025, 2, 1),
            EndDate=datetime(2025, 6, 1)
        )
        course1.save()

        # Create an announcement
        announcement = Announcement(course=course1, message="Welcome to the course!")
        announcement.save()

        # Create a week
        week1 = Week(course=course1, title="Week 1: Getting Started", deadline=datetime(2025, 2, 10))
        week1.save()

        # Create modules
        module1 = Module(
            week=week1,
            title="Introduction to Flask - Video",
            type="video",
            url="https://example.com/flask-intro-video"
        ).save()

        module2 = Module(
            week=week1,
            title="Flask Coding Challenge",
            type="coding",
            language="Python",
            description="Write a simple Flask app.",
            code_template="from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef home():\n    return 'Hello, Flask!'",
            test_cases=[
                TestCase(input_data="GET /", expected_output="Hello, Flask!")
            ]
        ).save()

        module3 = Module(
            week=week1,
            title="Flask Basics - Assignment",
            type="assignment",
            graded=True,
            questions=[
                Question(
                    question_text="What is Flask?",
                    type="mcq",
                    options=["A web framework", "A database", "A programming language"],
                    correct_answer="A web framework"
                )
            ]
        ).save()

        module4 = Module(
            week=week1,
            title="Flask Documentation",
            type="document",
            doc_type="PDF",
            doc_url="https://example.com/flask-docs.pdf"
        ).save()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
    # app.run(debug=True)
