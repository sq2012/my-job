#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import string
from django.contrib import auth
from django.shortcuts import render_to_response,render
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context, RequestContext
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from mysite.iclock.models import *
from mysite.acc.models import *
#from mysite.iclock.datasproc import *
from django.core.paginator import Paginator
#from mysite.iclock.datas import *
from mysite.core.menu import *
from mysite.core.tools import *
from mysite.core.cmdproc import *
from mysite.iclock.models import *
from mysite.utils import *
#from django.shortcuts import render
import ctypes


@login_required
def index(request, ModelName):
    if request.method=='GET':
        tmpFile='acc/'+'acc_sys.html'
        tmpFile=request.GET.get('t', tmpFile)
        sub_menu='"%s"'%createmenu(request,ModelName)
        cc={}

        cc['sub_menu']=sub_menu
        #print sub_menu
        return render(request,tmpFile,cc)#render_to_response(tmpFile,cc,RequestContext(request, {}))







            #if ModelName=='inbio' or ModelName=='iaccess':
            #    tmpFile='acc/'+ModelName+'_sys.html'
            #    tmpFile=request.GET.get('t', tmpFile)
            #    sub_menu='"%s"'%createmenu(request,ModelName)
            #    cc={}
            #    
            #    cc['sub_menu']=sub_menu
            #    
            #    #print sub_menu
            #    return render_to_response(tmpFile,cc,RequestContext(request, {}))
            #else:
            #    tmpFile='acc/'+ModelName+'.html'
            #    tmpFile=request.GET.get('t', tmpFile)
            #    cc={}
            #    return render_to_response(tmpFile, cc,RequestContext(request, {}))
 
 
 
 
 
@login_required	
def SaveLevelEmp(request):
    levelID=request.GET.get('levelid','')
    deptIDs=request.POST.get('deptIDs',"")
    userIDs=request.POST.get('UserIDs',"")
    isContainedChild=request.POST.get('isContainChild',"")
    if levelID=='':
        return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})
    levelID=levelID.split(',')   
    if userIDs == "":
            isAllDept=0
            deptidlist=deptIDs.split(',')
            deptids=[]
            if isContainedChild=="1":
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
                emps=employee.objects.all().exclude(OffDuty=1).exclude(DelTag=1)
            else:
                emps=employee.objects.filter(DeptID__in=deptids).exclude(OffDuty=1).exclude(DelTag=1)
                
    else:
        userids=userIDs.split(',')
        emps=employee.objects.filter(id__in=userids)
    for emp in emps:
        for t in levelID:
            sql,params=getSQL_insert_new(level_emp._meta.db_table,level_id=t,UserID_id=emp.id)
            try:
                customSqlEx(sql,params)
            except Exception,e:
                    #print e
                    pass
    sendLevelToAccEx(emps,levelID)
    adminLog(time=datetime.datetime.now(),User=request.user,object=request.META["REMOTE_ADDR"], model=level._meta.verbose_name, action=_(u"修改")).save(force_insert=True)#
    return getJSResponse({"ret":0,"message":u"%s"%_('Operation Successful')})

#按人员设置
def SaveLevel_Emp(request):
    userid=request.GET.get('id','')
    levelids=request.POST.get('K',"")
    if levelids=='':
        return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})
    levelID=levelids.split(',')
    for t in levelID:
        sql,params=getSQL_insert_new(level_emp._meta.db_table,level_id=t,UserID_id=userid)
        customSql(sql,params)
#	emp=employee.objByID(userid)
    emps=employee.objects.filter(id=userid)
    sendLevelToAccEx(emps,levelID)
    adminLog(time=datetime.datetime.now(),User=request.user,object=request.META["REMOTE_ADDR"], model=level._meta.verbose_name, action=_(u"修改")).save(force_insert=True)#
    return getJSResponse({"ret":0,"message":u"%s"%_('Operation Successful')})


