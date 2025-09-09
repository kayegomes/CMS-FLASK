from flask import Blueprint, jsonify, session
from src.models.usuario import Usuario
from src.models.avaliacao import Avaliacao, db

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

def admin_required(func):
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Não autenticado"}, 401
        usuario = Usuario.query.get(user_id)
        if not usuario or usuario.tipo != 'admin' or not usuario.ativo:
            return {"error": "Acesso negado"}, 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/ranking_geral')
@admin_required
def ranking_geral():
    usuarios = Usuario.query.filter_by(ativo=True).all()
    resultado = []

    for u in usuarios:
        avaliacoes = Avaliacao.query.filter_by(avaliado_id=u.id).all()
        media_geral = round(sum(a.media_geral for a in avaliacoes) / len(avaliacoes), 2) if avaliacoes else None

        autoavaliacao = Avaliacao.query.filter_by(
            avaliador_id=u.id, avaliado_id=u.id, tipo_avaliacao='autoavaliacao'
        ).first()
        auto_media = autoavaliacao.media_geral if autoavaliacao else None

        resultado.append({
            "id": u.id,
            "nome": u.nome,
            "cargo": u.cargo,
            "media_geral": media_geral,
            "autoavaliacao": auto_media
        })

    # Ordenar por média geral
    resultado = sorted(resultado, key=lambda x: x['media_geral'] or 0, reverse=True)
    return jsonify(resultado)
