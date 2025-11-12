from flask import Flask
from flask_mysqldb import MySQL
import os

import os.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'style')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'chave_super_segura')  

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')  #aqui poem a senha
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'biblioteca')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

try:
    mysql = MySQL(app)
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
    mysql = MySQL(app)

# Importa e registra os blueprints (as rotas)
from controllers.main.routes import main_bp
from controllers.auth.routes import auth_bp
from controllers.livro.routes import livro_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(livro_bp, url_prefix='/livros')
