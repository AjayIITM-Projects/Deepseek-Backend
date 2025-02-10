from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api
from api.models import db, User, Course, Announcement, Week, Module, TestCase, Question, UserCourse
from api.controllers import * # Import the controllers
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)  # Initialize bcrypt here to avoid undefined error
jwt = JWTManager(app)
api = Api(app)

# Register API resources
api.add_resource(Login, '/login')
api.add_resource(Study, '/study')
api.add_resource(CourseAPI, '/course')

# Register Flask routes
app.register_blueprint(course_bp)

# Function to drop tables, recreate them, and seed dummy data
def reset_and_seed_database():
    with app.app_context():
        print("Resetting database...")
        db.drop_all()  # Delete all tables
        db.create_all()  # Recreate tables
        print("Database reset completed.")

        print("Seeding database with dummy data...")

        # Create a sample user
        hashed_password = bcrypt.generate_password_hash("password123").decode('utf-8')
        user1 = User(username="admin", password=hashed_password, role="admin", email="admin@example.com", name="Admin User")
        db.session.add(user1)

        # Create a sample course
        course1 = Course(
            CourseID=1,
            CourseName="Introduction to Flask",
            CourseDescription="Learn Flask from scratch.",
            StartDate=datetime.strptime("2025-02-01", "%Y-%m-%d"),  
            EndDate=datetime.strptime("2025-06-01", "%Y-%m-%d")
        )
        db.session.add(course1)
        db.session.commit()

        # Create an announcement
        announcement = Announcement(course_id=course1.CourseID, message="Welcome to the course!")
        db.session.add(announcement)

        # Create a week
        week1_deadline = datetime.strptime("2025-02-10", "%Y-%m-%d").date()
        week1 = Week(course_id=course1.CourseID, title="Week 1: Getting Started", deadline=week1_deadline)
        db.session.add(week1)
        db.session.commit()

        # Create modules with different types
        module_video = Module(
            week_id=week1.id,
            title="Introduction to Flask - Video",
            type="video",
            url="https://example.com/flask-intro-video"
        )

        module_coding = Module(
            week_id=week1.id,
            title="Flask Coding Challenge",
            type="coding",
            language="Python",
            description="Write a simple Flask app that returns 'Hello, Flask!'",
            code_template="from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef home():\n    return 'Hello, Flask!'"
        )

        module_assignment = Module(
            week_id=week1.id,
            title="Flask Basics - Assignment",
            type="assignment",
            graded=True
        )

        module_document = Module(
            week_id=week1.id,
            title="Flask Documentation",
            type="document",
            doc_type="PDF",
            doc_url="https://example.com/flask-docs.pdf"
        )

        db.session.add_all([module_video, module_coding, module_assignment, module_document])
        db.session.commit()

        print("Database seeded successfully!")


# Run the Flask app
if __name__ == '__main__':
    reset_and_seed_database()  # Reset and populate DB every time the app runs
    # app.run(debug=True)
