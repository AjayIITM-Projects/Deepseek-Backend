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
    # Added camelCase fields for controller compatibility
    questionsAttempted = fields.ListField(fields.ReferenceField('Question'))  # Corrected to camelCase
    modulesCompleted = fields.ListField(fields.ReferenceField('Module'))  # Corrected to camelCase
    averageScore = fields.FloatField()  # Corrected to camelCase

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
    date = fields.DateTimeField(default=datetime.now)

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


class ChatHistory(Document):
    # Modified to include sessionId as per the controller route
    sessionId = fields.StringField(required=True, max_length=100)  # Assuming sessionId is a string
    user = fields.ReferenceField('User', required=True, reverse_delete_rule=CASCADE)
    query = fields.StringField(required=True, max_length=500)
    response = fields.StringField(required=True, max_length=1000)
    timestamp = fields.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"ChatHistory(sessionId={self.sessionId}, query={self.query}, response={self.response})"


class CodeSubmission(Document):
    user = fields.ReferenceField('User', required=True, reverse_delete_rule=CASCADE)
    question = fields.ReferenceField('Question', required=True, reverse_delete_rule=CASCADE)
    submittedCode = fields.StringField(required=True)
    output = fields.StringField()
    isCorrect = fields.BooleanField(default=False)
    timestamp = fields.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"CodeSubmission(user={self.user}, question={self.question}, submittedCode={self.submittedCode}, output={self.output})"
