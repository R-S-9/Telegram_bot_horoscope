# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta
import time
import pytz


time_is = str(datetime.now())
time_is = time_is[:10]

previous_day = (str(datetime.now() + timedelta(days=1)))[:10]

end_of_url_today = {
    'Овен': '?znak=aries',  # aries
    'Телец': '?znak=taurus',  # taurus
    'Близнец': '?znak=gemini',  # gemini
    'Рак': '?znak=cancer',  # cancer
    'Лев': '?znak=leo',  # leo
    'Дева': '?znak=virgo',  # virgo
    'Весы': '?znak=libra',  # libra
    'Скорпион': '?znak=scorpio',  # scorpio
    'Стрелец': '?znak=sagittarius',  # sagittarius
    'Казерог': '?znak=capricorn',  # capricorn
    'Водолей': '?znak=aquarius',  # aquarius
    'Рыба': '?znak=pisces',  # pisces
}

end_of_url_tomorrow = {
    'Овен': '?znak=aries&kn=tomorrow',  # aries
    'Телец': '?znak=taurus&kn=tomorrow',  # taurus
    'Близнец': '?znak=gemini&kn=tomorrow',  # gemini
    'Рак': '?znak=cancer&kn=tomorrow',  # cancer
    'Лев': '?znak=leo&kn=tomorrow',  # leo
    'Дева': '?znak=virgo&kn=tomorrow',  # virgo
    'Весы': '?znak=libra&kn=tomorrow',  # libra
    'Скорпион': '?znak=scorpio&kn=tomorrow',  # scorpio
    'Стрелец': '?znak=sagittarius&kn=tomorrow',  # sagittarius
    'Казерог': '?znak=capricorn&kn=tomorrow',  # capricorn
    'Водолей': '?znak=aquarius&kn=tomorrow',  # aquarius
    'Рыба': '?znak=pisces&kn=tomorrow',  # pisces

}

# Имя браузера, что бы сервер думал что это человек
head = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/'
        '537.36'}


def pars_and_clean(One, Two):

    convert = []

    if One:

        for item in end_of_url_today.values():

            url = 'https://1001goroskop.ru/' + str(item)

            # Начинаем парсить данные с сайта.
            full_page = requests.get(url, headers=head)

            soup = BeautifulSoup(full_page.content, 'html.parser')
            convert_price = soup.findAll('div', {'itemprop': 'description'})

            # Обрабатываем нужные нам данные.
            convert.append([x.text for x in convert_price])

        return convert

    if Two:

        for item in end_of_url_tomorrow.values():

            url = 'https://1001goroskop.ru/' + str(item)

            # Начинаем парсить данные с сайта.
            full_page = requests.get(url, headers=head)

            soup = BeautifulSoup(full_page.content, 'html.parser')
            convert_price = soup.findAll('div', {'itemprop': 'description'})

            # Обрабатываем нужные нам данные.
            convert.append([x.text for x in convert_price])

        return convert


def sett(today, tomorrow):

    clue = []
    finish = []

    for key in end_of_url_today.keys():

        clue.append(str(key))

    for number, index in enumerate(today, 0):

        index.insert(0, clue[number])
        index.append(time_is)
        finish.append(index)

    clues = []
    finish_t = []

    for key in end_of_url_tomorrow.keys():

        clues.append(str(key))

    for number, index in enumerate(tomorrow, 0):

        index.insert(0, clues[number])
        index.append(previous_day)
        finish_t.append(index)

    return finish, finish_t


def create_connection(path):
    connect = None
    try:
        connect = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connect


def execute_query(connect):
    cursor = connect.cursor()
    try:
        for index in convert_today:
            cursor.execute(f'INSERT INTO users VALUES (?, ?, ?)', (index[0], index[1], index[2]))

        for index in convert_tomorrow:
            cursor.execute(f'INSERT INTO users VALUES (?, ?, ?)', (index[0], index[1], index[2]))
            connect.commit()
            print("Query executed successfully")

    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connect, query):
    cursor = connect.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


def del_query(connect):
    cursor = connect.cursor()
    try:
        cursor.execute(f'DELETE FROM users;')
        connect.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def look_for_hor():
    
    select_users = "SELECT * from users"
    users = execute_read_query(connection, select_users)

    for user in users:
        print(user)


while True:

    # Обновление на сайте происходит по московскому времени (4 утра по нашему)
    moscow_time = datetime.now(pytz.timezone('Europe/Moscow'))
    moscow_time = str(moscow_time)[11:16]

    if moscow_time == "12:33":

        print('The download process is underway.')

        first, Sec = True, False
        convert_today = pars_and_clean(first, Sec)

        Sec, first = True, False
        convert_tomorrow = pars_and_clean(first, Sec)

        convert_today, convert_tomorrow = sett(convert_today, convert_tomorrow)\

        connection = create_connection("base_of_horoscope.sqlite")

        del_query(connection)  # Удаляем данные в бд.

        execute_query(connection)  # Добаждвляем то что спарили.

        look_for_hor()  # Вызываем что бы проверить Гороскоп.

        print("Is's finish.")

        time.sleep(3600)

    else:

        print("It's not time yet - " + moscow_time)
        time.sleep(60)
