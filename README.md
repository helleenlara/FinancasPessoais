# 💰 MinhasFinanças

App web de finanças pessoais desenvolvido com Python/Flask para a disciplina **Python RAD — UniRuy/Wyden**.

## 🌐 Acesse o app
👉 https://financaspessoais-mt7o.onrender.com

## 📋 Sobre o projeto

App criado para resolver um problema real do dia a dia: controlar múltiplas contas bancárias, registrar entradas e saídas de diferentes fontes e guardar dinheiro por objetivos (cofres).

## ✅ Funcionalidades

- 🔐 Login e cadastro de usuário
- 🏦 Gerenciamento de contas bancárias (CRUD)
- 💸 Registro de lançamentos por categoria (CRUD)
- 🐷 Cofres com metas e barra de progresso
- 📊 Relatório mensal por categoria
- 📱 Interface responsiva — funciona no celular

## 🛠️ Tecnologias utilizadas

- **Backend:** Python 3.11 + Flask + SQLAlchemy + Flask-Login
- **Banco de dados:** PostgreSQL (produção) / SQLite (desenvolvimento)
- **Frontend:** Bootstrap 5 + Bootstrap Icons
- **Deploy:** Render (cloud gratuito)
- **Versionamento:** GitHub

## 🚀 Como rodar localmente

```bash
# 1. Clone o repositório
git clone https://github.com/helleenlara/FinancasPessoais.git
cd FinancasPessoais

# 2. Crie o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode o app
python run.py
```

Acesse: http://localhost:5000

## 📁 Estrutura do projeto

```text
FinancasPessoais/
│
├── app/
│   ├── templates/      ← páginas HTML
│   ├── static/         ← CSS próprio
│   ├── __init__.py     ← inicializa o app
│   ├── models.py       ← tabelas do banco
│   ├── routes.py       ← rotas principais
│   └── auth.py         ← login e registro
│
├── run.py              ← inicia o servidor
├── config.py           ← configurações
├── requirements.txt    ← dependências
├── Procfile            ← configuração do deploy
└── runtime.txt         ← versão do Python
```

## 👩‍💻 Autora

**Lara Hellen** — UniRuy/Wyden 2026.1