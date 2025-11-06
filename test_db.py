from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_atividade17'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT NOW()')
    data = cur.fetchone()
    return f"Conexão bem-sucedida! Hora do MySQL: {data[0]}"

if __name__ == '__main__':
    app.run(debug=True)