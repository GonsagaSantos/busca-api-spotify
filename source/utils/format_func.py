def format_data_before_persist(df_data, api_data):
    df_data = [album for album in df_data if album['album_name'] == api_data['name']]

    if df_data[0]['description'] is None \
        or df_data[0]['description'] == 'NaN' \
        or df_data[0]['valor'] == 0:
            ## Implementar a chamada de API do discogs para complementar esses campos
            pass 
        

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
