from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/overlay', methods=['GET', 'POST'])
def overlay():
    if request.method == 'POST':
        # Get form data
        # name = request.form['name']
        # age = int(request.form['age'])
        
        # # Perform calculations (Example: add 5 to the age)
        # modified_age = age + 5

        # Render template with data
        return render_template('overlay.html')

    # return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
