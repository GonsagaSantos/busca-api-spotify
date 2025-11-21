import requests as re
import json
import os

from source.database.repository import save_data_database
from source.utils.format_func import format_data_before_persist

API_URL = os.getenv('API_URL_SPOTIFY')
TOKEN_API_URL = os.getenv('TOKEN_SPOTIFY_API_URL')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

def get_auth_token():
    payload = {
        'grant_type': 'client_credentials', 
        'client_id': CLIENT_ID, 
        'client_secret': CLIENT_SECRET
    }

    try:
        token = re.post(f'{TOKEN_API_URL}/api/token', data=payload, headers={'content_type': 'application/x-www-form-urlencoded'})
        print('passou na função de pegar o token')
    except Exception as e:
        print(f'Erro ao pegar token de autenticação: {e}')
    print(token.text)
    return json.loads(token.text)

def get_albums_from_api(token, album_info):
    headers = {'Authorization': f'Bearer {token}'}
    data_list = []

    id = 100
    try:
        for album_data in album_info:
            id+=1

            print(f'Salvando o album {album_data['album_name']}')

            album_name = album_data['album_name'].replace(' ', '%20')

            try:
                raw_response = re.get(f'{API_URL}/v1/search?q={album_name}&type=album,artist', headers=headers)
                response = json.loads(raw_response.text)

                print(f'album {album_data['album_name']} foi encontrado no spotify')
            except Exception as e:
                print(f"Erro ao consultar o album {album_data['album_name']}! Erro: {e}")

            album_list = response['albums'].get('items', [])
            album_exact_data_list = [
                album for album in album_list
                if (
                    album['name'] == album_data['album_name'] and 
                    album['artists'] and album['artists'][0]['name'] == album_data['artist'] and
                    album['release_date'][:4] == album_data['release_year']
                )
            ]

            print(f'album {album_data['album_name']} exato encontrado!')

            if album_exact_data_list:
                album_exact_data = album_exact_data_list[0]
                artist_id = album_exact_data['artists'][0]['id']
                genres = get_genres_by_artist(token, artist_id)

                print(f'criando objeto do {album_data['album_name']}')
                album_complete_data = {
                    'id': id,
                    'name': album_data['album_name'],
                    'genres': genres['genres'],
                    'image_640': album_exact_data['images'][0]['url'],
                    'image_300': album_exact_data['images'][1]['url'],
                    'image_64': album_exact_data['images'][2]['url'],
                    'artist': artist_id,
                    'total_tracks': album_exact_data['total_tracks'],
                    'release_date': album_exact_data['release_date']
                }

                print(f'formatando album {album_complete_data['name']}')
                album_formated_data = format_data_before_persist(album_info, album_complete_data)

                data_list.append(album_formated_data)

        save_data_database(data_list)
    except Exception as e:
        response = e

    print('passou na função de consultar os albums')
    return data_list

def get_genres_by_artist(token, artist_id):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = re.get(f'{API_URL}/v1/artists/{artist_id}', headers=headers)
    except Exception as e:
        print(f'Erro ao buscar dados dos artistas: {e}')

    print('passou na função de consultar os generos')
    return json.loads(response.text)