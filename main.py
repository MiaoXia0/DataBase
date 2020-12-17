from datetime import *

from flask import Flask, request, render_template, redirect
from flask_login import login_user, logout_user, LoginManager, login_required, current_user, AnonymousUserMixin
from pandas import DataFrame
import SQL
import user
from user import User

app = Flask(__name__)
app.secret_key = 'fc40b27b6b513b756ce785f3eecf8a6d'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'log'
login_manager.login_message = '请先登录！'

SQL.login()


@login_manager.user_loader
def load_user(user_id):
    usr = SQL.select('select * from accounts where account=\'%s\'' % user_id)
    if len(usr) > 0:
        curr_user = User()
        curr_user.type = user.gettype(user_id)
        curr_user.id = user_id
        return curr_user


@app.route('/')
def index():
    if not current_user.is_anonymous:
        table = []

        if user.gettype(current_user.id) == 'student':
            table = SQL.select('''select * 
                from students 
                where account = '%s'
                ''' % current_user.id)
        elif user.gettype(current_user.id) == 'teacher':
            table = SQL.select('''select * 
                        from teachers 
                        where account = '%s'
                        ''' % current_user.id)
        return render_template('index.html',
                               login=1,
                               username=current_user.id,
                               type=user.gettype(current_user.id),
                               StatusTable=table,
                               typ=user.gettype(current_user.id))
    else:
        return render_template('index.html', login=0, username='', type='')


