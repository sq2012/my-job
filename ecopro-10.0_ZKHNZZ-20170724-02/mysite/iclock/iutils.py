#!/usr/bin/env python
#coding=utf-8
"""
有关部门的规则

1 前台没有选择包含子部门时 查询的数据是指当前部门的数据
2 前台选择包含子部门时 分如下情况
   如果选择的部门为总公司级即第一级部门 系统将认为是所有部门 在有关查询条件中不要加部门限制 getAllAuthChildDept返回的结果为[-1]
   如果不是第一级时对超级用户将自动包括其下级所有部门 如果是普通用户结果是被授权的所有子部门getAllAuthChildDept返回的结果为[3,4,5...]

"""
from mysite.iclock.models import *
from mysite.base.models import *
from mysite.acc.models import *
from mysite.ipos.models import *

from mysite.utils import *
from django.db import models
from django.utils.encoding import force_unicode, smart_str
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import datetime
d_deptDict={}
deptversion=''

#def Childrens(DeptID):
#	objs=department.objects.filter(parent=DeptID)
#	ret=[DeptID]
#	for t in objs:
#		ret.append(t.DeptID)
#	return ret
#def AllChildrens(curid, start=[]):
#	for d in Childrens(curid):
#		if d not in start:
#			start.append(d)
#			AllChildrens(d,start)


def Childrens(DeptID,d_item):
    #objs=department.objects.filter(parent=DeptID)
    #ret=[]
    #for t in objs:
    #	ret.append(int(t.DeptID))
    try:
        ret=d_item[DeptID]
    except:
        ret=[]
    return ret

def AllChildrens(curid, d_item,start=[]):
    """获取当前部门下的所有子部门，不含当前部门"""
    for d in Childrens(curid,d_item):
        if d not in start:
            start.append(d)
            AllChildrens(d,d_item,start)


def AllParents(curid):
    result=[]
    deptid=int(curid)
    while True:
        d=department.objByID(deptid)
        if not d:break
        if d.parent>0:
            result.append(int(d.parent))
        else:
            break
        deptid=int(d.parent)
    return result


gStatus=[]
#重点函数,管理员拥有的部门
def userDeptList(user):
    v=GetParamValue('DEPTVERSION')
    settings.DEPTVERSION=v

    Result=cache.get("%s_userdepts_%s_%s"%(settings.UNIT, user.id,settings.DEPTVERSION))
    if Result:
        return Result
    d_item=get_dept_as_dict()
    Result=[]
    if (user.is_superuser) or (user.is_alldept):
        # return Result
        rs_dept=department.objects.all().order_by('parent','DeptNumber')
        for t in rs_dept:
            Result.append(int(t.DeptID))
    else:
        rs_dept = DeptAdmin.objects.filter(user=user).order_by("dept")
        for t in rs_dept:
            if t.iscascadecheck==1:
                rs=[]
                AllChildrens(int(t.dept_id),d_item,rs)
                Result+=rs
            Result.append(int(t.dept_id))
    Result=list(set(Result))
    cache.set("%s_userdepts_%s_%s"%(settings.UNIT,user.id,settings.DEPTVERSION),Result,timeout=86400)
    return Result

#把所有部门数据预先加载成字典数据，保存到cache,这是其他部门操作函数的基础。{0:[1,2,3],1:[5,6,7,8],2:[],3:[],5:[],6:[],7:[],8:[10,11],10:[],11:[]}
def get_dept_as_dict(user=None):
    global d_deptDict
    global deptversion
    ver=GetParamValue('DEPTVERSION')
    if deptversion<>ver:
        d_deptDict=cache.get("%s_deptdict_%s"%(settings.UNIT,ver))
    if d_deptDict:
        deptversion=ver
        return d_deptDict
    else:
        d_deptDict=cache.get("%s_deptdict_%s"%(settings.UNIT,ver))
        if d_deptDict:
            deptversion=ver
            return d_deptDict

    dept_list=[]
    ll={}
    j=0
    i=0

    nt=datetime.datetime.now()
    secs=(nt.day*24*3600+nt.hour*3600+nt.minute*60+nt.second)/60
    is_loading=cache.get("_is_loading_%s"%(secs))
    #if is_loading:
    #	return dept_list
    #else:
    #	cache.set("_is_loading_%s"%(secs),1)
    #objs=department.objects.filter(Q(DelTag=None)|Q(DelTag=0)).order_by('parent','DeptNumber')
    objs=department.objects.exclude(DelTag=1).order_by('parent','DeptNumber')
    for o in objs:
        j=j+1
        try:
            ll[int(o.parent)].append(int(o.DeptID))
        except:
            ll[int(o.parent)]=[]
            ll[int(o.parent)].append(int(o.DeptID))


    ll['count']=j
    cache.set("%s_deptdict_%s"%(settings.UNIT,ver),ll)
    cache.delete("_is_loading_%s"%(secs))
    return ll






