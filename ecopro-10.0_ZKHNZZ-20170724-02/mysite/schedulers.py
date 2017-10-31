#!/usr/bin/env python
#coding=utf-8
import os,sys
from django.conf import settings
from django.core.cache import cache
import datetime
from mysite.utils import *
#from apscheduler.scheduler import Scheduler
from apscheduler.schedulers.blocking import BlockingScheduler
#import httplib, urllib
import urllib2
from mysite.base.models import *
from mysite.iclock.importwm import *
from mysite.iclock.models import *
from mysite.core.tools import *
from django.db import models, connection,connections
from mysite.tasks import *
sched=None
jCount=0
jjCount=150
import logging
logging.basicConfig()

def restartSvr(svrName):
    try:
        os.system("cmd /C net stop %s & net start %s"%(svrName, svrName))
    except:
        pass
def job_function(params):
    tempFile("job_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))+' begin restart')
    if params['TYPE']!='apache':
        restartSvr('AttServer')
    else:
        restartSvr('ZKEco-apache')

#def job_function1():
#	tempFile("att_%s.txt"%(datetime.datetime.now().strftime("%Y%m%d%H%M%S")),'begin restart')
#	restartSvr('attserver')
#	tempFile("att_%s.txt"%(datetime.datetime.now().strftime("%Y%m%d%H%M%S")),'end restart')
def job_check(params):
    global jCount
    global jjCount
    isRestart=cache.get(settings.UNIT+'_job')
    isRestartPull=cache.get(settings.UNIT+'_restart_pull')
    if isRestart and isRestart==1:
        cache.delete(settings.UNIT+'_job')
        processScheduler()
    if isRestartPull and isRestartPull==1:
        cache.delete(settings.UNIT+'_restart_pull')
        try:
            os.system("cmd /C %s/%s" % (settings.FILEPATH, 'iclockservice.exe -b 2'))
        except:
            pass
        tempFile("job_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s %s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),'restart pull service'))
    if cache.get('_iscalcing_'):return #在统计的时候暂时不检查，以免误判重启服务

    jjCount+=1
    if jjCount>4:
        jjCount=0
        tempFile("job_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s %s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),'ZKEco-server is running'))



    servers=params['SERVICES']
    if servers<2:
        url="http://%s:%s/iclock/getrequest"%(params['HOST'],params['Port'])
        try:
            response=urllib2.urlopen(url,data=None,timeout=10)
            jCount=0
        except Exception, e:
            if 'HTTP Error 500' not in str(e):
                jCount+=1
            else:
                print "job_check",e

            if jCount>1:
                jCount=0
                print "restart server start...."
                if params['TYPE']!='apache':
                    restartSvr('AttServer')
                else:
                    restartSvr('ZKEco-apache')
                tempFile("job_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s%s,%s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),' check restart',e))
                print "restart server end...."
    else:#集群，
        for p in range(servers):
            url="http://%s:%s/iclock/getrequest"%('127.0.0.1',params['Port%s'%p])
            try:
                response=urllib2.urlopen(url,data=None,timeout=10)
                jCount=0
            except Exception, e:
                if 'HTTP Error 500' not in str(e):
                    jCount+=1
                else:
                    print "job_check2",e

                if jCount>0:
                    jCount=0
                    print "restart server start....",p
                    restartSvr('ZKEco-apache%s'%p)
                    tempFile("job_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s%s,%s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),' check restart 0',e))
                    print "restart server end....",p

        #url="http://%s:%s/iclock/getrequest"%('127.0.0.1',params['Port1'])
        #try:
        #	response=urllib2.urlopen(url,data=None,timeout=20)
        #	jCount=0
        #except Exception, e:
        #	if 'HTTP Error 500' not in str(e):
        #		jCount+=1
        #	if jCount>0:
        #		jCount=0
        #		tempFile("job_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s%s,%s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),' check restart 1',e))
        #		restartSvr('iclock-apache1')



def job_test(params):
    tempFile("job_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s%s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),' ZKEco-server is running'))



    #tempFile("Calc_%s.txt"%(now.strftime("%Y%m")),'%s/%s-%s/%s sec'%(now.strftime("%Y%m%d"),st.strftime('%Y-%m-%d'),et.strftime('%Y-%m-%d'),t)+' end calc task')
    #try:
    #	adminLog(time=t2, action=u"自动统计", User=None,object=u'明细统计共%s人用时%s'%(sCount,(t2-t1).total_seconds()), model=u"%s %s"%(st.strftime('%Y-%m-%d'),et.strftime('%Y-%m-%d'))).save(force_insert=True)
    #except Exception,e:
    #	print "========1111",e
    #	pass

#sap对接读取人员表
def job_read_emp_data():
    checkEmpFile()
    checkSpecFile()

#sap对接读取排班表
def job_read_sch_data():
    checkSchFile()

def job_check_offline():
    checkDeviceOffline()

def job_photo_del_data():
    devs=iclock.objects.filter(ProductType=9).exclude(DelTag=1)
    for dev in devs:
        appendDevCmd(dev, "CLEAR PHOTO")
def job_trans_del_data():
    devs=iclock.objects.filter(ProductType=9).exclude(DelTag=1)
    for dev in devs:
        appendDevCmd(dev, "CLEAR LOG")

def job_check_trans():
    devs=iclock.objects.filter(ProductType=9).exclude(DelTag=1)
    st=datetime.datetime.now()
    for dObj in devs:
        dObj.LogStamp=0
        dObj.save()
        appendDevCmd(dObj, "CHECK",cmdTime=st)
        st+=datetime.timedelta(seconds=60)






def processScheduler():
    global sched
    sched.remove_all_jobs()
    nt=datetime.datetime.now()
    cfFileName=settings.APP_HOME+'/attsite.ini'
    hDict={}
    #tables = connections['DB'].introspection.table_names()
    if os.path.exists(cfFileName):
        import configparser
        cf = configparser.ConfigParser(strict=False,allow_no_value=True)
        cf.read(cfFileName)
        HOST = cf.get('Options','HOST',fallback='127.0.0.1')
        PORT = cf.getint('Options','Port',fallback=80)
        TYPE = cf.get('Options','Type',fallback='WSGI').lower()
        SERVICES=cf.getint('Options','Services',fallback=0) #只有集群时才需要设置如下3项，该值为2
        PORT0 = cf.getint('Options','Port0',fallback=8010)
        PORT1 = cf.getint('Options','Port1',fallback=8011)
        PORT2 = cf.getint('Options','Port2',fallback=8012)
        PORT3 = cf.getint('Options','Port3',fallback=8013)


        hDict={'Port':PORT,'HOST':HOST,'TYPE':TYPE,'Port0':PORT0,'Port1':PORT1,'Port2':PORT2,'Port3':PORT3,'SERVICES':SERVICES}


    try:
        cursor = connection.cursor()
    except:
        tempFile("Timer_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))+' start Timer task Failed,database connect failed')
        return


    tempFile("Timer_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))+' start Timer task')

    #监控服务任务
    #sched.add_cron_job(job_check,day_of_week='0-6', hour='4', minute='0', second='0', args=[hDict])
    #sched.add_cron_job(job_function,day_of_week='0-6', hour='4', minute='0', second='0', args=[hDict])
    if hDict:
        sched.add_job(job_check,'interval', seconds=30,args=[hDict])
    #sched.add_job(job_test,'interval', seconds=30,args=[hDict])

    now=datetime.datetime.now()



    #为四川泰康定制
    # AUTO_LOGS=(GetParamValue('opt_basic_Auto_logs','0')=='1')
    # if AUTO_LOGS:
    # 	sched.add_job(job_auto_logs,'cron',day_of_week='0-6', hour='22', minute='0', second='0', args=[])
    sched.add_job(job_check_acc_trans_again,'interval', minutes=180,args=[])
    sched.add_job(job_check_pos_trans_again,'interval',minutes=180,args=[])
    #收取门禁最新记录

    #自动统计任务
    calc_data=loads(GetParamValue('auto_calcdata','{}','tasks'))
    if calc_data:
        if calc_data['is_']==1:
            list_st=calc_data['st'].split('-')
            start_time=datetime.datetime(int(list_st[0]),int(list_st[1]),int(list_st[2]),0,0,0)

            if start_time<=nt:
                tasks_times = calc_data['stt'].split(';')
                for t in tasks_times:
                    tasks_time=t.split(':')
                    now=datetime.datetime.now()
                    sched.add_job(job_auto_calc_data,'cron',day_of_week='0-6', hour=tasks_time[0], minute=tasks_time[1], second='0', args=[2])

            sched.add_job(job_auto_calc_data,'interval',minutes=5, args=[0])

    #自动删除数据任务
    sched.add_job(job_auto_del_data,'cron',day_of_week='0-6', hour='6', minute='0', second='0', args=[])
    #每天9点收取设备上的考勤记录,倍耐力定制
    if settings.PIRELLI:
        sched.add_job(job_check_trans,'cron',day_of_week='0-6', hour='9', minute='0', second='0', args=[])
    #sched.add_cron_job(job_check_trans_again,day_of_week='0-6', hour='9', minute='0', second='0', args=[])
    #处理人员、排班及记录任务
    calc_data=loads(GetParamValue('sap_ftp','{}','sap'))
    if calc_data and calc_data['SAPhost'] and calc_data['SAPuser'] and calc_data['SAPpassword'] and calc_data['hour'] and calc_data['week_hour']:
        emp_hour=calc_data['hour']
        if emp_hour:
            tasks_time=emp_hour.split(':')
            tempFile("Emp_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s'%(emp_hour)+' start read emp')
            sched.add_job(job_read_emp_data,'cron',day_of_week='0-6', hour=tasks_time[0], minute=tasks_time[1], second='0', args=[])
        sch_hour=calc_data['week_hour']
        if sch_hour:
            tasks_time=sch_hour.split(':')
            tempFile("Sch_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s'%(sch_hour)+' start read emp')
            sched.add_job(job_read_sch_data,'cron',day_of_week='0-6', hour=tasks_time[0], minute=tasks_time[1], second='0', args=[])

    #脱机发送邮件任务
    calc_data=loads(GetParamValue('sap_email','{}','sap'))
    if calc_data and calc_data['emails'] and calc_data['interval'] and int(calc_data['interval'])>29:
        interval=int(calc_data['interval'])
        sched.add_job(job_check_offline,'interval', minutes=interval,args=[])

    #定时删除设备上的考勤照片或考勤记录
    del_data=loads(GetParamValue('auto_deldata','{}','tasks'))
    if del_data and 'st' in del_data.keys():
        del_st=del_data['st']
        if del_st:
            list_st=del_st.split('-')
            del_time=datetime.datetime(int(list_st[0]),int(list_st[1]),int(list_st[2]),0,0,0)

            if del_data and int(del_data['is_'])==1 and del_time<=nt:
                calc_data=loads(GetParamValue('day_deldata','{}','tasks'))
                if calc_data and  calc_data['trans_day'] and  calc_data['trans_day']==datetime.datetime.now().day:
                    sched.add_job(job_trans_del_data,'cron',day=calc_data['trans_day'], hour="9", minute="50", second='0', args=[])
                if calc_data and  calc_data['photo_day'] and  calc_data['photo_day']==datetime.datetime.now().day:
                    sched.add_job(job_photo_del_data,'cron',day=calc_data['photo_day'],hour="9", minute="50", second='0', args=[])

    if GetParamValue('opt_basic_Auto_iclock','0')=='1':
        check_mins=int(GetParamValue('opt_basic_check_mins','10'))
        if check_mins<1:check_mins=1
        sched.add_job(job_syncData,'interval', minutes=check_mins,args=[])
    if GetParamValue('opt_email_exceptionemail','')=='1' or  GetParamValue('opt_email_exceptionemail','')==1:
        sched.add_job(exception_sendemail,'cron',day_of_week='0-6', hour='7', minute='0', second='0', args=[])




def Run_Tasks():
    global sched
    cache.delete(settings.UNIT+'_job')
    sched = BlockingScheduler()
    processScheduler()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass


