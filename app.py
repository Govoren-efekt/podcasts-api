from flask import Flask
from utils.database_loader import populate_db

app = Flask(__name__)
populate_db()

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
