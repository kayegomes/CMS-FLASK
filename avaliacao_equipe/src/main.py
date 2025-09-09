import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session
from src.models.avaliacao import db
from src.models.usuario import Usuario
from src.routes.avaliacao import avaliacao_bp
from src.routes.colaborador import colaborador_bp
from src.routes.auth import auth_bp
from src.models.avaliacao import Avaliacao, db
from flask import jsonify, redirect, url_for, Blueprint
from sqlalchemy import func
from src.routes.admin import admin_bp



app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
app.register_blueprint(admin_bp)
app.register_blueprint(avaliacao_bp, url_prefix='/api')
app.register_blueprint(colaborador_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')

# Configurar banco de dados
database_dir = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(database_dir, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(database_dir, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Importar todos os modelos para garantir que as tabelas sejam criadas
    from src.models.usuario import Usuario
    from src.models.avaliacao import Avaliacao
    from src.models.colaborador import Colaborador
    
    db.create_all()
    print("Tabelas criadas com sucesso!")

@app.route('/api/current_user')
def current_user():
    # Verificar se usuário está logado
    user_id = session.get('user_id')
    
    if not user_id:
        return {'error': 'Usuário não autenticado'}, 401
    
    usuario = Usuario.query.get(user_id)
    if not usuario or not usuario.ativo:
        session.clear()
        return {'error': 'Usuário inválido'}, 401
    
    return usuario.to_dict_safe()

@app.route('/api/subordinados')
def subordinados():
    # Verificar se usuário está logado
    user_id = session.get('user_id')
    
    if not user_id:
        return {'error': 'Usuário não autenticado'}, 401
    
    usuario = Usuario.query.get(user_id)
    if not usuario or not usuario.ativo:
        return {'error': 'Usuário inválido'}, 401
    
    subordinados = []
    
    if usuario.tipo == 'gestor':
        # Gestores podem avaliar subordinados
        subordinados_query = Usuario.query.filter_by(
            gestor_imediato=usuario.nome, 
            ativo=True
        ).order_by(Usuario.nome).all()
        subordinados = [sub.to_dict_safe() for sub in subordinados_query]
    
    return subordinados

@app.route('/')
def index():
    # Verificar se usuário está logado
    if 'user_id' not in session:
        return send_from_directory(app.static_folder, 'login.html')
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/login')
def login_page():
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/api/ranking-geral')
def ranking_geral():
    user_id = session.get('user_id')
    if not user_id:
        return {'error': 'Usuário não autenticado'}, 401
    
    usuario = Usuario.query.get(user_id)
    if not usuario or usuario.tipo != 'admin':
        return {'error': 'Acesso negado'}, 403

    # Query que retorna todas avaliações com média e avaliador
    ranking = (
        db.session.query(
            Usuario.id.label("avaliado_id"),
            Usuario.nome.label("funcionario"),
            Usuario.cargo,
            Avaliacao.avaliador_id,
            db.func.avg(Avaliacao.media_geral).label("media_geral"),
            db.func.avg(Avaliacao.autoavaliacao).label("autoavaliacao")
        )
        .join(Avaliacao, Avaliacao.avaliado_id == Usuario.id)
        .filter(Usuario.ativo == True)
        .group_by(Usuario.id, Usuario.nome, Usuario.cargo, Avaliacao.avaliador_id)
        .order_by(db.desc("media_geral"))
        .all()
    )

    resultado = []
    for r in ranking:
        avaliador = Usuario.query.get(r.avaliador_id)
        resultado.append({
            "avaliado_id": r.avaliado_id,
            "funcionario": r.funcionario,
            "cargo": r.cargo,
            "avaliador": avaliador.nome if avaliador else "-",
            "media_geral": round(r.media_geral, 2) if r.media_geral else None,
            "autoavaliacao": round(r.autoavaliacao, 2) if r.autoavaliacao else None
        })

    return jsonify(resultado)
@app.route('/admin/ranking')
def ranking_geral_html():
    user_id = session.get('user_id')
    usuario = Usuario.query.get(user_id) if user_id else None

    if not usuario or usuario.tipo != 'admin':
        return "Acesso negado", 403

    return send_from_directory(app.static_folder, 'ranking_geral.html')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        # Se não encontrar o arquivo, verificar autenticação
        if 'user_id' not in session:
            return send_from_directory(app.static_folder, 'login.html')
        
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