def getChildFromCache(request):
    f=cache.get("%s_haschilds_%s_%s"%(settings.UNIT,request.user.id,settings.DEPTVERSION))     #f is dict
    return f
def getallChildFromCache(request):
    f=cache.get("%s_allchilds"%(settings.UNIT))     #f is dict
    return f
#获取授权的子部门	
def hasChildren(deptid,request,cacheDept,isSet=1,ret=[1]):
    f=cacheDept
    if f:
        if deptid in f.keys():
            return f[deptid]
    else:
        f={}
    a=department.objects.all()
    if not 1 in ret:
        ret.append(1)
    if (request.user.is_superuser) or (request.user.is_alldept):
        objl=department.objects.filter(parent=deptid).values_list('DeptID', flat=True).order_by('DeptNo','DeptID')
        f[deptid]=objl
    else:
        ulist=userDeptList(request.user)
        objs=department.objects.filter(parent__exact=deptid).order_by('DeptNo',"DeptID")
        dd=[]
        for t in objs:
            if t.DeptID in ulist:dd.append(t.DeptID)
        f[deptid]=dd
    if isSet:
        cache.set("%s_haschilds_%s_%s"%(settings.UNIT,request.user.id,settings.DEPTVERSION),f)
    return f[deptid]

#获取当前部门下的子部门	，作废
def AllChildren(deptid,request,cacheDept,isSet=1,ret=[1]):
    f=cacheDept
    if f:
        if deptid in f.keys():
            return f[deptid]
    else:
        f={}
    if not 1 in ret:
        ret.append(1)
    objl=department.objects.filter(parent=deptid).values_list('DeptID', flat=True).order_by('DeptNo','DeptID')
    f[deptid]=objl
    if isSet:
        cache.set("%s_allchilds"%(settings.UNIT),f,timeout=86400)
    return f[deptid]

#获取所有授权的子部门
#def getChildDepts(Curid,request,cdept,start=[],ret=[1]):
#	for d in hasChildren(Curid,request,cdept,0,ret):
#		start.append(d)
#		getChildDepts(d,request,cdept,start,ret)
def getChildDepts(Curid,result,d_item,userDeptList):
    try:
        d_list=d_item[Curid]
    except:
        d_list=[]
    for d in d_list:
        if userDeptList and userDeptList[0]==-1:
            result.append(d)
            getChildDepts(d,result,d_item,userDeptList)
        else:
            if d in userDeptList:
                result.append(d)
                getChildDepts(d,result,d_item,userDeptList)


#获取所有子部门
def getAllChildDept(Curid,request,cdept,start=[],ret=[1]):
    for d in AllChildren(Curid,request,cdept,0,ret):
        start.append(d)
        getAllChildDept(d,request,cdept,start,ret)

#获取所有授权子部门及其本身
def getAllAuthChildDept(curid,request=None):
    curid=int(curid)
    result=[curid]
    #if curid=='null':
    #	result=userDeptList(request.user)
    #else:
    #	cdept=getChildFromCache(request)
    #	curid=int(curid)
    #	ret=[]
    #	result.append(curid)
    #	try:
    #		getChildDepts(curid,request,cdept,result,ret)
    #	except:
    #		pass
    #	result=result[:999]
    #	if ret:
    #		cache.set("%s_haschilds_%s_%s"%(settings.UNIT,request.user.id,GetParamValue('DEPTVERSION')),cdept)
    d_item=get_dept_as_dict(request.user)
    if (request.user.is_superuser) or (request.user.is_alldept):
        userDepts=[-1]  #-1表示超级管理员
    else:
        userDepts=userDeptList(request.user)
    try:
        getChildDepts(curid,result,d_item,userDepts)
    except:
        pass
    return result

