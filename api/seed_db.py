from api.models import User, Course, Announcement, Week, Module, TestCase, Question  # Import models
from datetime import datetime

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

        # Create a sample user
        hashed_password = bcrypt.generate_password_hash("password123").decode('utf-8')
        user1 = User(
            role="admin",
            email="admin@example.com",
            name="Admin User"
        )
        user1.save()

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

        # Create an announcement for Course 1 (MLF)
        announcement1 = Announcement(course=course1, message="Welcome to the Machine Learning Fundamentals course!")
        announcement1.save()

        # Create an announcement for Course 2 (PDSA)
        announcement2 = Announcement(course=course2, message="Welcome to the Problem Solving and Data Structures Algorithms course!")
        announcement2.save()

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
                    correctAnswer="Grouping tweets based on topic similarity"
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
                    correctAnswer="1(2 ∈ (2, 3, 4)) = 0"
                ),
                Question(
                    question="Which of the following functions corresponds to a classification model?",
                    type="mcq",
                    options=[
                        "f : ℝ^d → ℝ",
                        "f : ℝ^d → { +1, -1 }",
                        "f : ℝ^d → ℝ^d'"
                    ],
                    correctAnswer="f : ℝ^d → { +1, -1 }"
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
                    correctAnswer="1/n ∑1(f(x_i) ≠ y_i)"
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
                    correctAnswer="Predicting whether an email is spam or not."
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
                    correctAnswer="def h(n): return (n ** .5) == int(n ** .5)"
                )
            ]
        ).save()

        # Graded Programming for PDSA
        module5_pdsa = Module(
            week=week1_pdsa,
            title="Graded Programming: Goldbach's Conjecture",
            type="coding",
            language="Python",
            description="Write a function to find prime pairs that sum to an even number.",
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

        # Practice Quiz for Week 2 of MLF
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
                    correctAnswer="A ∩ B = ∅"
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
                    correctAnswer="Only (i) and (iii)"
                )
            ]
        ).save()

        # Graded Quiz for Week 2 of MLF
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
                    correctAnswer="sin(x)"
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
                    correctAnswer="x x^T"
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
                    correctAnswer="right = mid - 1 # line 13, left = mid + 1 # line 15"
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
                    correctAnswer="3"
                )
            ]
        ).save()

        # Graded Programming for Week 2 of PDSA
        module7_week2_pdsa = Module(
            week=week2_pdsa,
            title="Graded Programming: Binary Search",
            type="coding",
            language="Python",
            description="Write a Python function binarySearchIndexAndComparisons(L, k) that accepts a sorted list L and an integer k. The function should return a tuple (True/False, numComparisons) indicating whether k is in L and the number of comparisons made.",
            codeTemplate="def binarySearchIndexAndComparisons(L, k):\n    s = len(L)\n    if s < 1:\n        return (False, 0)\n    left = 0\n    right = s - 1\n    c = 0\n    while left <= right:\n        mid = (left + right) // 2\n        c += 1\n        if k == L[mid]:\n            return (True, c)\n        elif k < L[mid]:\n            right = mid - 1\n        else:\n            left = mid + 1\n    return (False, c)",
            testCases=[
                TestCase(inputData="[2, 6, 8, 11, 17, 23, 33, 44, 46, 50, 65], 11", expectedOutput="(True, 3)"),
                TestCase(inputData="[2, 6, 8, 11, 17, 23, 33, 44, 46, 50, 65], 100", expectedOutput="(False, 4)")
            ]
        ).save()

        module8_week2_pdsa = Module(
            week=week2_pdsa,
            title="Graded Programming: Find Largest in Rotated Sorted List",
            type="coding",
            language="Python",
            description="Write a Python function findLargest(L) that accepts a list L of unique numbers, which is sorted and rotated n times (n is unknown). The function should return the largest number in the list. Try to give an O(log n) solution. Hint: One of the O(log n) solutions can be implemented using binary search and using 'first or last' element to know, the direction of searching further.",
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
            ]
        ).save()

        print("Database seeded successfully!")