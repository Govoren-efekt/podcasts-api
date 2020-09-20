from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from utils.database_loader import populate_db
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, select
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from flask_marshmallow import Marshmallow

app = Flask(__name__)

populate_db()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itunes_db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# api = Api(app)

ma = Marshmallow(app)


# Classes
# Base = automap_base()
# Base.prepare(db.engine, reflect=True)
# Podcast = Base.classes.podcasts
# Genre = Base.classes.genres


# genre_podcast = Base.classes.genres_podcasts

genre_podcast = db.Table('genre_podcast',
                         db.Column('id', db.Integer, db.ForeignKey('podcast.id')),
                         db.Column('genreId', db.Integer, db.ForeignKey('genre.genreId')))

class Genre(db.Model):
    genreId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    url = db.Column(db.String(1000))


class Podcast(db.Model):
    index = db.Column(db.Integer)
    artistName = db.Column(db.String(400))
    id = db.Column(db.Integer, primary_key=True)
    releaseDate = db.Column(db.String(200))
    name = db.Column(db.String(200))
    kind = db.Column(db.String(100))
    copyright = db.Column(db.String(300))
    artistId = db.Column(db.String(100))
    contentAdvisoryRating = db.Column(db.String(100))
    artistUrl = db.Column(db.String(1000))
    artworkUrl100 = db.Column(db.String(1000))
    url = db.Column(db.String(1000))
    genres = db.relationship('Genre', secondary='genre_podcast')


class GenreSchema(ma.Schema):
    class Meta:
        fields = ('genreId', 'name', 'url')


class PodcastSchema(ma.Schema):
    genres = ma.Nested(GenreSchema, many=True)

    class Meta:
        fields = ('index', 'artistName', 'id',
                  'releaseDate', 'name', 'kind', 'copyright', 'artistId',
                  'contentAdvisoryRating', 'artistUrl', 'artworkUrl100', 'url', 'genres')


# Init Schema
genres_schema = GenreSchema(many=True)
podcasts_schema = PodcastSchema(many=True)


# class PodcastSchema(ma.Schema):
#     class

# pocast_lookup_args = reqparse.RequestParser()
# pocast_lookup_args.add_argument("name", type=str, help="Name of the podcast is required!", required=True)


# class Podcast(Resource):
#     def post(self):
#         args = pocast_lookup_args.parse_args()
#         engine = create_engine('sqlite:///itunes_db.sqlite')
#         connection = engine.connect()
#         metadata = MetaData()
#         podcasts = Table('podcasts', metadata, autoload=True,
#                          autoload_with=engine)
#         stmt = select([podcasts])
#         results = connection.execute(stmt).fetchall()
#         podcasts_df = pd.DataFrame(results)
#         podcasts_df.columns = results[0].keys()
#         podcasts_dict = podcasts_df.to_dict(orient='records')
#         return json.dumps(podcasts_dict)


@app.route('/api', methods=['GET'])
def hello_world():
    # all_genres = db.session.query(Genre).all()
    all_podcasts = Podcast.query.all()
    result = podcasts_schema.dump(all_podcasts)
    # result = genres_schema.dump(all_genres)
    return jsonify(result)
    # results = db.session.query(Podcast).all()
    # for r in results:
    #     print(r.name)
    # # print(results)
    # return {}


# api.add_resource(Podcast, "/api")

if __name__ == '__main__':
    app.run(debug=True)
