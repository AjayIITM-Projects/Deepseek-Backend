from datetime import timedelta
from flask import Blueprint, make_response, request, jsonify, session
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, unset_jwt_cookies
from youtube_transcript_api import YouTubeTranscriptApi
from api.models import User, Course, Announcement, Week, Module, TestCase, Question, ChatHistory, CodeSubmission # Import models
from bson import ObjectId



# Create a Blueprint
course_bp = Blueprint('course', __name__)

class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            name = data.get('name')
            picture = data.get('picture')
            if not email:
                return make_response(jsonify({"error": "Email is required"}), 400)

            user = User.objects(email=email).first()

            if not user:
                user = User(
                    role="student",
                    email=email,
                    name=name if name else email.split("@")[0].capitalize(),
                    profilePictureUrl=picture if picture else "",
                    registeredCourses=[]
                )
                user.save()
            
            # Flask session creation to store user info
            session['userId'] = str(user.id)  # Store the user ID in the session

            return make_response(jsonify({
                'message': 'Login successful',
                'userId': str(user.id),  # Changed user_id to userId
                'role': user.role,
                'email': user.email,
                'name': user.name,
                'picture': user.profilePictureUrl,
            }), 200)
        except Exception as e:
            return make_response(jsonify({"error": "Something went wrong", "message": str(e)}), 500)

# Create a Blueprint
user_bp = Blueprint('user', __name__)

class UsersAPI(Resource):
    def get(self, userId=None):  # Changed user_id to userId
        """Fetch all users or a specific user by ID"""
        try:
            
            if 'userId' not in session:  # If user is not logged in
                return make_response(jsonify({"error": "Unauthorized, please log in"}), 401)


            if userId:
                if not ObjectId.is_valid(userId):
                    return make_response(jsonify({"error": "Invalid user ID"}), 400)

                user = User.objects(id=userId).first()
                if not user:
                    return make_response(jsonify({"error": "User not found"}), 404)

                return jsonify({
                    "id": str(user.id),
                    "role": user.role,
                    "email": user.email,
                    "name": user.name,
                    "profilePictureUrl": user.profilePictureUrl,
                    "registeredCourses": [str(course.id) for course in user.registeredCourses]
                })
            
            # Fetch all users
            users = User.objects()
            userList = [{
                "id": str(user.id),
                "role": user.role,
                "email": user.email,
                "name": user.name,
                "profilePictureUrl": user.profilePictureUrl,
                "registeredCourses": [str(course.id) for course in user.registeredCourses]
            } for user in users]

            return jsonify(userList)

        except Exception as e:
            return make_response(jsonify({"error": "Something went wrong", "message": str(e)}), 500)

    def delete(self, userId):
        """Delete a user by ID"""
        try:
            
            if 'userId' not in session:  # If user is not logged in
                return make_response(jsonify({"error": "Unauthorized, please log in"}), 401)

            if not ObjectId.is_valid(userId):
                return make_response(jsonify({"error": "Invalid user ID"}), 400)

            user = User.objects(id=userId).first()
            if not user:
                return make_response(jsonify({"error": "User not found"}), 404)

            user.delete()
            return make_response(jsonify({"message": "User deleted successfully"}), 200)

        except Exception as e:
            return make_response(jsonify({"error": "Something went wrong", "message": str(e)}), 500)


