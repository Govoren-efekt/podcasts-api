from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from utils.database_loader import populate_db
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, select
import json
# App creation and db preparation
app = Flask(__name__)
api = Api(app)
populate_db()

pocast_lookup_args = reqparse.RequestParser()
pocast_lookup_args.add_argument("name", type=str, help="Name of the podcast is required!", required=True)


class Podcast(Resource):
    def post(self):
        args = pocast_lookup_args.parse_args()
        engine = create_engine('sqlite:///itunes_db.sqlite')
        connection = engine.connect()
        metadata = MetaData()
        podcasts = Table('podcasts', metadata, autoload=True,
                         autoload_with=engine)
        stmt = select([podcasts])
        results = connection.execute(stmt).fetchall()
        podcasts_df = pd.DataFrame(results)
        podcasts_df.columns = results[0].keys()
        podcasts_dict = podcasts_df.to_dict(orient='records')

        print(podcasts_dict)
        return json.dumps(podcasts_dict)

    #


# @app.route('/api', methods=['POST'])
# def hello_world():
#     args = pocast_lookup_args.parse_args()
#     print(args)
#     return args

api.add_resource(Podcast, "/api")

if __name__ == '__main__':
    app.run(debug=True)
