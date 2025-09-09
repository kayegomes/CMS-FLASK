# Sistema de Avaliação de Equipe - Globo

Sistema web completo para avaliação de desempenho de equipes com autenticação, autoavaliação e comparativo de resultados.

## 🎯 **Funcionalidades Principais**

### **Sistema de Autenticação**
- Login via email corporativo
- Controle de acesso baseado em hierarquia (funcionário/gestor)
- Sessões persistentes e logout seguro

### **Autoavaliação para Funcionários**
- Funcionários podem fazer autoavaliação
- Interface intuitiva com sliders para critérios numéricos
- Campos de texto para pontos fortes e pontos a desenvolver

### **Avaliação de Subordinados para Gestores**
- Gestores podem avaliar seus subordinados
- Seleção automática baseada na hierarquia organizacional
- Controle de permissões por usuário

### **Critérios de Avaliação (0-10)**
- Produção
- Edição
- Coordenação
- Pró-atividade
- Criatividade
- Resolução de problemas
- Flexibilidade / adaptabilidade
- Relacionamento com equipe
- Relacionamento com outras áreas
- Inteligência emocional
- Visão institucional

### **Campos de Texto**
- Pontos Fortes
- Pontos a Desenvolver

### **Estatísticas e Relatórios**
- Comparativo entre avaliação do gestor e autoavaliação
- Médias gerais por funcionário
- Dashboard com estatísticas consolidadas
- Visualização de diferenças entre percepções

## 🎨 **Interface Moderna**

### **Design Responsivo**
- Layout adaptável para desktop e mobile
- Gradiente roxo/azul da identidade Globo
- Logo da Globo integrado ao header
- Sliders interativos com feedback visual
- Cards informativos e navegação por abas

### **Experiência do Usuário**
- Interface intuitiva e moderna
- Feedback visual em tempo real
- Animações suaves e micro-interações
- Mensagens de sucesso/erro claras

## 🔧 **Arquitetura Técnica**

### **Backend (Flask)**
- API RESTful completa
- Autenticação baseada em sessões
- Modelos relacionais com SQLAlchemy
- Controle de permissões por hierarquia
- Validação de dados e tratamento de erros

### **Frontend (HTML/CSS/JavaScript)**
- Interface responsiva sem frameworks externos
- JavaScript vanilla para interatividade
- CSS moderno com gradientes e animações
- Componentes reutilizáveis

### **Banco de Dados**
- SQLite para desenvolvimento
- Modelos: Usuario, Avaliacao, Colaborador
- Relacionamentos entre usuários e hierarquia
- Histórico completo de avaliações

## 📊 **Hierarquia Organizacional**

O sistema foi populado com 61 usuários baseados na planilha fornecida:

### **Estrutura**
- **Funcionários**: Podem fazer autoavaliação
- **Gestores**: Podem avaliar subordinados + autoavaliação
- **Hierarquia**: Baseada na relação gestor-subordinado da planilha

### **Controle de Acesso**
- Funcionários veem apenas opção de autoavaliação
- Gestores veem opções de autoavaliação e avaliação de subordinados
- Select de "Nome do Avaliado" é filtrado por permissões
- Campo "Nome do Avaliador" é automático (baseado no login)

## 🚀 **Como Usar**

### **1. Instalação**
```bash
# Extrair o arquivo ZIP
unzip sistema-avaliacao-equipe.zip
cd avaliacao-equipe

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### **2. Executar o Sistema**
```bash
# Iniciar servidor
python src/main.py

# Acessar no navegador
http://localhost:5000
```

### **3. Popular Banco de Dados**
```bash
# O banco será criado automaticamente
# Para popular com usuários da planilha, acesse:
# POST /api/populate_users (via console do navegador)
```

### **4. Login de Teste**
Use qualquer email da planilha fornecida, por exemplo:
- **Funcionário**: `amanda.farias@g.globo`
- **Gestor**: `andre.lara@g.globo`

## 📋 **Funcionalidades Testadas**

### ✅ **Autenticação**
- Login com email corporativo
- Redirecionamento automático para login
- Controle de sessão
- Logout funcional

### ✅ **Interface**
- Design responsivo e moderno
- Logo da Globo integrado
- Navegação por abas
- Sliders interativos

### ✅ **Autoavaliação**
- Funcionários podem se autoavaliar
- Formulário completo com todos os critérios
- Campos de texto funcionais
- Seleção automática do próprio nome

### ✅ **Hierarquia**
- Sistema reconhece funcionários vs gestores
- Opções de avaliação baseadas no tipo de usuário
- Controle de permissões implementado

## 🔄 **Fluxo de Uso**

### **Para Funcionários:**
1. Login com email corporativo
2. Aba "Nova Avaliação" → "Autoavaliação"
3. Preencher critérios de 0-10
4. Adicionar pontos fortes e a desenvolver
5. Salvar autoavaliação
6. Visualizar em "Minhas Avaliações"

### **Para Gestores:**
1. Login com email corporativo
2. Aba "Nova Avaliação" → Escolher tipo:
   - "Autoavaliação" (para si mesmo)
   - "Avaliar Subordinado" (para equipe)
3. Selecionar funcionário a ser avaliado
4. Preencher avaliação completa
5. Visualizar comparativos em "Estatísticas"

## 📈 **Estatísticas Disponíveis**

- **Total de avaliações realizadas**
- **Número de funcionários avaliados**
- **Média geral das avaliações**
- **Comparativo detalhado**: Avaliação do gestor vs Autoavaliação
- **Diferenças de percepção** (positivas/negativas)

## 🛠 **Tecnologias Utilizadas**

- **Backend**: Python 3.11, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript ES6
- **Banco**: SQLite
- **Design**: CSS Grid, Flexbox, Gradientes
- **Autenticação**: Sessions Flask

## 📁 **Estrutura do Projeto**

```
avaliacao-equipe/
├── src/
│   ├── main.py                 # Aplicação principal
│   ├── models/
│   │   ├── avaliacao.py       # Modelo de avaliação
│   │   ├── usuario.py         # Modelo de usuário
│   │   └── colaborador.py     # Modelo de colaborador
│   ├── routes/
│   │   ├── avaliacao.py       # Rotas de avaliação
│   │   ├── auth.py            # Rotas de autenticação
│   │   └── colaborador.py     # Rotas de colaborador
│   ├── static/
│   │   ├── index.html         # Interface principal
│   │   ├── login.html         # Tela de login
│   │   └── logo-globo.jpg     # Logo da empresa
│   └── database/
│       └── app.db             # Banco SQLite
├── venv/                      # Ambiente virtual
├── requirements.txt           # Dependências
└── README.md                  # Esta documentação
```

## 🔐 **Segurança**

- Autenticação obrigatória para todas as funcionalidades
- Controle de acesso baseado em hierarquia
- Validação de permissões no backend
- Sessões seguras com chave secreta
- Sanitização de dados de entrada

## 🎯 **Próximos Passos**

Para produção, considere:
- Migrar para PostgreSQL
- Implementar HTTPS
- Adicionar logs de auditoria
- Backup automático do banco
- Deploy em servidor dedicado
- Integração com Active Directory

## 📞 **Suporte**

Sistema desenvolvido para atender aos requisitos específicos da Globo:
- Hierarquia funcionário-gestor baseada na planilha fornecida
- Interface com identidade visual da empresa
- Funcionalidades de autoavaliação e avaliação de subordinados
- Comparativos estatísticos entre diferentes tipos de avaliação

---

**Desenvolvido com ❤️ para a equipe Globo**

