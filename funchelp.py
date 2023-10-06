from __future__ import annotations
from config import *
import re
from hashlib import md5
from pymysql import connect, cursors


def connecttodb():
    """Коннект с баззой данных"""

    conn = None
    try:
        conn = connect(  # образец конекта с бд
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            cursorclass=cursors.DictCursor)
        print(f'Connected to {DATABASE}')

    except Exception as ex:
        print('SQL error', type(ex), ex)

    return conn


########################################################################################################################
def get_hash(string: str) -> str:
    """Хэш-функция"""

    return md5(bytes(string, 'utf-8')).hexdigest()


########################################################################################################################
def check_value_for_registration(login: str, password: str, copy_password: str, email: str, conn) -> str:
    """проверяет данные с формы регистрации вернет строку с ошибкой если ошибок нет то пустую строку"""

    if not login or not password or not copy_password: return 'Enter all fields'
    if password != copy_password: return 'Passwords must match'
    if len(login) < 4: return 'The length of the login must be at least 4 characters'
    if len(password) < 8: return 'The password must be at least 8 characters long'

    pattern = re.compile(r'\A[а-яА-ЯA-Za-z0-9_-]+\Z')
    if not re.search(pattern, login): return 'The login must contain only letters numbers and _, -'
    if not re.search(pattern, password): return 'The password must contain only letters numbers and _, -'

    if '@mail.ru' in email: return 'Mail.ru is not supported due to blocking of our sent emails'
    if '@' not in email: return 'Mail entered incorrectly'

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM `users` WHERE `login` = '{login}';"""
        )
        user = cursor.fetchall()
    if user: return 'This login is busy'

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM `users` WHERE `password` = '{get_hash(password)}';"""
        )
        user = cursor.fetchall()
    if user: return 'Try a different password'

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM `users` WHERE `email` = '{email}';"""
        )
        user = cursor.fetchall()
    if user: return 'This mail is busy'

    return ''


########################################################################################################################
def check_value_for_entrance(login_or_email: str, password: str, conn) -> str:
    """проверяет данные с формы входа вернет строку с ошибкой если ошибок нет то пустую строку"""

    pattern = re.compile(r'\A[а-яА-ЯA-Za-z0-9_-]+\Z')
    if not login_or_email or not password: return 'Enter all fields'
    if not re.search(pattern, password): return 'The password must contain only letters numbers and _, -'
    if len(password) < 8: return 'The password must be at least 8 characters long'
    if '@mail.ru' in login_or_email: return 'Mail.ru is not supported due to blocking of our sent emails'

    if '@' not in login_or_email:  # ЕСЛИ ЭТО ЛОГИН!

        if not re.search(pattern, login_or_email): return 'The login must contain only letters numbers and _, -'
        if len(login_or_email) < 4: return 'The length of the login must be at least 4 characters'

        with conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT `password` FROM `users` WHERE `login` = '{login_or_email}'"""
            )
            password_in_bd = cursor.fetchall()
            if len(password_in_bd) == 0: return 'There is no such user'

            if password_in_bd[0]['password'] != get_hash(password): return 'Wrong password'

    else:  # ЕСЛИ ЭТО ПОЧТА!
        with conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT `password` FROM `users` WHERE `email` = '{login_or_email}'"""
            )
            password_in_bd = cursor.fetchall()

            if len(password_in_bd) == 0: return 'There is no such user'

            if password_in_bd[0]['password'] != get_hash(password): return 'Wrong password'

    return ''


########################################################################################################################
def check_value_for_change_password(copy_password: str, password: str, conn) -> str:
    """Проверяет значения для изменения пароля вернет строку с ошибкой если ошибок нет пустую стркоу"""

    if copy_password != password: return "Passwords must match"
    if len(password) < 8: return 'The password must be at least 8 characters long'

    pattern = re.compile(r'\A[а-яА-ЯA-Za-z0-9_-]+\Z')
    if not re.search(pattern, password): return 'The password must contain only letters numbers and _, -'

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM `users` WHERE password = '{get_hash(password)}'"""
        )
        user = cursor.fetchall()

    if user: return 'Try a different password'

    return ''


########################################################################################################################
def check_value_for_change_mail(new_mail: str, conn) -> str:
    """Проверяет данные для изменения почты вернет строку с ошибкой иначе пуситую стркоу"""

    if '@' not in new_mail: return 'Incorrect mail'
    elif '@mail.ru' in new_mail: return 'Mail.ru is not supported due to blocking of our sent emails'

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM `users` WHERE `email` = '{new_mail}'"""
        )
        user = cursor.fetchall()

    if user: return 'Mail is busy'

    return ''


########################################################################################################################
def check_value_for_change_login(login: str, conn) -> str:
    """Проверяет данные для изменения логина вернет строку с ошибкой иначе пуситую стркоу"""

    if len(login) < 4: return 'The length of the login must be at least 4 characters'
    pattern = re.compile(r'\A[а-яА-ЯA-Za-z0-9_-]+\Z')
    if not re.search(pattern, login): return 'The login must contain only letters numbers and _, -'

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM `users` WHERE `login` = '{login}';"""
        )
        user = cursor.fetchall()
    if user: return 'This login is busy'

    return ''


########################################################################################################################
def reg_user(login: str, password: str, email: str, conn):
    """Регистрирует пользователя"""

    with conn.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO `users` (`login`, `password`, `email`)
                    VALUES ('{login}', '{get_hash(password)}', '{email}')"""
        )

    conn.commit()


########################################################################################################################
def find_by_login(login: str, conn) -> None | tuple[dict]:
    """Ищет пользователей по логину если найдет вернет его почту иначе None"""

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT `email` FROM `users`
                WHERE `login` = '{login}'"""
        )

    mail = cursor.fetchall()

    if mail:
        return mail

    return None


