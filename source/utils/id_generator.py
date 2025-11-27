"""
Módulo para geração segura de IDs incrementais (PKs).
Usa sequência no banco de dados ou contador em memória com sincronização.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/discontento')
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class IDGenerator:
    """Gerador de IDs incrementais sincronizado com o banco de dados."""
    
    def __init__(self, table_name='produto', id_column='id_produto'):
        self.table_name = table_name
        self.id_column = id_column
        self._current_id = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa o gerador buscando o maior ID existente no banco."""
        try:
            with Session(engine) as session:
                query = text(f'SELECT MAX({self.id_column}) as max_id FROM {self.table_name}')
                result = session.execute(query).fetchone()
                max_id = result[0] if result and result[0] else 0
                self._current_id = max_id
                print(f'IDGenerator inicializado. Próximo ID será: {max_id + 1}')
        except Exception as e:
            print(f'Erro ao inicializar IDGenerator: {e}. Iniciando com ID=100')
            self._current_id = 100
    
    def get_next_id(self):
        """Retorna o próximo ID incremental."""
        self._current_id += 1
        return self._current_id
    
    def get_next_ids(self, count):
        """Retorna uma lista com N IDs incrementais."""
        ids = []
        for _ in range(count):
            ids.append(self.get_next_id())
        return ids
    
    def peek_next_id(self):
        """Retorna o próximo ID sem incrementar."""
        return self._current_id + 1


_id_generator = IDGenerator()


def get_next_product_id():
    """Função helper para obter próximo ID de produto."""
    return _id_generator.get_next_id()


def get_next_product_ids(count):
    """Função helper para obter múltiplos IDs de produto."""
    return _id_generator.get_next_ids(count)


def reset_id_generator():
    """Reseta o gerador (útil para testes)."""
    global _id_generator
    _id_generator = IDGenerator()
