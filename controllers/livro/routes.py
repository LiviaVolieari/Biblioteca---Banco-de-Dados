from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from config import mysql

livro_bp = Blueprint('livro_bp', __name__)

@livro_bp.route('/')
def view_livros():
    if not mysql:
        # Se o banco estiver indisponível, mostra mensagem e retorna lista vazia
        flash('Atenção: conexão com o banco de dados indisponível.', 'warning')
        return render_template('view_livros.html', livros=[])

    cursor = mysql.connection.cursor()
    cursor.execute("""
    SELECT 
        livros.id,
        livros.titulo,
        autores.nome_autor,
        generos.nome_genero,
        editoras.nome_editora,
        livros.ano,
        livros.isbn,
        livros.quantidade
    FROM livros
    LEFT JOIN autores ON livros.autor_id = autores.id_autor
    LEFT JOIN generos ON livros.genero_id = generos.id_genero
    LEFT JOIN editoras ON livros.editora_id = editoras.id_editora;
    """)
    livros = cursor.fetchall()
    cursor.close()
    return render_template('view_livros.html', livros=livros)

@livro_bp.route('/add', methods=['GET', 'POST'])
def add_livro():
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível. Não é possível adicionar livros.', 'danger')
        return render_template('add_livro.html')

    if request.method == 'POST':
        cursor = None
        try:
            cursor = mysql.connection.cursor()

            titulo = request.form['titulo']
            ano = request.form['ano']
            isbn = request.form['isbn']
            resumo = request.form['resumo']

            # 🔹 Quantidade (deixa o trigger agir se vier vazia)
            quantidade = request.form.get('quantidade')
            if not quantidade:
                flash(
                    'Quantidade não informada. O sistema definiu automaticamente o valor padrão (1).',
                    'info'
                )
                quantidade = None  # IMPORTANTE: deixa o trigger funcionar

            nome_autor = request.form['autor'].strip()
            nome_genero = request.form['genero'].strip()
            nome_editora = request.form['editora'].strip()

            # 🔹 Autor
            cursor.execute("SELECT id_autor FROM autores WHERE nome_autor = %s", (nome_autor,))
            autor = cursor.fetchone()
            if autor:
                autor_id = autor['id_autor']
            else:
                cursor.execute(
                    "INSERT INTO autores (nome_autor) VALUES (%s)",
                    (nome_autor,)
                )
                mysql.connection.commit()
                autor_id = cursor.lastrowid

            # 🔹 Gênero
            cursor.execute("SELECT id_genero FROM generos WHERE nome_genero = %s", (nome_genero,))
            genero = cursor.fetchone()
            if genero:
                genero_id = genero['id_genero']
            else:
                cursor.execute(
                    "INSERT INTO generos (nome_genero) VALUES (%s)",
                    (nome_genero,)
                )
                mysql.connection.commit()
                genero_id = cursor.lastrowid

            # 🔹 Editora
            cursor.execute("SELECT id_editora FROM editoras WHERE nome_editora = %s", (nome_editora,))
            editora = cursor.fetchone()
            if editora:
                editora_id = editora['id_editora']
            else:
                cursor.execute(
                    "INSERT INTO editoras (nome_editora) VALUES (%s)",
                    (nome_editora,)
                )
                mysql.connection.commit()
                editora_id = cursor.lastrowid

            # 🔹 Insere o livro
            cursor.execute("""
                INSERT INTO livros 
                (titulo, ano, isbn, quantidade, resumo, autor_id, genero_id, editora_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                titulo,
                ano,
                isbn,
                quantidade,
                resumo,
                autor_id,
                genero_id,
                editora_id
            ))

            mysql.connection.commit()
            cursor.close()

            flash('Livro cadastrado com sucesso!', 'success')
            return redirect(url_for('livro_bp.view_livros'))

        except Exception as e:
            if cursor:
                cursor.close()
            mysql.connection.rollback()
            flash('Erro ao salvar livro: ' + str(e), 'danger')
            return render_template('add_livro.html')

    return render_template('add_livro.html')

# def add_livro():
#     if not mysql:
#         flash('Erro: conexão com o banco de dados indisponível. Não é possível adicionar livros.', 'danger')
#         return render_template('add_livro.html')

#     if request.method == 'POST':
#         try:
#             cursor = mysql.connection.cursor()
#             titulo = request.form['titulo']
#             ano = request.form['ano']
#             isbn = request.form['isbn']
#             quantidade = request.form['quantidade']
#             resumo = request.form['resumo']

#             nome_autor = request.form['autor'].strip()
#             nome_genero = request.form['genero'].strip()
#             nome_editora = request.form['editora'].strip()

#             # Autor — insere se não existir
#             cursor.execute("SELECT id_autor FROM autores WHERE nome_autor = %s", (nome_autor,))
#             autor = cursor.fetchone()
#             if autor:
#                 autor_id = autor['id_autor']
#             else:
#                 cursor.execute("INSERT INTO autores (nome_autor) VALUES (%s)", (nome_autor,))
#                 mysql.connection.commit()
#                 autor_id = cursor.lastrowid  # pega o id recém-criado

#             # Gênero — insere se não existir
#             cursor.execute("SELECT id_genero FROM generos WHERE nome_genero = %s", (nome_genero,))
#             genero = cursor.fetchone()
#             if genero:
#                 genero_id = genero['id_genero']
#             else:
#                 cursor.execute("INSERT INTO generos (nome_genero) VALUES (%s)", (nome_genero,))
#                 mysql.connection.commit()
#                 genero_id = cursor.lastrowid

#             # Editora — insere se não existir
#             cursor.execute("SELECT id_editora FROM editoras WHERE nome_editora = %s", (nome_editora,))
#             editora = cursor.fetchone()
#             if editora:
#                 editora_id = editora['id_editora']
#             else:
#                 cursor.execute("INSERT INTO editoras (nome_editora) VALUES (%s)", (nome_editora,))
#                 mysql.connection.commit()
#                 editora_id = cursor.lastrowid

#             # Agora insere o livro com os IDs corretos
#             cursor.execute("""
#                 INSERT INTO livros (titulo, ano, isbn, quantidade, resumo, autor_id, genero_id, editora_id)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#             """, (titulo, ano, isbn, quantidade, resumo, autor_id, genero_id, editora_id))

#             mysql.connection.commit()
#             cursor.close()
#             flash('Livro com sucesso!', 'success')
#             return redirect(url_for('livro_bp.view_livros'))
#         except Exception as e:
#             # tenta dar rollback e fecha cursor se necessário
#             try:
#                 current_app.logger.exception('Erro ao inserir livro')
#             except Exception:
#                 pass
#             try:
#                 mysql.connection.rollback()
#             except Exception:
#                 pass
#             try:
#                 cursor.close()
#             except Exception:
#                 pass
#             flash('Erro ao salvar livro: ' + str(e), 'danger')
#             return render_template('add_livro.html')

#     return render_template('add_livro.html')


@livro_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_livro(id):
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível. Não é possível editar livros.', 'danger')
        return redirect(url_for('livro_bp.view_livros'))

    cursor = mysql.connection.cursor()

    # Busca o livro atual
    cursor.execute("""
        SELECT 
            livros.id,
            livros.titulo,
            livros.ano,
            livros.isbn,
            livros.quantidade,
            livros.resumo,
            autores.nome_autor,
            generos.nome_genero,
            editoras.nome_editora
        FROM livros
        LEFT JOIN autores ON livros.autor_id = autores.id_autor
        LEFT JOIN generos ON livros.genero_id = generos.id_genero
        LEFT JOIN editoras ON livros.editora_id = editoras.id_editora
        WHERE livros.id = %s
    """, (id,))
    livro = cursor.fetchone()

    if request.method == 'POST':
        try:
            titulo = request.form['titulo']
            ano = request.form['ano']
            isbn = request.form['isbn']
            quantidade = request.form['quantidade']
            resumo = request.form['resumo']

            nome_autor = request.form['autor'].strip()
            nome_genero = request.form['genero'].strip()
            nome_editora = request.form['editora'].strip()

            cursor.execute("SELECT id_autor FROM autores WHERE nome_autor = %s", (nome_autor,))
            autor = cursor.fetchone()
            if autor:
                autor_id = autor['id_autor']
            else:
                cursor.execute("INSERT INTO autores (nome_autor) VALUES (%s)", (nome_autor,))
                mysql.connection.commit()
                autor_id = cursor.lastrowid

            cursor.execute("SELECT id_genero FROM generos WHERE nome_genero = %s", (nome_genero,))
            genero = cursor.fetchone()
            if genero:
                genero_id = genero['id_genero']
            else:
                cursor.execute("INSERT INTO generos (nome_genero) VALUES (%s)", (nome_genero,))
                mysql.connection.commit()
                genero_id = cursor.lastrowid

            cursor.execute("SELECT id_editora FROM editoras WHERE nome_editora = %s", (nome_editora,))
            editora = cursor.fetchone()
            if editora:
                editora_id = editora['id_editora']
            else:
                cursor.execute("INSERT INTO editoras (nome_editora) VALUES (%s)", (nome_editora,))
                mysql.connection.commit()
                editora_id = cursor.lastrowid

            # Atualiza o livro
            cursor.execute("""
                UPDATE livros
                SET titulo = %s, ano = %s, isbn = %s, quantidade = %s, resumo = %s,
                    autor_id = %s, genero_id = %s, editora_id = %s
                WHERE id = %s
            """, (titulo, ano, isbn, quantidade, resumo, autor_id, genero_id, editora_id, id))

            mysql.connection.commit()
            cursor.close()
            flash('Livro atualizado com sucesso!', 'success')
            return redirect(url_for('livro_bp.view_livros'))
        except Exception as e:
            try:
                current_app.logger.exception('Erro ao atualizar livro')
            except Exception:
                pass
            try:
                mysql.connection.rollback()
            except Exception:
                pass
            try:
                cursor.close()
            except Exception:
                pass
            flash('Erro ao atualizar livro: ' + str(e), 'danger')
            return render_template('edit_livro.html', livro=livro)

    cursor.close()
    return render_template('edit_livro.html', livro=livro)



@livro_bp.route('/delete/<int:id>')
def delete_livro(id):
    if not mysql:
        flash('Erro: conexão com o banco de dados indisponível. Não foi possível remover o livro.', 'danger')
        return redirect(url_for('livro_bp.view_livros'))

    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM livros WHERE id=%s', (id,))
        mysql.connection.commit()
        cursor.close()
        flash('Livro removido com sucesso!', 'info')
    except Exception as e:
        try:
            current_app.logger.exception('Erro ao remover livro')
        except Exception:
            pass
        try:
            mysql.connection.rollback()
        except Exception:
            pass
        try:
            cursor.close()
        except Exception:
            pass
        flash('Erro ao remover livro ', 'danger')

    return redirect(url_for('livro_bp.view_livros'))

