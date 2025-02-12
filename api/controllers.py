from flask import Blueprint, request, jsonify
from flask_restful import Resource
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from youtube_transcript_api import YouTubeTranscriptApi
from api.models import User, Course, Announcement, Week, Module, TestCase, Question  # Import models
from bson import ObjectId

# Create a Blueprint
course_bp = Blueprint('course', __name__)

# Login Resource
class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            print(data)
            username = data.get('username')
            password = data.get('password')

            user = User.objects(username=username).first()
            if not user or not check_password_hash(user.password, password):
                return jsonify({'error': 'Invalid credentials', 'code': 400})

            access_token = create_access_token(identity={
                'user_id': str(user.id),
                'role': user.role,
                'email': user.email
            })

            return jsonify({
                'token': access_token,
                'code': 200,
                'user_id': str(user.id),
                'role': user.role,
                'email': user.email,
                'name': user.name,
                'profilePictureUrl': user.profilePictureUrl if hasattr(user, 'profilePictureUrl') else ''
            })
        except Exception as e:
            return jsonify({'error': 'Something went wrong', 'code': 500, 'message': str(e)})


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


# Get the user registered courses
@course_bp.route('/registered-courses', methods=['GET'])
@jwt_required()
def get_registered_courses():
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']

        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found", "code": 404})

        registered_courses = user.registeredCourses  # Updated
        if not registered_courses:
            return jsonify({"registeredCourses": []})

        course_list = [
            {"id": str(course.id), "name": course.name, "description": course.description}  # Updated
            for course in registered_courses
        ]
        return jsonify({"registeredCourses": course_list})  # Updated
    except Exception as e:
        return jsonify({"error": "Something went wrong", "message": str(e)}), 500
