#coding:utf-8
import requests
import pytesseract
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import termcolor
import re
from http import cookiejar
import dao.mydao
from sendmail import *
import time
from calgpa import *

session = requests.session()
login_url = 'http://210.42.38.26:84/jwc_glxt/Login.aspx'         #登录地址
kb_url = 'http://210.42.38.26:84/jwc_glxt/Course_Choice/Course_Schedule.aspx'    #课表地址
logout_url = 'http://210.42.38.26:84/jwc_glxt/Login.aspx?xttc=1'     #退出账户
weather_url = 'http://www.weather.com.cn/weather/101200901.shtml'    #中国天气网
score_url = 'http://210.42.38.26:84/jwc_glxt/Student_Score/Score_Query.aspx'     #分数地址
code_url = 'http://210.42.38.26:84/jwc_glxt/ValidateCode.aspx'         #验证码地址
course_url = 'http://210.42.38.26:84/jwc_glxt/Course_Choice/Stu_Course_Query.aspx'       #已选课程
year = ''
term = ''

session.cookies = cookiejar.LWPCookieJar("cookies")

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
}

term_info = dao.mydao.select_current_term()[0]    #获取当前学期
year = term_info['year']
term = term_info['term']

try:
    session.cookies.load(ignore_discard=True, ignore_expires=True)
except:
    pass

def do_login(username,password):
    prelogin = session.get(login_url)
    presoup = BeautifulSoup(prelogin.text, 'html.parser')
    VIEWSTATE = presoup.find('input',id='__VIEWSTATE')["value"]
    EVENTVALIDATION = presoup.find('input',id='__EVENTVALIDATION')["value"]
    image = Image.open(BytesIO(session.get(code_url).content))
    try:
        vcode = pytesseract.image_to_string(image).replace(' ','')
    except IOError:
        print("出错了...")
    data = {
        "__VIEWSTATE":VIEWSTATE,
        "__EVENTVALIDATION":EVENTVALIDATION,
        'txtUserName': username,
        'txtPassword': password,
        'CheckCode':vcode,
        'btnLogin.x':37,
        'btnLogin.y':4
    }
    print ("验证码为："+vcode)
    resp = session.post(login_url,data=data, headers=headers)
    return resp


def get_class(username,password,email):
    while(True):
        resp = do_login(username,password)
        soup = BeautifulSoup(resp.text, 'html.parser')
        if(soup.title.string.replace('\n','').strip() == '三峡大学教务管理系统'):  # 提取title的值并剔除其中的换行符和字符串
            print('登录成功！')
            kbresp = session.get(kb_url)          #跳转到已选课表页面
            kbsoup = BeautifulSoup(kbresp.text, 'html.parser')            
            course_count = get_course_count()    #获取课程总数
            session.get(logout_url)              #退出登录
            print ('退出成功！')
            sname = soup.body.find('span', {'id': 'ctl00_lblSignIn'}).string  #爬取姓名
            sname = re.sub(r'([\d]+)','',sname)
            print(sname+'，课程总数：',course_count)
            dao.mydao.insert_student(int(username),password,email,sname,course_count)
            table = kbsoup.body.find('table', {'id': 'ctl00_MainContentPlaceHolder_GridScore'})
            tr = table.find_all('tr')       #每个tr表示第几节课
            for i in range(1,len(tr)):
                td = tr[i].find_all('td')       #每个td表示星期几
                for j in range(1,len(td)):
                    myclass = td[j].get_text().split('\xa0')
                    if(myclass[0] != ''):
                        cname =  myclass[0]
                        k = 0
                        while(k < len(myclass) - 1):
                            flag = 0
                            cweek = j
                            ctime = td[0].get_text()
                            startweek = re.findall(r"\d+",myclass[k + 1])[0]   #通过正则表达式剔除汉字得到起始周
                            endweek = re.findall(r"\d+",myclass[k + 1])[1]
                            if(len(myclass) > 3 & k >= 1):
                                cname = myclass[k].split('等')[1]     #同一个时间段可能还会有其他的课 也要提取出来
                            if('单周' in myclass[k + 2]):         #判断单双周
                                flag = 1
                            elif('双周' in myclass[k + 2]):
                                flag = 2
#                            print(cname,startweek,endweek,ctime,flag)
                            k = k + 2
                            dao.mydao.insert_course(int(username), cname,int(startweek),int(endweek),ctime,cweek,flag)
            return 1
            break
        else:                      #登录失败
            error = soup.find_all('span')[0].get_text()             #提取错误信息
            if(error == '登录失败： 请检查用户名和密码是否输入正确'):
                print (error)
                return error
            elif(error == '登录失败： 该用户已经登录系统，不允许重复登录！'):
                print (error)
                return error
            elif(error == '登录失败： '+str(username)+'不合法'):        #这三种错误无法进入系统，所以退出循环
                print (error)
                return error
            else:
                print (error)          #验证码不对

def get_weather():
    wresp = session.get(weather_url)
    wresp.encoding = 'utf-8'
    wsoup = BeautifulSoup(wresp.text, 'html.parser')
    body = wsoup.body
    result = '<tr><td>明日天气：'
    data = body.find('div', {'id': '7d'})
    ul = data.find('ul')
    day = ul.find_all('li')

    date = day[1].find('h1').string
    text = day[1].find_all('p')
    result = result + text[0].string
    if text[1].find('span') is None:
        high = None
    else:
        high = text[1].find('span').string
        low = text[1].find('i').string
    result = result +  '，' + high + '~' + low + '</td></tr>'   #温度
    
    live = body.find('div', {'id': 'livezs'})          #获取生活指数
    liveul = live.find_all('ul')
    liveli = liveul[1].find_all('li')
    livezs = ''
    for i in range(1,len(liveli)):
        if i != 4:
            livezs = livezs + '<tr><td>' + liveli[i].find_all('p')[0].string + '</td></tr>'
    result = result + livezs
    return result

