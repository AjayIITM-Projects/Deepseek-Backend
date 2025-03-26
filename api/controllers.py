from datetime import timedelta, datetime
from flask import Blueprint, make_response, request, jsonify, session
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, unset_jwt_cookies
from youtube_transcript_api import YouTubeTranscriptApi
from api.models import User, Course, Announcement, Week, Module, TestCase, Question, VideoTranscript, ChatHistory, ChatQuestions # Import models
from bson import ObjectId
import re
import os
import requests
import subprocess
import sys
from mongoengine.errors import DoesNotExist


def get_ist_time():
    return datetime.now() + timedelta(hours=5, minutes=30)

def process_history(history):
    # Remove the first entry of the history
    history = history[1:]
    
    # Prepare the formatted result
    formatted_history = []

    # Iterate through the history and pair user query with bot response
    for i in range(0, len(history), 2):
        if i + 1 < len(history):  # Ensure there is a corresponding bot response
            query = history[i]['text']  # User's message
            answer = history[i + 1]['text']  # Bot's response
            formatted_history.append({
                'query': query,
                'answer': answer
            })
    
    return formatted_history

def get_module_type(moduleId):
    # Fetch the module from the database using the moduleId
    module = Module.objects(id=moduleId).first()
    
    if not module:
        return "Module not found"
    
    prompt_option = ""

    if module.isGraded:
        prompt_option = "graded"
    elif module.type == "assignment":
        prompt_option = "practice"
    else:
        prompt_option = "learning"
    
    return prompt_option

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
            
            user.lastLogin = get_ist_time()
            user.save()
            return make_response(jsonify({
                'message': 'Login successful',
                'userId': str(user.id),  # Changed user_id to userId
                'role': user.role,
                'email': user.email,
                'name': user.name,
                'picture': user.profilePictureUrl,
                'lastLogin': user.lastLogin
            }), 200)
        except Exception as e:
            return make_response(jsonify({"error": "Something went wrong", "message": str(e)}), 500)

user_bp = Blueprint('user', __name__)

class UsersAPI(Resource):
    def get(self, userId=None):  # Changed user_id to userId
        """Fetch all users or a specific user by ID"""
        try:
            
            # if 'userId' not in session:  # If user is not logged in
            #     return make_response(jsonify({"error": "Unauthorized, please log in"}), 401)


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
            
            # if 'userId' not in session:  # If user is not logged in
            #     return make_response(jsonify({"error": "Unauthorized, please log in"}), 401)

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
            # if 'userId' not in session:  # If user is not logged in
            #     return make_response(jsonify({'error': 'Unauthorized, please log in'}), 401)
            
            if courseId:
                # Validate course_id
                if not ObjectId.is_valid(courseId):
                    return make_response(jsonify({'error': 'Invalid course ID format'}), 400)

                # Fetch the specific course
                course = Course.objects(id=courseId).first()
                if not course:
                    return make_response(jsonify({'error': 'Course not found'}), 404)

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
                                "codeTemplate": module.codeTemplate,
                                "hint": module.hint or "No hint available.",  # Added hint for coding modules
                                "testCases": [
                                    {"inputData": tc.inputData, "expectedOutput": tc.expectedOutput} for tc in module.testCases
                                ]
                            })
                        elif module.type == "assignment":
                            moduleData.update({
                                "questions": [
                                    {
                                        "question": q.question,
                                        "type": q.type,
                                        "options": q.options,
                                        "correctAnswer": q.correctAnswer,
                                        "hint": q.hint  # Added hint field for assignment type
                                    } 
                                    for q in module.questions
                                ],
                                "graded": module.isGraded
                            })
                        elif module.type == "document":
                            moduleData.update({
                                "docType": module.docType,
                                "docUrl": module.docUrl,
                                "description": module.description
                            })
                        moduleList.append(moduleData)

                    weekList.append({
                        "weekId": str(week.id),
                        "title": week.title,
                        "deadline": week.deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "modules": moduleList
                    })

                # Construct the response
                course_data = {
                    "courseId": str(course.id),
                    "name": course.name,
                    "description": course.description,
                    "startDate": course.startDate.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "endDate": course.endDate.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "announcements": announcementList,
                    "weeks": weekList
                }
                return make_response(jsonify(course_data), 200)

            else:
                # Get all courses
                courses = Course.objects()
                course_list = [{
                    'id': str(course.id),
                    'name': course.name,
                    'description': course.description,
                    'startDate': course.startDate.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'endDate': course.endDate.strftime("%Y-%m-%dT%H:%M:%SZ"),
                } for course in courses]
                return make_response(jsonify({"courses": course_list}), 200)

        except Exception as e:
            return make_response(jsonify({'error': 'Something went wrong', 'message': str(e)}), 500)
        
# Helper function to extract video ID from YouTube URL
def extract_video_id(video_url):
    """
    Extracts the video ID from a YouTube URL.
    Supports various YouTube URL formats.
    """
    # Regex to match YouTube video IDs in different URL formats
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, video_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

# Function to fetch and save transcripts
def fetch_and_save_transcripts(video_urls):
    """
    Fetches transcripts for a list of video URLs and saves them in the database.
    """
    for video_url in video_urls:
        try:
            # Extract video ID from the URL
            video_id = extract_video_id(video_url)
            
            # Fetch transcript using YouTubeTranscriptApi
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Save the transcript in the database
            video_transcript = VideoTranscript(videoID=video_id, transcript=transcript)
            video_transcript.save()
            print(f"Transcript saved for video URL: {video_url} (Video ID: {video_id})")
        except Exception as e:
            print(f"Error fetching transcript for video URL {video_url}: {str(e)}")

# Route to fetch transcript for a specific video URL
class VideoTranscriptAPI(Resource):
    def get(self):
        try:
            video_url = request.args.get('videoURL')  # Get video URL from query parameter
            if not video_url:
                return make_response(jsonify({"error": "videoURL is required"}), 400)

            # Extract video ID from the URL
            video_id = extract_video_id(video_url)

            # Fetch the transcript from the database
            video_transcript = VideoTranscript.objects(videoID=video_id).first()
            if not video_transcript:
                return make_response(jsonify({"error": "Transcript not found for the given video URL"}), 404)

            # Concatenate the full transcript from the chunked transcript
            full_transcript = " ".join([chunk["text"] for chunk in video_transcript.transcript])

            return make_response(jsonify({
                "videoURL": video_url,
                "videoID": video_transcript.videoID,
                "transcript": full_transcript  # Return only the full transcript
            }), 200)
        except ValueError as e:
            return make_response(jsonify({"error": "Invalid YouTube URL", "message": str(e)}), 400)
        except Exception as e:
            return make_response(jsonify({"error": "Something went wrong", "message": str(e)}), 500)

# Register the VideoTranscriptAPI route
course_bp.add_url_rule('/video-transcript', view_func=VideoTranscriptAPI.as_view('video_transcript_api'))

class ChatbotInteractionAPI(Resource):
    def post(self):
        try:
            data = request.get_json()
            query = data.get("query")
            history = data.get("history")
            email = data.get("email")
            moduleId = data.get("moduleId")
            
            user = User.objects(email=email).first()
            if not user:
                return {"error": "User not found"}, 404
            
            if not query or not history:
                return {"error": "Query and history are required"}, 400

            
            # Retrieve the module based on moduleId
            module = Module.objects(id=moduleId).first()
            
            # Look for existing ChatQuestions entry for the same user, date, course, and week
            existing_question_entry = ChatQuestions.objects(
                user=user,
                date=get_ist_time().date(),
                course=module.week.course,
                week=module.week
            ).first()

            # If an entry exists, append the new question to the existing array of questions
            if existing_question_entry:
                existing_question_entry.update(push__questions=query)
                # return {"message": "Question added to existing entry"}, 200
            else:
                # If no entry exists, create a new entry
                new_question_entry = ChatQuestions(
                    user=user, 
                    week=module.week,
                    course=module.week.course,
                    date=get_ist_time().date(),
                    questions=[query],  # Initialize with the current question
                )
                new_question_entry.save()
                # return {"message": "New question entry created"}, 201

            # Optionally, you could also handle the response from an external service
            data = {
                'query' : query,
                'history' : process_history(history),
                'prompt_option' : get_module_type(moduleId)
            }
            
            response = requests.post(os.getenv("RAG_API") + "/ask", json=data)

            # Check the status code and the response
            if response.status_code == 200:
                return response.json(), 200
            else:
                return response.text, response.status_code
            
        except Exception as e:
            # Return error with details
            return {"error": "Something went wrong", "message": str(e)}, 500

        
    def serialize_user(self, user):
        # Serialize the user object
        if user:
            return {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "profilePictureUrl": user.profilePictureUrl
            }
        return None

class FetchWeekwiseQuestionsAPI(Resource):
    def get(self):
        try:
            # Get query parameter for the course
            courseId = request.args.get('courseId')
            course = Course.objects(id=courseId).first()
            
            # Ensure the 'course' parameter is provided
            if not course:
                return {"error": "Course is required"}, 400
            
            # Retrieve all ChatQuestions that match the given course
            questions = ChatQuestions.objects(course=course)
            
            if not questions:
                return {"message": "No questions found for the given course"}, 404
            
            # Group questions by week
            weekwise_questions = {}
            
            for question_entry in questions:
                week = question_entry.week
                if week not in weekwise_questions:
                    weekwise_questions[week] = []
                
                # Append the questions for each week
                weekwise_questions[week].extend(question_entry.questions)
            
            # Prepare the result to return, sorted by week
            result = []
            for week, questions_list in sorted(weekwise_questions.items()):
                result.append({
                    'week': week,
                    'questions': questions_list
                })
            
            return {"weekwise_questions": result}, 200

        except Exception as e:
            # Return error if something went wrong
            return {"error": "Something went wrong", "message": str(e)}, 500

