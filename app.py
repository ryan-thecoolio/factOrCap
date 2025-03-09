from functools import wraps
from flask import Flask, render_template, redirect, url_for, session, request
import requests

app = Flask(__name__)
app.secret_key = "SECRET_KEY"
def get_question(query):
    api_key = "GOOGLE_API_KEY"
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    search_query = query
    params = {
        "query": search_query,
        "languageCode": "en",
        "pageSize": 10,
        "maxAgeDays": 365,
        "key": api_key
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        filtered = []
        for item in data.get('claims', []):  # Safely access 'claims'
            if isinstance(item, dict):  # Ensure 'item' is a dictionary
                if 'claimReview' in item and isinstance(item['claimReview'], list):
                    if item['claimReview'][0].get('textualRating') in ['True', 'False']:
                        filtered.append(item)
        return filtered
    else:
        print(f"Error fetching data: {r.status_code} {r.text}")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def clear_session():
    mylist = ['current_question','user','score','topic']
    for i in mylist:
        session.pop(i,None)
    return

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['username']
        session['current_question'] = 0
        session['score'] = 0
        return redirect(url_for('user'))
    if 'user' in session:
        return redirect(url_for('user'))
    return render_template ('login.html')

@app.route('/user', methods=['GET','POST'])
@login_required
def user():
    user = session['user']
    if request.method == 'POST':
        topic = request.form['topic']
        if 'topic' not in session:
            session['topic'] = get_question(topic)
        return redirect(url_for('quiz'))
    return render_template('index.html',user=user)

@app.route('/quiz', methods=['GET','POST'])
@login_required
def quiz():
    data = session['topic']
    print(data)
    if request.method == 'POST':
        user_answer = request.form.get('button_value')  
        correct_answer = data[session['current_question']]['claimReview'][0]['textualRating'].lower()
        if user_answer:
            if user_answer == correct_answer:
                session['score'] += 1
                print(f"My Answer - {user_answer}")
                print(f"Actual Answer - {correct_answer}")
                print(f"Current Question Index - {session['current_question']}")
            session['current_question'] += 1
        if session['current_question'] >= len(data):
            return redirect(url_for('result'))
        else:
            print('No answer')
    print(f"Score: {session['score']}")
    print(f"Current Question Index: {session['current_question']}")
    return render_template('quiz.html',data=data)

@app.route('/result')
@login_required
def result():
    total = len(session['topic'])
    score=session['score']
    clear_session()
    return render_template('result.html',score=score,total=total)

@app.route('/logout')
def logout():
    clear_session()
    return redirect(url_for('index'))

if __name__ in '__main__':
    app.run(debug=True)