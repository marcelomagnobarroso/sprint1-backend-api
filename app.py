from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

import json
from sqlalchemy.exc import IntegrityError

from model import Session, Produto, Comentario
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
produto_tag = Tag(name="Produto", description="Adição, visualização e remoção de produtos à base")
comentario_tag = Tag(name="Comentario", description="Adição de um comentário à um produtos cadastrado na base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.post('/product/add', tags=[produto_tag],
          responses={"200": ProdutoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_produto(form: ProdutoSchema):
    """Adiciona um novo Produto à base de dados

    Retorna uma representação dos produtos e comentários associados.
    """
    produto = Produto(
        nome=form.nome,
        quantidade=form.quantidade,
        valor=form.valor)
    logger.debug(f"Adicionando produto de nome: '{produto.nome}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(produto)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado produto de nome: '{produto.nome}'")
        return apresenta_produto(produto), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Produto de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar produto '{produto.nome}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar produto '{produto.nome}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/products/get_all', tags=[produto_tag],
         responses={"200": ListagemProdutosSchema, "404": ErrorSchema})
def get_produtos():
    """Realiza a busca de todos os Produto cadastrados

    Retorna uma representação da listagem de produtos.
    """
    logger.debug(f"Coletando produtos ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    produtos = session.query(Produto).all()

    if not produtos:
        # se não há produtos cadastrados
        return {"produtos": []}, 200
    else:
        logger.debug(f"%d rodutos econtrados" % len(produtos))
        # retorna a representação de produto
        print(produtos)
        return apresenta_produtos(produtos), 200


@app.get('/products/sarch_name', tags=[produto_tag],
         responses={"200": ProdutoNameBuscaSchema, "404": ErrorSchema})
def find_ProductsByName(query: ProdutoNameBuscaSchema):
    """Realiza a busca de todos os Produto cadastrados filtrando pelo nome

    Retorna uma representação da listagem de produtos.
    """

    produto_nome = query.nome
    logger.debug(f"Coletando dados sobre produto #{produto_nome}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca

    print("len(produto_nome)....: " + produto_nome)
    if len(produto_nome) < 3:
        produtos = session.query(Produto).all()
    else:
        produtos = session.query(Produto).filter(Produto.nome.like('%' + produto_nome + '%')).from_self()

    if not produtos:
        # se não há produtos cadastrados
        return {"produtos": []}, 200
    else:
        logger.debug(f"Produtos econtrados: '{produtos}'")
        # retorna a representação de produto
        print(produtos)
        return apresenta_produtos(produtos), 200


@app.get('/product/find_id', tags=[produto_tag],
         responses={"200": ProdutoViewSchema, "404": ErrorSchema})
def get_produto(query: ProdutoBuscaSchema):
    """Realiza a busca de um Produto a partir do id do produto

    Retorna uma representação dos produtos e comentários associados.
    """
    produto_id = query.id
    logger.debug(f"Coletando dados sobre produto #{produto_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    produto = session.query(Produto).filter(Produto.id == produto_id).first()

    if not produto:
        # se o produto não foi encontrado
        error_msg = "Produto não encontrado na base :/"
        logger.warning(f"Erro ao buscar produto '{produto_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Produto econtrado: '{produto.nome}'")
        # retorna a representação de produto
        return apresenta_produto(produto), 200


if __name__ == "__main__":
    app.run(debug=True)
