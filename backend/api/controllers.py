from flask import Blueprint, request, jsonify
from flask_restful import Resource
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity
from models import db, User, Course, Announcement, Week, Module, TestCase, Question, UserCourse
from youtube_transcript_api import YouTubeTranscriptApi
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


# Create a Blueprint
course_bp = Blueprint('course', __name__)

# Login Resource
class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            user = User.query.filter_by(username=username).first()
            if not user or not bcrypt.check_password_hash(user.password, password):
                return jsonify({'error': 'Invalid credentials', 'code': 400})

            access_token = create_access_token(identity={'user_id': user.id, 'role': user.role, 'email': user.email})

            return jsonify({
                'token': access_token,
                'code': 200,
                'user_id': user.id,
                'role': user.role,
                'email': user.email,
                'name': user.name,
                'profile_picture_url': user.profile_picture_url
            })
        except Exception as e:
            return jsonify({'error': 'Something went wrong', 'code': 500, 'message': str(e)})

# Study Resource
class Study(Resource):
    # @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            user = User.query.get(current_user['user_id'])
            if not user:
                return jsonify({'error': 'User not found', 'code': 404})

            courses = Course.query.all()
            course_content = [
                {
                    'course_id': course.CourseID,
                    'course_name': course.CourseName,
                    'course_description': course.CourseDescription,
                    'start_date': course.StartDate,
                    'end_date': course.EndDate,
                } for course in courses
            ]
            return jsonify({'study': course_content, 'code': 200})
        except Exception as e:
            return jsonify({'error': 'Something went wrong', 'code': 500, 'message': str(e)})

# Course API Resource
class CourseAPI(Resource):
    def get(self):
        try:
            course = Course.query.first()
            if not course:
                return jsonify({'error': 'Course not found', 'code': 404})

            announcements = Announcement.query.filter_by(course_id=course.CourseID).all()
            announcement_list = [
                {"announcementId": ann.id, "message": ann.message, "date": ann.date.isoformat()}
                for ann in announcements
            ]

            weeks = Week.query.filter_by(course_id=course.CourseID).all()
            week_list = []
            for week in weeks:
                modules = Module.query.filter_by(week_id=week.id).all()
                module_list = []
                for module in modules:
                    module_data = {"moduleId": module.id, "title": module.title, "type": module.type}
                    if module.type == "video":
                        module_data["url"] = module.url
                    elif module.type == "coding":
                        module_data.update({
                            "language": module.language,
                            "description": module.description,
                            "codeTemplate": module.code_template,
                            "testCases": [
                                {"testCaseId": tc.id, "input": tc.input_data, "expectedOutput": tc.expected_output}
                                for tc in TestCase.query.filter_by(module_id=module.id).all()
                            ]
                        })
                    elif module.type == "assignment":
                        module_data.update({
                            "questions": [
                                {"questionId": q.id, "question": q.question_text, "type": q.type,
                                 "options": q.options.split(",") if q.options else [], "correctAnswer": q.correct_answer}
                                for q in Question.query.filter_by(module_id=module.id).all()
                            ],
                            "graded": module.graded
                        })
                    elif module.type == "document":
                        module_data.update({"docType": module.doc_type, "url": module.url, "description": module.description})
                    module_list.append(module_data)
                week_list.append({"weekId": week.id, "weekTitle": week.title, "deadline": week.deadline.isoformat(), "modules": module_list})

            course_data = {
                "courseId": course.CourseID,
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
        courses = Course.query.all()
        course_list = [
            {
                "id": course.CourseID,
                "name": course.CourseName,
                "description": course.CourseDescription
            }
            for course in courses
        ]
        return jsonify({"courses": course_list, "code": 200})
    except Exception as e:
        return jsonify({"error": "Something went wrong", "code": 500, "message": str(e)})
    

@course_bp.route('/registered-courses', methods=['GET'])
# @jwt_required()
def get_registered_courses():
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']

        # Fetch all courses registered by the user from UserCourse table
        registered_courses = UserCourse.query.filter_by(user_id=user_id).all()
        if not registered_courses:
            return jsonify({"registered_courses": []})

        course_ids = [uc.course_id for uc in registered_courses]
        courses = Course.query.filter(Course.CourseID.in_(course_ids)).all()
        
        course_list = [{"id": course.CourseID, "title": course.CourseName, "description": course.CourseDescription} for course in courses]
        return jsonify({"registered_courses": course_list})

    except Exception as e:
        return jsonify({"error": "Something went wrong", "message": str(e)}), 500

