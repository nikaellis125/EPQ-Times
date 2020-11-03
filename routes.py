from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import pyodbc, re, random
from get_connected import get_connected
from notifications import *
app = Flask(__name__)
app.secret_key = 'super secret key'
flname = fname = lname = emailid = uname = empid = emposition = country = city = startdate =''
@app.route('/')
@app.route('/homepage')
def homepage():
    return render_template('homepage.html')    

@app.route('/login/', methods=['GET', 'POST'])
def login():
    msg =''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        con=get_connected()
        with con:
            c = con.cursor()
            c.execute("SELECT * from LOGIN_INFO WHERE EMAIL_ID = ? AND PASSWORD = ?",(username, password))
            lginfo = c.fetchone()
            if lginfo:
                session['loggedin'] = True
                session['id'] = lginfo[0]
                c.execute("SELECT EMPLOYEE_ID, LASTNAME, FIRSTNAME, EMP_POSITION, CONVERT(varchar, EMP_START_DATE, 101), CITY, STATE, COUNTRY, EMAIL_ID, CONTACT_NO from EMPLOYEES WHERE EMPLOYEE_ID = ?",(lginfo[0]))
                empinfo = c.fetchone()
                global flname, fname, lname, emailid, uname, empid, emposition, country, city, startdate
                empid = lginfo[0]
                emailid = lginfo[2]
                uname = lginfo[1]
                fname = empinfo[2]
                lname = empinfo[1]
                country = empinfo[7]
                city = empinfo[5]
                emposition = empinfo[3]
                startdate = empinfo[4]
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
    if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form and 'authority' in request.form and 'startdate' in request.form and 'ContactNo' in request.form and 'Position' in request.form:
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        remail = request.form['email']
        authority = request.form['authority']
        Position = request.form['Position']
        strtdate = request.form['startdate']
        contactno = request.form['ContactNo']
        con=get_connected()
        with con:
            c = con.cursor()
            c.execute("SELECT * from LOGIN_INFO WHERE EMAIL_ID = ?",(remail))
            lginfo = c.fetchone()
            con.commit()
            if lginfo:
                flash('Account already exists!')
            elif not firstname or not lastname:
                flash('Please fill out the form!')  
            else:
                uid = ''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
                rusername = firstname[ 0 : 1 ] + lastname + ''.join([str(random.randint(0, 99)).zfill(3) for _ in range(1)])
                rpass = firstname[ 0 : 1 ] + lastname[ 0:1 ] +'_' +''.join([str(random.randint(0, 99)).zfill(4) for _ in range(1)])
                c.execute("INSERT INTO LOGIN_INFO (EMPLOYEE_ID, USERNAME, EMAIL_ID, AUTHORITY, PASSWORD) VALUES (?, ?, ?, ?, ?)",(int(uid), rusername, remail, authority, rpass))
                c.execute("INSERT INTO EMPLOYEES (EMPLOYEE_ID, LASTNAME, FIRSTNAME, EMP_POSITION, EMP_START_DATE, EMAIL_ID, CONTACT_NO) VALUES (?, ?, ?, ?, ?, ?, ?)",(int(uid), lastname, firstname, Position, strtdate, remail, contactno))
                con.commit()
                flash("Employee Inserted Successfully")
                sub = 'EPQ Time Clock Registration'
                content = 'Hi ' + firstname+ '!  You are registered for EPQ Time Clock online account.  You can login to the system using your email id ' + remail + ' and Password '+rpass+' .'
                send_mail(remail,sub,content)
                return redirect(url_for('editemp'))
    return redirect(url_for('editemp'))



@app.route('/index')
def index():
    return render_template('index.html', flname=flname)

@app.route('/table')
def table():
    return render_template('table.html', flname=flname)

@app.route('/ManagerDashboard')
def ManagerDashboard():
    
    return render_template('ManagerDashboard.html', flname = flname)

@app.route('/vacreq/')
def vacreq():
    con=get_connected()
    with con:
        c = con.cursor()
        c.execute("SELECT EMPLOYEE_ID, LASTNAME, FIRSTNAME, EMP_POSITION, CONVERT(varchar, START_DATE, 101), CONVERT(varchar, END_DATE, 101), TOTAL_DAYS, DECISION from VACATION_REQ WHERE DECISION = 'Pending'")
        Vacreqinfo = c.fetchall()
    return render_template('VacReq.html', flname=flname, table=Vacreqinfo)

