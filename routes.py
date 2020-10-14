from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc
import re
import random
from get_connected import get_connected
app = Flask(__name__)
app.secret_key = 'super secret key'

@app.route('/')
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
            c.execute("SELECT * from LOGIN_INFO WHERE EMAIL_ID = ? OR USERNAME = ?  AND PASSWORD = ?",(username, username, password))
            lginfo = c.fetchone()
            if lginfo:
                session['loggedin'] = True
                session['id'] = lginfo[0]
                session['username'] = lginfo[1]
                session['email'] = lginfo[2]
                session['authority'] = lginfo[4]
                return 'Logged in successfully!'
            else:
                msg = 'Incorrect email/password!'
    return render_template('login.html', msg=msg)
@app.route('/logout/')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('authority', None)
    return redirect(url_for('login'))
@app.route('/register/', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form and 'password' in request.form and 'password_repeat' in request.form:
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        password_rp = request.form['password_repeat']
        con=get_connected()
        with con:
            c = con.cursor()
            c.execute("SELECT * from LOGIN_INFO WHERE EMAIL_ID = ? AND PASSWORD = ?",(email, password))
            lginfo = c.fetchone()
            if lginfo:
                return 'Account already exists!'
            #elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            #    msg = 'Invalid email address!'
            elif not firstname or not lastname or not email or not password or not password_rp:
                return 'Please fill out the form!'  
            else:
                uid = ''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
                c.execute("INSERT INTO LOGIN_INFO (EMPLOYEE_ID, EMAIL_ID, PASSWORD) VALUES (?, ?, ?)",(int(uid), email, password))
                return 'successfully registered!'

    return render_template('register.html', code=msg)
