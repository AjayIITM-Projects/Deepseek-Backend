from flask import Blueprint, request, jsonify
from flask_restful import Resource
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from youtube_transcript_api import YouTubeTranscriptApi
from api.models import User, Course, Announcement, Week, Module, TestCase, Question  # Import models

# Create a Blueprint
course_bp = Blueprint('course', __name__)

# Login Resource
class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            user = User.objects(username=username).first()
            if not user or not check_password_hash(user.password, password):
                return jsonify({'error': 'Invalid credentials', 'code': 400})

            access_token = create_access_token(identity={'user_id': str(user.id), 'role': user.role, 'email': user.email})

            return jsonify({
                'token': access_token,
                'code': 200,
                'user_id': str(user.id),
                'role': user.role,
                'email': user.email,
                'name': user.name,
                'profile_picture_url': user.profile_picture_url if hasattr(user, 'profile_picture_url') else ''
            })
        except Exception as e:
            return jsonify({'error': 'Something went wrong', 'code': 500, 'message': str(e)})

# Study Resource
class Study(Resource):
    def get(self):
        try:
            courses = Course.objects()
            course_content = [
                {
                    'course_id': str(course.id),
                    'course_name': course.CourseName,
                    'course_description': course.CourseDescription,
                    'start_date': course.StartDate.strftime("%Y-%m-%d"),
                    'end_date': course.EndDate.strftime("%Y-%m-%d"),
                } for course in courses
            ]
            return jsonify({'study': course_content, 'code': 200})
        except Exception as e:
            return jsonify({'error': 'Something went wrong', 'code': 500, 'message': str(e)})

# Course API Resource
class CourseAPI(Resource):
    def get(self):
        try:
            course = Course.objects.first()
            if not course:
                return jsonify({'error': 'Course not found', 'code': 404})

            announcements = Announcement.objects(course=course)
            announcement_list = [
                {"announcementId": str(ann.id), "message": ann.message, "date": ann.date.strftime("%Y-%m-%d")}
                for ann in announcements
            ]

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
                            "codeTemplate": module.code_template,
                            "testCases": [{"input": tc.input_data, "expected": tc.expected_output} for tc in module.test_cases]
                        })
                    elif module.type == "assignment":
                        module_data.update({
                            "questions": [{"question_text": q.question_text, "type": q.type, "options": q.options, "correct": q.correct_answer} for q in module.questions],
                            "graded": module.graded
                        })
                    elif module.type == "document":
                        module_data.update({"docType": module.doc_type, "url": module.doc_url, "description": module.description})
                    module_list.append(module_data)

                week_list.append({
                    "weekId": str(week.id),
                    "weekTitle": week.title,
                    "deadline": week.deadline.strftime("%Y-%m-%d"),
                    "modules": module_list
                })

            course_data = {
                "courseId": str(course.id),
                "title": course.CourseName,
                "description": course.CourseDescription,
                "announcements": announcement_list,
                "weeks": week_list
            }
            return jsonify(course_data)
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

# Get all available courses
@course_bp.route('/courses', methods=['GET'])
def get_courses():
    try:
        courses = Course.objects()
        course_list = [{"id": str(course.id), "name": course.CourseName, "description": course.CourseDescription} for course in courses]
        return jsonify({"courses": course_list, "code": 200})
    except Exception as e:
        return jsonify({"error": "Something went wrong", "code": 500, "message": str(e)})

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

        registered_courses = user.registered_courses  # Assuming `registered_courses` is a ListField
        if not registered_courses:
            return jsonify({"registered_courses": []})

        course_list = [
            {"id": str(course.id), "title": course.CourseName, "description": course.CourseDescription}
            for course in registered_courses
        ]
        return jsonify({"registered_courses": course_list})
    except Exception as e:
        return jsonify({"error": "Something went wrong", "message": str(e)}), 500
