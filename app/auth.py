from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_senha(senha):
            login_user(usuario, remember=True)
            return redirect(url_for('main.dashboard'))
        flash('E-mail ou senha incorretos.', 'danger')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'danger')
            return render_template('register.html')
        usuario = Usuario(nome=nome, email=email)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario)
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))