@login_required	
def SaveFirstOpen_Emp(request):
    FirstID=request.GET.get('door','')
    deptIDs=request.POST.get('deptIDs',"")
    userIDs=request.POST.get('UserIDs',"")
    isContainedChild=request.POST.get('isContainChild',"")
    if FirstID=='':
        return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})
    FirstIDs=FirstID.split(',')   
    if userIDs == "":
            isAllDept=0
            deptidlist=deptIDs.split(',')
            if isContainedChild=="1":
                    for d in deptidlist:#支持选择多部门
                            if(request.user.is_superuser) or ( request.user.is_alldept):
                                    if department.objByID(int(d)).parent==0:
                                            isAllDept=1
                                            deptids=[]
                                            break
                            if int(d) not in deptids:
                                    deptids +=getAllAuthChildDept(d,request)
            else:
                    deptids=deptidlist
                    
            if isAllDept==1:
                userids=list(employee.objects.all().exclude(OffDuty=1).exclude(DelTag=1).values_list('id',flat=True))
            else:
                userids=list(employee.objects.filter(DeptID__in=deptids).exclude(OffDuty=1).exclude(DelTag=1).values_list('id',flat=True))
                
    else:
            userids=userIDs.split(',')
    for uid in userids:
        for t in FirstIDs:
            sql,params=getSQL_insert_new(FirstOpen_emp._meta.db_table,firstopen_id=t,UserID_id=uid)
 #           try:
            customSql(sql,params)
            # except Exception,e:
            #         #print e
            #         pass
    sendFirstCardToAcc(FirstIDs)
    adminLog(time=datetime.datetime.now(),User=request.user,object=request.META["REMOTE_ADDR"], model=FirstOpen_emp._meta.verbose_name, action=_(u"修改")).save(force_insert=True)#
    return getJSResponse({"ret":0,"message":u"%s"%_('Operation Successful')})
  
  
@login_required
def save_linkage(request,key):
    """input_type:0-any  1-AccDoor  2-Reader  3-AuxIn     output_type:0-AccDoor 1-AuxOut"""
    #   print request.POST
    SN=request.POST.get('device','')
    name=request.POST.get('name')
    remark=request.POST.get('remark')
    action_type=int(request.POST.get('action_type','-1'))
    events=request.POST.get('events_h')
    inputs=request.POST.get('inputs_h')
    outputs=request.POST.get('outputs_h')
    action_time=int(request.POST.get('action_time','0'))
    tab_index=int(request.POST.get('tab_index','0'))
    if events:
        events=events.split(',')
    else:
        events=[]
        outputs=[]
        inputs=[]

    if inputs:
        inputs=inputs.split(',')
    else:
        events=[]
        outputs=[]
        inputs=[]

    if outputs:
        outputs=outputs.split(',')
    else:
        events=[]
        outputs=[]
        inputs=[]


    try:
        events.remove(-10)
    except:pass
    #print inputs,outputs,events
    #action={0:0,1:20,2:255}
    if key=='_new_':
        #sqlstr,params=getSQL_insert_new(linkage._meta.db_table,device_id=SN,name=name)
        link_obj=linkage(device_id=SN,name=name,remark=remark)
        try:
            #pass
            link_obj.save(force_insert=True)
        except Exception,e:
            print "save_linkage",e
            return getJSResponse({"ret":1,"message": u"%s"%_(u'保存失败')})
        link_id=link_obj.id
    else:
        link_id=key
        link_obj=linkage(id=link_id,device_id=SN,name=name,remark=remark)
        link_obj.save(force_update=True)
    objs=linkage_trigger.objects.filter(linkage=link_id)
    if tab_index==0:
        objs=objs.filter(trigger_cond__in=[5,7,8,9,24,25,28,36,37,38,100,102,200,201,202,204,205,209])

    if tab_index==1:
        objs=objs.filter(trigger_cond__in=[0,2,3,4,20,21,22,23,27,29,41,42,101])


    if tab_index==2:
        objs=objs.filter(trigger_cond__in=[220,221])
    del_linkage_trig(SN,objs)
    objs.delete()
    if tab_index==0:
        linkage_inout.objects.filter(linkage=link_id,input_type__in=[0,1]).delete()
    if tab_index==1:
        linkage_inout.objects.filter(linkage=link_id,input_type__in=[2,100]).delete()
    if tab_index==2:
        linkage_inout.objects.filter(linkage=link_id,input_type__in=[3,1000]).delete()
    for its in inputs:
        its=int(its)
        if its==0:
            inputtype=0
            if tab_index==1:
                inputtype=100   #读头为任意时
            if tab_index==2: #辅助输入为任意时
                inputtype=1000
        elif tab_index==2:#('220' in events) or ('221' in events):
            inputtype=3
        elif tab_index==0:
            inputtype=1
        elif tab_index==1:
            inputtype=2
        for ots in outputs:
            ots=int(ots)
            outtype=0
            if ots<0:
                outtype=1
                ots=ots*(-1)
            link_inout=linkage_inout(linkage_id=link_id,input_type=inputtype,input_id=its,output_type=outtype,output_id=ots,action_type=action_type,action_time=action_time)
            link_inout.save(force_insert=True)
            inout_id=link_inout.id
            for es in events:
                link_trig=linkage_trigger(trigger_cond=es,linkage_index=inout_id,linkage_id=link_id,linkage_inout_id=inout_id)
                link_trig.save(force_insert=True)
    try:
        sendLinkageToAcc(link_id)
    except Exception,e:
        print "sendLinkageToAcc=======",e

    return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')})

