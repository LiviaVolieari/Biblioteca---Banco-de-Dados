import MySQLdb
import os

HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
PORT = int(os.environ.get('MYSQL_PORT', 3306))
USER = os.environ.get('MYSQL_USER', 'root')
PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
DB = os.environ.get('MYSQL_DB', 'biblioteca')

print(f'Tentando conectar em {HOST}:{PORT} como {USER} ao DB {DB!r}')
try:
    conn = MySQLdb.connect(host=HOST, port=PORT, user=USER, passwd=PASSWORD, db=DB)
    print('Conexão bem-sucedida')
    conn.close()
except Exception as e:
    print('Falha ao conectar:', type(e).__name__, e)
    print('\nSugestões:')
    print('- Verifique usuário/senha e a porta do MySQL.')
    print('- Tente conectar pelo cliente mysql: mysql -u', USER, '-p -h', HOST, '-P', str(PORT))
    print('- Se estiver usando XAMPP, confirme a porta no painel do XAMPP.')
