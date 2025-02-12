from mongoengine import Document, EmbeddedDocument, fields, connect, CASCADE
from datetime import datetime


# -----------------------------
# User Model
# -----------------------------
class User(Document):
    role = fields.StringField(required=True, max_length=50)
    email = fields.EmailField(required=True, unique=True)
    name = fields.StringField(required=True, max_length=120)
    profilePictureUrl = fields.StringField(max_length=200)  # Optional
    registeredCourses = fields.ListField(fields.ReferenceField('Course'))  # Many-to-Many

# -----------------------------
# Course Model
# -----------------------------
class Course(Document):
    name = fields.StringField(required=True, max_length=120)
    description = fields.StringField(required=True, max_length=500)
    startDate = fields.DateTimeField(required=True)
    endDate = fields.DateTimeField(required=True)
    registeredUsers = fields.ListField(fields.ReferenceField(User))  # Many-to-Many

# -----------------------------
# Announcement Model
# -----------------------------
class Announcement(Document):
    course = fields.ReferenceField(Course, required=True, reverse_delete_rule=CASCADE)
    message = fields.StringField(required=True, max_length=500)
    date = fields.DateTimeField(default=datetime.utcnow)

# -----------------------------
# Week Model
# -----------------------------
class Week(Document):
    course = fields.ReferenceField(Course, required=True, reverse_delete_rule=CASCADE)
    title = fields.StringField(required=True, max_length=120)
    deadline = fields.DateTimeField(required=True)

# -----------------------------
# Embedded Test Case Model
# -----------------------------
class TestCase(EmbeddedDocument):
    inputData = fields.StringField(required=True, max_length=200)
    expectedOutput = fields.StringField(required=True, max_length=200)

# -----------------------------
# Embedded Question Model
# -----------------------------
class Question(EmbeddedDocument):
    question = fields.StringField(required=True, max_length=500)
    type = fields.StringField(required=True, choices=["mcq", "msq", "nat"])
    options = fields.ListField(fields.StringField())  # Store as an array
    correctAnswer = fields.StringField(required=True, max_length=200)

# -----------------------------
# Module Model
# -----------------------------
class Module(Document):
    week = fields.ReferenceField(Week, required=True, reverse_delete_rule=CASCADE)
    title = fields.StringField(required=True, max_length=120)
    type = fields.StringField(required=True, choices=["video", "coding", "assignment", "document"])

    # Video type
    url = fields.StringField(max_length=300)

    # Coding type
    language = fields.StringField(max_length=50)
    description = fields.StringField(max_length=500)
    codeTemplate = fields.StringField()
    testCases = fields.EmbeddedDocumentListField(TestCase)  # Embedded Test Cases

    # Assignment type
    isGraded = fields.BooleanField(default=False)
    questions = fields.EmbeddedDocumentListField(Question)  # Embedded Questions

    # Document type
    docType = fields.StringField(max_length=20)
    docUrl = fields.StringField(max_length=300)
