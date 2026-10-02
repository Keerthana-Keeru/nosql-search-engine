from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import os
from dotenv import load_dotenv

# Load the .env file variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET_KEY")

# Fetch your MongoDB connection string from the .env file
CONNECTION_STRING = os.environ.get("CONNECTION_STRING")
client = MongoClient(CONNECTION_STRING)
db = client['search_engine_db']
users_collection = db['users']
courses_collection = db['courses']
feedback_collection = db['feedback']
documents_collection = db['documents']

@app.route('/')
def landing():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    all_courses = list(courses_collection.find({}))
    return render_template('landing.html', courses=all_courses)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        college = request.form.get('college')
        course = request.form.get('course')
        
        if users_collection.find_one({"email": email}):
            return "Email already registered! <a href='/login'>Login here</a>"
            
        hashed_password = generate_password_hash(password)
        user_data = {
            "name": name, "email": email, "password": hashed_password,
            "age": age, "college": college, "course": course,
            "role": 'student', "points": 0,
            "enrolled_courses": [],
            "completed_chapters": {}, 
            "completed_courses": []
        }
        users_collection.insert_one(user_data)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        selected_role = request.form.get('role_select')
        
        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            if user['role'] != selected_role:
                return f"Access Denied: Account type mismatch. <a href='/login'>Try again</a>"
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            session['name'] = user['name']
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('student_dashboard'))
        return "Invalid credentials. <a href='/login'>Try again</a>"
    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    all_users = list(users_collection.find({}, {'password': 0}))
    all_courses = list(courses_collection.find({}))
    all_feedback = list(feedback_collection.find({}))
    return render_template('admin_dashboard.html', users=all_users, courses=all_courses, feedback=all_feedback)

@app.route('/add_course', methods=['POST'])
def add_course():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    title = request.form.get('title')
    description = request.form.get('description')
    
    chapter_titles = request.form.getlist('chapter_titles[]')
    chapter_contents = request.form.getlist('chapter_contents[]')
    
    chapters = []
    for i in range(len(chapter_titles)):
        ch_num = i + 1
        ch_title = chapter_titles[i]
        ch_content = chapter_contents[i]
        
        quiz = []
        for q in range(1, 11):
            q_text = request.form.get(f"ch_{ch_num}_q_{q}")
            opts = [
                request.form.get(f"ch_{ch_num}_q_{q}_opt1"),
                request.form.get(f"ch_{ch_num}_q_{q}_opt2"),
                request.form.get(f"ch_{ch_num}_q_{q}_opt3"),
                request.form.get(f"ch_{ch_num}_q_{q}_opt4")
            ]
            ans = request.form.get(f"ch_{ch_num}_q_{q}_ans")
            if q_text and ans:
                quiz.append({
                    "question": q_text,
                    "options": opts,
                    "correct_answer": ans.strip()
                })
                
        chapters.append({
            "chapter_number": ch_num,
            "title": ch_title,
            "content": ch_content,
            "quiz": quiz
        })
        
    final_questions = []
    for j in range(1, 21):
        f_q = request.form.get(f"final_q_{j}")
        f_opts = [
            request.form.get(f"final_q_{j}_opt1"),
            request.form.get(f"final_q_{j}_opt2"),
            request.form.get(f"final_q_{j}_opt3"),
            request.form.get(f"final_q_{j}_opt4")
        ]
        f_ans = request.form.get(f"final_q_{j}_ans")
        if f_q and f_ans:
            final_questions.append({
                "question": f_q,
                "options": f_opts,
                "correct_answer": f_ans.strip()
            })
            
    course_data = {
        "title": title,
        "description": description,
        "chapters": chapters,
        "final_assessment": {
            "questions": final_questions
        }
    }
    courses_collection.insert_one(course_data)
    return redirect(url_for('admin_dashboard'))

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    all_courses = list(courses_collection.find({}))
    return render_template('student_dashboard.html', user=user, courses=all_courses)

