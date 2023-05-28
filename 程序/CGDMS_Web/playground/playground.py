import pymysql
from django.http import HttpResponse

from django.shortcuts import render

db = pymysql.connect(host='localhost',
                     user='root',
                     password='wue789789',
                     database='cgdms')
cursor = db.cursor()
cursor.execute("SELECT * FROM user WHERE Uno = '" + 'TochusC' + "' AND Upassword = '" + 'FearFor666' + "';")
if cursor.rowcount == 1:
    username, password, role = cursor.fetchone();
    sql = "SELECT * FROM STUDENT WHERE UNO = '" + username + "';"
    cursor.execute(sql)
    if cursor.rowcount == 0:
        sql = "SELECT * FROM STUDENT WHERE UNO = '" + username + "';"
        cursor.execute(sql)
    print(cursor.fetchone())
    # no, name, gender, birth, fno, mno, username = cursor.fetchone();
    # #将上面一行中的变量转为字典
    # self_info = {
    #     'no': no,
    #     "name": name,
    #     "gender": gender,
    #     "birth": birth,
    #     "fno": fno,
    #     "mno": mno,
    #     "username": username
    # }
    # print(self_info)