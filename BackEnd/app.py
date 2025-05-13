from flask import Flask, request, jsonify
import psycopg2
import jwt
import datetime
from config import DATABASE
from flask_cors import CORS  # Importando a biblioteca para CORS

# Cria a aplicação Flask
app = Flask(__name__)

# Definir a chave secreta para codificar e decodificar o JWT
app.config['SECRET_KEY'] = 'sua_chave_secreta'

# Habilitar CORS para a aplicação inteira (pode ser configurado para aceitar origens específicas)
CORS(app)

# Função para estabelecer a conexão com o banco de dados
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DATABASE['dbname'],
            user=DATABASE['user'],
            password=DATABASE['password'],
            host=DATABASE['host'],
            port=DATABASE['port']
        )
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None  # Retorna None em caso de erro

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

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conn.cursor()
        query = """
            INSERT INTO usuarios (nome, sobrenome, email, numero, senha)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nome, sobrenome, email, numero, senha))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Usuário adicionado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota de login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    senha = data.get('senha')

    if not all([email, senha]):
        return jsonify({"error": "E-mail e senha são obrigatórios"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Consulta o banco de dados para verificar as credenciais
        query = "SELECT * FROM usuarios WHERE email = %s AND senha = %s"
        cursor.execute(query, (email, senha))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            # Gerar o token JWT
            token = gerar_token(email)
            return jsonify({"message": "Login bem-sucedido", "token": token}), 200
        else:
            return jsonify({"error": "Credenciais inválidas"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT nome, sobrenome, email, numero FROM usuarios WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            usuario_data = {
                "nome": user[0],
                "sobrenome": user[1],
                "email": user[2],
                "numero": user[3]
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
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conn.cursor()
        query = """
            INSERT INTO estoque (produto, preco, marca, cor, codigo, quantidade, condicao, peso, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            dados['produto'],
            dados['preco'],
            dados['marca'],
            dados['cor'],
            dados['codigo'],
            dados['quantidade'],
            dados['condicao'],
            dados['peso'],
            dados.get('observacoes', '')
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'mensagem': 'Produto cadastrado com sucesso!'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para deletar um produto do estoque
@app.route('/estoque/deletar/<string:codigo>', methods=['DELETE'])
def deletar_produto(codigo):    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conn.cursor()
        cursor.execute("DELETE FROM estoque WHERE codigo = %s", (codigo,))
        if cursor.rowcount == 0:
            return jsonify({'erro': 'Produto não encontrado'}), 404
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'mensagem': 'Produto deletado com sucesso!'})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para editar um produto do estoque
@app.route('/estoque/editar/<string:codigo>', methods=['PUT'])
def editar_produto(codigo):
    dados = request.json
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conn.cursor()
        query = """
            UPDATE estoque
            SET produto = %s, preco = %s, marca = %s, cor = %s, quantidade = %s, condicao = %s, peso = %s, observacoes = %s
            WHERE codigo = %s
        """
        cursor.execute(query, (
            dados.get('produto'),
            dados.get('preco'),
            dados.get('marca'),
            dados.get('cor'),
            dados.get('quantidade'),
            dados.get('condicao'),
            dados.get('peso'),
            dados.get('observacoes'),
            codigo
        ))
        if cursor.rowcount == 0:
            return jsonify({'erro': 'Produto não encontrado'}), 404
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'mensagem': 'Produto atualizado com sucesso!'})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para listar todos os produtos no estoque
@app.route('/estoque/listar', methods=['GET'])
def listar_produtos():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT produto, preco, marca, cor, codigo, quantidade, condicao, peso, observacoes FROM estoque")
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()

        produtos_lista = [
            {
                'produto': produto[0],
                'preco': produto[1],
                'marca': produto[2],
                'cor': produto[3],
                'codigo': produto[4],
                'quantidade': produto[5],
                'condicao': produto[6],
                'peso': produto[7],
                'observacoes': produto[8]
            } for produto in produtos
        ]
        return jsonify(produtos_lista)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/estoque/produto/<string:codigo>', methods=['GET'])
def buscar_produto(codigo):
    try:
        # Conexão com o banco de dados
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conn.cursor()

        # Consulta SQL para buscar o produto pelo código
        query = """
            SELECT produto, preco, marca, cor, codigo, quantidade, condicao, peso, observacoes
            FROM estoque
            WHERE codigo = %s
        """
        cursor.execute(query, (codigo,))
        produto = cursor.fetchone()

        # Fechar a conexão com o banco
        cursor.close()
        conn.close()

        # Se o produto não for encontrado
        if not produto:
            return jsonify({"error": "Produto não encontrado"}), 404

        # Retornar os dados do produto como JSON
        produto_data = {
            "produto": produto[0],
            "preco": produto[1],
            "marca": produto[2],
            "cor": produto[3],
            "codigo": produto[4],
            "quantidade": produto[5],
            "condicao": produto[6],
            "peso": produto[7],
            "observacoes": produto[8]
        }
        return jsonify({"produto": produto_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

app.run(
    host='0.0.0.0',
    port=5000,
    #ssl_context = ('/etc/ssl/server.crt', '/etc/ssl/server.key'),
    debug=True
)