class UserStatisticsAPI(Resource):
    def get(self, userId):
        try:

            # if 'userId' not in session:  # If user is not logged in
            #     return jsonify({"error": "Unauthorized, please log in"}), 401

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
            moduleId = data.get("moduleId")
            code = data.get("code")

            # Validate input
            if not moduleId or not code:
                return {"error": "moduleId and code are required"}, 400

            # Find the module containing the code submission
            module = Module.objects(id=moduleId).first()
            if not module:
                return {"error": "Module not found"}, 404

            # Check if the module is of type "coding"
            if module.type != "coding":
                return {"error": "This module is not a coding module"}, 400

            # Check if the module has test cases
            if not hasattr(module, "testCases") or not module.testCases:
                return {"error": "No test cases found in this module"}, 404

            # Execute the code and compare with the test cases
            # (This is a placeholder; you'll need to implement code execution logic)
            result = {
                "status": "success",
                "output": "Test case results here",
                "isCorrect": True  # Placeholder
            }
            return result

        except Exception as e:
            return {"error": "Something went wrong", "message": str(e)}, 500

class AdminStatisticsAPI(Resource):
    def get(self):
        try:
            statisticsData = {
                "totalUsers": User.objects.count(),
                "totalModules": Module.objects.count(),
                "activeUsers": User.objects(active=True).count(),
                "questionsAttempted": sum(len(user.questionsAttempted) for user in User.objects)  # Sum the lengths of the lists
            }
            return statisticsData

        except Exception as e:
            return {"error": "Something went wrong", "message": str(e)}, 500
        