@login_required
def save_combopen_comb(request,key):
    door=request.POST.get('door','')
    name=request.POST.get('name')
    combs=request.POST.get('combopen_door_data','[]')
    if key=='_new_':
        obj=combopen_door(name=name,door_id=int(door))
        try:
            obj.save()
        except Exception,e:
            print "save_combopen_door",e
            return getJSResponse({"ret":1,"message": u"%s"%_('Save Failed')})
        combopen_door_id=obj.id
    else:
        combopen_door_id=key
        obj=combopen_door(id=key,name=name,door_id=int(door))
        obj.save()

    combopen_comb.objects.filter(combopen_door=combopen_door_id).delete()
    comb=loads(combs)
    j=0
    for t in comb:
        d={}
        d['combopen_door_id']=combopen_door_id
        d['combopen_id']=t['combid']
        d['opener_number']=t['empCount']
        d['sort']=j
        j=j+1
        sql,params=getSQL_insert_new(combopen_comb._meta.db_table,d)
        #try:
        customSql(sql,params)
        #except Exception,e:
            #print e
            #pass

    sendMulCardToAcc(combopen_door_id)
    return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')})


#人员维护时保存的有关门禁信息
def saveToAccEmployee(request,emp):
    set_time=False
    st=None
    et=None
    blacklist=False
    morecard_group=request.POST.get('morecard_group')
    set_valid_time=request.POST.get('set_valid_time')
    super_auth=request.POST.get('acc_super_auth')
    isblacklist=request.POST.get('isblacklist')
    levels=request.POST.getlist('level')

    if isblacklist=='on':
        blacklist=True
    if set_valid_time=='on':
        set_time=True
        startdate=request.POST.get('acc_startdate')[0:16]
        enddate=request.POST.get('acc_enddate')[0:16]

        st=datetime.datetime.strptime(startdate,'%Y-%m-%d %H:%M')
        et=datetime.datetime.strptime(enddate,'%Y-%m-%d %H:%M')
    tmp=acc_employee.objects.filter(UserID=emp)
    if tmp:
        tmp.delete()
    acc_employee(UserID=emp,morecard_group_id=morecard_group,set_valid_time=set_time,acc_startdate=st,acc_enddate=et,acc_super_auth=super_auth,isblacklist=blacklist).save()
    levellist = level_emp.objects.filter(UserID = emp).distinct().values_list('level', flat=True)
    #oldlevel_emp = level_emp.objects.filter(UserID=emp)
    #if oldlevel_emp:
    #	levellist = level_emp.objects.filter(UserID = emp).distinct().values_list('level', flat=True)
    #	emp_s = level_emp.objects.filter(UserID = emp).distinct().values('UserID')
    #	empobjs = employee.objects.filter(id__in = emp_s)
    #	deleteEmpfromAcc(levellist, empobjs)
    new_levels=[]
    del_levels=[]

    for t in levellist:
        if str(t) not in levels:
            del_levels.append(t)
    for t in levels:
        if int(t) not in levellist:
            new_levels.append(int(t))


    #level_emp.objects.filter(UserID=emp).delete()
    for t in new_levels:
        level_emp(UserID=emp,level_id=t).save()
    #if new_levels:
    emps=employee.objects.filter(id=emp.id)
    if new_levels:
        sendLevelToAccEx(emps,new_levels)