@app.route('/login', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        next = request.form['next']
        if user.verify(username, password):
            curr_user = User()
            curr_user.id = username
            curr_user.type = user.gettype(username)
            login_user(curr_user)
            if next != '':
                return render_template('loginsucceed.html',
                                       username=username, usertype=current_user.type, next=next)
            else:
                return render_template('loginsucceed.html',
                                       username=username, usertype=current_user.type, next='/')

        else:
            return render_template('login.html', fail='登陆失败')

    elif request.method == 'GET':
        try:
            next = request.args['next']
        except:
            next = ''
        return render_template('login.html', next=next)


@app.route('/register', methods=['GET'])
def regget():
    SQL.cur.execute('''select top 1 Num
        from students
        order by Num desc''')
    numstu = str(int(SQL.cur.fetchall()[0]['Num'][3:]) + 1)
    SQL.cur.execute('''select top 1 num
        from teachers
        order by num desc
        ''')
    numtch = str(int(SQL.cur.fetchall()[0]['num'][3:]) + 1)
    return render_template('register.html', numstu=numstu, numtch=numtch)


@app.route('/register', methods=['POST'])
def regpost():
    username = request.form['username']
    password = request.form['password']
    usertype = request.form['type']
    name = request.form['name']
    sex = request.form['sex']
    age = int(request.form['age'])
    dept = request.form['dept']
    grade = 0
    classs = 0
    if usertype == 'student':
        grade = int(request.form['grade'])
        classs = int(request.form['class'])
    regf = user.register(usr=username, psw=password, typ=usertype, name=name, sex=sex, age=age, dept=dept, grade=grade,
                         classs=classs)
    if regf == 1:
        return render_template('regsucceed.html', username=username, usertype=usertype)
    elif regf == 0:
        return render_template('return.html', message='注册失败')
    elif regf == 2:
        return render_template('return.html', message='用户已存在')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return render_template('logoutsucceed.html')


@app.route('/status', methods=['GET'])
@login_required
def status():
    table = []

    if user.gettype(current_user.id) == 'student':
        table = SQL.select('''select * 
        from students 
        where account = '%s'
        ''' % current_user.id)
    elif user.gettype(current_user.id) == 'teacher':
        table = SQL.select('''select * 
                from teachers 
                where account = '%s'
                ''' % current_user.id)
    return render_template('status.html', StatusTable=table, typ=user.gettype(current_user.id))


@app.route('/statusSelect', methods=['GET'])
@login_required
def statusSelectG():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生无权查询他人信息')
    else:
        return render_template('statusSelect.html')


@app.route('/statusSelect', methods=['POST'])
@login_required
def statusSelectP():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生无权查询他人信息')
    else:
        if request.form['via'] == 'num':
            num = 'stu' + request.form['num']
            if user.isExistStu(num):
                StatusTable = SQL.select('select * from students where Num = \'%s\'' % num)
                STable = SQL.select('select * from score where Snum = \'%s\'' % num)
                Sum = 0.0
                for item in STable:
                    Sum += item['score']
                if len(STable) == 0:
                    avg = 0
                else:
                    avg = Sum / len(STable)
                ScoreTable = [STable]
                avgs = {num: avg}
                return render_template('statusscore.html', currtype='teacher', StatusTable=StatusTable,
                                       ScoreTable=ScoreTable, avgs=avgs)
            else:
                return render_template('statusSelect.html', fail='找不到学生')
        elif request.form['via'] == 'nam':
            try:
                nam = request.form['nam']
                StatusTable = SQL.select('select * from students where Name = \'%s\'' % nam)
                ScoreTable = []
                avgs = {}
                for i in StatusTable:
                    STable = SQL.select(
                        'select * from score where Snum = \'%s\'' % i['Num'])
                    ScoreTable.append(STable)
                    Sum = 0.0
                    for item in STable:
                        Sum += item['score']
                        if len(ScoreTable) == 0:
                            avg = 0
                        else:
                            avg = Sum / len(STable)
                        avgs[i['Num']] = avg
                return render_template('statusscore.html', currtype='teacher', StatusTable=StatusTable,
                                       ScoreTable=ScoreTable, avgs=avgs)
            except:
                return render_template('statusSelect.html', fail='找不到学生')
        elif request.form['via'] == 'cla':
            try:
                gra = int(request.form['gra'])
                dep = request.form['dep']
                cla = int(request.form['cla'])
                StatusTable = SQL.select(
                    'select * from students where Grade = \'%d\' and Class = \'%d\' and Dept = \'%s\'' % (
                        gra, cla, dep))
                ScoreTable = []
                avgs = {}
                for i in StatusTable:
                    STable = SQL.select(
                        'select * from score where Snum = \'%s\'' % i['Num'])
                    ScoreTable.append(STable)
                    Sum = 0.0
                    for item in STable:
                        Sum += item['score']
                        if len(ScoreTable) == 0:
                            avg = 0
                        else:
                            avg = Sum / len(STable)
                        avgs[i['Num']] = avg
                return render_template('statusscore.html', currtype='teacher', StatusTable=StatusTable,
                                       ScoreTable=ScoreTable, avgs=avgs)
            except:
                return render_template('statusSelect.html', fail='找不到学生')


@app.route('/alterself', methods=['GET', 'POST'])
@login_required
def alterself():
    if request.method == 'GET':
        return render_template('alterone.html', currtype='student', username=current_user.id,
                               type=user.gettype(current_user.id),
                               num=user.getnum(current_user.id),
                               name=user.getname(current_user.id),
                               sex=user.getsex(current_user.id), grade=user.getgrade(current_user.id),
                               classs=user.getclass(current_user.id), age=user.getage(current_user.id),
                               dept=user.getdept(current_user.id))
    elif request.method == 'POST':
        usr = request.form['username']
        pswnew = request.form['pswnew']
        name = request.form['name']
        sex = request.form['sex']
        age = int(request.form['age'])
        dept = request.form['dept']
        try:
            grade = int(request.form['grade'])
            classs = int(request.form['class'])
        except:
            grade = 0
            classs = 0
        if usr != '':
            user.setStatus(pswnew=pswnew, name=name, sex=sex, age=age, dept=dept, grade=grade, classs=classs, user=usr)
        else:
            user.setStatus(pswnew=pswnew, name=name, sex=sex, age=age, dept=dept, grade=grade, classs=classs,
                           user=current_user.id)
        return render_template('return.html', message='修改成功')


@app.route('/alter', methods=['GET'])
@login_required
def alternum():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='教师才能修改其他学生的信息')
    return render_template('alter.html')


