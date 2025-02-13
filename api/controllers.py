from datetime import timedelta
from flask import Blueprint, make_response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, unset_jwt_cookies
from youtube_transcript_api import YouTubeTranscriptApi
from api.models import User, Course, Announcement, Week, Module, TestCase, Question  # Import models
from bson import ObjectId

# Create a Blueprint
course_bp = Blueprint('course', __name__)

from flask import request, jsonify, make_response
from flask_restful import Resource
from api.models import User

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

            return make_response(jsonify({
                'message': 'Login successful',
                'user_id': str(user.id),
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
    def get(self, user_id=None):
        """Fetch all users or a specific user by ID"""
        try:
            if user_id:
                if not ObjectId.is_valid(user_id):
                    return make_response(jsonify({"error": "Invalid user ID"}), 400)

                user = User.objects(id=user_id).first()
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
            user_list = [{
                "id": str(user.id),
                "role": user.role,
                "email": user.email,
                "name": user.name,
                "profilePictureUrl": user.profilePictureUrl,
                "registeredCourses": [str(course.id) for course in user.registeredCourses]
            } for user in users]

            return jsonify(user_list)

        except Exception as e:
            return make_response(jsonify({"error": "Something went wrong", "message": str(e)}), 500)

    def delete(self, user_id):
        """Delete a user by ID"""
        try:
            if not ObjectId.is_valid(user_id):
                return make_response(jsonify({"error": "Invalid user ID"}), 400)

            user = User.objects(id=user_id).first()
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

            registered_courses = user.registeredCourses
            if not registered_courses:
                return make_response(jsonify({"registeredCourses": []}), 200)

            course_list = [
                {
                    "id": str(course.id),
                    "name": course.name,
                    "description": course.description
                }
                for course in registered_courses
            ]
            return make_response(jsonify({"registeredCourses": course_list}), 200)

        except Exception as e:
            return make_response(jsonify({"error": "Something went wrong", "message": str(e)}), 500)

    def post(self):
        try:
            data = request.get_json()
            if not data or "email" not in data or "courses" not in data:
                return make_response(jsonify({"error": "Email and courses are required"}), 400)

            email = data["email"]
            course_ids = data["courses"]

            if not isinstance(course_ids, list) or not all(isinstance(course_id, str) for course_id in course_ids):
                return make_response(jsonify({"error": "Invalid course ID format"}), 400)

            try:
                course_object_ids = [ObjectId(course_id) for course_id in course_ids]
            except Exception as e:
                return make_response(jsonify({"error": "Invalid course ID", "details": str(e)}), 400)

            courses = Course.objects(id__in=course_object_ids)

            if len(courses) != len(course_ids):
                return make_response(jsonify({"error": "Some course IDs are invalid"}), 400)

            user = User.objects(email=email).first()

            if user:
                existing_courses = set(str(c.id) for c in user.registeredCourses)
                new_courses = [c for c in courses if str(c.id) not in existing_courses]

                if new_courses:
                    user.registeredCourses.extend(new_courses)
                    user.save()

                    for course in new_courses:
                        if user not in course.registeredUsers:
                            course.registeredUsers.append(user)
                            course.save()

                return make_response(jsonify({"message": "User updated with new courses", "user_id": str(user.id)}), 200)

            else:
                new_user = User(
                    role="student",
                    email=email,
                    name=email.split("@")[0].capitalize(),
                    registeredCourses=courses
                )
                new_user.save()

                for course in courses:
                    course.registeredUsers.append(new_user)
                    course.save()

                return make_response(jsonify({"message": "User registered successfully", "user_id": str(new_user.id)}), 201)

        except Exception as e:
            return make_response(jsonify({"error": "Something went wrong", "message": str(e)}), 500)


class CourseAPI(Resource):
    def get(self, course_id=None):
        try:
            if course_id:
                # Validate course_id
                if not ObjectId.is_valid(course_id):
                    return jsonify({'error': 'Invalid course ID format', 'code': 400})

                # Fetch the specific course
                course = Course.objects(id=course_id).first()
                if not course:
                    return jsonify({'error': 'Course not found', 'code': 404})

                # Fetch announcements for the course
                announcements = Announcement.objects(course=course)
                announcement_list = [
                    {
                        "announcementId": str(ann.id),
                        "message": ann.message,
                        "date": ann.date.strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                    for ann in announcements
                ]

                # Fetch weeks for the course
                weeks = Week.objects(course=course)
                week_list = []
                for week in weeks:
                    modules = Module.objects(week=week)
                    module_list = []
                    for module in modules:
                        module_data = {
                            "moduleId": str(module.id),
                            "title": module.title,
                            "type": module.type
                        }
                        if module.type == "video":
                            module_data["url"] = module.url
                        elif module.type == "coding":
                            module_data.update({
                                "language": module.language,
                                "description": module.description,
                                "codeTemplate": module.codeTemplate,  # Updated to camel case
                                "testCases": [
                                    {"inputData": tc.inputData, "expectedOutput": tc.expectedOutput} for tc in module.testCases  # Updated
                                ]
                            })
                        elif module.type == "assignment":
                            module_data.update({
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
                            module_data.update({
                                "docType": module.docType,  # Updated
                                "docUrl": module.docUrl,  # Updated
                                "description": module.description
                            })
                        module_list.append(module_data)

                    week_list.append({
                        "weekId": str(week.id),
                        "title": week.title,  # Fixed naming
                        "deadline": week.deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "modules": module_list
                    })

                # Construct the response
                course_data = {
                    "courseId": str(course.id),
                    "name": course.name,  # Updated
                    "description": course.description,  # Updated
                    "startDate": course.startDate.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Updated
                    "endDate": course.endDate.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Updated
                    "announcements": announcement_list,
                    "weeks": week_list
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

# YouTube Transcript API
@course_bp.route('/transcript', methods=['GET'])
def get_transcript():
    try:
        video_id = request.args.get('video_id')
        if not video_id:
            return jsonify({"error": "Missing video_id parameter"}), 400

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return jsonify({"video_id": video_id, "transcript": transcript})
    except Exception as e:
        return jsonify({"error": "Could not fetch transcript", "message": str(e)}), 500
