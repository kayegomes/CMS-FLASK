from flask import Blueprint, jsonify, request, session
from src.models.usuario import Usuario, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Fazer login do usuário"""
    try:
        data = request.json
        email = data.get('email')
        senha = data.get('senha', '')  # Senha opcional por enquanto
        
        if not email:
            return jsonify({'error': 'Email é obrigatório'}), 400
        
        # Buscar usuário por email
        usuario = Usuario.query.filter_by(email=email, ativo=True).first()
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Por enquanto, aceitar qualquer senha ou sem senha
        # Em produção, verificar senha: if not usuario.check_password(senha):
        
        # Salvar na sessão
        session['user_id'] = usuario.id
        session['user_email'] = usuario.email
        session['user_tipo'] = usuario.tipo
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'usuario': usuario.to_dict_safe()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Fazer logout do usuário"""
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'})

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Obter dados do usuário logado"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    usuario = Usuario.query.get(user_id)
    if not usuario or not usuario.ativo:
        session.clear()
        return jsonify({'error': 'Usuário inválido'}), 401
    
    return jsonify(usuario.to_dict_safe())

@auth_bp.route('/subordinados', methods=['GET'])
def get_subordinados():
    """Obter lista de subordinados do usuário logado"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    usuario = Usuario.query.get(user_id)
    if not usuario or not usuario.ativo:
        return jsonify({'error': 'Usuário inválido'}), 401
    
    subordinados = []
    
    if usuario.tipo == 'gestor':
        # Gestores podem avaliar subordinados
        subordinados_query = Usuario.query.filter_by(
            gestor_imediato=usuario.nome, 
            ativo=True
        ).order_by(Usuario.nome).all()
        subordinados = [sub.to_dict_safe() for sub in subordinados_query]
    
    # Todos podem se autoavaliar
    subordinados.append(usuario.to_dict_safe())
    
    return jsonify(subordinados)

@auth_bp.route('/usuarios', methods=['GET'])
def get_usuarios():
    """Listar todos os usuários (apenas para administração)"""
    usuarios = Usuario.query.filter_by(ativo=True).order_by(Usuario.nome).all()
    return jsonify([usuario.to_dict_safe() for usuario in usuarios])

@auth_bp.route('/populate_users', methods=['POST'])
def populate_users():
    """Popular banco com usuários da planilha (apenas para setup inicial)"""
    try:
        import json
        
        # Ler dados processados
        with open('/home/ubuntu/usuarios_sistema.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        usuarios_criados = 0
        
        for user_data in dados['usuarios']:
            # Verificar se usuário já existe
            usuario_existente = Usuario.query.filter_by(email=user_data['email']).first()
            
            if not usuario_existente:
                from datetime import datetime
                
                usuario = Usuario(
                    matricula=user_data['matricula'],
                    nome=user_data['nome'],
                    email=user_data['email'],
                    cargo=user_data['cargo'],
                    regiao=user_data['regiao'],
                    gestor_imediato=user_data['gestor_imediato'],
                    nivel_hierarquico=user_data['nivel_hierarquico'],
                    vinculo=user_data['vinculo'],
                    data_admissao=datetime.strptime(user_data['data_admissao'], '%Y-%m-%d').date(),
                    tipo=user_data['tipo']
                )
                
                db.session.add(usuario)
                usuarios_criados += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'{usuarios_criados} usuários criados com sucesso',
            'total_usuarios': Usuario.query.count()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

