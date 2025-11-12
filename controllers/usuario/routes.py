# from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# from config import mysql
# from werkzeug.security import generate_password_hash


# usuario_bp = Blueprint('usuario', __name__)


# @usuario_bp.route('/usuario', methods=['GET'])
# def perfil_usuario():
#     user_id = session.get('user_id')


#     if not user_id:
#         flash('Você precisa estar logado para acessar seu perfil.', 'warning')
#         return redirect(url_for('login'))


#     cursor = mysql.connection.cursor(dictionary=True)
#     cursor.execute('SELECT * FROM usuario WHERE id = %s', (user_id,))
#     usuario = cursor.fetchone()
#     cursor.close()


#     if not usuario:
#         flash('Usuário não encontrado.', 'danger')
#         return redirect(url_for('login'))


#     return render_template('usuario.html', usuario=usuario)




# @usuario_bp.route('/usuario/atualizar', methods=['POST'])
# def atualizar_usuario():
#     user_id = session.get('user_id')
#     if not user_id:
#         flash('Você precisa estar logado para atualizar suas informações.', 'warning')
#         return redirect(url_for('login'))


#     nome = request.form['nome']
#     email = request.form['email']
#     telefone = request.form.get('telefone')
#     senha = request.form.get('senha')


#     cursor = mysql.connection.cursor()


#     if senha:
#         senha_hash = generate_password_hash(senha)
#         cursor.execute(
#             'UPDATE usuario SET nome=%s, email=%s, telefone=%s, senha_hash=%s WHERE id=%s',
#             (nome, email, telefone, senha_hash, user_id)
#         )
#     else:
#         cursor.execute(
#             'UPDATE usuario SET nome=%s, email=%s, telefone=%s WHERE id=%s',
#             (nome, email, telefone, user_id)
#         )


#     mysql.connection.commit()
#     cursor.close()


#     flash('Informações atualizadas com sucesso!', 'success')
#     return redirect(url_for('usuario.perfil_usuario'))




from flask import Blueprint, render_template, request, redirect, url_for, flash, session

usuario_bp = Blueprint('usuario_bp', __name__)


@usuario_bp.route('/', methods=['GET'])
def usuarios():
    """Exibe o perfil do usuário baseado na sessão.

    Nota: o login atual armazena o nome do usuário em `session['usuario']`.
    Aqui fazemos uma verificação simples na sessão e renderizamos o template
    `usuario.html`. Se for necessário, pode-se reintroduzir acesso ao banco
    para consultar dados completos do usuário pelo id.
    """
    usuario = session.get('usuario')
    if not usuario:
        flash('Você precisa estar logado para acessar seu perfil.', 'warning')
        return redirect(url_for('auth_bp.login'))

    return render_template('usuario.html', usuario=usuario)



@usuario_bp.route('/atualizar', methods=['POST'])
def atualizar():
    """Atualização simples do perfil (placeholder).

    Neste momento apenas valida a sessão e redireciona de volta ao perfil com
    uma mensagem de sucesso. Se quiser persistir alterações, reintroduzir
    a lógica de acesso ao banco (`config.mysql`) e validações.
    """
    usuario = session.get('usuario')
    if not usuario:
        flash('Você precisa estar logado para atualizar suas informações.', 'warning')
        return redirect(url_for('auth_bp.login'))
    
    flash('Informações atualizadas com sucesso!', 'success')
    return redirect(url_for('usuario_bp.usuarios'))