#	sendLevelToAcc([emp],levels)
    if del_levels:

        level_emp_id = list(level_emp.objects.filter(UserID = emp,level__in=del_levels).distinct().values_list('id', flat=True))
        emps=employee.objects.filter(id=emp.id)

        deleteEmpfromAcc(del_levels, emps,level_emp_id)


    combopen_emp.objects.filter(UserID=emp).delete()
    if morecard_group:
        try:
            combopen_emp(UserID=emp,combopen_id=morecard_group).save()
        except:pass

#该方法主要用于远程开关门取消报警（包括开部分门)    
@login_required
def send_doors_data(request):
    funid = request.GET.get("func", "")
    itype = request.GET.get("type", "")
    door =  request.GET.get("data", "")
    devs=[]
    doors=[]
    if itype == 'part':
        doors_id = door.split(',')
        doors_count = len(doors_id)
        devs = AccDoor.objects.filter(id__in=doors_id).distinct().values('device')
        doors = AccDoor.objects.filter(id__in=doors_id).distinct()

    datas = []
    if funid in ["cancelalarm", "cancelall"]:#对应控制器的取消报警,不分门
        for t in devs:
            sn=t['device']
            dev=getDevice(sn)
            appendDevCmd(dev,'AC_UNALARM')  #0200
        return getJSResponse({'ret': 0})
    elif funid in ["opendoor", "openpart"]:
        interval = request.GET.get("open_interval", 0)#1-254
        enable = request.GET.get("enable_no_tzs", False)
        if enable == "true":#仅启用常开时间段，不开门
            #for door_obj in doors:
            #	if doors_count > 1:
            #		if not door_obj.device.show_status():
            #			continue

            for door in doors:
                door_no=door.door_no
                cmdstr="CONTROL DEVICE 04%02d0100"%(door_no)
                saveCmd(door.device_id,cmdstr)
            #ret = sync_control_no(door_obj, 1)#重新启用常开时间段
            #ret = sync_set_output(door_obj, 1, int(interval))#ret为None代表固件没有返回值，成功还是失败？  door_obj.lock_delay
            #datas.append({ "door_name": door_obj.door_name, "ret": ret == None and -1 or ret })
        else:
            #print '----remote 005', doors.count()
            #for dev in devs:
            for door in doors:
                door_no=door.door_no
                cmdstr="CONTROL DEVICE 01%02d01%02x"%(door_no,int(interval))
                #print cmdstr
                saveCmd(door.device_id,cmdstr)
                #datas.append({ "door_name": door_obj.door_name, "ret": ret == None and -1 or ret })
        return getJSResponse({'ret':0})
    elif funid in ["closedoor", "closepart"]:# "closeall",:
        disable = request.GET.get("disable_no_tzs", False)
        #print '----disable=',disable
        if disable == "true":
            #for dev in devs:
            for door in doors:
                door_no=door.door_no
                cmdstr="CONTROL DEVICE 04%02d0000"%(door_no)
                saveCmd(door.device_id,cmdstr)

            for t in devs:
                sn=t['device']
                auxs=AuxOut.objects.filter(device=sn)
                for tt in auxs:
                    aux_no=tt.aux_no
                    cmdstr="CONTROL DEVICE 01%02d0200"%aux_no
                    saveCmd(sn,cmdstr)




        else:
            #for dev in devs:
            for door in doors:
                door_no=door.door_no
                cmdstr="CONTROL DEVICE 01%02d0100"%(door_no)
                saveCmd(door.device_id,cmdstr)
            for t in devs:
                sn=t['device']
                auxs=AuxOut.objects.filter(device=sn)
                for tt in auxs:
                    aux_no=tt.aux_no
                    cmdstr="CONTROL DEVICE 01%02d0200"%aux_no
                    saveCmd(sn,cmdstr)


                #datas.append({ "door_name": door_obj.door_name, "ret": ret == None and -1 or ret })
        return getJSResponse({'ret':0})



