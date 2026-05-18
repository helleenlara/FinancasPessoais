from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Conta, Lancamento, Cofre
from datetime import datetime, date

main = Blueprint('main', __name__)

# ─── DASHBOARD ───────────────────────────────────────────────
@main.route('/dashboard')
@login_required
def dashboard():
    contas = Conta.query.filter_by(usuario_id=current_user.id).all()
    cofres = Cofre.query.filter_by(usuario_id=current_user.id).all()

    hoje = date.today()
    lancamentos_mes = Lancamento.query.filter_by(usuario_id=current_user.id).filter(
        db.extract('month', Lancamento.data) == hoje.month,
        db.extract('year', Lancamento.data) == hoje.year
    ).order_by(Lancamento.data.desc()).all()

    total_entradas = sum(l.valor for l in lancamentos_mes if l.tipo == 'entrada')
    total_saidas = sum(l.valor for l in lancamentos_mes if l.tipo == 'saida')
    saldo_total = sum(c.saldo_atual for c in contas)
    ultimos = lancamentos_mes[:5]

    return render_template('dashboard.html',
        contas=contas, cofres=cofres,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        saldo_total=saldo_total,
        ultimos=ultimos
    )

# ─── CONTAS ──────────────────────────────────────────────────
@main.route('/contas')
@login_required
def contas():
    contas = Conta.query.filter_by(usuario_id=current_user.id).all()
    return render_template('contas.html', contas=contas)

@main.route('/contas/nova', methods=['GET', 'POST'])
@login_required
def nova_conta():
    if request.method == 'POST':
        conta = Conta(
            nome=request.form['nome'],
            tipo=request.form['tipo'],
            saldo_inicial=float(request.form.get('saldo_inicial', 0)),
            usuario_id=current_user.id
        )
        db.session.add(conta)
        db.session.commit()
        flash('Conta criada!', 'success')
        return redirect(url_for('main.contas'))
    return render_template('contas.html', modo='nova',
                           contas=Conta.query.filter_by(usuario_id=current_user.id).all())

@main.route('/contas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_conta(id):
    conta = Conta.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
    if request.method == 'POST':
        conta.nome = request.form['nome']
        conta.tipo = request.form['tipo']
        conta.saldo_inicial = float(request.form.get('saldo_inicial', 0))
        db.session.commit()
        flash('Conta atualizada!', 'success')
        return redirect(url_for('main.contas'))
    return render_template('contas.html', modo='editar', conta_editar=conta,
                           contas=Conta.query.filter_by(usuario_id=current_user.id).all())

@main.route('/contas/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_conta(id):
    conta = Conta.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
    db.session.delete(conta)
    db.session.commit()
    flash('Conta excluída.', 'info')
    return redirect(url_for('main.contas'))

# ─── LANÇAMENTOS ─────────────────────────────────────────────
@main.route('/lancamentos')
@login_required
def lancamentos():
    contas = Conta.query.filter_by(usuario_id=current_user.id).all()
    todos = Lancamento.query.filter_by(usuario_id=current_user.id).order_by(Lancamento.data.desc()).all()
    return render_template('lancamentos.html', lancamentos=todos, contas=contas,
                           categorias_entrada=Lancamento.CATEGORIAS_ENTRADA,
                           categorias_saida=Lancamento.CATEGORIAS_SAIDA)

@main.route('/lancamentos/novo', methods=['POST'])
@login_required
def novo_lancamento():
    conta_id = int(request.form['conta_id'])
    Conta.query.filter_by(id=conta_id, usuario_id=current_user.id).first_or_404()
    lancamento = Lancamento(
        descricao=request.form['descricao'],
        valor=float(request.form['valor']),
        tipo=request.form['tipo'],
        categoria=request.form['categoria'],
        data=datetime.strptime(request.form['data'], '%Y-%m-%d').date(),
        conta_id=conta_id,
        usuario_id=current_user.id
    )
    db.session.add(lancamento)
    db.session.commit()
    flash('Lançamento registrado!', 'success')
    return redirect(url_for('main.lancamentos'))

@main.route('/lancamentos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_lancamento(id):
    lancamento = Lancamento.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
    db.session.delete(lancamento)
    db.session.commit()
    flash('Lançamento excluído.', 'info')
    return redirect(url_for('main.lancamentos'))

# ─── COFRES ──────────────────────────────────────────────────
@main.route('/cofres')
@login_required
def cofres():
    cofres = Cofre.query.filter_by(usuario_id=current_user.id).all()
    return render_template('cofres.html', cofres=cofres)

@main.route('/cofres/novo', methods=['POST'])
@login_required
def novo_cofre():
    cofre = Cofre(
        nome=request.form['nome'],
        meta=float(request.form['meta']),
        valor_atual=float(request.form.get('valor_atual', 0)),
        emoji=request.form.get('emoji', '🏦'),
        usuario_id=current_user.id
    )
    db.session.add(cofre)
    db.session.commit()
    flash('Cofre criado!', 'success')
    return redirect(url_for('main.cofres'))

@main.route('/cofres/depositar/<int:id>', methods=['POST'])
@login_required
def depositar_cofre(id):
    cofre = Cofre.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
    valor = float(request.form['valor'])
    acao = request.form.get('acao', 'depositar')
    if acao == 'retirar':
        cofre.valor_atual = max(0, cofre.valor_atual - valor)
        flash('Valor retirado do cofre.', 'info')
    else:
        cofre.valor_atual += valor
        flash('Valor depositado no cofre!', 'success')
    db.session.commit()
    return redirect(url_for('main.cofres'))

@main.route('/cofres/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_cofre(id):
    cofre = Cofre.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
    db.session.delete(cofre)
    db.session.commit()
    flash('Cofre excluído.', 'info')
    return redirect(url_for('main.cofres'))

# ─── RELATÓRIO ───────────────────────────────────────────────
@main.route('/relatorio')
@login_required
def relatorio():
    mes = request.args.get('mes', date.today().month, type=int)
    ano = request.args.get('ano', date.today().year, type=int)

    lancamentos = Lancamento.query.filter_by(usuario_id=current_user.id).filter(
        db.extract('month', Lancamento.data) == mes,
        db.extract('year', Lancamento.data) == ano
    ).all()

    entradas = [l for l in lancamentos if l.tipo == 'entrada']
    saidas = [l for l in lancamentos if l.tipo == 'saida']

    por_categoria = {}
    for l in saidas:
        por_categoria[l.categoria] = por_categoria.get(l.categoria, 0) + l.valor

    total_entradas = sum(l.valor for l in entradas)
    total_saidas = sum(l.valor for l in saidas)

    return render_template('relatorio.html',
        mes=mes, ano=ano,
        entradas=entradas, saidas=saidas,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        por_categoria=por_categoria
    )