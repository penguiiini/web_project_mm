import os
import io
from flask import Flask, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, Label, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, AnyOf, NoneOf, ValidationError
import email_validator
import sqlite3
import sys


__factory = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MSilko&MMal'

con = sqlite3.connect('data/FlaskProject.db', check_same_thread=False)
cur = con.cursor()

lesson = 1
num = 1
NowUser = False
User = ''


def save_answer(lesson, num, answer, user, ball):
    cur.execute(f'''INSERT INTO Answers (lesson, num, user, answer, ball) VALUES ({lesson}, {num}, "{user}", "{answer}", {ball})''')
    con.commit()


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


class Theory(FlaskForm):
    back_to_tasks1 = SubmitField(u'\u2190' +  ' К другим заданиям')
    back_to_main1 = SubmitField(u'\u2302' +  ' На главную')


class Prom1(FlaskForm):
    back_to_main = SubmitField(u'\u2190' +  ' На главную')
    task1 = SubmitField('Задача 1')
    theory = SubmitField('Учебный материал')
    task2 = SubmitField('Задача 2')
    task3 = SubmitField('Задача 3')


def registration1(login, password, email):
    input = [(login, email, password, 0)]
    cur.executemany('INSERT INTO Users(login, email, password, complete) VALUES(?,?,?,?)', input)
    cur.execute('INSERT INTO Users(complete) VALUES(0)')
    con.commit()


def test1_1(answer):
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


def test1_2(answer):
    tests, count = ['U1', 'U2', 'U3'], 0
    for i in tests:
        count += 1

        old_out = sys.stdout
        old_err = sys.stderr

        redirected_output = sys.stdout = io.StringIO()

        out, exc = None, None

        f1 = sys.stdin
        ra = f"Hello, {i}!"
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


def test1_3(answer):
    path, count = 'tasks/', 0
    tests = [path + 'input1.txt', path + 'input2.txt', path + 'input3.txt',
             path + 'input4.txt']
    for i in tests:
        count += 1
        with open(i, 'r') as file:
            ra = file.read().split('\n')[::-1]
        del ra[ra.index('')]
        if '' in ra:
            ra = ra[ra.index('') + 1:]
        old_out = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        out, exc = None, None

        f1 = sys.stdin
        f = open(i, 'r')
        sys.stdin = f
        try:
            exec(answer)
        except:
            import traceback
            exc = traceback.format_exc()
            return ra, out, exc, count

        out = redirected_output.getvalue()
        f.close()
        sys.stdin = f1
        sys.stdout = old_out

        out = out.split('\n')[:-1]

        if ra != out:
            return ra, out, 'Сбой в тесте №', count
    return '', '', None, count


def check1_1(right_answer, answer):
    out, exc = test1_1(answer)
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


def check1_23(answer, task_num):
    right_answer, out, exc, count = None, None, None, None
    if task_num == 2:
        right_answer, out, exc, count = test1_2(answer)
    elif task_num == 3:
        right_answer, out, exc, count = test1_3(answer)

    if exc is None:
        return True, '', '', right_answer
    else:
        if exc[0:4] == 'Сбой':
            output_exc = exc + str(count) + ':'
            return False, output_exc, out, right_answer
        else:
            return False, exc, out, right_answer


@app.route('/')
def root():
    return redirect("/authorization")


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
            global NowUser, User
            NowUser = True
            User = username
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
                pas = cur.execute(f'''SELECT password FROM Users WHERE login="{username}"''').fetchall()
                if password == pas[0][0]:
                    return redirect("/lessons")
            except sqlite3.Error:
                pass
    if form.reg.data:
        return redirect("/registration")
    if form.guest.data:
        User = 'Guest'
        return redirect("/lessons")
    return render_template('authorization.html', title='Авторизация', form=form)


@app.route('/lessons', methods=['GET', 'POST'])
def main_window():
    form = Lessons()
    global NowUser, User
    if User == 'Guest':
        form.exit.label.text = 'Войти в аккаунт'
    if not NowUser:
        try:
            pas = cur.execute('''SELECT login, complete FROM Users WHERE login = 
    (SELECT userlogin FROM Lastuser WHERE id = 1)''').fetchall()
            username, correct = pas[0][0], pas[0][1]
            User = username
        except:
            User = 'Guest'
            username = 'Гость'
            correct = '-'
    else:
        pas = cur.execute(f'''SELECT login, complete FROM Users WHERE login = "{User}"''').fetchall()
        username, correct = pas[0][0], pas[0][1]
        User = username
    if form.lesson1.data:
        return redirect('/lessons/les1')
    if form.lesson2.data and User != 'Guest':
        return redirect('/lessons/les2')
    if form.exit.data:
        NowUser = False
        return redirect('/authorization')
    return render_template('lessons.html', title='Уроки', form=form, username=username,
                           correct=correct, is_guest=User)