@app.route('/alter', methods=['POST'])
@login_required
def alter():
    usr = ''
    num = request.form['num']
    currtype = current_user.type
    if num[:3] == 'stu' and user.isExistStu(num):
        usr = SQL.select('select account from students where Num=\'%s\'' % num)[0]['account']
    elif num[:3] == 'tch' and user.isExistTch(num):
        usr = SQL.select('select account from teachers where num=\'%s\'' % num)[0]['account']
    if not user.isExist(usr):
        return render_template('alter.html', fail='找不到用户')
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='教师才能修改其他学生的信息')
    elif user.gettype(usr) == 'teacher' and current_user.id != usr:
        return render_template('return.html', message='教师不能修改其他教师的信息')
    else:
        return render_template('alterone.html', username=usr, type=user.gettype(usr), num=user.getnum(usr),
                               name=user.getname(usr),
                               sex=user.getsex(usr), grade=user.getgrade(usr), classs=user.getclass(usr),
                               age=user.getage(usr),
                               dept=user.getdept(usr), currtype=currtype)


@app.route('/deletenum', methods=['GET'])
@login_required
def deletenum():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能清除成绩！')
    else:
        return render_template('deletenum.html')


@app.route('/deletenum', methods=['POST'])
@login_required
def deletenump():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能清除成绩！')
    else:
        num = 'stu' + request.form['num']
        if user.isExistStu(num):
            usr = SQL.select('select account from students where Num=\'%s\'' % num)[0]['account']
            scores = SQL.select('select * from score where Snum=\'%s\'' % num)

            return render_template('delete.html', num=num, username=usr,
                                   name=user.getname(usr),
                                   sex=user.getsex(usr), grade=user.getgrade(usr), classs=user.getclass(usr),
                                   age=user.getage(usr),
                                   dept=user.getdept(usr), scores=scores)
        else:
            return render_template('deletenum.html', fail='找不到用户')


@app.route('/delete', methods=['POST'])
@login_required
def delete():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能清除成绩！')
    else:
        num = request.form['num']
        user.delstu(num)
        return render_template('return.html', message='删除成功')


@app.route('/add', methods=['GET'])
@login_required
def addg():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能录入成绩！')
    else:
        Tnum = user.getnum(current_user.id)
        numt = SQL.select(
            '''select Snum
            from cs
            where Cnum in(
                    select Cnum
                    from ct
                    where Tnum='%s'
                )''' % Tnum)
        myct = SQL.select('''select * from ct where Tnum='%s'
            ''' % Tnum)
        for i in myct:
            i['Cname'] = SQL.selectone('select name from courses where num=\'%s\'' % i['Cnum'])['name']
        ct = SQL.select(
            '''select *
            from courses
            where num in(
                select Cnum
                from cs
                where Snum in(
                    select Snum
                    from cs
                    where Cnum in(
                        select Cnum
                        from ct
                        where Tnum='%s'
                    )
                )
            )''' % Tnum
        )
        for t in ct:
            t['Lnum'] = SQL.select('select Lnum from ct where Cnum=\'%s\'' % t['num'])
        return render_template('add.html', Tnum=user.getnum(current_user.id), myct=myct, ct=ct, numt=numt)


