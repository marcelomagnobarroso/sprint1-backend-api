from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from typing import Union

from  model import Base


class Comentario(Base):
    __tablename__ = 'comentatio'

    id = Column(Integer, primary_key=True)
    texto = Column(String(4000))
    data_insercao = Column(DateTime, default=datetime.now())
    produto = Column(Integer, ForeignKey("produto.pk_produto"), nullable=False)

    def __init__(self, texto:str, data_insercao:Union[DateTime, None] = None):
        self.texto = texto
        if data_insercao:
            self.data_insercao = data_insercao