@app.route('/enroll/<course_id>', methods=['POST'])
def enroll(course_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    enrolled = user.get('enrolled_courses', [])
    completed = user.get('completed_courses', [])
    
    # Prevent duplicate enrollment if already enrolled or completed
    if course_id not in enrolled and course_id not in completed:
        users_collection.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$addToSet": {"enrolled_courses": course_id}}
        )
        
    return redirect(url_for('student_dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
        
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        college = request.form.get('college')
        course = request.form.get('course')
        
        users_collection.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$set": {"name": name, "age": age, "college": college, "course": course}}
        )
        session['name'] = name # Update session name
        return redirect(url_for('student_dashboard'))
        
    return render_template('profile.html', user=user)

@app.route('/course/<course_id>')
def course_home(course_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    return redirect(url_for('view_chapter', course_id=course_id, chapter_num=1))

@app.route('/course/<course_id>/chapter/<int:chapter_num>', methods=['GET', 'POST'])
def view_chapter(course_id, chapter_num):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    course = courses_collection.find_one({"_id": ObjectId(course_id)})
    chapters = course.get('chapters', [])
    
    if chapter_num < 1 or chapter_num > len(chapters):
        return redirect(url_for('student_dashboard'))
        
    current_chapter = chapters[chapter_num - 1]
    
    if request.method == 'POST':
        score = 0
        quiz_length = len(current_chapter.get('quiz', []))
        for idx, q in enumerate(current_chapter.get('quiz', [])):
            user_ans = request.form.get(f"q_{idx}")
            db_ans = str(q.get('correct_answer', '')).strip()
            
            if user_ans and db_ans:
                clean_user = user_ans.strip().lower()
                clean_db = db_ans.strip().lower()
                
                if len(clean_db) == 1:
                    if clean_user.startswith(clean_db):
                        score += 1
                else:
                    if clean_user in clean_db or clean_db in clean_user:
                        score += 1
                
        # Passing threshold: at least 7 out of 10
        if score >= 7:
            # Ensure completed_chapters is a dictionary in MongoDB, not a legacy list
            user_doc = users_collection.find_one({"_id": ObjectId(session['user_id'])})
            if not isinstance(user_doc.get("completed_chapters"), dict):
                users_collection.update_one(
                    {"_id": ObjectId(session['user_id'])},
                    {"$set": {"completed_chapters": {}}}
                )

            users_collection.update_one(
                {"_id": ObjectId(session['user_id'])},
                {"$addToSet": {f"completed_chapters.{course_id}": chapter_num}}
            )
            if chapter_num < len(chapters):
                return redirect(url_for('view_chapter', course_id=course_id, chapter_num=chapter_num+1))
            else:
                return redirect(url_for('final_assessment', course_id=course_id))
        else:
            return render_template('chapter_view.html', course=course, chapter=current_chapter, chapter_num=chapter_num, error=f"Quiz failed! Score: {score}/10. You need at least 7/10 to pass. Try again.")

    return render_template('chapter_view.html', course=course, chapter=current_chapter, chapter_num=chapter_num)

@app.route('/final_assessment/<course_id>', methods=['GET', 'POST'])
def final_assessment(course_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
        
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    
    completed_chapters_field = user.get('completed_chapters', {})
    completed_chaps = completed_chapters_field.get(course_id, []) if isinstance(completed_chapters_field, dict) else []
    
    if len(completed_chaps) < 10:
        return redirect(url_for('student_dashboard'))
        
    course = courses_collection.find_one({"_id": ObjectId(course_id)})
    final_exam = course.get('final_assessment', {}).get('questions', [])
    
    if request.method == 'POST':
        score = 0
        total_q = len(final_exam)
        for idx, q in enumerate(final_exam):
            ans = request.form.get(f"final_q_{idx}")
            db_ans = str(q.get('correct_answer', '')).strip()
            
            if ans and db_ans:
                clean_ans = ans.strip().lower()
                clean_db = db_ans.strip().lower()
                
                if len(clean_db) == 1:
                    if clean_ans.startswith(clean_db):
                        score += 1
                else:
                    if clean_ans in clean_db or clean_db in clean_ans:
                        score += 1
                
        if score >= (total_q * 0.75): # 75% passing requirement for final certificate
            users_collection.update_one(
                {"_id": ObjectId(session['user_id'])},
                {
                    "$inc": {"points": 250},
                    "$addToSet": {"completed_courses": course_id}
                }
            )
            return redirect(url_for('certificate', course_id=course_id))
        else:
            return render_template('final_assessment.html', course=course, final_exam=final_exam, error=f"Final Exam not passed! Score: {score}/{total_q}. Required: 75%. Try again.")
            
    return render_template('final_assessment.html', course=course, final_exam=final_exam)

@app.route('/certificate/<course_id>')
def certificate(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    course = courses_collection.find_one({"_id": ObjectId(course_id)})
    if course_id not in user.get('completed_courses', []):
        return redirect(url_for('student_dashboard'))
    return render_template('certificate.html', user=user, course=course, date=datetime.date.today())

@app.route('/submit_feedback/<course_id>', methods=['POST'])
def submit_feedback(course_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    if course_id not in user.get('completed_courses', []):
        return "Feedback allowed only after successful course certification!"
    course = courses_collection.find_one({"_id": ObjectId(course_id)})
    feedback_data = {
        "user_id": session['user_id'], "user_name": session['name'],
        "course_title": course['title'], "feedback": request.form.get('feedback'),
        "rating": request.form.get('rating'), "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    feedback_collection.insert_one(feedback_data)
    return redirect(url_for('student_dashboard'))
@app.route('/fix_cert')
def fix_cert():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    enrolled = user.get('enrolled_courses', [])
    
    if enrolled:
        first_enrolled_course_id = enrolled[0]
        # Force add the first enrolled course into completed_courses for testing
        users_collection.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$addToSet": {"completed_courses": first_enrolled_course_id}}
        )
        return f"Successfully added course ID {first_enrolled_course_id} to completed courses! <a href='/student_dashboard'>Go back to Dashboard</a>"
    return "No enrolled courses found to mark as completed."

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

@app.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    query = request.args.get('q', '').strip()
    if not query: return jsonify([])
    try:
        documents = list(documents_collection.find({}, {'_id': 0}))
        if not documents: return jsonify([])
        doc_texts = [f"{doc.get('title', '')} {doc.get('content', '')}" for doc in documents]
        corpus = [query] + doc_texts
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        ranked_results = [{"title": documents[i]['title'], "content": documents[i]['content'], "score": round(float(s), 4)} for i, s in enumerate(scores) if s > 0.0]
        ranked_results.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(ranked_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)