@app.route('/add', methods=['POST'])
@login_required
def addp():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能录入成绩！')
    else:
        Tnum = user.getnum(current_user.id)
        Snum = request.form['Snum']
        ct = SQL.select(
            '''select *
            from courses
            where num in(
                select Cnum
                from cs
                where Snum in(
                    select Snum
                    from cs
                    where Cnum in(
                        select Cnum
                        from ct
                        where Tnum='%s'
                    )
                )
            )''' % Tnum
        )
        for t in ct:
            t['Lnum'] = SQL.select('select Lnum from ct where Cnum=\'%s\'' % t['num'])
            myct = SQL.select('''select * from ct where Tnum='%s'
                        ''' % Tnum)
            for i in myct:
                i['Cname'] = SQL.selectone('select name from courses where num=\'%s\'' % i['Cnum'])['name']
        numt = SQL.select(
            '''select Snum
            from cs
            where Cnum in(
                    select Cnum
                    from ct
                    where Tnum='%s'
                )''' % Tnum)
        if user.isExistStu(Snum):
            Cnum = request.form['Cnum']
            Lnum = int(request.form['Lnum'])
            Cname = SQL.selectone('select name from courses where num=\'%s\'' % Cnum)['name']
            Score = int(request.form['score'])
            grade = SQL.selectone('select grade from cs where Cnum=\'%s\'' % Cnum)['grade']
            user.scorein(Snum, Cname, Score, grade, Cnum, Lnum)
            return render_template('add.html', Tnum=Tnum, ct=ct, myct=myct, numt=numt, message='录入成功！')
        else:
            return render_template('add.html', Tnum=Tnum, ct=ct, myct=myct, numt=numt, message='学生不存在！')


@app.route('/score', methods=['GET'])
@login_required
def score():
    st = SQL.select('''select *
    from score
    where Snum in(
        select Num
        from students
        where account='%s'
    )
    ''' % current_user.id)
    Sum = 0.0
    for item in st:
        Sum += item['score']
    if len(st) == 0:
        avg = 0
    else:
        avg = Sum / len(st)
    return render_template('score.html', ScoreTable=st, avg=avg)


@app.route('/test', methods=['GET'])
@login_required
def selectget():
    if current_user.id == 'miaoxiao':
        return 'accounts:' + DataFrame(SQL.select('select * from accounts')).to_html() + \
               'students:' + DataFrame(SQL.select('select * from students')).to_html() + \
               'teachers:' + DataFrame(SQL.select('select * from teachers')).to_html() + \
               'score:' + DataFrame(SQL.select('select * from score')).to_html()
    else:
        return redirect('/')


@app.route('/deleteone', methods=['POST'])
@login_required
def deleteone():
    num = request.form['num']
    Cnum = request.form['Cnum']
    usr = SQL.select('select account from students where Num=\'%s\'' % num)[0]['account']
    if user.delcourse(num, Cnum):
        scores = SQL.select('select * from score where Snum=\'%s\'' % num)
        return render_template('delete.html', num=num, username=usr,
                               name=user.getname(usr),
                               sex=user.getsex(usr), grade=user.getgrade(usr), classs=user.getclass(usr),
                               age=user.getage(usr),
                               dept=user.getdept(usr), scores=scores, succeed='删除成功！')
    else:
        scores = SQL.select('select * from score where Snum=\'%s\'' % num)
        return render_template('delete.html', num=num, username=usr,
                               name=user.getname(usr),
                               sex=user.getsex(usr), grade=user.getgrade(usr), classs=user.getclass(usr),
                               age=user.getage(usr),
                               dept=user.getdept(usr), scores=scores, succeed='删除失败！')


@app.route('/leave', methods=['GET'])
@login_required
def leave():
    tchs = SQL.select('select num from teachers')
    lst = SQL.select('select * from leave where Snum=\'%s\'' % user.getnum(current_user.id))
    for item in lst:
        if item['status'] == '未批准':
            return render_template('return.html', message='当前有未批准请假！')
        if item['status'] == '未销假':
            return render_template('return.html', message='当前有未销假请假！')
    return render_template('leave.html', tchs=tchs)


@app.route('/leave', methods=['POST'])
@login_required
def leavep():
    reason = request.form['reason']
    Tnum = request.form['Tnum']
    timestart = request.form['timestart']
    timestop = request.form['timestop']
    if user.isExistTch(Tnum):
        start = datetime.strptime(timestart, '%Y-%m-%dT%H:%M')
        stop = datetime.strptime(timestop, '%Y-%m-%dT%H:%M')
        if stop - start > timedelta(0):
            SQL.cur.execute('''insert into leave (Snum, Tnum, reason, timestart, timestop, status)
                values ('%s', '%s', '%s', '%s', '%s', '未批准')
                ''' % (user.getnum(current_user.id), Tnum, reason, timestart, timestop))
            SQL.conn.commit()
            return render_template('return.html', message='提交成功！')
        else:
            tchs = SQL.select('select num from teachers')
            return render_template('leave.html', tchs=tchs, message='停止时间不能比开始时间早')
    else:
        tchs = SQL.select('select num from teachers')
        return render_template('leave.html', tchs=tchs, message='无此教师')


