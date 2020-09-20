import requests
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column, ForeignKey, Date
import os


def fetch_json():
    response = requests.get('https://rss.itunes.apple.com/api/v1/us/podcasts/top-podcasts/all/100/explicit.json')
    response = response.json()
    return response['feed']['results']


def get_dfs(data):
    genres_list = []
    genres_podcasts_dict = {
        'id': [],
        'genreId': []
    }

    for row in data:
        for genreDict in row['genres']:
            # Extract genres
            genres_list.append(genreDict)
            genres_podcasts_dict['id'].append(row['id'])
            genres_podcasts_dict['genreId'].append(genreDict['genreId'])

    podcasts_df = pd.DataFrame(data)
    podcasts_df = podcasts_df.drop(['genres'], axis=1)
    genres_df = pd.DataFrame(genres_list)
    genres_df = genres_df.drop_duplicates()
    genres_podcasts_df = pd.DataFrame(genres_podcasts_dict)
    return podcasts_df, genres_df, genres_podcasts_df


def create_and_populate_tables(podcasts, genres, genres_podcasts):
    engine = create_engine('sqlite:///itunes_db.sqlite')
    metadata = MetaData()

    # genres
    Table('genre', metadata, Column('genreId', Integer, primary_key=True), Column('name', String(200)),
          Column('url', String(1000)))

    # Podcasts
    Table('podcast', metadata,
          Column('index', Integer),
          Column('artistName', String(400)),
          Column('id', Integer, primary_key=True),
          Column('releaseDate', String(200)),
          Column('name', String(200)),
          Column('kind', String(100)),
          Column('copyright', String(300)),
          Column('artistId', String(100)),
          Column('contentAdvisoryRating', String(100), nullable=True),
          Column('artistUrl', String(1000)),
          Column('artworkUrl100', String(1000)),
          Column('url', String(1000), nullable=True))

    # Genres Podcasts
    Table('genre_podcast', metadata,
          Column('id', Integer, ForeignKey('podcast.id'), primary_key=True),
          Column('genreId', Integer, ForeignKey('genre.genreId'), primary_key=True))

    metadata.create_all(engine)
    # Inserting dataframes in their corresponding tables
    podcasts.to_sql('podcast', con=engine, if_exists='append')
    genres.to_sql('genre', con=engine, if_exists='append', index=False)
    genres_podcasts.to_sql('genre_podcast', con=engine, if_exists='append', index=False)


def populate_db():
    print('populating db...')
    top_100_podcasts = fetch_json()
    podcasts, genres, genres_podcasts = get_dfs(top_100_podcasts)
    create_and_populate_tables(podcasts, genres, genres_podcasts)
    print('db was populated succesfully!')
