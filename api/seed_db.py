from api.models import User, Course, Announcement, Week, Module, TestCase, Question  # Import models
from datetime import datetime


def seed_database():
    from api.app import app, bcrypt
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
