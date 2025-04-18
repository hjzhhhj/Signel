from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from extensions import db, login_manager  
from models import User
from forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

# 유저 로딩 함수
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 로그인
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))  # 이미 로그인 상태면 홈으로

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('로그인 성공!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('이메일 또는 비밀번호가 틀렸습니다.', 'danger')

    return render_template('login.html', form=form)

# 회원가입
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('이미 존재하는 이메일입니다.', 'danger')
        else:
            hashed_pw = generate_password_hash(form.password.data)
            new_user = User(email=form.email.data, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            flash('회원가입 성공! 로그인 해주세요.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

# 로그아웃
@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('로그아웃 되었습니다.', 'info')
    return redirect(url_for('auth.login'))
