from src.models.avaliacao import db
from datetime import datetime

class Colaborador(db.Model):
    __tablename__ = 'colaborador'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=True)
    departamento = db.Column(db.String(100), nullable=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Colaborador {self.nome_completo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'cargo': self.cargo,
            'departamento': self.departamento,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

