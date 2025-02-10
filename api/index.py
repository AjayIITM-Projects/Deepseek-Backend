from flask import Flask
from api.add import add

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route('/add/<int:x>/<int:y>')
def add_route(x, y):
    return str(add(x, y))

# if __name__ == '__main__':
#     app.run(debug=True)

# python -m api.index