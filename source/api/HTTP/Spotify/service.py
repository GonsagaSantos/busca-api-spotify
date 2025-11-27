import requests as re
import json
import os
from difflib import SequenceMatcher

from source.database.repository import save_data_database
from source.utils.format_func import format_data_before_persist
from source.utils.id_generator import get_next_product_id
from source.api.HTTP.Discogs import service as discogs

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
    albums_not_processed = []

    try:
        for album_data in album_info:
            product_id = get_next_product_id()

            print(f'Salvando o album {album_data['album_name']} com ID: {product_id}')

            album_name = album_data['album_name'].replace(' ', '%20')

            try:
                raw_response = re.get(f'{API_URL}/v1/search?q={album_name}&type=album,artist', headers=headers)
                response = json.loads(raw_response.text)

                print(f'album {album_data['album_name']} foi encontrado no spotify')
            except Exception as e:
                print(f"Erro ao consultar o album {album_data['album_name']}! Erro: {e}")

            album_list = response['albums'].get('items', [])
            
            def similarity(a, b):
                return SequenceMatcher(None, a.lower(), b.lower()).ratio()
            
            album_exact_data_list = [
                album for album in album_list
                if (
                    album['name'] == album_data['album_name'] and 
                    album['artists'] and album['artists'][0]['name'] == album_data['artist']
                )
            ]
            
            if not album_exact_data_list:
                print(f'{album_data['name']} nao encontrado tentando fuzzy match')
                album_exact_data_list = [
                    album for album in album_list
                    if (
                        album['artists'] and
                        similarity(album['name'], album_data['album_name']) > 0.8 and
                        similarity(album['artists'][0]['name'], album_data['artist']) > 0.8
                    )
                ]
            
            if not album_exact_data_list:
                print(f'fuzzy match nao funcionou, tentando encontrar por nome')
                album_exact_data_list = [
                    album for album in album_list
                    if similarity(album['name'], album_data['album_name']) > 0.85
                ]
            
            if not album_exact_data_list:
                print(f"Album {album_data['album_name']} não encontrado no Spotify. Tentando fallback no Discogs")

                try:
                    discogs_search = discogs.get_infos_by_album(album_data=[{'album_name': album_data['album_name'], 'artist': album_data['artist']}])
                    if isinstance(discogs_search, dict) and discogs_search.get('results'):
                        disc_item = discogs_search['results'][0]
                        cover = disc_item.get('cover_image') or disc_item.get('thumb') or ''

                        print(f'Fallback Discogs encontrou dados para {album_data['album_name']}: id {disc_item.get('id')}')

                        album_complete_data = {
                            'id': product_id,
                            'name': album_data['album_name'],
                            'genres': [],
                            'image_640': cover,
                            'image_300': cover,
                            'image_64': cover,
                            'artist': album_data['artist'],
                            'total_tracks': album_data.get('total_tracks', 0),
                            'release_date': disc_item.get('year') or album_data.get('release_year', '')
                        }

                        album_formated_data = format_data_before_persist(album_info, album_complete_data)
                        if album_formated_data:
                            data_list.append(album_formated_data)
                        else:
                            print(f'Album {album_data['album_name']} pulado depois do fallback por erro no processamento')
                            albums_not_processed.append(album_data['album_name'])
                    else:
                        print(f'Discogs não retornou resultados para {album_data['album_name']}')
                        albums_not_processed.append(album_data['album_name'])
                except Exception as e:
                    print(f'Erro ao buscar no Discogs para {album_data['album_name']}: {e}')
                    albums_not_processed.append(album_data['album_name'])

            if album_exact_data_list:
                album_exact_data = album_exact_data_list[0]
                artist_id = album_exact_data['artists'][0]['id']
                genres = get_genres_by_artist(token, artist_id)

                images = album_exact_data.get('images', [])
                if len(images) < 3:
                    print(f'AVISO: Álbum {album_data['album_name']} tem apenas {len(images)} imagem(s). Esperado 3.')
                    if not images:
                        continue 

                print(f'criando objeto do {album_data['album_name']}')
                album_complete_data = {
                    'id': product_id,
                    'name': album_data['album_name'],
                    'genres': genres['genres'],
                    'image_640': images[0]['url'] if len(images) > 0 else '',
                    'image_300': images[1]['url'] if len(images) > 1 else (images[0]['url'] if images else ''),
                    'image_64': images[2]['url'] if len(images) > 2 else (images[0]['url'] if images else ''),
                    'artist': artist_id,
                    'total_tracks': album_exact_data['total_tracks'],
                    'release_date': album_exact_data['release_date']
                }

                print(f'formatando album {album_complete_data['name']}')
                album_formated_data = format_data_before_persist(album_info, album_complete_data)

                if album_formated_data:
                    data_list.append(album_formated_data)
                else:
                    print(f'Album {album_data['album_name']} foi pulado por erro no processamento')
                    albums_not_processed.append(album_data['album_name'])

        data_list = [album for album in data_list if album is not None]
        
        if data_list:
            TOP_POPULAR = int(os.getenv('TOP_POPULAR', '10'))
            TOP_PROMO = int(os.getenv('TOP_PROMO', '10'))

            sorted_by_pop = sorted(data_list, key=lambda x: x.get('artist_popularity', 0), reverse=True)
            popular_items = sorted_by_pop[:TOP_POPULAR]
            popular_ids = {item.get('id_produto') for item in popular_items}
            for item in popular_items:
                item['carrossel'] = 1
                item['destaque'] = 1

            remaining = [a for a in data_list if a.get('id_produto') not in popular_ids]
            sorted_by_price = sorted(remaining, key=lambda x: x.get('valor', 0), reverse=True)
            for item in sorted_by_price[:TOP_PROMO]:
                item['em_promo'] = 1

            save_data_database(data_list)
    except Exception as e:
        response = e
        print(f'ERRO ao salvar dados no banco: {e}')

    print('passou na função de consultar os albums')
    print(f'os albuns {albums_not_processed} não conseguiram ser processados')
    return data_list

def get_genres_by_artist(token, artist_id):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = re.get(f'{API_URL}/v1/artists/{artist_id}', headers=headers)
    except Exception as e:
        print(f'Erro ao buscar dados dos artistas: {e}')

    print('passou na função de consultar os generos')
    return json.loads(response.text)