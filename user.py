from hashlib import md5
from flask_login import UserMixin
import SQL


class User(UserMixin):
    type = ""


def verify(username: str, password: str):
    if isExist(username):
        psw = md5(password.encode('UTF-8')).hexdigest()
        pswget = SQL.selectone(
            '''
            select password
            from accounts
            where account='%s'
            ''' % username)
        if len(pswget) == 0:
            return False
        if psw == pswget['password']:
            return True
        else:
            return False
    else:
        return False


def register(usr, psw, typ, name, sex, age: int, dept, grade: int, classs: int):
    SQL.cur.execute('''
    select account from accounts where account='%s'
    ''' % usr)
    usrget = SQL.cur.fetchall()
    if len(usrget) > 0:
        if usr == usrget[0]['account']:
            return 2
    pswmd5 = md5(psw.encode('UTF-8')).hexdigest()
    instr = '''insert into accounts (account, password, type)
    values ('%s', '%s', '%s')''' % (usr, pswmd5, typ)
    if typ == 'student':
        SQL.cur.execute('select count(Num) cnt from students')
        num = 'stu' + str(int(SQL.cur.fetchall()[0]['cnt']) + 1)
        stustr = '''insert into students (Name, Num, Age, Class, Grade, Dept, sex, account)
            values ('%s', '%s', %d, %d, %d, '%s', '%s', '%s')''' % (name, num, age, classs, grade, dept, sex, usr)
        SQL.cur.execute(stustr)
        SQL.conn.commit()
    elif typ == 'teacher':
        SQL.cur.execute('select count(Num) cnt from teachers')
        num = 'tch' + str(int(SQL.cur.fetchall()[0]['cnt']) + 1)
        stustr = '''insert into teachers (name, sex, age, num, dept, account)
                    values ('%s', '%s', %d, '%s', '%s', '%s')''' % (name, sex, age, num, dept, usr)
        SQL.cur.execute(stustr)
        SQL.conn.commit()
    try:
        SQL.cur.execute(instr)
        SQL.conn.commit()
    except:
        return 0
    else:
        return 1


def gettype(user) -> str:
    try:
        type = SQL.select('select type from accounts where account=\'%s\'' % user)[0]['type']
    except:
        return ''
    else:
        return type


def isExist(usr):
    try:
        SQL.select('select account from accounts where account=\'%s\'' % usr)[0]['account']
    except:
        return False
    else:
        return True


def isExistStu(num):
    try:
        SQL.select('select Num from students where Num=\'%s\'' % num)[0]['Num']
    except:
        return False
    else:
        return True


def isExistTch(num):
    try:
        SQL.select('select num from teachers where num=\'%s\'' % num)[0]['num']
    except:
        return False
    else:
        return True


def setStatus(pswnew, name, sex, age: int, dept, grade: int, classs: int, user):
    if pswnew != '':
        pswmd5 = md5(pswnew.encode('UTF-8')).hexdigest()
        sqlstr = '''update accounts
        set password = '%s' 
        where account = '%s'
        ''' % (pswmd5, user)
        SQL.cur.execute(sqlstr)
        SQL.conn.commit()
    if gettype(user) == 'student':
        sqlstr = '''update students
        set Name='%s', sex='%s', Age='%d', Dept='%s', Grade='%d', Class='%d'
        where account = '%s'
        ''' % (name, sex, age, dept, grade, classs, user)
    elif gettype(user) == 'teacher':
        sqlstr = '''update teachers
                set name='%s', sex='%s', age='%d', dept='%s'
                where account = '%s'
                ''' % (name, sex, age, dept, user)
    SQL.cur.execute(sqlstr)
    SQL.conn.commit()


def getname(user) -> str:
    if gettype(user) == 'student':
        return SQL.select('select Name from students where account=\'%s\'' % user)[0]['Name']
    elif gettype(user) == 'teacher':
        return SQL.select('select name from teachers where account=\'%s\'' % user)[0]['name']


def getnum(user) -> str:
    if gettype(user) == 'student':
        return SQL.select('select Num from students where account=\'%s\'' % user)[0]['Num']
    elif gettype(user) == 'teacher':
        return SQL.select('select num from teachers where account=\'%s\'' % user)[0]['num']


def getage(user) -> str:
    if gettype(user) == 'student':
        return SQL.select('select Age from students where account=\'%s\'' % user)[0]['Age']
    elif gettype(user) == 'teacher':
        return SQL.select('select age from teachers where account=\'%s\'' % user)[0]['age']


def getsex(user) -> str:
    if gettype(user) == 'student':
        return SQL.select('select sex from students where account=\'%s\'' % user)[0]['sex']
    elif gettype(user) == 'teacher':
        return SQL.select('select sex from teachers where account=\'%s\'' % user)[0]['sex']


def getdept(user) -> str:
    if gettype(user) == 'student':
        return SQL.select('select Dept from students where account=\'%s\'' % user)[0]['Dept']
    elif gettype(user) == 'teacher':
        return SQL.select('select dept from teachers where account=\'%s\'' % user)[0]['dept']


def getgrade(user) -> str:
    if gettype(user) == 'student':
        return SQL.select('select Grade from students where account=\'%s\'' % user)[0]['Grade']
    elif gettype(user) == 'teacher':
        return 0  # SQL.select('select grade from teachers where account=\'%s\'' % user)[0]['grade']


def getclass(user) -> str:
    if gettype(user) == 'student':
        return SQL.select('select Class from students where account=\'%s\'' % user)[0]['Class']
    elif gettype(user) == 'teacher':
        return 0  # SQL.select('select class from teachers where account=\'%s\'' % user)[0]['class']


def getaccount(num: str) -> str:
    if num[:3] == 'stu':
        acc = SQL.select('select account from students where Num = \'%s\'' % num)[0]['account']
    elif num[:3] == 'tch':
        acc = SQL.select('select account from teachers where num = \'%s\'' % num)[0]['account']
    return acc


def logout():
    global loguser
    global log
    global usrtyp
    loguser = ''
    usrtyp = ''
    log = 0


def delstu(num: str):
    SQL.cur.execute('delete from score where Snum=\'%s\'' % num)
    SQL.conn.commit()


def delcourse(num: str, Cnum: str):
    try:
        SQL.cur.execute('delete from score where Cnum=\'%s\' and Snum=\'%s\'' % (Cnum, num))
        SQL.conn.commit()
        return True
    except:
        return False


def scorein(num: str, Cname: str, score: int, grade: int, Cnum: str, Lnum: int):
    SQL.cur.execute('''insert into score(Snum, course, score, grade, Cnum, Lnum)
                        values ('%s', '%s', %d, %d, '%s', %d)
                        ''' % (num, Cname, score, grade, Cnum, Lnum))
    SQL.conn.commit()
