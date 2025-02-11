from mongoengine import Document, EmbeddedDocument, fields, connect
from datetime import datetime

# Connect to MongoDB
connect(db="your_database_name", host="mongodb://localhost:27017/your_database_name")

# -----------------------------
# User Model
# -----------------------------
class User(Document):
    username = fields.StringField(required=True, unique=True, max_length=80)
    password = fields.StringField(required=True)
    role = fields.StringField(required=True, max_length=50)
    email = fields.EmailField(required=True, unique=True)
    name = fields.StringField(required=True, max_length=120)
    profile_picture_url = fields.StringField(max_length=200)  # Optional
    registered_courses = fields.ListField(fields.ReferenceField('Course'))  # Many-to-Many

# -----------------------------
# Course Model
# -----------------------------
class Course(Document):
    CourseName = fields.StringField(required=True, max_length=120)
    CourseDescription = fields.StringField(required=True, max_length=500)
    StartDate = fields.DateTimeField(required=True)
    EndDate = fields.DateTimeField(required=True)
    registered_users = fields.ListField(fields.ReferenceField(User))  # Many-to-Many

# -----------------------------
# Announcement Model
# -----------------------------
class Announcement(Document):
    course = fields.ReferenceField(Course, required=True, reverse_delete_rule=fields.CASCADE)
    message = fields.StringField(required=True, max_length=500)
    date = fields.DateTimeField(default=datetime.utcnow)

# -----------------------------
# Week Model
# -----------------------------
class Week(Document):
    course = fields.ReferenceField(Course, required=True, reverse_delete_rule=fields.CASCADE)
    title = fields.StringField(required=True, max_length=120)
    deadline = fields.DateTimeField(required=True)

# -----------------------------
# Embedded Test Case Model
# -----------------------------
class TestCase(EmbeddedDocument):
    input_data = fields.StringField(required=True, max_length=200)
    expected_output = fields.StringField(required=True, max_length=200)

# -----------------------------
# Embedded Question Model
# -----------------------------
class Question(EmbeddedDocument):
    question_text = fields.StringField(required=True, max_length=500)
    type = fields.StringField(required=True, choices=["mcq", "msq", "nat"])
    options = fields.ListField(fields.StringField())  # Store as an array
    correct_answer = fields.StringField(required=True, max_length=200)

# -----------------------------
# Module Model
# -----------------------------
class Module(Document):
    week = fields.ReferenceField(Week, required=True, reverse_delete_rule=fields.CASCADE)
    title = fields.StringField(required=True, max_length=120)
    type = fields.StringField(required=True, choices=["video", "coding", "assignment", "document"])

    # Video type
    url = fields.StringField(max_length=300)

    # Coding type
    language = fields.StringField(max_length=50)
    description = fields.StringField(max_length=500)
    code_template = fields.StringField()
    test_cases = fields.EmbeddedDocumentListField(TestCase)  # Embedded Test Cases

    # Assignment type
    graded = fields.BooleanField(default=False)
    questions = fields.EmbeddedDocumentListField(Question)  # Embedded Questions

    # Document type
    doc_type = fields.StringField(max_length=20)
    doc_url = fields.StringField(max_length=300)
