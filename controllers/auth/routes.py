from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from config import mysql
from flask_login import login_user, logout_user
from models.user import User


auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # Protege caso o banco esteja indisponível (credenciais/porta incorretas)
        if not mysql:
            flash('Erro: não foi possível conectar ao banco de dados. Verifique as configurações.', 'danger')
            return render_template('login.html')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE email=%s AND senha=%s', (email, senha))
            user = cursor.fetchone()
            cursor.close()
        except Exception as e:
            try:
                current_app.logger.exception('Erro na consulta de login')
            except Exception:
                pass
            flash('Erro ao consultar o banco de dados: ' + str(e), 'danger')
            return render_template('login.html')

        if user:
            usuario = User(user['id'], user['nome'], user['email'])
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main_bp.index'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if not mysql:
            flash('Erro: não foi possível conectar ao banco de dados. Verifique as configurações.', 'danger')
            return render_template('register.html')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)', (nome, email, senha))
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            try:
                current_app.logger.exception('Erro ao registrar usuário')
            except Exception:
                pass
            flash('Erro ao gravar no banco de dados: ' + str(e), 'danger')
            return render_template('register.html')

        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth_bp.login'))