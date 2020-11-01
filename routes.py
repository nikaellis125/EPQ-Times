from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import pyodbc, re, random
from get_connected import get_connected
app = Flask(__name__)
app.secret_key = 'super secret key'
flname = fname = lname = emailid = uname = empid = emposition = ''


@app.route('/')
@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        con = get_connected()
        with con:
            c = con.cursor()
            c.execute(
                "SELECT * from LOGIN_INFO WHERE EMAIL_ID = ? AND PASSWORD = ?",
                (username, password))
            lginfo = c.fetchone()
            if lginfo:
                session['loggedin'] = True
                session['id'] = lginfo[0]
                c.execute("SELECT * from EMPLOYEES WHERE EMPLOYEE_ID = ?",
                          (lginfo[0]))
                empinfo = c.fetchone()
                global flname, fname, lname, emailid, uname, empid, emposition
                empid = lginfo[0]
                emailid = lginfo[2]
                uname = lginfo[1]
                fname = empinfo[2]
                lname = empinfo[1]
                emposition = empinfo[3]
                flname = empinfo[2] + " " + empinfo[1]
                if lginfo[4] == 'M':
                    return redirect(url_for('ManagerDashboard'))
                else:
                    return redirect(url_for('index'))
            else:
                msg = 'Incorrect email/password!'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    return redirect(url_for('homepage'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form and 'authority' in request.form:
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        remail = request.form['email']
        authority = request.form['authority']

        con = get_connected()
        with con:
            c = con.cursor()
            c.execute("SELECT * from LOGIN_INFO WHERE EMAIL_ID = ?", (remail))
            lginfo = c.fetchone()
            if lginfo:
                return 'Account already exists!'
            #elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            #    msg = 'Invalid email address!'
            elif not firstname or not lastname or not remail or not authority:
                return 'Please fill out the form!'
            else:
                uid = ''.join(
                    [str(random.randint(0, 999)).zfill(3) for _ in range(2)])
                rusername = firstname[0:1] + lastname + ''.join(
                    [str(random.randint(0, 99)).zfill(3) for _ in range(1)])
                c.execute(
                    "INSERT INTO LOGIN_INFO (EMPLOYEE_ID, USERNAME, EMAIL_ID, AUTHORITY) VALUES (?, ?, ?, ?)",
                    (int(uid), rusername, remail, authority))
                con.commit()
                return redirect(url_for('index'))

    return render_template('register.html', code=msg)


@app.route('/index')
def index():
    return render_template('index.html', flname=flname)


@app.route('/table')
def table():
    return render_template('table.html', flname=flname)


@app.route('/ManagerDashboard')
def ManagerDashboard():

    return render_template('ManagerDashboard.html', flname=flname)


@app.route('/vacreq/', methods=['GET', 'POST'])
def vacreq():
    con = get_connected()
    with con:
        c = con.cursor()
        c.execute("SELECT * from VACATION_REQ WHERE DECISION IS NULL")
        Vacreqinfo = c.fetchall()
    return render_template('VacReq.html', flname=flname, table=Vacreqinfo)


@app.route('/evacreq/', methods=['GET', 'POST'])
def evacreq():
    con = get_connected()
    with con:
        c = con.cursor()
        c.execute("SELECT * from VACATION_REQ WHERE EMPLOYEE_ID = ?", (empid))
        evacreqinfo = c.fetchall()
    if request.method == 'POST' and 'start_date' in request.form and 'end_date' in request.form:
        stdate = datetime.strptime(request.form['start_date'], "%Y-%m-%d")
        eddate = datetime.strptime(request.form['end_date'], "%Y-%m-%d")
        totdays = abs((eddate - stdate).days)
        con = get_connected()
        with con:
            c = con.cursor()
            c.execute(
                "INSERT INTO VACATION_REQ (EMPLOYEE_ID, LASTNAME, FIRSTNAME, EMP_POSITION, START_DATE, END_DATE, TOTAL_DAYS) VALUES (?,?,?,?,?,?,?)",
                (empid, lname, fname, emposition, stdate, eddate, totdays))
            con.commit()
            c.execute("SELECT * from VACATION_REQ WHERE EMPLOYEE_ID = ?",
                      (empid))
            evacreqinfo = c.fetchall()
    return render_template('EVacReq.html', flname=flname, evacreq=evacreqinfo)


@app.route('/WeeklyAttendance/')
def WeeklyAttendance():
    return render_template('WeeklyAttendance.html', flname=flname)


@app.route('/editemp')
def editemp():
    con = get_connected()
    with con:
        c = con.cursor()
        c.execute("SELECT * from EMPLOYEES")
        empsinfo = c.fetchall()
    return render_template('EditEmp.html', flname=flname, employees=empsinfo)


@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')


@app.route('/profile/')
def profile():
    return render_template('profile.html',
                           flname=flname,
                           first_name=fname,
                           last_name=lname,
                           emailid=emailid,
                           user_name=uname)
