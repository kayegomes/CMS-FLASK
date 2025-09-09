from flask import Blueprint, jsonify, request
from src.models.colaborador import Colaborador, db

colaborador_bp = Blueprint('colaborador', __name__)

@colaborador_bp.route('/colaboradores', methods=['GET'])
def get_colaboradores():
    """Listar todos os colaboradores"""
    colaboradores = Colaborador.query.order_by(Colaborador.nome_completo).all()
    return jsonify([colaborador.to_dict() for colaborador in colaboradores])

@colaborador_bp.route('/colaboradores', methods=['POST'])
def create_colaborador():
    """Criar novo colaborador"""
    try:
        data = request.json
        
        # Validar campos obrigatórios
        if not data.get('nome_completo'):
            return jsonify({'error': 'Nome completo é obrigatório'}), 400
        
        colaborador = Colaborador(
            nome_completo=data['nome_completo'],
            cargo=data.get('cargo'),
            departamento=data.get('departamento')
        )
        
        db.session.add(colaborador)
        db.session.commit()
        return jsonify(colaborador.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@colaborador_bp.route('/colaboradores/<int:colaborador_id>', methods=['GET'])
def get_colaborador(colaborador_id):
    """Obter colaborador específico"""
    colaborador = Colaborador.query.get_or_404(colaborador_id)
    return jsonify(colaborador.to_dict())

@colaborador_bp.route('/colaboradores/<int:colaborador_id>', methods=['PUT'])
def update_colaborador(colaborador_id):
    """Atualizar colaborador existente"""
    try:
        colaborador = Colaborador.query.get_or_404(colaborador_id)
        data = request.json
        
        # Validar nome completo se fornecido
        if 'nome_completo' in data and not data['nome_completo']:
            return jsonify({'error': 'Nome completo não pode estar vazio'}), 400
        
        # Atualizar campos
        colaborador.nome_completo = data.get('nome_completo', colaborador.nome_completo)
        colaborador.cargo = data.get('cargo', colaborador.cargo)
        colaborador.departamento = data.get('departamento', colaborador.departamento)
        
        db.session.commit()
        return jsonify(colaborador.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@colaborador_bp.route('/colaboradores/<int:colaborador_id>', methods=['DELETE'])
def delete_colaborador(colaborador_id):
    """Deletar colaborador"""
    colaborador = Colaborador.query.get_or_404(colaborador_id)
    db.session.delete(colaborador)
    db.session.commit()
    return '', 204

@colaborador_bp.route('/colaboradores/search', methods=['GET'])
def search_colaboradores():
    """Buscar colaboradores por nome"""
    nome = request.args.get('nome', '')
    if nome:
        colaboradores = Colaborador.query.filter(
            Colaborador.nome_completo.ilike(f'%{nome}%')
        ).order_by(Colaborador.nome_completo).all()
    else:
        colaboradores = Colaborador.query.order_by(Colaborador.nome_completo).all()
    
    return jsonify([colaborador.to_dict() for colaborador in colaboradores])

@colaborador_bp.route('/colaboradores/departamento/<departamento>', methods=['GET'])
def get_colaboradores_departamento(departamento):
    """Obter colaboradores de um departamento específico"""
    colaboradores = Colaborador.query.filter_by(departamento=departamento).order_by(Colaborador.nome_completo).all()
    return jsonify([colaborador.to_dict() for colaborador in colaboradores])

