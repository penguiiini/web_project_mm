import os
import io
from flask import Flask, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, Label, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, AnyOf, NoneOf, ValidationError
import email_validator
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
import sqlite3
import sys

SqlAlchemyBase = dec.declarative_base()

__factory = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MSilko&MMal'

con = sqlite3.connect('data/FlaskProject.db', check_same_thread=False)
cur = con.cursor()

lesson = 1
num = 1
NowUser = False
User = ''


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


class Lesson1(FlaskForm):
    answer = TextAreaField('Введите решение', validators=[DataRequired("Это поле обязательно!")])
    send = SubmitField('Отправить')


def registration1(login, password, email):
    input = [(login, email, password)]
    cur.executemany('INSERT INTO Users(login, email, password) VALUES(?,?,?)', input)
    cur.execute('INSERT INTO Users(forall, complete, wrong) VALUES(0,0,0)')
    con.commit()


def test(answer):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = io.StringIO()

    out, exc = None, None

    try:

        exec(answer)

    except:

        import traceback
        exc = traceback.format_exc()

    out = redirected_output.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    return out, exc


def check(right_answer, answer):
    out, exc = test(answer)
    if len(out.strip()) == 0:
        output = exc
    else:
        output = out.strip().split('\n')
        if len(output) == 1:
            output = output[0]
    if output == right_answer:
        return True, '', output
    else:
        if exc is None:
            er = f'Fail on test number 1:\nExpected: {right_answer}\nReceived: {output}'
            er.split('/n')
        else:
            er = exc
            er.split('/n')
        return False, er, output


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
            last = cur.execute('''SELECT userlogin FROM Lastuser WHERE id = 1''').fetchall()
            if username != last[0][0]:
                cur.execute(f'''DELETE FROM Lastuser WHERE id = 1''')
                cur.execute(f'''INSERT INTO Lastuser(userlogin) VALUES("1")''')
                con.commit()
            try:
                pas = cur.execute(f'''SELECT password FROM Users WHERE login="{username}"''')
            except sqlite3.Error:
                pass
            global NowUser, User
            NowUser = True
            User = username
            if remember_me:
                cur.execute(f'''DELETE FROM Lastuser WHERE id = 1''')
                cur.execute(f'''INSERT INTO Lastuser(id, userlogin) VALUES(1, "{username}")''')
                con.commit()
            return redirect("/lessons")
        if form.reg.data:
            return redirect("/registration")
    return render_template('authorization.html', title='Авторизация', form=form)


@app.route('/lessons', methods=['GET', 'POST'])
def main_window():
    form = Lessons()
    if not NowUser:
        try:
            pas = cur.execute('''SELECT login, forall, complete, wrong FROM Users WHERE login = 
    (SELECT userlogin FROM Lastuser WHERE id = 1)''').fetchall()
            username, forall, correct, wrong = pas[0][0], pas[0][1], pas[0][2], pas[0][3]
        except:
            username = 'Гость'
            forall = '-'
            correct = '-'
            wrong = '-'
    else:
        pas = cur.execute(f'''SELECT login, forall, complete, wrong FROM Users WHERE login = "{User}"''').fetchall()
        username, forall, correct, wrong = pas[0][0], pas[0][1], pas[0][2], pas[0][3]

    if form.lesson1.data:
        return redirect('/lessons/les1')
    return render_template('lessons.html', title='Уроки', form=form, username=username, forall=forall,
                           correct=correct, wrong=wrong)


@app.route('/lessons/les1', methods=['GET', 'POST'])
def les1():
    form = Lesson1()
    if form.send.data:
        answer = request.form.get('answer')
        lesson = 1
        num = 1
        with open('test.py', 'w') as file:
            file.write(answer)
            ra = cur.execute(f"""SELECT answer FROM Exercises WHERE lesson = '{str(lesson)}' AND num = '{str(num)}'""").fetchall()
            check1 = check(ra[0][0], answer)
            check2 = check1[0]
            error = check1[1].split('\n')
            user_answer = check1[2]
            right_answer = ra[0][0]
    else:
        check2 = ''
        error = ''
        user_answer = ''
        right_answer = ''
    pas = cur.execute(f'''SELECT login, forall, complete, wrong FROM Users WHERE login = "{User}"''').fetchall()
    username, forall, correct, wrong = pas[0][0], pas[0][1], pas[0][2], pas[0][3]
    cur.execute(f'''UPDATE Users
        SET forall = {int(forall) + 1}
        WHERE login = "{User}"''')
    if check2 == True:
        cur.execute(f'''UPDATE Users
        SET complete = {int(correct) + 1}
        WHERE login = "{User}"''')
    elif check2 ==False:
        cur.execute(f'''UPDATE Users
        SET complete = {int(wrong) + 1}
        WHERE login = "{User}"''')
    return render_template('les1.html', title='Уроки', form=form, check=check2, error=error, answer=user_answer,
    exanswer=right_answer,
    task=['Условие задачи "Привет, world!":', ' ', 'Напишите программу, которая выводит "Hello, world!"'])


@app.route('/lessons/les1.2', methods=['GET', 'POST'])
def les12():
    form = Lesson1()
    if form.send.data:
        # answer = request.form.get('answer')
        # lesson = 1
        # num = 2
        # with open('test.py', 'w') as file:
        #     file.write(answer)
        #     ra = cur.execute(f"""SELECT answer FROM Exercises WHERE lesson = '{str(lesson)}' AND num = '{str(num)}'""").fetchall()
        #     check1 = check(ra[0][0], answer)
        #     check2 = check1[0]
        #     error = check1[1].split('\n')
        #     user_answer = check1[2]
        #     right_answer = ra[0][0]
        check2 = True
        error = ''
        user_answer = ''
        right_answer = ''
    else:
        check2 = ''
        error = ''
        user_answer = ''
        right_answer = ''
    pas = cur.execute(f'''SELECT login, forall, complete, wrong FROM Users WHERE login = "{User}"''').fetchall()
    username, forall, correct, wrong = pas[0][0], pas[0][1], pas[0][2], pas[0][3]
    cur.execute(f'''UPDATE Users
        SET forall = {int(forall) + 1}
        WHERE login = "{User}"''')
    if check2 == True:
        cur.execute(f'''UPDATE Users
        SET complete = {int(correct) + 1}
        WHERE login = "{User}"''')
    elif check2 ==False:
        cur.execute(f'''UPDATE Users
        SET complete = {int(wrong) + 1}
        WHERE login = "{User}"''')
    return render_template('les1.html', title='Уроки', form=form, check=check2, error=error, answer=user_answer,
                           exanswer=right_answer,
                           task=['Условие задачи "Привет, <user>!":', ' ', 'Напишите программу, которая принимает на вход имя пользователя',
                                 'и выводит его следующим образом: "Hello, <name>!".', ' ', 'Пример работы программы:', ' ', '|============|============|',
                                 '|User |Hello, User!|', '|============|============|'])


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
con.close()
