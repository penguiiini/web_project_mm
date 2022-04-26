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
    reg = SubmitField('Зарегестрироваться')
    guest = SubmitField('Войти как гость')


class Lessons(FlaskForm):
    lesson1 = SubmitField('Урок - 1: ввод и вывод данных')
    exit = SubmitField('Выйти из аккаунта')
    lesson2 = SubmitField('Урок - 2: тема')


class Lesson1(FlaskForm):
    back_to_tasks = SubmitField(u'\u2190' +  ' К другим заданиям')
    back_to_main = SubmitField(u'\u2302' +  ' На главную')
    answer = TextAreaField('Введите решение', validators=[DataRequired("Это поле обязательно!")])
    send = SubmitField('Отправить')


class Prom1(FlaskForm):
    back_to_main = SubmitField(u'\u2190' +  ' На главную')
    task1 = SubmitField('Задача 1')
    theory = SubmitField('Учебный материал')
    task2 = SubmitField('Задача 2')
    task3 = SubmitField('Задача 3')


def registration1(login, password, email):
    input = [(login, email, password, 0, 0, 0)]
    cur.executemany('INSERT INTO Users(login, email, password, forall, complete, wrong) VALUES(?,?,?,?,?,?)', input)
    cur.execute('INSERT INTO Users(forall, complete, wrong) VALUES(0,0,0)')
    con.commit()


def test11(answer):
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


def test12(answer):
    tests, count = {'U1': None, 'U2': None, 'U3': None}, 0
    for i in tests:
        count += 1

        old_out = sys.stdout
        old_err = sys.stderr

        redirected_output = sys.stdout = io.StringIO()

        out, exc = None, None

        f1 = sys.stdin
        ra= f"Hello, {i}!"
        f = io.StringIO(i)
        sys.stdin = f

        try:
            exec(answer)
        except:
            import traceback
            exc = traceback.format_exc()
            return ra, out, exc, count

        out = redirected_output.getvalue()
        sys.stdout = old_out
        sys.stderr = old_err

        f.close()
        sys.stdin = f1
        
        ra, out = ra.strip(), out.strip() 
        
        if ra != out:
            return ra, out, 'Сбой в тесте №', count
    return '', '', None, count


def check11(right_answer, answer):
    out, exc = test11(answer)
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
            er = f'Сбой в тесте №1:'
            er.split('/n')
        else:
            er = exc
            er.split('/n')
        return False, er, output


def check12(answer):
    right_answer, out, exc, count = test12(answer)
    
    if exc is None:
        return True, '', '', right_answer
    else:
        if exc[0:4] == 'Сбой':
            output_exc = exc + str(count) + ':'
            return False, output_exc, out, right_answer
        else:
            return False, exc, out, right_answer


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
    if form.submit.data:
        if form.validate_on_submit():
            username = request.form.get('username')
            password = request.form.get('password')
            remember_me = request.form.get('remember_me')
            last = cur.execute('''SELECT userlogin FROM Lastuser WHERE id = 1''').fetchall()
            if username != last[0][0]:
                cur.execute(f'''DELETE FROM Lastuser WHERE id = 1''')
                cur.execute(f'''INSERT INTO Lastuser(userlogin) VALUES("1")''')
                con.commit()
            if remember_me:
                cur.execute(f'''DELETE FROM Lastuser WHERE id = 1''')
                cur.execute(f'''INSERT INTO Lastuser(id, userlogin) VALUES(1, "{username}")''')
                con.commit()
            else:
                cur.execute(f'''DELETE FROM Lastuser WHERE id = 1''')
                cur.execute(f'''INSERT INTO Lastuser(id, userlogin) VALUES(1, "1")''')
                con.commit()
            try:
                pas = cur.execute(f'''SELECT password FROM Users WHERE login="{username}"''')
            except sqlite3.Error:
                pass
            global NowUser, User
            NowUser = True
            User = username
            return redirect("/lessons")
    if form.reg.data:
        return redirect("/registration")
    if form.guest.data:
        User = 'Guest'
        return redirect("/lessons")
    return render_template('authorization.html', title='Авторизация', form=form)


@app.route('/lessons', methods=['GET', 'POST'])
def main_window():
    form = Lessons()
    global NowUser
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
    if form.lesson2.data:
        return redirect('/lessons/les1.2')
    if form.exit.data:
        NowUser = False
        return redirect('/authorization')
    return render_template('lessons.html', title='Уроки', form=form, username=username, forall=forall,
                           correct=correct, wrong=wrong)