@login_required
def sync_doors_data(request):
    keys=request.POST.getlist('K')
    opts=request.POST.getlist('optBox')
    iclocks=iclock.objects.filter(SN__in=keys)#.exclude(DelTag=1).exclude(State=0)
    #for dev in iclocks:
    #	delete_acc_all_data(dev)
    if 'accLevel' in opts:
        for dev in iclocks:
            if dev.ProductType in [5,15,25]:
                delete_data(dev.SN,'user')
                delete_data(dev.SN,'userauthorize')
        sendLevelToAccEx([],[],keys)
    if 'timeZoneAndHoliday' in opts:
        for dev in iclocks:
            if dev.ProductType in [5,15,25]:
                delete_data(dev.SN,'holiday')
                delete_data(dev.SN,'timezone')


        sendTimeZonesToAcc([],keys)
        sendHolidayToAcc([],keys)
    if 'doorOpt' in opts:
        for dev in iclocks:
            if dev.ProductType in [5,15,25]:
                sendDoorToAcc(None,[dev.SN])
    if 'interlock' in opts:
        for dev in iclocks:
            if dev.ProductType in [5,15,25]:
                sendInterLockToAcc([],[dev.SN])
    if 'linkage' in opts:
        for dev in iclocks:
            if dev.ProductType in [5,15,25]:
                delete_data(dev.SN,'inoutfun')
                sendLinkageToAcc([],dev.SN)
    if 'antiPassBack' in opts:
        for dev in iclocks:
            if dev.ProductType in [5,15,25]:
                clear_antipassback(dev.SN)
                objs=AntiPassBack.objects.filter(device__in=[dev.SN])
                for obj in objs:
                    set_antipassback(obj)
    if 'firstPerson' in opts:
        for dev in iclocks:
            if dev.ProductType in [5,15,25]:
                delete_data(dev.SN,'firstcard')

                doors=AccDoor.objects.filter(device__in=[dev.SN])
                objs=FirstOpen.objects.filter(door__in=doors).values_list('id',flat=True)
                sendFirstCardToAcc(objs)
    if 'multiPerson' in opts:
        for dev in iclocks:
            if dev.ProductType in [5,15,25]:
                delete_data(dev.SN,'multimcard')

                sendMulCardToAcc([],[dev.SN])
    return getJSResponse({'ret': 0})

@login_required
def restartsvr2(request):
    try:
        os.system("cmd /C %s/%s"%(settings.FILEPATH,'iclockservice.exe -b 2'))
    except:
        pass

    return getJSResponse({'ret': 0,'message':u'%s'%_(u'启动成功!')})


def saveParamsToOtherDoor(request,newobj):
    opts=request.GET.getlist('optBox')
    objs=AccDoor.objects.all()
    doorset=[]
    for obj in objs:
        for k in opts:
            v=newobj.__getattribute__(k)
            obj.__setattr__(k,v)
            obj.save()
        doorset.append(obj)
    if doorset:
        set_dooroptions(doorset)


@login_required
def search_device(request):
    Host=request.META["HTTP_HOST"]
    #print Host

    auto_reg=GetParamValue('opt_basic_dev_auto','1')
    if auto_reg=='0':
        return getJSResponse({'ret': 0,'message':u'%s'%_(u'系统设置不允许自动添加新设备!')})


    commpro = ctypes.windll.LoadLibrary(settings.FILEPATH+"\zkeco_dlls\plcommpro.dll")
    str_buf_len = 64*1024*2 #64K*2 200台设备
    str_buf = ctypes.create_string_buffer("",str_buf_len)
    sCommType='UDP'
    sAddr='255.255.255.255'
    pCommType = ctypes.create_string_buffer(sCommType)
    pAddr = ctypes.create_string_buffer(sAddr)
    ret=commpro.SearchDevice("UDP","255.255.255.255",str_buf)
    sns=[]

    searchs.objects.update(State=3)
    if ret>0:
        result=str_buf.raw
        index=result.find('\0')
        result = result[0:index-2].split('\r\n')
