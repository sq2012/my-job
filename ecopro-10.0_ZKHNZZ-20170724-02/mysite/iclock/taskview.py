#!/usr/bin/env python
#coding=utf-8
from __future__ import division
from mysite.iclock.models import *
from django.template import loader, Context
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import string
import datetime
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import User
from mysite.cab import *
from mysite.iclock import reb
import os, time,re
from mysite.iclock.dataproc import *
from django.conf import settings
from mysite.iclock.iutils import *
from django.utils.translation import ugettext_lazy as _
#from django.utils.translation import gettext
from mysite.core.tools import *
from django.core.cache import cache
from mysite.utils import *
from mysite.iclock.schedule import *
from mysite.iclock.datas import LoadSchPlan
import calendar

lineFmt=u"&nbsp;&nbsp;&nbsp;&nbsp;%s<br />"
def InfoErrorRec(title, errorRecs):
    if not errorRecs: return ""
#	fname="import_%s.txt"%(datetime.datetime.now().isoformat().replace(":",""))
#	tmpFile(fname, "\n".join(errorRecs))
    return lineFmt%(_("%(num)d record(s) is duplicated or invalid.") % {'num':len(errorRecs)}) #u"<a href='/iclock/tmp/%s'> %d 条数据</a>为重复或无效记录。<br />"

def reportError(title, i, i_insert, i_update, i_rep, errorRecs):
    info=[]
    if i_insert: info.append(u"%s"%_("Inserted %(object_num)d successfully") % {'object_num':i_insert})
    if i_update: info.append(u"%s"%_("Updated %(object_num)d successfully") % {'object_num':i_update})
    if i_rep: info.append(u"%s"%_(" %(object_num)d already exists in the database")% {'object_num':i_rep})
    result = u"<h2>%s:</h2> <p />%s%s%s<br />" % (title,
        lineFmt%(u"%s"%_("In the data files %(object_num)d  %(object_name)s ")%{'object_num':i,'object_name': u"%s"%_('records')}),
        info and lineFmt%(u", ".join(info)) or "",
        InfoErrorRec(title, errorRecs))
    return result

def AppendUserDev(dispEmp, SNs, cursor):
    needSave=False
    try:
        pin=formatPIN(dispEmp[0])
        try:
            e=employee.objects.get(PIN=pin)
            if e.SN and (SNs!=settings.ALL_TAG) and (e.SN.SN not in SNs):
                return _("No permission to do on device %s!")%e.SN.SN #u"没有权限传送 %s 上登记的人员"%e.SN.SN
        except:
            e=employee(PIN=pin, DeptID=getDefaultDept())
            needSave=True
        try:
            device=getDevice(dispEmp[1])
            if (SNs!=settings.ALL_TAG) and (device.SN not in SNs):
                return _("No permission to download employee data to device %s!")%device.SN #u"没有权限传送人员到设备 %s"%device.SN
        except:
            if dispEmp[1]:
                return _("Designated device does not exist!") #u"指定设备不存在"
            elif SNs!=settings.ALL_TAG:
                return _("Not specified a device!") #u"没有指定设备"
            device=None
#		print "employee: dept=%s, sn=%s"%(e.DeptID, e.SN)
        if not e.DeptID:	#没有部门表示该员工已经被删除，所以需要恢复
            e.DeptID=getDefaultDept()
            needSave=True
#			print "save Dept of employee:", e
        if device and not e.SN: #没有登记设备的人员，则指定登记设备
            e.SN=device
            needSave=True
#			print "save device of employee:", e
        if needSave: e.save()
        if not device:	return
        cmdStr=getEmpCmdStr(e)
        if not cmdStr:
            return None
        appendDevCmd(device, cmdStr) #, UserName=User.username)
        for afp in fptemp.objects.filter(UserID=e):
#			print e.PIN, afp.FingerID
            appendDevCmd(device, u"DATA FP PIN=%s\tFID=%d\tSize=%d\tValid=%d\tTMP=%s"%\
                (e.pin(), afp.FingerID, 0, afp.Valid, afp.temp()))
    except Exception, e:
        errorLog()
        return "%s"%e

#"DATA DEL_USER PIN=%s"
def DelUserDev(dispEmp, SNs, cursor):
    try:
        pin=formatPIN(dispEmp[0])
        try:
            e=employee.objects.get(PIN=pin)
            if not e.DeptID:
                return _("Designated employee does not exist!")#u"指定人员不存在"
        except:
            return _("Designated employee does not exist!")#u"指定人员不存在"
        try:
            device=getDevice(dispEmp[1])
            if (SNs!=settings.ALL_TAG) and (device.SN not in SNs):
                return _("No permission to deete the employee's in device %s")%device #"没有权限删除设备 %s 中的人员"%device
        except:
            if dispEmp[1]:
                return _("Designated device does not exist!")
            elif (SNs!=settings.ALL_TAG and (not e.SN or (e.SN_id not in SNs))):
                if e.SN:
                    return _("Not specified a device, and no permission to delete employee from device %s.")%e.SN #u"没有指定设备"+u", 并且没有权限从登记设备 %s 中删除该人员"%e.SN
                else:
                    return _("Not specified a device, and the employee has no a enrollment device.") #u"没有指定设备，并且该人员没有登记设备")
            device=None
        delEmpFromDev(SNs==settings.ALL_TAG, e, device)
    except Exception, e:
        return "%s"%e

def NameUserDev(dispEmp, SNs, cursor):
    newUser=False
    assignDev=False
    try:
        device=getDevice(dispEmp[2])
    except:
        device=None
    try:
        userName=dispEmp[1]
    except:
        userName=u""
    try:
        pin=dispEmp[0]
        if (len(pin)!=PIN_WIDTH) or (not pin.isdigit()) or (int(pin,10) in DISABLED_PINS):
            return _("%s is not a valid PIN.")%pin #pin+u" 不是一个合法的考勤号码"
        try:
            e=employee.objects.get(PIN=pin)
        except:
            e=employee(PIN=pin, EName=userName, DeptID=getDefaultDept())
            if device: e.SN=device
            e.save()
            newUser=True
        else:
            if (not e.DeptID) or (userName and (userName!=e.EName)) or (device and not e.SN):
                e.DeptID=getDefaultDept()
                e.EName=userName
                if not e.SN:
                    assignDev=True
                    e.SN=device
                e.save()

            userName=e.EName
            if not device:
                device=e.SN
        if not device:
            return _("Not specified a valid device, or the employee has no a enrollment device!")#u"没有指定合适的考勤机，或者该人员没有登记考勤机"
        if (not newUser) and not userName:
            return _("The employee no in the database.")#u"该用户在数据库中还没有录入姓名"
        sql= u"DATA USER PIN=%s\tName=%s"%(e.pin(), e.EName)
        appendDevCmd(device, sql, cursor)
        #backDev=device.BackupDevice()
        #if backDev:
            #appendDevCmd(backDev, sql, cursor)
        if assignDev: #新用户同时传送指纹
            for afp in fptemp.objects.filter(PIN=e):
                #print e.PIN, afp.FingerID
                sql=u"DATA FP PIN=%s\tFID=%d\tSize=%d\tValid=%d\tTMP=%s"%\
                    (e.pin(), afp.FingerID, 0, afp.Valid, afp.temp())
                appendDevCmd(device, sql, cursor)
                #if backDev:
                    #appendDevCmd(backDev, sql, cursor)
    except Exception, e:
        return "%s"%e


def disp_emp(request, delemp):
    from django.db import connection as conn
    cursor = conn.cursor()
    task=(delemp and u"deluser" or ((request.path.find("name_emp")>=0) and u"username" or u"userinfo"))
    titles={"deluser": _("Delete employee from device"),# u"删除考勤机上的人员",
        "username":_("Download employee's name to device"),# u"传送人员姓名到考勤机",
        "userinfo":_("Dispatch employee to device")}# u"分派人员到考勤机"}
    title=titles[task]
    if not (request.method == 'POST'):
        return render_to_response("disp_emp.html", {"title": title, 'task': task})
    #POST
    cc=u""

    SNs=request.user.is_superuser and settings.ALL_TAG or getUserIclocks(request.user)

    process=(task=="deluser") and DelUserDev or ((task=="userinfo") and AppendUserDev or NameUserDev)
    errorLines=[]
    i=0;
    okc=0;
    f=request.FILES["fileUpload"]
    lines=""
    for chunk in f.chunks():
        lines+=chunk
    lines=lines.decode("GBK").split("\n")
    for line in lines:
        i+=1;
        if line:
            if line[-1] in ['\r','\n']: line=line[:-1]
        if line:
            if line[-1] in ['\r','\n']: line=line[:-1]
        try:
#			print line
            if line:
                if line.find("\t")>=0:
                    data=(line+"\t").split("\t")
                elif line.find(",")>=0:
                    data=(line+",").split(",")
                else:
                    data=(line+" ").split(" ",1)
                error=process(data,SNs,cursor)
                if error:
                    errorLines.append(u"Line %d(%s):%s"%(i,line,error))
                okc+=1
        except  Exception, e:
            errorLines.append(u"Line %d(%s):%s"%(i,line,str(e)))
    if okc:
        conn._commit()
    if len(errorLines)>0:
        if okc>0:
            cc+=(_("%s employee's data is ready to transfer, but following record(s) is missing:")%okc)+"</p><pre>" # u"%d 位员工处理数据已经提交准备传送, 但是发生如下错误:</p><pre>"%okc
        else:
            cc+=_("There are wrong: ")+"</p><pre>" # u"没有员工处理数据被传送, 发生如下错误:\n</p><pre>"
        cc+=u"\n".join(errorLines)
        cc+=u"</pre>"
    else:
        cc+=_("%s employee(s) data is ready to transfer.")%okc# u"%d 位员工处理数据已经提交准备传送"%okc
    return render_to_response("info.html", {"title": title, "content": cc})

@login_required
def FileDelEmp(request):
    return disp_emp(request, True)

@login_required
def FileChgEmp(request):
    return disp_emp(request, False)

@login_required
def disp_emp_log(request):
    return render_to_response("disp_emp_log.html",{"title": _("Dispatch employee data to device")})# u"分派人员到考勤机"})

def saveUser(pin, pwd, ename, card, grp, tzs):
    try:
        e=employee.objects.get(PIN=pin)
    except:
        e=employee(PIN=pin, DeptID=getDefaultDept())
    if ename: e.EName=unicode(ename,"gb2312")
#	if card: e.Card=card
    if pwd: e.MVerifyPass=pwd
    if grp: e.AccGroup=grp
    if tzs: e.TimeZones=tzs
    e.save()

def saveFTmp(pin, fid, tmp):
    try:
        t=fptemp.objects.get(PIN=employee.objects.get(PIN=pin), FingerID=fid)
        if t.Template!=tmp:
            t.Template=tmp
            t.save()
    except:
        t=fptemp(PIN=employee.objects.get(PIN=pin), FingerID=fid, Valid=1, Template=tmp)
        t.save()
#iNewCount=0
#iUpdateCount=0
#i_insert, i_update, i_rep = 0, 0, 0

