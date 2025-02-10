from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -----------------------------
# User Model (Already Provided)
# -----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    profile_picture_url = db.Column(db.String(200))  # Optional

# -----------------------------
# Course Model (Already Provided)
# -----------------------------
class Course(db.Model):
    CourseID = db.Column(db.Integer, primary_key=True)
    CourseName = db.Column(db.String(120), nullable=False)
    CourseDescription = db.Column(db.String(500), nullable=False)
    StartDate = db.Column(db.DateTime, nullable=False)
    EndDate = db.Column(db.DateTime, nullable=False)

# -----------------------------
# Announcement Model
# -----------------------------
class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.CourseID'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship("Course", backref=db.backref("announcements", lazy=True))

# -----------------------------
# Week Model
# -----------------------------
class Week(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.CourseID'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)

    course = db.relationship("Course", backref=db.backref("weeks", lazy=True))

# -----------------------------
# Module Model
# -----------------------------
class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # ["video", "coding", "assignment", "document"]
    
    # Video type
    url = db.Column(db.String(300))

    # Coding type
    language = db.Column(db.String(50))
    description = db.Column(db.String(500))
    code_template = db.Column(db.Text)

    # Assignment type
    graded = db.Column(db.Boolean, default=False)

    # Document type
    doc_type = db.Column(db.String(20))
    doc_url = db.Column(db.String(300))

    week = db.relationship("Week", backref=db.backref("modules", lazy=True))

# -----------------------------
# Test Case Model (For Coding Modules)
# -----------------------------
class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    input_data = db.Column(db.String(200), nullable=False)
    expected_output = db.Column(db.String(200), nullable=False)

    module = db.relationship("Module", backref=db.backref("test_cases", lazy=True))

# -----------------------------
# Question Model (For Assignments)
# -----------------------------
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    question_text = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # ["mcq", "msq", "nat"]
    options = db.Column(db.Text)  # Comma-separated options (for MCQ and MSQ)
    correct_answer = db.Column(db.String(200), nullable=False)

    module = db.relationship("Module", backref=db.backref("questions", lazy=True))


# -----------------------------
# UserCourse Model (Junction Table for Many-to-Many Relationship)
# -----------------------------
class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.CourseID'), nullable=False)

    user = db.relationship("User", backref=db.backref("registered_courses", lazy=True))
    course = db.relationship("Course", backref=db.backref("registered_users", lazy=True))