#		print "111111111111",result
        for t in result:
            devDict=lineToDict(t,',')
            sn=devDict['SN']


            #if 'WebServerIP' in devDict.keys() and devDict['WebServerIP']!='' and devDict['WebServerIP']!='0.0.0.0':continue
            Protype=''
            if "Protype" in devDict.keys():
                Protype=devDict["Protype"]
            devName=devDict['SN']
            if 'Device' in devDict.keys() and devDict['Device']!='':
                devName=devDict['Device']
            #	if 'C3' in devName:
            #		ProductType=15

            objs=searchs.objects.filter(SN=sn)
            if not objs:
                obj=searchs()
            else:
                obj=objs[0]
            obj.SN=sn
            obj.isAdd=0
            obj.State=1
            # try:
            # 	print "1111111111",sn
            # 	obj1=iclock.objects.get(SN=sn)#filter(SN=sn).filter(DelTag=1):
            # 	if
            # 			obj.isAdd=0
            # 	elif iclock.objects.filter(SN=sn).filter(DelTag=0):
            # 		print "------",sn
            # 		obj.isAdd=1
            # except:
            # 	obj.isAdd=0
            if not obj.Alias:
                obj.Alias=devName
            obj.Protype=Protype
            obj.MAC=devDict['MAC']
            obj.Reserved=''
            if not obj.IPAddress:
                obj.IPAddress=devDict['IP']
            else:
                if obj.IPAddress!=devDict['IP']:
                    obj.Reserved=u'设备IP:%s'%(devDict['IP'])
            if 'NetMask' in devDict.keys():
                if not obj.NetMask:
                        obj.NetMask=devDict['NetMask']
                else:
                    if obj.NetMask!=devDict['NetMask']:
                        obj.Reserved=obj.Reserved+' '+u'设备NetMask:%s'%(devDict['NetMask'])
            if 'GATEIPAddress' in devDict.keys():
                if not obj.GATEIPAddress:
                    obj.GATEIPAddress=devDict['GATEIPAddress']
                else:
                    if obj.GATEIPAddress!=devDict['GATEIPAddress']:
                        obj.Reserved=obj.Reserved+' '+u'设备GATEIP:%s'%(devDict['GATEIPAddress'])
            obj.DeviceName=devName
            if 'Ver' in devDict.keys():
                obj.FWVersion=devDict['Ver']
            if Protype=='push' and 'WebServerIP' in devDict.keys():
                if not obj.WebServerIP:
                    obj.WebServerIP=devDict['WebServerIP']
                else:
                    if obj.WebServerIP!=devDict['WebServerIP']:
                        obj.Reserved=obj.Reserved+' '+u'设备WEB:%s'%(devDict['WebServerIP'])

                if not obj.WebServerPort:
                    obj.WebServerPort=devDict['WebServerPort']
                else:
                    if obj.WebServerPort!=devDict['WebServerPort']:
                        obj.Reserved=obj.Reserved+' '+u'设备Port:%s'%(devDict['WebServerPort'])

                obj.WebServerURL=devDict['WebServerURL']
            obj.IsSupportSSL=0
            if 'IsSupportSSL' in devDict.keys():
                obj.IsSupportSSL=devDict['IsSupportSSL']
            obj.DNSFunOn=0
            if 'DNSFunOn' in devDict.keys():
                obj.DNSFunOn=devDict['DNSFunOn']
            if 'DNS' in devDict.keys():
                obj.DNS=devDict['DNS']
            obj.OpStamp=datetime.datetime.now()
            obj.save()


        # 	sns.append(sn)
        # 	try:
        # 	    zon=zone.objects.all().order_by('id').exclude(DelTag=1)[0]
        # 	    IclockZone(SN=device,zone=zon).save()
        # 	except Exception,e:
        # 	    pass
        # try:
        # 	if sns:
        # 		sendTimeZonesToAcc(None,sns)
        # 		#restartSvr('AttServer')
        # except Exception,e:
        # 	print "222222222222",e




                #mac = s['MAC']		# 目标设备的MAC地址
                #new_ip = '192.168.1.76'		# 设备新的IP地址
                #comm_pwd = ''
                #str = "MAC=%s,IPAddress=%s,NetMask=%s " % (mac,new_ip,'255.255.0.0')
                #p_buf = ctypes.create_string_buffer(str)
                #modify_ip = commpro.ModifyIPAddress("UDP", "255.255.255.255", p_buf)
    else:
        return getJSResponse({'ret': 0,'message':u'%s:%s'%(_(u'未搜索到设备!'),ret)})

    return getJSResponse({'ret': 0,'message':u'%s:共%s台,新增%s台'%(_(u'搜索完成!'),ret,len(sns))})