#获取所有子部门及其本身，作废
def getAllChildDepts(curid,request=None):
    if request.user.is_superuser or request.user.is_alldept:
        result=[]
        curid=int(curid)
        alldept=getallChildFromCache(request)
        ret=[]
        result.append(curid)
        getAllChildDept(curid,request,alldept,result,ret)
        if ret:
            cache.set("%s_allchilds"%(settings.UNIT),alldept,timeout=86400)
        return result
    else:
        return getAllAuthChildDept(curid,request)

#得到所有可用的父部门,此处不管管理员是否能管到该部门，此函数是修改部门的上级部门时调用		
def getAvailableParentDepts(dataKey,request):
    if not dataKey:return []
    if dataKey==1:return [1]
    obj=department.objByID(dataKey)
    if obj.parent==1:
        pDepts=department.objects.filter(Q(parent=1)|Q(parent=0)).values_list('DeptID',flat=True)
    else:
        d_item=get_dept_as_dict()
        childDepts=[]
        AllChildrens(dataKey,d_item,childDepts)
        pDepts=department.objects.exclude(DeptID__in=childDepts).values_list('DeptID',flat=True)
    pDepts=list(pDepts)
    try:
        pDepts.remove(dataKey)
    except Exception,e:
        pass
    return pDepts

#获取用户的权限
def getAllAuthPermissions(user):
    if user.is_superuser:return []
    sql="select gp.permission_id from auth_group_permissions gp where gp.group_id in (select group_id from auth_user_groups where auth_user_groups.myuser_id=%s)"
    cs=customSqlEx(sql,[user.id],False)
    result=set([int(row[0]) for row in cs.fetchall()])  #传到前台的权限id为 带L的数据 强制转换成整型
    result=list(result)
    return result

#此函数作废，以后设备和部门关联，不和用户关联
def userIClockList(user):
    Result=[]
    depts=userDeptList(user)
    if depts:
        rs_SN = iclock.objects.filter(DeptID__in=depts).exclude(DelTag=1)#filter(Q(DelTag__isnull=True)|Q(DelTag=0))
        Result=[row.SN for row in rs_SN]
    return Result
#此函数作废，以后设备和部门关联，不和用户关联
#def AuthedIClockList(user):
#	Result=cache.get("%s_iclockdepts_%s"%(settings.UNIT, user.id))
#	if Result:
#		return Result
#	Result=[]
#	dept_list=userDeptList(user)
#	if dept_list:
#		try:
#			rs_SN = IclockDept.objects.filter(dept__in=dept_list)
#		except Exception,e:
#			print "%s====="%e
#		Result=[row.SN_id for row in rs_SN]
#		Result=list(set(Result))
#	cache.set("%s_iclockdepts_%s"%(settings.UNIT,user.id),Result)
#	return Result

def AuthedIClockList(user):
    Result=cache.get("%s_iclockdepts_%s_%s"%(settings.UNIT, user.id,settings.DEPTVERSION))
    if Result:
        return Result
    Result=[]
    dept_list=userDeptList(user)
    if dept_list:
        try:
            rs_SN = IclockDept.objects.filter(dept__in=dept_list).exclude(SN__DelTag=1)
        except Exception,e:
            print "%s====="%e
        Result=[row.SN_id for row in rs_SN]
    rsdept=[]
    rs_dept = DeptAdmin.objects.filter(user=user).order_by("dept")
    for rs in rs_dept:
        rsdept.extend(rs.dept.AllParentsDeptID())
    result=[]
    if rsdept:
        rsdept=list(set(rsdept))
        try:
            rs_SN = IclockDept.objects.filter(dept__in=rsdept,iscascadecheck=1).exclude(SN__DelTag=1)
        except Exception,e:
            print "%s====="%e
        result=[row.SN_id for row in rs_SN]
    Result.extend(result)
    Result=list(set(Result))
    cache.set("%s_iclockdepts_%s_%s"%(settings.UNIT,user.id,settings.DEPTVERSION),Result)
    return Result

#此函数作废，以后设备和部门关联，不和用户关联
def getUserIclocks(user):
    return AuthedIClockList(user)
#	return userIClockList(user)

def fieldVerboseName(model, fieldName):
    try:
        f = model._meta.get_field(fieldName)
        return f.verbose_name
    except:
        pass



def InitStatus():
    pass