@app.route('/lessons/les1', methods=['GET', 'POST'])
def les1():
    form = Prom1()
    if form.task1.data:
        return redirect('/lessons/les1/task1')
    if form.task2.data:
        return redirect('/lessons/les1/task2')
    if form.task3.data:
        return redirect('/lessons/les1/task3')
    if form.theory.data:
        return redirect('/lessons/les1/theory1')
    if form.back_to_main.data:
        return redirect('/lessons')
    return render_template('prom1.html', title='Урок 1', form=form)


@app.route('/lessons/les2', methods=['GET', 'POST'])
def les2():
    form = Prom1()
    if form.task1.data:
        return redirect('/lessons/les2/task1')
    if form.task2.data:
        return redirect('/lessons/les2/task2')
    if form.task3.data:
        return redirect('/lessons/les2/task3')
    if form.theory.data:
        return redirect('/lessons/les2/theory')
    if form.back_to_main.data:
        return redirect('/lessons')
    return render_template('prom1.html', title='Урок 2', form=form)


@app.route('/lessons/les1/theory', methods=['GET', 'POST'])
def theory1():
    form = Theory()
    if form.back_to_tasks1.data:
        return redirect('/lessons/les1')
    if form.back_to_main1.data:
        return redirect('/lessons')
    return render_template('theory1.html', form=form, title='Урок 1: ввод и вывод')


@app.route('/lessons/les1/task1', methods=['GET', 'POST'])
def task11():
    lesson = 1
    num = 1
    form = Lesson1()
    check2 = ''
    error = ''
    user_answer = ''
    right_answer = ''
    answer = ''
    plus = False
    try:
        pas = cur.execute(f'''SELECT answer, ball FROM Answers WHERE user = "{User}" AND lesson = {lesson} AND num = {num}''').fetchall()
        answer = pas[0][0]
        ball1 = pas[0][1]
        ra = cur.execute(f"""SELECT answer FROM Exercises WHERE lesson = '{str(lesson)}' AND num = '{str(num)}'""").fetchall()
        check1 = check1_1(ra[0][0], answer)
        check2 = check1[0]
        error = check1[1].split('\n')
        user_answer = check1[2]
        right_answer = ra[0][0]
        if check2 == True and ball1 != 1:
            plus = True
            cur.execute(f'''UPDATE Answers SET ball = 1 WHERE user = "{User}" AND lesson = {lesson} AND num = {num}''')
        if ball1 == 1:
            plus = True
    except:
        pass
    if form.send.data:
        answer = request.form.get('answer')
        ra = cur.execute(f"""SELECT answer FROM Exercises WHERE lesson = '{str(lesson)}' AND num = '{str(num)}'""").fetchall()
        check1 = check1_1(ra[0][0], answer)
        check2 = check1[0]
        error = check1[1].split('\n')
        user_answer = check1[2]
        right_answer = ra[0][0]
        if check2 == True:
            ball = 1
        else:
            ball = 0
        if User != 'Guest':
            pas = cur.execute(f'''SELECT user FROM Answers WHERE lesson = {lesson} AND num = {num}''').fetchall()
            if len(pas) != 0:
                for i in pas:
                    if i[0] != User:
                        save_answer(lesson, num, answer, User, ball)
                    else:
                        cur.execute(f'''UPDATE Answers SET answer = "{answer}" WHERE user = "{User}" AND lesson = {lesson} AND num = {num}''')
            else:
                save_answer(lesson, num, answer, User, ball)
    if form.back_to_tasks.data:
        return redirect('/lessons/les1')
    if form.back_to_main.data:
        return redirect('/lessons')
    if plus == False:
        try:
            pas = cur.execute(f'''SELECT login, complete FROM Users WHERE login = "{User}"''').fetchall()
            username, correct = pas[0][0], pas[0][1]
            if check2 == True:
                cur.execute(f'''UPDATE Users
                    SET complete = {int(correct) + 1}
                    WHERE login = "{User}"''')
        except:
            pass
    form.answer.data = answer
    con.commit()
    return render_template('task.html', title='Уроки', form=form, check=check2, error=error, answer=user_answer,
                           exanswer=right_answer,
                           task=['Условие задачи "Привет, world!":', ' ', 'Напишите программу, которая выводит "Hello, world!".'], rows=0)