#暂时没用
def SendEmpAccAuth(request):
    keys=request.POST.getlist("K")
    for key in keys:
        lve_list=list(level_emp.objects.filter(UserID=key).values_list('level',flat=True))
        emps=employee.objects.filter(id__in=[key])

        sendLevelToAccEx(emps,levels)

def save_modify_device(request):
    id=request.POST.get('id',0)
    try:
        obj=searchs.objects.get(id=id)
        obj.IPAddress=request.POST.get('IPAddress','')
        obj.NetMask=request.POST.get('NetMask','')
        obj.GATEIPAddress=request.POST.get('GATEIPAddress','')
        obj.WebServerIP=request.POST.get('WebServerIP','')
        obj.WebServerPort=request.POST.get('WebServerPort','')
        obj.save()

        commpro = ctypes.windll.LoadLibrary(settings.FILEPATH+"\zkeco_dlls\plcommpro.dll")

        #comm_pwd = ''
        if obj.Protype=='push':
            str = "MAC=%s,IPAddress=%s,NetMask=%s,WebServerIP=%s,WebServerPort=%s,Reboot=1" % (obj.MAC,obj.IPAddress,obj.NetMask,obj.WebServerIP,obj.WebServerPort)
        else:
            str = "MAC=%s,IPAddress=%s,NetMask=%s,Reboot=1" % (obj.MAC,obj.IPAddress,obj.NetMask)
        p_buf = ctypes.create_string_buffer(str)
        modify_ip = commpro.ModifyIPAddress("UDP", "255.255.255.255", p_buf)







    except:
        pass



    return getJSResponse({"ret":0,"message":u"%s"%_('Operation Successful')})

def add_devices(request):
    sns=[]
    keys=request.POST.get('k').split(',')
    objs=searchs.objects.filter(id__in=keys)
    ret=len(keys)
    pull_flag=0
    try:
        auth_zone=zone.objects.get(pk=1)
    except:
        auth_zone=None
    for t in objs:
        sn=t.SN
        try:
            obj=iclock.objects.get(SN=sn)
            #if t.Protype and t.Protype!='push':
            if t.Protype != 'push':
                if obj.IPAddress!=t.IPAddress:
                    obj.IPAddress=t.IPAddress
                    pull_flag = 1

                if obj.DelTag==1:
                    pull_flag=1
                    IclockZone(SN=obj,zone=auth_zone).save()
                    obj.DelTag=0
                obj.save()
            else:
                if obj.DelTag==1:
                    IclockZone(SN=obj,zone=auth_zone).save()
                    obj.DelTag=0
                    obj.save()
            sns.append(t.id)

        except:
            obj=iclock()
            obj.SN=sn
            obj.IPAddress=t.IPAddress
            obj.DeviceName=t.DeviceName
            if t.Protype=='push':
                obj.ProductType=5
            else:
                obj.ProductType=15
                pull_flag=1

            obj.save(force_insert=True)
            if auth_zone:
                IclockZone(SN=obj,zone=auth_zone).save()
            sns.append(t.id)
        if pull_flag==1:
            cache.set(settings.UNIT+'_restart_pull',1)
    return getJSResponse({'ret': 0,'message':u'%s:共%s台,新增%s台'%(_(u'操作完成!'),ret,len(sns))})
