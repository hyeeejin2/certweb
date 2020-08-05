from flask import Flask, app, request, render_template, url_for, redirect, session, escape, flash
import pymysql, json

app=Flask(__name__)
app.config['DEBUG']=True
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'redsfsfsfsfis'

def permissionCheck(post_num, n_num, user_id):
    db = pymysql.connect(host='127.0.0.1', port=3306, user='saferoad_manager', password='backend1234', db='SAFEROAD_MANAGER', charset='utf8')
    cursor=db.cursor()

    query="SELECT POST_NUM FROM USER_INFO, POST WHERE USER_ID=%s AND USER_NUM=U_NUM AND POST_NUM=%s AND N_NUM=%s;"
    value=(user_id, post_num, n_num)

    cursor.execute(query, value)
    data=cursor.fetchall()

    for row in data:
        data=row[0]

    if data:
        cursor.close()
        db.close()
        return True
    else:
        query="SELECT NOTICE_NUM FROM USER_INFO, NOTICE_INFO WHERE USER_ID=%s AND USER_NUM=U_NUM AND NOTICE_NUM=%s;"
        value=(user_id, n_num)

        cursor.execute(query, value)
        data=cursor.fetchall()

        cursor.close()
        db.close()

        for row in data:
            data=row[0]
        
        if data:
            return True
        else:
            return False

@app.route("/complaint/main")
def complaint_main():
    return render_template('complaint.html')

@app.route("/listProcess")
def listProcess():
    if request.method=='GET':
        n_num=request.args.get('kind')
        db = pymysql.connect(host='127.0.0.1', port=3306, user='saferoad_manager', password='backend1234', db='SAFEROAD_MANAGER', charset='utf8')
        cursor=db.cursor()
    
        query="SELECT POST_NUM, POST_TITLE, USER_ID, POST_DATE, POST_VIEW FROM POST, USER_INFO WHERE N_NUM=%s AND U_NUM=USER_NUM;"
        value=(n_num)
    
        cursor.execute(query, value)
        data=cursor.fetchall()

        cursor.close()
        db.close()

        datalist=[]
        no=1
        for row in data:
            dic={'no':no, 'post_num':row[0], 'post_title':row[1], 'user_id':row[2], 'post_date':row[3], 'post_view':row[4]}
            datalist.append(dic)
            no+=1

        json_datalist={'data':datalist}
        r=json.dumps(json_datalist)
        loaded_r=json.loads(r)
        return loaded_r

@app.route("/complaint/post/<post_num>")
def get_pnum(post_num):
    if request.method=='GET':
        db = pymysql.connect(host='127.0.0.1', port=3306, user='saferoad_manager', password='backend1234', db='SAFEROAD_MANAGER', charset='utf8')
        cursor=db.cursor()

        query="SELECT POST_NUM FROM POST WHERE POST_NUM=%s AND N_NUM=1;"
        value=(int(post_num))

        cursor.execute(query, value)
        data=cursor.fetchall()

        for row in data:
            data=row[0]

        if data:
            query="SELECT POST_NUM, POST_TITLE, POST_CONTENT, USER_ID, POST_DATE FROM POST, USER_INFO WHERE POST_NUM=%s AND N_NUM=1 AND U_NUM=USER_NUM;"
            value=(post_num)

            cursor.execute(query, value)
            data=cursor.fetchall()
            
            cursor.close()
            db.close()

            if 'username' in session:
                user='%s' %escape(session['username'])
                access=permissionCheck(int(post_num), 1, user)
                if access:
                    return render_template('complaint_detail.html', data=data, user=user, access=access)
                else:
                    return render_template('complaint_detail.html', data=data, user=user)
            else:
                return render_template('complaint_detail.html', data=data)
        else:
            cursor.close()
            db.close()
            return redirect(url_for('complaint_main'))

@app.route("/complaint/write")
def complaint_write():
    if 'username' in session:
        user='%s' %escape(session['username'])
        return render_template('complaint_write.html', user=user)
    else:
        return redirect(url_for('index'))

@app.route("/writeProcess", methods=['POST'])
def writeProcess():
    if 'username' in session:
        if request.method=='POST':
            n_num=int(request.form['kind'])
            title=request.form['title']
            content=request.form['content']
            writer=request.form['writer']
            date=request.form['date']

            db = pymysql.connect(host='127.0.0.1', port=3306, user='saferoad_manager', password='backend1234', db='SAFEROAD_MANAGER', charset='utf8')
            cursor=db.cursor()

            query="SELECT POST_NUM FROM POST WHERE N_NUM=%s;"
            value=(n_num)

            cursor.execute(query, value)
            post_num=cursor.fetchall()

            for row in post_num:
                post_num=row[0]

            query="SELECT USER_NUM FROM USER_INFO WHERE USER_ID=%s;"
            value=(writer)

            cursor.execute(query, value)
            u_num=cursor.fetchall()

            for row in u_num:
                u_num=row[0]

            query="INSERT INTO POST VALUES(%s, %s, %s, %s, %s, %s, %s);"
            value=(int(post_num)+1, n_num, title, content, u_num, date, 0)
    
            cursor.execute(query, value)
            data=cursor.fetchall()

            if not data:
                db.commit()
                cursor.close()
                db.close()
                return redirect(url_for('complaint_main')) # referring
            else:
                db.rollback()
                cursor.close()
                db.close()
                return redirect(url_for('complaint_main')) #referring
    else:
        return redirect(url_for('index'))

@app.route('/modifyProcess', methods=['POST'])
def modifyProcess():
    return "test"

@app.route('/deleteProcess', methods=['POST'])
def deleteProcess():
    if 'username' in session:
        if request.method=='POST':
            post_num=int(request.form['post_num'])
            n_num=int(request.form['kind'])
            user='%s' %escape(session['username'])
            if permissionCheck(post_num, n_num, user):
                db = pymysql.connect(host='127.0.0.1', port=3306, user='saferoad_manager', password='backend1234', db='SAFEROAD_MANAGER', charset='utf8')
                cursor=db.cursor()

                query="DELETE FROM POST WHERE POST_NUM=%s AND N_NUM=%s;"
                value=(post_num, n_num)

                cursor.execute(query, value)
                data=cursor.fetchall()

                if not data:
                    db.commit()
                    cursor.close()
                    db.close()
                    #return
                else:
                    db.rollback()
                    cursor.close()
                    db.close()
                    #return
            else:
                return "test"
                #referring

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

