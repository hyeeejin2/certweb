from flask import Flask, app, request, render_template, url_for, redirect, session, escape
import pymysql, json

app=Flask(__name__)
app.config['DEBUG']=True

@app.route("/")
def index():
    return "test"

@app.route("/write")
def write():
    return render_template('write.html', user="admin")

@app.route("/writeProcess", methods=['POST'])
def writeProcess():
    title=request.form['title']
    content=request.form['content']
    writer=request.form['writer']
    date=request.form['date']

    db = pymysql.connect(host='127.0.0.1', port=3306, user='saferoad_manager', password='backend1234', db='SAFEROAD_MANAGER', charset='utf8')
    cursor=db.cursor()

    query="SELECT COUNT(*) FROM POST WHERE N_NUM=1;"

    cursor.execute(query)
    post_num=cursor.fetchall()

    for row in post_num:
        post_num=row[0]

    query="INSERT INTO POST VALUES(%s, %s, %s, %s, %s, %s, %s);"
    value=(int(post_num)+1, 1, title, content, 1, date, 0)

    cursor.execute(query, value)
    data=cursor.fetchall()

    if not data:
        db.commit()
        cursor.close()
        db.close()
        return "success!"
    else:
        db.rollback()
        cursor.close()
        db.close()
        return "failed!"

    

