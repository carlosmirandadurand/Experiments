from flask import Flask, render_template, request
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
        return render_template('thankyou.html', name=name)
    return render_template('form.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
