import dao.mydao
from sendmail import *
import time
import datetime
from crawler import *

def sendclass():
    users = []         #从数据库中查出来的用户保存在此字典中
    courses = []         #同上
    text = ''            #邮件内容
    head = '<table border="0" cellpadding="1" cellspacing="1" style="font-size:15px;color:#000000;line-height:30px;">'
    tail = '</table>'
    users = dao.mydao.select_class_student()
    term = dao.mydao.select_current_term()[0]
    weather = get_weather()
    words = get_words()
    english = words.split('\n')[0]
    chinese = words.split('\n')[1]
    author = words.split('\n')[2]
    for user in users:
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(user['stu_id'],user['email'],user['sname'])
        courses = dao.mydao.select_course(user['stu_id'],term)
        count = len(courses)                #课程总数
        allclass = ''        #明天的课程名称
        title = ''              #邮件标题
        add = ''              #明天有实验课的提示
        sorry = '<tr><td></br><p>（邀请朋友注册请<a href="https://ke.qmxwj.com/">点击这里</a>，退订请<a href="https://stop.qmxwj.com/">点击这里</a>）</p></td></tr>'
        haveclass = 1
        for course in courses:
            if ('实验' in  course['cname']):
                add = '<tr><td>（明天有实验课，记得提前准备好实验用品）</td></tr>'
            if ('第九～十节' in course['ctime'] and '第十一～十二节' in courses[count - 1]['ctime']):
                allclass = allclass + '<tr><td style="color:#FF0000">' + course['cname'] + ' 第九～十一节' + '</td></tr>'  #将9-12节课整合为一节课
                count = count - 1
                break
            else:
                allclass = allclass + '<tr><td style="color:#FF0000">' + course['cname'] + ' ' + course['ctime'] + '</td></tr>'
        if (count == 0):
            title = '明日天气：'+weather.split('：')[1].split('，')[0].split('<')[0]+'，无课'
            text = '明天没课，不如相约图书馆'
            haveclass = 0
        else:
            title = '明日天气：'+weather.split('：')[1].split('，')[0].split('<')[0]+'，有'+str(count)+'节课'
            text = '<tr><td>明天总共有' + str(count) + '门课，分别是：</td></tr>' + allclass + add
        if dao.mydao.is_the_last_class(user['stu_id'],term) == 1:
            title = '本学期已结课'
            text = text + '<tr><td>截止到目前，你这学期的所有课程都已结束，本课表功能对你将停止推送，下学期将自动打开，祝你逢考必过！</td></tr>'
            dao.mydao.shutdown_class(user['stu_id'])
        shanbei = '<tr><td style="height: 10px;"></td></tr><tr><td>'+english+'</td></tr><tr><td>'+chinese+'</td></tr><tr><td style="height: 10px;"></td></tr>'
        text = text + shanbei + weather + sorry
        text = head+text+tail
        sname = user['sname']
        if sname == '朱海晴':
            sname = '晴姐'
        if haveclass == 1:
            result = sendmail(user['email'],text,title,sname)
            if result:
                print("邮件发送成功")
            else:
                print("邮件发送失败")
        else:
            print(sname+"无课")

if __name__ == '__main__':
    sendclass()
