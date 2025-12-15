from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from config import mysql

emprestimo_bp = Blueprint('emprestimo_bp', __name__)

@emprestimo_bp.route('/')
def view_emprestimos():
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return render_template('view_emprestimos.html', emprestimos=[])

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT 
            e.id_emprestimo,
            u.nome AS nome_usuario,
            l.titulo AS titulo_livro,
            e.data_emprestimo,
            e.data_devolucao_prevista,
            e.data_devolucao_real,
            e.status_emprestimo
        FROM emprestimos e
        LEFT JOIN usuarios u ON e.usuario_id = u.id
        LEFT JOIN livros l ON e.livro_id = l.id
        ORDER BY e.data_emprestimo DESC;
    """)
    emprestimos = cursor.fetchall()
    cursor.close()
    return render_template('view_emprestimos.html', emprestimos=emprestimos)

@emprestimo_bp.route('/add', methods=['GET', 'POST'])
def add_emprestimo():
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return redirect(url_for('emprestimo_bp.view_emprestimos'))

    cursor = mysql.connection.cursor()

    # Carregar usuários e livros para os <select>
    cursor.execute("SELECT id, nome FROM usuarios;")
    usuarios = cursor.fetchall()
    cursor.execute("SELECT id, titulo FROM livros;")
    livros = cursor.fetchall()

    if request.method == 'POST':
        try:
            usuario_id = request.form['usuario_id']
            livro_id = request.form['livro_id']
            data_emprestimo = request.form['data_emprestimo']
            data_devolucao_prevista = request.form['data_devolucao_prevista']
            status = request.form['status_emprestimo']
            if status not in ['pendente', 'devolvido', 'atrasado']:
                flash(
                    'Status inválido informado. O sistema ajustou automaticamente.',
                    'warning'
                ) #MUDEI

            cursor.execute("""
                INSERT INTO emprestimos (usuario_id, livro_id, data_emprestimo, data_devolucao_prevista, status_emprestimo)
                VALUES (%s, %s, %s, %s, %s)
            """, (usuario_id, livro_id, data_emprestimo, data_devolucao_prevista, status))
            mysql.connection.commit()

            flash('Empréstimo registrado com sucesso!', 'success')
            return redirect(url_for('emprestimo_bp.view_emprestimos'))
        except Exception as e:
            mysql.connection.rollback()
            flash(str(e), 'danger') #TAVA FEIO

    cursor.close()
    return render_template('add_emprestimo.html', usuarios=usuarios, livros=livros)

@emprestimo_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_emprestimo(id):
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return redirect(url_for('emprestimo_bp.view_emprestimos'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT * FROM emprestimos WHERE id_emprestimo = %s
    """, (id,))
    emprestimo = cursor.fetchone()

    cursor.execute("SELECT id, nome FROM usuarios;")
    usuarios = cursor.fetchall()
    cursor.execute("SELECT id, titulo FROM livros;")
    livros = cursor.fetchall()

    if request.method == 'POST':
        try:
            usuario_id = request.form['usuario_id']
            livro_id = request.form['livro_id']
            data_emprestimo = request.form['data_emprestimo']
            data_prevista = request.form['data_devolucao_prevista']
            data_real = request.form.get('data_devolucao_real') or None
            status = request.form['status_emprestimo']

            cursor.execute("""
                UPDATE emprestimos
                SET usuario_id = %s,
                    livro_id = %s,
                    data_emprestimo = %s,
                    data_devolucao_prevista = %s,
                    data_devolucao_real = %s,
                    status_emprestimo = %s
                WHERE id_emprestimo = %s
            """, (usuario_id, livro_id, data_emprestimo, data_prevista, data_real, status, id))
            mysql.connection.commit()

            flash('Empréstimo atualizado com sucesso!', 'success')
            return redirect(url_for('emprestimo_bp.view_emprestimos'))
        except Exception as e:
            mysql.connection.rollback()
            flash(str(e), 'danger')

    cursor.close()
    return render_template('edit_emprestimo.html', emprestimo=emprestimo, usuarios=usuarios, livros=livros)

@emprestimo_bp.route('/delete/<int:id>')
def delete_emprestimo(id):
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível.', 'danger')
        return redirect(url_for('emprestimo_bp.view_emprestimos'))

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM emprestimos WHERE id_emprestimo = %s", (id,))
        mysql.connection.commit()
        flash('Empréstimo excluído com sucesso!', 'info')
    except Exception as e:
        mysql.connection.rollback()
        flash(str(e), 'danger')
    finally:
        cursor.close()

    return redirect(url_for('emprestimo_bp.view_emprestimos'))
