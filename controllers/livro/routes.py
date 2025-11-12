from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import mysql

livro_bp = Blueprint('livro_bp', __name__)

@livro_bp.route('/')
def view_livros():
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
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        titulo = request.form['titulo']
        ano = request.form['ano']
        isbn = request.form['isbn']
        quantidade = request.form['quantidade']
        resumo = request.form['resumo']

        nome_autor = request.form['autor'].strip()
        nome_genero = request.form['genero'].strip()
        nome_editora = request.form['editora'].strip()

        # 1️⃣ Autor — insere se não existir
        cursor.execute("SELECT id_autor FROM autores WHERE nome_autor = %s", (nome_autor,))
        autor = cursor.fetchone()
        if autor:
            autor_id = autor['id_autor']
        else:
            cursor.execute("INSERT INTO autores (nome_autor) VALUES (%s)", (nome_autor,))
            mysql.connection.commit()
            autor_id = cursor.lastrowid  # pega o id recém-criado

        # 2️⃣ Gênero — insere se não existir
        cursor.execute("SELECT id_genero FROM generos WHERE nome_genero = %s", (nome_genero,))
        genero = cursor.fetchone()
        if genero:
            genero_id = genero['id_genero']
        else:
            cursor.execute("INSERT INTO generos (nome_genero) VALUES (%s)", (nome_genero,))
            mysql.connection.commit()
            genero_id = cursor.lastrowid

        # 3️⃣ Editora — insere se não existir
        cursor.execute("SELECT id_editora FROM editoras WHERE nome_editora = %s", (nome_editora,))
        editora = cursor.fetchone()
        if editora:
            editora_id = editora['id_editora']
        else:
            cursor.execute("INSERT INTO editoras (nome_editora) VALUES (%s)", (nome_editora,))
            mysql.connection.commit()
            editora_id = cursor.lastrowid

        # 4️⃣ Agora insere o livro com os IDs corretos
        cursor.execute("""
            INSERT INTO livros (titulo, ano, isbn, quantidade, resumo, autor_id, genero_id, editora_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (titulo, ano, isbn, quantidade, resumo, autor_id, genero_id, editora_id))

        mysql.connection.commit()
        cursor.close()
        flash('Livro com sucesso!', 'success')
        return redirect(url_for('livro_bp.view_livros'))

    cursor.close()
    return render_template('add_livro.html')


@livro_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_livro(id):
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

    if not livro:
        cursor.close()
        flash('Livro não encontrado!', 'error')
        return redirect(url_for('livro_bp.view_livros'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        ano = request.form['ano']
        isbn = request.form['isbn']
        quantidade = request.form['quantidade']
        resumo = request.form['resumo']

        nome_autor = request.form['autor'].strip()
        nome_genero = request.form['genero'].strip()
        nome_editora = request.form['editora'].strip()

        # 1️⃣ Autor — cria se não existir
        cursor.execute("SELECT id_autor FROM autores WHERE nome_autor = %s", (nome_autor,))
        autor = cursor.fetchone()
        if autor:
            autor_id = autor['id_autor']
        else:
            cursor.execute("INSERT INTO autores (nome_autor) VALUES (%s)", (nome_autor,))
            mysql.connection.commit()
            autor_id = cursor.lastrowid

        # 2️⃣ Gênero — cria se não existir
        cursor.execute("SELECT id_genero FROM generos WHERE nome_genero = %s", (nome_genero,))
        genero = cursor.fetchone()
        if genero:
            genero_id = genero['id_genero']
        else:
            cursor.execute("INSERT INTO generos (nome_genero) VALUES (%s)", (nome_genero,))
            mysql.connection.commit()
            genero_id = cursor.lastrowid

        # 3️⃣ Editora — cria se não existir
        cursor.execute("SELECT id_editora FROM editoras WHERE nome_editora = %s", (nome_editora,))
        editora = cursor.fetchone()
        if editora:
            editora_id = editora['id_editora']
        else:
            cursor.execute("INSERT INTO editoras (nome_editora) VALUES (%s)", (nome_editora,))
            mysql.connection.commit()
            editora_id = cursor.lastrowid

        # 4️⃣ Atualiza o livro
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