@app.route('/vacdenied/<id>/', methods = ['GET', 'POST'])
def vacdenied(id):
    con=get_connected()
    with con:
        c = con.cursor()
        c.execute("UPDATE VACATION_REQ SET DECISION = 'Denied' WHERE EMPLOYEE_ID = ?", (id))
        con.commit()
        flash("Application denied!")
    return redirect(url_for('vacreq'))

@app.route('/vacapproved/<id>/', methods = ['GET', 'POST'])
def vacapproved(id):
    con=get_connected()
    with con:
        c = con.cursor()
        c.execute("UPDATE VACATION_REQ SET DECISION = 'Approved' WHERE EMPLOYEE_ID = ?", (id))
        con.commit()
        flash("Application Approved!")
    return redirect(url_for('vacreq'))


@app.route('/evacreq/', methods=['GET', 'POST'])
def evacreq():
    msg = ''
    con=get_connected()
    with con:
        c = con.cursor()
        c.execute("SELECT EMPLOYEE_ID, LASTNAME, FIRSTNAME, EMP_POSITION, CONVERT(varchar, START_DATE, 101), CONVERT(varchar, END_DATE, 101), TOTAL_DAYS, DECISION from VACATION_REQ WHERE EMPLOYEE_ID = ?",(empid))
        evacreqinfo = c.fetchall()
    if request.method == 'POST' and 'start_date' in request.form and 'end_date' in request.form:
        stdate = request.form['start_date']
        eddate = request.form['end_date']

        if not stdate or not eddate:
            msg = 'Please fill out the form!'
        else: 
            stdate = datetime.strptime(request.form['start_date'], "%Y-%m-%d")
            eddate = datetime.strptime(request.form['end_date'], "%Y-%m-%d")
            totdays = abs((eddate - stdate).days)
            con=get_connected()
            with con:
                c = con.cursor()
                c.execute("INSERT INTO VACATION_REQ (EMPLOYEE_ID, LASTNAME, FIRSTNAME, EMP_POSITION, START_DATE, END_DATE, TOTAL_DAYS, DECISION) VALUES (?,?,?,?,?,?,?,'Pending')" ,(empid, lname, fname, emposition, stdate, eddate, totdays))
                con.commit()
                c.execute("SELECT * from VACATION_REQ WHERE EMPLOYEE_ID = ?",(empid))
                evacreqinfo = c.fetchall()
                sub = 'Vacation Request'
                content = 'Hi' + flname + 'Vacation Request Application has been Submitted to the management'
            send_mail(emailid,sub,content)
    return render_template('EVacReq.html', flname=flname, evacreq=evacreqinfo, msg= msg)

@app.route('/WeeklyAttendance/')
def WeeklyAttendance():
    return render_template('WeeklyAttendance.html', flname=flname)

@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    con=get_connected()
    with con:
        c = con.cursor()
        c.execute("DELETE FROM EMPLOYEES WHERE EMPLOYEE_ID = ?", (id))
        c.execute("DELETE FROM LOGIN_INFO WHERE EMPLOYEE_ID = ?", (id))
        con.commit()
        flash("Employee deleted Successfully")
    return redirect(url_for('editemp'))
@app.route('/editemp/', methods=['GET', 'POST'])
def editemp():
    con=get_connected()
    with con:
        c = con.cursor()
        c.execute("SELECT EMPLOYEE_ID, LASTNAME, FIRSTNAME, EMP_POSITION, CONVERT(varchar, EMP_START_DATE, 101), CITY, STATE, COUNTRY, EMAIL_ID, CONTACT_NO from EMPLOYEES")
        empsinfo = c.fetchall()
        con.commit()
    if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form and 'authority' in request.form and 'startdate' in request.form and 'ContactNo' in request.form and 'Position' in request.form:
        empeditid = int(request.form.get('id'))
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        remail = request.form['email']
        authority = request.form['authority']
        Position = request.form['Position']
        strtdate = request.form['startdate']
        contactno = request.form['ContactNo']
        c.execute("UPDATE EMPLOYEES SET LASTNAME = ?, FIRSTNAME = ?, EMP_POSITION = ?, EMP_START_DATE = CONVERT(varchar, ?, 23), EMAIL_ID = ?, CONTACT_NO = ? WHERE EMPLOYEE_ID = ?", lastname, firstname, Position, strtdate, remail, contactno, empeditid)
        con.commit()
        flash("Employee Updated Successfully")
        return redirect(url_for('editemp'))
    return render_template('EditEmp.html', flname=flname, employees = empsinfo)

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/profile/')
def profile():
    return render_template('profile.html', flname=flname, first_name=fname, last_name=lname, emailid = emailid, user_name=uname, city=city, country=country)
