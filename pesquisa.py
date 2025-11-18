import pandas as pd
import requests as re
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from model import Produto

TOKEN_API_URL = 'https://accounts.spotify.com'
API_URL = 'https://api.spotify.com'

engine = create_engine('postgresql://postgres:postgres@localhost:5432/discontento', pool_pre_ping=True)

def get_albums_from_csv():
    album_info_to_request = []
    
    df = pd.read_csv('assets/pesquisa.csv', sep=',', na_values="")
    
    for index, row in df.iterrows():
        album_data = {
            'curators_name': row['Your name (what will be shown on page)'],
            'album_name': row["Album's name"],
            'artist': row["Artist or band"],
            'release_year': row["Release year"],
            'description': row['Description'],
            'country': row['Country'],
            'label': row['Label'] 
        }

        album_info_to_request.append(album_data)

    print('passou na função de pegar os dados')
    return album_info_to_request

def get_auth_token():
    payload = {}

    try:
        token = re.post(f'{TOKEN_API_URL}/api/token', data=payload, headers={'content_type': 'application/x-www-form-urlencoded'})
        print('passou na função de pegar o token')
    except Exception as e:
        print(f'Erro ao pegar token de autenticação: {e}')

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

def save_data_database(album_data):
    with Session(engine) as session:
        albums = []

        for album in album_data:
            new_album = Produto(
                id_produto = album['id_produto'],
                descritivo = album['descritivo'],
                destaque = album['destaque'],
                keywords = album['keywords'],
                nome = album['nome'],
                promo = album['promo'],
                quantidade = album['quantidade'],
                valor = album['valor'],
                url_imagem = album['url_imagem'],
                ano_lancamento = album['ano_lancamento'],
                artista = album['artista'],
                curador = album['curador'],
                gravadora = album['gravadora'],
                pais_origem = album['pais_origem'],
                carrossel = album['carrossel'],
                underground = album['underground'],
                genero = album['genero'],
                em_promo = album['em_promo']
            )

            albums.append(new_album)

        try:
            session.add_all(albums)
            session.commit()
        except Exception as e:
            print(f'ERRO ao salvar o album no banco: {e}')

def format_data_before_persist(df_data, api_data):
    # url_imagem = base64.b64encode(api_data['image_300'])
    df_data = [album for album in df_data if album['album_name'] == api_data['name']]

    new_album = {
        'id_produto': api_data['id'],
        'descritivo': df_data[0]['description'],
        'destaque': 0,
        'keywords': str(api_data['genres']),
        'nome': df_data[0]['album_name'],
        'promo': 0.00,
        'quantidade': 10,
        'valor': 0.00,
        'url_imagem': api_data['image_640'],
        'ano_lancamento': df_data[0]['release_year'],
        'artista': df_data[0]['artist'],
        'curador': df_data[0]['curators_name'],
        'gravadora': df_data[0]['label'],
        'pais_origem': df_data[0]['country'],
        'carrossel': 0,
        'underground': 0,
        'genero': str(api_data['genres']),
        'em_promo': 0
    }

    print(f'O objeto que vai ser gravado é: {new_album['nome']}')

    # save_data_database(new_album)
    return new_album

def main():
    info = get_albums_from_csv()
    token_data = get_auth_token()
    access_token_string = token_data.get('access_token') 
    
    get_albums_from_api(access_token_string, info)

    # print(response_albums)

if __name__ == '__main__':
    main()