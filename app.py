from flask import Flask, request, jsonify, make_response
from utils.database_loader import populate_db
import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

# Create folder for storing the json outputs.
if 'json_outputs' not in os.listdir():
    os.mkdir('json_outputs')

# Create db if doesn't exists
if 'itunes_db.sqlite' not in os.listdir():
    populate_db()

# App configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itunes_db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Many-to-many intermediate table
genre_podcast = db.Table('genre_podcast',
                         db.Column('id', db.Integer, db.ForeignKey('podcast.id')),
                         db.Column('genreId', db.Integer, db.ForeignKey('genre.genreId')))


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated




# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))



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


# Schema created to avoid showing genre column when grouping podcasts by genre
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


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/api', methods=['POST'])
@token_required
def search_lookup(current_user):
    if 'name' not in request.json.keys() or not isinstance(request.json['name'], str):
        return {'message': 'name string field is required'}, 400
    name = request.json['name']
    all_podcasts = Podcast.query.filter(Podcast.name.like('%' + name.lower() + '%')).all()
    result = podcasts_schema.dump(all_podcasts)
    if len(result) > 0:
        return jsonify(result)
    else:
        return {'message': 'No matches for that name.'}, 404


@app.route('/api/top20', methods=['GET'])
@token_required
def store_top_20(current_user):
    top_20 = Podcast.query.order_by(Podcast.index).limit(20).all()
    result = podcasts_schema.dump(top_20)
    with open('json_outputs/top_20.json', 'w') as json_file:
        json.dump(result, json_file)

    return {'message': 'Top 20 podcasts'
                       ' had been written in: json_outputs/top_20.json'}, 200


@app.route('/api/swap', methods=['GET'])
@token_required
def swap_top_bottom(current_user):
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
@token_required
def delete_podcast(current_user,id):
    podcast = Podcast.query.get(id)
    if podcast is None:
        return {'message': f'Podcast with id: {id} does not exists.'}, 404
    db.session.delete(podcast)
    db.session.commit()
    return {'message': f'podcast with id {id} was deleted successfully.'}, 200


@app.route('/api/grouped', methods=['GET'])
@token_required
def podcasts_by_genres(current_user):
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
    app.run()
