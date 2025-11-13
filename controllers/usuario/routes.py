from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from config import mysql

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/')
def view_usuarios():
    if not mysql:
        flash('Atenção: conexão com o banco de dados indisponível.', 'warning')
        return render_template('view_usuarios.html', usuarios=[])

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nome, email FROM usuarios ORDER BY nome ASC;")
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('view_usuarios.html', usuarios=usuarios)

@usuario_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_usuario(id):
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return redirect(url_for('usuario_bp.view_usuarios'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nome, email, senha FROM usuarios WHERE id = %s;", (id,))
    usuario = cursor.fetchone()

    if not usuario:
        flash('Usuário não encontrado.', 'warning')
        cursor.close()
        return redirect(url_for('usuario_bp.view_usuarios'))

    if request.method == 'POST':
        try:
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']

            cursor.execute("""
                UPDATE usuarios
                SET nome = %s, email = %s, senha = %s
                WHERE id = %s
            """, (nome, email, senha, id))

            mysql.connection.commit()
            cursor.close()
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('usuario_bp.view_usuarios'))

        except Exception as e:
            try:
                mysql.connection.rollback()
            except:
                pass
            flash('Erro ao atualizar usuário: ' + str(e), 'danger')
            return render_template('edit_usuario.html', usuario=usuario)

    cursor.close()
    return render_template('edit_usuario.html', usuario=usuario)

@usuario_bp.route('/delete/<int:id>')
def delete_usuario(id):
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return redirect(url_for('usuario_bp.view_usuarios'))

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        flash('Usuário removido com sucesso!', 'info')

    except Exception as e:
        try:
            mysql.connection.rollback()
        except:
            pass
        flash('Erro ao remover usuário: ' + str(e), 'danger')

    return redirect(url_for('usuario_bp.view_usuarios'))