@app.route('/currleave', methods=['GET'])
@login_required
def currleave():
    Sname = user.getname(current_user.id)
    Snum = user.getnum(current_user.id)
    LeaveTable = SQL.select('select * from leave where Snum = \'%s\'' % Snum)
    for table in LeaveTable:
        Tname = user.getname(user.getaccount(table['Tnum']))
        table['Tname'] = Tname
    return render_template('currleave.html', LeaveTable=LeaveTable, Sname=Sname)


@app.route('/leavemanage', methods=['GET'])
@login_required
def leavemanage():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能管理请假')
    Tnum = user.getnum(current_user.id)
    LeaveTable = SQL.select('select * from leave where Tnum = \'%s\'' % Tnum)
    if len(LeaveTable) > 0:
        for table in LeaveTable:
            Sname = user.getname(user.getaccount(table['Snum']))
            table['Sname'] = Sname
    return render_template('leavemanage.html', LeaveTable=LeaveTable)


@app.route('/leavemanage', methods=['POST'])
@login_required
def leavemanagep():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能管理请假')
    Snum = request.form['Snum']
    Tnum = user.getnum(current_user.id)
    try:
        act = request.form['act']
    except:
        pass
    status = request.form['status']
    if status == '未批准':
        if act == '准假':
            SQL.cur.execute(
                'update leave set status=\'未销假\' where status=\'未批准\' and Tnum=\'%s\' and Snum=\'%s\'' % (Tnum, Snum))
            SQL.conn.commit()
        elif act == '驳回':
            SQL.cur.execute(
                'update leave set status=\'已驳回\' where status=\'未批准\' and Tnum=\'%s\' and Snum=\'%s\'' % (Tnum, Snum))
            SQL.conn.commit()
    elif status == '未销假':
        SQL.cur.execute(
            'update leave set status=\'已销假\' where status=\'未销假\' and Tnum=\'%s\' and Snum=\'%s\'' % (Tnum, Snum))
        SQL.conn.commit()
    LeaveTable = SQL.select('select * from leave where Tnum = \'%s\'' % Tnum)
    for table in LeaveTable:
        Sname = user.getname(user.getaccount(table['Snum']))
        table['Sname'] = Sname
    return render_template('leavemanage.html', LeaveTable=LeaveTable, Sname=Sname)


@app.route('/course', methods=['GET'])
@login_required
def courseg():
    Snum = user.getnum(current_user.id)
    myct = SQL.select('select * from cs where Snum=\'%s\'' % Snum)
    for t in myct:
        Cname = SQL.selectone('select name from courses where num=\'%s\'' % t['Cnum'])['name']
        t['Cname'] = Cname
    ct = SQL.select('select * from ct')
    for t in ct:
        t['Tname'] = user.getname(user.getaccount(t['Tnum']))
        t['Cname'] = SQL.selectone('select name from courses where num=\'%s\'' % t['Cnum'])['name']

    return render_template('course.html', ct=ct, myct=myct)


