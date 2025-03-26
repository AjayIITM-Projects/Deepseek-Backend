from api.models import User, Course, VideoTranscript, Announcement, Week, Module, TestCase, Question, ChatHistory  # Import models
from datetime import datetime
import re
from youtube_transcript_api import YouTubeTranscriptApi

# Helper function to extract video ID from YouTube URL
def extract_video_id(video_url):
    """
    Extracts the video ID from a YouTube URL.
    Supports various YouTube URL formats.
    """
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, video_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

def fetch_and_save_transcripts(video_modules):
    """
    Fetches transcripts for a list of video modules and saves them in the database.
    Skips saving if a transcript for the video already exists.
    """
    for module in video_modules:
        try:
            # Extract video ID from the URL
            video_id = extract_video_id(module.url)
            
            # Check if a transcript for this video already exists
            existing_transcript = VideoTranscript.objects(videoID=video_id).first()
            if existing_transcript:
                print(f"Transcript already exists for video URL: {module.url} (Video ID: {video_id})")
                continue  # Skip fetching and saving
            
            # Fetch transcript using YouTubeTranscriptApi
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Save the transcript in the database
            video_transcript = VideoTranscript(videoID=video_id, transcript=transcript)
            video_transcript.save()
            print(f"Transcript saved for video URL: {module.url} (Video ID: {video_id})")
        except Exception as e:
            print(f"Error fetching transcript for video URL {module.url}: {str(e)}")

            
