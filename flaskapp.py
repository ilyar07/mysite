from random import randint
from flask import Flask, render_template, request, url_for, redirect, make_response
import funchelp as fh

app = Flask(__name__)


########################################################################################################################
@app.route('/', methods=['POST', 'GET'])
def index():
    """Главная страница"""

    if request.method == 'POST':
        user_login_or_mail = request.form.get('login')
        user_password = request.form.get('password')
    else:
        user_login_or_mail = request.args.get('login')
        user_password = request.args.get('password')

    error = ' '

    if user_login_or_mail or user_password:
        conn = fh.connecttodb()
        error = fh.check_value_for_entrance(user_login_or_mail, user_password, conn)  # проверяем на ошибки

    if user_login_or_mail and not error:
        if '@' in user_login_or_mail:  # ЭТО ПОЧТА
            conn = fh.connecttodb()
            user = fh.get_user_by_mail(user_login_or_mail, conn)[0]
        else:  # ЭТО ЛОГИН
            conn = fh.connecttodb()
            user = fh.get_user_by_login(user_login_or_mail, conn)[0]

        return redirect(url_for('account', login=user['login'], password=user['password'], mail=user['email']))

    return render_template('index.html', error=error)


########################################################################################################################
@app.route('/registration', methods=['POST', 'GET'])
def registrarion():
    """Страница регистрации"""

    if request.method == 'POST':
        user_login = request.form.get('login')
        user_password = request.form.get('password')
        user_copy_password = request.form.get('copy-password')
        user_mail = request.form.get('email')
    else:
        user_login = request.args.get('login')
        user_password = request.args.get('password')
        user_copy_password = request.args.get('copy-password')
        user_mail = request.args.get('email')

    error = ' '

    if user_login or user_password or user_copy_password or user_mail:
        conn = fh.connecttodb()
        error = fh.check_value_for_registration(user_login, user_password,
                                             user_copy_password, user_mail,
                                             conn)  # проверяем на ошибки

    html = render_template('reg-page.html', error=error)
    responce = make_response(html)

    if not error:
        rand = str(randint(10000, 99999))  # код который будет отправлен в письме

        responce.set_cookie('rand', rand, max_age=600)
        responce.set_cookie('user_login', user_login, max_age=600)
        responce.set_cookie('user_mail', user_mail, max_age=600)
        responce.set_cookie('user_password', user_password, max_age=600)

        return responce

    return responce


########################################################################################################################
@app.route('/account', methods=['GET', 'POST'])
def account():
    """Страница аккаунта"""

    if request.args.get('login') and request.args.get('password') and request.args.get(
            'mail'):  # получаю данные с url если они там есть
        login = request.args.get('login')
        password = request.args.get('password')
        mail = request.args.get('mail')
    else:  # иначе с cookies
        login = request.cookies.get('login')
        password = request.cookies.get('password')
        mail = request.cookies.get('mail')

    conn = fh.connecttodb()
    users = fh.get_all_records(conn)
    records = fh.get_records_and_logins_for_table(users)

    html = render_template('account.html',
                           record1=records[0]['record1'],
                           login1=records[0]['login1'],
                           record2=records[1]['record2'],
                           login2=records[1]['login2'],
                           record3=records[2]['record3'],
                           login3=records[2]['login3'],
                           record4=records[3]['record4'],
                           login4=records[3]['login4'],
                           record5=records[4]['record5'],
                           login5=records[4]['login5'],
                           record6=records[5]['record6'],
                           login6=records[5]['login6'],
                           record7=records[6]['record7'],
                           login7=records[6]['login7'],
                           record8=records[7]['record8'],
                           login8=records[7]['login8'],
                           record9=records[8]['record9'],
                           login9=records[8]['login9'],
                           record10=records[9]['record10'],
                           login10=records[9]['login10'],
                           )
    response = make_response(html)

    response.set_cookie('login', login)  # зписываю в cookie чтобы не потерять их при перезагрузки страницы
    response.set_cookie('password', password)
    response.set_cookie('mail', mail)

    return response


