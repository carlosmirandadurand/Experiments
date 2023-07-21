
import os
import requests
import time

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

import json
import openai

from dotenv import load_dotenv


###########################################################################
# Application Objects
###########################################################################

# Load environment variables
load_dotenv()


# Initialize web application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_basic_app.db'
app.config['SECRET_KEY'] = os.getenv('flask_basic_app_secret_key')

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Connect to OpenAI 
openai.organization = os.getenv('openai_organization_id')
openai.api_key = os.getenv('openai_organization_key')
openai_model = 'gpt-3.5-turbo' 



###########################################################################
# Database
###########################################################################

class Question(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer)
    user_email  = db.Column(db.String(50))
    question    = db.Column(db.Text)
    answer      = db.Column(db.Text)

    def __init__(self, user_id, user_email, question):
        self.user_id    = user_id
        self.user_email = user_email
        self.question   = question

    def set_answer(self, answer):
        self.answer = answer
        db.session.commit()


class User(UserMixin, db.Model):
    id         = db.Column(db.Integer    , primary_key=True)
    username   = db.Column(db.String(50) , nullable=False, unique=True)
    password   = db.Column(db.String(255), nullable=False)
    full_name  = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, username, password, full_name, user_email):
        self.username   = username
        self.password   = password
        self.full_name  = full_name
        self.user_email = user_email



###########################################################################
# APIs
###########################################################################

def chat_gpt_basic_call (model, prompt):

    if model is None:
        return prompt # For testing 
    
    try:
        completion = openai.ChatCompletion.create(
            model = model,
            temperature = 0.1,
            n = 1,
            messages=[
                {"role": "user", "content": prompt},
            ])
        
        response = completion['choices'][0]['message']['content']
        response_attributes = { 
            'id':                completion['id'],
            'response_ms':       completion.response_ms,
            'model':             completion['model'],
            'prompt_tokens':     completion['usage']['prompt_tokens'],
            'completion_tokens': completion['usage']['completion_tokens'],
            'total_tokens':      completion['usage']['total_tokens'],
            }    

    except Exception as err:
        response = f"Unexpected Error: {err=}"
        response_attributes = {}

    return (response, response_attributes)



def start_process_new_question(question_id, question):

    prompt = question

    response, response_attributes = chat_gpt_basic_call (openai_model, prompt)

    return (response, response_attributes)




###########################################################################
# Authentication / Registration Routes
###########################################################################


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                session['user_id'] = user.id
                return redirect(url_for('form_question'))
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username   = request.form['username']
        password   = request.form['password']
        full_name  = request.form['full_name']
        user_email = request.form['email']
    
        try:
            new_user = User(username=username, password=generate_password_hash(password), full_name=full_name, user_email=user_email)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            session['user_id'] = new_user.id
            return redirect(url_for('form_question'))

        except IntegrityError as e:
            db.session.rollback()
            error_message = "Username or email already exists. Please choose a different one."
            return render_template('register.html', error_message=error_message)
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



###########################################################################
# Application Routes
###########################################################################


@app.route('/')
def index():
    return redirect(url_for('form_question'))


@app.route('/form_question', methods=['GET', 'POST'])
@login_required
def form_question():

    # Identify the user
    user_id = session.get('user_id', '')
    user = User.query.filter_by(id=user_id).first()
    if user:
        name = user.full_name
        user_email = user.user_email
    else:
        return redirect(url_for('logout'))

    # Process the submited form
    if request.method == 'POST':
        question = request.form['question']
        new_question = Question(user_id, user_email, question)
        db.session.add(new_question)
        db.session.commit()
        session['question_id'] = new_question.question_id
        response, response_attributes = start_process_new_question(new_question.question_id, question)  
        new_question.set_answer(response)
        return render_template('form_answer.html', name=name, question=question, response=response)
    
    # Load the form 
    return render_template('form_question.html', name=name, email=user_email)


@app.route('/form_answer', methods=['GET', 'POST'])
@login_required
def form_answer():
    
    # Identify the user
    user_id = session.get('user_id', '')
    user = User.query.filter_by(id=user_id).first()
    if user:
        name = user.full_name
        user_email = user.user_email
    else:
        return redirect(url_for('logout'))

    # Identify question
    question_id = session.get('question_id', '')

    # Process the submited form
    if request.method == 'POST':
        button = request.form['button']
        if button == 'New Question':
            return redirect(url_for('form_question'))
        elif button == 'List Questions':
            return redirect(url_for('report_questions'))
        elif button == 'Logout':
            return redirect(url_for('logout'))
    
    # Load the form 
    return render_template('form_answer.html')


@app.route('/report_questions', methods=['GET'])
@login_required
def report_questions():
    
    # Identify the user
    user_id = session.get('user_id', '')
    user = User.query.filter_by(id=user_id).first()
    if user:
        name = user.full_name
        user_email = user.user_email
    else:
        return redirect(url_for('logout'))
    
    # Pull and show all the questions
    rows = Question.query.all()
    column_names = Question.__mapper__.columns.keys()
    return render_template('report_questions.html', rows=rows, column_names=column_names)



###########################################################################
# Execute
###########################################################################

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
