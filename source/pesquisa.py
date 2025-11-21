import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from source.api.HTTP.Spotify.service import get_albums_from_api, get_auth_token
from source.pandas.service import get_albums_from_csv


def main():
    info = get_albums_from_csv()
    token_data = get_auth_token()
    access_token_string = token_data.get('access_token') 
    
    get_albums_from_api(access_token_string, info)

if __name__ == '__main__':
    main()