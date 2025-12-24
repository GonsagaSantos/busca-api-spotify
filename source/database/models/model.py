from typing import Optional
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Produto(Base):
    __tablename__ = "produto"

    id_produto: Mapped[int] = mapped_column(primary_key = True)
    descritivo: Mapped[Optional[str]] = mapped_column(String(100000))
    destaque: Mapped[int] = mapped_column(Integer)
    keywords: Mapped[Optional[str]] = mapped_column(String(255))
    nome: Mapped[str] = mapped_column(String(255))
    promo: Mapped[float] = mapped_column()
    quantidade: Mapped[int] = mapped_column(Integer) 
    valor: Mapped[float] = mapped_column()
    url_imagem: Mapped[Optional[str]] = mapped_column(String(255))
    ano_lancamento: Mapped[Optional[str]] = mapped_column(String(255))
    artista: Mapped[Optional[str]] = mapped_column(String(255))
    curador : Mapped[Optional[str]] = mapped_column(String(255))
    gravadora: Mapped[Optional[str]] = mapped_column(String(255))
    pais_origem: Mapped[Optional[str]] = mapped_column(String(255))
    carrossel: Mapped[int] = mapped_column(Integer)
    underground: Mapped[int] = mapped_column(Integer)
    genero: Mapped[Optional[str]] = mapped_column(String(255))
    em_promo: Mapped[int] = mapped_column(Integer)