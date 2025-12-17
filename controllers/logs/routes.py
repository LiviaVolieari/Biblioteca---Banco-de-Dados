from flask import Blueprint, render_template, flash, current_app
from config import mysql
from flask_login import login_required
from MySQLdb.cursors import DictCursor

logs_bp = Blueprint('logs_bp', __name__)

@logs_bp.route('/logs')
@login_required
def view_logs():
    if not mysql:
        flash('Erro: não foi possível conectar ao banco de dados.', 'danger')
        return render_template('logs.html', logs=[])

    try:
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("""
            SELECT 
                l.tabela_afetada,
                l.operacao,
                u.nome AS usuario_nome,
                l.data_operacao,
                l.dados_anteriores,
                l.dados_novos
            FROM auditoria_logs l
            LEFT JOIN usuarios u ON u.id = l.usuario_responsavel
            ORDER BY l.data_operacao DESC
        """)

        logs = cursor.fetchall()
        cursor.close()
    except Exception as e:
        current_app.logger.exception('Erro ao buscar logs de auditoria')
        flash('Erro ao buscar logs: ' + str(e), 'danger')
        logs = []

    return render_template('logs.html', logs=logs)