@app.route('/lessons/les1', methods=['GET', 'POST'])
def les1():
    form = Prom1()
    if form.task1.data:
        return redirect('/lessons/les1/task1')
    if form.task2.data:
        return redirect('/lessons/les1/task2')
    if form.task3.data:
        return redirect('/lessons/les1/task3')
    if form.back_to_main.data:
        return redirect('/lessons')
    return render_template('prom1.html', title='Урок 1', form=form)


@app.route('/lessons/les1/task1', methods=['GET', 'POST'])
def task11():
    form = Lesson1()
    check2 = ''
    error = ''
    user_answer = ''
    right_answer = ''
    if form.send.data:
        answer = request.form.get('answer')
        lesson = 1
        num = 1
        ra = cur.execute(f"""SELECT answer FROM Exercises WHERE lesson = '{str(lesson)}' AND num = '{str(num)}'""").fetchall()
        check1 = check11(ra[0][0], answer)
        check2 = check1[0]
        error = check1[1].split('\n')
        user_answer = check1[2]
        right_answer = ra[0][0]
    if form.back_to_tasks.data:
        return redirect('/lessons/les1')
    if form.back_to_main.data:
        return redirect('/lessons')
    try:
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
    except:
        pass
    return render_template('task.html', title='Уроки', form=form, check=check2, error=error, answer=user_answer,
    exanswer=right_answer,
    task=['Условие задачи "Привет, world!":', ' ', 'Напишите программу, которая выводит "Hello, world!"'])


@app.route('/lessons/les1/task2', methods=['GET', 'POST'])
def task12():
    form = Lesson1()
    check2 = ''
    error = ''
    user_answer = ''
    right_answer = ''
    if form.send.data:
        answer = request.form.get('answer')
        check1 = check12(answer)
        check2 = check1[0]
        error = check1[1].split('\n')
        user_answer = check1[2]
        right_answer = check1[3]
    if form.back_to_tasks.data:
        return redirect('/lessons/les1')
    if form.back_to_main.data:
        return redirect('/lessons')
    try:
        pas = cur.execute(f'''SELECT login, forall, complete, wrong FROM Users WHERE login = "{User}"''').fetchall()
        username, forall, correct, wrong = pas[0][0], pas[0][1], pas[0][2], pas[0][3]
        cur.execute(f'''UPDATE Users
            SET forall = {int(forall) + 1}
            WHERE login = "{User}"''')
        if check2 == True:
             cur.execute(f'''UPDATE srs
                SET complete = {int(correct) + 1}
                WHERE login = "{User}"''')
        elif check2 ==False:
            cur.execute(f'''UPDATE Users
                 SET complete = {int(wrong) + 1}
                 WHERE login = "{User}"''')
    except:
        pass

    return render_template('task.html', title='Уроки', form=form, check=check2, error=error, answer=user_answer,
                           exanswer=right_answer,
                           task=['Условие задачи "Привет, <user>!":', ' ', 'Напишите программу, которая принимает на вход имя пользователя (например, <name>),',
                                 'и выводит его следующим образом: "Hello, <name>!".', ' ', 'Пример работы программы:', ' ', '|============|============|', '| Ввод:      | Вывод:     |', '|============|============|',
                                 '|User        |Hello, User!|', '|============|============|'])


@app.route('/lessons/les1/task3', methods=['GET', 'POST'])
def task13():
    form = Lesson1()
    if form.send.data:
        answer = request.form.get('answer')
        lesson = 1
        num = 1
        ra = cur.execute(f"""SELECT answer FROM Exercises WHERE lesson = '{str(lesson)}' AND num = '{str(num)}'""").fetchall()
        check1 = check13(ra[0][0], answer)
        check2 = check1[0]
        error = check1[1].split('\n')
        user_answer = check1[2]
        right_answer = ra[0][0]
    else:
        check2 = ''
        error = ''
        user_answer = ''
        right_answer = ''
    try:
        pa = cur.execute(f'''SELECT login, forall, complete, wrong FROM Users WHERE login = "{User}"''').fetchall()
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
    except:
        pass
    return render_template('task.html', title='Уроки', form=form, check=check2, error=error, answer=user_answer,
        exanswer=right_answer,
        task=['Условие задачи "Привет, world!":', ' ', 'Напишите программу, которая выводит "Hello, world!"'])


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
con.close()  
