from flask import Flask, render_template, url_for, redirect, session
import sqlite3
from forms.personal import PersonalForm
from forms.login import LoginForm
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.register import RegisterForm
from data.users import User, set_password, check_password
from data import db_session


def write_to_file(data, name):
    photo_path = os.path.join("static/icons", name + "_icon.png")
    with open(photo_path, 'wb') as file:
        file.write(data)
    icon = url_for('static', filename=f'icons/{name}_icon.png')
    path = os.getcwd().replace('\\', '/')
    os.chdir(path+'/static/icons')
    os.remove(f'{name}_icon.png')
    os.chdir(path)
    return icon


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/settings.db")
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def main():
    return render_template('main.html', title='Personal Link')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            nickname=form.name.data,
            email=form.email.data,
            password=set_password(form.password.data)
        )
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == form.username.data).first()
        if user:
            db_id, nickname, email, icon, body, password = user.id, user.nickname, user.email,\
                                                           user.icon, user.body, user.password
            body = [x.split('   ') for x in body.split('      ')] if body else []
            if check_password(password=password):
                login_user(user, remember=form.remember_me.data)
                return redirect(f'/c/{nickname}')
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/c/<page_id>', methods=['GET', 'POST'])
@login_required
def cabinet(page_id):
    if current_user.nickname == page_id:
        form = PersonalForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.nickname == current_user.nickname).first()
            user.body = form.body.data
            user.icon = form.icon.data
            db_sess.commit()
        return render_template('cabinet.html', title='Ваш кабинет', form=form)
    return render_template('error.html', msg='У вас нет доступа к этому кабинету',  title='Ошибка')


@app.route('/v/<page_id>')
def view(page_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == page_id).first()
    if user:
        db_id, nickname, email, icon, body, password = user.id, user.nickname, user.email, \
                                                       user.icon, user.body, user.password
        return render_template('view.html', title=nickname,
                               icon=write_to_file(icon, nickname) if icon else None)
    return render_template('error.html', title='Ошибка', msg='Страница не найдена')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
