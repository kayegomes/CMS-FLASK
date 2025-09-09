from flask import Blueprint, jsonify, request, session
from src.models.avaliacao import Avaliacao, db
from src.models.usuario import Usuario

avaliacao_bp = Blueprint('avaliacao', __name__)

def require_auth():
    """Verificar se usuário está autenticado"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    usuario = Usuario.query.get(user_id)
    if not usuario or not usuario.ativo:
        session.clear()
        return None
    
    return usuario

@avaliacao_bp.route('/avaliacoes', methods=['GET'])
def get_avaliacoes():
    """Listar avaliações do usuário logado"""
    usuario = require_auth()
    if not usuario:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Buscar apenas avaliações feitas pelo usuário logado
    avaliacoes = Avaliacao.query.filter_by(avaliador_id=usuario.id).order_by(Avaliacao.data_avaliacao.desc()).all()
    
    return jsonify([avaliacao.to_dict() for avaliacao in avaliacoes])

@avaliacao_bp.route('/avaliacoes', methods=['POST'])
def create_avaliacao():
    """Criar nova avaliação"""
    usuario = require_auth()
    if not usuario:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.json
        
        # Validar campos obrigatórios
        required_fields = [
            'avaliado_id', 'tipo_avaliacao', 'producao', 'edicao', 'coordenacao', 'co_coordenacao',
            'pro_atividade', 'criatividade', 'resolucao_problemas',
            'flexibilidade_adaptabilidade', 'relacionamento_equipe',
            'relacionamento_outras_areas', 'inteligencia_emocional', 'lideranca', 'visao_institucional'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se o usuário avaliado existe
        avaliado = Usuario.query.get(data['avaliado_id'])
        if not avaliado or not avaliado.ativo:
            return jsonify({'error': 'Usuário avaliado não encontrado'}), 404
        
        # Verificar permissões
        if not usuario.pode_avaliar(avaliado):
            return jsonify({'error': 'Você não tem permissão para avaliar este usuário'}), 403
        
        # Verificar se já existe avaliação do mesmo tipo
        avaliacao_existente = Avaliacao.query.filter_by(
            avaliador_id=usuario.id,
            avaliado_id=data['avaliado_id'],
            tipo_avaliacao=data['tipo_avaliacao']
        ).first()
        
        if avaliacao_existente:
            return jsonify({'error': f'Já existe uma {data["tipo_avaliacao"]} para este usuário'}), 400
        
        # Criar avaliação
        avaliacao = Avaliacao(
            avaliador_id=usuario.id,
            avaliado_id=data['avaliado_id'],
            tipo_avaliacao=data['tipo_avaliacao'],
            producao=data['producao'],
            edicao=data['edicao'],
            coordenacao=data['coordenacao'],
            co_coordenacao=int(data['co_coordenacao']),
            pro_atividade=data['pro_atividade'],
            criatividade=data['criatividade'],
            resolucao_problemas=data['resolucao_problemas'],
            flexibilidade_adaptabilidade=data['flexibilidade_adaptabilidade'],
            relacionamento_equipe=data['relacionamento_equipe'],
            relacionamento_outras_areas=data['relacionamento_outras_areas'],
            inteligencia_emocional=data['inteligencia_emocional'],
            lideranca=int(data['lideranca']),
            visao_institucional=data['visao_institucional'],
            pontos_fortes=data.get('pontos_fortes'),
            pontos_desenvolver=data.get('pontos_desenvolver')
        )
        
        # Calcular média
        avaliacao.calcular_media()
        
        db.session.add(avaliacao)
        db.session.commit()
        
        return jsonify(avaliacao.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@avaliacao_bp.route('/avaliacoes/<int:avaliacao_id>', methods=['GET'])
def get_avaliacao(avaliacao_id):
    """Obter avaliação específica"""
    usuario = require_auth()
    if not usuario:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)
    
    # Verificar se o usuário pode ver esta avaliação
    if avaliacao.avaliador_id != usuario.id:
        return jsonify({'error': 'Acesso negado'}), 403
    
    return jsonify(avaliacao.to_dict())

@avaliacao_bp.route('/avaliacoes/<int:avaliacao_id>', methods=['PUT'])
def update_avaliacao(avaliacao_id):
    """Atualizar avaliação existente"""
    usuario = require_auth()
    if not usuario:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        avaliacao = Avaliacao.query.get_or_404(avaliacao_id)
        
        # Verificar permissões
        if avaliacao.avaliador_id != usuario.id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.json
        
        # Atualizar campos numéricos
        numeric_fields = [
            'producao', 'edicao', 'coordenacao','co_coordenacao', 'pro_atividade', 'criatividade',
            'resolucao_problemas', 'flexibilidade_adaptabilidade', 'relacionamento_equipe',
            'relacionamento_outras_areas', 'inteligencia_emocional', 'lideranca', 'visao_institucional'
        ]
        
        for field in numeric_fields:
            if field in data:
                setattr(avaliacao, field, data[field])
        
        # Atualizar campos de texto
        if 'pontos_fortes' in data:
            avaliacao.pontos_fortes = data['pontos_fortes']
        if 'pontos_desenvolver' in data:
            avaliacao.pontos_desenvolver = data['pontos_desenvolver']
        
        # Recalcular média
        avaliacao.calcular_media()
        
        db.session.commit()
        return jsonify(avaliacao.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@avaliacao_bp.route('/avaliacoes/<int:avaliacao_id>', methods=['DELETE'])
def delete_avaliacao(avaliacao_id):
    """Deletar avaliação"""
    usuario = require_auth()
    if not usuario:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)
    
    # Verificar permissões
    if avaliacao.avaliador_id != usuario.id:
        return jsonify({'error': 'Acesso negado'}), 403
    
    db.session.delete(avaliacao)
    db.session.commit()
    return '', 204

@avaliacao_bp.route('/avaliacoes/estatisticas', methods=['GET'])
def get_estatisticas():
    """Obter estatísticas das avaliações"""
    usuario = require_auth()
    if not usuario:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Estatísticas básicas das avaliações feitas pelo usuário
        avaliacoes_feitas = Avaliacao.query.filter_by(avaliador_id=usuario.id).all()
        
        if not avaliacoes_feitas:
            return jsonify({
                'total_avaliacoes': 0,
                'funcionarios_avaliados': 0,
                'media_geral': 0,
                'comparativo_auto_avaliacao': [],
                'ranking_subordinados': []
            })
        
        # Calcular estatísticas básicas
        total_avaliacoes = len(avaliacoes_feitas)
        funcionarios_avaliados = len(set(av.avaliado_id for av in avaliacoes_feitas))
        media_geral = round(sum(av.media_geral for av in avaliacoes_feitas if av.media_geral) / total_avaliacoes, 1)
        
        # Comparativo entre avaliação e autoavaliação
        comparativo = []
        ranking = []
        
        if usuario.tipo == 'gestor':
            # Para gestores, mostrar comparativo dos subordinados com notas detalhadas
            subordinados = usuario.get_subordinados()
            subordinados_com_avaliacao = []
            
            for subordinado in subordinados:
                # Buscar avaliação feita pelo gestor para este subordinado
                avaliacao_gestor = Avaliacao.query.filter_by(
                    avaliador_id=usuario.id,
                    avaliado_id=subordinado.id,
                    tipo_avaliacao='subordinado'
                ).first()
                
                # Buscar autoavaliação do subordinado
                autoavaliacao = Avaliacao.query.filter_by(
                    avaliador_id=subordinado.id,
                    avaliado_id=subordinado.id,
                    tipo_avaliacao='autoavaliacao'
                ).first()
                
                # Incluir no comparativo se houver pelo menos uma das avaliações
                if avaliacao_gestor or autoavaliacao:
                    avaliacao_media = avaliacao_gestor.media_geral if avaliacao_gestor else None
                    auto_media = autoavaliacao.media_geral if autoavaliacao else None
                    
                    diferenca = None
                    if avaliacao_media is not None and auto_media is not None:
                        diferenca = round(avaliacao_media - auto_media, 1)
                    
                    # Notas detalhadas por critério (apenas para gestores)
                    notas_detalhadas_gestor = None
                    notas_detalhadas_auto = None
                    
                    if avaliacao_gestor:
                        notas_detalhadas_gestor = {
                            'producao': avaliacao_gestor.producao,
                            'edicao': avaliacao_gestor.edicao,
                            'coordenacao': avaliacao_gestor.coordenacao,
                            'co_coordenacao': avaliacao_gestor.co_coordenacao,
                            'pro_atividade': avaliacao_gestor.pro_atividade,
                            'criatividade': avaliacao_gestor.criatividade,
                            'resolucao_problemas': avaliacao_gestor.resolucao_problemas,
                            'flexibilidade_adaptabilidade': avaliacao_gestor.flexibilidade_adaptabilidade,
                            'relacionamento_equipe': avaliacao_gestor.relacionamento_equipe,
                            'relacionamento_outras_areas': avaliacao_gestor.relacionamento_outras_areas,
                            'inteligencia_emocional': avaliacao_gestor.inteligencia_emocional,
                            'lideranca': avaliacao_gestor.lideranca,
                            'visao_institucional': avaliacao_gestor.visao_institucional,
                            'pontos_fortes': avaliacao_gestor.pontos_fortes,
                            'pontos_desenvolver': avaliacao_gestor.pontos_desenvolver
                        }
                    
                    if autoavaliacao:
                        notas_detalhadas_auto = {
                            'producao': autoavaliacao.producao,
                            'edicao': autoavaliacao.edicao,
                            'coordenacao': autoavaliacao.coordenacao,
                            'co_coordenacao': autoavaliacao.co_coordenacao,
                            'pro_atividade': autoavaliacao.pro_atividade,
                            'criatividade': autoavaliacao.criatividade,
                            'resolucao_problemas': autoavaliacao.resolucao_problemas,
                            'flexibilidade_adaptabilidade': autoavaliacao.flexibilidade_adaptabilidade,
                            'relacionamento_equipe': autoavaliacao.relacionamento_equipe,
                            'relacionamento_outras_areas': autoavaliacao.relacionamento_outras_areas,
                            'inteligencia_emocional': autoavaliacao.inteligencia_emocional,
                            'lideranca': autoavaliacao.lideranca,
                            'visao_institucional': autoavaliacao.visao_institucional,
                            'pontos_fortes': autoavaliacao.pontos_fortes,
                            'pontos_desenvolver': autoavaliacao.pontos_desenvolver
                        }
                    
                    comparativo.append({
                        'funcionario': subordinado.nome,
                        'cargo': subordinado.cargo,
                        'avaliacao_gestor': avaliacao_media,
                        'autoavaliacao': auto_media,
                        'diferenca': diferenca,
                        'notas_detalhadas_gestor': notas_detalhadas_gestor,
                        'notas_detalhadas_auto': notas_detalhadas_auto
                    })
                    
                    # Para ranking, incluir apenas subordinados com avaliação do gestor
                    if avaliacao_gestor:
                        subordinados_com_avaliacao.append({
                            'funcionario': subordinado.nome,
                            'cargo': subordinado.cargo,
                            'media_geral': avaliacao_gestor.media_geral,
                            'avaliacao_id': avaliacao_gestor.id,
                            'autoavaliacao': auto_media
                        })
            
            # Criar ranking ordenado por média geral (maior para menor)
            ranking = sorted(subordinados_com_avaliacao, key=lambda x: x['media_geral'], reverse=True)
            
        else:
            # Para funcionários, mostrar apenas autoavaliação (SEM avaliação do gestor)
            # Buscar autoavaliação do funcionário
            autoavaliacao = Avaliacao.query.filter_by(
                avaliador_id=usuario.id,
                avaliado_id=usuario.id,
                tipo_avaliacao='autoavaliacao'
            ).first()
            
            # Incluir apenas autoavaliação no comparativo
            if autoavaliacao:
                comparativo.append({
                    'funcionario': usuario.nome,
                    'cargo': usuario.cargo,
                    'avaliacao_gestor': None,  # Ocultar para funcionários
                    'autoavaliacao': autoavaliacao.media_geral,
                    'diferenca': None,  # Sem comparação para funcionários
                    'notas_detalhadas_gestor': None,  # Ocultar para funcionários
                    'notas_detalhadas_auto': {
                        'producao': autoavaliacao.producao,
                        'edicao': autoavaliacao.edicao,
                        'coordenacao': autoavaliacao.coordenacao,
                        'co_coordenacao': autoavaliacao.co_coordenacao,
                        'pro_atividade': autoavaliacao.pro_atividade,
                        'criatividade': autoavaliacao.criatividade,
                        'resolucao_problemas': autoavaliacao.resolucao_problemas,
                        'flexibilidade_adaptabilidade': autoavaliacao.flexibilidade_adaptabilidade,
                        'relacionamento_equipe': autoavaliacao.relacionamento_equipe,
                        'relacionamento_outras_areas': autoavaliacao.relacionamento_outras_areas,
                        'inteligencia_emocional': autoavaliacao.inteligencia_emocional,
                        'lideranca': autoavaliacao.lideranca,
                        'visao_institucional': autoavaliacao.visao_institucional,
                        'pontos_fortes': autoavaliacao.pontos_fortes,
                        'pontos_desenvolver': autoavaliacao.pontos_desenvolver
                    }
                })
        
        return jsonify({
            'total_avaliacoes': total_avaliacoes,
            'funcionarios_avaliados': funcionarios_avaliados,
            'media_geral': media_geral,
            'comparativo_auto_avaliacao': comparativo,
            'ranking_subordinados': ranking
        })
        
    except Exception as e:
        print(f"Erro nas estatísticas: {str(e)}")  # Para debug
        return jsonify({'error': str(e)}), 500