@login_required
def importEmp(request):
#	if not (request.method == 'POST'):
#		return render_to_response("Import_emp.html",{"title": _("Upload employee list") # u"批量上传人员列表",
#		})
    try:
        etype = {}
        for et in EMPTYPE_CHOICES:
            etype[et[1]] = et[0]
        imFields=['badgenumber']
        imFieldsInfo={}
        imDatalist=[]
        sUserids=[]
        Male=request.POST["man"]
        Female=request.POST["woman"]
        OffDuty_yes=request.POST["OffDuty_yes"]
        dept=request.POST.get("dept",'')
        oriFields=request.POST["fields"].split(',')
        fromline=request.POST.get("rowid2","1")
        isAllowNoDept=request.POST.get("nodept","")
        deptid=''
        if dept:
            deptid=int(dept)
        if isAllowNoDept=='on':
            isAllowNoDept=True
        else:
            isAllowNoDept=False

        if fromline=="":
            fromline=1
        fromline=int(fromline)
        for t in oriFields:
            fldName=request.POST.get(t,"")
            if fldName=='on':
                imFields.append(t)
        maxCol=0
        for t in imFields:
            try:
                imFieldsInfo[t]=int(request.POST.get(t+"2file","-1"))
                if maxCol<imFieldsInfo[t]:maxCol=imFieldsInfo[t]
            except:
                cc=_("employee's data imported failed")+"</p><pre>"
                cc+=request.POST.get(t+"2file","-1")
                return render_to_response("info.html", {"title": _("Import employee list"), "content": cc})
        f=request.FILES["fileUpload"]
        data=""
        fName=f.name
        whatrow=request.POST["whatrowid2file"]
        #ext=fName[fName.find('.')+1:].upper()
        ext=''
        fl=fName.split('.')
        if fl:
            ext=fl[-1].upper()
        if ext=='XLSX':ext='XLS'
        zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
        lines=[]
        for chunk in f.chunks(): data+=chunk
        if ext=='TXT' or ext=='CSV':
            lines=data.splitlines()
        elif ext=='XLS' or ext=='XLSX':
            import xlrd
#			fn="%s/%s"%(tmpDir(),fName)
            fName=fName.encode("gb2312")#修改导入文件名称为中文报错问题
            fn="%s/%s"%(tmpDir(),fName)
            f=file(fn, "wb")
            try:
                f.write(data)
            except:
                pass
            f.close()
            bk = xlrd.open_workbook(fn)
            sheetNames=bk.sheet_names()
            if not sheetNames:
                cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            shxrange = range(bk.nsheets)
            try:
                sh = bk.sheet_by_index(0)
            except:
                s="no sheet in %s named %s" %(fn,sheetNames[0])
                cc=u"%s,%s"%(_('imported failed'),s)
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            nrows = sh.nrows
            ncols = sh.ncols
            for i in range(0,nrows):
                sv=[]
                c=0
                #try:
                for sr in sh.row_values(i):
                    if type(sr)==type(1.0):
                        sr=str(long(sr))
                        if sr.find(".0")!='-1':
                            sr=sr.split(".")[0]
                        else:
                            sr=sr
                    sv.append(sr)
                    c=c+1
                    if c>maxCol-1:break

#				row_data = sh.row_values(i)
                row_data = sv
                lines.append(row_data)
        jjj=0
        jj=0



        settings.DEV_STATUS_SAVE=1

        iCount=len(lines)          #import users count
        i_insert=0
        i_update=0
        i_rep=0
        errorRec=[]
        #adminLog(time=datetime.datetime.now(),User=request.user,model = employee._meta.verbose_name,action=u'%s'%_("import employee data"),count = iCount).save(force_insert = True)
        sqlList=[]
        r=0

        for t in lines:
            r+=1
            if int(whatrow)>r:
                continue
            jj+=1
            if jj<fromline:continue
            dDict={}
            if ext=="TXT":
                ls=t.split('\t')
            elif ext=='CSV':
                ls=t.split(',')
            elif ext=='XLS' or ext=='XLSX':
                ls=t
            for k,v in imFieldsInfo.items():
                try:
                    if v<1 or v>100:
                        continue
                except:
                    continue
                v=int(v)
                ls[v-1]=ls[v-1].strip()
                if k=='badgenumber':
#					ls[v-1]=ls[v-1]
                    if ls[v-1]=='':
                        errorRec.append(ls[v-1])
                        dDict={}
                        break
                    match = zhPattern.search(ls[v-1])
                    if match:
                        errorRec.append(ls[v-1])
                        dDict={}
                        break


                    sUserids.append(ls[v-1])
                if k=="Gender":
                    if v<=len(ls):
                        if ext=='XLS' or ext=='XLSX':
                            s=ls[v-1]
                        else:
                            s=getStr_c_decode(ls[v-1])
                        if s==Male:
                            ls[v-1]="M"
                        elif s==Female:
                            ls[v-1]="F"
                        else:
                            ls[v-1]=""
                if k=="OffDuty":
                    if v<=len(ls):
                        if ext=='XLS' or ext=='XLSX':
                            s=ls[v-1]
                        else:
                            s=getStr_c_decode(ls[v-1])
                        if s==OffDuty_yes:
                            ls[v-1]=1
                        else:
                            ls[v-1]=0
                if v<=len(ls):
                    s=ls[int(v)-1]
                    if ext=='XLS' or ext=='XLSX':
                        if k in ['Birthday','Hiredday']:
                            if str(type(s))=="<type 'unicode'>":#因日期格式复杂，当为文本时暂不支持，建议修改EXCEL文件单元格格式为日期型

                                #bb=s.split('-')
                                #iDate1=datetime.datetime(int(bb[0]),int(bb[1]),int(bb[2]))
                                #dDict[k]=iDate1
                                dDict[k]=''
                            else:
                                #try:
                                #	aa=s
                                #	bb=aa.split('-')
                                #	iDate1=datetime.datetime(int(bb[0]),int(bb[1]),int(bb[2]))
                                #	dDict[k]=iDate1
                                #
                                #except:
                                #	try:
                                #		iDate = int(s)
                                #		lDate=xlrd.xldate_as_tuple(iDate,bk.datemode)
                                #		dDict[k]=datetime.datetime(lDate[0],lDate[1],lDate[2])
                                #	except:
                                #		dDict[k]=None
                                try:		#dDict[k]=datetime.datetime.now().strftime("%Y-%m-%d")
                                    iDate = int(s)
                                    lDate=xlrd.xldate_as_tuple(iDate,bk.datemode)
                                    dDict[k]=datetime.datetime(lDate[0],lDate[1],lDate[2])
                                except:
                                    dDict[k]=''
                        else:
                            dDict[k]=s
                    else:
                        dDict[k]=getStr_c_decode(s)
            if dDict:
                if dDict.has_key('Birthday'):
                    if not dDict['Birthday']:
                        del dDict['Birthday']
                if dDict.has_key('Hiredday'):
                    if not dDict['Hiredday']:
                        del dDict['Hiredday']
                if dDict.has_key('Employeetype'):
                    ht = dDict['Employeetype']
                    if etype.has_key(ht):
                        dDict['Employeetype'] = etype[ht]
                    else:
                        dDict['Employeetype'] = ''
                if not dDict.has_key('defaultdeptid'):
                    if not deptid:
                        if not isAllowNoDept:
                            s=u"部门编号为不能为空"
                            cc=u"%s,%s"%(_('imported failed'),s)
                            settings.DEV_STATUS_SAVE=0

                            return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                    else:
                        dDict['defaultdeptid']=deptid
                        isAllowNoDept=False
                else:
                    isAllowNoDept=False
                    deptNum=dDict['defaultdeptid']   #实际为部门编号
                    dt=department.objByNumber(dDict['defaultdeptid'])
                    if dt:
                        dDict['defaultdeptid']=dt.DeptID
                    else:
                        errorRec.append(dDict['badgenumber'])
                        s=u"人员身份证号为 %s 的部门编号不存在" %(dDict['badgenumber'])
                        cc=u"%s,%s"%(_('imported failed'),s)
                        settings.DEV_STATUS_SAVE=0
                        return getJSResponse({"ret":1,"message": cc},mtype="text/plain")

                jjj+=1
                try:
                    #e=employee.objByPIN(dDict['badgenumber'])
                    e=employee.objects.filter(PIN=dDict['badgenumber'])
                except:
                    e=None
                dDict['DelTag']=0
                if not dDict.has_key('OffDuty'):
                    dDict['OffDuty']=0
                iclocks=iclock.objects.filter(ProductType__in=[5,15,25])
                if e:
                    e=e[0]
                    dDict['wherebadgenumber']=dDict['badgenumber']
                    if dDict.has_key('Workcode'):
                        if e.Workcode != dDict['Workcode']:
                            dDict['OpStamp']=datetime.datetime.now()
                    if dDict.has_key('name'):
                        if e.EName != dDict['name']:
                            dDict['OpStamp']=datetime.datetime.now()
                    if dDict.has_key('Card'):
                        if e.Card != dDict['Card']:
                            dDict['OpStamp']=datetime.datetime.now()
                    if dDict.has_key('defaultdeptid') and e.DeptID_id != dDict['defaultdeptid']:
                        dDict['OpStamp']=datetime.datetime.now()
                    dDict['SN']=''
                    del dDict['badgenumber']
                    sql,params=getSQL_update_new('userinfo',dDict)
                    if customSqlEx(sql,params):
                        i_update+=1
                        cache.delete("%s_iclock_emp_%s"%(settings.UNIT,e.id))
                        cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,e.PIN))
                    if dDict.has_key('OffDuty') and dDict['OffDuty']==1:
                        emppin=e.pin()
                        if settings.IDFORPIN==1:
                            emppin=e.id
                        for dev in iclocks:
                            delete_data(dev.SN,'user','Pin=%s'%emppin)
                else:
                    if not isAllowNoDept:
                        dDict['OffPosition']=0
                        dDict['bstate']=2
                        dDict['ATT']=1
                        dDict['OverTime']=1
                        dDict['Holiday']=1
                        dDict['INLATE']=0
                        dDict['OutEarly']=0
                        dDict['OpStamp']=datetime.datetime.now()
                        sql,params=getSQL_insert_new('userinfo',dDict)
                        if customSqlEx(sql,params):
                            i_insert+=1
                    else:
                        errorRec.append(dDict['badgenumber'])
        # if dept:
        #     imp_DeptNumber = department.objects.get(DeptID = int(dept),DelTag = 0).DeptNumber
        #     adminLog_object = u'%s:'%_(u"department number") + u'%s'%imp_DeptNumber
        #     adminLog(time = datetime.datetime.now(), User = request.user, model = employee._meta.verbose_name,
        #              object = adminLog_object, action = u'%s' % _(u"import employee data"),
        #              count = jjj).save(force_insert = True)
        # else:
        #     adminLog(time = datetime.datetime.now(), User = request.user, model = employee._meta.verbose_name,
        #             object = request.META["REMOTE_ADDR"], action = u'%s' % _(u"import employee data"),
        #              count = jjj).save(force_insert = True)#
        result=reportError(u"%s"%_("user information"), jjj, i_insert, i_update, i_rep, errorRec)
        settings.DEV_STATUS_SAVE=0
        return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")

    except Exception,e:
        print "importEmp====",e
        settings.DEV_STATUS_SAVE=0
        cc=u"<h1>%s</h1><br/>%s"%(_("Import employee list"),_("employee's data imported failed"))+"</p><pre>"
        return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