@app.route('/course', methods=['POST'])
@login_required
def coursep():
    Snum = user.getnum(current_user.id)
    myct = SQL.select('select * from cs where Snum=\'%s\'' % Snum)
    Cnum = request.form['Cnum']
    Lnum = int(request.form['Lnum'])
    for t in myct:
        if Cnum == t['Cnum']:
            SQL.cur.execute('delete from cs where Cnum=\'%s\' and Lnum=\'%d\'' % (Cnum, Lnum))
            SQL.conn.commit()
            ct = SQL.select('select * from ct')
            for tct in ct:
                tct['Tname'] = user.getname(user.getaccount(tct['Tnum']))
                tct['Cname'] = SQL.selectone('select name from courses where num=\'%s\'' % tct['Cnum'])['name']
            myct = SQL.select('select * from cs where Snum=\'%s\'' % Snum)
            for myt in myct:
                Cname = SQL.selectone('select name from courses where num=\'%s\'' % myt['Cnum'])['name']
                myt['Cname'] = Cname
            return render_template('course.html', ct=ct, myct=myct)
    grade = int(user.getgrade(current_user.id))
    SQL.cur.execute('''insert into cs (Cnum, Snum, grade, Lnum)
    values ('%s', '%s', '%d', '%d')
    ''' % (Cnum, Snum, grade, Lnum))
    SQL.conn.commit()
    ct = SQL.select('select * from ct')
    for tct in ct:
        tct['Tname'] = user.getname(user.getaccount(tct['Tnum']))
        tct['Cname'] = SQL.selectone('select name from courses where num=\'%s\'' % tct['Cnum'])['name']
    myct = SQL.select('select * from cs where Snum=\'%s\'' % Snum)
    for myt in myct:
        Cname = SQL.selectone('select name from courses where num=\'%s\'' % myt['Cnum'])['name']
        myt['Cname'] = Cname
    return render_template('course.html', ct=ct, myct=myct)


@app.route('/courses', methods=['GET'])
@login_required
def courses():
    Snum = user.getnum(current_user.id)
    ct = SQL.select('select * from cs where Snum=\'%s\'' % Snum)
    for t in ct:
        Cname = SQL.selectone('select name from courses where num=\'%s\'' % t['Cnum'])['name']
        t['Cname'] = Cname
    return render_template('courses.html', ct=ct)


@app.route('/coursenew', methods=['GET'])
@login_required
def courseng():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能添加课程')
    Cnum = int(SQL.selectone('select top 1 num from courses order by num desc')['num'][4:]) + 1
    return render_template('coursenew.html', Cnum=Cnum)


@app.route('/coursenew', methods=['POST'])
@login_required
def coursenp():
    if current_user.type == 'teacher':
        name = request.form['name']
        num = 'cour' + str(SQL.selectone('select count(num) cnt from courses')['cnt'] + 1)
        SQL.cur.execute('insert into courses (name, num) values (\'%s\', \'%s\')'
                        % (name, num))
        SQL.conn.commit()
        Cnum = int(SQL.selectone('select top 1 num from courses order by num desc')['num'][4:]) + 1
        return render_template('coursenew.html', message='添加成功', Cnum=Cnum)
    else:
        return render_template('return.html', message='学生不能开课')


@app.route('/courseset', methods=['GET'])
@login_required
def courseset():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能开课')
    CTable = SQL.select('select * from courses')
    return render_template('courseset.html', CTable=CTable)


@app.route('/courseset', methods=['POST'])
@login_required
def coursesetp():
    if current_user.type == 'teacher':
        Cnum = request.form['Cnum']
        Lnum = int(request.form['Lnum'])
        Tnum = user.getnum(current_user.id)
        SQL.cur.execute('insert into ct (Cnum, Tnum, Lnum) values (\'%s\', \'%s\', \'%d\')'
                        % (Cnum, Tnum, Lnum))
        SQL.conn.commit()
        CTable = SQL.select('select * from courses')
        return render_template('courseset.html', message='开课成功', CTable=CTable)
    else:
        return render_template('return.html', message='学生不能开课')


@app.route('/mycourse', methods=['GET'])
@login_required
def mycourse():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能开课')
    Tnum = user.getnum(current_user.id)
    ct = SQL.select('select * from ct where Tnum=\'%s\'' % Tnum)
    for i in ct:
        i['Cname'] = SQL.selectone('select name from courses where num=\'%s\'' % i['Cnum'])['name']
    return render_template('mycourse.html', ct=ct)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
