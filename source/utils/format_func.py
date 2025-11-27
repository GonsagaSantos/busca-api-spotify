import numpy as np

from api.HTTP.Discogs import service as discogs

def format_data_before_persist(df_data, api_data):
    if not df_data:
        print(f'ERRO: df_data vazio para {api_data['name']}')
        return None
    
    df_data = [album for album in df_data if album['album_name'] == api_data['name']]
    
    if not df_data:
        print(f"ERRO: Nenhum álbum encontrado em df_data para {api_data['name']}")
        return None

    response_discogs = discogs.get_infos_by_album(album_data=df_data)
    
    if not response_discogs.get('results') or len(response_discogs['results']) == 0:
        print(f'ERRO: Nenhum resultado do Discogs para {api_data['name']}')
        preco_normal = 0.00
        preco_promo = 0.00
    else:
        precos_disco = discogs.get_price_by_album(response_discogs['results'][0]['id'])

        if precos_disco.status_code == 200:
            try:
                precos_disco_json = precos_disco.json()
                
                all_prices = []
                for condition, price_info in precos_disco_json.items():
                    if isinstance(price_info, dict) and 'value' in price_info:
                        price_value = price_info.get('value', 0.00)
                        if price_value > 0:
                            all_prices.append(price_value)
                
                if all_prices:
                    preco_normal = float(np.mean(all_prices))
                    print(f'Preços encontrados: {all_prices} | Média: {preco_normal}')
                else:
                    preco_normal = 0.00
                
                preco_promo = precos_disco_json.get("Fair (F)", {}).get('value', None)
                if preco_promo is None:
                    preco_promo = float(preco_normal * 0.9) if preco_normal > 0 else 0.00
                else:
                    preco_promo = float(preco_promo)
                
            except Exception as e:
                print(f'Erro ao processar preços do Discogs: {e}')
                preco_normal = 0.00
                preco_promo = 0.00

        else:
            preco_normal = 0.00
            preco_promo = 0.00


    api_data['genres'] = (str(api_data['genres'])
                        .replace('[', '')
                        .replace(']', '')
                        .replace("'", ''))

    valor_final = float(round(preco_normal, 2)) if preco_normal else 0.0
    promo_final = float(round(preco_promo, 2)) if preco_promo else 0.0

    new_album = {
        'id_produto': api_data.get('id'),
        'descritivo': df_data[0].get('description', ''),
        'destaque': 0,
        'keywords': str(api_data.get('genres', '')),
        'nome': df_data[0].get('album_name', ''),
        'promo': promo_final,
        'quantidade': int(df_data[0].get('quantity', 10)) if df_data[0].get('quantity') is not None else 10,
        'valor': valor_final,
        'url_imagem': api_data.get('image_640', ''),
        'ano_lancamento': df_data[0].get('release_year', ''),
        'artista': df_data[0].get('artist', ''),
        'curador': df_data[0].get('curators_name', ''),
        'gravadora': df_data[0].get('label', ''),
        'pais_origem': df_data[0].get('country', ''),
        'carrossel': 0,
        'underground': 0,
        'genero': str(api_data.get('genres', '')),
        'em_promo': 0,
        'artist_popularity': int(api_data.get('artist_popularity')) if api_data.get('artist_popularity') is not None else 0
    }

    print(f'O objeto que vai ser gravado é: {new_album['nome']}')

    # save_data_database(new_album)
    return new_album