#		cc+=request.POST.get(t+"2file","")
#		return HttpResponse(content="result=1",mimetype='text/plain')#render_to_response("info.html", {"title": _("Import employee list"), "content": cc})

@login_required
def importTrans(request):
    try:
        imFields=[]
        imFieldsInfo={}
        imDatalist=[]
        sUserids=[]
        i_insert=0
        i_update=0
        i_rep=0

        imFields=request.POST["fields"].split(',')
        for t in imFields:
            try:
                imFieldsInfo[t]=int(request.POST.get(t+"2file","-1"))
            except:
                cc=_(u"导入考勤记录失败")+"</p><pre>"
                cc+=request.POST.get(t+"2file","-1")
                return render_to_response("info.html", {"title": _(u"批量上传考勤记录"), "content": cc})
        f=request.FILES["fileUpload"]
        data=""
        fName=f.name
        whatrow=request.POST["whatrowid2file"]
        #ext=fName[fName.find('.')+1:].upper()
        fl=fName.split('.')
        ext=''
        if fl:
            ext=fl[-1].upper()
        if ext not in ['TXT','CSV','XLS','XLSX']:
            result=u'%s'%(u'导入的文件名扩展名错误')
            return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")
        if ext=='XLSX':ext='XLS'
        for chunk in f.chunks():
            data+=chunk
        lines = []
        if ext=='TXT' or ext=='CSV':
            lines=data.splitlines()
        elif ext=='XLS' or ext=='XLSX':
            import xlrd
#			fn="%s/%s"%(tmpDir(),fName)
            fName=fName.encode("gb2312")
            fn="%s/%s"%(tmpDir(),fName)
            f=file(fn, "wb")
            try:
                f.write(data)
            except:
                pass
            f.close()
            bk = xlrd.open_workbook(fn)
            sheetNames=bk.sheet_names()
            if not sheetNames:
                cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")

            shxrange = range(bk.nsheets)
            try:
                sh = bk.sheet_by_index(0)
            except:
                s="no sheet in %s named %s" %(fn,sheetNames[0])
                cc=u"%s,%s"%(_('imported failed'),s)
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            nrows = sh.nrows
            ncols = sh.ncols
            for i in range(0,nrows):
                sv=[]
                for sr in sh.row_values(i):
                    if type(sr)==type(1.0):
                        sr=str(long(sr))
                        if sr.find(".0")!='-1':
                            sr=sr.split(".")[0]
                        else:
                            sr=sr
                    sv.append(sr)
                row_data = sv
                lines.append(row_data)
        jjj=0
        iCount=0
        sqlList=[]
        r=0
        for t in lines:
            r+=1
            if int(whatrow)>r:
                continue
            dDict={}
            if ext=="TXT":
                ls=t.split('\t')
            elif ext=='CSV':
                ls=t.split(',')
            elif ext=='XLS' or ext=='XLSX':
                ls=t
            for k,v in imFieldsInfo.items():
                try:
                    if v<1 or v>10:
                        continue
                except:
                    continue
                if k.lower()=='PIN':

                    if ext!='XLS' and ext!='XLSX':
                        if ls[v-1]==''  or (not ls[v-1].isdigit()):
                            dDict={}
                            break
                    else:
                        if ls[v-1]=='' or isinstance(type(ls[v-1]),type(u'1')) or isinstance(type(ls[v-1]),type(1))or isinstance(type(ls[v-1]),type(1.0)):
                            dDict={}
                            break
                        else:
                            try:
                                ls[v-1]=int(ls[int(v)-1])
                            except:
                                dDict={}
                                break
                if v<=len(ls):
                    if ext!='XLS' and ext!='XLSX':
                        dDict[k]=getStr_c_decode(ls[int(v)-1])
                    else:
                        if k=='checktime':
                            if str(type(ls[int(v)-1]))=="<type 'unicode'>":
                                try:
                                    dDict['checktime']=datetime.datetime.now().strptime(ls[int(v)-1],"%Y-%m-%d %H:%M:%S")
                                except:
                                    dDict['checktime']=datetime.datetime.now().strptime(ls[int(v)-1],"%Y/%m/%d %H:%M:%S")
                            else:
                                try:
                                    iDate = int(ls[int(v)-1])
                                    lDate=xlrd.xldate_as_tuple(iDate,bk.datemode)
                                    dDict[k]=datetime.datetime(lDate[0],lDate[1],lDate[2])
                                except:
                                    dDict[k]=''
                        else:
                            dDict[k]=ls[int(v)-1]
            if dDict!={}:
                jjj+=1
                emp=employee.objects.filter(PIN=dDict['PIN'])
                if emp:
                    dDict['userid']=emp[0].id
                    del dDict['PIN']
                    sqlList.append(dDict)
                else:
                    #s=u"人员工号为 %s 的人员不存在" %(dDict['PIN'])
                    #cc=u"<h2>%s</h2><p>%s</p>"%(_(u'导入失败'),s)
                    #return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                    continue
        for dDict_n in sqlList:
            sql,params=getSQL_insert_new(transactions._meta.db_table,dDict_n)
            try:
                customSql(sql,params)
                i_insert+=1
            except:
                pass
        result=reportError(u"%s"%_(u"导入考勤记录"), jjj, i_insert, i_update, i_rep, [])
        adminLog(time=datetime.datetime.now(),User=request.user, action=u'%s'%_(u"Import"),model = transactions._meta.verbose_name,object = request.META["REMOTE_ADDR"],count = jjj).save(force_insert = True)
        return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")
    except Exception,e:
        print "import transactions====%s"%e
        cc=u"<h2>%s</h2>"%_(u"导入考勤记录失败")
        return getJSResponse({"ret":1,"message": cc},mtype="text/plain")

@login_required
def importDept(request):
#	if not (request.method == 'POST'):
#		return render_to_response("Import_emp.html",{"title": _("Upload employee list") # u"批量上传人员列表",
#		})
    try:
        imFields=[]
        imFieldsInfo={}
        imDatalist=[]
        sUserids=[]
        i_insert=0
        i_update=0
        i_rep=0

        imFields=request.POST["fields"].split(',')
        for t in imFields:
            try:
                imFieldsInfo[t]=int(request.POST.get(t+"2file","-1"))
            except:
                cc=_("department's data imported failed")+"</p><pre>"
                cc+=request.POST.get(t+"2file","-1")
                return render_to_response("info.html", {"title": _("Import department list"), "content": cc})
        f=request.FILES["fileUpload"]
        data=""
        fName=f.name
        whatrow=request.POST["whatrowid2file"]
        #ext=fName[fName.find('.')+1:].upper()
        ext=''
        fl=fName.split('.')
        if fl:
            ext=fl[-1].upper()
        if ext=='XLSX':ext='XLS'
        for chunk in f.chunks():
            data+=chunk
        lines = []
        if ext=='TXT' or ext=='CSV':
            lines=data.splitlines()
        elif ext=='XLS' or ext=='XLSX':
            import xlrd
#			fn="%s/%s"%(tmpDir(),fName)
            fName=fName.encode("gb2312")
            fn="%s/%s"%(tmpDir(),fName)
            f=file(fn, "wb")
            try:
                f.write(data)
            except:
                pass
            f.close()
            bk = xlrd.open_workbook(fn)
            sheetNames=bk.sheet_names()
            if not sheetNames:
                cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")

            shxrange = range(bk.nsheets)
            try:
                sh = bk.sheet_by_index(0)
            except:
                s="no sheet in %s named %s" %(fn,sheetNames[0])
                cc=u"%s,%s"%(_('imported failed'),s)
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            nrows = sh.nrows
            ncols = sh.ncols
            for i in range(0,nrows):
                sv=[]
                for sr in sh.row_values(i):
                    if type(sr)==type(1.0):
                        sr=str(long(sr))
                        if sr.find(".0")!='-1':
                            sr=sr.split(".")[0]
                        else:
                            sr=sr
                    sv.append(sr)
#				row_data = sh.row_values(i)
                row_data = sv
                lines.append(row_data)
        jjj=0
        iCount=0
        sqlList=[]
        r=0
        noparents=[]
        for t in lines:
            r+=1
            if int(whatrow)>r:
                continue
            dDict={}
            if ext=="TXT":
                ls=t.split('\t')
            elif ext=='CSV':
                ls=t.split(',')
            elif ext=='XLS' or ext=='XLSX':
                ls=t
            for k,v in imFieldsInfo.items():
                try:
                    if v<1 or v>10:
                        continue
                except:
                    continue
                if k.lower()=='deptid':
                    if ext!='XLS' and ext!='XLSX':
                        if ls[v-1]==''  or (not ls[v-1].isdigit()):
                            dDict={}
                            break
                    else:
                        if ls[v-1]=='' or isinstance(type(ls[v-1]),type(u'1')) or isinstance(type(ls[v-1]),type(1))or isinstance(type(ls[v-1]),type(1.0)):
                            dDict={}
                            break
                        else:
                            try:
                                ls[v-1]=int(ls[int(v)-1])
                            except:
                                dDict={}
                                break
                if v<=len(ls):
                    if ext!='XLS' and ext!='XLSX':
                        dDict[k]=getStr_c_decode(ls[int(v)-1])
                    else:
                        dDict[k]=ls[int(v)-1]
            if dDict!={}:
                jjj+=1
                # supdt=department.objByNumber(dDict['supdeptnum'])
                if not dDict['supdeptnum']:
                    s=u"部门编号为 %s 的上级部门不能为空" %(dDict['DeptNumber'])
                    cc=u"%s,%s"%(_('imported failed'),s)
                    return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                else:
                    try:
                        supdt = department.objects.get(DeptNumber=dDict['supdeptnum'])
                    except:#如果没有上级部门暂时放在总部门下
                        supdt = department.objects.order_by('DeptID').first()
                        noparents.append(dDict.copy())
                    try:
                        # dt=department.objByNumber(dDict['DeptNumber'])
                        dt = department.objects.get(DeptNumber=dDict['DeptNumber'])
                    except:
                        dt = None
                    if supdt:
                        dDict['supdeptid']=supdt.DeptID
                    elif dDict['supdeptnum']=='0' or dDict['DeptNumber']=='1':
                        dDict['supdeptid']=0
                        if not dt:
                            dt = department.objects.order_by('DeptID').first()
                # if not dDict['supdeptnum']:
                #     s=u"部门编号为 %s 的上级部门不能为空" %(dDict['DeptNumber'])
                #     cc=u"%s,%s"%(_('imported failed'),s)
                #     return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                # # else:
                #     s=u"部门编号为 %s 的上级部门不存在" %(dDict['DeptNumber'])
                #     cc=u"%s,%s"%(_('imported failed'),s)
                #     return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                del dDict['supdeptnum']
                dDict['DelTag']=0
                if dt:
                    dDict['whereDeptID']=dt.DeptID
                    sql,params=getSQL_update_new('departments',dDict)
                    if customSqlEx(sql,params):
                        cache.delete("%s_iclock_dept_%s_%s"%(settings.UNIT,dt.DeptID,settings.DEPTVERSION))
                        i_update+=1
                else:
                    sql,params=getSQL_insert_new('departments',dDict)
                    if customSqlEx(sql,params):
                        i_insert+=1
        for dDict in noparents:
            try:
                supdt = department.objects.get(DeptNumber=dDict['supdeptnum'])
            except:  # 如果没有上级部门暂时放在总部门下
                supdt = None
            try:
                dt = department.objects.get(DeptNumber=dDict['DeptNumber'])
            except:
                dt = None
            if supdt and dt:
                dDict['supdeptid'] = supdt.DeptID
                dDict['whereDeptID'] = dt.DeptID
                del dDict['supdeptnum']
                sql, params = getSQL_update_new('departments', dDict)
                if customSqlEx(sql, params):
                    cache.delete("%s_iclock_dept_%s_%s" % (settings.UNIT, dt.DeptID, settings.DEPTVERSION))

        UpdateDeptCache()   #更新部门Cache
        cache.delete("%s_allchilds"%(settings.UNIT))
        result=reportError(u"%s"%_("department information"), jjj, i_insert, i_update, i_rep, [])
        adminLog(time=datetime.datetime.now(),User=request.user, action=u'%s'%_(u"Import"),model = department._meta.verbose_name,object = request.META["REMOTE_ADDR"],count = jjj).save(force_insert = True)
        return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")
    except Exception,e:
        print "import department%s"%e
        cc=u"%s"%_("department's data imported failed")
        return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
