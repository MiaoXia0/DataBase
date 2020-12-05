import pymssql

global cur
global conn


def login():
    try:
        global conn
        conn = pymssql.connect(host='localhost',
                               server='DESKTOP-P475VGJ',
                               port='1433',
                               user='miaoxiao',
                               password='miaoxiao123',
                               database='Stu',
                               charset='utf8',
                               as_dict=True)
    except:
        print("SQL Connection Failed!")
    else:
        global cur
        cur = conn.cursor()
        print("SQL Connection Succeed!")


def select(sqlStr):
    cur.execute(sqlStr)
    data = cur.fetchall()
    return data


def selectone(sqlStr):
    cur.execute(sqlStr)
    data = cur.fetchone()
    return data