def seed_database():
    from api.app import app, bcrypt
    with app.app_context():
        print("Seeding database with dummy data...")

        # Clear existing data
        User.objects.delete()
        Course.objects.delete()
        Announcement.objects.delete()
        Week.objects.delete()
        Module.objects.delete()

        # # Create a sample user
        # hashed_password = bcrypt.generate_password_hash("password123").decode('utf-8')
        # user1 = User(
        #     role="admin",
        #     email="admin@example.com",
        #     name="Admin User",
        #     profilePictureUrl="DP:)"
        # )
        # user1.save()

        # user2 = User(
        #     role="student",
        #     email="student@example.com",
        #     name="Student User",
        #     profilePictureUrl="DP:)"
        # )
        # user2.save()

        # user3 = User(
        #     role="faculty",
        #     email="faculty@example.com",
        #     name="Faculty User",
        #     profilePictureUrl="DP:)"
        # )
        # user3.save()



        # Create Course 1: MLF (Machine Learning Fundamentals)
        course1 = Course(
            name="Machine Learning Fundamentals (MLF)",
            description="Learn the fundamentals of Machine Learning, including regression, classification, and dimensionality reduction.",
            startDate=datetime(2025, 2, 1),
            endDate=datetime(2025, 6, 1)
        )
        course1.save()

        # Create Course 2: PDSA (Problem Solving and Data Structures Algorithms)
        course2 = Course(
            name="Problem Solving and Data Structures Algorithms (PDSA)",
            description="Learn problem-solving techniques and data structures algorithms, including sorting, searching, and binary search.",
            startDate=datetime(2025, 2, 1),
            endDate=datetime(2025, 6, 1)
        )
        course2.save()

        # =============================================
        # MLF Course Announcements
        # =============================================

        # Welcome announcement - Jan 23
        Announcement(
            course=course1,
            message="Welcome to Machine Learning Fundamentals (MLF)! We're excited to have you in this course.",
            date=datetime(2025, 1, 23, 9, 0)
        ).save()

        # Week -1 Released - Jan 23
        Announcement(
            course=course1,
            message="Week -1: Course Orientation materials are now available. Please review them before Week 1 begins.",
            date=datetime(2025, 1, 23, 10, 0)
        ).save()

        # Week 1 Released - Jan 23
        Announcement(
            course=course1,
            message="Week 1: Introduction to Machine Learning materials are now available!",
            date=datetime(2025, 1, 23, 11, 0)
        ).save()

        # Week 1 Assignment Due Reminder - Feb 2 (10 days after Week 1 release)
        Announcement(
            course=course1,
            message="REMINDER: Week 1 assignments are due tomorrow (Feb 3)!",
            date=datetime(2025, 2, 2, 18, 0)
        ).save()

        # Week 2 Released - Jan 30 (7 days after Week 1)
        Announcement(
            course=course1,
            message="Week 2: Continuity, Differentiability, and Linear Approximation materials are now available!",
            date=datetime(2025, 1, 30, 9, 0)
        ).save()

        # Week 2 Assignment Due Reminder - Feb 9
        Announcement(
            course=course1,
            message="REMINDER: Week 2 assignments are due tomorrow (Feb 10)!",
            date=datetime(2025, 2, 9, 18, 0)
        ).save()

        # Week 3 Released - Feb 6
        Announcement(
            course=course1,
            message="Week 3: Multivariate Calculus materials are now available!",
            date=datetime(2025, 2, 6, 9, 0)
        ).save()

        # Week 3 Assignment Due Reminder - Feb 16
        Announcement(
            course=course1,
            message="REMINDER: Week 3 assignments are due tomorrow (Feb 17)!",
            date=datetime(2025, 2, 16, 18, 0)
        ).save()

        # Week 4 Released - Feb 13
        Announcement(
            course=course1,
            message="Week 4: Probability Basics materials are now available!",
            date=datetime(2025, 2, 13, 9, 0)
        ).save()

        # Week 4 Assignment Due Reminder - Feb 23
        Announcement(
            course=course1,
            message="REMINDER: Week 4 assignments are due tomorrow (Feb 24)!",
            date=datetime(2025, 2, 23, 18, 0)
        ).save()

        # Week 5 Released - Feb 20
        Announcement(
            course=course1,
            message="Week 5: Linear Regression materials are now available!",
            date=datetime(2025, 2, 20, 9, 0)
        ).save()

        # Week 5 Assignment Due Reminder - Mar 2
        Announcement(
            course=course1,
            message="REMINDER: Week 5 assignments are due tomorrow (Mar 3)!",
            date=datetime(2025, 3, 2, 18, 0)
        ).save()

        # Week 6 Released - Feb 27
        Announcement(
            course=course1,
            message="Week 6: Logistic Regression materials are now available!",
            date=datetime(2025, 2, 27, 9, 0)
        ).save()

        # Week 6 Assignment Due Reminder - Mar 9
        Announcement(
            course=course1,
            message="FINAL REMINDER: Week 6 assignments are due tomorrow (Mar 10)! This is your last submission for the course.",
            date=datetime(2025, 3, 9, 18, 0)
        ).save()

        # =============================================
        # PDSA Course Announcements
        # =============================================

        # Welcome announcement - Jan 23
        Announcement(
            course=course2,
            message="Welcome to Problem Solving and Data Structures Algorithms (PDSA)! Let's build strong coding fundamentals together.",
            date=datetime(2025, 1, 23, 9, 30)
        ).save()

        # Week -1 Released - Jan 23
        Announcement(
            course=course2,
            message="Week -1: Course Orientation materials are now available. Please review the syllabus and setup your development environment.",
            date=datetime(2025, 1, 23, 10, 30)
        ).save()

        # Week 1 Released - Jan 23
        Announcement(
            course=course2,
            message="Week 1: Python Recap and Sorting Algorithms materials are now available!",
            date=datetime(2025, 1, 23, 11, 30)
        ).save()

        # Week 1 Assignment Due Reminder - Feb 2
        Announcement(
            course=course2,
            message="REMINDER: Week 1 coding assignments are due tomorrow (Feb 3)! Don't forget to test your solutions thoroughly.",
            date=datetime(2025, 2, 2, 18, 30)
        ).save()

        # Week 2 Released - Jan 30
        Announcement(
            course=course2,
            message="Week 2: Searching and Sorting Algorithms materials are now available!",
            date=datetime(2025, 1, 30, 9, 30)
        ).save()

        # Week 2 Assignment Due Reminder - Feb 9
        Announcement(
            course=course2,
            message="REMINDER: Week 2 assignments (including Binary Search implementation) are due tomorrow (Feb 10)!",
            date=datetime(2025, 2, 9, 18, 30)
        ).save()

        # Week 3 Released - Feb 6
        Announcement(
            course=course2,
            message="Week 3: Trees and Graphs materials are now available! This is an important week for interview preparation.",
            date=datetime(2025, 2, 6, 9, 30)
        ).save()

        # Week 3 Assignment Due Reminder - Feb 16
        Announcement(
            course=course2,
            message="REMINDER: Week 3 assignments (including BFS implementation) are due tomorrow (Feb 17)!",
            date=datetime(2025, 2, 16, 18, 30)
        ).save()

        # Week 4 Released - Feb 13
        Announcement(
            course=course2,
            message="Week 4: Dynamic Programming materials are now available! Start early as these concepts take time to master.",
            date=datetime(2025, 2, 13, 9, 30)
        ).save()

        # Week 4 Assignment Due Reminder - Feb 23
        Announcement(
            course=course2,
            message="REMINDER: Week 4 DP assignments are due tomorrow (Feb 24)! Don't procrastinate on these challenging problems.",
            date=datetime(2025, 2, 23, 18, 30)
        ).save()

        # Week 5 Released - Feb 20
        Announcement(
            course=course2,
            message="Week 5: Greedy Algorithms materials are now available!",
            date=datetime(2025, 2, 20, 9, 30)
        ).save()

        # Week 5 Assignment Due Reminder - Mar 2
        Announcement(
            course=course2,
            message="REMINDER: Week 5 assignments (Activity Selection Problem) are due tomorrow (Mar 3)!",
            date=datetime(2025, 3, 2, 18, 30)
        ).save()

        # Week 6 Released - Feb 27
        Announcement(
            course=course2,
            message="Week 6: Advanced Topics materials are now available! This concludes our regular course content.",
            date=datetime(2025, 2, 27, 9, 30)
        ).save()

        # Week 6 Assignment Due Reminder - Mar 9
        Announcement(
            course=course2,
            message="FINAL REMINDER: Week 6 assignments are due tomorrow (Mar 10)! Submit all outstanding work before the deadline.",
            date=datetime(2025, 3, 9, 18, 30)
        ).save()

        # Create Week 1 for Course 1 (MLF)
        week1_mlf = Week(course=course1, title="Week 1: Introduction to Machine Learning", deadline=datetime(2025, 2, 10))
        week1_mlf.save()

        # Create Week 1 for Course 2 (PDSA)
        week1_pdsa = Week(course=course2, title="Week 1: Python Recap and Sorting Algorithms", deadline=datetime(2025, 2, 10))
        week1_pdsa.save()

        # Create modules for Week 1 of Course 1 (MLF)
        module1_mlf = Module(
            week=week1_mlf,
            title="1.1 – Supervised Learning: Regression - Video",
            type="video",
            url="https://www.youtube.com/embed/iVcrCdEaJ7A"
        ).save()

        module2_mlf = Module(
            week=week1_mlf,
            title="1.2 – Supervised Learning: Classification - Video",
            type="video",
            url="https://www.youtube.com/embed/QtOrjs0Fzzc"
        ).save()

        module3_mlf = Module(
            week=week1_mlf,
            title="1.3 – Unsupervised Learning: Dimensionality Reduction - Video",
            type="video",
            url="https://www.youtube.com/embed/EuNPsw9zA1k"
        ).save()

        # Practice Quiz for MLF
        module4_mlf = Module(
            week=week1_mlf,
            title="Practice Quiz",
            type="assignment",
            isGraded=False,
            questions=[
                Question(
                    question="Which of the following are examples of unsupervised learning problems?",
                    type="mcq",
                    options=[
                        "Grouping tweets based on topic similarity",
                        "Making clusters of cells having similar appearance under microscope.",
                        "Checking whether an email is spam or not.",
                        "Identify the gender of online customers based on buying behaviour."
                    ],
                    correctAnswer="Grouping tweets based on topic similarity",
                    hint="Unsupervised learning deals with finding hidden patterns or structures in data without labeled outputs."
                ),
                Question(
                    question="Which of the following is/are incorrect?",
                    type="mcq",
                    options=[
                        "1(2 ± even) = 1",
                        "1(10%3 = 0) = 0",
                        "1(0.5 ∉ ℝ) = 0",
                        "1(2 ∈ (2, 3, 4)) = 0"
                    ],
                    correctAnswer="1(2 ∈ (2, 3, 4)) = 0",
                    hint="Carefully analyze the logical expressions and remember that ℝ represents the set of real numbers."
                ),
                Question(
                    question="Which of the following functions corresponds to a classification model?",
                    type="mcq",
                    options=[
                        "f : ℝ^d → ℝ",
                        "f : ℝ^d → { +1, -1 }",
                        "f : ℝ^d → ℝ^d'"
                    ],
                    correctAnswer="f : ℝ^d → { +1, -1 }",
                    hint="Classification models output discrete categories rather than continuous values."
                )
            ]
        ).save()


        # Graded Quiz for MLF
        module5_mlf = Module(
            week=week1_mlf,
            title="Graded Quiz",
            type="assignment",
            isGraded=True,
            questions=[
                Question(
                    question="Which of the following may not be an appropriate choice of loss function for regression?",
                    type="mcq",
                    options=[
                        "1/n ∑(f(x_i) - y_i)^2",
                        "1/n ∑|f(x_i) - y_i|",
                        "1/n ∑1(f(x_i) ≠ y_i)"
                    ],
                    correctAnswer="1/n ∑1(f(x_i) ≠ y_i)",
                    hint="Regression models predict continuous values, so their loss functions should reflect the magnitude of errors rather than discrete classification errors."
                ),
                Question(
                    question="Identify which of the following requires use of classification technique.",
                    type="mcq",
                    options=[
                        "Predicting the amount of rainfall in May 2022 in North India based on precipitation data of the year 2021.",
                        "Predicting the price of a land based on its area and distance from the market.",
                        "Predicting whether an email is spam or not.",
                        "Predicting the number of Covid cases on a given day based on previous month data."
                    ],
                    correctAnswer="Predicting whether an email is spam or not.",
                    hint="Classification problems deal with categorizing inputs into discrete labels, while regression predicts continuous numerical values."
                )
            ]
        ).save()


        # Create modules for Week 1 of Course 2 (PDSA)
        module1_pdsa = Module(
            week=week1_pdsa,
            title="1.1 – Python Recap-1 - Video",
            type="video",
            url="https://www.youtube.com/embed/2W3BKOSg958"
        ).save()

        module2_pdsa = Module(
            week=week1_pdsa,
            title="1.2 – Python Recap-2 - Video",
            type="video",
            url="https://www.youtube.com/embed/q9rS_GFCtQg"
        ).save()

        module3_pdsa = Module(
            week=week1_pdsa,
            title="1.3 – Python Recap-3 - Video",
            type="video",
            url="https://www.youtube.com/embed/PBnhRTf00Z0"
        ).save()

        # Practice Quiz for PDSA
        module4_pdsa = Module(
            week=week1_pdsa,
            title="Practice Quiz",
            type="assignment",
            isGraded=False,
            questions=[
                Question(
                    question="Which of the following options will validate whether n is a perfect square or not?",
                    type="mcq",
                    options=[
                        "def h(n): return (n ** .5) == int(n ** .5)",
                        "def h(n): return (n ** .5) == int(n) **",
                        "def h(n): for i in range(1, n + 1): if i * i == n: return True return False",
                        "def h(n): for i in range(1, n + 1): if i * i > n: break elif i * i == n: return True return False"
                    ],
                    correctAnswer="def h(n): return (n ** .5) == int(n ** .5)",
                    hint="A perfect square is a number whose square root is an integer. Consider checking whether the square root of 'n' is equal to its integer conversion."
                )
            ]
        ).save()


        # Graded Programming for PDSA
        module5_pdsa = Module(
            week=week1_pdsa,
            title="Graded Programming: Goldbach's Conjecture",
            type="coding",
            language="Python",
            isGraded = True,
            description="Write a function to find prime pairs that sum to an even number.",
            hint = "Try breaking the problem into checking prime numbers and finding pairs.",
            codeTemplate="def prime(n):\n    if n < 2:\n        return False\n    for i in range(2, n//2 + 1):\n        if n % i == 0:\n            return False\n    return True\n\ndef Goldbach(n):\n    Res = []\n    for i in range((n//2) + 1):\n        if prime(i) == True:\n            if prime(n - i) == True:\n                Res.append((i, n - i))\n    return Res",
            testCases=[
                TestCase(inputData="12", expectedOutput="[(5, 7)]"),
                TestCase(inputData="26", expectedOutput="[(3, 23), (7, 19), (13, 13)]")
            ]
        ).save()

        
        # Create Week 2 for Course 1 (MLF)
        week2_mlf = Week(course=course1, title="Week 2: Continuity, Differentiability, and Linear Approximation", deadline=datetime(2025, 2, 17))
        week2_mlf.save()

        # Create modules for Week 2 of Course 1 (MLF)
        module1_week2_mlf = Module(
            week=week2_mlf,
            title="1.1 – Univariate Calculus: Continuity and Differentiability - Video",
            type="video",
            url="https://www.youtube.com/embed/yvaPORg2w9c"
        ).save()

        module2_week2_mlf = Module(
            week=week2_mlf,
            title="1.2 – Univariate Calculus: Derivatives and Linear Approximations - Video",
            type="video",
            url="https://www.youtube.com/embed/AG2fQvxEpbE"
        ).save()

        module3_week2_mlf = Module(
            week=week2_mlf,
            title="1.3 – Univariate Calculus:: Applications and Advanced Rules - Video",
            type="video",
            url="https://www.youtube.com/embed/En15LA59Fsw"
        ).save()

        module4_week2_mlf = Module(
            week=week2_mlf,
            title="Practice Quiz",
            type="assignment",
            isGraded=False,
            questions=[
                Question(
                    question="If U = [10, 100], A = [30, 50], and B = [50, 90], which of the following is/are false? (Consider all values to be integers)",
                    type="mcq",
                    options=[
                        "A^C = [10, 30] ∪ [50, 100]",
                        "A^C = [10, 30] ∪ (50, 100]",
                        "A ∪ B = [30, 90]",
                        "A ∩ B = ∅",
                        "A ∩ B = {50}",
                        "A^C ∩ B^C = [10, 30] ∪ [91, 100]"
                    ],
                    correctAnswer="A ∩ B = ∅",
                    hint="Carefully analyze the intersections and complements of sets. A ∩ B represents the common elements between A and B."
                ),
                Question(
                    question="Consider two 6-dimensional vectors x and y. Which of the following terms are equivalent? (i) x^T y, (ii) x y, (iii) ∑(x_i y_i)",
                    type="mcq",
                    options=[
                        "Only (i) and (ii)",
                        "Only (i) and (iii)",
                        "Only (ii) and (iii)",
                        "(i), (ii), and (iii)"
                    ],
                    correctAnswer="Only (i) and (iii)",
                    hint="The dot product of two vectors is computed by summing the element-wise product of their components."
                )
            ]
        ).save()


        module5_week2_mlf = Module(
            week=week2_mlf,
            title="Graded Quiz",
            type="assignment",
            isGraded=True,
            questions=[
                Question(
                    question="Which of the following functions is/are continuous?",
                    type="mcq",
                    options=[
                        "1/(x - 1)",
                        "(x^2 - 1)/x",
                        "sign(x - 2)",
                        "sin(x)"
                    ],
                    correctAnswer="sin(x)",
                    hint="A function is continuous if it has no abrupt jumps, breaks, or asymptotes in its domain."
                ),
                Question(
                    question="Regarding a d-dimensional vector x, which of the following is not equivalent to the rest?",
                    type="mcq",
                    options=[
                        "x^T x",
                        "||x||^2",
                        "∑(x_i^2)",
                        "x x^T"
                    ],
                    correctAnswer="x x^T",
                    hint="Think about the dimensions of the resulting matrices for each operation. Some represent scalars, while others result in matrices."
                )
            ]
        ).save()




        # Create Week 2 for Course 2 (PDSA)
        week2_pdsa = Week(course=course2, title="Week 2: Searching and Sorting Algorithms", deadline=datetime(2025, 2, 17))
        week2_pdsa.save()

        # Create modules for Week 2 of Course 2 (PDSA)
        module1_week2_pdsa = Module(
            week=week2_pdsa,
            title="2.1 – Searching in a List - Video",
            type="video",
            url="https://www.youtube.com/embed/nLHPNN_d85I"
        ).save()

        module2_week2_pdsa = Module(
            week=week2_pdsa,
            title="2.2 – Selection Sort - Video",
            type="video",
            url="https://www.youtube.com/embed/PzLW39b12Cc"
        ).save()

        module3_week2_pdsa = Module(
            week=week2_pdsa,
            title="2.3 – Insertion Sort - Video",
            type="video",
            url="https://www.youtube.com/embed/NEWwLaeFols"
        ).save()

        module4_week2_pdsa = Module(
            week=week2_pdsa,
            title="2.4 – Merge Sort - Video",
            type="video",
            url="https://www.youtube.com/embed/HBF0FNPJQeA"
        ).save()

        # Practice Quiz for Week 2 of PDSA
        module5_week2_pdsa = Module(
            week=week2_pdsa,
            title="Practice Quiz",
            type="assignment",
            isGraded=False,
            questions=[
                Question(
                    question="Which of the following options complete the missing lines in the binary search implementation?",
                    type="mcq",
                    options=[
                        "right = mid + 1 # line 13, left = mid - 1 # line 15",
                        "right = mid - 1 # line 13, left = mid + 1 # line 15",
                        "right = mid - left # line 13, left = mid + right # line 15",
                        "right = mid - right # line 13, left = mid + left # line 15"
                    ],
                    correctAnswer="right = mid - 1 # line 13, left = mid + 1 # line 15",
                    hint="Remember that in binary search, you reduce the search space by adjusting `left` or `right` based on the comparison with `mid`."
                )
            ]
        ).save()


        # Graded Quiz for Week 2 of PDSA
        module6_week2_pdsa = Module(
            week=week2_pdsa,
            title="Graded Quiz",
            type="assignment",
            isGraded=True,
            questions=[
                Question(
                    question="What is the value of I when the list [1, 2, 3, 6, 7, 8] becomes completely sorted for the first time using selection sort?",
                    type="mcq",
                    options=["1", "2", "3", "4"],
                    correctAnswer="3",
                    hint="In selection sort, the smallest element is placed in its correct position in each iteration. Count the swaps until the list is fully sorted."
                )
            ]
        ).save()


        module7_week2_pdsa = Module(
            week=week2_pdsa,
            title="Graded Programming: Binary Search",
            type="coding",
            language="Python",
            isGraded=True, 
            description="Write a Python function binarySearchIndexAndComparisons(L, k) that accepts a sorted list L and an integer k. The function should return a tuple (True/False, numComparisons) indicating whether k is in L and the number of comparisons made.",
            codeTemplate="def binarySearchIndexAndComparisons(L, k):\n    s = len(L)\n    if s < 1:\n        return (False, 0)\n    left = 0\n    right = s - 1\n    c = 0\n    while left <= right:\n        mid = (left + right) // 2\n        c += 1\n        if k == L[mid]:\n            return (True, c)\n        elif k < L[mid]:\n            right = mid - 1\n        else:\n            left = mid + 1\n    return (False, c)",
            testCases=[
                TestCase(inputData="[2, 6, 8, 11, 17, 23, 33, 44, 46, 50, 65], 11", expectedOutput="(True, 3)"),
                TestCase(inputData="[2, 6, 8, 11, 17, 23, 33, 44, 46, 50, 65], 100", expectedOutput="(False, 4)")
            ],
            hint="Binary search works by dividing the list in half iteratively. Count the number of comparisons needed to determine if the target element exists."
        ).save()

        module8_week2_pdsa = Module(
            week=week2_pdsa,
            title="Graded Programming: Find Largest in Rotated Sorted List",
            type="coding",
            language="Python",
            isGraded=True,
            description="Write a Python function findLargest(L) that accepts a list L of unique numbers, which is sorted and rotated n times (n is unknown). The function should return the largest number in the list. Try to give an O(log n) solution.",
            codeTemplate="""def findLargest(L):
                left = 0
                s = len(L)
                right = s - 1

                # If the list has only one element, return that element
                if s == 1:
                    return L[0]

                while left <= right:
                    mid = (left + right) // 2

                    # If mid is at the last index, the next element to compare is at index 0
                    if mid == s - 1:
                        nextToMid = 0
                    else:
                        nextToMid = mid + 1

                    # If the mid element is greater than the next element, it is the largest
                    if L[mid] > L[nextToMid]:
                        return L[mid]
                    # If the mid element is less than the first element, the largest is in the left half
                    elif L[mid] < L[0]:
                        right = mid - 1
                    # Otherwise, the largest is in the right half
                    else:
                        left = mid + 1""",
            testCases=[
                TestCase(inputData="[7, 8, 2, 4, 5]", expectedOutput="8"),
                TestCase(inputData="[2, 4, 5, 7, 9]", expectedOutput="9"),
                TestCase(inputData="[10, 20, 30, 40, 5]", expectedOutput="40"),
                TestCase(inputData="[3, 4, 5, 1, 2]", expectedOutput="5"),
                TestCase(inputData="[6]", expectedOutput="6")
            ],
            hint="This problem can be solved in O(log n) using a binary search approach. Compare the middle element with the first or last element to determine which half to search next."
        ).save()


        # # -----------------------------
        # # Seeding ChatHistory
        # # -----------------------------
        # chat1 = ChatHistory(
        #     sessionId="session123",
        #     user=user1,
        #     query="How do I define a function in Python?",
        #     response="Use the def keyword followed by the function name and parameters."
        # ).save()


        # # -----------------------------
        # # Seeding Code Submissions
        # # -----------------------------
        # code_submission1 = CodeSubmission(
        #     user=user1,
        #     question=None,  # Placeholder since Question is embedded
        #     submittedCode="def add(a, b): return a + b",
        #     output="5",
        #     isCorrect=True
        # ).save()




        # =============================================
        # MLF Course Weeks 3-6
        # =============================================

        # Week 3 MLF: Multivariate Calculus
        week3_mlf = Week(course=course1, title="Week 3: Multivariate Calculus", deadline=datetime(2025, 2, 24)).save()
        Module(week=week3_mlf, title="3.1 – Partial Derivatives", type="video", url="https://www.youtube.com/embed/JAf_aSIJryg").save()
        Module(week=week3_mlf, title="3.2 – Gradient and Directional Derivatives", type="video", url="https://www.youtube.com/embed/tDPp5uWSIiU").save()
        Module(week=week3_mlf, title="3.3 – Hessian Matrix", type="video", url="https://www.youtube.com/embed/q4pgxZfW0a4").save()
        Module(week=week3_mlf, title="Practice Quiz", type="assignment", isGraded=False, questions=[
            Question(question="What does the gradient vector represent?", type="mcq",
                    options=["Direction of steepest ascent", "Direction of steepest descent", "Both A and B", "Neither"],
                    correctAnswer="Direction of steepest ascent")
        ]).save()

        # Week 4 MLF: Probability Basics
        week4_mlf = Week(course=course1, title="Week 4: Probability Basics", deadline=datetime(2025, 3, 3)).save()
        Module(week=week4_mlf, title="4.1 – Random Variables", type="video", url="https://www.youtube.com/embed/3v9w79NhsfI").save()
        Module(week=week4_mlf, title="4.2 – Probability Distributions", type="video", url="https://www.youtube.com/embed/OprNqnHsVIA").save()
        Module(week=week4_mlf, title="4.3 – Bayes Theorem", type="video", url="https://www.youtube.com/embed/HZGCoVF3YvM").save()
        Module(week=week4_mlf, title="Graded Quiz", type="assignment", isGraded=True, questions=[
            Question(question="Which distribution is used for modeling binary outcomes?", type="mcq",
                    options=["Normal", "Poisson", "Bernoulli", "Uniform"],
                    correctAnswer="Bernoulli")
        ]).save()

        # Week 5 MLF: Linear Regression
        week5_mlf = Week(course=course1, title="Week 5: Linear Regression", deadline=datetime(2025, 3, 10)).save()
        Module(week=week5_mlf, title="5.1 – Simple Linear Regression", type="video", url="https://www.youtube.com/embed/nk2CQITm_eo").save()
        Module(week=week5_mlf, title="5.2 – Multiple Linear Regression", type="video", url="https://www.youtube.com/embed/zITIFTsivN8").save()
        Module(week=week5_mlf, title="5.3 – Regularization", type="video", url="https://www.youtube.com/embed/NGf0voTMlcs").save()
        Module(week=week5_mlf, title="Graded Programming", type="coding", language="Python",
              description="Implement linear regression from scratch",
              testCases=[TestCase(inputData="[[1,2],[3,4]]", expectedOutput="[1.0, 1.0]")]).save()

        # Week 6 MLF: Logistic Regression
        week6_mlf = Week(course=course1, title="Week 6: Logistic Regression", deadline=datetime(2025, 3, 17)).save()
        Module(week=week6_mlf, title="6.1 – Classification Problems", type="video", url="https://www.youtube.com/embed/yIYKR4sgzI8").save()
        Module(week=week6_mlf, title="6.2 – Logistic Function", type="video", url="https://www.youtube.com/embed/BfKanl1aSG0").save()
        Module(week=week6_mlf, title="6.3 – Model Evaluation", type="video", url="https://www.youtube.com/embed/OAl6eAyP-yo").save()
        Module(week=week6_mlf, title="Final Quiz", type="assignment", isGraded=True, questions=[
            Question(question="What is the range of logistic function?", type="mcq",
                    options=["(0,1)", "(-∞,∞)", "[0,1]", "(0,1]"],
                    correctAnswer="(0,1)")
        ]).save()





        # =============================================
        # PDSA Course Weeks 3-6
        # =============================================

        # Week 3 PDSA: Trees and Graphs
        week3_pdsa = Week(course=course2, title="Week 3: Trees and Graphs", deadline=datetime(2025, 2, 24)).save()
        Module(week=week3_pdsa, title="3.1 – Binary Trees", type="video", url="https://www.youtube.com/embed/fAAZixBzIAI").save()
        Module(week=week3_pdsa, title="3.2 – Graph Representations", type="video", url="https://www.youtube.com/embed/09_LlHjoEiY").save()
        Module(week=week3_pdsa, title="3.3 – Tree Traversals", type="video", url="https://www.youtube.com/embed/WLvU5EQVZqY").save()
        Module(week=week3_pdsa, title="Graded Programming", type="coding", language="Python",
              description="Implement BFS for a graph",
              testCases=[TestCase(inputData="adjacency_list", expectedOutput="[0,1,2,3]")]).save()

        # Week 4 PDSA: Dynamic Programming
        week4_pdsa = Week(course=course2, title="Week 4: Dynamic Programming", deadline=datetime(2025, 3, 3)).save()
        Module(week=week4_pdsa, title="4.1 – DP Introduction", type="video", url="https://www.youtube.com/embed/oBt53YbR9Kk").save()
        Module(week=week4_pdsa, title="4.2 – Fibonacci Sequence", type="video", url="https://www.youtube.com/embed/vYquumk4nWw").save()
        Module(week=week4_pdsa, title="4.3 – Knapsack Problem", type="video", url="https://www.youtube.com/embed/8LusJS5-AGo").save()
        Module(week=week4_pdsa, title="Practice Quiz", type="assignment", isGraded=False, questions=[
            Question(question="What is the time complexity of naive Fibonacci?", type="mcq",
                    options=["O(n)", "O(2^n)", "O(n^2)", "O(log n)"],
                    correctAnswer="O(2^n)")
        ]).save()

        # Week 5 PDSA: Greedy Algorithms
        week5_pdsa = Week(course=course2, title="Week 5: Greedy Algorithms", deadline=datetime(2025, 3, 10)).save()
        Module(week=week5_pdsa, title="5.1 – Greedy Paradigm", type="video", url="https://www.youtube.com/embed/ARvQcqJ_-NY").save()
        Module(week=week5_pdsa, title="5.2 – Activity Selection", type="video", url="https://www.youtube.com/embed/poWB2UCuozA").save()
        Module(week=week5_pdsa, title="5.3 – Huffman Coding", type="video", url="https://www.youtube.com/embed/co4_ahEDCho").save()
        Module(week=week5_pdsa, title="Graded Programming", type="coding", language="Python",
              description="Implement activity selection problem",
              testCases=[TestCase(inputData="activities", expectedOutput="[1,3,5]")]).save()

        # Week 6 PDSA: Advanced Topics
        week6_pdsa = Week(course=course2, title="Week 6: Advanced Topics", deadline=datetime(2025, 3, 17)).save()
        Module(week=week6_pdsa, title="6.1 – Tries", type="video", url="https://www.youtube.com/embed/AXjmTQ8LEoI").save()
        Module(week=week6_pdsa, title="6.2 – Segment Trees", type="video", url="https://www.youtube.com/embed/2bSS8rtFym4").save()
        Module(week=week6_pdsa, title="6.3 – Final Review", type="video", url="https://www.youtube.com/embed/p1EnSvS3urU").save()
        Module(week=week6_pdsa, title="Final Exam", type="assignment", isGraded=True, questions=[
            Question(question="Which data structure is best for prefix searches?", type="mcq",
                    options=["Hash Table", "Binary Tree", "Trie", "Linked List"],
                    correctAnswer="Trie")
        ]).save()


        # Fetch all video-type modules and dynamically fetch their transcripts
        video_modules = Module.objects(type="video")
        fetch_and_save_transcripts(video_modules)

        print("Database seeded successfully!")