#		return HttpResponse(content="result=1",mimetype='text/plain')#render_to_response("info.html", {"title": _("Import department list"), "content": cc})
#作废
def importFptemp(request):
    if not (request.method == 'POST'):
        return render_to_response("Import_emp.html",{"title": _("Upload fptemp list")
        })
    try:
        imFields=[]
        imFieldsInfo={}
        imDatalist=[]
        sUserids=[]
        i_insert=0
        i_update=0
        i_rep=0
        imFields=request.POST["fields"].split(',')
        for t in imFields:
            try:
                imFieldsInfo[t]=int(request.POST.get(t+"2file","-1"))
            except:
                cc=_("fptemp's data imported failed")+"</p><pre>"
                cc+=request.POST.get(t+"2file","-1")
                return render_to_response("info.html", {"title": _("Import fptemp list"), "content": cc})
        f=request.FILES["fileUpload"]
        data=""
        fName=f.name
        whatrow=request.POST["whatrowid2file"]
        #ext=fName[fName.find('.')+1:].upper()
        ext=''
        fl=fName.split('.')
        if fl:
            ext=fl[-1].upper()
        if ext=='XLSX':ext='XLS'
        for chunk in f.chunks():
            data+=chunk
        lines = []
        if ext=='TXT' or ext=='CSV':
            lines=data.splitlines()
        elif ext=='XLS' or ext=='XLSX':
            import xlrd
#			fn="%s/%s"%(tmpDir(),fName)
            fName=fName.encode("gb2312")
            fn="%s/%s"%(tmpDir(),fName)
            f=file(fn, "wb")
            try:
                f.write(data)
            except:
                pass
            f.close()
            bk = xlrd.open_workbook(fn)
            sheetNames=bk.sheet_names()
            if not sheetNames:
                cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            shxrange = range(bk.nsheets)
            try:
                sh = bk.sheet_by_index(0)
            except:
                s="no sheet in %s named %s" %(fn,sheetNames[0])
                cc=u"%s,%s"%(_('imported failed'),s)
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            nrows = sh.nrows
            ncols = sh.ncols
            for i in range(0,nrows):
                sv=[]
                for sr in sh.row_values(i):
                    if type(sr)==type(1.0):
                        sr=str(long(sr))
                        if sr.find(".0")!='-1':
                            sr=sr.split(".")[0]
                        else:
                            sr=sr
                    sv.append(sr)
#				row_data = sh.row_values(i)
                row_data = sv
                lines.append(row_data)
        jjj=0
        iCount=0
        sqlList=[]
        r=0
        for t in lines:
            r+=1
            if int(whatrow)>r:
                continue
            dDict={}
            if ext=="TXT":
                ls=t.split('\t')
            elif ext=="CSV":
                ls=t.split(',')
            else:
                ls=t
            for k,v in imFieldsInfo.items():
                try:
                    if v<1 or v>10:
                        continue
                except:
                    continue
                if k.lower()=='userid':
                    if ls[v-1]=='':
                        dDict={}
                        break
                if v<=len(ls):
                    if ext=='XLS' or ext=='XLSX':
                        dDict[k]=ls[int(v)-1]
                    else:
                        dDict[k]=getStr_c_decode(ls[int(v)-1])
            if dDict!={}:
#				imDatalist.append(dDict.copy())	
                jjj+=1
                try:
                    e=employee.objByPIN(dDict['badgenumber'])
                except:
                    e=None
                if e:
                    fingerid=int(dDict['FingerID'])
                    try:
                        f=fptemp.objects.get(UserID=e.id, FingerID=fingerid)
                    except:
                        f=None
                    sql=''
                    if f:
                        i_update+=1
                        sql="update template set template = '%s'  where userid=%s and fingerid=%s" % (dDict['Template'],  e.id, fingerid)
                    else:
                        i_insert+=1
                        sql = getSQL_insert("template", UserID=e.id, FingerID=fingerid,Template=dDict['Template'],Valid=1,DelTag=0,AlgVer=10)

                    if sql:
                        customSqlEx(sql)

        result=reportError(u"%s"%_("fptemp information"), jjj, i_insert, i_update, i_rep, [])
        adminLog(time=datetime.datetime.now(),User=request.user, action=u'%s'%_(u"Import"),model = BioData._meta.verbose_name,object = request.META["REMOTE_ADDR"],count = jjj).save(force_insert = True)
        return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")
    except Exception,e:
        print "import template%s"%e
        cc=u"%s"%_("data imported failed")
        return getJSResponse({"ret":1,"message": cc},mtype="text/plain")



#		typedef struct _User_{		//size:72
#			U16 PIN;				//[:2]
#			U8 Privilege;			//[2:3]		Privilege
#			char Password[8];		//[3:11]	Password
#			char Name[24];			//[11:35]	EName
#			U8 Card[4];				//[35:39]					//卡号码，用于存储对应的ID卡的号码
#			U8 Group;				//[39:40]	AccGroup		//用户所属的分组
#			U16 TimeZones[4];		//[40:48]	TimeZones		//用户可用的时间段，位标志
#			char PIN2[24];			//[48:]		PIN
#		}GCC_PACKED TUser, *PUser;			

def importBiodata(request):
    if not (request.method == 'POST'):
        return render_to_response("Import_emp.html",{"title": _("Upload fptemp list")
        })
    try:
        imFields=[]
        imFieldsInfo={}
        imDatalist=[]
        sUserids=[]
        i_insert=0
        i_update=0
        i_rep=0
        imFields=request.POST["fields"].split(',')
        for t in imFields:
            try:
                imFieldsInfo[t]=int(request.POST.get(t+"2file","-1"))
            except:
                cc=_("fptemp's data imported failed")+"</p><pre>"
                cc+=request.POST.get(t+"2file","-1")
                return render_to_response("info.html", {"title": _("Import fptemp list"), "content": cc})
        f=request.FILES["fileUpload"]
        data=""
        fName=f.name
        whatrow=request.POST["whatrowid2file"]
        #ext=fName[fName.find('.')+1:].upper()
        ext=''
        fl=fName.split('.')
        if fl:
            ext=fl[-1].upper()
        if ext=='XLSX':ext='XLS'
        for chunk in f.chunks():
            data+=chunk
        lines = []
        if ext=='TXT' or ext=='CSV':
            lines=data.splitlines()
        elif ext=='XLS' or ext=='XLSX':
            import xlrd
#			fn="%s/%s"%(tmpDir(),fName)
            fName=fName.encode("gb2312")
            fn="%s/%s"%(tmpDir(),fName)
            f=file(fn, "wb")
            try:
                f.write(data)
            except:
                pass
            f.close()
            bk = xlrd.open_workbook(fn)
            sheetNames=bk.sheet_names()
            if not sheetNames:
                cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            shxrange = range(bk.nsheets)
            try:
                sh = bk.sheet_by_index(0)
            except:
                s="no sheet in %s named %s" %(fn,sheetNames[0])
                cc=u"%s,%s"%(_('imported failed'),s)
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            nrows = sh.nrows
            ncols = sh.ncols
            for i in range(0,nrows):
                sv=[]
                for sr in sh.row_values(i):
                    if type(sr)==type(1.0):
                        sr=str(long(sr))
                        if sr.find(".0")!='-1':
                            sr=sr.split(".")[0]
                        else:
                            sr=sr
                    sv.append(sr)
#				row_data = sh.row_values(i)
                row_data = sv
                lines.append(row_data)
        jjj=0
        iCount=0
        sqlList=[]
        r=0

        new_lines = []
        face_dict = {}
        bio_type = request.POST.get('BioType',None)
        for t in lines:
            r+=1
            if int(whatrow)>r:
                continue
            dDict={}
            if ext=="TXT":
                ls=t.split('\t')
            elif ext=="CSV":
                ls=t.split(',')
            else:
                ls=t
            for k,v in imFieldsInfo.items():
                try:
                    if v<1 or v>10:
                        continue
                except:
                    continue
                if k.lower()=='userid':
                    if ls[v-1]=='':
                        dDict={}
                        break
                if v<=len(ls):
                    if ext=='XLS' or ext=='XLSX':
                        dDict[k]=ls[int(v)-1]
                    else:
                        dDict[k]=getStr_c_decode(ls[int(v)-1])
            new_lines.append(dDict)

        if bio_type == '2':
            #将多条数据合并为一条
            tmp_dict = {}
            for line in new_lines:
                pin = line['badgenumber']
                if not tmp_dict.has_key(pin):
                    tmp_dict[pin] = {
                                    'badgenumber':pin,
                                    'majorver':line['majorver'],
                                    'bio_tmp':{
                                        line['bio_index']:line['bio_tmp']
                                    }
                                }
                else:
                    tmp_dict[pin]['bio_tmp'].update({
                                        line['bio_index']:line['bio_tmp']
                                        })
            new_lines = []
            for k,v in tmp_dict.items():
                new_lines.append(v)

        for dDict in new_lines:
            if dDict!={}:
