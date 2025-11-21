import os
import sys
from fastapi import FastAPI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from source.api.HTTP.Spotify.service import get_albums_from_api, get_auth_token
from source.pandas.service import get_albums_from_csv

app = FastAPI()

@app.get('/processarForms')
def processarForms():
    print('hello world')
    return {"status": "ok", "message": "hello world"}