def get_scores(username,password,email,sname,total_scores_count,uncomment_scores):
    while(True):
        resp = do_login(username,password)
        soup = BeautifulSoup(resp.text, 'html.parser')
        if(soup.title.string.replace('\n','').strip() == '三峡大学教务管理系统'):  # 提取title的值并剔除其中的换行符和字符串
            print('登录成功！')
            score_resp = session.get(score_url)          #跳转到分数表页面
            score_soup = BeautifulSoup(score_resp.text, 'html.parser')
            session.get(logout_url)              #退出登录
            print ('退出成功！')
            sname = soup.body.find('span', {'id': 'ctl00_lblSignIn'}).string  #爬取姓名
            sname = re.sub(r'([\d]+)','',sname)
            print(sname)
            trList = score_soup.body.find(id="ctl00_MainContentPlaceHolder_GridScore").findAll('tr')
            flag = 0
            newscore_count = 0
            new_scores = ""
            for tr in trList[1:]:
                tdList = tr.findAll("td")
                score_year = tdList[0].get_text()
                score_term = tdList[1].get_text()
                coursename = tdList[2].get_text()
                credit = tdList[3].get_text()
                test_type  = tdList[4].get_text()
                grade = tdList[5].get_text()
                coursenum = tdList[7].get_text()
                if (int(score_year) == year and int(score_term) == term ):  #筛选出当前学期
                    if(dao.mydao.is_the_new_score(int(username),coursename,year,term)):  #判断最新成绩
                        dao.mydao.insert_score(int(username), year, term, coursename,float(credit),test_type,grade)
                        flag = 1
                        newscore_count = newscore_count + 1
                        new_scores = new_scores + coursename + " " + credit + " " + test_type + " " + grade + " " + str(calgpa(grade)) + "\n"
                    else:
                        for uncomment_score in uncomment_scores:
                            if (int(username) == uncomment_score['stu_id'] and coursename == uncomment_score['coursename']):
                                dao.mydao.update_score(int(username), coursename,year, term,grade)
            if (flag):   #如果有新成绩出来
                all_scores = ""
                scores = dao.mydao.select_score(int(username),year,term)  #查询数据库中所有成绩
                current_scores_count = len(scores)
                for score in scores:
                    all_scores = all_scores + score['coursename'] + " " + str(score['credit']) + " " + score['test_type'] + " " + score['grade'] + " " + str(score['gpa']) + "\n"
                text = "滴滴滴，亲爱的"+sname+"同学，你今天有"+str(newscore_count)+"门新成绩出来啦！\n课程名称  学分  考试类型  成绩  绩点\n" + new_scores + "\n"
                if (current_scores_count  == total_scores_count):  #所有成绩都出来了
                    text = text + "你总共有"+str(total_scores_count)+"门课，到目前为止所有成绩均已出来，分别是：\n课程名称  学分  考试类型  成绩  绩点\n" + all_scores
                    dao.mydao.shutdown_score(int(username))    #关闭成绩推送
                else:
                    text = text + "你总共有"+str(total_scores_count)+"门课，到目前为止已有" + str(current_scores_count) + "门成绩出来啦！分别是：\n" + all_scores
                title = "滴滴滴，出新成绩啦！"
                if (sname == "朱海晴"):
                    sname = "晴姐"
                result = sendmail(email,text,title,sname)      #发送邮件
                if result:
                    print("邮件发送成功")
                else:
                    print("邮件发送失败")
            break
        else:                      #登录失败
            error = soup.find_all('span')[0].get_text()             #提取错误信息
            if(error == '登录失败： 请检查用户名和密码是否输入正确'):
                return error
            elif(error == '登录失败： 该用户已经登录系统，不允许重复登录！'):
                return error
            elif(error == '登录失败： '+username+'不合法'):        #这三种错误无法进入系统，所以退出循环
                return error
            else:
                print (error)      #验证码不对  继续循环

def get_course_count():
    pre_getcourse = session.get(course_url)
    presoup = BeautifulSoup(pre_getcourse.text,'html.parser')

    VIEWSTATE = presoup.find('input',id='__VIEWSTATE')["value"]
    EVENTVALIDATION = presoup.find('input',id='__EVENTVALIDATION')["value"]

    course_data = {
                "__EVENTTARGET":"",
                "__EVENTARGUMENT":"",
                "__VIEWSTATE":VIEWSTATE,
                "__EVENTVALIDATION":EVENTVALIDATION,
                "ctl00$MainContentPlaceHolder$School_Year":year,
                "ctl00$MainContentPlaceHolder$School_Term":term,
                "ctl00$MainContentPlaceHolder$BtnSearch.x":17,
                'ctl00$MainContentPlaceHolder$BtnSearch.y':7
    }
    course_resp = session.post(course_url,data=course_data)          #跳转到分数表页面
    course_soup = BeautifulSoup(course_resp.text, 'html.parser')
    
    tr = course_soup.find('table', {'id': 'ctl00_MainContentPlaceHolder_GridCourse_Q'}).find_all('tr')
    count = len(tr) - 1       #课程总数
    return count

def get_words():
    shanbei_url = 'https://www.shanbay.com/soup/mobile/quote/' + time.strftime("%Y-%m-%d",time.localtime())    #扇贝每日一句
    words_resp = session.get(shanbei_url)
    words_soup = BeautifulSoup(words_resp.text, 'html.parser')
    english = words_soup.find('div',{'class':'content'}).string
    chinese = words_soup.find('div',{'class':'translation'}).string
    author = words_soup.find('div',{'class':'author'}).string
    return english + '\n' + chinese + '\n' + author