#				imDatalist.append(dDict.copy())	
                jjj+=1
                try:
                    e=employee.objByPIN(dDict['badgenumber'])
                except:
                    e=None
                if e:
                    majorver = dDict['majorver']
                    try:
                        from models import BioData
                        if bio_type != '2':
                            bio_index=int(dDict['bio_index'])
                            f=BioData.objects.get(UserID=e.id, bio_index=bio_index,bio_type=bio_type,majorver=majorver)
                        else:
                            f=BioData.objects.get(UserID=e.id,bio_type=bio_type,majorver=majorver)
                    except:
                        f=None
                    sql=''
                    utime=str(datetime.datetime.now())[:10]
                    if bio_type !='2':
                        if f:
                            i_update+=1
                            sql="update bio_data set bio_tmp = '%s',set UTime='%s'  where userid=%s and bio_index=%s" % (dDict['bio_tmp'],utime,  e.id, bio_index)
                        else:
                            i_insert+=1
                            sql = getSQL_insert("bio_data", UserID=e.id, bio_index=bio_index,bio_tmp=dDict['bio_tmp'],bio_no=bio_index,bio_type=bio_type,Valid=1,majorver=majorver,duress=0,UTime=utime)
                    else:
                        if f:
                            i_update+=1
                            sql="update bio_data set bio_tmp = '%s',set UTime='%s'  where userid=%s" % (dDict['bio_tmp'],utime,  e.id)
                        else:
                            i_insert+=1
                            sql = getSQL_insert("bio_data", UserID=e.id,bio_tmp=str(dDict['bio_tmp']).replace('\'','\"'),bio_type=bio_type,Valid=1,majorver=majorver,duress=0,UTime=utime)
                    if sql:
                        customSqlEx(sql)

        result=reportError(u"%s"%_(u"导入特征模板信息"), jjj, i_insert, i_update, i_rep, [])#result=reportError(u"%s"%_("template information"), jjj, i_insert, i_update, i_rep, [])
        adminLog(time = datetime.datetime.now(), User = request.user, action = u'%s' % _(u"Import"),
                 model = BioData._meta.verbose_name, object = request.META["REMOTE_ADDR"], count = jjj).save(force_insert = True)
        return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")
    except Exception,e:
        import traceback;traceback.print_exc()
        print "import template%s"%e
        cc=u"%s"%_("data imported failed")
        return getJSResponse({"ret":1,"message": cc},mtype="text/plain")

#导入U盘数据
def upload_data(request):	# 上传导出到U盘的数据
    import struct
    emps=[]
    result = ""
    sqlList=[]
    sn = request.POST.get("SN","")
    device=getDevice(sn)
    if not device:
        return getJSResponse({"ret":1,"message":u"%s"%_("Not specified a target")})
    fs = request.FILES
    pin_pin2 = {}
    errorRecs=[]
    i_insert, i_update, i_rep = 0, 0, 0
    adminLog(time=datetime.datetime.now(),User=request.user, action=u"%s"%_(u"Import U-disk data files"),object = request.META["REMOTE_ADDR"]).save(force_insert = True)
    pin_pin2={}
    if fs.has_key("file_user"): # 用户信息
        try:
            dept = getDefaultDept()	# 默认部门
            f = fs["file_user"]
            data=""
            for chunk in f.chunks():
                data+=chunk
            upload_user=data
            i, count = 0, int(len(upload_user) / 72)
            if not (count>0 and count*72==len(upload_user)):
                raise Exception()
            i_insert, i_update, i_rep = 0, 0, 0
            errorRecs=[]
            while i < count:
                l=()
                buf = upload_user[i*72:(i+1)*72]
                try:
                    fmt="HB8s24s4sB8x24s"
                    l=struct.unpack(fmt,buf)
                except Exception,e:
                    print "---------%s"%e
                i+=1
                card=buf[35:39]
                card="%02X%02X%02X%02X"%(ord(buf[38]),ord(buf[37]),ord(buf[36]),ord(buf[35]))
                card=str(int(card,16))
                if not l:continue
                pin0=l[0]
                pin=formatPIN(getStr_c_decode(l[6]))    #考勤号码
                if pin in settings.DISABLED_PINS or (not pin.isdigit()):
                    continue
                priv=l[1]
                passwd=getStr_c_decode(l[2])
                ename=l[3]
                grp=l[5]
                fldNames=[]
                values=[]
                pin_pin2[pin0]=pin     #记住pin和pin2的对应,为后续的导入指纹使用
                if ename:
                    ename=getStr_c_decode(ename)
                emp=employee.objects.filter(PIN=pin)
                if emp:
                    e=emp[0]
                    if ename and (ename!=e.EName):
                        fldNames.append('name')
                        values.append(ename)
                    if passwd and (passwd!=e.MVerifyPass):
                        fldNames.append('MVerifyPass')      #考勤密码
                        values.append(passwd)
                    if (priv!=e.Privilege):
                        if (not (priv==0) and (e.Privilege==None)):
                            fldNames.append('privilege')
                            values.append(priv)
                    if card and card!=e.Card:
                        fldNames.append('Card')
                        values.append(card)
    #				if int(agrp)!=e.AccGroup:
    #					fldNames.append('AccGroup')
    #					values.append(agrp)
                    if len(fldNames)>0: #有更新的用户信息
                        sql="update userinfo set %s where badgenumber='%s'"%(','.join([u"%s=%s"%(fldNames[p],'%s') for p in range(len(fldNames))]), pin)
                    else:
                        sql=''
                        i_rep+=1
                    if sql:
                        customSqlEx(sql,values)
                        cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,pin))
                        cache.delete("%s_iclock_emp_%s"%(settings.UNIT,e.id))
                        i_update+=1
                else:
                    sql = getSQL_insert("userinfo", BadgeNumber = pin, defaultdeptid = dept.DeptID, OffDuty=0, DelTag=0,
                        Name = ename,Card=card, MVerifyPass = passwd,privilege=priv,ATT=1,OverTime=1,Holiday=1)
                    customSqlEx(sql)
                    i_insert+=1
            result+=reportError(u"%s"%_("user information"), i, i_insert, i_update, i_rep, errorRecs)
        except:
            return getJSResponse({"ret":1,"message":u"%s"%_("Employee information does not match the data, select the correct employee information data file")})
    if fs.has_key("file_fptemp"): # 指纹模版
        try:
            if not pin_pin2:
                return getJSResponse({"ret":1,"message":u"%s"%_('No User data file')},mtype="text/plain")
            errorRecs=[]
            fp = fs["file_fptemp"]
            data=""
            for chunk in fp.chunks():
                data+=chunk
            upload_fptemp=data
            #fsn,upload_fptemp,sum=checkRecData(data,1024)
            #i, count = 0, round(len(upload_fptemp) / 1024)
            #if not (count>0 and ord(upload_fptemp[6])==0xA1 and ord(upload_fptemp[7])==0xCA ):
            #	raise Exception()
            #if not pin_pin2:
            #	return render_to_response("info.html", {"title": _("fail "),
             #                       "content": _("<h1> Data upload failure </ h1>, <br /> If the fingerprint template to upload, please also upload their associated user information!") });
            i_insert, i_update, i_rep = 0, 0, 0
            s=0
            while len(upload_fptemp)>0:
                sizebuf=upload_fptemp[:2]
                fmt="H"
                size_t=struct.unpack(fmt,sizebuf)
                size=size_t[0]
                fpsize=size-6
                buf=upload_fptemp[:size]
                try:
                    fmt="HHBB%ds"%fpsize
                    l=struct.unpack(fmt,buf)
                except Exception,e:
                    print "---------%s"%e
                upload_fptemp=upload_fptemp[size:]
                s+=1
                pin0=l[1]
                try:
                    pin=pin_pin2[pin0]
                except:
                    continue
                fingerid=l[2]
                valid=l[3]
                try:
                    e=employee.objByPIN(pin)
                except:
                    e=None
                if not e:continue          #如果人员不存在不保存指纹
                fpbuf=getFptemp_c(l[4])
                fptemplate=fpbuf.encode("base64").replace("\n","").replace("\r","")
                try:
                    fp=fptemp.objects.get(UserID=e.id, FingerID = fingerid)
                except:
                    fp=None
                sql=''
                if fp:
                    if not (fp.Template[:100]==fptemplate[:100]):
                        fp.Template=fptemplate
                        fp.save()
                        i_update+=1
                    else:
                        i_rep+=1
                else:
                    sql = getSQL_insert("template", UserID=e.id, Template = fptemplate, FingerID = fingerid, Valid = valid)
                if sql:
                    customSql(sql)
                    i_insert+=1

            result+=reportError(u"%s"%_("Fingerprint template"), s, i_insert, i_update, i_rep, errorRecs)
        except Exception,e:
            print "fptemp===%s"%e
