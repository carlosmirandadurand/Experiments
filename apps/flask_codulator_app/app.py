from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        question = request.form.get('question')
        return render_template('thankyou.html', name=name)
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)

