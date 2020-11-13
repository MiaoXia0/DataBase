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
        return render_template('index.html',
                               login=1,
                               username=current_user.id,
                               type=user.gettype(current_user.id))
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
    SQL.cur.execute('select count(Num) cnt from students')
    numstu = str(int(SQL.cur.fetchall()[0]['cnt']) + 1)
    SQL.cur.execute('select count(Num) cnt from teachers')
    numtch = str(int(SQL.cur.fetchall()[0]['cnt']) + 1)
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
        num = 'stu' + request.form['num']
        if user.isExistStu(num):
            StatusTable = SQL.select('select * from students where Num = \'%s\'' % num)
            ScoreTable = SQL.select('select * from score where Snum = \'%s\'' % num)
            Sum = 0.0
            for item in ScoreTable:
                Sum += item['score']
            avg = Sum / len(ScoreTable)
            return render_template('statusscore.html', StatusTable=StatusTable, ScoreTable=ScoreTable, avg=avg)
        else:
            return render_template('statusSelect.html', fail='找不到学生')


@app.route('/alterself', methods=['GET', 'POST'])
@login_required
def alterself():
    if request.method == 'GET':
        return render_template('alterone.html', username=current_user.id, type=user.gettype(current_user.id),
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
                               dept=user.getdept(usr))


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
def addp():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能录入成绩！')
    else:
        return render_template('add.html', Tnum=user.getnum(current_user.id))


@app.route('/add', methods=['POST'])
@login_required
def addg():
    if user.gettype(current_user.id) == 'student':
        return render_template('return.html', message='学生不能录入成绩！')
    else:
        Tnum = request.form['Tnum']
        Snum = 'stu' + request.form['Snum']
        if user.isExistStu(Snum):
            Cname = request.form['Cname']
            score = int(request.form['score'])
            grade = int(request.form['grade'])
            user.scorein(Snum, Tnum, Cname, score, grade)
            return render_template('add.html', Tnum=user.getnum(current_user.id), message='录入成功！')
        else:
            return render_template('add.html', Tnum=user.getnum(current_user.id), message='学生不存在！')


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
    Cname = request.form['Cname']
    usr = SQL.select('select account from students where Num=\'%s\'' % num)[0]['account']
    if user.delcourse(num, Cname):
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='80')