#			errorLog(request)
#			info=_('Upload data files!')
            return getJSResponse({"ret":1,"message":(u"<h1>%s"%_('Data Import Results'))+"</h1><br />"+u"%s"%(result,)+(u"<br /><h1>%s"%_('Data Import failure'))+u"</h1><br /><br />%s"%_("Fingerprint template does not match the data or data file is empty, please select the correct <b>fingerprint template </b> data file!")},mtype="text/plain")
                                  #return getJSResponse({"ret":1,"message":info})
            #return getJSResponse({"ret":0,"message":"Upload data success"})
            #return render_to_response("info.html", {"title": _("Import data"),
            #		"content": _("<h1>Upload data success</h1><br /><br />%(object_name)s<br /><h1>Data Import failure</h1><br /><br />Fingerprint template does not match the data or data file is empty, please select the correct <b>fingerprint template </b>data files" )% {'object_name':result,}});


    if fs.has_key("file_facetemp"): # 面部模版
        try:
            if not pin_pin2:
                return getJSResponse({"ret":1,"message":u"%s"%_('No User data file')},mtype="text/plain")
            errorRecs=[]
            fp = fs["file_facetemp"]
            data=""
            for chunk in fp.chunks():
                data+=chunk
            upload_facetemp=data
            i_insert, i_update, i_rep = 0, 0, 0
            s=0
            while len(upload_facetemp)>0:
                structsize=2576
                face_tmp_maxsize=2560
                buf=upload_facetemp[:structsize]
                buftemp=buf
                try:
                    fmt="HHBBHII%ds"%(face_tmp_maxsize)
                    l=struct.unpack(fmt,buf)
                except Exception,e:
                    print "---------%s"%e
                upload_facetemp=upload_facetemp[structsize:]
                s+=1
                pin0=l[1]
                try:
                    pin=pin_pin2[pin0]
                except:
                    continue
                faceid=l[2]
                valid=l[3]
                algver=l[4]
                utime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    e=employee.objByPIN(pin)
                except:
                    e=None
                if not e:continue          #如果人员不存在不保存面部
                fpbuf=buftemp[15:1230]
                fptemplate=fpbuf.encode("base64").replace("\n","").replace("\r","")
                fptemplate="AAAAAAAAAAAAAAAAAAAA%sAAAAAAAA"%fptemplate
                try:
                    fp=facetemp.objects.get(UserID=e.id, FaceID = faceid)
                except:
                    fp=None
                sql=''
                if fp:
                    if not (fp.Template[:100]==fptemplate[:100]):
                        fp.Template=fptemplate
                        fp.save()
                        i_update+=1
                    else:
                        i_rep+=1
                else:
                    sql = getSQL_insert("facetemplate", UserID=e.id, Template = fptemplate,FaceID = faceid, Valid = valid, SN=sn,UTime=utime, AlgVer=algver)
                if sql:
                    customSql(sql)
                    i_insert+=1

            result+=reportError(u"%s"%_("Face template"), s, i_insert, i_update, i_rep, errorRecs)
        except Exception,e:
            print "facetemp===%s"%e
            return getJSResponse({"ret":1,"message":(u"<h1>%s"%_('Data Import Results'))+"</h1><br />"+u"%s"%(result,)+(u"<br /><h1>%s"%_('Data Import failure'))+u"</h1><br /><br />%s"%_("Face template does not match the data or data file is empty, please select the correct <b>face template </b> data file!")},mtype="text/plain")




    if fs.has_key("file_transaction"): # 考勤记录
        try:
            f = fs["file_transaction"]
            data=""
            for chunk in f.chunks():
                data+=chunk
            #fsn,upload_transaction,sum=checkALogData(data)
            arr = data.split("\n")
            i, count = 0, len(data) / 32
            i, i_insert,i_rep,i_update = 0, 0,0,0
            errorRecs=[]
            maxtime=(datetime.datetime.now()+datetime.timedelta(1, 0, 0)).strftime("%Y-%m-%d %H:%M:%S")
            for row in arr:
                if row=="": continue
                arr_row = row.split("\t")
                i += 1
                pin=formatPIN(arr_row[0].strip())
                time=arr_row[1]
                if pin.isdigit() and (len(time) in [19,16]) and (maxtime>time) and (not pin in settings.DISABLED_PINS):
                    try:
                        e=employee.objByPIN(pin)    #目的是如果导入的考勤记录中考勤号码在人员信息不存在不进行导入,要求必须先导入人员才能导入记录
                    except:
                        e=None
                        errorRecs.append(row)
                    if e:
                        sql = getSQL_insert("checkinout", userid=e.id, checktime=time, SN=sn,
                            checktype=arr_row[3], verifycode =arr_row[2])
                        try:
                            if customSqlEx(sql):
                                i_insert += 1
                        except Exception, e:
                            estr="%s"%e
                            if ('IntegrityError' in estr) or ("UNIQUE KEY" in estr) or ("are not unique" in estr) or ("Duplicate entry" in estr) or ("unique constraint" in estr):
                                i_rep+=1
                            else:
                                errorRecs.append(row)

                else:
                    errorRecs.append(row)
            result+=reportError(_("Transactions"), i, i_insert,i_update, i_rep, errorRecs)
        except:
            return getJSResponse({"ret":1,"message":(u"<h1>%s"%_('Data Import Results'))+"</h1><br />"+u"%s"%(result,)+(u"<br /><h1>%s"%_('Data Import failure'))+u"</h1><br /><br />%s"%_("Transactions does not match data, Please select the correct <b>transaction</b> data file!")},mtype="text/plain")
            #return render_to_response("info.html", {"title": _("Import data"),
            #		"content": (u"<h1>%s"%_('Data Import Results'))+"</h1><br /><br />"+u"%s"%(result,)+(u"<br /><h1>%s"%_('Data Import failure'))+u"</h1><br /><br />%s"%_("Transactions does not match data, Please select the correct <b>transaction</b> data file!")});


    if fs.has_key("file_transpic"): # 考勤记录照片
        try:
            f = fs["file_transpic"]
            request.user.iclock_url_rel='../..'
            from mysite.iclock.datamisc import saveUploadTranspic
            fname="%s%s%s/%s"%(settings.ADDITION_FILE_ROOT,'upload/temp_transpic/',sn, f)
            saveUploadTranspic(request, "file_transpic", fname)
        except Exception,e:
            print 'EEEEEEEEEE',e

    return getJSResponse({"ret":0,"message": u"<h1>%s</h1>%s"%(_('Data Import Results'),result)},mtype="text/plain")


@login_required
def app_emp(request):
    if not (request.method == 'POST'):
        return render_to_response("disp_emp.html",{"title": _("Upload employee list"), # u"批量上传人员列表",
                'task':'userinfo'})
    i=0;
    f=request.FILES["fileUpload"]
    data=""
    for chunk in f.chunks(): data+=chunk
    lines=data.splitlines()
    pin,ename,pwd,card,grp,tzs='','','','','1',''
    userTmp=[]
    for line in lines:
#		try:
        if line.find('[Users_')==0:
            i+=1
            if(len(pin)>0):
                saveUser(pin, pwd, ename, card, grp, tzs)
                for tmp in userTmp:
                    saveFTmp(pin, tmp['fid'], tmp['tmp'])
            pin=line[7:-1]
            ename,pwd,card,grp,tzs='','','','1',''
            userTmp=[]
        elif line.find('Name=')==0: ename=line[5:]
        elif line.find('Password=')==0: pwd=line[9:]
        elif line.find('AccTZ1=')==0: tzs=line[7:]
        elif line.find('Card=')==0: card=line[5:]
        elif line.find('Grp=')==0: grp=line[4:]
        elif line.find('FPT_')==0:
            ftmp=line.split('=')
            fid=ftmp[0][4:]
            userTmp.append({"fid":fid, "tmp":ftmp[1]})
#		except  Exception, e:
#			errorLines.append("LINE(%d):%s :%s"%(i,str(e),line))
    if(len(pin)>0):
        saveUser(pin, pwd, ename, card, grp, tzs)
        for tmp in userTmp:
            saveFTmp(pin, tmp['fid'], tmp['tmp'])
    response = HttpResponse(content_type='text/plain')
    #response.write(gettext("%(object)s employee has been successfully!")%{'object':i});
    return response


@login_required
def del_emp_log(request):
    pass
    #return render_to_response("disp_emp_log.html",{"title": gettext("Delete the employee(s) in device"), 'task':'deleteuser'})

@login_required
def upgrade(request):
    if not (request.method == 'POST'):
        return render_to_response("upgrade.html",{"title": gettext("Server upgrades")})
    i=0;
    f=request.FILES["fileUpload"]
    bytes=""
    for chunk in f.chunks(): bytes+=chunk
    target=tmpDir()+"/mysite.zip"
    bkFile="%s/%s.zip"%(tmpDir(),time.strftime("%Y%m%d%H%M%S"))
    file(target,"wb+").write(bytes)
    zipDir('c:/mysite/', bkFile)
    fl=unzipFile(target, 'c:/')
    response = HttpResponse(content_type='text/plain')
    response.write("BACKUP OLD FILE TO: "+bkFile+"\r\n"+("\r\n".join([("%s\t%s"%(fl[f], f)) for f in fl.keys()])));
    if fl:
        restartThread("iclock-server").start()
        restartThread("iclock").start()
        restartThread("Apache2").start()
    return response

from gzip import *
def getGZipSize(fname):
    g=GzipFile(filename=fname, mode="rb")
    s=0
    while True:
        chunk=g.read(1024)
        cs=len(chunk)
        if cs>0:
            s+=cs
        else:
            break
    return s


@login_required
def restartDev(request):
    ip=request.GET.get("IP","")
    if ip:
        url, fname=getFW(iclock(Style="X938"))
        fwSize=getGZipSize(fname)
        ret=reb.tryDoInDev(ip,["ls /mnt/mtdblock/main -l","reboot"])
        if type(ret).__doc__.find("list")==0:
#			if ret[0].find(" %s"%fwSize)<10:
#				ret=reb.tryDoInDev(ip,["cd /mnt/mtdblock/","wget http://192.168.1.254/iclock/file/fw/X938/main.gz","reboot"])
            ret=gettext("Restart device successfully: ")+ip+"</p><p>"+(ret[0].find(" %s"%fwSize)<10 and ret[0]+"</p><p>"+gettext("Its size and standard firmware(%(object_name)s) is inconsistent, Need to upgrade firmware If there is no automatic inspection later firmware update, or manually upgrade firmware")%{'object_name':fwSize or ""})
        else:
            ret=gettext("Failure to restart device:")+ip+"</p><p>"+ret
    else:
        ret=_("Please enter the IP address of the device")
    return render_to_response("info.html",{"title": _("Restart device"), 'content': ret})

@login_required
def autoRestartDev(request):
    iclocks=iclock.objects.filter(LastActivity__lt=datetime.datetime.now()-datetime.timedelta(0,(settings.REBOOT_CHECKTIME>30 and settings.REBOOT_CHECKTIME or 30)*60)).filter(Q(DelTag__isnull=True)|Q(DelTag=0))
    ips=updateLastReboot(iclocks)
    rebDevsReal(ips)
    return render_to_response("info.html",{"title": _("Automatically check sluggish device"), 'content':gettext("The device(s) does not connect with the server more than half and an hour: </p><p>")+("<br />".join([u"%s: %s"%(i, i.IPAddress()) for i in iclocks]))+"</p><p>&nbsp;</p><p>"+(ips and gettext("The system will connect and re-start the following device automaticly: </p><p>")+("<br />".join(ips)) or "")})



