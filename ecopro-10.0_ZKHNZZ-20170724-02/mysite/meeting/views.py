#!/usr/bin/env python
#coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required,permission_required
from mysite.meeting.models import *
from mysite.iclock.models import *
from mysite.utils import *
from mysite.iclock.iutils import  *
from django.utils.translation import ugettext_lazy as _
from mysite.core.tools import *
from django.shortcuts import render_to_response
from django.template import  RequestContext
@login_required
def SaveParticipants(request):
    meetID=int(request.GET.get('meetid','-1'))
    deptIDs=request.POST.get('deptIDs',"")
    userIDs=request.POST.get('UserIDs',"")
    isContainedChild=request.POST.get('isContainChild',"")
    if meetID==-1:
        return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})

    if userIDs == "":
        isAllDept=0
        deptidlist=deptIDs.split(',')
        if isContainedChild=="1":
            deptids=[]
            for d in deptidlist:#支持选择多部门
                if(request.user.is_superuser) or ( request.user.is_alldept):
                    if department.objByID(int(d)).parent==0:
                        isAllDept=1
                        deptids=[]
                        break
                if int(d) not in deptids:
                    deptids+=getAllAuthChildDept(d,request)
        else:
            deptids=deptidlist

        if isAllDept==1:
            userids=list(employee.objects.all().exclude(OffDuty=1).exclude(DelTag=1).values_list('id',flat=True))
        else:
            userids=list(employee.objects.filter(DeptID__in=deptids).exclude(OffDuty=1).exclude(DelTag=1).values_list('id',flat=True))

    else:
        userids=userIDs.split(',')
    for uid in userids:
        sql,params=getSQL_insert_new(participants_details._meta.db_table,participants_tplID_id=meetID,UserID_id=uid)
        try:
            customSqlEx(sql,params)
        except Exception,e:
            #print e
            pass
    return getJSResponse({"ret":0,"message":u"%s"%_('Operation Successful')})

def Savemappicture(request):
    spd=request.POST.get("userspeday")
    f=request.FILES["fileToUpload"]
    try:
        os.makedirs("%smeetmap/"%settings.ADDITION_FILE_ROOT)
    except:
        pass
    if f.name[-4:]<>'.jpg':
        return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})
    filename=spd+'.jpg'
    fname="%s%s/%s"%(settings.ADDITION_FILE_ROOT,'meetmap', filename)
    fl=open(fname,'wb')
    try:
        fl.writelines(f)
    finally:
        fl.close()
    tbName=getStoredFileName("meetmap/thumbnail", None, spd+".jpg")
    if os.path.exists(tbName):
        os.remove(tbName)
    return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})#getJSResponse({"ret":0,"message":_("Save Success")})

@login_required
def SaveEmployee_meet(request):
    meetID=int(request.GET.get('meetid','-1'))
    deptIDs=request.POST.get('deptIDs',"")
    userIDs=request.POST.get('UserIDs',"")
    tpl=request.POST.get('meet_tpl',"")
    isContainedChild=request.POST.get('isContainChild',"")
    if meetID==-1:
        return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})
    userids=[]
    if userIDs != "":
        userids=userIDs.split(',')

    if tpl:
        tpls=tpl.split(',')
        objs=participants_details.objects.filter(participants_tplID__in=tpls)
        for t in objs:
            userids.append(t.UserID_id)
        userids=set(userids)

    for uid in userids:
        sql,params=getSQL_insert_new(Meet_details._meta.db_table,MeetID_id=meetID,UserID_id=uid)
        customSql(sql,params)
    # if tpl:
    #     tpls=tpl.split(',')
    #     objs=participants_details.objects.filter(participants_tplID__in=tpls)
    #     for t in objs:
    #         sql,params=getSQL_insert_new(Meet_details._meta.db_table,MeetID_id=meetID,UserID_id=t.UserID_id)
    #         customSql(sql,params)
    if userids:
        emps=employee.objects.filter(id__in=userids)
        LocationID=Meet.objects.get(id=meetID).LocationID
        dev=meet_devices.objects.filter(LocationID=LocationID).values_list('SN', flat=True)
        from mysite.core.cmdproc import deptEmptoDev
        deptEmptoDev(dev, emps, cursor=None, finger=1, face=1, PIC=0, Palm=1, Vein=1)

    return getJSResponse({"ret":0,"message":u"%s"%_('Operation Successful')})

def SyncEmployee_meet(request):
    meetids = request.POST.getlist("K")
    try:
        if meetids:
            for meetid in meetids:
                userids = Meet_details.objects.filter(MeetID = meetid).values_list('UserID', flat = True)
                if userids:
                    LocationID = Meet.objects.get(id = meetid).LocationID
                    dev = meet_devices.objects.filter(LocationID = LocationID).values_list('SN', flat = True)
                    emps = employee.objects.filter(id__in=userids)
                    from mysite.core.cmdproc import deptEmptoDev
                    deptEmptoDev(dev, emps, cursor = None, finger = 1, face = 1, PIC = 0, Palm = 1, Vein = 1)
            return getJSResponse({"ret":0, "message":u"%s" % _('Operation Successful')})
    except Expression,e:
        print e
        return getJSResponse({"ret":1, "message":u"%s" % _('Operation Failed')})








def exportfilename(request):
    k=request.GET.get("id",'')
    k=unquote(k)
    mi=Minute.objects.filter(FileNumber=k)
    name=""
    if mi.count()>0:
        name=mi[0].Appendixes
    return render(request,'meeting/attachmenthtml.html',{'filename':name})

@login_required
def saveMinutefile(request):    #上传人员照片
    request.user.iclock_url_rel='../..'
    request.model = Minute
    if request.method == 'POST':
        FileNumber= request.GET.get("FileNumber")
        f=request.FILES["fileToUpload"]
        if len(f.name)>40:
            return getJSResponse({"ret":1,"message":u"%s"%_(u'保存失败，附件文件名过长!')})
        try:
            os.makedirs("%sminute/"%settings.ADDITION_FILE_ROOT)
        except:
            pass
        filename=f.name
        fname="%s%s/%s"%(settings.ADDITION_FILE_ROOT,'minute', filename)
        fl=open(fname,'wb')
        try:
            fl.writelines(f)
        finally:
            fl.close()
        Minute.objects.filter(FileNumber=FileNumber).update(Appendixes=filename)
        return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})#getJSResponse({"ret":0,"message":_("Save Success")})
