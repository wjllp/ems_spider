#coding:utf-8
from crawler import *
from dao import mydao
from flask import Flask, request, render_template
import datetime
from sendmail import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(username+'\n'+password+'\n'+email)
    if(mydao.is_registed(int(username)) != False):
        return '<script>alert("该用户已注册，请不要重复注册!");window.location.href="/"</script>'
    else:
        result = get_class(username,password,email)
        if (result == 1):
            title = '注册成功'
            text = '恭喜你已成功注册课表/成绩推送小助手\n\n开学时课表推送功能会自动开启，每天向你推送明天要上的课以及天气\n\n成绩推送功能会在考试周每当你有新成绩出来时向你推送成绩\n\n若要停用某功能，仅需在邮件中回复"退订课表"或者"退订成绩"即可'
            mail_result = sendmail(email,text,title,username)
            if (mail_result == 1):
                f = open('registed.txt','a+')
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'：'+username+'注册成功！\n')
                f.close()
                print (username + "注册成功！")
                return '<script>alert("注册成功，已发送一封邮件到你的邮箱，若未收到请检查邮箱是否填写错误");window.location.href="/"</script>'
            else:
                f = open('registed.txt','a+')
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'：'+username+'注册邮件发送失败！\n')
                f.close()
                print (username + "邮箱填写错误！")
                result  = '<script>alert("注册失败，请检查邮箱是否填写错误！\n"'+email+');window.location.href="/"</script>'
                return result
        else:
            f = open('registed.txt','a+')
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'：'+username+'注册失败！\n')
            f.close()
            print (username + result)
            result ='<script>alert("' + result + '");window.location.href="/"</script>'
            return result
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000,debug = True)
    
