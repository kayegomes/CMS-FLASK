from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Avaliacao(db.Model):
    __tablename__ = 'avaliacao'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relacionamentos com usuários
    avaliador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    avaliado_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Tipo de avaliação
    tipo_avaliacao = db.Column(db.String(20), nullable=False)  # 'avaliacao' ou 'autoavaliacao'
    
    # Data da avaliação
    data_avaliacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Critérios de avaliação (0-10)
    producao = db.Column(db.Integer, nullable=False)
    edicao = db.Column(db.Integer, nullable=False)
    coordenacao = db.Column(db.Integer, nullable=False)
    co_coordenacao = db.Column(db.Integer, nullable=False)
    pro_atividade = db.Column(db.Integer, nullable=False)
    criatividade = db.Column(db.Integer, nullable=False)
    resolucao_problemas = db.Column(db.Integer, nullable=False)
    flexibilidade_adaptabilidade = db.Column(db.Integer, nullable=False)
    relacionamento_equipe = db.Column(db.Integer, nullable=False)
    relacionamento_outras_areas = db.Column(db.Integer, nullable=False)
    inteligencia_emocional = db.Column(db.Integer, nullable=False)
    lideranca = db.Column(db.Integer, nullable=False)
    visao_institucional = db.Column(db.Integer, nullable=False)
    
    # Campos de texto
    pontos_fortes = db.Column(db.Text, nullable=True)
    pontos_desenvolver = db.Column(db.Text, nullable=True)
    
    # Média calculada automaticamente
    media_geral = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Avaliacao {self.id}>'

    def calcular_media(self):
        """Calcula a média geral dos critérios"""
        criterios = [
            self.producao, self.edicao, self.coordenacao, self.co_coordenacao, self.pro_atividade,
            self.criatividade, self.resolucao_problemas, self.flexibilidade_adaptabilidade,
            self.relacionamento_equipe, self.relacionamento_outras_areas,
            self.inteligencia_emocional, self.lideranca, self.visao_institucional
        ]
        self.media_geral = round(sum(criterios) / len(criterios), 1)
        return self.media_geral

    def to_dict(self):
        try:
            # Importar aqui para evitar importação circular
            from src.models.usuario import Usuario
            
            avaliador = Usuario.query.get(self.avaliador_id)
            avaliado = Usuario.query.get(self.avaliado_id)
            
            return {
                'id': self.id,
                'avaliador_id': self.avaliador_id,
                'avaliado_id': self.avaliado_id,
                'avaliador_nome': avaliador.nome if avaliador else 'Usuário não encontrado',
                'avaliado_nome': avaliado.nome if avaliado else 'Usuário não encontrado',
                'avaliado_cargo': avaliado.cargo if avaliado else None,
                'avaliado_departamento': avaliado.regiao if avaliado else None,
                'tipo_avaliacao': self.tipo_avaliacao,
                'data_avaliacao': self.data_avaliacao.isoformat() if self.data_avaliacao else None,
                'producao': self.producao,
                'edicao': self.edicao,
                'coordenacao': self.coordenacao,
                'co_coordenacao': self.co_coordenacao,
                'pro_atividade': self.pro_atividade,
                'criatividade': self.criatividade,
                'resolucao_problemas': self.resolucao_problemas,
                'flexibilidade_adaptabilidade': self.flexibilidade_adaptabilidade,
                'relacionamento_equipe': self.relacionamento_equipe,
                'relacionamento_outras_areas': self.relacionamento_outras_areas,
                'inteligencia_emocional': self.inteligencia_emocional,
                'lideranca': self.lideranca,
                'visao_institucional': self.visao_institucional,
                'pontos_fortes': self.pontos_fortes or '',
                'pontos_desenvolver': self.pontos_desenvolver or '',
                'media_geral': self.media_geral
            }
        except Exception as e:
            # Em caso de erro, retornar dados básicos
            return {
                'id': self.id,
                'avaliador_id': self.avaliador_id,
                'avaliado_id': self.avaliado_id,
                'avaliador_nome': 'Erro ao carregar',
                'avaliado_nome': 'Erro ao carregar',
                'avaliado_cargo': None,
                'avaliado_departamento': None,
                'tipo_avaliacao': self.tipo_avaliacao,
                'data_avaliacao': self.data_avaliacao.strftime('%d/%m/%Y') if self.data_avaliacao else None,
                'producao': self.producao,
                'edicao': self.edicao,
                'coordenacao': self.coordenacao,
                'co_coordenacao': self.co_coordenacao,
                'pro_atividade': self.pro_atividade,
                'criatividade': self.criatividade,
                'resolucao_problemas': self.resolucao_problemas,
                'flexibilidade_adaptabilidade': self.flexibilidade_adaptabilidade,
                'relacionamento_equipe': self.relacionamento_equipe,
                'relacionamento_outras_areas': self.relacionamento_outras_areas,
                'inteligencia_emocional': self.inteligencia_emocional,
                'lideranca': self.lideranca,
                'visao_institucional': self.visao_institucional,
                'pontos_fortes': self.pontos_fortes or '',
                'pontos_desenvolver': self.pontos_desenvolver or '',
                'media_geral': self.media_geral,
                'error': str(e)
            }

