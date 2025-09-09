from src.models.avaliacao import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = 'usuario'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.Integer, unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=True)  # Opcional para primeira implementação
    cargo = db.Column(db.String(100), nullable=True)
    regiao = db.Column(db.String(50), nullable=True)
    gestor_imediato = db.Column(db.String(100), nullable=True)
    nivel_hierarquico = db.Column(db.String(50), nullable=True)
    vinculo = db.Column(db.String(50), nullable=True)
    data_admissao = db.Column(db.Date, nullable=True)
    tipo = db.Column(db.String(20), nullable=False, default='funcionario')  # 'funcionario' ou 'gestor'
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

    def set_password(self, password):
        """Define a senha do usuário"""
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha está correta"""
        if not self.senha_hash:
            return False
        return check_password_hash(self.senha_hash, password)

    def get_subordinados(self):
        """Retorna lista de subordinados diretos"""
        return Usuario.query.filter_by(gestor_imediato=self.nome, ativo=True).all()

    def pode_avaliar(self, usuario_avaliado):
        """Verifica se este usuário pode avaliar outro usuário"""
        # Sempre pode se autoavaliar
        if self.id == usuario_avaliado.id:
            return True
            
        # Se for gestor, pode avaliar subordinados diretos
        if self.tipo == 'gestor':
            # Verificar se o usuário avaliado é subordinado direto
            subordinados = self.get_subordinados()
            subordinados_ids = [sub.id for sub in subordinados]
            return usuario_avaliado.id in subordinados_ids
            
        # Funcionários só podem se autoavaliar
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'matricula': self.matricula,
            'nome': self.nome,
            'email': self.email,
            'cargo': self.cargo,
            'regiao': self.regiao,
            'gestor_imediato': self.gestor_imediato,
            'nivel_hierarquico': self.nivel_hierarquico,
            'vinculo': self.vinculo,
            'data_admissao': self.data_admissao.isoformat() if self.data_admissao else None,
            'tipo': self.tipo,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

    def to_dict_safe(self):
        """Versão segura sem informações sensíveis"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'cargo': self.cargo,
            'regiao': self.regiao,
            'tipo': self.tipo
        }