class RegisteredCourses(Resource):
    def get(self):
        try:
            email = request.args.get('email')
            if not email:
                return make_response(jsonify({"error": "Email is required"}), 400)

            user = User.objects(email=email).first()
            if not user:
                return make_response(jsonify({"error": "User not found"}), 404)

            registeredCourses = user.registeredCourses
            if not registeredCourses:
                return make_response(jsonify({"registeredCourses": []}), 200)

            courseList = [
                {
                    "id": str(course.id),
                    "name": course.name,
                    "description": course.description
                }
                for course in registeredCourses
            ]
            return make_response(jsonify({"registeredCourses": courseList}), 200)

        except Exception as e:
            return make_response(jsonify({"error": "Something went wrong", "message": str(e)}), 500)

    def post(self):
        try:
            data = request.get_json()
            if not data or "email" not in data or "courses" not in data:
                return make_response(jsonify({"error": "Email and courses are required"}), 400)

            email = data["email"]
            courseIds = data["courses"]

            if not isinstance(courseIds, list) or not all(isinstance(courseId, str) for courseId in courseIds):
                return make_response(jsonify({"error": "Invalid course ID format"}), 400)

            try:
                courseObjectIds = [ObjectId(courseId) for courseId in courseIds]
            except Exception as e:
                return make_response(jsonify({"error": "Invalid course ID", "details": str(e)}), 400)

            courses = Course.objects(id__in=courseObjectIds)

            if len(courses) != len(courseIds):
                return make_response(jsonify({"error": "Some course IDs are invalid"}), 400)

            user = User.objects(email=email).first()

            if user:
                existingCourses = set(str(c.id) for c in user.registeredCourses)
                newCourses = [c for c in courses if str(c.id) not in existingCourses]

                if newCourses:
                    user.registeredCourses.extend(newCourses)
                    user.save()

                    for course in newCourses:
                        if user not in course.registeredUsers:
                            course.registeredUsers.append(user)
                            course.save()

                return make_response(jsonify({"message": "User updated with new courses", "user_id": str(user.id)}), 200)

            else:
                newUser = User(
                    role="student",
                    email=email,
                    name=email.split("@")[0].capitalize(),
                    registeredCourses=courses
                )
                newUser.save()

                for course in courses:
                    course.registeredUsers.append(newUser)
                    course.save()

                return make_response(jsonify({"message": "User registered successfully", "user_id": str(newUser.id)}), 201)

        except Exception as e:
            return make_response(jsonify({"error": "Something went wrong", "message": str(e)}), 500)


