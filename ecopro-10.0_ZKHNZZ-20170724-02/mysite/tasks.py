# -*- coding: utf-8 -*-
import os,sys
from mysite.utils import *
from iclock.importwm import * 
from django.conf import settings
from iclock.datas import *
from apscheduler.schedulers.background import BackgroundScheduler
from mysite.iclock.models import *
from mysite.acc.models import *
from mysite.base.models import *
from mysite.core.tools import *
from mysite.core.cmdproc import *
import logging
logging.basicConfig()
from mysite.iclock.sendmail import *



def job_check_trans_again():
    u"""定时重收集记录"""
    devs=iclock.objects.filter(ProductType__in=[9,None]).exclude(DelTag=1).exclude(State=0)
    st=datetime.datetime.now()
    et=st-datetime.timedelta(days=1)
    sdate=datetime.datetime(et.year,et.month,et.day,0,0,0).strftime("%Y-%m-%d %H:%M:%S")
    enddate=st.strftime("%Y-%m-%d %H:%M:%S")
    for dObj in devs:
        if dObj.getDynState()==DEV_STATUS_OK:
            saveCmd(dObj.SN, "DATA QUERY ATTLOG StartTime=%s\tEndTime=%s"%(sdate,enddate),cmdTime=None)


def readrawData(device):
    u"""重新收取门禁记录"""
    fn="%s/reloadtrans_%s.log"%(logDir(),device.SN)
    if not os.path.exists(fn):return
    fnew="%s/reloadtrans_%s_read.log"%(logDir(),device.SN)
    try:
        os.remove(fnew)
    except Exception,e:
        pass
    try:
        os.rename(fn, fnew)
    except Exception,e:
        return
    f=open(fnew,'r')
    lines=f.readlines()
    f.close()

    attEventlist=['0', '1', '2', '3', '14', '15', '16', '17', '18', '19', '21', '22', '23', '26', '32', '35','203']
    try:
        for line in lines:
            line=line.strip()
            if line:
                ops=line.split(" ",1)
                if ops[0] in ['transaction','tranaction']:
                    d=lineToDict(ops[1])
                    d['eventaddr']=d['doorid']
                    #if d['doorid']>'0':
                    #	try:
                    #		obj=AccDoor.objects.get(device=device,door_no=d['doorid'])
                    #		d['eventaddr']=obj.door_name
                    #	except Exception,e:
                    #		pass

                    verify=200
                    if 'event' in d.keys() and d['event'] in ['220','221']:#辅助输入
                        d['cardno']=''
                    elif 'event' in d.keys() and d['event'] in ['12','13']:#联动
                        d['cardno']=''
                    else:
                        verify=d['verified']
                    if 'event' in d.keys() and d['event'] in ['105', '214']:continue
                    d['time']=OldDecodeTime(d['time_second'])
                    k=d['time']
                    logtime=datetime.datetime(int(k[0:4]),int(k[5:7]),int(k[8:10]),int(k[11:13]),int(k[14:16]),int(k[17:19]))
                    name=''
                    try:
                        emp=employee.objByPIN(d['pin'])
                        name=emp.EName or ''
                    except:
                        pass



                    logDict={'pin':d['pin'],'name':name,'card_no':d['cardno'],'TTime':logtime,'inorout':d['inoutstate'],'verify':verify,'SN_id':device.SN,'event_point_name':d['eventaddr'],'event_no':d['eventtype'],'dev_serial_num':d['index']}
                    sql,params=getSQL_insert_new(records._meta.db_table,logDict)
                    customSql(sql,params)
                    if hasattr(device,'Purpose') and device.Purpose==1:
                        if ('event' in d.keys() and d['event'] in attEventlist) or ('EventType' in d.keys() and d['EventType'] in attEventlist):
                            try:
                                obj=employee.objByPIN(d['pin'])
                            except:
                                obj=None
                            if obj:
                                CRCCode=''#encryption('%s'%(logtime.strftime('%H%M%S%m%d')))

                                RecordDict={'userid':obj.id,'checktime':logtime,'checktype':'I','verifycode':verify,'sn':device.SN,'workcode': 0, 'Reserved':CRCCode,'Purpose':9}
                                sql,params=getSQL_insert_new(transactions._meta.db_table,RecordDict)
                                customSql(sql,params)
        nt=datetime.datetime.now()
        fnewbak="%s/reloadtrans_%s_bak_%s.log"%(logDir(),device.SN,nt.strftime("%Y%m%d%H%M%S"))
        os.rename(fnew, fnewbak)
    except Exception,e:
        print "=================================readRawData"

