from flask import Flask, request, jsonify
from utils.database_loader import populate_db
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from flask_marshmallow import Marshmallow

app = Flask(__name__)

populate_db()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itunes_db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

ma = Marshmallow(app)

# Many-to-many intermediate table
genre_podcast = db.Table('genre_podcast',
                         db.Column('id', db.Integer, db.ForeignKey('podcast.id')),
                         db.Column('genreId', db.Integer, db.ForeignKey('genre.genreId')))


# Models
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


# Schema creation
class GenreSchema(ma.Schema):
    class Meta:
        fields = ('genreId', 'name', 'url')


class PodcastSchema(ma.Schema):
    genres = ma.Nested(GenreSchema, many=True)

    class Meta:
        fields = ('index', 'artistName', 'id',
                  'releaseDate', 'name', 'kind', 'copyright', 'artistId',
                  'contentAdvisoryRating', 'artistUrl', 'artworkUrl100', 'url', 'genres')


# Init Schemas
genres_schema = GenreSchema(many=True)
podcasts_schema = PodcastSchema(many=True)


@app.route('/api', methods=['GET'])
def hello_world():
    all_podcasts = Podcast.query.all()
    result = podcasts_schema.dump(all_podcasts)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