########################################################################################################################
@app.route('/confirm-mail', methods=['GET', 'POST'])
def confirm_mail():
    """Подтверждение почты"""

    info = ''
    rand = request.cookies.get('rand')
    user_login = request.cookies.get('user_login')
    user_password = request.cookies.get('user_password')
    user_mail = request.cookies.get('user_mail')

    html = render_template('confirm-mail.html', info=info, mail=user_mail)
    response = make_response(html)

    if not rand and not user_login and not user_password and not user_mail:
        return redirect(url_for('index'))

    if rand.isdigit():
        response.set_cookie('rand', fh.get_hash(rand))

    if request.method == 'POST':
        code = request.form.get('code')
    else:
        code = request.args.get('code')

    if code:  # если код введен
        if not code.isdigit() and code != '':
            return render_template('confirm-mail.html', info='Code wrong!', mail=user_mail)

        code = fh.get_hash(code)

        if code == rand:  # если хэш совпал регистрирую пользователя

            response = make_response(
                render_template('confirm-mail.html', info='You have successfully registered', mail=user_mail))

            response.delete_cookie('rand')  # удаляю все cookie
            response.delete_cookie('user_login')
            response.delete_cookie('user_password')
            response.delete_cookie('user_mail')

            conn = fh.connecttodb()
            fh.reg_user(user_login, user_password, user_mail, conn)
            return response

        else:
            return render_template('confirm-mail.html', info='Code wrong!', mail=user_mail)

    return response


########################################################################################################################
@app.route('/confirm-new-mail', methods=['GET', 'POST'])
def confirm_new_mail():
    """Подтверждение новой почты"""

    info = ''
    rand = request.cookies.get('rand')
    new_mail = request.cookies.get('new_mail')

    html = render_template('confirm-new-mail.html', info=info, mail=new_mail)
    response = make_response(html)

    if not rand and not new_mail:
        return redirect(url_for('index'))

    if rand.isdigit():
        response.set_cookie('rand', fh.get_hash(rand))

    if request.method == 'POST':
        code = request.form.get('code')
    else:
        code = request.args.get('code')

    if code:
        if not code.isdigit() and code != '':
            return render_template('confirm-new-mail.html', info='Code wrong!', mail=new_mail)

        code = fh.get_hash(code)

        if code == rand:
            response = make_response(
                render_template('confirm-new-mail.html', info='You have successfully changed your mail', mail=new_mail))

            response.delete_cookie('new_mail')
            response.delete_cookie('rand')

            old_mail = request.cookies.get('mail')
            conn = fh.connecttodb()
            fh.changing_the_mail(new_mail, old_mail, conn)

            return response

        else:
            return render_template('confirm-new-mail.html', info='Code wrong!', mail=new_mail)

    return response


########################################################################################################################
@app.route('/select-account', methods=['GET', 'POST'])
def select_account():
    """Выбор какому аккаунту менять пароль"""

    if request.method == 'POST':
        login_or_mail = request.form.get('login')
    else:
        login_or_mail = request.args.get('login')

    error = ' '

    if login_or_mail:

        if '@' in login_or_mail:  # если это почта
            conn = fh.connecttodb()
            if fh.find_by_mail(login_or_mail, conn):
                rand = str(randint(10000, 99999))  # код который будет отправлен в письме

                response = make_response(render_template('select-account.html', error=''))
                response.set_cookie('mail', login_or_mail, max_age=600)
                response.set_cookie('rand', rand, max_age=600)

                return response

            return render_template('select-account.html', error='There is no user with such mail')

        else:
            conn = fh.connecttodb()# если это логин
            mail = fh.find_by_login(login_or_mail, conn)
            if not mail:
                return render_template('select-account.html', error='There is no user with such login')

            mail = mail[0]['email']
            rand = str(randint(10000, 99999))  # код который будет отправлен в письме

            response = make_response(render_template('select-account.html', error=''))
            response.set_cookie('mail', mail, max_age=600)
            response.set_cookie('rand', rand, max_age=600)

            return response

    return render_template('select-account.html', error=error)


