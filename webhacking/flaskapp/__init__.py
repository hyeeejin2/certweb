from flask import Flask, app, request, render_template, redirect, url_for, session, escape, flash
import pymysql, json

app=Flask(__name__)
app.config["SECRET_KEY"] = "SECRET"

@app.route("/")
def main():
    if 'username' in session:
        user='%s' %escape(session['username'])
        return render_template("main.html", user=user)
    else:    
        return render_template("main.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/loginProcess", methods=['POST'])
def loginProcess():
    if request.method=="POST":
        userID = request.form['id']
        userPW = request.form['pw']

        db = pymysql.connect(host='127.0.0.1', port=3306, user='saferoad_manager', password='backend1234', db='WEB', charset='utf8')
        cursor = db.cursor()

        query = "SELECT USER_NUM FROM USER_INFO WHERE USER_ID= '%s' AND USER_PW='%s'" % (userID, userPW)

        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        db.close()

        if result:
            session['username']=request.form['id']
            return redirect(url_for('main'))
        
        else:
            flash("아이디 또는 비밀번호를 잘못 입력하였습니다.")
            return redirect(url_for('login'))

@app.route("/signupProcess", methods=['POST'])
def signupProcess():
    if request.method=="POST":
        userName=request.form['name']
        userID=request.form['id']
        userPW=request.form['pw']
        
        db = pymysql.connect(host='127.0.0.1', port=3306, user='saferoad_manager', password='backend1234', db='WEB', charset='utf8')
        cursor = db.cursor()

        query = 'SELECT count(*) FROM USER_INFO;'
        cursor.execute(query)
        num = cursor.fetchall()
        
        for row in num:
            num=row[0]

        query = 'INSERT INTO USER_INFO VALUES(%s ,%s, %s, %s);'
        value = (int(num)+1, userID, userPW, userName)

        cursor.execute(query, value)
        result=cursor.fetchall()

        cursor.close()

        if result:
            db.rollback()
            db.close()
            return redirect(url_for('signup'))

        else:
            db.commit()
            db.close()
            return redirect(url_for('login'))