@course_bp.route('/submit/code', methods=['POST'])
def submit_code():
    """
    API endpoint to handle code submission.
    Expects JSON payload with:
    - email: Email of the user submitting the code
    - moduleId: ID of the module (coding problem)
    - code: The submitted code as a string
    """
    try:
        # Parse the request data
        data = request.get_json()
        email = data.get('email')
        module_id = data.get('moduleId')
        submitted_code = data.get('code')

        if not email or not module_id or not submitted_code:
            return jsonify({"error": "Missing required fields (email, moduleId, code)"}), 400

        # Fetch the user from the database using email
        user = User.objects(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Fetch the module (coding problem) from the database
        module = Module.objects(id=module_id).first()
        if not module or module.type != "coding":
            return jsonify({"error": "Invalid module or module is not a coding problem"}), 404

        # Fetch the test cases for the module
        test_cases = module.testCases
        if not test_cases:
            return jsonify({"error": "No test cases found for this module"}), 404

        # Validate the syntax of the submitted code
        try:
            compile(submitted_code, '<string>', 'exec')
        except SyntaxError as e:
            return jsonify({
                "error": "Syntax error in the submitted code",
                "syntaxError": str(e),
                "line": e.lineno,
                "offset": e.offset,
                "message": e.msg
            }), 400

        # Prepare the results
        results = []
        all_passed = True
        passed_count = 0  # Counter for passed test cases

        # Execute the code for each test case
        for test_case in test_cases:
            input_data = test_case.inputData
            expected_output = test_case.expectedOutput

            try:
                # Execute the user's code with the input data
                process = subprocess.run(
                    [sys.executable, "-c", submitted_code],
                    input=input_data,
                    text=True,
                    capture_output=True
                )

                # Get the output from the executed code
                actual_output = process.stdout.strip()

                # Compare the actual output with the expected output
                is_correct = (actual_output == expected_output)
                if is_correct:
                    passed_count += 1  # Increment passed count
                else:
                    all_passed = False

                # Store the result for this test case
                results.append({
                    "input": input_data,
                    "expectedOutput": expected_output,
                    "actualOutput": actual_output,
                    "isCorrect": is_correct
                })

            except Exception as e:
                # Handle execution errors (e.g., runtime errors)
                return jsonify({"error": f"Code execution failed: {str(e)}"}), 500

        # # Save the submission to the database
        # code_submission = CodeSubmission(
        #     user=user,  # Reference to the User document
        #     question=None,  # You can embed the question if needed
        #     submittedCode=submitted_code,
        #     output=str(results),  # Store the results as a string
        #     isCorrect=all_passed
        # )
        # code_submission.save()

        # Update the user's attempted questions or modules if needed
        if module not in user.modulesCompleted:
            user.modulesCompleted.append(module)
            user.save()

        # Return the results to the user
        return jsonify({
            "message": "Code submitted successfully",
            "allPassed": all_passed,
            "passedCount": passed_count,  # Number of test cases passed
            "totalTestCases": len(test_cases),  # Total number of test cases
            "results": results
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@course_bp.route('/debug/code', methods=['POST'])
def debug_code2():
    """
    API endpoint to debug code submissions.
    Expects JSON payload with:
    - email: Email of the user submitting the code
    - moduleId: ID of the module (coding problem)
    - code: The submitted code as a string
    """
    try:
        # Parse the request data
        data = request.get_json()
        email = data.get('email')
        module_id = data.get('moduleId')
        submitted_code = data.get('code')

        if not email or not module_id or not submitted_code:
            return jsonify({"error": "Missing required fields (email, moduleId, code)"}), 400

        # Fetch the user from the database using email
        user = User.objects(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Fetch the module (coding problem) from the database
        module = Module.objects(id=module_id).first()
        if not module or module.type != "coding":
            return jsonify({"error": "Invalid module or module is not a coding problem"}), 404
        

        debug_prompt = f"""
You are 'Alfred', an expert Python programmer and debugging assistant.
Analyze the provided Python code and identify any errors or issues.
Respond with a concise explanation in **two lines only**.

**Code:** {submitted_code}

**Question:** {module.description}
"""
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{
                "role": "user",
                "content": debug_prompt
            }]
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"
        })

        # Check if the RAG API responded successfully
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            # If the RAG API response was not successful, return the error response from RAG API
            return jsonify({"error": "Failed to debug code", "message": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    

@course_bp.route('/dashboard/user/questions', methods=['GET'])
def get_coursewise_questions():
    try:
        # Get user email from request
        user_email = request.args.get('email') or request.json.get('email')
        
        if not user_email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Get the user object
        user = User.objects.get(email=user_email)
        
        # Query all ChatQuestions for this user, sorted by date descending
        chat_questions = ChatQuestions.objects(user=user).order_by('-date')
        
        # Dictionary to group by course
        courses = {}
        
        for cq in chat_questions:
            course_id = str(cq.course.id)
            
            if course_id not in courses:
                courses[course_id] = {
                    'course_name': cq.course.name,
                    'questions': []
                }
            
            # Add all questions with their dates
            for question in cq.questions:
                courses[course_id]['questions'].append({
                    'question': question,
                    'date': cq.date.isoformat()
                })
        
        # Sort questions within each course by date descending
        for course in courses.values():
            course['questions'].sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': courses
        })
        
    except DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@course_bp.route('/top-questions', methods=['POST'])
def get_top_questions():
    """
    API endpoint to debug code submissions.
    Expects JSON payload with:
    - email: Email of the user submitting the code
    - moduleId: ID of the module (coding problem)
    - code: The submitted code as a string
    """
    try:
        # Parse the request data
        data = request.get_json()
        email = data.get('email')
        courseId = data.get('courseId')

        if not email or not courseId:
            return jsonify({"error": "Missing required fields (email, courseId)"}), 400

        # Fetch the user from the database using email
        user = User.objects(email=email).first()
        if not user or user.role != "instructor":
            return jsonify({"error": "User not found"}), 404

        # Fetch the module (coding problem) from the database
        course = Course.objects(id=courseId).first()
        if not course:
            return jsonify({"error": "Invalid courseId"}), 404
        
        questions = ChatQuestions.objects(course=course).all()
        all_questions = []
        for question in questions:
            all_questions.extend(question.questions)
        
        
        prompt = f"""
Analyze these programming questions and return the top 5 most frequent topics. Respond with ONLY a Python list literal containing exactly 5 unquoted items separated by commas, formatted exactly like this example:
Python functions, Lists, Error handling, OOP, File handling
STRICT REQUIREMENTS: "
1. No quotation marks of any kind
2. No backslashes or escape characters
3. No counts or numbering
4. No additional text or commentary
5. Exactly 5 comma-separated
6. Each topic must be 2-4 words in lowercase/uppercase
If you include any quotes, backslashes, or other formatting, the response is wrong.\n\n
QUESTIONS: {"\n - ".join(all_questions)}
"""
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"
        })

        # Check if the RAG API responded successfully
        if response.status_code == 200:
            return jsonify({
                "allQuestions" : all_questions,
                "topQuestions" : response.json()["choices"][0]["message"]["content"].split(", ")
                }), 200
        else:
            # If the RAG API response was not successful, return the error response from RAG API
            return jsonify({"error": "Failed to get hot topics", "message": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500