########################################################################################################################
@app.route('/confirm-change-password', methods=['GET', 'POST'])
def confirm_change_password():
    """Подтверждение что этот аккаунт принадлежит пользователю"""

    mail = request.cookies.get('mail')
    rand = request.cookies.get('rand')
    info = ''

    html = render_template('confirm-change-password.html', info=info, mail=mail)
    response = make_response(html)

    if rand.isdigit():
        response.set_cookie('rand', fh.get_hash(rand))

    if request.method == 'POST':
        code = request.form.get('code')
    else:
        code = request.args.get('code')

    if code:  # если код введен

        if not code.isdigit() and code != '':
            return render_template('confirm-change-password.html', info='Code wrong!', mail=mail)

        code = fh.get_hash(code)
        if code == rand:  # если совпал отправляю дальше
            return redirect(url_for('change_password'))

        else:
            return render_template('confirm-change-password.html', info='Code wrong!', mail=mail)

    return response


########################################################################################################################
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """Изменение пароля"""

    if request.method == 'POST':
        password = request.form.get('password')
        copy_password = request.form.get('copy-password')
    else:
        password = request.args.get('password')
        copy_password = request.args.get('copy-password')

    error = ' '

    if copy_password or password:
        conn = fh.connecttodb()
        error = fh.check_value_for_change_password(copy_password, password, conn)  # проверяем на ошибки

    if not error:  # если ошибок нет
        html = render_template('change-password.html', error='Password changed successfully')
        response = make_response(html)

        mail = request.cookies.get('mail')
        conn = fh.connecttodb()
        fh.changing_the_password(password, mail, conn)

        response.delete_cookie('rand')

        return response

    return render_template('change-password.html', error=error)


########################################################################################################################
@app.route('/account/personal_data', methods=['GET', 'POST'])
def personal_data():
    """Персональные данные"""

    login = request.cookies.get('login')
    password = request.cookies.get('password')
    mail = request.cookies.get('mail')

    return render_template('personal-data.html', login=login, password=password, mail=mail)


########################################################################################################################
@app.route('/account/about-me', methods=['GET', 'POST'])
def about_me():
    """Информация обо мне"""

    return render_template('about-me.html')


########################################################################################################################
@app.route('/account/dino', methods=['GET', 'POST'])
def dino():
    """Игра динозаврик"""

    mail = request.cookies.get('mail')
    conn = fh.connecttodb()
    record = fh.get_record_by_mail(mail, conn)

    return render_template('dino.html', record=record)


########################################################################################################################
@app.route('/change-mail', methods=['GET', 'POST'])
def change_mail():
    """Изменение почты"""

    if request.method == 'POST':
        new_mail = request.form.get('new_mail')
    else:
        new_mail = request.args.get('new_mail')

    error = ' '

    if new_mail:
        conn = fh.connecttodb()
        error = fh.check_value_for_change_mail(new_mail, conn)

    if not error:
        rand = str(randint(10000, 99999))  # код который будет отправлен в письме

        response = make_response(render_template('change-mail.html', error=error))
        response.set_cookie('new_mail', new_mail, max_age=600)
        response.set_cookie('rand', rand, max_age=600)

        return response

    return render_template('change-mail.html', error=error)


########################################################################################################################
@app.route('/change-login', methods=['GET', 'POST'])
def change_login():
    """Изменение почты"""

    if request.method == 'POST':
        login = request.form.get('login')
    else:
        login = request.args.get('login')

    error = ' '

    if login:
        conn = fh.connecttodb()
        error = fh.check_value_for_change_login(login, conn)  # проверяем на ошибки

    if not error:  # если ошибок нет
        html = render_template('change-login.html', error='Login changed successfully')
        response = make_response(html)

        mail = request.cookies.get('mail')
        conn = fh.connecttodb()
        fh.changing_the_login(login, mail, conn)

        return response

    return render_template('change-login.html', error=error)


########################################################################################################################
@app.route('/save-record', methods=['POST'])
def save_record():
    """Сохраняет рекорд в бд"""

    record = int(request.form.get('record'))
    mail = request.cookies.get('mail')
    conn = fh.connecttodb()
    fh.saving_the_record(mail, record, conn)

    return ''