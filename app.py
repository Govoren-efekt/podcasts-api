from flask import Flask, request, jsonify
from flask_restful import abort
from utils.database_loader import populate_db
import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)

if 'json_outputs' not in os.listdir():
    os.mkdir('json_outputs')

# DB creation
if 'itunes_db.sqlite' not in os.listdir():
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
        fields = ('artistName', 'id',
                  'releaseDate', 'name', 'kind', 'copyright', 'artistId',
                  'contentAdvisoryRating', 'artistUrl', 'artworkUrl100', 'url', 'genres')


class PodcastByGenreSchema(ma.Schema):
    class Meta:
        fields = ('artistName', 'id',
                  'releaseDate', 'name', 'kind', 'copyright', 'artistId',
                  'contentAdvisoryRating', 'artistUrl', 'artworkUrl100', 'url')


# Init Schemas
genres_schema = GenreSchema(many=True)
podcast_schema = PodcastSchema()
podcasts_schema = PodcastSchema(many=True)
podcast_by_genre = PodcastByGenreSchema()


@app.route('/api', methods=['POST'])
def search_lookup():
    name = request.json['name']
    all_podcasts = Podcast.query.filter(Podcast.name.like('%' + name.lower() + '%')).all()
    result = podcasts_schema.dump(all_podcasts)
    return jsonify(result)


@app.route('/api/top20', methods=['GET'])
def store_top_20():
    top_20 = Podcast.query.order_by(Podcast.index).limit(20).all()
    result = podcasts_schema.dump(top_20)
    with open('json_outputs/top_20.json', 'w') as json_file:
        json.dump(result, json_file)

    return {'message': 'Top 20 podcasts'
                       'had been written in: json_outputs/top_20.json'}, 200


@app.route('/api/swap', methods=['GET'])
def swap_top_bottom():
    sorted_podcast = Podcast.query.order_by(Podcast.index).all()
    top_20 = sorted_podcast[:20]
    bottom_20 = sorted_podcast[-20:]
    sorted_podcast[:20] = bottom_20
    sorted_podcast[-20:] = top_20
    result = podcasts_schema.dump(sorted_podcast)
    with open('json_outputs/swapped_top_bottom.json', 'w') as json_file:
        json.dump(result, json_file)
    return {'message': 'Swapped JSON of top 20  bottom 20 '
                       'has been written in: json_outputs/swapped_top_bottom.json '}, 200


@app.route('/api/<id>', methods=['DELETE'])
def delete_podcast(id):
    podcast = Podcast.query.get(id)
    if podcast is None:
        abort(404, message='Podcast does not exists.')
    db.session.delete(podcast)
    db.session.commit()
    return {'message': f'podcast with id {id} was deleted successfully.'}, 200


@app.route('/api/grouped', methods=['GET'])
def podcasts_by_genres():
    raw_query = (""" 
        SELECT genre.name,
        p.id
        FROM genre
        JOIN genre_podcast gp ON genre.genreId = gp.genreId
        JOIN podcast p ON gp.id = p.id
        ORDER BY genre.name;
    
    """)
    results = db.engine.execute(raw_query).fetchall()
    genres_dict = {}
    for r in results:
        if r[0] not in genres_dict.keys():
            genres_dict[r[0]] = []
        podcast_list = Podcast.query.get(r[1])
        podcast_list = podcast_by_genre.dump(podcast_list)
        genres_dict[r[0]].append(podcast_list)
    print(genres_dict)
    return genres_dict


if __name__ == '__main__':
    app.run(debug=True)