def job_check_acc_trans_again():
    u"""每隔180分钟重收取门禁记录"""
    devs=iclock.objects.filter(ProductType__in=[5,15,25]).exclude(DelTag=1)
    st=datetime.datetime.now()
    j=0
    for dObj in devs:
        if dObj.getDynState()==DEV_STATUS_OK:
            j=1
            appendDevCmd(dObj,"DATA QUERY tablename=transaction,fielddesc=*,filter=NewRecord",cmdTime=st)
    if j>0:
        tempFile("job_check_acc_trans_again_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),u'%s----设备重收门禁记录命令下发完成'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S")))

def job_check_pos_trans_again():
        u"""每隔180分钟重收取消费记录"""
        from mysite.ipos.views import deviceLogCheck
        devs = iclock.objects.filter(ProductType__in=[11]).exclude(DelTag=1)
        st = datetime.datetime.now()
        err_log=[]
        for dObj in devs:
            if dObj.getDynState() == DEV_STATUS_OK:
                et=datetime.datetime.now()
                st=et-datetime.timedelta(seconds=3*60*60)
                err_log=deviceLogCheck(dObj.SN,st,et)
                if err_log:
                    message = u'成功检测到%s条未上传记录，系统已自动下发获取未上传记录命令' % len(err_log)
                    savePosLogToFile('checklog',message,dObj.SN)


