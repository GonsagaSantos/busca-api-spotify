import requests as re
import os

REQUEST_TOKEN_DISCOGS_API_URL = os.getenv('REQUEST_TOKEN_DISCOGS_API_URL')
TOKEN_DISCOGS_API_URL = os.getenv('TOKEN_DISCOGS_API_URL')
API_URL_DISCOGS = os.getenv('API_URL_DISCOGS')
TOKEN_DISCOGS = os.getenv('TOKEN_DISCOGS')
CLIENT_SECRET_DISCOGS = os.getenv('CLIENT_SECRET_DISCOGS')
CLIENT_KEY_DISCOGS = os.getenv('CLIENT_KEY_DISCOGS')

def get_price_by_album(album_token: str):
    headers = {
        'Authorization': f'Discogs token={TOKEN_DISCOGS}'
    }

    try:
        response = re.get(f'{API_URL_DISCOGS}/marketplace/price_suggestions/{album_token}?currency=BRL', headers=headers)
    except Exception as e:
        print(f'Erro ao buscar as informações do álbum {album_token} na API do Discogs.')

    return response

def get_infos_by_album(album_data):
    headers = {
        'Authorization': f'Discogs key={CLIENT_KEY_DISCOGS}, secret={CLIENT_SECRET_DISCOGS}'
    }

    try:
        response = re.get(f'{API_URL_DISCOGS}/database/search?q={album_data[0]['album_name']}, {album_data[0]['artist']}', headers=headers)
    except Exception as e:
        print(f'Erro ao buscar as informações do álbum {album_data['name']} na API do Discogs.')

    return response.json()