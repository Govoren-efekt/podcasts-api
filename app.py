from flask import Flask, request
from flask_restful import Api, Resource
from utils.database_loader import populate_db

app = Flask(__name__)
api = Api(app)
populate_db()


# @app.route('/', methods=['POST'])
# def hello_world():
#     data = request.form['ticker']
#     print(data)
#     return 'Hello World!'
class Podcast(Resource):
    def post(self):
        print(request.form)
        return {}


api.add_resource(Podcast, '/api')

if __name__ == '__main__':
    app.run(debug=True)
