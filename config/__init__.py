from flask import Flask
from flask_mysqldb import MySQL
import os

# Permite configuração via variáveis de ambiente para facilitar execução local
import os.path

# Diretório base do projeto (pasta acima da pasta `config`)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Atribui paths absolutos para templates e static para evitar problemas com o package `config`
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'style')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'chave_super_segura')  # Necessária para flash messages e sessões

# Configuração do MySQL - compatível com XAMPP e MySQL standalone
# XAMPP: usa root sem senha na porta 3306
# MySQL: usa a senha definida durante a instalação
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '1234')  

# vazio é padrão XAMPP, defina via env se usar MySQL
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'biblioteca')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Melhor tratamento de erros de conexão
try:
    mysql = MySQL(app)
    # Testa a conexão
    with app.app_context():
        mysql.connection.ping()
except Exception as e:
    print('\nErro ao conectar ao MySQL:')
    print('1. Verifique se o MySQL está rodando (XAMPP ou serviço MySQL)')
    print('2. Confira as credenciais:')
    print(f'   - Host: {app.config["MYSQL_HOST"]}:{app.config["MYSQL_PORT"]}')
    print(f'   - Usuário: {app.config["MYSQL_USER"]}')
    print('   - Senha:', 'vazia' if not app.config["MYSQL_PASSWORD"] else 'definida')
    print('3. O banco "biblioteca" precisa existir. Crie com:')
    print('   mysql -u root -p < database/schema.sql')
    print('\nDetalhes do erro:', str(e))
    # Continua a execução, mas as rotas que usam DB vão falhar
    mysql = MySQL(app)

# Importa e registra os blueprints (rotas)
from controllers.main.routes import main_bp
from controllers.auth.routes import auth_bp
from controllers.livro.routes import livro_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(livro_bp, url_prefix='/livros')
