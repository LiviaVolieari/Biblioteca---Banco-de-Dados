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

@livro_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_livro(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM livros WHERE id=%s', (id,))
    livro = cursor.fetchone()

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano = request.form['ano']

        cursor.execute('UPDATE livros SET titulo=%s, autor=%s, ano=%s WHERE id=%s', (titulo, autor, ano, id))
        mysql.connection.commit()
        cursor.close()

        flash('Livro atualizado com sucesso!', 'success')
        return redirect(url_for('livro_bp.view_livros'))

    cursor.close()
    return render_template('edit_livro.html', livro=livro)


@livro_bp.route('/delete/<int:id>')
def delete_livro(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM livros WHERE id=%s', (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Livro removido com sucesso!', 'info')
    return redirect(url_for('livro_bp.view_livros'))