@login_required
def importIclock(request):
    try:
        imFields=['SN','DeptID']
        imFieldsInfo={}
        imDatalist=[]
        sUserids=[]
        oriFields=request.POST["fields"].split(',')
        fromline=request.POST.get("rowid2","1")
        if fromline=="":
            fromline=1
        fromline=int(fromline)
        for t in oriFields:
            fldName=request.POST.get(t,"")
            if fldName=='on':
                imFields.append(t)
        maxCol=0
        for t in imFields:
            try:
                imFieldsInfo[t]=int(request.POST.get(t+"2file","-1"))
                if maxCol<imFieldsInfo[t]:maxCol=imFieldsInfo[t]
            except:
                cc=_(u"导入设备失败")+"</p><pre>"
                #cc+=request.POST.get(t+"2file","-1")
                return render_to_response("info.html", {"title": _(u"设备列表"), "content": ""})
        f=request.FILES["fileUpload"]
        data=""
        fName=f.name
        whatrow=request.POST["whatrowid2file"]
        #ext=fName[fName.find('.')+1:].upper()[:3]
        ext=''
        fl=fName.split('.')
        if fl:
            ext=fl[-1].upper()
        if ext=='XLSX':ext='XLS'
        lines=[]
        for chunk in f.chunks(): data+=chunk
        if ext=='TXT' or ext=='CSV':
            lines=data.splitlines()
        elif ext=='XLS' or ext=='XLSX':
            import xlrd
            fName=safe_unicode(fName,"GB18030")#fName.encode("gb2312")#修改导入文件名称为中文报错问题
            fn="%s/%s"%(tmpDir(),fName)
            f=file(fn, "wb")
            try:
                f.write(data)
            except:
                pass
            f.close()
            bk = xlrd.open_workbook(fn)
            sheetNames=bk.sheet_names()
            if not sheetNames:
                cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            shxrange = range(bk.nsheets)
            try:
                sh = bk.sheet_by_index(0)
            except:
                s="no sheet in %s named %s" %(fn,sheetNames[0])
                cc=u"%s,%s"%(_('imported failed'),s)
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            nrows = sh.nrows
            ncols = sh.ncols
            for i in range(0,nrows):
                sv=[]
                c=0
                for sr in sh.row_values(i):
                    if type(sr)==type(1.0):
                        sr=str(long(sr))
                        if sr.find(".0")!='-1':
                            sr=sr.split(".")[0]
                        else:
                            sr=sr
                    sv.append(sr)
                    c=c+1
                    if c>maxCol-1:break
                row_data = sv
                lines.append(row_data)
        jjj=0
        jj=0
        iCount=len(lines)          #import users count
        i_insert=0
        i_update=0
        i_rep=0
        errorRec=[]
        now=datetime.datetime.now()
        #adminLog(time=now,User=request.user, action=u"导入设备数据").save()
        sqlList=[]
        stoptag=0
        r=0
        for t in lines:
            r+=1
            if int(whatrow)>r:
                continue
            jj+=1
            if jj<fromline:continue
            dDict={}
            if ext=="TXT":
                ls=t.split('\t')
            elif ext=='CSV':
                ls=t.split(',')
            elif ext=='XLS' or ext=='XLSX':
                ls=t
            for k,v in imFieldsInfo.items():
                try:
                    if v<1 or v>100:
                        continue
                except:
                    continue
                v=int(v)
                try:
                    ls[v-1]=ls[v-1].strip()
                except:
                    pass
                if k=='SN' and ls[v-1]=='':
                    stoptag=1
                    break
                if k=='SN' and (len(ls[v-1])<10 or len(ls[v-1])>15):
                    errorRec.append(ls[v-1])
                    dDict={}
                    iclockDeptDict={}
                    break
                    #sUserids.append(ls[v-1])
                if k=='DeptID':
                    iclockDeptDict={}
                    dt=department.objByNumber(ls[int(v)-1])
                    if dt:
                        iclockDeptDict['dept_id']=dt.DeptID
                    else:
                        cc=u"导入失败,请查看第%s行数据,未填写授权部门"%r
                        return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                    continue
                if k=='Alias':
                    ls[int(v)-1]=ls[int(v)-1][:20]
                if v<=len(ls):
                    s=ls[int(v)-1]
                    if ext=='XLS' or ext=='XLSX':
                        dDict[k]=s
                    else:
                        dDict[k]=getStr_c_decode(s)

            if stoptag==1:
                break

            if dDict:
                #dept=department.objByNumber(dDict['SN'])
                #if dept:
                #	if not dDict.has_key('Alias'):
                #		dDict['Alias']=department.objByNumber(dDict['SN']).DeptName
                #else:
                #	dDict['DeptID']=1
                #	if not dDict.has_key('Alias'):
                #		dDict['Alias']=department.objByID('1').DeptName
                jjj+=1
                try:
                    ClockSN = getDevice(dDict['SN'])
                except:
                    ClockSN = None
                SN=dDict['SN']
                if ClockSN:
                    dDict['whereSN']=dDict['SN']

                    dDict['DelTag']=0
                    #cache.delete("iclock_"+dDict['SN'])
                    del dDict['SN']
                    sql,params=getSQL_update_new('iclock',dDict)
                    if customSqlEx(sql,params):
                        i_update+=1
                    cache.delete("iclock_"+dDict['whereSN'])
                else:
                    dDict['TransInterval']=1
                    dDict['AlgVer']='10'
                    dDict['TZAdj']=8
                    dDict['State']=1
                    dDict['UpdateDB']='1111100000'
                    dDict['AccFun']=0
                    dDict['DelTag']=0
                    dDict['LogStamp']=0
                    dDict['OpLogStamp']=0
                    dDict['PhotoStamp']=0
                    dDict['Authentication']=1
                    dDict['ProductType']=9
                    #dDict['saveStamp']=datetime.datetime.now()
                    #dDict['Purpose']=9
                    dDict['isUSERPIC']=0
                    dDict['isFptemp']=1
                    dDict['isFace']=0

                    dDict['is_add']=0
                    dDict['is_zeor']=0
                    dDict['is_OK']=0

                    dDict['check_black_list']=0
                    dDict['check_white_list']=1
                    dDict['is_cons_keap']=0
                    dDict['is_cons_keap']=0
                    dDict['is_check_operate']=0

                    #dDict['wlan']=0
                    sql,params=getSQL_insert_new('iclock',dDict)
                    if customSqlEx(sql,params):
                        i_insert+=1
                    #dev=iclock.objects.get(SN=dDict['SN'])
                    #cache.set("iclock_"+dDict['SN'], dev)
            if iclockDeptDict:
                iclockDeptDict['SN_id']=SN
                iclockDeptDict['iscascadecheck']=0
                sql,params=getSQL_insert_new('iclock_iclockdept',iclockDeptDict)
                try:
                    ic=iclock.objects.all().exclude(DelTag=1).count()
                    if ic>=settings.MAX_DEVICES:
                        return getJSResponse({"ret":0,"message": u"%s"%(u'超过系统规定的设备数!')},mtype="text/plain")



                    customSqlEx(sql,params)
                except Exception,e:
                    pass
        result=reportError(u"%s"%_("Data Import Results"), jjj, i_insert, i_update, i_rep, errorRec)
        adminLog(time = datetime.datetime.now(), User = request.user, action = u'%s' % _(u"Import"),
                 model = iclock._meta.verbose_name, object = request.META["REMOTE_ADDR"], count = jjj).save(force_insert = True)#
        return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")
    except Exception,e:
        print "importIclock====",e
        cc=""#u"<h1>%s</h1><br/>%s"%(_("导入设备"),_("导入设备数据失败"))+"</p><pre>"
        return getJSResponse({"ret":1,"message": cc},mtype="text/plain")


def importschclasstmpShift(request):
    try:
        imFields=[]
        imFieldsInfo={'pin','name','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31'}
        imDatalist=[]
        sUserids=[]
        i_insert=0
        i_update=0
        i_rep=0
        f=request.FILES["fileUpload"]
        data=""
        fName=f.name
        whatrow=request.POST["whatrowid2file"]
        year=int(request.POST["year2file"])
        month=int(request.POST["month2file"])
        #ext=fName[fName.find('.')+1:].upper()
        ext=''
        fl=fName.split('.')
        if fl:
            ext=fl[-1].upper()
        for chunk in f.chunks():
            data+=chunk
        lines = []
        if ext=='TXT' or ext=='CSV':
            lines=data.splitlines()
        elif ext=='XLS' or ext=='XLSX':
            import xlrd
#			fn="%s/%s"%(tmpDir(),fName)
            fName=fName.encode("gb2312")
            fn="%s/%s"%(tmpDir(),fName)
            f=file(fn, "wb")
            try:
                f.write(data)
            except:
                pass
            f.close()
            bk = xlrd.open_workbook(fn)
            sheetNames=bk.sheet_names()
            if not sheetNames:
                cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            shxrange = range(bk.nsheets)
            try:
                sh = bk.sheet_by_index(0)
            except:
                s="no sheet in %s named %s" %(fn,sheetNames[0])
                cc=u"%s,%s"%(_('imported failed'),s)
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            nrows = sh.nrows
            ncols = sh.ncols
            for i in range(0,nrows):
                sv=[]
                for sr in sh.row_values(i):
                    if type(sr)==type(1.0):
                        sr=str(sr)
                        if sr.index(".0")!='-1':
                            sr=sr.split(".")[0]
                        else:
                            sr=sr
                    sv.append(sr)
#				row_data = sh.row_values(i)
                row_data = sv
                lines.append(row_data)
        jjj=0
        iCount=0
        sqlList=[]
        r=0
        time=datetime.datetime.now()
        time=datetime.datetime.strftime(time,'%Y-%m-%d %H:%M:%S')
        #d1="%s-%s-%s"%(year,month,1)
#		d1=datetime.datetime.strptime(d1,'%Y-%m-%d')
        d1=datetime.datetime(int(year),int(month),1,0,0,0)
        d2=d1+datetime.timedelta(days=32)
        d2=datetime.datetime(d2.year,d2.month,1,0,0,0)-datetime.timedelta(days=1)
        first_name=request.user.first_name
        for t in lines:
            r+=1
            if int(whatrow)>r:
                continue
            dDict={}
            if ext=="TXT":
                ls=t.split('\t')
            elif ext=="CSV":
                ls=t.split(',')
            else:
                ls=t
            for k in imFieldsInfo:
                if k.lower()=='name':continue
                if k.lower()=='pin':
                    if ls[0]=='':
                        dDict={}
                        break
                    else:
                        try:
                            pin=str(ls[0]).split(".")[0]
                            pin=formatPIN(pin)
                            userid=employee.objByPIN(pin)
                            #userid=userid.id
                            dDict['userid']=userid
                        except:
                            dDict={}
                            s=u"人员编号为%s的不存在" %(pin)
                            cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
                            return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                else:
                    try:
                        k=int(k)
                        monthRange = calendar.monthrange(year,month)
                        if k>monthRange[1]:continue

                        checktime="%s-%s-%s"%(year,month,k)
                        #dDict['datetime']=checktime
                        k=k+1
                        if ext=='XLS' or ext=='XLSX':
                            dDict[checktime]=ls[k].split(".")[0]
                        else:
                            dDict[checktime]=getStr_c_decode(ls[k]).split(".")[0]
                    except:
                        pass
            if dDict!={}:
                jjj+=1
                emp=dDict['userid']
                i=emp.id


                deleteCalcLog(UserID=int(i),StartDate=d1,EndDate=d2)
                deleteUserShifts(uid=i,startdate=d1,enddate=d2)
                tmp_t = d2 + datetime.timedelta(days=0,hours=23,minutes=59,seconds=0)
                USER_TEMP_SCH.objects.filter(UserID=i,ComeTime__range=(d1, tmp_t)).delete()
                din=0
                for key in dDict.keys():
                    if key !='userid':
                        try:
                            st=datetime.datetime.strptime(key,'%Y-%m-%d')
                            tl=dDict[key]
                            tl=tl.split(",")
                            for t in tl:
                                t=int(t)
                                FTTimeZones=[]
                                UserSchPlan=LoadSchPlan(emp,True,False)
                                SchedulerShifts=GetUserScheduler(emp, st, st,UserSchPlan['HasHoliday'])
                                schClass=FindSchClassByID(t)
                                if schClass:
                                    stime=schClass['TimeZone']['StartTime']
                                    etime=schClass['TimeZone']['EndTime']
                                    NextDay=schClass['NextDay']
                                    tt=datetime.datetime.strptime(key,'%Y-%m-%d')
                                    starttime = datetime.datetime(tt.year,tt.month,tt.day,stime.hour,stime.minute)
                                    endtime = datetime.datetime(tt.year,tt.month,tt.day,etime.hour,etime.minute)+datetime.timedelta(days=NextDay)
                                    if TestTimeZone(FTTimeZones,starttime,endtime):
                                        AddScheduleShift(SchedulerShifts, starttime, endtime,t,0)
                                    sTemp={'StartDate':starttime,'EndDate':endtime,'schclassid':t}
                                    saveEmpScheduleLogToFile('emp_schedule','%s %s %s import'%(dumps(sTemp),request.user,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),emp.pin())

                                    SaveTempSch(i,st,st,SchedulerShifts)
                                else:
                                    s=u"时段编号为%s的可能不存在" %(t)
                                    cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
                                    return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                        except Exception,e:
                            #print 'error=====',e
                            pass
                if din>0:
                    i_update+=1
                else:
                    i_insert+=1
        result=reportError(u"%s"%_(u"导入排班数据"), jjj, i_insert, i_update, i_rep, [])
        #adminLog(time=datetime.datetime.now(),User=request.user, action=u"导入排班").save()
        adminLog(time = datetime.datetime.now(), User = request.user, action = u'%s' % _(u"Import"),
                 model = USER_TEMP_SCH._meta.verbose_name, object = request.META["REMOTE_ADDR"], count = jjj).save(
            force_insert = True)
        return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")
    except Exception,e:
        import traceback;traceback.print_exc()
        cc=u"%s"%_("data imported failed")
        return getJSResponse({"ret":1,"message": cc},mtype="text/plain")