########################################################################################################################
def find_by_mail(mail: str, conn) -> bool:
    """Ищет пользователя по почте если найдет вернет True иначе False"""

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT `id` FROM `users`
                WHERE email = '{mail}'"""
        )

        user = cursor.fetchall()

    return bool(user)


########################################################################################################################
def changing_the_password(new_password: str, mail: str, conn):
    """Меняет пароль пользователя"""

    with conn.cursor() as cursor:
        cursor.execute(
            f"""UPDATE `users` SET `password` = '{get_hash(new_password)}'
                WHERE `email` = '{mail}'"""
        )
    conn.commit()


########################################################################################################################
def changing_the_mail(new_mail: str, old_mail: str, conn):
    """Изменяет почту"""

    with conn.cursor() as cursor:
        cursor.execute(
            f"""UPDATE `users` SET `email` = '{new_mail}'
                WHERE `email` = '{old_mail}'"""
        )
    conn.commit()


########################################################################################################################
def changing_the_login(login: str, mail: str, conn):
    """Изменяет логин"""

    with conn.cursor() as cursor:
        cursor.execute(
            f"""UPDATE `users` SET `login` = '{login}'
                WHERE `email` = '{mail}'"""
        )
    conn.commit()


########################################################################################################################
def get_user_by_mail(mail: str, conn) -> tuple[dict, dict, dict, dict, dict]:
    """Возвращает все данные пользователя по почте"""

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM `users` WHERE email = '{mail}'"""
        )
        user = cursor.fetchall()

    return user


########################################################################################################################
def get_user_by_login(login: str, conn) -> tuple[dict, dict, dict, dict, dict]:
    """Возвращает все данные пользователя по логину"""

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM `users` WHERE login = '{login}'"""
        )
        user = cursor.fetchall()

    return user


########################################################################################################################
def get_record_by_mail(mail: str, conn) -> int:
    """Вернет рекорд пользователя по почте"""

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT `record` FROM `users` WHERE `email` = '{mail}'"""
        )
        user = cursor.fetchall()[0]

    return user['record']


########################################################################################################################
def get_all_records(conn) -> list:
    """Вернет все рекорды и логины пользоватлей"""

    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT `login`, `record` FROM `users`"""
        )
        users = cursor.fetchall()

    return users


########################################################################################################################
def saving_the_record(mail: str, record: int, conn):
    """Сохраняет рекорд в бд"""

    with conn.cursor() as cursor:
        cursor.execute(
           f"""UPDATE `users` SET `record` = {record}
                WHERE `email` = '{mail}'"""
        )
    conn.commit()


########################################################################################################################
def get_records_and_logins_for_table(users: list) -> list:
    """Преобразовывает значения для вывода в таблицу"""

    records = sorted([i['record'] for i in users], reverse=True)
    logins = []

    try:
        record1 = records[0]
        login1 = [i['login'] for i in users if i['record'] == record1 and i['login'] not in logins][0]
        logins.append(login1)
    except Exception:
        record1 = '----'
        login1 = '----'

    try:
        record2 = records[1]
        login2 = [i['login'] for i in users if i['record'] == record2 and i['login'] not in logins][0]
        logins.append(login2)
    except Exception:
        record2 = '----'
        login2 = '----'

    try:
        record3 = records[2]
        login3 = [i['login'] for i in users if i['record'] == record3 and i['login'] not in logins][0]
        logins.append(login3)
    except Exception:
        record3 = '----'
        login3 = '----'

    try:
        record4 = records[3]
        login4 = [i['login'] for i in users if i['record'] == record4 and i['login'] not in logins][0]
        logins.append(login4)
    except Exception:
        record4 = '----'
        login4 = '----'

    try:
        record5 = records[4]
        login5 = [i['login'] for i in users if i['record'] == record5 and i['login'] not in logins][0]
        logins.append(login5)
    except Exception:
        record5 = '----'
        login5 = '----'

    try:
        record6 = records[5]
        login6 = [i['login'] for i in users if i['record'] == record6 and i['login'] not in logins][0]
        logins.append(login6)
    except Exception:
        record6 = '----'
        login6 = '----'

    try:
        record7 = records[6]
        login7 = [i['login'] for i in users if i['record'] == record7 and i['login'] not in logins][0]
        logins.append(login7)
    except Exception:
        record7 = '----'
        login7 = '----'

    try:
        record8 = records[7]
        login8 = [i['login'] for i in users if i['record'] == record8 and i['login'] not in logins][0]
        logins.append(login8)
    except Exception:
        record8 = '----'
        login8 = '----'

    try:
        record9 = records[8]
        login9 = [i['login'] for i in users if i['record'] == record9 and i['login'] not in logins][0]
        logins.append(login9)
    except Exception:
        record9 = '----'
        login9 = '----'

    try:
        record10 = records[9]
        login10 = [i['login'] for i in users if i['record'] == record10 and i['login'] not in logins][0]
        logins.append(login10)
    except Exception:
        record10 = '----'
        login10 = '----'

    return [{'record1': record1, 'login1': login1},
            {'record2': record2, 'login2': login2},
            {'record3': record3, 'login3': login3},
            {'record4': record4, 'login4': login4},
            {'record5': record5, 'login5': login5},
            {'record6': record6, 'login6': login6},
            {'record7': record7, 'login7': login7},
            {'record8': record8, 'login8': login8},
            {'record9': record9, 'login9': login9},
            {'record10': record10, 'login10': login10}]