class CourseAPI(Resource):
    def get(self, courseId=None):
        try:
            
            if 'userId' not in session:  # If user is not logged in
                return jsonify({'error': 'Unauthorized, please log in', 'code': 401})
            
            if courseId:
                # Validate course_id
                if not ObjectId.is_valid(courseId):
                    return jsonify({'error': 'Invalid course ID format', 'code': 400})

                # Fetch the specific course
                course = Course.objects(id=courseId).first()
                if not course:
                    return jsonify({'error': 'Course not found', 'code': 404})

                # Fetch announcements for the course
                announcements = Announcement.objects(course=course)
                announcementList = [
                    {
                        "announcementId": str(ann.id),
                        "message": ann.message,
                        "date": ann.date.strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                    for ann in announcements
                ]

                # Fetch weeks for the course
                weeks = Week.objects(course=course)
                weekList = []
                for week in weeks:
                    modules = Module.objects(week=week)
                    moduleList = []
                    for module in modules:
                        moduleData = {
                            "moduleId": str(module.id),
                            "title": module.title,
                            "type": module.type
                        }
                        if module.type == "video":
                            moduleData["url"] = module.url
                        elif module.type == "coding":
                            moduleData.update({
                                "language": module.language,
                                "description": module.description,
                                "codeTemplate": module.codeTemplate,  # Updated to camel case
                                "testCases": [
                                    {"inputData": tc.inputData, "expectedOutput": tc.expectedOutput} for tc in module.testCases  # Updated
                                ]
                            })
                        elif module.type == "assignment":
                            moduleData.update({
                                "questions": [
                                    {
                                        "question": q.question,
                                        "type": q.type,
                                        "options": q.options,
                                        "correctAnswer": q.correctAnswer  # Updated
                                    } 
                                    for q in module.questions
                                ],
                                "graded": module.isGraded
                            })
                        elif module.type == "document":
                            moduleData.update({
                                "docType": module.docType,  # Updated
                                "docUrl": module.docUrl,  # Updated
                                "description": module.description
                            })
                        moduleList.append(moduleData)

                    weekList.append({
                        "weekId": str(week.id),
                        "title": week.title,  # Fixed naming
                        "deadline": week.deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "modules": moduleList
                    })

                # Construct the response
                course_data = {
                    "courseId": str(course.id),
                    "name": course.name,  # Updated
                    "description": course.description,  # Updated
                    "startDate": course.startDate.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Updated
                    "endDate": course.endDate.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Updated
                    "announcements": announcementList,
                    "weeks": weekList
                }
                return jsonify(course_data)

            else:
                # Get all courses
                courses = Course.objects()
                course_list = [{
                    'id': str(course.id),
                    'name': course.name,  # Updated
                    'description': course.description,  # Updated
                    'startDate': course.startDate.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Updated
                    'endDate': course.endDate.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Updated
                } for course in courses]
                return jsonify({"courses": course_list, "code": 200})

        except Exception as e:
            return jsonify({'error': 'Something went wrong', 'code': 500, 'message': str(e)})


class YouTubeTranscriptAPI(Resource):
    def get(self):
        try:
            videoId = request.args.get('videoId')
            if not videoId:
                return jsonify({"error": "Video ID is required"}), 400

            transcript = YouTubeTranscriptApi.get_transcript(videoId)
            return jsonify({"transcript": transcript})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

class ChatbotInteractionAPI(Resource):
    def post(self):
        try:
            data = request.get_json()
            query = data.get("query")
            option = data.get("option")
            sessionId = data.get("sessionId")

            if not query or not option:
                return jsonify({"error": "Query and option are required"}), 400

            chatHistory = []
            if sessionId:
                chatHistory = ChatHistory.objects(sessionId=sessionId).order_by('timestamp')

            responseText = "RAG API response based on history"

            chatEntry = ChatHistory(sessionId=sessionId, query=query, response=responseText)
            chatEntry.save()

            response = {
                "sessionId": sessionId,
                "question": query,
                "answer": responseText,
                "chatHistory": [{"query": chat.query, "answer": chat.response} for chat in chatHistory]
            }
            return jsonify(response)

        except Exception as e:
            return jsonify({"error": "Something went wrong", "message": str(e)}), 500

class UserStatisticsAPI(Resource):
    def get(self, userId):
        try:

            if 'userId' not in session:  # If user is not logged in
                return jsonify({"error": "Unauthorized, please log in"}), 401

            if not ObjectId.is_valid(userId):
                return jsonify({"error": "Invalid user ID"}), 400

            user = User.objects(id=userId).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

            userData = {
                "id": str(user.id),
                "role": user.role,
                "email": user.email,
                "name": user.name,
                "registeredCourses": [str(course.id) for course in user.registeredCourses],
                "statistics": {
                    "questionsAttempted": len(getattr(user, 'questionsAttempted', [])),
                    "modulesCompleted": len(getattr(user, 'modulesCompleted', [])),
                    "averageScore": getattr(user, 'averageScore', None)
                }
            }
            return jsonify(userData)

        except Exception as e:
            return jsonify({"error": "Something went wrong", "message": str(e)}), 500

class RunCodeAPI(Resource):
    def post(self):
        try:
            data = request.get_json()
            questionId = data.get("questionId")
            code = data.get("code")
            if not questionId or not code:
                return jsonify({"error": "Question ID and code are required"}), 400

            question = Question.objects(id=questionId).first()
            if not question:
                return jsonify({"error": "Question not found"}), 404

            result = {"status": "success", "output": "Test case results here"}
            return jsonify(result)

        except Exception as e:
            return jsonify({"error": "Something went wrong", "message": str(e)}), 500

class AdminStatisticsAPI(Resource):
    def get(self):
        try:
            statisticsData = {
                "totalUsers": User.objects.count(),
                "totalModules": Module.objects.count(),
                "activeUsers": User.objects(active=True).count(),
                "questionsAttempted": sum(user.questionsAttempted for user in User.objects)
            }
            return jsonify(statisticsData)

        except Exception as e:
            return jsonify({"error": "Something went wrong", "message": str(e)}), 500
