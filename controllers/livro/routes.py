from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import mysql

livro_bp = Blueprint('livro_bp', __name__)

@livro_bp.route('/')
def view_livros():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    cursor.close()
    return render_template('view_livros.html', livros=livros)

@livro_bp.route('/add', methods=['GET', 'POST'])
def add_livro():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano = request.form['ano']

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO livros (titulo, autor, ano) VALUES (%s, %s, %s)', (titulo, autor, ano))
        mysql.connection.commit()
        cursor.close()

        flash('Livro adicionado com sucesso!', 'success')
        return redirect(url_for('livro_bp.view_livros'))
    return render_template('add_livro.html')
