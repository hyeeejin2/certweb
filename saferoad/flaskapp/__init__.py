from flask import Flask, app, request, render_template, url_for, redirect, session, escape, flash
import pymysql, json

app=Flask(__name__)
app.config['DEBUG']=True
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'redsfsfsfsfis'

@app.route("/write")
def write():
    if 'username' in session:
        return render_template('write.html', user="admin")
    else:
        return redirect(url_for('index'))

@app.route("/writeProcess", methods=['POST'])
def writeProcess():
    if 'username' in session:
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
    else:
        return redirect(url_for('index'))

@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/sessionCheck")
def sessionCheck():
    if 'username' in session:
        flash("로그인 성공!")
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
@app.route('/login/<error>')
def login():
    if 'username' in session:
        return redirect(url_for('sessionCheck'))
    else:
        return render_template("sign_in.html")

@app.route('/loginProcess', methods=['POST'])
@app.route('/loginProcess/<error>')
def loginProcess():
    if request.method=="POST":
        if request.form['id'] == '' or request.form['pw'] == '':
            flash("아이디 또는 비밀번호를 입력하세요.")
            return redirect(url_for('login'))
        else:
            #salt = "@bAr2adY%Sb#Q1&z"
            ID = request.form['id']
            pw = request.form['pw']
            #db_password = pw + salt
            #hash_pw = hashlib.sha256(db_password.encode()).hexdigest()

            db = pymysql.connect(host='127.0.0.1', port=3306, user='saferoad_manager', password='backend1234',
                                 db='SAFEROAD_MANAGER', charset='utf8')
            cursor = db.cursor()

            query = 'SELECT USER_ID, USER_PW FROM USER_INFO WHERE USER_ID= %s AND USER_PW=%s;'
            value = (ID, pw)

            cursor.execute(query, value)
            result = cursor.fetchall()

            cursor.close()
            db.close()

            if result:
                session['username']=request.form['id']
                return redirect(url_for('sessionCheck'))

            else:
                flash("아이디 또는 비밀번호를 잘못 입력하였습니다.")
                return redirect(url_for('login'))

@app.route("/logout")
def logout():
    if 'username' in session:
        session.clear()
    
        return redirect(url_for('index'))
    else:
        
        return redirect(url_for('index', error=load_j))


@app.route("/signup", methods=['POST','GET'])
@app.route('/signup/<error>')
def signup():
    return render_template('sign_up.html')


@app.route("/signupProcess", methods=['POST', 'GET'])
def signupProcess():
    if request.method=="POST":
        if request.form['id'] == '' or request.form['pw'] == '' or request.form['addr']=='':
            flash("빈칸을 채우세요.")
            
            return redirect(url_for('signup'))

        else:
            #salt="@bAr2adY%Sb#Q1&z"
            ID=request.form['id']
            pw=request.form['pw']
            check_pw=request.form['check_pw']
            addr=request.form['addr']

            #db_password = pw + salt
            #hash_pw = hashlib.sha256(db_password.encode()).hexdigest()

            if pw==check_pw and len(pw)>=10 and len(check_pw)>=10:
                db = pymysql.connect(host='127.0.0.1', port=3306, user='saferoad_manager', password='backend1234',
                                 db='SAFEROAD_MANAGER', charset='utf8')
                cursor = db.cursor()

                query = 'SELECT USER_ID FROM USER_INFO WHERE USER_ID= %s;'
                value = (ID)

                cursor.execute(query, value)
                result = cursor.fetchall()

                query = 'SELECT USER_ID FROM USER_INFO WHERE USER_ID= %s;'
                value = (ID)

                cursor.execute(query, value)
                exist = cursor.fetchall()
                
                if exist:
                    cursor.close()
                    db.close()
                    flash('이미 존재하는 아이디 입니다.')
                    return redirect(url_for('signup'))

                else:
                    query = 'SELECT count(*) FROM USER_INFO;'
                    cursor.execute(query)
                    num = cursor.fetchall()

                    for row in num:
                        num=row[0]

                    query = 'INSERT INTO USER_INFO VALUES(%s ,%s, %s);'
                    value = (num+1, ID, pw)
                    cursor.execute(query, value)
                    result=cursor.fetchall() 

                    addr = request.form['addr'].split(' ')
                    detail_addr=request.form['detail_addr']
                    address=[]
                    for i in addr:
                        address.append(i)

                    query = 'INSERT INTO ADDRESS VALUES(%s, %s, %s, %s, %s, %s, %s, %s);'
                    
                    value=(num+1,num+1,'집',address[0], address[1], address[2], detail_addr, 1)
                    cursor.execute(query, value)
                    addr_result=cursor.fetchall()

                    if not result:
                        db.commit()
                        db.close()
                        flash("회원가입 성공")
                        return redirect(url_for('login'))
                    else:
                        db.rollback()
                        cursor.close()
                        db.close()
                        return redirect(url_for('signup'))
    flash("비밀번호 확인해주세요.")
    return render_template('sign_up.html')    

