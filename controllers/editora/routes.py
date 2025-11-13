from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import mysql

editora_bp = Blueprint('editora_bp', __name__)

@editora_bp.route('/')
def view_editoras():
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'warning')
        return render_template('view_editoras.html', editoras=[])
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM editoras ORDER BY nome_editora ASC")
    editoras = cursor.fetchall()
    cursor.close()
    return render_template('view_editoras.html', editoras=editoras)

@editora_bp.route('/add', methods=['GET', 'POST'])
def add_editora():
    if request.method == 'POST':
        nome_editora = request.form['nome_editora']
        endereco_editora = request.form['endereco_editora']

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO editoras (nome_editora, endereco_editora) VALUES (%s, %s)",
                (nome_editora, endereco_editora),
            )
            mysql.connection.commit()
            cursor.close()
            flash('Editora adicionada com sucesso!', 'success')
            return redirect(url_for('editora_bp.view_editoras'))
        except Exception as e:
            mysql.connection.rollback()
            flash('Erro ao adicionar editora: ' + str(e), 'danger')
    return render_template('add_editora.html')

@editora_bp.route('/edit/<int:id_editora>', methods=['GET', 'POST'])
def edit_editora(id_editora):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM editoras WHERE id_editora = %s", (id_editora,))
    editora = cursor.fetchone()

    if not editora:
        flash('Editora não encontrada.', 'warning')
        return redirect(url_for('editora_bp.view_editoras'))

    if request.method == 'POST':
        nome_editora = request.form['nome_editora']
        endereco_editora = request.form['endereco_editora']
        try:
            cursor.execute(
                "UPDATE editoras SET nome_editora = %s, endereco_editora = %s WHERE id_editora = %s",
                (nome_editora, endereco_editora, id_editora),
            )
            mysql.connection.commit()
            cursor.close()
            flash('Editora atualizada com sucesso!', 'success')
            return redirect(url_for('editora_bp.view_editoras'))
        except Exception as e:
            mysql.connection.rollback()
            flash('Erro ao atualizar editora: ' + str(e), 'danger')

    cursor.close()
    return render_template('edit_editora.html', editora=editora)

@editora_bp.route('/delete/<int:id_editora>')
def delete_editora(id_editora):
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return redirect(url_for('editora_bp.view_editoras'))

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT COUNT(*) AS total FROM livros WHERE editora_id = %s", (id_editora,))
        total = cursor.fetchone()['total']

        if total > 0:
            flash('Não é possível excluir esta editora: existem livros associados.', 'warning')
            cursor.close()
            return redirect(url_for('editora_bp.view_editoras'))
        
        cursor.execute("DELETE FROM editoras WHERE id_editora = %s", (id_editora,))
        mysql.connection.commit()
        cursor.close()

        flash('Editora removida com sucesso!', 'info')

    except Exception as e:
        mysql.connection.rollback()
        flash('Erro ao remover editora: ' + str(e), 'danger')

    return redirect(url_for('editora_bp.view_editoras'))