#
def job_auto_del_data():
    u"""每天6点运行清除任务"""
    from mysite.iclock.models import devcmds,devlog,adminLog,oplog,transactions
    del_data=GetParamValue('auto_deldata','{}','tasks')
    dDict=loads(del_data)
    if not dDict:return
    nt=datetime.datetime.now()
    if dDict['is_']==0:return
    try:
        if datetime.datetime.strptime(dDict['st'],'%Y-%m-%d')>nt:return
    except:
        return

    if int(dDict['items'][0]['days'])>0:#服务器下发命令
        devcmds.objects.filter(Q(CmdTransTime__lt=nt-datetime.timedelta(days=int(dDict['items'][0]['days'])))|Q(CmdCommitTime__lt=nt-datetime.timedelta(days=30))).delete()
    if int(dDict['items'][1]['days'])>0:#设备上传数据日志
        devlog.objects.filter(OpTime__lt=nt-datetime.timedelta(days=int(dDict['items'][1]['days']))).delete()

    if int(dDict['items'][2]['days'])>0:#管理员操作日志
        adminLog.objects.filter(time__lt=nt-datetime.timedelta(days=int(dDict['items'][2]['days']))).delete()

    if int(dDict['items'][3]['days'])>0:#设备操作日志
        oplog.objects.filter(OPTime__lt=nt-datetime.timedelta(days=int(dDict['items'][3]['days']))).delete()
    if int(dDict['items'][4]['days'])>0:#考勤记录
        transactions.objects.filter(TTime__lt=nt-datetime.timedelta(days=int(dDict['items'][4]['days']))).delete()
    if int(dDict['items'][5]['days'])>0:#考勤照片
        import shutil
        pic_path=settings.ADDITION_FILE_ROOT+'upload'
        for root,dirs,files in os.walk(pic_path):
            for name in dirs:
                if len(name)<=6 and name<=(nt-datetime.timedelta(int(dDict['items'][5]['days']))).strftime("%Y%m"):
                    shutil.rmtree(os.path.join(root,name))
                    #print 'delete %s ok'%(os.path.join(root,name))

    tempFile("job_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),'%s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))+' del data end')




#
def job_auto_calc_data(isForce):
    u"""自动统计任务"""

    now=datetime.datetime.now()

    if isForce==0:
        if now.hour<10 or now.hour>16:return
    tempFile("job_%s.txt"%(now.strftime("%Y%m")),'%s'%(now.strftime("%Y%m%d%H%M%S"))+' start calc task')

    from mysite.iclock.attcalc import MainCalc
    st=datetime.datetime(now.year,now.month,1,0,0)
    et=datetime.datetime(now.year,now.month,now.day,23,59,59)
    lock_date=int(GetParamValue('opt_basic_lock_date','8'))
    stand=st+datetime.timedelta(days=lock_date)
    if stand>now  or lock_date==0:
        st=st-datetime.timedelta(days=2)
        st=datetime.datetime(st.year,st.month,1,0,0)
    t1=now
    #adminLog(time=datetime.datetime.now(), action=u"自动统计", object=u'自动统计开始', model="").save(force_insert=True)

    sCount=MainCalc([],[],st,et,isForce,1)
    t2=datetime.datetime.now()
    t=(t2-t1).total_seconds()

    tempFile("job_%s.txt"%(now.strftime("%Y%m")),'%s %s seconds'%(t2.strftime("%Y%m%d%H%M%S"),t)+' end calc task')


#定时收集无工号人员的记录，仅一个月之内的
def job_auto_logs():
    from mysite.iclock.devview import normalState,normalVerify
    logfiles=os.listdir(logDir())
    nt=datetime.datetime.now()
    PINS=[]
    tempFile("process_%s.txt"%(nt.strftime("%Y%m")),'%s-%s-start'%(nt.strftime("%Y%m%d"),nt.strftime("%H:%M")))
    for fn in logfiles:
        if fn[-3:].lower()!='log':continue
        sdate=fn[:8]
        if sdate<(nt-datetime.timedelta(days=31)).strftime('%Y%m%d'):
            try:
                os.remove(logDir()+'\%s' % (fn))
            except:pass
        else:
            pin=formatPIN(fn[9:-4])
            try:
                empl=employee.objByPIN(pin)
            except Exception,e:
                continue
            uid=empl.id

            p=(fn[9:-4],uid)
            if p not in PINS:
                PINS.append(p)


            f = open("%s/%s"%(logDir(),fn),'r')
            for eachline in f:
                lines=eachline[:-1].split('\t')
                if len(lines)<4:continue
                sn=lines[0]
                flds=lines[1:]+["","","","","","",""]
                if flds[5]=='255' and flds[3]=='3' and flds[0]==flds[4]:
                    continue

                k=flds[1]
                logtime=datetime.datetime(int(k[0:4]),int(k[5:7]),int(k[8:10]),int(k[11:13]),int(k[14:16]),int(k[17:19]),0)
                nt=datetime.datetime.now()
                purpose=9
                CRCCode=encryption('%s'%(logtime.strftime('%H%M%S%m%d')))

                logDict={'userid':uid,'checktime':logtime,'checktype':normalState(flds[2]),'verifycode':normalVerify(flds[3]),'sn':sn,'workcode': flds[4], 'Reserved':CRCCode,'Purpose':purpose}


                sql,params=getSQL_insert_new(transactions._meta.db_table,logDict)
                try:
                    customSqlEx(sql,params)

                except:
                    pass
            try:
                f.close()
                os.remove(logDir()+'\%s' % (fn))
            except:
                pass
    #处理指纹面部文件
    for pi in PINS:
        pin=pi[0]
        uid=pi[1]
        for i in range(10):
            fn='%s/%s-%s-%s.dat'%(settings.ADDITION_FILE_ROOT+"/reports",'FP',pin,i)
            try:
                f = open(fn,'r')
            except:
                f=None
            if not f:continue
            for line in f:
                ops=line.split(" ", 1)
                flds={}
                for item in ops[1].split("\t"):
                    index=item.find("=")
                    if index>0: flds[item[:index]]=item[index+1:]
                fp=trimTemp(flds["TMP"])
                sql=''
                try:
                    if fp:
                        fpver=10
                        f=BioData.objects.get(UserID=uid, bio_no=flds["FID"],majorver=fpver,bio_type=bioFinger)
                        if fp[:300]==f.bio_tmp[:300]:
                            pass # Template is same

                        else:
                            sql="update bio_data set bio_tmp = '%s', utime='%s' where userid=%s and bio_no=%s and majorver=%s and bio_type=bioFinger" % (fp, str(datetime.datetime.now())[:19], uid, f.FingerID,fpver)
                except ObjectDoesNotExist:
                    sql="insert into bio_data(bio_tmp, userid, bio_no,  utime, valid, majorver,bio_index,bio_format,minorver,bio_type) values('%s', %s, %s, '%s', 1,%s,0,0,'0',1)" % (fp, uid, flds["FID"],  str(datetime.datetime.now())[:19],fpver)
                if sql:
                    customSql(sql)
            try:
                f.close()
                os.remove(fn)
            except:
                pass

        for i in range(12):
            fn='%s/%s-%s-%s.dat'%(settings.ADDITION_FILE_ROOT+"/reports",'FACE',pin,i)
            try:
                f = open(fn,'r')
            except:
                f=None
            if not f:break
            for line in f:
                ops=line.split(" ", 1)
                flds={}
                for item in ops[1].split("\t"):
                    index=item.find("=")
                    if index>0: flds[item[:index]]=item[index+1:]
                fp=trimTemp(flds["TMP"])
                sql=''
                fpver=7
                fid=flds["FID"]
                if fp:
                    try:
                        f=BioData.objects.get(UserID=uid,majorver=fpver,bio_type=bioFace)
                        d_tmp=loads(f.bio_tmp)
                        isUpdate=True
                        if fid in d_tmp.keys():
                            if fp[:300]==d_tmp[fid][:300]:
                                isUpdate=False # Template is same
                        if isUpdate:
                            d_tmp[fid]=fp
                            dDict={'whereuserid':uid,'wheremajorver':fpver,'wherebio_type':bioFace,'bio_tmp':dumps1(d_tmp),'utime':datetime.datetime.now()}
                            sql,params=getSQL_update_new(BioData._meta.db_table,dDict)


                    except ObjectDoesNotExist:
                        d_tmp={fid:fp}
                        dDict={'userid':uid,'bio_no':0,'bio_index':0,'bio_format':0,'minorver':'0','duress':0,'majorver':fpver,'bio_tmp':dumps1(d_tmp),'bio_type':bioFace,'valid':1,'utime':datetime.datetime.now()}
                        sql,params=getSQL_insert_new(BioData._meta.db_table,dDict)
                if sql:
                    customSqlEx(sql,params)
            try:
                f.close()
                os.remove(fn)
            except:
                pass




def processTranData(device):
    #if device.ProductType!=9:
    #	if device.ProductType==None:
    #		pass
        #else:
        #	return
    nt=datetime.datetime.now()
#	if device.ProductType in [4,5,15]:return
    update_flag=False
    if not device.TransTime:
        device.TransTime=datetime.datetime(2000,1,1,0,0)


    stamp=device.TransTime
    empids=[]
    emps=employee.objects.filter(OpStamp__gt=stamp,OpStamp__lte=nt)  #不要加删除标记和离职查询条件
    fpts=BioData.objects.filter(UTime__gt=stamp)
    #faces=BioData.objects.filter(UTime__gt=stamp,bio_type=bioFace)
    device.TransTime=nt

    if  (device.UserCount>0) and (GetParamValue('opt_basic_Auto_del_iclock','0')=='1'):#处理离职删除人员，发送到所有设备
        LZ_emps=emps.filter(Q(OffDuty=1)|Q(DelTag=1)).filter(OpStamp__gt=nt-datetime.timedelta(days=60))
        for emp in LZ_emps:
            update_flag=True
            zk_delete_user_data(device,emp.pin())
            #appendDevCmdNew([device.SN], "DATA DEL_USER PIN=%s"%emp.pin())




    deptids=getDepartmentBySN(device.SN)
    if deptids:
        nt=datetime.datetime.now()

        if -1 not in deptids:
            emps=emps.filter(DeptID__in=deptids)
            fpts=fpts.filter(UserID__DeptID__in=deptids)

        emps=emps.exclude(OffDuty=1).exclude(DelTag=1).exclude(SN=device.SN)  #排除由设备本身上传的数据再把自己更新，这就要求人员通过其他方式更新数据时把SN更新或置空

        for emp in emps:
            empids.append(emp.id)
            update_flag=True
            #if (emp.SN!=device.SN):
            #appendEmpToDevNew([device.SN], emp, cursor=None,cmdTime=nt,finger=1,face=1,PIC=1)
        #处理设备上传的指纹面部到其他设备

        fps=list(fpts.exclude(SN=device.SN).values_list('UserID', flat=True).distinct())
        for t in fps:
            if t in empids:continue
            emp=employee.objByID(t)
            if emp.OffDuty==1 or emp.DelTag==1:continue
            empids.append(t)
            update_flag=True

        if empids:
            emps=employee.objects.filter(id__in=empids)
            zk_set_data(device,'userinfo',emps,cmdTime=None,is_finger=1,is_face=1,is_pic=1,is_pv=1,is_fv=1)

        #laKey="iclock_la_"+device.SN  #实现保存
        #cache.delete(laKey)
        if update_flag:
            device.TransTime=nt
            device.save(force_update=True)

def job_syncData():
    devs=iclock.objects.exclude(ProductType__in=[5,15,25,11,12,13]).exclude(DelTag=1)
    st=datetime.datetime.now()
    j=0
    for dObj in devs:
        if dObj.getDynState()!=DEV_STATUS_OK:continue
        device=getDevice(dObj.SN)
        try:
            processTranData(device) #实现自动下发变更人员信息
        except Exception,e:
            print "processTranData===",e
def exception_sendemail():
    att_date=trunc(datetime.datetime.now()-datetime.timedelta(days=1))
    attshifts=attShifts.objects.filter(Q(NoIn=1)|Q(NoOut=1)).filter(AttDate=att_date)
    for b in attshifts:
        emp=employee.objByID(b.UserID_id)
        if (not emp) or (not emp.email):
            continue
        toadd=[]
        addr_name='武陟县人民政府云考勤平台'
        content='您好！'
        ww='考勤异常通知'
        if b.NoIn==1:
            content+=str(b.ClockInTime)
            content+=':未签到;'
        if b.NoOut==1:
            content+=str(b.ClockOutTime)
            content+=':未签退;'
        content+='请留意！'
        toadd.append(emp.email)
        try:
            mail = SendMail(ww,'email/attExceptionMessage.html',{'MessageContent':content},toadd,from_addr_name=u"%s"%(u'时间&安全精细化管理平台'))
            mail.send_mail()
        except Exception,e:
            pass



def job_read_query_acc_log(param):
    scheduler = BackgroundScheduler()
    nt=datetime.datetime.now()+datetime.timedelta(seconds=2)
    scheduler.add_job(readrawData, 'date', run_date=nt,args=[param])
    scheduler.start()































def hourlyTask():
    import datetime
    try:
        checkUpload()
    except: pass

    #重新把自己加入任务列表, 1小时候重新运行
    cmd="%s\\hourlyTask.cmd %s"%(WORK_PATH, WORK_PATH)
    d=datetime.datetime.now()+datetime.timedelta(0, 60*60)
    scheduleTask(cmd, d.strftime("%H:%M:%S"), [])

def dailyTask():
    checkEmpFile()

def weeklyTask():
    checkSchFile()


def installTasks():
    cmd="%s\\dailyTask.cmd %s"%(WORK_PATH, WORK_PATH)
    scheduleTask(cmd, "00:00")

    cmd="%s\\weeklyTask.cmd %s"%(WORK_PATH, WORK_PATH)
    scheduleTask(cmd, "00:00", ['Su,']) #'Su', 'M', 'T', 'W', 'Th', 'F', 'Sa'

    d=datetime.datetime.now()+datetime.timedelta(0, 1*60*60)
    cmd="%s\\hourlyTask.cmd %s"%(WORK_PATH, WORK_PATH)
    scheduleTask(cmd, d.strftime("%H:00"), [])

if __name__=='__main__':
    argc=len(sys.argv)
    if argc<=1: #no arg
        hourlyTask()
    elif sys.argv[1]=='daily':
        dailyTask()
    elif sys.argv[1]=='week':
        weeklyTask()
    elif sys.argv[1]=='install':
        installTasks()
    else:
        print "ERROR argument"
