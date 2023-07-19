from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questions.db'
db = SQLAlchemy(app)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    question = db.Column(db.Text)

    def __init__(self, name, email, question):
        self.name = name
        self.email = email
        self.question = question

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        question = request.form['question']
        new_question = Question(name, email, question)
        db.session.add(new_question)
        db.session.commit()
        start_process_new_question(name, email, question)  # Call new function
        return redirect(url_for('thankyou', name=name))
    return render_template('form.html')

@app.route('/thankyou', methods=['GET', 'POST'])
def thankyou():
    name = request.args.get('name')
    if request.method == 'POST':
        button = request.form['button']
        if button == 'New Question':
            return redirect(url_for('form', name=name))
        elif button == 'Check Status':
            get_process_status_for_question()
            # Perform appropriate action for checking status (implement as needed)
    return render_template('thankyou.html', name=name)

def start_process_new_question(name, email, question):
    # Placeholder function for processing new question (implement as needed)
    pass

def get_process_status_for_question():
    # Placeholder function for getting process status for a question (implement as needed)
    pass

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
