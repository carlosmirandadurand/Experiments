
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash


###########################################################################
# Application Objects
###########################################################################


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_basic_app.db'
app.config['SECRET_KEY'] = os.environ.get('FLASK_BASIC_APP_SECRET_KEY')

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


###########################################################################
# Database
###########################################################################

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    question = db.Column(db.Text)

    def __init__(self, name, email, question):
        self.name = name
        self.email = email
        self.question = question

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, username, password, full_name, email):
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email


###########################################################################
# APIs
###########################################################################

def start_process_new_question(name, email, question):
    # Placeholder function for processing new question (implement as needed)
    pass

def get_process_status_for_question():
    # Placeholder function for getting process status for a question (implement as needed)
    pass


###########################################################################
# Routes
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
                session['name'] = user.full_name
                session['email'] = user.email
                return redirect(url_for('form_question'))
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        email = request.form['email']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, full_name=full_name, email=email)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('form_question'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('form_question'))

@app.route('/form_question', methods=['GET', 'POST'])
@login_required
def form_question():
    name = session.get('name', '')
    email = session.get('email', '')
    print("form_question: name:", name, "email:", email, "method:", request.method)

    if request.method == 'POST':
        question = request.form['question']
        new_question = Question(name, email, question)
        db.session.add(new_question)
        db.session.commit()
        start_process_new_question(name, email, question)  
        return redirect(url_for('form_answer'))
    return render_template('form_question.html', name=name, email=email)

@app.route('/form_answer', methods=['GET', 'POST'])
@login_required
def form_answer():
    name = session.get('name', '')
    if request.method == 'POST':
        button = request.form['button']
        if button == 'New Question':
            return redirect(url_for('form_question'))
        elif button == 'Check Status':
            get_process_status_for_question()
            # Perform appropriate action for checking status (implement as needed)
    return render_template('form_answer.html')


###########################################################################
# Execute
###########################################################################

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
