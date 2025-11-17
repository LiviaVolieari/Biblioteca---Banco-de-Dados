from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from config import mysql

genero_bp = Blueprint('genero_bp', __name__)

@genero_bp.route('/')
def view_generos():
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return render_template('view_generos.html', generos=[])

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM generos ORDER BY nome_genero ASC")
    generos = cursor.fetchall()
    cursor.close()
    return render_template('view_generos.html', generos=generos)

@genero_bp.route('/add', methods=['GET', 'POST'])
def add_genero():
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return render_template('add_genero.html')

    if request.method == 'POST':
        nome_genero = request.form['nome_genero'].strip()

        if not nome_genero:
            flash('O nome do gênero é obrigatório.', 'warning')
            return render_template('add_genero.html')

        try:
            cursor = mysql.connection.cursor()
            # Verifica se já existe
            cursor.execute("SELECT id_genero FROM generos WHERE nome_genero = %s", (nome_genero,))
            existente = cursor.fetchone()

            if existente:
                flash('Este gênero já está cadastrado.', 'info')
            else:
                cursor.execute("INSERT INTO generos (nome_genero) VALUES (%s)", (nome_genero,))
                mysql.connection.commit()
                flash('Gênero adicionado com sucesso!', 'success')

            cursor.close()
            return redirect(url_for('genero_bp.view_generos'))

        except Exception as e:
            mysql.connection.rollback()
            flash('Erro ao adicionar gênero: ' + str(e), 'danger')
            return render_template('add_genero.html')

    return render_template('add_genero.html')

@genero_bp.route('/edit/<int:id_genero>', methods=['GET', 'POST'])
def edit_genero(id_genero):
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return redirect(url_for('genero_bp.view_generos'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM generos WHERE id_genero = %s", (id_genero,))
    genero = cursor.fetchone()

    if not genero:
        flash('Gênero não encontrado.', 'warning')
        cursor.close()
        return redirect(url_for('genero_bp.view_generos'))

    if request.method == 'POST':
        nome_genero = request.form['nome_genero'].strip()

        try:
            cursor.execute("UPDATE generos SET nome_genero = %s WHERE id_genero = %s", (nome_genero, id_genero))
            mysql.connection.commit()
            cursor.close()
            flash('Gênero atualizado com sucesso!', 'success')
            return redirect(url_for('genero_bp.view_generos'))
        except Exception as e:
            mysql.connection.rollback()
            cursor.close()
            flash('Erro ao atualizar gênero: ' + str(e), 'danger')

    cursor.close()
    return render_template('edit_genero.html', genero=genero)

@genero_bp.route('/delete/<int:id_genero>')
def delete_genero(id_genero):
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return redirect(url_for('genero_bp.view_generos'))

    try:
        cursor = mysql.connection.cursor()

        # Verifica se há livros usando esse gênero
        cursor.execute("SELECT COUNT(*) AS total FROM livros WHERE genero_id = %s", (id_genero,))
        total = cursor.fetchone()['total']
        if total > 0:
            flash('Não é possível excluir este gênero: existem livros associados.', 'warning')
            cursor.close()
            return redirect(url_for('genero_bp.view_generos'))

        cursor.execute("DELETE FROM generos WHERE id_genero = %s", (id_genero,))
        mysql.connection.commit()
        cursor.close()
        flash('Gênero removido com sucesso!', 'info')

    except Exception as e:
        mysql.connection.rollback()
        flash('Erro ao remover gênero ', 'danger')

    return redirect(url_for('genero_bp.view_generos'))
