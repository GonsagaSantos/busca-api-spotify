from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.model import Produto

engine = create_engine('postgresql://postgres:postgres@localhost:5432/discontento', pool_pre_ping=True)

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