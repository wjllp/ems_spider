#coding:utf-8
from crawler import *
from dao import mydao
from flask import Flask, request, render_template
import datetime
from sendmail import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index2.html')

@app.route('/', methods=['POST'])
def delete():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(username+'\n'+password+'\n'+email)
    user = mydao.is_registed(int(username))
    if (user == False):
        result = """<script>alert("该用户不存在！");window.location.href="/"</script>"""
        return result
    else:
        if (password == user[0]['password'] or email == user[0]['email']):
            mydao.shutdown_class(int(username))
            f = open('deleted.txt','a+')
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'：'+username+'已退订！\n')
            f.close()
            print(username+'已退订！')
            result = """<script>alert("退订成功！");window.location.href="/"</script>"""
            return result
        else:
            f = open('deleted.txt','a+')
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'：'+username+'尝试退订失败！\n')
            f.close()
            result = """<script>alert("密码或邮箱输入错误！");window.location.href="/"</script>"""
            return result
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 7486,debug = True)
    
