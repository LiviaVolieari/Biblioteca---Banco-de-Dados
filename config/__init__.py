from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'chave_super_segura'  # Necessária para flash messages e sessões
# Configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sua_senha_aqui'
app.config['MYSQL_DB'] = 'biblioteca'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Importa e registra os blueprints (rotas)
from controllers.main.routes import main_bp
from controllers.auth.routes import auth_bp
from controllers.livro.routes import livro_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(livro_bp, url_prefix='/livros')
