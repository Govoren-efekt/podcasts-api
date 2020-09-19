import requests
import pandas as pd
from random import randint
from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column


def fetch_json():
    response = requests.get('https://rss.itunes.apple.com/api/v1/us/podcasts/top-podcasts/all/100/explicit.json')
    response = response.json()
    return response['feed']['results']


def create_artist_id(ids, min_id, max_id):
    while True:
        artist_id = randint(min_id, max_id)
        if artist_id not in ids:
            return artist_id


def get_dfs(data):
    genres_list = []
    genres_podcasts_dict = {
        'podcastId': [],
        'genreId': []
    }

    artists_dict = {
        'artistId': [],
        'artistName': [],
        'artistUrl': []
    }
    current_artists_ids = [int(element['artistId']) for element in data if 'artistId' in element]
    for row in data:
        for genreDict in row['genres']:
            # Extract genres
            genres_list.append(genreDict)
            genres_podcasts_dict['podcastId'].append(row['id'])
            genres_podcasts_dict['genreId'].append(genreDict['genreId'])

        artists_dict['artistName'].append(row['artistName'])
        if 'artistId' not in row:
            min_id = min(current_artists_ids)
            max_id = max(current_artists_ids)
            new_id = create_artist_id(current_artists_ids, min_id, max_id)
            current_artists_ids.append(new_id)
            row['artistId'] = new_id

        artists_dict['artistId'].append(row['artistId'])

        if 'artistUrl' not in row:
            artists_dict['artistUrl'].append('')

        else:
            artists_dict['artistUrl'].append(row['artistUrl'])

    podcasts = pd.DataFrame(data)
    podcasts_df = podcasts.drop(['artistName', 'artistUrl', 'genres'], axis=1)
    genres_df = pd.DataFrame(genres_list)
    genres_df = genres_df.drop_duplicates()
    genres_podcasts_df = pd.DataFrame(genres_podcasts_dict)
    artists_df = pd.DataFrame(artists_dict)
    artists_df = artists_df.drop_duplicates(subset='artistName')
    return podcasts_df, artists_df, genres_df, genres_podcasts_df


def create_and_populate_tables(podcasts, artists, genres, genres_podcasts):
    engine = create_engine('sqlite:///itunes_db.sqlite')
    metadata = MetaData()
    genres_podcasts_table = Table('genres_podcasts', metadata,
                                  Column('podcastId', Integer, primary_key=True),
                                  Column('genreId', Integer, primary_key=True))
    metadata.create_all(engine)
    genres_podcasts.to_sql('genres_podcasts', con=engine, if_exists='append', index=False)
#

top_100_podcasts = fetch_json()
podcasts, artists, genres, genres_podcasts = get_dfs(top_100_podcasts)
create_and_populate_tables(podcasts, artists, genres, genres_podcasts)

# print(engine.execute('SELECT * FROM genres_podcasts').fetchall())
