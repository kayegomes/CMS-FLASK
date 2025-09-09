from datetime import datetime
from main import app, db
from src.models.usuario import Usuario

with app.app_context():
    # Verifica se já existe admin
    admin_existente = Usuario.query.filter_by(tipo="admin", ativo=True).first()
    if admin_existente:
        print("Admin já existe:", admin_existente.email)
    else:
        # Criar novo admin
        admin = Usuario(
            matricula=1,
            nome="Administrador",
            email="admin@empresa.com",
            cargo="Administrador",
            regiao="Central",
            gestor_imediato="",
            nivel_hierarquico="Admin",
            vinculo="CLT",
            tipo="admin",
            ativo=True,
            data_cadastro=datetime.utcnow()
        )

        # Define a senha
        admin.set_password("123456")  # Troque para a senha que desejar

        db.session.add(admin)
        db.session.commit()

        print("Admin criado com sucesso! Email:", admin.email)
