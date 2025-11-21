import pandas as pd

def get_albums_from_csv():
    album_info_to_request = []
    
    df = pd.read_csv('../assets/pesquisa.csv', sep=',', na_values="")
    
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
