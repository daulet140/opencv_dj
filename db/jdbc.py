# -*- coding: utf-8 -*-
import sqlite3
import Person
import datetime

# Создаем соединение с нашей базой данных
conn = sqlite3.connect("db.sqlite3")
# Создаем курсор - это специальный объект который делает запросы и получает их результаты
cursor = conn.cursor()


# def creaeteTable():
#     cursor.execute(
#         "CREATE TABLE IF NOT EXISTS detector_person(id INTEGER ,  max_age text,createtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP )")
#     conn.commit()


def insert2Table(person):
    print(person.getId())
    insert = "insert into main.detector_person(name,pub_date) values ('{}','{}')".format(person.getId(), datetime.datetime.now())
    cursor.execute(insert)
    conn.commit()
