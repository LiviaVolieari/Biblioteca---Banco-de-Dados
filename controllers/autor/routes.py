from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from config import mysql

autor_bp = Blueprint('autor_bp', __name__)

@autor_bp.route('/')
def view_autores():
    if not mysql:
        flash('Conexão com o banco indisponível.', 'warning')
        return render_template('view_autores.html', autores=[])

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM autores ORDER BY nome_autor ASC;")
    autores = cursor.fetchall()
    cursor.close()
    return render_template('view_autores.html', autores=autores)

@autor_bp.route('/add', methods=['GET', 'POST'])
def add_autor():
    if not mysql:
        flash('Erro: sem conexão com o banco.', 'danger')
        return render_template('add_autor.html')

    if request.method == 'POST':
        try:
            nome_autor = request.form['nome_autor']
            nacionalidade = request.form['nacionalidade']
            data_nascimento = request.form['data_nascimento']
            biografia = request.form['biografia']

            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO autores (nome_autor, nacionalidade, data_nascimento, biografia)
                VALUES (%s, %s, %s, %s)
            """, (nome_autor, nacionalidade, data_nascimento, biografia))
            mysql.connection.commit()
            cursor.close()
            flash('Autor adicionado com sucesso!', 'success')
            return redirect(url_for('autor_bp.view_autores'))

        except Exception as e:
            try:
                mysql.connection.rollback()
            except:
                pass
            flash('Erro ao adicionar autor: ' + str(e), 'danger')
            return render_template('add_autor.html')

    return render_template('add_autor.html')

@autor_bp.route('/edit/<int:id_autor>', methods=['GET', 'POST'])
def edit_autor(id_autor):
    if not mysql:
        flash('Erro: conexão com o banco indisponível.', 'danger')
        return redirect(url_for('autor_bp.view_autores'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM autores WHERE id_autor = %s", (id_autor,))
    autor = cursor.fetchone()

    if request.method == 'POST':
        try:
            nome_autor = request.form['nome_autor']
            nacionalidade = request.form['nacionalidade']
            data_nascimento = request.form['data_nascimento']
            biografia = request.form['biografia']

            cursor.execute("""
                UPDATE autores
                SET nome_autor = %s, nacionalidade = %s, data_nascimento = %s, biografia = %s
                WHERE id_autor = %s
            """, (nome_autor, nacionalidade, data_nascimento, biografia, id_autor))
            mysql.connection.commit()
            cursor.close()
            flash('Autor atualizado com sucesso!', 'success')
            return redirect(url_for('autor_bp.view_autores'))

        except Exception as e:
            try:
                mysql.connection.rollback()
            except:
                pass
            flash('Erro ao atualizar autor: ' + str(e), 'danger')
            return render_template('edit_autor.html', autor=autor)

    cursor.close()
    return render_template('edit_autor.html', autor=autor)

@autor_bp.route('/delete/<int:id_autor>')
def delete_autor(id_autor):
    if not mysql:
        flash('Erro: sem conexão com o banco.', 'danger')
        return redirect(url_for('autor_bp.view_autores'))

    try:
        cursor = mysql.connection.cursor()
        # Verifica se o autor tem livros vinculados
        cursor.execute("SELECT COUNT(*) AS total FROM livros WHERE autor_id = %s", (id_autor,))
        tem_livros = cursor.fetchone()['total']

        if tem_livros > 0:
            flash('Não é possível excluir este autor: ele possui livros cadastrados.', 'warning')
            cursor.close()
            return redirect(url_for('autor_bp.view_autores'))

        # Caso não tenha livros, pode excluir
        cursor.execute('DELETE FROM autores WHERE id_autor = %s', (id_autor,))
        mysql.connection.commit()
        cursor.close()
        flash('Autor excluído com sucesso!', 'info')

    except Exception as e:
        try:
            mysql.connection.rollback()
        except:
            pass
        flash('Erro ao excluir autor: ' + str(e), 'danger')

    return redirect(url_for('autor_bp.view_autores'))

