from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    contas = db.relationship('Conta', backref='usuario', lazy=True, cascade='all, delete-orphan')
    lancamentos = db.relationship('Lancamento', backref='usuario', lazy=True, cascade='all, delete-orphan')
    cofres = db.relationship('Cofre', backref='usuario', lazy=True, cascade='all, delete-orphan')
    cartoes = db.relationship('CartaoCredito', backref='usuario', lazy=True, cascade='all, delete-orphan')
    gastos_fixos = db.relationship('GastoFixo', backref='usuario', lazy=True, cascade='all, delete-orphan')
    transferencias = db.relationship('Transferencia', backref='usuario', lazy=True, cascade='all, delete-orphan')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Conta(db.Model):
    __tablename__ = 'contas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    saldo_inicial = db.Column(db.Float, default=0.0)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    lancamentos = db.relationship('Lancamento', backref='conta', lazy=True)

    @property
    def saldo_atual(self):
        entradas = sum(l.valor for l in self.lancamentos if l.tipo == 'entrada')
        saidas = sum(l.valor for l in self.lancamentos if l.tipo == 'saida')
        return self.saldo_inicial + entradas - saidas


class Lancamento(db.Model):
    __tablename__ = 'lancamentos'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    CATEGORIAS_ENTRADA = ['Salário', 'Freela', 'Vendas', 'Presente', 'Outros']
    CATEGORIAS_SAIDA = ['Alimentação', 'Transporte', 'Moradia', 'Saúde', 'Lazer', 'Roupas', 'Educação', 'Outros']


class Cofre(db.Model):
    __tablename__ = 'cofres'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    meta = db.Column(db.Float, nullable=False)
    valor_atual = db.Column(db.Float, default=0.0)
    emoji = db.Column(db.String(10), default='🏦')
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Transferencia(db.Model):
    __tablename__ = 'transferencias'
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(200))
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    tipo = db.Column(db.String(30), nullable=False)
    # conta origem e destino (opcionais dependendo do tipo)
    conta_origem_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=True)
    conta_destino_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=True)
    cofre_id = db.Column(db.Integer, db.ForeignKey('cofres.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    conta_origem = db.relationship('Conta', foreign_keys=[conta_origem_id])
    conta_destino = db.relationship('Conta', foreign_keys=[conta_destino_id])
    cofre = db.relationship('Cofre', foreign_keys=[cofre_id])


class CartaoCredito(db.Model):
    __tablename__ = 'cartoes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    limite = db.Column(db.Float, default=0.0)
    dia_vencimento = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    compras = db.relationship('CompraCartao', backref='cartao', lazy=True, cascade='all, delete-orphan')

    @property
    def total_fatura_atual(self):
        from datetime import date
        hoje = date.today()
        return sum(c.valor for c in self.compras
                   if c.data.month == hoje.month and c.data.year == hoje.year)


class CompraCartao(db.Model):
    __tablename__ = 'compras_cartao'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    parcelas = db.Column(db.Integer, default=1)
    cartao_id = db.Column(db.Integer, db.ForeignKey('cartoes.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


class GastoFixo(db.Model):
    __tablename__ = 'gastos_fixos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    dia_vencimento = db.Column(db.Integer, nullable=False)
    pago = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def percentual(self):
        if self.meta <= 0:
            return 0
        return min(int((self.valor_atual / self.meta) * 100), 100)