def GetRecordStatus():
    p=cache.get("%s_%s"%(settings.UNIT, 'all_record_states'))
    if p:return p
    dd={}
    l=[]
    j=0
    for i in ATTSTATES:
        d=u"%s"%(i[1])#(dict(ATTSTATES).get(i[0]))
        #print "1111",d
        dd['pName']=u'%s'%d
        dd['pValue']=unicode(j)
        dd['id']=j+10
        dd['symbol']=i[0]
        pKey='opt_check_'+str(j+10)
        dd['pKey']=pKey
        l.append(dd.copy())
        j=j+1
#		pName='opt_check_'+dd['pValue']
    attp=AttParam.objects.filter(ParaName__startswith='opt_check_').order_by('ParaName')   #表示考勤系统规定的六种状态
    if attp:
        j=0
        for t in attp:
            if t.ParaType=='0':
                for i in l:
                    if i['pKey']==t.ParaName[:12]:
                        i['pValue']=t.ParaName[13:]
            else:
                dd={}
                dd['pName']=t.ParaValue
                dd['pValue']=t.ParaName[14:]
                pKey='opt_check_100_'+t.ParaName[14:]
                dd['pKey']=pKey
                dd['id']=100
                dd['symbol']=t.ParaName[14:]
                j=j+1
                l.append(dd.copy())
    cache.set("%s_%s"%(settings.UNIT,'all_record_states'),l)
    return l
#通过记录状态值得到显示名称
def getRecordName(state):
    gStatus=GetRecordStatus()
    ret=state
    #if state=='I':#为了兼容老的数据库内容
        #ret=u'%s'%(_("Check in"))
    #elif state=='O':#为了兼容老的数据库内容
        #ret=u'%s'%(_("Check out"))
    for t in gStatus:
        if t['symbol']==state or t['pValue']==state:
            ret=u'%s'%t['pName']
            break
    return ret
#通过记录状态值得到数据库中保存的状态值
def getRecordSym(state):
    gStatus=GetRecordStatus()
    ret=state
    #if state=='I':#为了兼容老的数据库内容
        #ret=u'%s'%(_("Check in"))
    #elif state=='O':#为了兼容老的数据库内容
        #ret=u'%s'%(_("Check out"))
    for i in gStatus:
        if i['pValue']==state:
            ret=i['symbol']
            break
    return ret

"""有关判断设备归属的函数========================================="""

def getDepartmentBySN(SN):
    """返回的为[]时表示归属所有部门"""
    result=[]
    d_item=get_dept_as_dict()
    objs=IclockDept.objects.filter(SN=SN).order_by("dept")
    for t in objs:
        deptid=int(t.dept_id)
        if t.iscascadecheck==1:
            if deptid==1:
                result=[-1]
                return result
            else:
                childDepts=[]
                AllChildrens(deptid, d_item,childDepts)
                result.append(deptid)
                result+=childDepts
        else:
            result.append(deptid)

#	if not result:       #当设备没有配置归属时，系统默认归属总公司
#		result=[1]
    result=list(set(result))
    return result

def getZoneBySN(SN):
    """返回的为[]时表示归属所有区域"""
    result=[]
    objs=IclockZone.objects.filter(SN=SN)
    for t in objs:
        id=int(t.zone_id)
        result.append(id)
    result=list(set(result))
    return result

def getDiningBySN(SN):
    """返回的为[]时表示归属所有餐厅"""
    result=[]
    objs=IclockDininghall.objects.filter(SN=SN).exclude(SN__DelTag=1)
    for t in objs:
        id=int(t.dining_id)
        result.append(id)
    result=list(set(result))
    return result



def getDeviceListByDept(curid):
    """根据部门获取所分配的设备"""
    curid=int(curid)
    deptlist=AllParents(curid)
    deptlist.append(curid)
    result=[]
    objs=IclockDept.objects.filter(dept__in=deptlist).exclude(SN__DelTag=1)
    for t in objs:
        deptid=int(t.dept_id)
        if deptid==curid:
            result.append(t.SN_id)
        else:
            if t.iscascadecheck==1:
                result.append(t.SN_id)
    return list(set(result))


"""end==================================="""

def getOwnedUsers(userid,dataname,start=[]):
    """获取拥有的用户"""
    userid=int(userid)
    if userid not in start:
        start.append(userid)
    objs=UserAdmin.objects.filter(user=userid,dataname=dataname)
    for t in objs:
        owned=int(t.owned)
        if owned not in start:
            start.append(owned)
            getOwnedUsers(owned,dataname,start)

