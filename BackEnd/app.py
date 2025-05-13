from flask import Flask, request, jsonify
import psycopg2
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS  # Importando a biblioteca para CORS
from flask_sqlalchemy import SQLAlchemy

# Cria a aplicação Flask
app = Flask(__name__)

# Definir a chave secreta para codificar e decodificar o JWT
app.config['SECRET_KEY'] = 'sua_chave_secreta'

# Habilitar CORS para a aplicação inteira (pode ser configurado para aceitar origens específicas)
CORS(app)

# Configuração para o novo banco de dados (SQLite em memória para exemplo)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do SQLAlchemy
db = SQLAlchemy(app)

# Variável de controle para garantir que as tabelas sejam criadas apenas uma vez
tabelas_criadas = False

# Definição dos modelos das tabelas
class Estoque(db.Model):
    __tablename__ = 'estoque'
    id = db.Column(db.Integer, primary_key=True)
    produto = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    marca = db.Column(db.String(50))
    cor = db.Column(db.String(30))
    codigo = db.Column(db.String(20), nullable=False, unique=True)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    condicao = db.Column(db.String(20))
    peso = db.Column(db.Numeric(5, 2))
    observacoes = db.Column(db.Text)

    def __repr__(self):
        return f"<Estoque {self.produto}>"

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=True)
    sobrenome = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    numero = db.Column(db.String(20))
    senha_hash = db.Column(db.Text, nullable=False)  # Para armazenar o hash da senha

    def __repr__(self):
        return f"<Usuario {self.email}>"

# Função para gerar um token JWT
def gerar_token(email):
    try:
        # Cria o payload com o e-mail e a expiração do token (1 hora)
        payload = {
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        # Gera o token JWT
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        return token
    except Exception as e:
        print(f"Erro ao gerar token: {e}")
        return None

@app.before_request
def create_tables():
    global tabelas_criadas
    if not tabelas_criadas:
        with app.app_context():
            db.create_all()
            print("Tabelas 'estoque' e 'usuarios' criadas no banco de dados.")
        tabelas_criadas = True

# Rota para cadastrar um novo usuário
@app.route('/new_user', methods=['POST'])
def new_user():
    if not request.is_json:
        return jsonify({"error": "Content-Type deve ser application/json"}), 415

    data = request.get_json()  # Obter o JSON do corpo da requisição
    nome = data.get('nome')
    sobrenome = data.get('sobrenome')
    email = data.get('email')
    numero = data.get('numero')
    senha = data.get('senha')

    # Verifica se todos os campos foram enviados
    if not all([nome, sobrenome, email, numero, senha]):
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "Email já cadastrado"}), 409

    senha_hash = generate_password_hash(senha)

    try:
        novo_usuario = Usuario(nome=nome, sobrenome=sobrenome, email=email, numero=numero, senha_hash=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()
        return jsonify({"message": "Usuário adicionado com sucesso"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Rota de login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    senha = data.get('senha')

    if not all([email, senha]):
        return jsonify({"error": "E-mail e senha são obrigatórios"}), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and check_password_hash(usuario.senha_hash, senha):
        # Gerar o token JWT
        token = gerar_token(email)
        return jsonify({"message": "Login bem-sucedido", "token": token}), 200
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401

# Rota de perfil
@app.route('/perfil', methods=['GET'])
def perfil():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"error": "Token não fornecido"}), 401

    try:
        # Remover o prefixo "Bearer " do token
        token = token.split(" ")[1]

        # Decodificar o token JWT
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        email = payload['email']

        # Buscar os dados do usuário no banco de dados
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            usuario_data = {
                "nome": usuario.nome,
                "sobrenome": usuario.sobrenome,
                "email": usuario.email,
                "numero": usuario.numero
            }
            return jsonify({"perfil": usuario_data}), 200
        else:
            return jsonify({"error": "Usuário não encontrado"}), 404

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

# Rota para cadastrar um produto no estoque
@app.route('/estoque/cadastrar', methods=['POST'])
def cadastrar_produto():
    dados = request.json
    try:
        novo_produto = Estoque(
            produto=dados['produto'],
            preco=dados['preco'],
            marca=dados.get('marca'),
            cor=dados.get('cor'),
            codigo=dados['codigo'],
            quantidade=dados.get('quantidade', 0),
            condicao=dados.get('condicao'),
            peso=dados.get('peso'),
            observacoes=dados.get('observacoes')
        )
        db.session.add(novo_produto)
        db.session.commit()
        return jsonify({'mensagem': 'Produto cadastrado com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Rota para deletar um produto do estoque
@app.route('/estoque/deletar/<string:codigo>', methods=['DELETE'])
def deletar_produto(codigo):
    try:
        produto = Estoque.query.filter_by(codigo=codigo).first()
        if produto:
            db.session.delete(produto)
            db.session.commit()
            return jsonify({'mensagem': 'Produto deletado com sucesso!'})
        else:
            return jsonify({'erro': 'Produto não encontrado'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Rota para editar um produto do estoque
@app.route('/estoque/editar/<string:codigo>', methods=['PUT'])
def editar_produto(codigo):
    dados = request.json
    try:
        produto = Estoque.query.filter_by(codigo=codigo).first()
        if produto:
            for key, value in dados.items():
                setattr(produto, key, value)
            db.session.commit()
            return jsonify({'mensagem': 'Produto atualizado com sucesso!'})
        else:
            return jsonify({'erro': 'Produto não encontrado'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Rota para listar todos os produtos no estoque
@app.route('/estoque/listar', methods=['GET'])
def listar_produtos():
    try:
        produtos = Estoque.query.all()
        produtos_lista = [{
            'produto': p.produto,
            'preco': float(p.preco),
            'marca': p.marca,
            'cor': p.cor,
            'codigo': p.codigo,
            'quantidade': p.quantidade,
            'condicao': p.condicao,
            'peso': float(p.peso),
            'observacoes': p.observacoes
        } for p in produtos]
        return jsonify(produtos_lista)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/estoque/produto/<string:codigo>', methods=['GET'])
def buscar_produto(codigo):
    try:
        produto = Estoque.query.filter_by(codigo=codigo).first()
        if produto:
            produto_data = {
                "produto": produto.produto,
                "preco": float(produto.preco),
                "marca": produto.marca,
                "cor": produto.cor,
                "codigo": produto.codigo,
                "quantidade": produto.quantidade,
                "condicao": produto.condicao,
                "peso": float(produto.peso),
                "observacoes": produto.observacoes
            }
            return jsonify({"produto": produto_data}), 200
        else:
            return jsonify({"error": "Produto não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )