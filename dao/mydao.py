#coding:utf-8
import datetime
import pymysql.cursors
from calgpa import *
connection = pymysql.connect(host='127.0.0.1',
                             port=3360,
                             user='root',
                             password='root',
                             db='users',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()
def select_class_student():
    sql = "select * from student where class_status = '1'"
    cursor.execute(sql)
    return cursor.fetchall()

def select_score_student():
    sql = "select * from student where score_status = '1'"
    cursor.execute(sql)
    return cursor.fetchall()

def is_registed(username):
    sql = 'select * from student where stu_id = %d'
    data = (username)
    cursor.execute(sql%data)
    if(cursor.rowcount) == 0:         #若为0则表示没有注册
        return False
    else:
        return cursor.fetchall()

def insert_student(username,password,email,sname,course_count):
    sql = "insert into student(stu_id,password,email,sname,course_count,class_status,score_status) values ('%d','%s','%s','%s','%d','%d','%d')"
    data = (username,password,email,sname,course_count,1,0)
    cursor.execute(sql%data)
    connection.commit()
    print('添加用户成功！')

def select_course(username,term):
    weekday = (datetime.datetime.now().weekday() + 2 ) % 7               #得到今天的星期 0代表星期天  所以加1代表今天星期，再加1代表明天的星期 星期天的时候会算出明天是星期八  所以需要取7的模
    currentweek = int((datetime.datetime.now() - term['first_week_day']).days/7) + 1
    if weekday == 1:
        currentweek = currentweek + 1      #如果明天是周一  就把当前周加1
    flag = 2
    if (currentweek % 2 != 0):             #判断单双周
        flag = 1
    sql = 'select * from course where stu_id = %d and sweek <= %d and %d <= eweek and cweek = %d and (wweek = %d or wweek = %d)'
    data = (username,currentweek,currentweek,weekday,flag ,0)
    cursor.execute(sql%data)
    return cursor.fetchall()

def insert_course(username,cname,sweek,eweek,ctime,cweek,wweek):
    sql = "insert into course(stu_id,cname,sweek,eweek,ctime,cweek,wweek) values('%d','%s','%d','%d','%s','%d','%d')"
    data = (username,cname,sweek,eweek,ctime,cweek,wweek)
    cursor.execute(sql%data)
    connection.commit()
    print(cname,'起始周:' + str(sweek),'结束周:' + str(eweek),ctime,'每周' + str(cweek))

def is_the_last_class(username,term):
    weekday = (datetime.datetime.now().weekday() + 2 ) % 7        
    currentweek = int((datetime.datetime.now() - term['first_week_day']).days/7) + 1
    if weekday == 1:
        currentweek = currentweek + 1      #如果明天是周一  就把当前周加1

    sql1 = 'select count(*) from course where stu_id = %d and eweek > %d'
    sql2 = 'select count(*) from course where stu_id = %d and eweek = %d and cweek > %d'
    data = (username,currentweek)
    data2 = (username,currentweek,weekday - 1)
    cursor.execute(sql1%data)
    if cursor.fetchall()[0]['count(*)'] == 0:
        cursor.execute(sql2%data2)
        if cursor.fetchall()[0]['count(*)'] == 0:
            print('所有课程已经完毕，今天是周',weekday-1)
            return 1
        else:
            print('最后一周，下周无课，今天是周',weekday-1)
            return 0
    else:
        print('还有课 ，本周周数：',currentweek)
        return 0

def shutdown_class(username):
    sql = 'update student set class_status = 0 where stu_id = %d'
    data = (username)
    cursor.execute(sql%data)
    connection.commit()
    print(username,'关闭成绩推送')

def start_class(username):
    sql = 'update student set class_status = 1 where stu_id = %d'
    data = (username)
    cursor.execute(sql%data)
    connection.commit()
    print(username,'开启成绩推送')

def shutdown_score(username):
    sql = 'update student set score_status = 0 where stu_id = %d'
    data = (username)
    cursor.execute(sql%data)
    connection.commit()
    print(username,'关闭分数推送')

def start_score(username):
    sql = 'update student set score_status = 1 where stu_id = %d'
    data = (username)
    cursor.execute(sql%data)
    connection.commit()
    print(username,'开启分数推送')

def is_the_new_score(username,coursename,year,term):
    sql = "select * from score where stu_id = '%d' and coursename = '%s' and year = '%d' and term = '%d'"
    data = (username,coursename,year,term)
    cursor.execute(sql%data)
    if(cursor.rowcount) == 0:    #若查不到此数据则说明是最新成绩
        return True
    else:
        return False

def select_uncomment_score(year,term):
    sql = "select stu_id,coursename  from score where grade = '未评教' and year = %d and term = %d"
    data = (year,term)
    cursor.execute(sql%data)
    return cursor.fetchall()

def update_score(username,coursename,year,term,grade):
    gpa = calgpa(grade)
    sql = "update score set grade = '%s',gpa = '%f' where stu_id = '%d' and coursename = '%s' and year = '%d' and term = '%d'"
    data = (grade,gpa,username,coursename,year,term)
    cursor.execute(sql%data)
    connection.commit()
    print (username,'更新分数成功！'+coursename,grade)
    
def insert_score(username,year,term,coursename,credit,test_type,grade):
    gpa = calgpa(grade)
    sql = "insert into score(stu_id,year,term,coursename,credit,test_type,grade,gpa) values ('%d','%d','%d','%s','%f','%s','%s','%f')"
    data = (username,year,term,coursename,credit,test_type,grade,gpa)
    cursor.execute(sql%data)
    connection.commit()
    print (username,'添加分数成功！'+coursename,grade)

def select_score(username,year,term):
    sql = 'select * from score where stu_id = %d and year = %d and term = %d'
    data = (username,year,term)
    cursor.execute(sql%data)
    return cursor.fetchall()

def select_current_term():
    sql = 'select * from current_term'
    cursor.execute(sql)
    return cursor.fetchall()

def backup_student():
    sql = 'select * from teststudent'
    cursor.execute(sql)
    users = cursor.fetchall()
    for user in users:
        insert_student(user['stu_id'],user['password'],user['email'],user['sname'],user['course_count'])
        print ('备份用户成功！',user['stu_id'])
    
def backup_course():
    sql = 'select * from testcourse'
    cursor.execute(sql)
    courses = cursor.fetchall()
    for course in courses:        
        insert_course(course['stu_id'],course['cname'],course['sweek'],course['eweek'],course['ctime'],course['cweek'],course['wweek'])
        print ('备份课程成功！', course['stu_id'])

def backup_score():
    sql = 'select * from testscore'
    cursor.execute(sql)
    scores = cursor.fetchall()
    for score in scores:
        insert_score(score['stu_id'],score['year'],score['term'],score['coursename'],score['credit'],score['test_type'],score['grade'])
        print ('备份成绩成功！', score['stu_id'])