@login_required
def importSpeday(request):
    try:
        leave=[]
        qryLeaveClass=LeaveClass.objects.all().order_by('LeaveID')
        for t in qryLeaveClass:
            r=FetchLeaveClass(t)
            if len(r)>0:
                leave.append(r)
        imFields=['badgenumber','StartSpecDay','EndSpecDay','StartSpecDayTime','EndSpecDayTime','DateID']
        imFieldsInfo={}
        imDatalist=[]
        sUserids=[]

        #clearance_yes=request.POST["clearance_yes"]
        #clearance_no=request.POST["clearance_no"]
        oriFields=request.POST["fields"].split(',')
        fromline=request.POST.get("rowid2","1")
        if fromline=="":
            fromline=1
        fromline=int(fromline)
        for t in oriFields:
            fldName=request.POST.get(t,"")
            if fldName=='on':
                imFields.append(t)

        for t in imFields:
            try:
                imFieldsInfo[t]=int(request.POST.get(t+"2file","-1"))
            except:
                cc=_(u"请假数据导入失败")+"</p><pre>"
                cc+=request.POST.get(t+"2file","-1")
                return render_to_response("info.html", {"title": _("Import employee list"), "content": cc})
        f=request.FILES["fileUpload"]
        data=""
        fName=f.name
        whatrow=request.POST["whatrowid2file"]
        #ext=fName[fName.find('.')+1:].upper()
        ext=''
        fl=fName.split('.')
        if fl:
            ext=fl[-1].upper()
        if ext=='XLSX':ext='XLS'
        lines=[]
        for chunk in f.chunks(): data+=chunk
        if ext=='TXT' or ext=='CSV':
            lines=data.splitlines()
        elif ext=='XLS' or ext=='XLSX':
            import xlrd
#			fn="%s/%s"%(tmpDir(),fName)
            fName=fName.encode("gb2312")#修改导入文件名称为中文报错问题
            fn="%s/%s"%(tmpDir(),fName)
            f=file(fn, "wb")
            try:
                f.write(data)
            except:
                pass
            f.close()

            bk = xlrd.open_workbook(fn)
            sheetNames=bk.sheet_names()
            if not sheetNames:
                cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            shxrange = range(bk.nsheets)
            try:
                sh = bk.sheet_by_index(0)
            except:
                s="no sheet in %s named %s" %(fn,sheetNames[0])
                cc=u"%s,%s"%(_('imported failed'),s)
                return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
            nrows = sh.nrows
            ncols = sh.ncols
            for i in range(0,nrows):
                sv=[]
                for sr in sh.row_values(i):
                    if type(sr)==type(1.0):
                        sr=str(sr)
                        try:
                            if sr.index(".0")!='-1':
                                sr=sr.split(".")[0]
                            else:
                                sr=sr
                        except:
                            sr=sr
                    sv.append(sr)
#				row_data = sh.row_values(i)
                row_data = sv
                lines.append(row_data)
        jjj=0
        jj=0
        iCount=len(lines)          #import users count
        i_insert=0
        i_update=0
        sql_insert=[]
        sql_update=[]
        i_rep=0
        errorRec=[]
        #adminLog(time=datetime.datetime.now(),User=request.user, action=u"导入请假数据").save()
        sqlList=[]
        r=0
        for t in lines:
            r+=1
            if int(whatrow)>r:
                continue
            jj+=1
            if jj<fromline:continue
            dDict={}
            if ext=="TXT":
                ls=t.split('\t')
            elif ext=='CSV':
                ls=t.split(',')
            elif ext=='XLS' or ext=='XLSX':
                ls=t
            for k,v in imFieldsInfo.items():
                try:
                    if v<1 or v>100:
                        continue
                except:
                    continue
                v=int(v)

                ls[v-1]=ls[v-1].strip()
                if k=='badgenumber':
                    if ls[v-1]=='': #or (not ls[v-1].isdigit()):
                        errorRec.append(ls[v-1])
                        dDict={}
                        break
                    sUserids.append(ls[v-1])
                #if k=="clearance":
                #	if v<=len(ls):
                #		if ext=='XLS'  or ext=='XLSX':
                #			s=ls[v-1]
                #		else:
                #			s=getStr_c_decode(ls[v-1])
                #		if s==clearance_yes:
                #			ls[v-1]=1
                #		elif s==clearance_no:
                #			ls[v-1]=0
                #		else:
                #			ls[v-1]=0
                if k=="DateID":
                    if v<=len(ls):
                        if ext=='XLS'  or ext=='XLSX':
                            s=ls[v-1]
                        else:
                            s=getStr_c_decode(ls[v-1])
                        isHave=0
                        for t in leave:
                            if s==t['LeaveName']:
                                tmp_l = LeaveClass.objects.get(LeaveName=s)
                                if tmp_l.DelTag==1:
                                    isHave=2
                                else:
                                    isHave=1
                                    ls[v-1]=t['LeaveID']
                        if isHave==0:
                            s=u"系统假类中名称为%s的不存在" %(s)
                            cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
                            return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                        elif isHave==2:
                            s=u"系统假类中名称为%s的已删除" %(s)
                            cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
                            return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                if v<=len(ls):
                    s=ls[int(v)-1]
                    if ext=='XLS' or ext=='XLSX':
                        if k in ['StartSpecDay','EndSpecDay']:
                            #if str(type(s))=="<type 'unicode'>":
                            if '-' in s:
                                lDate=s.split('-')
                                dDict[k]=datetime.datetime(int(lDate[0]),int(lDate[1]),int(lDate[2]))
                            else:
                                iDate = int(s)
                                lDate=xlrd.xldate_as_tuple(iDate,bk.datemode)
                                iDate1=datetime.datetime(lDate[0],lDate[1],lDate[2])
                                dDict[k]=iDate1
                        else:
                            dDict[k]=s
                    else:
                        dDict[k]=getStr_c_decode(s)
            if dDict!={}:
                jjj+=1
                #print dDict
                if dDict.has_key('YUANYING'):
                    dDict['YUANYING']=dDict['YUANYING'].replace("\'","")
                    dDict['YUANYING']=dDict['YUANYING'].replace("\"","")
                else:
                    dDict['YUANYING']=''
                try:
                    e=employee.objByPIN(dDict['badgenumber'])
                    dDict['UserID']=e.id
                except:
                    s=u"工号为%s的人员不存在" %(dDict['badgenumber'])
                    cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
                    return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                    #errorRec.append(dDict['badgenumber'])
                    #continue
                if dDict['StartSpecDayTime']:
                    if ':' in dDict['StartSpecDayTime']:
                        slTime=dDict['StartSpecDayTime'].split(':')
                        dDict['StartSpecDay']=dDict['StartSpecDay']+datetime.timedelta(hours=int(slTime[0]),minutes=int(slTime[1]))
                    else:
                        iTime = float(dDict['StartSpecDayTime'])
                        dDict['StartSpecDay']=dDict['StartSpecDay']+datetime.timedelta(days=iTime)


                del dDict['StartSpecDayTime']

                if dDict['EndSpecDayTime']:
                    if ':' in dDict['EndSpecDayTime']:
                        slTime=dDict['EndSpecDayTime'].split(':')
                        dDict['EndSpecDay']=dDict['EndSpecDay']+datetime.timedelta(hours=int(slTime[0]),minutes=int(slTime[1]))
                    else:
                        iTime = float(dDict['EndSpecDayTime'])
                        dDict['EndSpecDay']=dDict['EndSpecDay']+datetime.timedelta(days=iTime)

                if dDict['StartSpecDay']>dDict['EndSpecDay']:
                    s=u"工号为%s的人员开始日期和结束日期出错" %(dDict['badgenumber'])
                    cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
                    return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
                del dDict['EndSpecDayTime']
                dDict['clearance']=0
                dDict['State']=2
                dDict['roleid']=0
                dDict['processid']=-1
                dDict['procSN']=0
                dDict['ApplyDate']=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                del dDict['badgenumber']
                #uspe=USER_SPEDAY.objects.filter(UserID=e,StartSpecDay=dDict['StartSpecDay'],DateID=dDict['DateID'])
                uspe=USER_SPEDAY.objects.filter(UserID=e,StartSpecDay=dDict['StartSpecDay'])
                if uspe:
                    sql_update.append(dDict)
                else:
                    sql_insert.append(dDict)
        for up_dDict in sql_update:
            up_dDict['whereUserID']=up_dDict['UserID']
            up_dDict['whereStartSpecDay']=up_dDict['StartSpecDay']
            del up_dDict['UserID']
            del up_dDict['StartSpecDay']
            sql,params=getSQL_update_new('USER_SPEDAY',up_dDict)
            if customSqlEx(sql,params):
                i_update+=1

        for in_dDict in sql_insert:
            sql,params=getSQL_insert_new('USER_SPEDAY',in_dDict)
            if customSqlEx(sql,params):
                i_insert+=1
                e=employee.objByID(in_dDict['UserID'])
                uspe=USER_SPEDAY.objects.get(UserID=e,StartSpecDay=in_dDict['StartSpecDay'],DateID=in_dDict['DateID'])
                USER_SPEDAY_DETAILS(USER_SPEDAY_ID=uspe,remarks='',Place='',mobile='',successor='').save()

        cache.delete("%s-%s"%(settings.UNIT,'home_user_speadays'))

        result=reportError(u"%s"%_(u"请假信息"), jjj, i_insert, i_update, i_rep,errorRec)
        adminLog(time = datetime.datetime.now(), User = request.user, action = u'%s' % _(u"Import"),
                 model = USER_SPEDAY._meta.verbose_name, object = request.META["REMOTE_ADDR"], count = jjj).save(force_insert = True)
        return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")

    except Exception,e:
        import traceback;traceback.print_exc()
        print 'importSpeday error---',e
        cc=u"<h1>%s</h1><br/>%s"%(_(u"批量上传请假列表"),_(u"请假信息导入失败"))+"</p><pre>"
        return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
#		cc+=request.POST.get(t+"2file","")
#		return HttpResponse(content="result=1",mimetype='text/plain')#render_to_response("info.html", {"title": _("Import employee list"), "content": cc})



