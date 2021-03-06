#coding:utf-8
from crawler import *
from dao import mydao
from sendmail import *
import datetime
import time

def sendscore():
    users = []
    term_info = mydao.select_current_term()[0]
    year = term_info['year']
    term = term_info['term']
    uncomment_scores = mydao.select_uncomment_score(year,term)
    for uncomment_score in uncomment_scores:          #如果有未评教，则打开分数推送开关更新分数
        mydao.start_score(uncomment_score['stu_id'])
    users = mydao.select_score_student()
    usercount = len(users)
    for user in users:
        total_scores_count = user['course_count']
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print (user['stu_id'],user['password'],user['email'],user['sname'])
        print ('发送邮件的前一步')
        get_scores(str(user['stu_id']),user['password'],user['email'],user['sname'],total_scores_count,uncomment_scores)
        current_score_count = len(mydao.select_score(user['stu_id'],year,term))
        print ('总课程：%d'%total_scores_count,'当前课程：%d'%current_score_count)
        if (total_scores_count == current_score_count):
            mydao.shutdown_score(user['stu_id'])
        print ('发送邮件的后一步')
    return usercount

if __name__ == '__main__':
    a = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    starttime = time.time()
    usercount = sendscore()
    endtime = time.time()
    costtime = endtime-starttime
    print ('开始时间：',a)
    print ('结束时间：',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print ('用户数量：%d'%usercount,',耗费总时间(秒)：%0.2f'%costtime,',平均耗时(秒)：%0.2f'%(float(costtime/usercount)))
    text = "开始时间："+a+"\n结束时间："+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"\n用户数量："+str(usercount)+"\n耗费总时间：%0.2f"%costtime+"\n平均耗时：%0.2f"%float(costtime/usercount)
    sendmail('1242924472@qq.com',text,'已发送','汪俊')