@app.route('/lessons/les1/task2', methods=['GET', 'POST'])
def task12():
    lesson = 1
    num = 2
    form = Lesson1()
    check2 = ''
    error = ''
    user_answer = ''
    right_answer = ''
    answer = ''
    plus = False
    try:
        pas = cur.execute(f'''SELECT answer, ball FROM Answers WHERE user = "{User}" AND lesson = {lesson} AND num = {num}''').fetchall()
        answer = pas[0][0]
        ball1 = pas[0][1]
        check1 = check1_23(answer, 2)
        check2 = check1[0]
        error = check1[1].split('\n')
        user_answer = check1[2]
        right_answer = check1[3]
        if check2 == True and ball1 != 1:
            plus = True
            cur.execute(f'''UPDATE Answers SET ball = 1 WHERE user = "{User}" AND lesson = {lesson} AND num = {num}''')
        if ball1 == 1:
            plus = True
    except:
        pass
    if form.send.data:
        answer = request.form.get('answer')
        check1 = check1_23(answer, 2)
        check2 = check1[0]
        error = check1[1].split('\n')
        user_answer = check1[2]
        right_answer = check1[3]

        if check2 == True:
            ball = 1
        else:
            ball = 0
        if User != 'Guest':
            pas = cur.execute(f'''SELECT user FROM Answers WHERE lesson = {lesson} AND num = {num}''').fetchall()
            if len(pas) != 0:
                for i in pas:
                    if i[0] != User:
                        save_answer(lesson, num, answer, User, ball)
                    else:
                        cur.execute(f'''UPDATE Answers SET answer = "{answer}" WHERE user = "{User}" AND lesson = {lesson} AND num = {num}''')
            else:
                save_answer(lesson, num, answer, User, ball)
    if form.back_to_tasks.data:
        return redirect('/lessons/les1')
    if form.back_to_main.data:
        return redirect('/lessons')
    if plus == False:
        try:
            pas = cur.execute(f'''SELECT login, complete FROM Users WHERE login = "{User}"''').fetchall()
            username, correct = pas[0][0], pas[0][1]
            if check2 == True:
                cur.execute(f'''UPDATE Users
                SET complete = {int(correct) + 1}
                WHERE login = "{User}"''')
        except:
            pass
    form.answer.data = answer
    con.commit()
    return render_template('task.html', title='Уроки', form=form, check=check2, error=error, answer=user_answer,
                           exanswer=right_answer,
                           task=['Условие задачи "Привет, <user>!":', ' ', 'Напишите программу, которая принимает на вход имя пользователя', '(например, <name>), и выводит его следующим образом:', '"Hello, <name>!".', ' ', 'Пример работы программы:'], inputi='User', outputi='Hello, User!', rows=1)


@app.route('/lessons/les1/task3', methods=['GET', 'POST'])
def task13():
    lesson = 1
    num = 3
    form = Lesson1()
    check2 = ''
    error = ''
    user_answer = ''
    right_answer = ''
    answer = ''
    plus = False
    try:
        pas = cur.execute(f'''SELECT answer, ball FROM Answers WHERE user = "{User}" AND lesson = {lesson} AND num = {num}''').fetchall()
        answer = pas[0][0]
        ball1 = pas[0][1]
        check1 = check1_23(answer, 3)
        check2 = check1[0]
        error = check1[1].split('\n')
        user_answer = check1[2]
        right_answer = check1[3]
        if check2 == True and ball1 != 1:
            plus = True
            cur.execute(f'''UPDATE Answers SET ball = 1 WHERE user = "{User}" AND lesson = {lesson} AND num = {num}''')
        if ball1 == 1:
            plus = True
    except:
        pass
    if form.send.data:
        answer = request.form.get('answer')
        check1 = check1_23(answer, 3)
        check2 = check1[0]
        error = check1[1].split('\n')
        user_answer = check1[2]
        right_answer = check1[3]
        if check2 == True:
            ball = 1
        else:
            ball = 0
        if User != 'Guest':
            pas = cur.execute(f'''SELECT user FROM Answers WHERE lesson = {lesson} AND num = {num}''').fetchall()
            if len(pas) != 0:
                for i in pas:
                    if i[0] != User:
                        save_answer(lesson, num, answer, User, ball)
                    else:
                        cur.execute(f'''UPDATE Answers SET answer = "{answer}" WHERE user = "{User}" AND lesson = {lesson} AND num = {num}''')
            else:
                save_answer(lesson, num, answer, User, ball)
    if form.back_to_tasks.data:
        return redirect('/lessons/les1')
    if form.back_to_main.data:
        return redirect('/lessons')
    if plus == False:
        try:
            pas = cur.execute(f'''SELECT login, complete FROM Users WHERE login = "{User}"''').fetchall()
            username, correct = pas[0][0], pas[0][1]
            if check2 == True:
                cur.execute(f'''UPDATE Users
                SET complete = {int(correct) + 1}
                WHERE login = "{User}"''')
        except:
            pass
    form.answer.data = answer
    con.commit()
    return render_template('task.html', title='Уроки', form=form, check=check2, error=error, answer=user_answer,
                           exanswer=right_answer,
                           task=['Условие задачи "Обратный порядок":', ' ', 'Напишите программу, которая принимает на вход 4 строки,', 'а затем выводит их в обратном порядке. Помните, что каждая', 'новая строчка выводится одной новой командой <print()>.', '', 'Пример работы программы:'], inputi='A\nB\nC\nD', outputi='D\nC\nB\nA', rows=2, inputi2='1\n2\n3\n4', outputi2='4\n3\n2\n1')


@app.route('/lessons/les2/theory', methods=['GET', 'POST'])
def theory2():
    form = Theory()
    if form.back_to_tasks1.data:
        return redirect('/lessons/les2')
    if form.back_to_main1.data:
        return redirect('/lessons')
    return render_template('theory2.html', form=form, title='Урок 2: условный оператор')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
con.close()
