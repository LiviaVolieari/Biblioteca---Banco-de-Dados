from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from config import mysql

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email=%s AND senha=%s', (email, senha))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['usuario'] = user['nome']
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

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)', (nome, email, senha))
        mysql.connection.commit()
        cursor.close()

        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html')
