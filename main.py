import os

from flask import Flask, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, Label
from wtforms.validators import DataRequired, Email, Length, EqualTo, AnyOf, NoneOf, ValidationError
import email_validator
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
import sqlite3

SqlAlchemyBase = dec.declarative_base()

__factory = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MSilko&MMal'

con = sqlite3.connect('data/FlaskProject.db', check_same_thread=False)
cur = con.cursor()

memory = False


class Registraiton(FlaskForm):
    username = StringField('Логин', validators=[DataRequired("Это поле обязательно!")])
    email = EmailField('Электронная почта', validators=[DataRequired("Это поле обязательно!"),
                                                        Email("Некорректный email")])
    password = PasswordField('Пароль', validators=[DataRequired("Это поле обязательно!"),
                             Length(min=4, max=16, message="Пароль должен быть от 4 до 16 символов")])
    again_password = PasswordField('Повторите пароль еще раз', validators=[DataRequired("Это поле обязательно!"),
                                   EqualTo('password', "Пароли должны совпадать")])
    submit = SubmitField('Создать аккаунт')


class Authorization(FlaskForm):
    username = StringField('Логин', validators=[DataRequired("Это поле обязательно!")])
    password = PasswordField('Пароль', validators=[DataRequired("Это поле обязательно!"),
            Length(min=4, max=16, message="Неверный пароль")])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    reg = SubmitField('Зарегестрироватся')


class Lessons(FlaskForm):
    lesson1 = SubmitField('Урок - 1: тема')
    lesson2 = SubmitField('Урок - 2: тема')
    lesson3 = SubmitField('Урок - 3: тема')
    lesson4 = SubmitField('Урок - 4: тема')
    lesson5 = SubmitField('Урок - 5: тема')


def registration1(login, password, email):
    input = [(login, email, password)]
    cur.executemany('INSERT INTO Users(login, email, password) VALUES(?,?,?)', input)
    con.commit()


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = Registraiton()
    if request.method == 'POST' and form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        email = str(request.form.get('email'))
        print(username, email, password)
        registration1(username, password, email)
        return redirect("/authorization")
    return render_template('login.html', title='Регистрация', form=form, )


@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    form = Authorization()
    if form.validate_on_submit():
        if form.submit.data:
            username = request.form.get('username')
            password = request.form.get('password')
            remember_me = request.form.get('remember_me')
            if remember_me:
                global memory
                memory = True
            try:
                pas = cur.execute(f'''SELECT password FROM Users WHERE login="{username}"''')
                if pas != password:
                    form = Authorization(pas=False)
            except sqlite3.Error:
                form = Authorization(log=False)
            return redirect("/lessons")
        if form.reg.data:
            return redirect("/registration")
    return render_template('authorization.html', title='Авторизация', form=form)


@app.route('/lessons', methods=['GET'])
def main_window():
    form = Lessons()
    return render_template('lessons.html', title='Уроки', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')

con.close()