#用于向控制器中添加门
def auto_add_door(dev,in_count,out_count):
    if dev.ProductType not in [4,5,15,25]:return

    f4to2i=0
    if dev.ProductType in [5,15,25]:
        f4to2i=GetParamValue('f4to2_%s'%dev.SN,'0')
        if f4to2i=='on':
            f4to2i=1
        f4to2i=int(f4to2i)

    iCount=	AccDoor.objects.filter(device=dev).count()
    doors=int(dev.LockFunOn)
    if f4to2i==1 and doors==4:
        doors=2

    if iCount==doors:return
    if not dev.LockFunOn:return
#	AccDoor.objects.filter(device=dev).delete()
    if in_count==0:
        t_obj=device_options.objects.filter(SN=dev.SN,ParaName='AuxInCount')
        if t_obj:
            try:
                in_count=int(t_obj[0].ParaValue)
            except:
                pass
    if out_count==0:
        t_obj=device_options.objects.filter(SN=dev.SN,ParaName='AuxOutCount')
        if t_obj:
            try:
                out_count=int(t_obj[0].ParaValue)
            except:
                pass
    InCount=AuxIn.objects.filter(device=dev).count()
    OutCount=AuxOut.objects.filter(device=dev).count()
    if in_count!=InCount and InCount>0:
        AuxIn.objects.filter(device=dev).delete()
    if out_count!=OutCount and OutCount>0:
        AuxOut.objects.filter(device=dev).delete()





    for i in range(doors+1,iCount+1):
        Doors=AccDoor.objects.filter(device = dev, door_no=i)#.delete()
        #for t in Doors:
        #	level_door.objects.filter(door=t).delete()
        Doors.delete()
    for i in range(iCount,doors):
        try:
            opentype=OPENDOOR_CHOICES_DEFAULT
            if dev.ProductType in [25]:
                opentype=21
            AccDoor(device_id = dev.SN, door_no = (i+1), opendoor_type=opentype,door_name = u'%s-%s' % (dev.SN, str(i+1))).save(force_insert=True)
        except Exception,e:#特殊情况下，门有效时间段ID可能不是1，上面的方法添加门会失败
            dDict = {'device_id': dev.SN, 'door_no': i + 1, 'opendoor_type':6,'door_name': u'%s-%s' % (dev.SN, str(i + 1))}
            obj=timezones.objects.first()
            if obj:
                dDict['lock_active_id']=obj.id
            obj=AccWiegandFmt.objects.first()
            if obj:
                dDict['wiegand_fmt_id']=obj.id

            sql, params = getSQL_insert_new(AccDoor._meta.db_table, dDict)
            customSql(sql, params)
    if in_count!=InCount:
        for i in range(int(in_count)):
            AuxIn(device = dev, aux_no = (i+1), aux_name = u'%s-%s' % (_(u'辅助输入'), str(i+1)),printer_name=u'%s-%s' % (_(u'辅助输入'), str(i+1))).save(force_insert=True)
    if out_count!=OutCount:
        for i in range(int(out_count)):
            AuxOut(device = dev, aux_no = (i+1), aux_name = u'%s-%s' % (_(u'辅助输出'), str(i+1)),printer_name=u'%s-%s' % (_(u'辅助输出'), str(i+1))).save(force_insert=True)
    from mysite.core.cmdproc import set_dooroptions
    if dev.ProductType in [5,15]:
        set_dooroptions([],[dev])


def getoptionsAttParam(device=None):
    #keys=["ErrorDelay","Delay","Realtime","TransTimes","TransInterval","TransType"]
    defvalues={"ErrorDelay":60,"Delay":30,"Realtime":1,"TransTimes":'00:00;14:05',"TransInterval":1,"TransType":'1111111111','compwd':''}
    if not device:
        defvalues={"ErrorDelay":60,"Delay":60,"Realtime":1,"TransTimes":'00:00;14:05',"TransInterval":1,"TransType":'1111111111','compwd':''}
    if hasattr(device,'ProductType') and device.ProductType in [5,15,25]:
        defvalues={"ErrorDelay":60,"Delay":20,"Realtime":1,"TransTimes":'00:00;14:05',"TransInterval":1,"TransType":'1111111111','compwd':''}
    ll={}
    keys=defvalues.keys()
    for k in keys:
        ll[k]=GetParamValue(k,defvalues[k])
    return ll
