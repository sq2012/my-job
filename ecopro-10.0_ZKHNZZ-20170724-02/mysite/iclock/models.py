# coding: utf-8
from django.db import models, connection,connections
from django.db.models import Q
from django.contrib.auth.models import  Permission, Group
import datetime
import os
import string
#from django.contrib import auth,admin
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from mysite.utils import *
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelChoiceIterator
import copy
from django.contrib.auth import get_user_model
from mysite.base.models import *
#from django.forms import ModelForm
#from django import forms
from mysite.utils import *
from django.db.models.fields import AutoField, FieldDoesNotExist
from mysite.core.tools import *

(bioZero, bioFinger, bioFace,bioSound,bioIris,bioRetina,bioFriction,bioVein,bioHand)=range(9)

def transAbnormiteName(abnormiteID):
    if abnormiteID==0:
        return _('Valid')
    elif abnormiteID==1:
        return _('Invalid')
    elif abnormiteID==2:
        return _('Repeat')
    elif abnormiteID==3:
        return _('ErrorState')
    elif abnormiteID==4:
        return _('Out')
    elif abnormiteID==5:
        return _('OT')
    elif abnormiteID==6:
        return _('FreeOT')
    elif abnormiteID==7:
        return _('AutoSch')
    else:
        return _('ErrorState')
JIEZHUANG_STATES=(
                  (0,_(u'否')),
                  (1,_(u'是')),
)
AUDIT_STATES=(
    (0,_('Apply')),
#	(1,_('Auditing')),
    (2,_('Accepted')),
    (3,_('Refused')),
#	(4,_('Paused')),
#	(5,_('Re-Apply')),
    (6,_('Again')),
#	(7,_('Cancel_leave'))
)
AUDIT_STATES_PROCESS=(
#	(1,_('Auditing')),
    (2,_('Accepted')),
    (3,_('Refused')),
#	(4,_('Paused')),
#	(5,_('Re-Apply')),
    (6,_('Again')),
)
DEPT_NAME=_("department")
DEPT_NAME_2=_("department name")
DEPT_NAME_ID=_("department number")

#各种机型常量
DEVICE_C3_100 = '4'
DEVICE_C3_200 = '1'
DEVICE_C3_400 = '2'
DEVICE_C3_400_TO_200 = '7'
DEVICE_C4_200 = '5'
DEVICE_C4_400 = '3'
DEVICE_C4_400_TO_200 = '6'
DEVICE_C3_160 = '8'
DEVICE_C3_260 = '9'
DEVICE_C3_460 = '10'
DEVICE_ELEVATOR   = '11'
DEVICE_ACCESS_CONTROL_DEVICE = '12' #一体机



def getDefaultDept():
    """ 获取默认部门；没，则创建
        """
    dept=None
    try:
        dept = department.objects.filter(parent=0).order_by('DeptID')
        if dept:
            dept =dept[0]
        else:
            d = department.objects.all().order_by('DeptID')
            dept=d[0]
    except:
        pass

    return dept

class NestedDeptException(Exception): pass

class department(models.Model):
#	DeptID = models.IntegerField(DEPT_NAME_ID,primary_key=True)
    DeptID=models.AutoField(db_column="DeptID", primary_key=True, null=False,editable=False)
    DeptNumber = models.CharField(_(u'单位编号'),blank=False,null=False,max_length=40,help_text=_(u'最大长度不超过40个字符,修改单位编号后不会改变人员所在的单位。'))   #用于显示的编号
    DeptName = models.CharField(DEPT_NAME_2,max_length=40)
    parent = models.IntegerField(db_column="supdeptid",verbose_name=_('parent'), null=False, blank=True, default=0)
    #DeptNo = models.IntegerField(verbose_name=_(u'序号'), null=True, blank=True, default=0,editable=False)
    DeptAddr = models.CharField(_(u'单位地址'),max_length=50,blank=True,null=True)
    DeptPerson = models.CharField(_(u'联系人'),max_length=20,blank=True,null=True)
    DeptPhone = models.CharField(_(u'联系电话'),max_length=20,blank=True,null=True)
    DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)


    def Parent(self):
        if self.parent:
            return self.objByID(self.parent)
        return None
    @staticmethod
    def clear():
#		deptid=getDefaultDept().DeptID
        for dept in department.objects.all():#.exclude(DeptID=deptid):
            dept.delete()
        UpdateDeptCache()
        cache.delete("%s_allchilds"%(settings.UNIT))

    def AllParents(self):
        ps=[]
        d=self
        for i in range(100):
            try:
                d=self.objByID(d.parent)
                ps.append(d)
                if d==self: break
            except:
                break
        return ps
    def AllParentsDeptID(self):
        ps=[]
        d=self
        for i in range(100):
            try:
                d=self.objByID(d.parent)
                ps.append(d.DeptID)
                if d==self: break
            except:
                break
        return ps
    def DeptLongName(self):
        ps=self.DeptName
        d=self
        for i in range(100):
            try:
                d=self.objByID(d.parent)
                #if d==getDefaultDept(): break
                if d.parent==0: break
                ps="%s->%s"%(ps,d.DeptName)
            except:
                break
        return ps
    def Children(self):
        return department.objects.filter(parent=self.DeptID)
    def AllChildren(self, start=[]):
        for d in self.Children():
            if d not in start:
                start.append(d)
                d.AllChildren(start)

    @staticmethod
    def objByID(id):
        if id==None: return None
        d=cache.get("%s_iclock_dept_%s_%s"%(settings.UNIT,id,settings.DEPTVERSION))
        if d: return d
        try:
            d=department.objects.get(DeptID=id)
        except:
            d=None
        if d:
            cache.set("%s_iclock_dept_%s_%s"%(settings.UNIT,id,settings.DEPTVERSION),d)
        return d
    @staticmethod
    def objByNumber(DeptNum):
        if DeptNum==None: return None
        d=cache.get("%s_iclock_deptNum_%s_%s"%(settings.UNIT,DeptNum,settings.DEPTVERSION))
        if d: return d
        try:
            d=department.objects.get(DeptNumber=DeptNum,DelTag = 0)
        except:
            d=None
        if d:
            cache.set("%s_iclock_deptNum_%s_%s"%(settings.UNIT,DeptNum,settings.DEPTVERSION),d)
        return d
    def __unicode__(self):
        try:
            return u"%s %s"%(self.DeptNumber, self.DeptName.decode("utf-8"))
        except:
            return u"%s %s"%(self.DeptNumber, unicode(self.DeptName))
    def save(self):
        try:
            UpdateDeptCache()
            #cache.delete("%s_iclock_dept_%s_%s"%(settings.UNIT,self.DeptID,settings.DEPTVERSION))
            #cache.delete("%s_iclock_deptNum_%s_%s"%(settings.UNIT,self.DeptNumber,settings.DEPTVERSION))

            cache.delete("%s_allchilds"%(settings.UNIT))
        except:pass

        #if (department.objects.all().count()==0) or (not self.parent) or (int(self.parent)==0) or ( department.objects.filter(DeptID=self.parent).count()>0):
        #	if (not self.parent) or (self.DeptID==1): self.parent=0
        #	if self in self.AllParents():
        #		raise NestedDeptException(_('Nested department parent'))
        #else:#改为对于没有父部门时存为一级部门
        #    self.parent=0
        try:
            d=department.objects.get(DeptNumber=self.DeptNumber)
            if d.DelTag==1:
                self.DelTag=0
                self.DeptID=d.DeptID
                self.parent=d.parent
                super(department,self).save()
            else:
                models.Model.save(self)

        except:
            models.Model.save(self)


            #raise Exception("Parent is not exist.")
    def delete(self):
        try:
            UpdateDeptCache()
            cache.delete("%s_allchilds"%(settings.UNIT))
        except: pass
        self.DelTag=1
        super(department, self).save()
    def empCount(self):
        return employee.objects.filter(DeptID=self,OffDuty=0).exclude(DelTag=1).count()
    @staticmethod
    def colModels():
        return [
            {'name':'DeptID','width':100,'hidden':True},
            {'name':'DeptNumber','width':100,'label':unicode(department._meta.get_field('DeptNumber').verbose_name)},
            {'name':'DeptName','width':220,'label':unicode(department._meta.get_field('DeptName').verbose_name)},
            {'name':'Parent','index':'parent','width':220,'label':unicode(_('parent'))},
            {'name':'DeptAddr','width':220,'label':unicode(department._meta.get_field('DeptAddr').verbose_name)},
            {'name':'DeptPerson','width':80,'label':unicode(department._meta.get_field('DeptPerson').verbose_name)},
            {'name':'DeptPhone','width':80,'label':unicode(department._meta.get_field('DeptPhone').verbose_name)},
            {'name':'empCount','sortable':False,'width':80,'label':unicode(_('EmpCount'))}
            #{'name':'DeptNo','sortable':False,'width':80,'label':unicode(u'序号')}
            ]
    class Admin:
        search_fields = ['DeptNumber','DeptName']
        @staticmethod
        def initial_data():
            if department.objects.all().count()==0:
                department( DeptName=u"总单位",DeptNumber='1', parent=0).save()

    class Meta:
        db_table = 'departments'
#		verbose_name=_("transaction")
        verbose_name=DEPT_NAME
        verbose_name_plural=verbose_name
        unique_together = (("DeptNumber",),)

# 获得部门的下级所有部门
def getChildDept(dept):
    child_list=[]
    dept.AllChildren(child_list)
    return child_list


BOOLEANS=((0,_("No")),(1,_("Yes")),)
AC_Group_BOOLEANS=((0,_(u"自定义时间段")),(1,_(u"使用组设置")),)
DEV_STATUS_OK=1
DEV_STATUS_TRANS=2
DEV_STATUS_OFFLINE=3
DEV_STATUS_PAUSE=0

nocmd_device_cname="%s_nocmd_device_%s"

def deviceCmd(device):
    nocmd_device=[]
    nocmd_device=cache.get(nocmd_device_cname%(settings.UNIT,device.SN))
    nowCmds=[]
    #nocmd_device=None#测试用，正式的要注释
    if nocmd_device:
        if device.State!=1:
            device.State=1
            laKey="iclock_la_"+device.SN  #实现保存
            cache.delete(laKey)
    else: #and (device.SN in nocmd_device):
        cmds=devcmds.objects.filter(SN=device,CmdTransTime__isnull=True).order_by('id')[:50]
#		cmds=devcmds.objects.filter(SN=device,CmdOverTime__isnull=True).order_by('id')[:50]
        #cmds=devcmds.objects.filter(SN=device,CmdOverTime__isnull=True).exclude(CmdTransTime__gt=datetime.datetime.now()-datetime.timedelta(seconds=300)).order_by('id')[:100]
        if not cmds:
            #if not nocmd_device: nocmd_device=[]
            #nocmd_device.append(device.SN)
            cache.set(nocmd_device_cname%(settings.UNIT,device.SN), 1)
            if device.State!=1:
                device.State=1
                laKey="iclock_la_"+device.SN  #实现保存
                cache.delete(laKey)
        else:
            now=datetime.datetime.now()
            for cmd in cmds:
                if cmd.CmdCommitTime<=now: nowCmds.append(cmd)
            if nowCmds:
                if len(nowCmds)>20:
                    device.State=2
            else:
                device.State=1
    return nowCmds

import socket
sNotify = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def deviceHasCmd(deviceSN):
    try:
        cache.delete(nocmd_device_cname%(settings.UNIT,deviceSN))
    except: pass
def sendRecCMD(device):
    try:
        ip=device.IPAddress
        if ip: sNotify.sendto("R-CMD", (ip, 4374))
#		print "Notify: ", ip, 4374
    except:
#		print ip
#		errorLog()
        pass

def getValueFrom(data, key):
    d={}
    for v in data.split("\n"):
        if v:
            if v[-1] in ['\r','\n']: v=v[:-1]
        nv=v.split("=")
        if len(nv)>1:
            if key==nv[0]:
                return "=".join(nv[1:])
    return ""


def setValueFor(data, key, value):
    d={}
    for line in data.split("\n"):
        if line:
            v=line.split("\r")[0]
        else:
            v=line
        nv=v.split("=", 1)
        if len(nv)>1:
            try:
                v=str(nv[1])
                d[nv[0]]=v
            except:
#print nv
                pass
    if key:
        d[key]=value
    return "\n".join(["%s=%s"%(k, d[k]) for k in d.keys()])

def mergeValues(data1, data2):
    return setValueFor(data1+"\n"+data2, "","")
last_reboot_cname="%s_lastReboot"%settings.UNIT	

def updateLastReboot(iclocks):
    lastReboot=cache.get(last_reboot_cname)
    d=datetime.datetime.now()
    #rebInterval=(REBOOT_CHECKTIME>0 and REBOOT_CHECKTIME or 10)
    ips=[]
# #	print "lastReboot:",lastReboot
#     if not lastReboot: lastReboot={}
#     for i in iclocks:
#         ip=i.IPAddress()
#         if ip:
#             if ip in lastReboot:
#                 if d-lastReboot[ip]>datetime.timedelta(0,rebInterval*60):
#                     ips.append(ip)
#                     lastReboot[ip]=d
# #					print "reboot:", ip, lastReboot[ip]
#             else:
#                 ips.append(ip)
#                 lastReboot[ip]=d
#     if ips: cache.set(last_reboot_cname, lastReboot, rebInterval*60)
#	print "lastReboot:",lastReboot
    return ips

def removeLastReboot(ip):
    lastReboot=cache.get(last_reboot_cname)
    if not lastReboot: return
    if ip in lastReboot:
        lastReboot.pop(ip)
        cache.set(last_reboot_cname, lastReboot)
def checkTime(t):
    if str(type(t))=="<type 'datetime.datetime'>":
        return datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second)
    elif str(type(t))=="<type 'datetime.time'>":
        return datetime.datetime(1900,12,30,t.hour,t.minute,t.second)
    elif str(type(t))=="<type 'datetime.date'>":
        return datetime.datetime(t.year,t.month,t.day,0,0,0)
def getDevice(n):
    n=n and string.strip(n) or ""
    if not n: return None
    dev=cache.get("iclock_"+n)
    if dev:
        return dev
    dev=iclock.objects.get(SN=n)
    #if dev.DelTag==1:
    #	auto_reg=GetParamValue('opt_basic_dev_auto','1')
    #	if auto_reg!='0':
    #		dev.DelTag=0
    #		dev.save()
    dev.PvFunOn=0
    dev.FvFunOn=0
    objs=device_options.objects.filter(SN=n,ParaName__in = ['PvFunOn','FvFunOn','FvVersion','PvVersion'])#判断设备支持的类型
    for t in objs:
        if t.ParaName=='PvFunOn' and t.ParaValue=='1':
            dev.PvFunOn=1#掌

        elif t.ParaName=='FvFunOn' and t.ParaValue=='1':
            dev.FvFunOn=1#指静脉
        elif t.ParaName=='FvVersion':
            dev.FvVersion=t.ParaValue
        elif t.ParaName=='PvVersion':
            dev.PvVersion=t.ParaValue

    if dev.ProductType in [11,12,13,14]:

        if not hasattr(dev,'ding'):
            try:
                from mysite.ipos.models import IclockDininghall
                obj=IclockDininghall.objects.get(SN=dev)
                dev.ding=obj.dining_id
            except:
                dev.ding=None




    cache.set("iclock_"+n, dev)
    cache.set("iclock_old_"+n, dev)
    return dev

TIMEZONE_CHOICES=(
    (-12,'Etc/GMT-12'),
    (-11,'Etc/GMT-11'),
    (-10,'Etc/GMT-10'),
    (-9,'Etc/GMT-9'),
    (-8,'Etc/GMT-8'),
    (-7,'Etc/GMT-7'),
    (-6,'Etc/GMT-6'),
    (-5,'Etc/GMT-5'),
    (-4,'Etc/GMT-4'),
    (-3,'Etc/GMT-3'),
    (-2,'Etc/GMT-2'),
    (-1,'Etc/GMT-1'),
    (0,'Etc/GMT'),
    (1,'Etc/GMT+1'),
    (2,'Etc/GMT+2'),
    (3,'Etc/GMT+3'),
    (4,'Etc/GMT+4'),
    (5,'Etc/GMT+5'),
    (6,'Etc/GMT+6'),
    (7,'Etc/GMT+7'),
    (8,'Etc/GMT+8'),
    (9,'Etc/GMT+9'),
    (10,'Etc/GMT+10'),
    (11,'Etc/GMT+10'),
    (12,'Etc/GMT+12'),
    (13,'Etc/GMT+13'),
)
#TIMEZONES_CHOICES=(
#	(1,'1'),
#	(2,'2'),
#	(3,'3'),
#	(4,'4'),
#	(5,'5'),
#	(6,'6'),
#	(7,'7'),
#	(8,'8'),
#	(9,'9'),
#	(10,'10'),
#	(11,'11'),
#	(12,'12'),
#	(13,'13'),
#	(14,'14'),
#	(15,'15'),
#	(16,'16'),
#	(17,'17'),
#	(18,'18'),
#	(19,'19'),
#	(20,'20'),
#	(21,'21'),
#	(22,'22'),
#	(23,'23'),
#	(24,'24'),
#	(25,'25'),
#	(26,'26'),
#	(27,'27'),
#	(28,'28'),
#	(29,'29'),
#	(30,'30'),
#	(31,'31'),
#	(32,'32'),
#	(33,'33'),
#	(34,'34'),
#	(35,'35'),
#	(36,'36'),
#	(37,'37'),
#	(38,'38'),
#	(39,'39'),
#	(40,'40'),
#	(41,'41'),
#	(42,'42'),
#	(43,'43'),
#	(44,'44'),
#	(45,'45'),
#	(46,'46'),
#	(47,'47'),
#	(48,'48'),
#	(49,'49'),
#	(50,'50'),
#)

#ACGroupS_CHOICES=(
#	(1,'1'),
#	(2,'2'),
#	(3,'3'),
#	(4,'4'),
#	(5,'5'),
#	(6,'6'),
#	(7,'7'),
#	(8,'8'),
#	(9,'9'),
#	(10,'10'),
#	(11,'11'),
#	(12,'12'),
#	(13,'13'),
#	(14,'14'),
#	(15,'15'),
#	(16,'16'),
#	(17,'17'),
#	(18,'18'),
#	(19,'19'),
#	(20,'20'),
#	(21,'21'),
#	(22,'22'),
#	(23,'23'),
#	(24,'24'),
#	(25,'25'),
#	(26,'26'),
#	(27,'27'),
#	(28,'28'),
#	(29,'29'),
#	(30,'30'),
#	(31,'31'),
#	(32,'32'),
#	(33,'33'),
#	(34,'34'),
#	(35,'35'),
#	(36,'36'),
#	(37,'37'),
#	(38,'38'),
#	(39,'39'),
#	(40,'40'),
#	(41,'41'),
#	(42,'42'),
#	(43,'43'),
#	(44,'44'),
#	(45,'45'),
#	(46,'46'),
#	(47,'47'),
#	(48,'48'),
#	(49,'49'),
#	(50,'50'),
#	(51,'51'),
#	(52,'52'),
#	(53,'53'),
#	(54,'54'),
#	(55,'55'),
#	(56,'56'),
#	(57,'57'),
#	(58,'58'),
#	(59,'59'),
#	(60,'60'),
#	(61,'61'),
#	(62,'62'),
#	(63,'63'),
#	(64,'64'),
#	(65,'65'),
#	(66,'66'),
#	(67,'67'),
#	(68,'68'),
#	(69,'69'),
#	(70,'70'),
#	(71,'71'),
#	(72,'72'),
#	(73,'73'),
#	(74,'74'),
#	(75,'75'),
#	(76,'76'),
#	(77,'77'),
#	(78,'78'),
#	(79,'79'),
#	(80,'80'),
#	(81,'81'),
#	(82,'82'),
#	(83,'83'),
#	(84,'84'),
#	(85,'85'),
#	(86,'86'),
#	(87,'87'),
#	(88,'88'),
#	(89,'89'),
#	(90,'90'),
#	(91,'91'),
#	(92,'92'),
#	(93,'93'),
#	(94,'94'),
#	(95,'95'),
#	(96,'96'),
#	(97,'97'),
#	(98,'98'),
#	(99,'99'),
#)

#ACUnlockCombS_CHOICES=(
#	(1,'1'),
#	(2,'2'),
#	(3,'3'),
#	(4,'4'),
#	(5,'5'),
#	(6,'6'),
#	(7,'7'),
#	(8,'8'),
#	(9,'9'),
#	(10,'10'),
#)

#PURPOSE=(
#	(9,_('Checking Attendance')),
#	(1,_('Access')),
#	(2,_('Expends')),
#	(3,_('Attendance and Access')),
#	(4,_('Attendance and Expends')),
#	)

PURPOSE=(
    (0,_('No')),
    (1,_('Yes')),
)
ALGVER=(
    (10,_('ZKFinger VX10.0')),
    (9,_('ZKFinger VX9.0')),
    )
AUTHENTICATION=(
    (1,_('Non-Combined verify')),#非组合验证
    (2,_('Combined verify')),#组合验证
)


#ACGroup_VerifyType=(#门禁验证方式
#	(0,_('FP/PW/RF/FACE')),
#	(1,_('FP')),
#	(2,_('PIN')),
#	(3,_('PW')),
#	(4,_('RF')),
#	(5,_('FP/PW')),
#	(6,_('FP/RF')),
#	(7,_('PW/RF')),
#	(8,_('PIN&FP')),
#	(9,_('FP&PW')),
#	(10,_('FP&RF')),
#	(11,_('PW&RF')),
#	(12,_('FP&PW&RF')),
#	(13,_('PIN&FP&PW')),
#	(14,_('FP&RF/PIN')),
#	(15,_('FACE')),
#	(16,_('FACE&FP')),
#	(17,_('FACE&PW')),
#	(18,_('FACE&RF')),
#	(19,_('FACE&FP&RF')),
#	(20,_('FACE&FP&PW')),
#)
ISNOTFACEFP=(
    (0,_('No')),
    (1,_('Yes')),
)
M=settings.MOD_DICT

PRODUCTTYPE=(
        (M['att'],_(u'考勤')),
        (M['meeting'],_(u'会议')),
        #(M['patrol'],_(u'巡更')),
        #(M['ipos'],_(u'消费机')),
        (25,_(u'门禁一体机')),
        (M['acc'],_(u'门禁设备')),

    )
ACC_TYPE_CHOICES = ((1, _(u'单门控制器')),(2, _(u'两门控制器')),(4, _(u'四门控制器')))

CONSUMEMODEL = ((1, _(u'定值模式')),(2, _(u'金额模式')),(3, _(u'键值模式')),(4, _(u'计次模式')),(5, _(u'商品模式')),(6, _(u'计时模式')),(7, _(u'记帐模式')))

CASHMODEL = ((0, _(u'定值模式')),(1, _(u'金额模式')))

CASHTYPE = ((0, _(u'充值')),(1, _(u'退款')))

class iclock(models.Model):
    SN = models.CharField(_(u'serial number'), max_length=20, primary_key=True, help_text=_(u'应与设备一致'))
    State = models.IntegerField(_(u'状态'),default=1, editable=False)
    LastActivity = models.DateTimeField(_('last activity'),null=True, blank=True,editable=False)
    TransTimes = models.CharField(_('transfer time'),max_length=50, null=True, blank=True, editable=False,default="00:00;14:05", help_text=_('Setting device for a moment from the plane started to send checks to the new data server. Hh: mm (hours: minutes) format, with a number of time between the semicolon (;) separately'))
    TransInterval = models.IntegerField(_('Trans interval'),default=1, blank=True, editable=False, null=True,help_text=_('Device set for each interval to check how many minutes to send new data server'))
#	RealLog=models.BooleanField(_('RealTransLog'),null=True,default=True, blank=True,editable=True)
    LogStamp = models.CharField(_('trans record stamp'),max_length=20,default=0, null=True, blank=True, editable=False, help_text=_('Logo for the latest device to the server send the transactions timestamps'))
    OpLogStamp = models.CharField(_('trans OP stamp'),max_length=20,default=0, null=True, blank=True, editable=False, help_text=_('Marking device for the server to the employee data transfer as timestamps'))
    PhotoStamp = models.CharField(_('trans photo stamp'),max_length=20,default=0, null=True, editable=False, blank=True, help_text=_('Marking device for the server to the picture transfer as timestamps'))


    PosLogStamp = models.CharField(max_length=20, null=True, editable=False, blank=True)#为设备最后上传消费记录的记录时间戳标记
    FullLogStamp = models.CharField(max_length=20, null=True, editable=False, blank=True)#为设备最后上传充值记录的记录时间戳标记
    AllowLogStamp = models.CharField(max_length=20, null=True, editable=False, blank=True)#为设备最后上传补贴记录的记录时间戳标记
    PosLogStampId = models.CharField(max_length=20, null=True, editable=False, blank=True)#为设备最后上传消费记录的记录戳标记
    FullLogStampId = models.CharField(max_length=20, null=True, editable=False, blank=True)#为设备最后上传充值记录的记录戳标记
    AllowLogStampId = models.CharField(max_length=20, null=True, editable=False, blank=True)#为设备最后上传补贴记录的记录戳标记

    PosBakLogStampId= models.CharField(max_length=20, null=True, editable=False, blank=True)#为设备最后上传消费备份记录的记录戳标记
    FullBakLogStampId = models.CharField(max_length=20, null=True, editable=False, blank=True)#为设备最后上传充值备份记录的记录戳标记
    AllowBakLogStampId = models.CharField(max_length=20, null=True, editable=False, blank=True)#为设备最后上传补贴备份记录的记录戳标记
    TableNameStamp = models.CharField(max_length=20, null=True, editable=False, blank=True)




    Alias = models.CharField(_('Device Alias name'),max_length=20,null=True, blank=True, help_text=_('Device of a name'))
#	DeptID = models.ForeignKey("department", db_column="DeptID", blank=True, verbose_name=DEPT_NAME, default=1,editable=False, null=True)
    UpdateDB = models.CharField(_('update flag'),max_length=10, default="1111100000", blank=True, editable=False, help_text=_('To identify what kind of data should be transfered to the server'))
    Style = models.CharField(_('style'),max_length=20, null=True, blank=True, default="", editable=False)#门禁中表示不同设备，见文件开头定义
    FWVersion = models.CharField(_('FW Version'),max_length=30, null=True, blank=True,editable=False)
    FPCount = models.IntegerField(_('FP Count'), null=True, blank=True,editable=False)
    TransactionCount = models.IntegerField(_('Transaction Count'), null=True, blank=True,editable=False)
    UserCount = models.IntegerField(_('User Count'), null=True, blank=True,editable=False)
#	MainTime = models.CharField(_('MainTime'),max_length=20, null=True, blank=True,editable=False)
    MaxFingerCount = models.IntegerField(_('MaxFingerCount'), null=True, blank=True,editable=False)
    MaxAttLogCount = models.IntegerField(_(u'记录容量'), null=True, blank=True,editable=False)
    MaxUserCount = models.IntegerField(_(u'用户容量'), null=True, blank=True,editable=False)
    DeviceName = models.CharField(_('Device Name'),max_length=30, null=True, blank=True,editable=False)
    AlgVer = models.CharField(_('AlgVer'),max_length=30, null=True, blank=True,default='10',editable=False,choices=ALGVER,help_text=u'选择与设备相一致的算法版本')
#	FlashSize = models.CharField(_('FlashSize'),max_length=10, null=True, blank=True,editable=False)
#	FreeFlashSize = models.CharField(_('FreeFlashSize'),max_length=10, null=True, blank=True,editable=False)
#	Language = models.CharField(_('Language'),max_length=30, null=True, blank=True,editable=False)
#	VOLUME = models.CharField(_('VOLUME'),max_length=10, null=True, blank=True,editable=False)
    DtFmt = models.CharField(_('DtFmt'),max_length=10, null=True, blank=True,editable=False)
    IPAddress = models.CharField(_('IPAddress'),max_length=20, null=True, blank=True,editable=True,help_text=_(u'当通讯方式为RS485时,此处填写格式为: 机号:COM2 如 3:COM2'))
    IsTFT = models.CharField(_('IsTFT'),max_length=5, null=True, blank=True,editable=False)
    Platform = models.CharField(_('Platform'),max_length=20, null=True, blank=True,editable=False)
#	Brightness = models.CharField(_('Brightness'),max_length=5, null=True, blank=True,editable=False)
    BackupDev = models.CharField(_(u'标准机构代码'),max_length=30, null=True, blank=True,editable=(settings.TAIKANG>0))#此字段借用给泰康保险用来保存总公司定义的机构代码
    OEMVendor = models.CharField(_('OEMVendor'),max_length=30, null=True, blank=True,editable=False)
    City = models.CharField(_('city'),max_length=50, null=True, blank=True, help_text=_('City of the location'))
    LockFunOn = models.IntegerField(_(u'门禁控制器类型'),db_column='AccFun', default=0, choices=ACC_TYPE_CHOICES,blank=True, editable=True, help_text=_('Access Function'))#用作表示几门控制器
    TZAdj = models.SmallIntegerField(_('Timezone'), default=8, blank=False, editable=True, help_text=_('Timezone of the location'), choices=TIMEZONE_CHOICES)
    DelTag = models.IntegerField(default=0, editable=False, null=True, blank=True)
    Purpose=models.IntegerField(_(u'用作考勤记录'), null=True, default=0,blank=True,editable=True,choices=PURPOSE,help_text=_(u'该设备的记录参与考勤计算'))
    ProductType=models.IntegerField(_(u'设备用途'),null=True, blank=True,editable=True,default=9,choices=PRODUCTTYPE,help_text=_(u'谨慎选择设备类型，不可误选'))  #9代表考勤,1代表会议 11消费机 12出纳机 13 补贴机  4代表门禁一体机 5代表门禁控制器(PUSH) 15 代表非PUSH的控制器 2代表巡更机
    Authentication=models.SmallIntegerField(_('Authentication'),null=True, default=1, blank=True,editable=False,choices=AUTHENTICATION)
    isFace=models.SmallIntegerField(_('isNotFace'),null=True, default=0, blank=True,editable=False)#是否支持面部
    isFptemp=models.SmallIntegerField(_('isNotFptemp'), null=True,default=1, blank=True,editable=False)#是否支持指纹
    isUSERPIC=models.SmallIntegerField(_('isNotUSERPIC'),null=True, default=0, blank=True,editable=False)#是否支持照片下载
    FaceAlgVer=models.CharField(_('FaceAlgVer'),null=True, max_length=10, blank=True,editable=False)#面部算法版本
    faceNumber=models.IntegerField(_(u'面部数'),null=True, blank=True,editable=False,default=0)#人脸数
    faceTempNumber=models.IntegerField(null=True, blank=True,editable=False,default=0)#人脸模板个数
    pushver=models.CharField(_('pushver'),null=True, max_length=40, blank=True,editable=False)#push版本号
    TransTime = models.DateTimeField(_('transfer time'),null=True, blank=True,editable=False)#自动下发时间
    CreateTime = models.DateTimeField(_('Create time'),null=True, blank=True,editable=False)#加入时间

    consume_model = models.IntegerField(verbose_name=_(u'消费模式'),default=1,editable=True,choices=CONSUMEMODEL, null=True, blank=True)
    dz_money = models.DecimalField(verbose_name=_(u'定值金额'),default=10,max_digits=6,decimal_places=2,null=True,blank=True,editable=True,help_text=_(u'最大限额为999元'))
    time_price = models.DecimalField(verbose_name=_(u'时价(元)'),max_digits=10,decimal_places=2,default=6,null=True,blank=True,editable=True)
    long_time = models.IntegerField(_(u'时长取整(分钟)'),default=20, null=True, blank=True, editable=True,help_text=_(u'超出时长不足本设定值时，以本设定值计算'))
    #IC消费字段
    cash_model = models.IntegerField(verbose_name=_(u'出纳模式'),editable=True,choices=CASHMODEL, null=True, blank=True)
    cash_type = models.IntegerField(verbose_name=_(u'出纳类型'),editable=True,choices=CASHTYPE, null=True, blank=True)
    favorable = models.IntegerField(verbose_name=_(u'优惠比例'),editable=True, null=True, blank=True,default = 0,help_text=_(u'%  优惠比例20% 即额外赠送20%充值金额'))
    card_max_money = models.DecimalField(verbose_name=_(u'最大限额'),max_digits=5,decimal_places=2,null=True,blank=True,default=999,editable=True)
    is_add = models.BooleanField(verbose_name=_(u"累加补贴"), default=False)#对未下发的补贴金额进行累计再下发
    is_zeor = models.BooleanField(verbose_name=_(u"清零补贴"), default=False)#每次只下发最后一次补贴金额
    is_OK = models.BooleanField(verbose_name=_(u"按确定键补贴"), default=False)# 是否按确定键进行补贴
    check_black_list = models.BooleanField(verbose_name=_(u'黑名单检查'),null=False,default=True, blank=True, editable=False)#启用True(1)-禁用False(0)-默认为1
    check_white_list = models.BooleanField(verbose_name=_(u'白名单检查'),null=False,default=False, blank=True, editable=True)#启用True(1)-禁用False(0)-默认为1
    is_cons_keap = models.BooleanField(verbose_name=_(u"是否记账"), default=False)
    is_check_operate = models.BooleanField(verbose_name=_(u"操作员卡检查"), default=False)
    #only_RFMachine = models.CharField(_(u'是否只是卡机'), max_length=5, null=True, blank=True, editable=False,default='0')

    def	GetCopyFields(self):
            return ["TransTimes", "TransInterval"]


    def getInfo(self, info):
        if not self.Info: return ""
        return getValueFrom(self.Info, info)

    def IsTft(self):
        ret=self.IsTFT
        if ret and ret=="1": return True
        ret=self.Platform
        if ret and ret.find("_TFT")>0: return True
        ret=self.Brightness
        if ret and ret>"0": return True
        return False
    def BackupDevice(self):
        pass
#		sn=self.BackupDev
##		print "SN:'%s'"%sn
#		if not sn: return None
#		try:
#			return getDevice(sn)
#		except:
#			pass
    def GetDevice(self):
        try:
            return getDevice(self.SN)
        except:
            return None
    def getDynState(self):
        try:
            if self.State==DEV_STATUS_PAUSE: return DEV_STATUS_PAUSE
            aObj=getDevice(self.SN)#cache.get("iclock_"+self.SN)

            if aObj and not aObj.LastActivity: return DEV_STATUS_OFFLINE
            if aObj and not self.LastActivity:self.LastActivity=aObj.LastActivity
            if aObj  and aObj.LastActivity>self.LastActivity:
                self.LastActivity=aObj.LastActivity
#		if self.SN in ["521463"]: print "LastActivity", self.LastActivity
            d=datetime.datetime.now()-self.LastActivity
            if d>datetime.timedelta(0,settings.MAX_DEVICES_STATE):
                return DEV_STATUS_OFFLINE
            else:
                #if len(deviceCmd(self))==0:
                if aObj and aObj.State!=2:
                    return DEV_STATUS_OK


            #if len(deviceCmd(self))>0:#if devcmds.objects.filter(SN=self,CmdOverTime__isnull=True).count()>0:
            if aObj and aObj.State==2:
                return DEV_STATUS_TRANS

            return DEV_STATUS_OK
        except:
            return -1
            #errorLog()

    def getDoorState(self,door_no):
        #print "----",door_no,self.SN
        state=self.getDynState()
        if state==DEV_STATUS_PAUSE:
            return ('disabled',0,0,0)
        elif state==DEV_STATUS_OFFLINE:
            return ('offline',0,0,0)
        elif state==DEV_STATUS_OK or state==DEV_STATUS_TRANS:
            rtstate=cache.get('_device_%s'%self.SN)
            if not rtstate:return ('default',0,0,0)
            d=lineToDict(rtstate)
            tm=d['time']
            sensor=d['sensor']
            relay=int(d['relay'],16)
            alarm=d['alarm']
            rela=relay>>(door_no-1)&0x01
            if door_no<5:
                sens=sensor[0:2]
            else:
                sens=sensor[2:4]
            sens=int(sens,16)
            sens=sens>>((door_no-1)*2)&0x03
            #print "ssss-----",sens
            return ('closed',sens,rela,0)
        else:
            return ('default',0,0,0)


    def getImgUrl(self):
#		if self.DeviceName:
#			imgUrl=settings.MEDIA_ROOT+'img/device/'+self.DeviceName+'.png'
#			if os.path.exists(imgUrl):
#				return settings.MEDIA_URL+'/img/device/'+self.DeviceName+'.png'
#		return settings.MEDIA_URL+'/img/device/noImg.png'
        if self and self.SN:
            imgUrl="%sphoto/device/iclock_%s.jpg" %(settings.ADDITION_FILE_ROOT,self.SN)
            if os.path.exists(imgUrl):
                return "/iclock/file/photo/device/iclock_%s.jpg"%(self.SN)
        return settings.MEDIA_URL+'img/device/noImg.png'

    def GetCommType(self):
        if self.ProductType==5:
            return 'HTTP'
        elif self.ProductType==15:
            if self.IPAddress and ':' in self.IPAddress:
                return 'RS485'
            return 'TCP'

    def getThumbnailUrl(self):
        return self.getImgUrl()
    def save(self, *args, **kwargs):
        #if self.DelTag==1 and not self.DeptID:
        #	self.DeptID=getDefaultDept()
        if not self.Authentication:
            self.Authentication=1
        if not self.AlgVer:
            self.AlgVer='10'
        if not self.LockFunOn:
            self.LockFunOn=0
        if self.ProductType==4:
            self.LockFunOn=1
        #if not self.Purpose:
        #    self.Purpose=9
        if not self.pushver:
            self.pushver='2.0.1'
        if not self.CreateTime:
            self.CreateTime=datetime.datetime.now()
        if not self.TransTime:
            self.TransTime=datetime.datetime(2000,1,1,12,0,0)

        if not self.DelTag: self.DelTag=0
        cache.delete("iclock_"+self.SN)
        cache.delete("iclock_old_"+self.SN)
        super(iclock, self).save(*args, **kwargs)
        #return models.Model.save(self)
    def clear(self):
        devs=self.model.objects.all().filter(DelTag__isnull=True)
        for o in devs:
            #cache.delete("iclock_"+o.SN)
            o.DelTag=1
            o.save()
#		return models.Model.clear(self)
    def delete(self):
#		print "delete iclock", self.SN
        #cache.delete("iclock_"+self.SN)
        self.DelTag=1
        self.save()

    def __unicode__(self):
        if self.Alias:
            return u'%s(%s)'%(self.SN,self.Alias)
        return unicode(self.SN)
    @staticmethod
    def colModels(request=None):
        ret= [
            {'name':'SN','width':120,'label':unicode(iclock._meta.get_field('SN').verbose_name),'frozen':True},
            {'name':'Alias','width':120,'label':unicode(iclock._meta.get_field('Alias').verbose_name),'frozen':False},
            {'name':'DeptIDS','sortable':False,'width':150,'label':unicode(_(u'归属餐厅')),'mod':'ipos'},
            {'name':'DeptIDS','sortable':False,'width':150,'label':unicode(_(u'归属区域')),'mod':'acc'},
            {'name':'DeptIDS','sortable':False,'width':150,'label':unicode(_(u'归属单位')),'mod':'adms;att;meeting;patrol'},
            {'name':'Dept','sortable':False,'width':120,'label':unicode(_(u'标准机构代码')),'mod':'adms;att;meeting;patrol','hidden':(settings.TAIKANG==0)},
            {'name':'IPAddress','width':100,'label':unicode(iclock._meta.get_field('IPAddress').verbose_name)},
            {'name':'ProductType','width':70,'label':unicode(iclock._meta.get_field('ProductType').verbose_name),'mod':'ipos'},
            {'name':'State','sortable':False,'index':'State','width':60,'label':unicode(iclock._meta.get_field('State').verbose_name)},
            {'name':'PosLogStamp','width':120,'label':unicode(_(u'最近传送记录时间')),'mod':'ipos'},
            {'name':'LastLogId','width':110,'label':unicode(_(u'最近传送流水号')),'mod':'ipos','sortable':False},
            {'name':'Data_pos','width':100,'sortable':False,'label':unicode(_(u'数据')),'mod':'ipos'},
            {'name':'Data_acc','width':100,'sortable':False,'label':unicode(_(u'数据')),'mod':'acc'},
            {'name':'Data_','width':100,'sortable':False,'label':unicode(_(u'数据')),'mod':'adms;att;meeting;patrol'},
            {'name':'City','sortable':False,'width':100,'label':unicode(iclock._meta.get_field('City').verbose_name)},
            {'name':'LastActivity','width':100,'label':unicode(iclock._meta.get_field('LastActivity').verbose_name)},
            {'name':'LogStamp','width':120,'label':unicode(iclock._meta.get_field('LogStamp').verbose_name),'mod':'att;acc;meeting;adms'},
            {'name':'UserCount','width':50,'sortable':False,'label':unicode(iclock._meta.get_field('UserCount').verbose_name),'mod':'adms;att;meeting;patrol;acc'},
            {'name':'FPCount','width':50,'sortable':False,'label':unicode(iclock._meta.get_field('FPCount').verbose_name),'mod':'att;acc;meeting;adms'},
            {'name':'FaceCount','width':50,'sortable':False,'label':unicode(iclock._meta.get_field('faceNumber').verbose_name),'mod':'att;acc;meeting;adms'},

            {'name':'TransactionCount','sortable':False,'width':50,'label':unicode(iclock._meta.get_field('TransactionCount').verbose_name),'mod':'att;acc;meeting;adms'},
            {'name':'FWVersion','width':120,'label':unicode(iclock._meta.get_field('FWVersion').verbose_name)},
            {'name':'DeviceName','width':120,'label':unicode(iclock._meta.get_field('DeviceName').verbose_name)},
            {'name':'MaxAttLogCount','sortable':False,'width':80,'label':unicode(iclock._meta.get_field('MaxAttLogCount').verbose_name),'mod':'adms;att;meeting;patrol;acc'},
            {'name':'MaxUserCount','sortable':False,'width':80,'label':unicode(iclock._meta.get_field('MaxUserCount').verbose_name),'mod':'adms;att;meeting;patrol;acc'},
            {'name':'CommType','sortable':False,'width':80,'label':unicode(_(u'通讯方式')),'mod':'acc'},
            {'name':'AlgVer','sortable':False,'hidden':True,'width':80,'label':unicode(_(u'指纹算法'))},
            {'name':'Memo','sortable':False,'width':400,'label':unicode(_(u'备注'))},
            {'name':'getImgUrl','hidden':True}
            ]
        if not request:return ret
        using_m=request.GET.get('mod_name','att')
        ret_Data=[]
        for t in ret:
            try:
                mod=t['mod']
                if using_m in mod:
                    if using_m=='ipos':
                        if t['name']=='ProductType':
                            t['label']=u'%s'%(_(u'消费机类型'))

                    ret_Data.append(t)
            except:
                ret_Data.append(t)

        return ret_Data
    class Admin:
        list_display = ('SN', 'Alias', 'Style', 'LastActivity')
        search_fields = ["SN", "Alias"]
        lock_fields=['DeptID']
    class Meta:
        db_table = 'iclock'
        verbose_name=_('device')
        verbose_name_plural=verbose_name
        permissions = (
            ('pause_iclock','Pause device'),
            ('resume_iclock','Resume a resumed device'),
            ('reloaddata_iclock','Upload data again'),
            ('reloadlogdata_iclock','Upload transactions again'),
            ('info_iclock','Refresh device information'),#更新设备信息
            ('reboot_iclock','Reboot device'),#重新启动设备
            ('loaddata_iclock','Upload new data'),#立即检查并传送数据
            ('cleardata_iclock','Clear data in device'),#清除设备上所有的数据
            ('clearlog_iclock','Clear transactions in device'),#清除设备上的考勤记录
            ('devoption_iclock','Set options of device'),#设置通信密码
            ('unlock_iclock', 'Output unlock signal'),
            ('unalarm_iclock', 'Terminate alarm signal'),
            ('attdataProof_iclock','Attendance data proofreading'),
            ('toDevWithin_iclock','Transfer to the device templately'),
            ('mvToDev_iclock','Move employee to a new device'),
            ('AutoToDev_employee','Auto transfer employee to the device'),
            ('Upload_AC_Options', 'Upload AC Options'),#上传门禁基本设置
            ('Upload_User_AC_Options', 'Upload User AC Options'),#上传用户门禁设置

            ('deptEmptoDev_iclock','Transfer employee of department to the device'),
            ('deptEmptoDelete_iclock','Delete employee from the device'),#按部门人员从设备中删除人员
            ('browselogPic','browse logPic'),#查看考勤记录照片
            #('toDevPic_iclock','toDevPic employee'),#传送人员照片到设备
            #('delFingerFromDev_iclock','Delete fingers from the device'),
            #('delFaceFromDev_iclock','Delete face from the device'),
            #('clearpic_iclock','Clear pictures in device'),

            ('Upload_pos_all_data', 'Upload All Data'),#上传消费所有数据
            ('Upload_pos_Merchandise', 'Upload Merchandise'),#上传商品资料
            ('Upload_pos_Meal', 'Upload Meal'),#上传餐别资料
            ('Upload_Iclock_Photo','Upload Iclock Photo'),
            ('delDevPic_iclock','delDevPic employee')#删除设备上的人员照片

        )

def ValidIClocks(qs):
    return qs.filter(Q(DelTag__isnull=True)|Q(DelTag=0)).order_by("Alias")

class DeptAdmin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    dept = models.ForeignKey(department, verbose_name=_('granted department'), null=False, blank=False)
    iscascadecheck=models.IntegerField(null=True, blank=True,editable=False,default=0)
    def __unicode__(self):
        return unicode(self.user)
    class Admin:
        list_display=("user","dept", )
    class Meta:
        verbose_name=_("admin granted department")
        verbose_name_plural=verbose_name
        unique_together = (("user", "dept"),)

#class GroupAdmin(models.Model):
    #user = models.ForeignKey(User)
    #group = models.ForeignKey(Group, verbose_name=_('granted group'), null=False, blank=False)

    #def __unicode__(self):
        #return unicode(self.user)
    #class Admin:
        #list_display=("user","group", )
    #class Meta:
        #verbose_name=_("admin granted group")
        #verbose_name_plural=verbose_name
        #unique_together = (("user", "group"),)

class UserAdmin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    owned = models.IntegerField(db_column='owned',null=True,blank=True)
    dataname = models.CharField(db_column="dataname",null=False,max_length=30)

    def __unicode__(self):
        return unicode(self.user)
    class Admin:
        list_display=("user", )
    class Meta:
        verbose_name=_("admin granted")
        verbose_name_plural=verbose_name
        unique_together = (("user", "owned","dataname"),)

class device_options(models.Model):
    SN = models.ForeignKey(iclock)
    ParaName=models.CharField(max_length=30,null=False)
    ParaType=models.CharField(max_length=10,null=True)
    ParaValue=models.CharField(max_length=100,null=False)
    def __unicode__(self):
        return unicode(self.SN)
    class Admin:
        list_display=("SN","ParaName", )
    class Meta:
        verbose_name=_("device_options")
        verbose_name_plural=verbose_name
        unique_together = (("SN", "ParaName"),)




class IclockDept(models.Model):
    SN = models.ForeignKey(iclock)
    dept = models.ForeignKey(department, verbose_name=_('granted department'), null=False, blank=False)
    iscascadecheck=models.IntegerField(null=True, blank=True,editable=False,default=0)
    def __unicode__(self):
        return unicode(self.SN)
    class Admin:
        list_display=("SN","dept", )
    class Meta:
        verbose_name=_("admin granted department")
        verbose_name_plural=verbose_name
        unique_together = (("SN", "dept"),)

        permissions = (
            ('IclockDept_calcreports','IclockDept_calcreports'),('IclockDept_reports','IclockDept_reports'),
            )

    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'Device','index':'SN__SN','width':200,'label':unicode(_('device'))}
            #{'name':'PIN','index':'UserID__PIN','width':100,'label':unicode(_('PIN'))},
            #{'name':'EName','index':'UserID__EName','width':100,'label':unicode(_('Emp Name'))},
            #{'name':'DeptName','index':'UserID__DeptID__DeptName','width':100,'label':unicode(_('department name'))},
            #{'name':'Title','index':'UserID__Title','width':80,'label':unicode(_('Title'))},
            #{'name':'Device','hidden':True,'index':'SN','width':180,'label':unicode(_('Device name'))}
            ]
#class iclock_option(models.Model):
#	SN=models.CharField(u'设备编号',max_length=20,null=True, blank=True)
#	ErrorDelay=models.CharField(u'异常连接时间',max_length=3,null=True, blank=True)
#	Delay=models.CharField(u'正常连接时间',max_length=3,null=True, blank=True)
#	Realtime=models.CharField(u'实时上传标记',max_length=2,null=True, blank=True)
#	TransTimes=models.CharField(u'定时上传时间',max_length=20,null=True, blank=True)
#	TransInterval=models.CharField(u'传送时间间隔',max_length=2,null=True, blank=True)
#	TransType=models.CharField(u'传送数据类型',max_length=20,null=True, blank=True)
#	@staticmethod
#	def geticlockoption(sn):
#		e=cache.get("%s_iclock_SN_%s"%(settings.UNIT, sn))
#		if e: return e
#		try:
#			u=iclock_option.objects.get(SN=sn)
#			ll={}
#			ll['ErrorDelay']=u.ErrorDelay
#			ll['Delay']=u.Delay
#			ll['Realtime']=u.Realtime
#			ll['TransTimes']=u.TransTimes
#			ll['TransInterval']=u.TransInterval
#			ll['TransType']=u.TransType
#		except:
#			ll={"ErrorDelay":60,"Delay":60,"Realtime":1,"TransTimes":'00:00',"TransInterval":1,"TransType":'1111111111'}
#		cache.set("%s_iclock_SN_%s"%(settings.UNIT,sn),ll)
#		return ll
#	class Meta:
#		verbose_name=_("iclock option")
#		verbose_name_plural=verbose_name

GENDER_CHOICES = (
    ('M', _('Male')),
    ('F', _('Female')),
)


PRIV_CHOICES=(
    (0,_('Normal')),
    (4,_('Registrar')),
    (6,_('Administrator')),
    (14,_('Supervisor')),
)

def formatPIN(pin):
    if not settings.PIN_WIDTH: return pin
    return string.zfill(devicePIN(pin.rstrip()), settings.PIN_WIDTH)

def devicePIN(pin):
    if not settings.PIN_WIDTH: return pin
    i=0
    for c in pin[0:-1]:
        if c=="0":
            i+=1
        else:
            break
    return pin[i:]
#MAX_PIN_INT=int("999999999999999999999999"[:settings.PIN_WIDTH])
#if settings.PIN_WIDTH==5: MAX_PIN_INT=65534
#elif settings.PIN_WIDTH==10: MAX_PIN_INT=4294967294L
#elif settings.PIN_WIDTH==1: MAX_PIN_INT=999999999999999999999999L
CHECK_CLOCK_IN=(
    (0,_('By Time Zone')),
    (1,_('Must Clock In')),
    (2,_('Don\'t Check In')),
)
CHECK_CLOCK_OUT=(
    (0,_('By Time Zone')),
    (1,_('Must Clock Out')),
    (2,_('Don\'t Check Out')),
)
EDU_CHOICES=(
    (0,_('Technical secondary school')),
    (1,_('High school')),
    (2,_('College')),
    (3,_('Undergraduate')),
    (4,_('Master')),
    (5,_('Doctorate ')),

)
EMPTYPE_CHOICES = (
    ('0', _(u'在编')),
    ('1', _(u'聘用')),
    ('2', _(u'合同内')),
    ('3', _(u'合同外')),
)



class employee(models.Model):

    id=models.AutoField(db_column="userid", primary_key=True, null=False,editable=False)
    PIN = models.CharField(_('PIN'),db_column="badgenumber",null=False,max_length=24)
    EName = models.CharField(_('Emp Name'),db_column="name",null=True,max_length=24, blank=True, default="")
    DeptID = models.ForeignKey(department,db_column="defaultdeptid", verbose_name=DEPT_NAME, editable=True, null=True)
    Password = models.CharField(_('Password'),max_length=20, null=True, blank=True, editable=False)
    MVerifyPass=models.CharField(_(u'设备密码'),max_length=20, null=True, blank=True,editable=True, help_text=_('1.Admin password of the device;2.Checkinout password'))
    Privilege = models.IntegerField(_(u'设备权限'),null=True, blank=True, choices=PRIV_CHOICES,help_text=u'仅超级用户能编辑')
    Card = models.CharField(_('ID Card'),max_length=20, null=True, blank=True, editable=True)
    AccGroup = models.IntegerField(_('Access Group'),null=True, blank=True,editable=False)#多人开门组使用
    TimeZones = models.CharField(_('Access Timezone'),max_length=20, null=True, blank=True,editable=False)
    Gender = models.CharField(_('sex'),max_length=2, choices=GENDER_CHOICES, null=True, blank=True)
    Birthday = models.DateTimeField(_('birthday'),max_length=8, null=True, blank=True)#help_text=unicode(_('Date format is '))+"ISO;"+unicode( _('for example'))+':1999-01-10/1999-1-11')
    Address = models.CharField(_('address'),db_column="street",max_length=80, null=True, blank=True)
    PostCode = models.CharField(_('postcode'),db_column="zip",max_length=6, null=True, blank=True)
    Tele = models.CharField(_('office phone'),db_column="ophone",max_length=20, editable=True,null=True, blank=True)
    FPHONE=models.CharField(_(u'联系电话'),max_length=20, null=True, blank=True)
    Mobile = models.CharField(_('mobile'),db_column="pager",max_length=20, null=True, blank=True)
    National = models.CharField(_('nationality'),db_column="minzu",max_length=8, null=True, blank=True)
    Title = models.CharField(_('title'),db_column="title",max_length=20, null=True, blank=True)
    #SN = models.ForeignKey(iclock, db_column='SN', verbose_name=_('registration device'), null=True, blank=True, editable=False) #屏蔽掉登记设备设置
    SN = models.CharField( db_column='SN', max_length=20,verbose_name=_('registration device'), null=True, blank=True, editable=False)#设备序列号，不允许借用他用
    SSN=models.CharField(_('social insurance num'),max_length=20, null=True, blank=True)
    UTime = models.DateTimeField(_('refresh time'), null=True, blank=True, editable=False)
    Hiredday=models.DateField(_(u'参加工作时间'),max_length=8, null=True, blank=True)
    VERIFICATIONMETHOD=models.SmallIntegerField(u'验证方式',null=True, blank=True,editable=False)
    State=models.CharField(u'省代码',max_length=6, null=True, blank=True,editable=False)#此字段可做他用
    City=models.CharField(u'市代码',max_length=6, null=True, blank=True,editable=False)#此字段可做他用
    SECURITYFLAGS=models.SmallIntegerField(u'管理员标志',null=True, blank=True,editable=False)
    ATT=models.NullBooleanField(_('Active AC'),null=True,default=True,  blank=True,editable=True)
    OverTime=models.NullBooleanField(_('Count OT'),null=True,default=True, blank=True,editable=False)
    Holiday=models.NullBooleanField(_('Rest on Holidays'),null=True,default=True, blank=True,editable=False) #备用
    INLATE=models.SmallIntegerField(_('Check Clock In'),null=True,default=0, choices=CHECK_CLOCK_IN, blank=True,editable=True)
    OutEarly=models.SmallIntegerField(_('Check Clock Out'),null=True,default=0, choices=CHECK_CLOCK_OUT, blank=True,editable=True)
    Lunchduration=models.SmallIntegerField(u'有午休',null=True,default=1, blank=True,editable=False)
    SEP=models.SmallIntegerField(null=True,default=1,editable=False)
    OffDuty=models.SmallIntegerField(_("left"), null=True, default=0, editable=False, choices=BOOLEANS)
    AutoSchPlan=models.SmallIntegerField(null=True,default=1,editable=False)
    MinAutoSchInterval=models.IntegerField(null=True,default=24,editable=False)
    RegisterOT=models.IntegerField(null=True,default=1,editable=False)
    sysPass=models.CharField(_(u'自助登录密码'),db_column="sysPass",max_length=20, null=True, blank=True,editable=True)   #2009.3.20
    email = models.EmailField(_('e-mail'), blank=True, null=True)
    OpStamp = models.DateTimeField(_('modify time'),null=True, blank=True,editable=False)                 #保存人员信息的更新时间,不编辑
    Reserved=models.IntegerField(null=True,default=0,blank=True,editable=False)       #  泰康约定人员的工号修改后将该字段写1    #预留保存一些临时统计信息比如指纹数可实现查询没有指纹的人员
    Annualleave=models.FloatField(_('Annual leave'), null=True, default=0, blank=True,editable=False)                  #暂时不编辑

    #人事合同信息
    Educational = models.CharField(_('Educational'),max_length=2, choices=EDU_CHOICES, null=True, blank=True)
    Trialstarttime=models.DateField(_('Trialstarttime'),max_length=8, null=True, blank=True)
    Trialendtime=models.DateField(_('Trialendtime'),max_length=8, null=True, blank=True)
#	Startwork=models.DateField(_('Startwork'),max_length=8, null=True, blank=True)
#	Worktime=models.DateField(_('Worktime'),max_length=8, null=True, blank=True)
    #Workyears=models.DateField(_('Workyears'),max_length=8, null=True, blank=True)
    Contractstarttime=models.DateField(_('Contractstarttime'),max_length=8, null=True, blank=True)
    Contractendtime=models.DateField(_('Contractendtime'),max_length=8, null=True, blank=True)
    Employeetype= models.CharField(_(u'雇佣类型'),max_length=2, choices=EMPTYPE_CHOICES, null=True, blank=True)
    DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)

    Workcode = models.CharField(_('NewPin'), max_length=20, null=False)
    OffPosition = models.SmallIntegerField(_(u"是否离岗"), null=True, default=0, choices=BOOLEANS)
    OffPositionDate=models.DateTimeField(_(u'离岗时间'),max_length=8, null=True, blank=True)
    bstate = models.IntegerField(_(u'借调状态'), null=True, blank=True,editable=False,default=2)


    @staticmethod
    def objByID(id):
        if (id==None) or (id==0) or (id=='0') or (id<0):
            return None
        emp=cache.get("%s_iclock_emp_%s"%(settings.UNIT, id))
        if emp:
            if emp.Reserved and emp.Reserved==1:
                sql="update userinfo set Reserved=0 where userid=%s"%(emp.id)
                customSql(sql)
            else:
                return emp


        try:
            u=employee.objects.get(id=id)
        except Exception,e:
            print "objByID===",id,e
            u=None
        if u:
            u.IsNewEmp=False
            cache.set("%s_iclock_emp_%s"%(settings.UNIT,u.id),u)
            cache.set("%s_iclock_emp_PIN_%s"%(settings.UNIT,u.PIN),u)
        #if not u:
        #	print "==============",id
        return u

    @staticmethod
    def objByPIN(pin, Device=None):
        if not pin:return None
        emp=cache.get("%s_iclock_emp_PIN_%s"%(settings.UNIT,pin))
        if emp:
            if emp.Reserved and emp.Reserved==1:
                sql="update userinfo set Reserved=0 where userid=%s"%(emp.id)
                customSql(sql)
            else:
                return emp
        empl=employee.objects.filter(PIN=pin)
        if empl:
            if empl[0].DelTag==1:
                if Device:
                    if Device.ProductType not in [5,15,25,11,12,13]:
                        IDepts = IclockDept.objects.filter(SN=Device).order_by('id')
                        if IDepts:
                            obj = IDepts[0]
                            dept = obj.dept
                            empl[0].DeptID=dept
                            empl[0].DelTag=0
                            empl[0].save()
                            e=empl[0]
                        else:
                            return None
                    elif  Device.ProductType in [25]:
                        empl[0].DelTag = 0
                        empl[0].save()
                        e = empl[0]
                    else:
                        return None
                else:
                    cache.delete("%s_iclock_emp_%s"%(settings.UNIT,empl[0].id))
                    cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,empl[0].PIN))
                    raise Exception("Employee PIN %s not found"%pin)
            else:
                e=empl[0]  #about 60ms
                e.IsNewEmp=False
                cache.set("%s_iclock_emp_PIN_%s"%(settings.UNIT,pin),e)
        else:
            if Device:
                try:
                    try:
                        #deptid=Device.DeptID
                        #if not deptid: deptid=getDefaultDept()
                        if Device.ProductType not in [5, 15, 25, 11, 12, 13]:

                            IDepts=IclockDept.objects.filter(SN=Device).order_by('id')
                            if IDepts:
                                obj=IDepts[0]
                                deptid=obj.dept
                            else:
                                return None
                        elif Device.ProductType in [25]:
                            deptid = getDefaultDept()
                        else:
                            return None
                    except:
                        return None

#						e=employee(PIN=pin, EName=" ", DeptID=deptid, SN=Device, UTime=datetime.datetime.now())
                    e=employee(PIN=pin, EName="",DeptID=deptid,SN=Device.SN)
                    e.save()
                    e.IsNewEmp=True
                    cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,pin))
                    cache.delete("%s_iclock_emp_%s"%(settings.UNIT,e.id))
                except Exception, er:
                    #errorLog()
                    raise er
            else:
                raise Exception("Employee PIN %s not found"%pin)
        return e
    def Dept(self): #cached user
        return department.objByID(self.DeptID_id)
    @staticmethod
    def clear():
        emps=employee.objects.all()
        for e in emps:
            e.DelTag=1
            e.save()
    def Device(self):
        return getDevice(self.SN_id)
    def getUrl(self):
        return settings.UNIT_URL+"iclock/data/employee/%s/"%self.pk
    def getImgUrl(self, default=None):
        if not self.PIN: return default
        if os.path.exists(getStoredFileName("photo", None, devicePIN(self.PIN)+".jpg")):
            url=getStoredFileURL("photo", None, devicePIN(self.PIN)+".jpg")
            import random
            url += '?time=%s'%str(random.random()).split('.')[1]
            return url
        elif self.SSN and os.path.exists(getStoredFileName("photo", None, self.SSN+".jpg")):
            url=getStoredFileURL("photo", None, self.SSN+".jpg")
            import random
            url += '?time=%s'%str(random.random()).split('.')[1]
            return url
        return default
    def rmThumbnail(self):
        tbName=getStoredFileName("photo/thumbnail", None, devicePIN(self.PIN)+".jpg")
        if os.path.exists(tbName):
            os.remove(tbName)
    def getThumbnailUrl(self, default=None,tag=True):
        import random
        varile = str(random.random()).split('.')[1]
        if tag:
            if GetParamValue('opt_basic_emp_pic','')!='1':return ''

        if not self.PIN: return default
        # if hasattr(settings,'SHOWEMPPHOTO') and settings.SHOWEMPPHOTO==0:
        #     if facetemp.objects.filter(UserID=self.id).count()==0:
        #         return ""
        if not os.path.exists(getStoredFileName("photo/thumbnail", None, self.PIN+".jpg")) and \
            not os.path.exists(getStoredFileName("photo", None, devicePIN(self.PIN)+".jpg")):
            if self.SSN:
                tbName=getStoredFileName("photo", None, self.SSN+".jpg")
                tbUrl=getStoredFileURL("photo", None, self.SSN+".jpg")
                if os.path.exists(tbName):#取路径先判断压缩图是否已经存在
                    return tbUrl+'?'+varile
        else:
            tbName=getStoredFileName("photo/thumbnail", None, self.PIN+".jpg")
            tbUrl=getStoredFileURL("photo/thumbnail", None, self.PIN+".jpg")
            if os.path.exists(tbName):#取路径先判断压缩图是否已经存在
                return tbUrl+'?'+varile
            else:#压缩图不存在 创建
                fullName=getStoredFileName("photo", None, self.PIN+".jpg")
                if os.path.exists(fullName):
                    if createThumbnail(fullName, tbName):
                        return tbUrl+'?'+varile
        return ''
    def save(self):
        self.PIN=self.PIN.strip()
        pin=self.PIN
        if pin in settings.DISABLED_PINS:# or (not pin.isdigit()):
            raise Exception("Employee PIN '%s' is disabled"%pin)
        #if pin_int>MAX_PIN_INT:
        #	raise Exception("Max employee PIN is %d"%MAX_PIN_INT)
        self.PIN=formatPIN(self.PIN)

        if not self.id: #new employee
            try:
                old=self.objByPIN(self.PIN, None)
            except:
                old=None
            if old:
                emp=employee.objects.filter(PIN=self.PIN)
                if emp and emp[0].DelTag<>1:
                    raise Exception("Duplicated")
        else: # modify a employee
            old_emp=self.objByID(self.id)
            if old_emp.PIN<>self.PIN: #changed the PIN
                if employee.objects.filter(PIN=self.PIN).count()>0:
                    raise Exception("Duplicated Employee PIN: %s"%self.PIN)
        #if self.Card:#isvalidate card
        #	empcard=employee.objects.filter(Card=self.Card).exclude(DelTag=1).exclude(OffDuty=1)
        #	if empcard.count()>0 and empcard[0].PIN!=self.PIN:
        #		raise Exception(_(u"卡号重复: %s")%self.Card)
        self.OpStamp=datetime.datetime.now()
        self.SN=''
        if not self.id:
            try:
                emp=employee.objects.get(PIN=self.PIN)
                self.id=emp.id
                self.DelTag=0

                super(employee,self).save(force_update=True)
            except:
                super(employee,self).save()
        else:
            super(employee,self).save()


        #if GetParamValue('opt_basic_Auto_iclock','0')=='1':
        #	from iclock.dataproc import autoemptodev
        #	if self.OffDuty!=1:
        #		autoemptodev(self)
        #if GetParamValue('opt_basic_Auto_del_iclock','0')=='1':
        #	from iclock.dataproc import autodelempfromdev
        #	if self.OffDuty==1:
        #		autodelempfromdev(self)
        try:

            cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,self.PIN))
            cache.delete("%s_iclock_emp_%s"%(settings.UNIT,self.id))
        except:
            pass
        return self
    def delete(self):
        try:
            cache.delete("%s_iclock_emp_%s"%(settings.UNIT,self.id))
            cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,self.PIN))
            super(employee, self).delete()
        except Exception,e:
            #print "=====%s"%e
            pass
    def pin(self):
        return devicePIN(self.PIN)
    def fpCount(self):
        return BioData.objects.filter(UserID=self,bio_type=bioFinger).count()
    def faceCount(self):
        if BioData.objects.filter(UserID=self,bio_type=bioFace).count()>0:return 1
        return 0
    def	GetCopyFields(self):
        return ["National", "PostCode", "Address", "Gender"]
    def __unicode__(self):
        return self.PIN+(self.EName and " %s"%self.EName or "")
    @staticmethod
    def colModels():
        ret=[{'name':'id','hidden':True,'frozen': False},
            {'name':'PIN','index':'PIN','width':120,'search':True,'label':unicode(employee._meta.get_field('PIN').verbose_name),'frozen':False},
            {'name':'Workcode', 'index': 'Workcode', 'width': 100, 'search': True,'label': unicode(employee._meta.get_field('Workcode').verbose_name), 'frozen': True},
            {'name':'EName','sortable':False,'width':80,'label':unicode(employee._meta.get_field('EName').verbose_name),'frozen': False},
            {'name':'DeptID','width':60,'label':unicode(employee._meta.get_field('DeptID').verbose_name)},
            {'name':'DeptName','sortable':False,'index':'DeptID__DeptName','width':180,'label':unicode(_(u'单位名称'))},
            #{'name': 'BorrowTag', 'sortable': False, 'width':70 , 'label': unicode(_(u'借调标记'))},
            #{'name': 'BorrowDept', 'sortable': False, 'width': 180, 'label': unicode(_(u'借调单位'))},
            {'name':'Gender','width':50,'search':False,'label':unicode(employee._meta.get_field('Gender').verbose_name)},
            #{'name':'Card','sortable':False,'width':80,'label':unicode(employee._meta.get_field('Card').verbose_name)},
            # {'name':'SSN','sortable':False,'width':120,'label':unicode(employee._meta.get_field('SSN').verbose_name)},
            {'name':'Privilege','width':90,'search':False,'label':unicode(employee._meta.get_field('Privilege').verbose_name)},
            {'name': 'emptype', 'width': 70, 'sortable':False,'search': False,'label': unicode(employee._meta.get_field('Employeetype').verbose_name)},
            {'name':'Birthday','sortable':False,'search':False,'width':80,'label':unicode(employee._meta.get_field('Birthday').verbose_name)},
            {'name':'National','search':False,'width':50,'sortable':False,'label':unicode(employee._meta.get_field('National').verbose_name)},
            {'name':'Title','width':60,'label':unicode(employee._meta.get_field('Title').verbose_name)},
            {'name':'Tele','search':False,'width':80,'sortable':False,'label':unicode(employee._meta.get_field('Tele').verbose_name)},
            {'name':'Mobile','search':False,'sortable':False,'width':80,'label':unicode(employee._meta.get_field('Mobile').verbose_name)},
            {'name':'Hiredday','sortable':False,'search':False,'width':100,'label':unicode(employee._meta.get_field('Hiredday').verbose_name)},
            {'name':'photo','search':False,'sortable':False,'width':100,'label':unicode(_("Picture"))},
            {'name':'email','sortable':False,'width':100,'label':unicode(employee._meta.get_field('email').verbose_name)},
            {'name':'OffDuty','search':False,'width':70,'label':unicode(_("Left"))},
            {'name': 'OffPosition','search': False, 'width': 70, 'label': unicode(_(u"离岗标记"))},
            {'name': 'bstate','search': False, 'width': 70, 'label': unicode(_(u"借调标记"))},
            {'name': 'OffPositionDate','search': False, 'width': 120, 'label': unicode(_(u"离岗时间"))},
            {'name':'OpStamp','width':120,'label':unicode(employee._meta.get_field('OpStamp').verbose_name)}
            ]
        if GetParamValue('opt_basic_emp_pic','')!='1':
            for t in ret:
                if t['name']=='photo':
                    t['hidden']=True
                if t['name'] in ['id','PIN','EName']:
                    t['frozen']=True

        return ret


    class Admin:
        list_display=('PIN','EName','DeptID','Gender','Title','Tele','Mobile')
        list_filter = ('DeptID','Gender','Birthday','OffDuty',)
        search_fields = ['PIN','EName','Card','Mobile','Title', 'Workcode','OffPosition']
        lock_fields=['DeptID']

    class Meta:
        db_table = 'userinfo'
        verbose_name=_("employee")
        verbose_name_plural=verbose_name
        unique_together = (("PIN",),)
        permissions = (
                    ('empLeave_employee','Employee leave'),
                    ('restoreEmpLeave_employee','restore Employee leave'),
                    ('toDepart_employee',"Change employee's department"),
                    ('enroll_employee','Enroll employee\'s fingerprint'),
                    ('Upload_pictures','Upload pictures'),
                    ('edit_privilege','edit privilege'),
                    ('edit_MVerifyPass','edit MVerifyPass'),
                    ('edit_Card','edit Card'),
                    ('ligang','ligang'),
                    ('liganghuifu','liganghuifu'),
        )

def getNormalCard(card):
    if not card: return ""
    try:
        num=int(str(card))
        card="[%02X%02X%02X%02X%02X]"%(num & 0xff, (num >> 8) & 0xff, (num >> 16) & 0xff, (num >> 24) & 0xff, (num >> 32) & 0xff)
    except:
        card=card[:-3]+'00]'
    return card

def getEmpCmdStr(emp,device=None,groupId=None):
    ename=emp.EName and emp.EName.strip() or ""
    ret=''
    if type(device)==list:
        device=getDevice(device[0])
    if (not device) or (device.ProductType not in [5,15]):
        ret= "DATA USER PIN=%s\t%s\t%s\t%s\t%s\t%s\tGrp=%s"%(emp.pin(),
                ename and ("Name=%s"%ename) or "",
                "Pri=%s"%(emp.Privilege and emp.Privilege or 0),
                "Passwd=%s"%(emp.MVerifyPass or ""),
                "Card=%s"%(getNormalCard(emp.Card) or ""),
                "",
                1)
    elif device.ProductType in [5,15,25]:#为门禁控制器生成命令
        isDisabled=0
        super_auth=0
        starttime=0
        endtime=0
        grp=0
        try:
            from mysite.acc.models import acc_employee
            obj=acc_employee.objects.get(UserID=emp)
            if obj.isblacklist:isDisabled=1
            super_auth=obj.acc_super_auth or 0
            if obj.set_valid_time and obj.acc_startdate and obj.acc_enddate:
                starttime=OldEncodeTime(obj.acc_startdate)
                endtime=OldEncodeTime(obj.acc_enddate)
            if obj.morecard_group:
                grp=obj.morecard_group_id

        except:
            pass
        emppin=emp.pin()
        if settings.IDFORPIN==1:
            emppin=emp.id
        if device.ProductType in [5,25]:
            ret="\r\nCardNo=%s\tPin=%s\tPassword=%s\tGroup=%s\tStartTime=%s\tEndTime=%s\tName=%s\tSuperAuthorize=%s\tDisable=%s"%(emp.Card or '',emppin,emp.MVerifyPass or '',grp or 0,starttime,endtime,ename,super_auth,isDisabled)
        else:#PULL设备时间格式YYYYMMDD
            st= OldDecodeTime(starttime)[:10].replace('-','')
            et= OldDecodeTime(endtime)[:10].replace('-','')

            if device.Style not in [DEVICE_C3_100, DEVICE_C3_200, DEVICE_C3_400, DEVICE_C3_400_TO_200]:
                ret="\r\nCardNo=%s\tPin=%s\tPassword=%s\tGroup=%s\tStartTime=%s\tEndTime=%s"%(emp.Card or '',emppin,emp.MVerifyPass or '',grp or 0,st,et)
            else:
                ret="\r\nCardNo=%s\tPin=%s\tPassword=%s\tGroup=%s\tStartTime=%s\tEndTime=%s"%(emp.Card or '',emppin,emp.MVerifyPass or '',grp or 0,st,et)




    return ret


EMPLEAVETYPE = (
        (0, _(u'自离')),
        (1, _(u'辞退')),
        (2, _(u'辞职')),
        (3, _(u'调离')),
        (4, _(u'停薪留职')),
)

EMPLEAVESTATE = (
        (0, _(u'已离职')),
        (1, _(u'离职恢复')),
)

def GetLeavetype():
    ret = []
    for leav in EMPLEAVETYPE:
        dleav = {}
        dleav['symbol'] = leav[0]
        dleav['pName'] = str(leav[1])
        ret.append(dleav)
    return ret

class empleavelog(models.Model):
    UserID = models.ForeignKey(employee,  verbose_name=u"员工")
    leavedate=models.DateField(verbose_name=_(u'离职日期'),editable=True)
    leavetype=models.IntegerField(verbose_name=_(u'离职类型'),choices=EMPLEAVETYPE,editable=True)
    reason=models.CharField(verbose_name=_(u'离职原因'),max_length=200,null=True,blank=True,editable=True)
    createtime=models.DateTimeField(verbose_name=_(u'操作时间'),editable=True)
    deltag = models.IntegerField(_(u'删除标记'),default=0,choices=EMPLEAVESTATE, editable=False, null=True, blank=True)

    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None

    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'EName','index':'UserID__EName','width':80,'label':unicode(_('EName'))},
            {'name':'Workcode', 'index':'UserID__Workcode', 'width':80, 'label':unicode(_('NewPin'))},
            {'name':'leavedate', 'width':120,'label':unicode(empleavelog._meta.get_field('leavedate').verbose_name)},
            {'name':'leavetype', 'width':90,'label':unicode(empleavelog._meta.get_field('leavetype').verbose_name)},
            {'name':'reason','sortable':False,'width':120,'label':unicode(_(u'离职原因'))}
            ]

    class Admin:
        list_filter =['UserID','leavedate','leavetype']
        lock_fields=['UserID']
        search_fields = ['UserID__PIN','UserID__EName','UserID__Workcode']
    class Meta:
        db_table = 'user_empleavelog'
        verbose_name = _(u'离职人员')
        verbose_name_plural=verbose_name
        unique_together = (("UserID", "leavedate","leavetype","deltag", "createtime"),)
        permissions = (
            )

class stafflogin(models.Model):
    UserID = models.ForeignKey(employee,  verbose_name=u"员工")
    StaffUsername = models.CharField(_(u'用户名'),max_length=20, null=True, blank=True,unique=True)
    LoginMethod = models.IntegerField(_(u'登录方式'),null=True, blank=True,editable=False)

    def __unicode__(self):
        return self.StaffUsername

    class Admin:
        pass

    class Meta:
        db_table = 'stafflogin'
        verbose_name = _(u'登录方式')
        verbose_name_plural=verbose_name
        #unique_together = (("StaffUsername",),)




FINGERIDS=(
    (0, u'左手小指'),
    (1, u'左手无名指'),
    (2, u'左手中指'),
    (3, u'左手食指'),
    (4, u'左手拇指'),
    (5, u'右手拇指'),
    (6, u'右手食指'),
    (7, u'右手中指'),
    (8, u'右手无名指'),
    (9, u'右手小指'),
)

#class fptemp(models.Model):
#	id=models.AutoField(primary_key=True)
#	UserID = models.ForeignKey("employee", db_column='userid', verbose_name=u"员工")
#	Template = models.TextField(u'指纹模板',null=True)
#	FingerID = models.IntegerField(u'手指',default=0, choices=FINGERIDS)
#	Valid = models.IntegerField(u'是否有效',default=1, choices=BOOLEANS)
#	#DelTag = models.IntegerField(u'删除标记',default=0, choices=BOOLEANS,null=True)
#	SN = models.ForeignKey(iclock, db_column='SN', verbose_name=u'登记设备', null=True, blank=True)
#	UTime = models.DateTimeField(_('refresh time'), null=True, blank=True, editable=False)
#	#BITMAPPICTURE=models.TextField(null=True,editable=False)
#	#BITMAPPICTURE2=models.TextField(null=True,editable=False)
#	#BITMAPPICTURE3=models.TextField(null=True,editable=False)
#	#BITMAPPICTURE4=models.TextField(null=True,editable=False)
#	USETYPE = models.IntegerField(null=True,editable=False)
##	Template2 = models.TextField(u'指纹模板',null=True,editable=False)
##	Template3 = models.TextField(u'指纹模板',null=True,editable=False)
#	AlgVer=models.IntegerField(null=True,default=0,blank=True,editable=False)         
#	def __unicode__(self):
#		return "%s, %d"%(self.UserID.__unicode__(),self.FingerID)
#	def template(self):
#		return self.Template.decode("base64")
#	def temp(self):
#		#去掉BASE64编码的指纹模板中的回车
#		return self.Template.replace("\n","").replace("\r","")
#	def employee(self): #cached employee
#		try:
#			return employee.objByID(self.UserID_id)
#		except:
#			return None
#	@staticmethod	
#	def colModels():
#		return [{'name':'id','hidden':True},
#			{'name':'DeptName','index':'UserID__DeptID','sortable':False,'width':200,'label':unicode(_('department name'))},
#			{'name':'PIN','index':'UserID__PIN','width':100,'label':unicode(_('PIN'))},
#			{'name':'EName','index':'UserID__EName','width':100,'label':unicode(_('EName'))},
#			{'name':'FingerID','width':100,'label':unicode(_('Finger serial number'))},
#			{'name':'FingerName','width':100,'sortable':False,'label':unicode(fptemp._meta.get_field('FingerID').verbose_name)},
#			{'name':'Fingerprint Images','label':unicode(_('Fingerprint Images')),'hidden':True},
#			{'name':'AlgVer','index':'AlgVer','width':100,'label':unicode(_(u'指纹版本'))},
#			{'name':'UTime','width':120,'label':unicode(_(u'采集时间'))}
#			]	
#	class Admin:
#		list_display=('UserID', 'FingerID', 'Valid')
#		list_filter = ('UserID',)
#		search_fields = ['=UserID__PIN','=UserID__EName']
#	class Meta:
#		db_table = 'template'
#		unique_together = (("UserID", "FingerID","AlgVer"),)
#		verbose_name=_("fingerprint")#u"人员指纹"
#		verbose_name_plural=verbose_name

#class iface(models.Model):
#	UserID = models.ForeignKey("employee", db_column='userid')
#	FaceID = models.CharField(max_length=50, null=True, blank=True)
#	PersonID = models.CharField(max_length=50, null=True, blank=True)
#	Valid = models.SmallIntegerField(default=1)
#
#	class Meta:
#		db_table = 'iface'
#		unique_together = (("UserID", "PersonID"),)
#
#	def save(self, *args, **kwargs):
#		super(iface, self).save(*args, **kwargs)


#class facetemp(models.Model):
#	id=models.AutoField(primary_key=True)
#	UserID = models.ForeignKey("employee", db_column='userid', verbose_name=u"员工")
#	Template = models.TextField(u'面部模板',max_length=2048,null=True)
#	FaceID = models.SmallIntegerField(u'模板编号',default=0)
#	Valid = models.SmallIntegerField(u'是否有效',default=1, choices=BOOLEANS)
#	#DelTag = models.SmallIntegerField(u'删除标记',default=0, choices=BOOLEANS,null=True)
#	SN = models.ForeignKey(iclock, db_column='SN', verbose_name=u'登记设备', null=True, blank=True)
#	UTime = models.DateTimeField(_('refresh time'), null=True, blank=True, editable=False)
#	USETYPE = models.SmallIntegerField(null=True,editable=False)
#	AlgVer=models.IntegerField(null=True,default=0,blank=True,editable=False)         
#	def __unicode__(self):
#		return "%s, %d"%(self.UserID.__unicode__(),self.FaceID)
#	def template(self):
#		return self.Template.decode("base64")
#	def temp(self):
#		#去掉BASE64编码的模板中的回车
#		return self.Template.replace("\n","").replace("\r","")
#	def employee(self): #cached employee
#		try:
#			return employee.objByID(self.UserID_id)
#		except:
#			return None
#	@staticmethod	
#	def colModels():
#		return [{'name':'id','hidden':True},
#			{'name':'DeptName','sortable':False,'index':'UserID__DeptID','width':200,'label':unicode(_('department name'))},
#			{'name':'PIN','index':'UserID__PIN','width':100,'label':unicode(_('PIN'))},
#			{'name':'EName','index':'UserID__EName','width':100,'label':unicode(_('EName'))},
#			{'name':'FaceID','width':100,'label':unicode(_('face serial number')),'hidden':True},
#			#{'name':'FaceName','width':100,'sortable':False,'label':unicode(facetemp._meta.get_field('FaceID').verbose_name)},
#			{'name':'face Images','label':unicode(_('face Images')),'hidden':True},
#			{'name':'AlgVer','width':100,'label':unicode(_('AlgVer'))},
#			{'name':'UTime','width':120,'label':unicode(_(u'采集时间'))}
#			]	
#	class Admin:
#		list_display=('UserID', 'FaceID', 'Valid')
#		list_filter = ('UserID',)
#		search_fields = ['=UserID__PIN','=UserID__EName']
#	class Meta:
#		db_table = 'facetemplate'
#		unique_together = (("UserID", "FaceID","AlgVer"),)
#		verbose_name=_("face template")#u"人员面部"
#		verbose_name_plural=verbose_name




"""大容量协议，暂时未考虑
DATA UPDATE BIODATA Pin=%s\tNo=0\tIndex=%s\tValid=1\tDuress=0\tType=%s\tMajorVer=%s\tMinorVer=0\tFormat=0\tTmp=%s
"""
class BioData(models.Model):
    id=models.AutoField(primary_key=True)
    UserID = models.ForeignKey("employee", db_column='userid', verbose_name=_(u"员工"))
    bio_tmp = models.TextField(_(u'特征模板'))
    bio_no = models.IntegerField(_(u'编号'), default=0, null=True)#生物具体个体编号，默认值为0 0为左眼 1为右眼  0为左手 1为右手 指纹0---9
    bio_index = models.IntegerField(_(u'序号'),default=0, null=True)#生物具体个体模板编号，该值一般都为0，一个指静脉3个模板保存在一行，因此bio_index=0 一张脸12个保存在一行
    bio_type = models.IntegerField(_(u'模板类型'))# 0 通用 1 指纹 2 面部 3  声纹  4 虹膜 5 视网膜  6 掌纹 7 指静脉  8       手掌
    majorver = models.CharField(_(u'算法版本'), max_length=30)#指纹版本存10,9 非10.0
    minorver = models.CharField(_(u'算法版本'), max_length=30, null=True)
    bio_format = models.IntegerField(_(u'算法格式'), default=0, null=True)#模板格式，如指纹有ZK=0\ISO=1\ANSI=2等格式
    valid = models.IntegerField(_(u'是否有效'),default=1, choices=BOOLEANS)#是否有效标示，0：无效，1：有效，默认为1
    duress = models.IntegerField(_(u'是否协迫'),default=0, choices=BOOLEANS)#是否胁迫标示，0：非胁迫，1：胁迫，默认为0
    UTime = models.DateTimeField(_('refresh time'), null=True, blank=True, editable=False)
    SN = models.ForeignKey(iclock, db_column='SN', verbose_name=_(u'登记设备'), null=True, blank=True)
    def __unicode__(self):
        return u"%s,%s"%(self.UserID.__unicode__(), unicode(self.bio_type))

    def template(self):
        return self.bio_tmp.decode("base64")

    def temp(self):
        #去掉BASE64编码的指纹模板中的回车
        return self.bio_tmp.replace("\n","").replace("\r","")

    class Admin:
        list_display=('UserID', 'bio_type', 'valid')
        list_filter = ('UserID',)
        search_fields = ['=UserID__PIN','=UserID__EName','UserID__Workcode']

    class Meta:
        db_table = 'bio_data'
        unique_together = (("UserID", "bio_no", "bio_type", "majorver"),)
        verbose_name = _(u"特征模板")
        verbose_name_plural=verbose_name

    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    def bio_type_name(self, ):
        bio_type_names=(_(u'通用'),_(u'指纹') ,_(u'面部'),_(u'声纹'),_(u'虹膜'),_(u'视网膜'),_(u'掌纹'),_(u'指静脉'),_(u'手掌'))
        return bio_type_names[self.bio_type]
    def bio_name(self, ):
        if self.bio_type==bioFinger:
            return FINGERIDS[self.bio_no][1]
        elif self.bio_type==bioFace:
            return ''
        elif self.bio_type==bioIris:
            bio_type_names=(_(u'左眼'),_(u'右眼'))
            return bio_type_names[self.bio_no]
        return u''

    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
            {'name':'DeptName','sortable':False,'index':'UserID__DeptID','width':200,'label':unicode(_('department name'))},
            {'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'EName','index':'UserID__EName','width':100,'label':unicode(_('EName'))},
            {'name':'Workcode', 'index':'UserID__Workcode', 'width':100, 'label':unicode(_('NewPin'))},
            {'name':'bio_type','sortable':False,'width':80,'label':unicode(BioData._meta.get_field('bio_type').verbose_name)},
            {'name':'bio_no','width':60,'label':unicode(BioData._meta.get_field('bio_no').verbose_name)},
            {'name':'bio_name','sortable':False,'width':80,'label':unicode(_(u'名称'))},
            #{'name':'FaceName','width':100,'sortable':False,'label':unicode(facetemp._meta.get_field('FaceID').verbose_name)},
            {'name':'AlgVer','sortable':False,'width':80,'label':unicode(_('AlgVer'))},
            {'name':'SN','sortable':False,'width':120,'label':unicode(_('Device name'))},
            {'name':'UTime','width':120,'label':unicode(_(u'采集时间'))}
            ]







VERIFYS=(
(3, _("Card")),
(0, _("Password")),#控制器上传值为3保存时减3
(1, _("Fingerprint")),
(2, _("Card")),
(4, _("Card")),#为控制器
(5, _("Add")),

(9, _("Other")),
(11, _(u"卡+密码")),#为控制器

(15,_("FACE")),
(16,_("Mobile")),
)




COMVERIFYS=(#组合验证
(0, _("FP_OR_PW_OR_RF")),#指纹或密码或卡
(1, _("FP")),#指纹
(2, _("PIN")),#考勤号
(3, _("PW")),#密码
(4, _("RF")),#卡
(5, _("FP_OR_PW")),#指纹或密码
(6, _("FP_OR_RF")),#指纹或卡
(7, _("PW_OR_RF")),#密码或卡
(8, _("PIN_AND_FP")),#考勤号和指纹
(9, _("FP_AND_PW")),#指纹和密码
(10, _("FP_AND_RF")),#指纹和卡
(11, _("PW_AND_RF")),#密码和卡
(12, _("FP_AND_PW_AND_RF")),#指纹和密码和卡
(13, _("PIN_AND_FP_AND_PW")),#考勤号和指纹和密码
(14, _("FP_AND_RF_OR_PIN")),#指纹和卡和考勤号
(15,_("FACE")),
(16,_("FACE_AND_FP")),#人脸加指纹
(17, _("FACE_AND_PW")),#人脸加密码
(18, _("FACE_AND_RF")),#人脸加卡
(19, _("FACE_AND_FP_AND_RF")),#人脸加指纹加卡
(20, _("FACE_AND_FP_AND_PW")),#人脸加指纹加密码
)

#ATTSTATES=(
#("I",_("Check in")),
#("O",_("Check out")),
##("8",_("Meal start")),
##("9",_("Meal end")),
##("i",_("Overtime in")),
##("o",_("Overtime out")),
##("0",_("Break out")),
##("1",_("Break in")),
#("2",_("Break out")),
#("3",_("Break in")),
#("4",_("Overtime in")),
#("5",_("Overtime out")),
##("160",_("Test Data")),
#)

#新的默认状态定义,可以通过系统设置进行重新定义,变化是原来的I变成0,O变成1,获得状态名称统一通过getRecordName(state)实现
ATTSTATES=(
("I",_("Check in")),
("O",_("Check out")),
("i",_("Break out")),
("o",_("Break in")),
("V",_("Overtime in")),
("v",_("Overtime out")),
)

def transAttState(state):
    if state:
        for i in range(len(ATTSTATES)):
            if ATTSTATES[i][0] in state:
                return ATTSTATES[i][1].title()
        return ''
    else:
        return ''

def tranAttVerify(code):
    if code:
        for i in range(len(VERIFYS)):
            if VERIFYS[i][0]==code:
                return VERIFYS[i][1].title()
        return ''
    else:
        return ''


def createThumbnail(imgUrlOrg, imgUrl):
    import PIL.Image as Image

    try:
        im = Image.open(imgUrlOrg)
    except IOError, e:
#		print "error to open", imgUrlOrg, e.message
        return
    cur_width, cur_height = im.size
    new_width, new_height = 100,75
    if 0: #crop
        if cur_width < cur_height:
            ratio = float(new_width)/cur_width
        else:
            ratio = float(new_height)/cur_height
        x = (cur_width * ratio)
        y = (cur_height * ratio)
        x_diff = int(abs((new_width - x) / 2))
        y_diff = int(abs((new_height - y) / 2))
        box = (x_diff, y_diff, (x-x_diff), (y-y_diff))
        resized = im.resize((x, y), Image.ANTIALIAS).crop(box)
    else:
        if not new_width == 0 and not new_height == 0:
            if cur_width > cur_height:
                ratio = float(new_width)/cur_width
            else:
                ratio = float(new_height)/cur_height
        else:
            if new_width == 0:
                ratio = float(new_height)/cur_height
            else:
                ratio = float(new_width)/cur_width
        resized=im.resize((int(cur_width*ratio), int(cur_height*ratio)), Image.ANTIALIAS)
    try:
        os.makedirs(os.path.split(imgUrl)[0])
    except:
        pass
    resized.save(imgUrl)
#	print "save to:", imgUrl
    return imgUrl





class transactions(models.Model):
    UserID = models.ForeignKey("employee", db_column='userid', verbose_name=_("employee"))
    TTime = models.DateTimeField(_('time'), db_column='checktime')
    State = models.CharField(_('state'), db_column='checktype', max_length=5,null=True, default='I')  #原长度为1  门禁功能中表示进出
    Verify = models.IntegerField(_('verification'), db_column='verifycode', null=True,default=0, choices=VERIFYS)
    SN = models.ForeignKey(iclock, db_column='SN', verbose_name=_('device'), null=True, blank=True)
    #sensorid = models.CharField(db_column='sensorid', verbose_name=u'Sensor ID', null=True, blank=True, max_length=5, editable=False)

    NewType = models.CharField(_('NewType'), max_length=3,null=True,blank=True)
    AbNormiteID=models.IntegerField(null=True,blank=True)
    SchID=models.IntegerField(_('Schclass'), null=True,blank=True)



    purpose = models.IntegerField(u'用途',null=True)#0考勤记录 1 会议记录    2 ...   3 ...
    WorkCode = models.CharField(_('work code'), max_length=10, null=True, blank=True)
    Reserved = models.CharField(_('Reserved'), max_length=100, null=True, blank=True)
    #Reserved2 = models.CharField(_('Memo'), max_length=40, db_column='Reserved2',null=True, blank=True)
    #DeptID = models.IntegerField(db_column='deptid', default=1,editable=False,null=True, blank=True)

    def getComVerifys(self):
        try:
            if self.SN:
                iclockObj=getDevice(self.SN_id)#iclock.objects.get(SN=self.SN_id)
                if iclockObj.Authentication==2:
                    for i in range(len(COMVERIFYS)):
                        if self.Verify==COMVERIFYS[i][0]:
                            return COMVERIFYS[i][1].title()
                else:
                    return self.get_Verify_display()
            else:
                return ""
        except Exception,e:
            print 99999999,e
            return ""#self.get_Verify_display()
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    def Time(self):
        #if self.TTime.microsecond>500000:
        #	self.TTime=self.TTime+datetime.timedelta(0,0,1000000-self.TTime.microsecond)
        return self.TTime
    def StrTime(self,diffSec=0):
        tm=self.Time()+datetime.timedelta(seconds=diffSec)
        return tm.strftime('%Y%m%d%H%M%S')
    @staticmethod
    def delOld(): return ("TTime", 365)
    def Device(self):
        return getDevice(self.SN_id)
    def getImgUrl(self, user,default=None):
        #from mysite.utils import getUploadFileURL
        if GetParamValue('opt_users_rec_pic','0',user.id)!='1':return ''
        device=self.Device()
        emp=self.employee()

        if emp and device:
            pin=formatPIN(emp.PIN)
            #try:
            #	pin=int(emp.PIN)
            #except:
            #	pin=emp.PIN
            fname="%s-%s.jpg"%(self.StrTime(),pin)
            imgUrl=getUploadFileName("%s/%s"%(device.SN,self.TTime.strftime('%Y%m')),'', fname)
            if os.path.exists(imgUrl):
                return getUploadFileURL("%s/%s"%(device.SN,self.TTime.strftime('%Y%m')), '', fname)
            #解决考勤照片与记录时间差的问题
            fname="%s-%s.jpg"%(self.StrTime(-1),pin)
            imgUrl=getUploadFileName("%s/%s"%(device.SN,self.TTime.strftime('%Y%m')),'', fname)
            if os.path.exists(imgUrl):
                return getUploadFileURL("%s/%s"%(device.SN,self.TTime.strftime('%Y%m')), '', fname)
            fname="%s-%s.jpg"%(self.StrTime(-2),pin)
            imgUrl=getUploadFileName("%s/%s"%(device.SN,self.TTime.strftime('%Y%m')),'', fname)
            if os.path.exists(imgUrl):
                return getUploadFileURL("%s/%s"%(device.SN,self.TTime.strftime('%Y%m')), '', fname)
            fname="%s-%s.jpg"%(self.StrTime(1),pin)
            imgUrl=getUploadFileName("%s/%s"%(device.SN,self.TTime.strftime('%Y%m')),'', fname)
            if os.path.exists(imgUrl):
                return getUploadFileURL("%s/%s"%(device.SN,self.TTime.strftime('%Y%m')), '', fname)



        return default
#	def getThumbnailUrl(self, default=None):
#		device=self.Device()
#		emp=self.employee()
#		if device and emp:
#			try:
#				pin=int(emp.PIN)
#			except:
#				pin=emp.PIN
#			fname="%s.jpg"%(self.StrTime())
#			imgUrl=getUploadFileName("thumbnail/"+device.SN, pin, fname)
#			#print imgUrl
#			if not os.path.exists(imgUrl):
#				imgUrlOrg=getUploadFileName(device.SN, pin, fname)
#				if not os.path.exists(imgUrlOrg):
#					#print imgUrlOrg, "is not exists"
#					return default
#				if not createThumbnail(imgUrlOrg, imgUrl):
#					#print imgUrl, "create fail."
#					return default
#			return getUploadFileURL("thumbnail/"+device.SN, pin, fname)
#		#print "device, emp", device, emp
#		return default
    def __unicode__(self):
        return self.UserID.__unicode__()+', '+self.TTime.strftime("%y-%m-%d %H:%M:%S")
    @staticmethod
    def colModels(request=None):
        ret= [
            {'name':'id','hidden':True},
            {'name':'DeptID','width':80,'index':'UserID__DeptID','label':unicode(_('department number'))},
            {'name':'DeptName','width':180,'index':'UserID__DeptID__DeptName','label':unicode(_('department name'))},
            {'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'Workcode', 'index':'UserID__Workcode', 'width':120, 'label':unicode(_('NewPin'))},
            {'name':'EName','index':'UserID__EName','width':80,'label':unicode(_('EName'))},
            {'name':'TTime','width':120,'search':False,'label':unicode(transactions._meta.get_field('TTime').verbose_name)},
            {'name':'State','width':80,'hidden':False,'search':False,'label':unicode(transactions._meta.get_field('State').verbose_name)},
            {'name':'Verify','width':80,'search':False,'label':unicode(transactions._meta.get_field('Verify').verbose_name),'hidden':True},
            {'name':'Device','index':'SN','width':180,'label':unicode(_('Device name'))},
            #{'name':'valid','sortable':False,'width':80,'label':unicode(_(u'时间校验'))},
            {'name':'photo','search':False,'sortable':False,'width':80,'label':u'登记照片'},
            {'name':'thumbnailUrl','search':False,'sortable':False,'width':100,'label':u'考勤照片'}
            ]
        #if GetParamValue('opt_basic_checkinouttype','')=='0' or  GetParamValue('opt_basic_checkinouttype','0')==0:
        is_state= int(GetParamValue('opt_basic_checkinouttype','0'))
        is_rec_pic=0
        if request:
            is_rec_pic= int(GetParamValue('opt_users_rec_pic','0',request.user.id))
        is_emp_pic= int(GetParamValue('opt_basic_emp_pic','0'))


        for t in ret:
            if is_state==0 and t['name']=='State':
                t['hidden']=True
            if is_rec_pic==0 and t['name']=='thumbnailUrl':
                t['hidden']=True
            if is_emp_pic==0 and t['name']=='photo':
                t['hidden']=True
        return ret
    class Meta:
        verbose_name=_("transaction")
        verbose_name_plural=_("transaction")
        db_table = 'checkinout'
        unique_together = (("UserID", "TTime"),)
        permissions = (
#				('clearObsoleteData_transaction','Clear Obsolete Data'),
                ('monitor_oplog', 'Transaction Monitor'),
                )

    class Admin:
        list_display=('State','Verify','SN')
        list_filter = ('State','Verify','SN',)
        search_fields = ['=UserID__PIN','UserID__EName','UserID__Workcode']
def OpName(op):
    OPNAMES={0: _("start up"),
        1: _("shutdown"),
        2: _("validation failure"),
        3: _("alarm"),
        4: _("enter the menu"),
        5: _("change settings"),
        6: _("registration fingerprint"),
        7: _("registration password"),
        8: _("card registration"),
        9: _("delete User"),
        10: _("delete fingerprints"),
        11: _("delete the password"),
        12: _("delete RF card"),
        13: _("remove data"),
        14: _("MF create cards"),
        15: _("MF registration cards"),
        16: _("MF registration cards"),
        17: _("MF registration card deleted"),
        18: _("MF clearance card content"),
        19: _("moved to the registration card data"),
        20: _("the data in the card copied to the machine"),
        21: _("set time"),
        22: _("restore factory settings"),
        23: _("delete records access"),
        24: _("remove administrator rights"),
        25: _("group set up to amend Access"),
        26: _("modify user access control settings"),
        27: _("access time to amend paragraph"),
        28: _("amend unlock Portfolio"),
        29: _("unlock"),
        30: _("registration of new users"),
        31: _("fingerprint attribute changes"),
        32: _("stress alarm"),
        34: _("Lock"),
        35: _("Button"),
        36: _("Alarm Off"),


        } #{0: u"开机",
        #1: u"关机",
        #2: u"验证失败",
        #3: u"报警",
        #4: u"进入菜单",
        #5: u"更改设置",
        #6: u"登记指纹",
        #7: u"登记密码",
        #8: u"登记HID卡",
        #9: u"删除用户",
        #10: u"删除指纹",
        #11: u"删除密码",
        #12: u"删除射频卡",
        #13: u"清除数据",
        #14: u"创建MF卡",
        #15: u"登记MF卡",
        #16: u"注册MF卡",
        #17: u"删除MF卡注册",
        #18: u"清除MF卡内容",
        #19: u"把登记数据移到卡中",
        #20: u"把卡中的数据复制到机器中",
        #21: u"设置时间",
        #22: u"恢复出厂设置",
        #23: u"删除进出记录",
        #24: u"清除管理员权限}",
        #25: u"修改门禁组设置",
        #26: u"修改用户门禁设置",
        #27: u"修改门禁时间段",
        #28: u"修改开锁组合设置",
        #29: u"开锁",
        #30: u"登记新用户",
        #31: u"更改指纹属性",
        #32: u"胁迫报警",
    try:
        return u'%s'%OPNAMES[op]
    except:
        return op and "%s"%op or ""

def AlarmName(obj):
    ALARMNAMES={
        50:_("Door Close Detected"),
        51:_("Door Open Detected"),
        55:_("Machine Been Broken"),
        53:_("Out Door Button"),
        54:_("Door Broken Accidentally"),
        58:_("Try Invalid Verification"),
        59:_("Force"),
        60:_(u"设备脱机"),
        4:_(u"门打开"),
        5:_(u"门关闭"),
        65535:_("Alarm Cancelled"),
    }
    try:
        return u'%s'%ALARMNAMES[obj]
    except:
        return obj and "%s"%obj or ""
#设备操作日志										   
class oplog(models.Model):
    SN = models.ForeignKey(iclock, db_column='SN', verbose_name=_('device'), null=True, blank=True)
    admin = models.IntegerField(_('device administrator'), null=False, blank=False, default=0)
    OP = models.SmallIntegerField(_('Operation'), null=False, blank=False, default=0)
    OPTime=models.DateTimeField(_('time'))
    Object=models.IntegerField(_('Object'), null=True, blank=True)
    Param1=models.IntegerField(_('Parameter1'), null=True, blank=True)
    Param2=models.IntegerField(_('Parameter2'), null=True, blank=True)
    Param3=models.IntegerField(_('Parameter3'), null=True, blank=True)
    def Device(self):
        return getDevice(self.SN_id)
    @staticmethod
    def delOld(): return ("OPTime", 200)
    def OpName(self):
        return OpName(self.OP)
    def ObjName(self):
        if self.OP==3:
            return AlarmName(self.Object)
        return self.Object or ""
    def __unicode__(self):
        return "%s,%s,%s"%(self.Device(), self.OP, self.OPTime.strftime("%y-%m-%d %H:%M:%S"))
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'SN','width':200,'label':unicode(oplog._meta.get_field('SN').verbose_name)},
            {'name':'admin','width':150,'label':unicode(oplog._meta.get_field('admin').verbose_name)},
            {'name':'OpName','index':'OP','width':220,'label':unicode(oplog._meta.get_field('OP').verbose_name)},
            {'name':'OPTime','width':120,'label':unicode(oplog._meta.get_field('OPTime').verbose_name)},
            {'name':'ObjName','index':'Object','width':200,'label':unicode(oplog._meta.get_field('Object').verbose_name)}

            ]
    class Meta:
        verbose_name=_("device operation log")
        verbose_name_plural=_("device operation logs")
        unique_together = (("SN", "OPTime"),)
        permissions = (
#			('monitor_oplog', 'Transaction Monitor'),
            )
    class Admin:
        list_display=('SN','admin','OP','OPTime', 'Object',)
        list_filter = ('SN','admin','OP','OPTime')
        search_fields=['SN__SN','SN__Alias']
class iaccessoplog(models.Model):
    SN = models.ForeignKey(iclock, db_column='SN', verbose_name=_('device'), null=True, blank=True)
    Even = models.CharField(_('Operation'), max_length=20,null=False, blank=False, default=0)#OP
    OPTime=models.DateTimeField(_('time'))
    Object=models.CharField(_('Object'),  max_length=20,null=True, blank=True)
    Message=models.CharField(_(u'事件'),  max_length=20,null=True, blank=True)#object
    Param1=models.IntegerField(_('Parameter1'), null=True, blank=True)
    Param2=models.IntegerField(_('Parameter2'), null=True, blank=True)
    Param3=models.CharField(_('Parameter3'),  max_length=20,null=True, blank=True)
    def Device(self):
        return getDevice(self.SN_id)
    @staticmethod
    def delOld(): return ("OPTime", 200)
    def OpName(self):
        #print 883332,OpName(int(self.Even))
        return OpName(int(self.Even))
    def ObjName(self):
#		if self.OP==3:
        #print 33333,AlarmName(int(self.Message))
        return AlarmName(int(self.Message))
#		return self.Object or ""
    def __unicode__(self):
        return "%s,%s,%s"%(self.Device(), self.Even, self.OPTime.strftime("%y-%m-%d %H:%M:%S"))
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'SN','width':200,'label':unicode(iaccessoplog._meta.get_field('SN').verbose_name)},
            {'name':'ObjName','index':'Object','width':80,'label':unicode(iaccessoplog._meta.get_field('Object').verbose_name)},
            {'name':'OPTime','width':120,'label':unicode(iaccessoplog._meta.get_field('OPTime').verbose_name)},
            {'name':'OpName','index':'Even','width':150,'label':unicode(iaccessoplog._meta.get_field('Even').verbose_name)},
            {'name':'Message','width':150,'label':unicode(iaccessoplog._meta.get_field('Message').verbose_name)}
            ]
    class Meta:
        verbose_name=_("iaccessoplog")
        verbose_name_plural=_("iaccessoplog")
        unique_together = (("SN", "OPTime"),)
        permissions = (
            ('monitor_iaccessoplog', 'Transaction Monitor'),
            )
    class Admin:
        list_display=('SN','Message','Even','OPTime', 'Object',)
        list_filter = ('SN','Message','Even','OPTime')
        search_fields=['SN__SN','SN__Alias']
#设备上传数据日志		
class devlog(models.Model):
    SN = models.ForeignKey(iclock, verbose_name=_('device'))
    OP = models.CharField(_('data'),max_length=8, default="TRANSACT",)
    Object = models.CharField(_('object'),max_length=60, null=True, blank=True)
    Cnt = models.IntegerField(_('record count'),default=1, blank=True)
    ECnt = models.IntegerField(_('error count'),default=0, blank=True)
    OpTime = models.DateTimeField(_('Upload Time'))
    def Device(self):
        return getDevice(self.SN_id)
    @staticmethod
    def delOld(): return ("OpTime", 30)
    def save(self, *args, **kwargs):
        if not self.id:
            self.OpTime=datetime.datetime.now()
        models.Model.save(self, *args, **kwargs)
    def __unicode__(self): return "%s, %s, %s"%(self.SN, self.OpTime.strftime('%y-%m-%d %H:%M'), self.OP)
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'Device','index':'SN__SN','width':200,'label':unicode(_('device'))},
            {'name':'OpTime','width':150,'label':unicode(devlog._meta.get_field('OpTime').verbose_name)},
            {'name':'OP','width':220,'label':unicode(devlog._meta.get_field('OP').verbose_name)},
            {'name':'Object','width':220,'label':unicode(devlog._meta.get_field('Object').verbose_name)},
            {'name':'Cnt','width':90,'label':unicode(devlog._meta.get_field('Cnt').verbose_name)},
            {'name':'ECnt','width':40,'label':unicode(devlog._meta.get_field('ECnt').verbose_name)},
            {'name':'DeviceSN','hidden':True}

            ]

    class Admin:
        list_display=('SN','OpTime','OP','Cnt','Object',)
        list_filter=("SN",'OpTime')
        search_fields = ["=SN__SN","OP","Object"]
    class Meta:
        verbose_name=_("data from device")
        verbose_name_plural=verbose_name
        db_table = 'devlog'


class devcmds(models.Model):
    SN = models.ForeignKey("iclock", verbose_name=_('device'))
    #UserName = models.CharField('提交用户',max_length=20,null=True, blank=True)
    CmdContent = models.TextField(_('command content'))
    CmdCommitTime = models.DateTimeField(_('submit time'))
    CmdTransTime = models.DateTimeField(_('transfer time'),null=True, blank=True)
    CmdOverTime = models.DateTimeField(_('return time'),null=True, blank=True)
    CmdReturn = models.IntegerField(_('return value'), null=True, blank=True)

    def Device(self):
        return getDevice(self.SN_id)
    def __unicode__(self):
        return u"%s, %s" % (self.SN, self.CmdCommitTime.strftime('%y-%m-%d %H:%M'))
    def save(self, *args, **kwargs):
        super(devcmds, self).save(*args, **kwargs)



    def fileURL(self):
        if self.CmdContent.find("GetFile ")==0:
            fname=self.CmdContent[8:]
        elif self.CmdContent.find("Shell ")==0:
            fname="shellout.txt"
        else:
            return ""
        return getUploadFileURL(self.SN.SN, self.id, fname)
    @staticmethod
    def delOld(): return ("CmdOverTime", 10)
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'Device','index':'SN__SN','width':180,'label':unicode(_('device'))},
            {'name':'CmdContent','sortable':False,'width':400,'label':unicode(devcmds._meta.get_field('CmdContent').verbose_name)},
            {'name':'CmdCommitTime','width':120,'label':unicode(devcmds._meta.get_field('CmdCommitTime').verbose_name)},
            {'name':'CmdTransTime','width':120,'label':unicode(devcmds._meta.get_field('CmdTransTime').verbose_name)},
            {'name':'CmdOverTime','width':120,'label':unicode(devcmds._meta.get_field('CmdOverTime').verbose_name)},
            {'name':'CmdReturn','width':50,'label':unicode(devcmds._meta.get_field('CmdReturn').verbose_name)},
            {'name':'fileURL','hidden':True}

            ]

    class Admin:
        list_display=('SN','CmdCommitTime','CmdTransTime','CmdOverTime','CmdContent',)
        search_fields = ["=SN__SN"]
        list_filter =['SN', 'CmdCommitTime', 'CmdOverTime']
    class Meta:
        db_table = 'devcmds'
        verbose_name=_("command to device")
        verbose_name_plural=verbose_name

class AttDataProofCmd(models.Model):
    SN = models.ForeignKey("iclock", verbose_name=_('device'))
    OperateTime = models.DateTimeField(_('Operate time'))
    StartTime = models.DateTimeField(_('Begin time'),null=True, blank=True)
    EndTime = models.DateTimeField(_('End time'),null=True, blank=True)
    DevCount = models.IntegerField(_('DevCount'), null=True, blank=True)
    SerCount = models.IntegerField(_('SerCount'), null=True, blank=True)
    flag=models.IntegerField(_('state'),null=True,default=0,blank=True)#状态0正常，-1异常
    Reserved=models.IntegerField(null=True,default=0,blank=True,editable=False)
    Reserved1=models.FloatField(null=True,default=0,blank=True,editable=False)
    Reserved2=models.CharField(max_length=30,null=False,editable=False)

    def Device(self):
        return getDevice(self.SN_id)
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'Device','index':'SN__SN','width':200,'label':unicode(_('device'))},
            {'name':'OperateTime','width':120,'label':unicode(AttDataProofCmd._meta.get_field('OperateTime').verbose_name)},
            {'name':'StartTime','width':120,'label':unicode(AttDataProofCmd._meta.get_field('StartTime').verbose_name)},
            {'name':'EndTime','width':120,'label':unicode(AttDataProofCmd._meta.get_field('EndTime').verbose_name)},
            {'name':'flag','width':60,'label':unicode(AttDataProofCmd._meta.get_field('flag').verbose_name)},
            {'name':'DevCount','width':100,'label':unicode(AttDataProofCmd._meta.get_field('DevCount').verbose_name)},
            {'name':'SerCount','width':100,'label':unicode(AttDataProofCmd._meta.get_field('SerCount').verbose_name)}
            ]

    class Admin:
        list_display=('SN__SN','OperateTime','StartTime','EndTime',)
        search_fields = ["SN__SN"]
        list_filter =['SN', 'OperateTime', 'StartTime','EndTime']
    class Meta:
        db_table = 'attdataproofcmd'
        verbose_name=_("attdata proof cmd")
        verbose_name_plural=verbose_name

def isUpdatingFW(device):
    return devcmds.objects.filter(SN=device, CmdReturn__isnull=True, CmdContent__startswith='PutFile ', CmdContent__endswith='main.gz.tmp',).count()

def clearData():
    for obj in employee.objects.all(): obj.delete()
    for obj in devcmds.objects.all():
        obj.CmdOverTime=None
        obj.CmdTransTime=None
        obj.save()
    for obj in iclock.objects.all():
        obj.LogStamp=0
        obj.OpLogStamp=0
        cache.delete("iclock_"+obj.SN)
        obj.DelTag=1
        obj.save()


#Iclock 信息订阅服务

M_WEATHER=1
M_NEWS=2
M_DEPT_NOTES=3
M_SYS_NOTES=4
M_DEPT_SMS=6
M_PRIV_SMS=5

PUBMSGSERVICES=(
(M_NEWS, _("News Channel")),
(M_DEPT_NOTES, _("Company Notice")),
(M_SYS_NOTES, _("Notice System")),
(M_DEPT_SMS, _("Companies short message")),
)

MSGSERVICES=(
(M_WEATHER, _("Weather Forecast")),
(M_PRIV_SMS, _("Employee SMS")),
(M_NEWS, _("News Channel")),
(M_DEPT_NOTES, _("Company Notice")),
(M_SYS_NOTES, _("System Notice")),
(M_DEPT_SMS, _("Companies SMS")),
)

class messages(models.Model):
    MsgType = models.IntegerField(_("type"), null=False, blank=False, default=5, choices=PUBMSGSERVICES)
    StartTime = models.DateTimeField(_("take effect"), null=False, blank=False)
    EndTime	= models.DateTimeField(_("out-of-service"), null=True, blank=True)
    MsgContent = models.TextField(_("Content"), max_length=2048, null=True, blank=True)
    MsgImage = models.CharField(_("picture"), max_length=64, null=True, blank=True)
    DeptID = models.ForeignKey(department, verbose_name=_('company/department'), null=True, blank=True)
    MsgParam = models.CharField(_("parameter"), max_length=32, null=True, blank=True)
    def __unicode__(self):
        return unicode(u"%s[%s]: %s"%(self.get_MsgType_display(), self.StartTime, self.MsgContent and self.MsgContent[:40] and ''))
    class Admin:
        list_filter =['StartTime','MsgType', 'MsgParam', 'DeptID']
    class Meta:
        verbose_name=_("public information")
        verbose_name_plural=verbose_name


class IclockMsg(models.Model):
    SN = models.ForeignKey(iclock, verbose_name=_('device'), null=False, blank=False)
    MsgType = models.IntegerField(_("type"), null=False, blank=False, default=5, choices=MSGSERVICES)
    StartTime = models.DateTimeField(_("take effect"), null=False, blank=False)
    EndTime	= models.DateTimeField(_("out-of-service"), null=True, blank=True)
    MsgParam = models.CharField(_("parameter"), max_length=32, null=True, blank=True)
    MsgContent = models.CharField(_("content"), max_length=200, null=True, blank=True)
    LastTime = models.DateTimeField(_("recently service"), null=True, blank=True, editable=False)
    def Device(self):
        return getDevice(self.SN_id)
    def __unicode__(self):
        return unicode(u"%s"%(self.SN))
    class Admin:
        list_filter =['SN','MsgType','StartTime','EndTime']
    class Meta:
        verbose_name=_("information subscription")
        verbose_name_plural=verbose_name

class adminLog(models.Model):
    time = models.DateTimeField(_('time'), null=False, blank=False)
    User = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('administrator'), null=True, blank=True)
    model = models.CharField(_('data'), max_length=40, null=True, blank=True)
    action = models.CharField(_('operation'), max_length=40, default="Modify", null=False, blank=False)
    object = models.CharField(_('object'), max_length=100, null=True, blank=True)
    count = models.IntegerField(_('amount'), default=1, null=False, blank=False)
    @staticmethod
    def delOld(): return ("time", 200)
    #def save(self):
    #	if not self.id: self.time=datetime.datetime.now()
    #	logFile(self.time.strftime("%Y-%m-%d %H:%M:%S")+'   '+self.User.username+'  '+self.action)
    #	models.Model.save(self)
    def __unicode__(self):
        if self.User:
            return u"[%s]%s, %s"%(self.time, self.User.username, self.action)
        else:
            return u"[%s]%s, %s"%(self.time, '', self.action)

    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'time','width':120,'label':unicode(adminLog._meta.get_field('time').verbose_name)},
            {'name':'User','width':80,'label':unicode(adminLog._meta.get_field('User').verbose_name)},
            {'name':'action','width':220,'label':unicode(adminLog._meta.get_field('action').verbose_name)},
            {'name':'model','width':220,'label':unicode(adminLog._meta.get_field('model').verbose_name)},
            {'name':'object','width':220,'label':unicode(adminLog._meta.get_field('object').verbose_name)},
            {'name':'count','width':80,'label':unicode(adminLog._meta.get_field('count').verbose_name)}

            ]
    class Admin:
        list_filter =['time','User','model']
        search_fields = ['User__username']
    class Meta:
        verbose_name=_("administration log")
        verbose_name_plural=_("administration logs")
        #unique_together = (("time", "User"),)


    def save(self, *args, **kwargs):
        if self.model=='level_door' or self.model=='level_emp':
            self.model='level'
        super(adminLog, self).save(*args, **kwargs)


#员工登陆日志
class employeeLog(models.Model):
    LTime = models.DateTimeField(_('time'),  null=False, blank=False)
    PIN = models.CharField(_('PIN'), max_length=24, null=False, blank=False)
    Name = models.CharField(_('EName'), max_length=24, null=True, blank=False)
    DeptID = models.IntegerField(_('Dept'),  null=True, blank=False)
    action = models.CharField(_('operation'), max_length=20, default="Login", null=True, blank=True)
    loginIP = models.CharField(_('Login IP'), max_length=100, null=True, blank=True)
#	count = models.IntegerField(_('amount'), default=1, null=False, blank=False)
    def __unicode__(self):
        return unicode(u"[%s]%s, %s"%(self.LTime, self.PIN, self.action))

    def Dept(self):
        return department.objByID(self.DeptID)

    def save(self, *args, **kwargs):
        super(employeeLog, self).save(*args, **kwargs)

    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'LTime','width':120,'label':unicode(employeeLog._meta.get_field('LTime').verbose_name)},
            {'name':'PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'Name','width':120,'label':unicode(_('EName'))},
            {'name':'DeptName','width':180,'sortable':False,'label':unicode(_('department name'))},
            {'name':'action','width':220,'label':unicode(employeeLog._meta.get_field('action').verbose_name)},
            {'name':'loginIP','width':120,'label':u'登陆IP'},
            ]
    class Admin:
        list_filter =[]
        search_fields = ['PIN','Name']
    class Meta:
        verbose_name=_(u"员工登陆日志")
        verbose_name_plural=_(u"员工登陆日志")
        unique_together = (("LTime", "PIN"),)

def delOldRecords(model, field, days):
    table=model._meta.db_table
    field=model._meta.get_field(field).column
    #cursor = connection.cursor()
    if 'oracle' in settings.DATABASE_ENGINE:
        sql="DELETE FROM %s WHERE %s < TIMESTAMP '%s 00:00:00'"%(table, field,days )#str((datetime.datetime.today())-datetime.timedelta(days))
    else:
        sql="DELETE FROM %s WHERE %s < '%s'"%(table, field, days)#str((datetime.datetime.today()).date()-datetime.timedelta(days))
    customSql(sql)
    # try:
    #     #cursor.execute(sql)
    #     #connection._commit()
    # except:
    #     #connection.close()
    #     cursor.execute(sql)
    #     connection._commit()

#	for t in adminLog.objects.filter(time__lt=datetime.datetime.now()-datetime.timedelta(200)):
#		t.delete()





def customSql(sql,params=[],action=True):
    try:
        cursor = connection.cursor()
        cursor.execute(sql,params)
    except Exception,e:
        cursor= None
    if action:
        connection.commit()
    return cursor

def customSqlEx(sql,params=[],action=True,connDB=None):
    if connDB:
        conn=connections[connDB]
        cursor = conn.cursor()
        if settings.DB_ENGINE == 'ibm_db_django':
            if not params:params=()

    else:
        cursor = connection.cursor()
        if settings.DATABASE_ENGINE == 'ibm_db_django':
            if not params:params=()
    if params:
        cursor.execute(sql,params)
    else:
        cursor.execute(sql)
    if action:
        connection.commit()
    return cursor
##员工考勤修改日志##
##补签记录##
class checkexact(models.Model):
    UserID = models.ForeignKey(employee, db_column='UserID', null=False, default=1, verbose_name=_("employee"))
    CHECKTIME = models.DateTimeField(_('Check time'),null=True,default=0, blank=True)
    CHECKTYPE=models.CharField(_('Check type'),max_length=2, null=True, default='I',blank=True, choices=ATTSTATES)
    ISADD=models.SmallIntegerField(null=True, blank=True,editable=False)
    YUYIN=models.CharField(_('reson'),max_length=100, null=True, blank=True)
    ISMODIFY=models.SmallIntegerField(null=True, default=0,blank=True,editable=False)
    ISDELETE=models.SmallIntegerField(null=True,default=0, blank=True,editable=False)
    INCOUNT=models.SmallIntegerField(null=True,default=0, blank=True,editable=False)
    ISCOUNT=models.SmallIntegerField(null=True, default=0,editable=False)
    MODIFYBY = models.CharField(_('Modify by'),max_length=20,null=True, blank=True)
    SaveStamp = models.CharField(_('Modify date'),max_length=20,null=True, blank=True)
    #DATE=models.DateTimeField(_('Modify date'),null=True, blank=True)
    State=models.IntegerField(_('state'), null=True, default=0, blank=True, choices=AUDIT_STATES, editable=False)
    ApplyDate=models.DateTimeField(_('apply date'), null=True,  blank=True)
    SN = models.ForeignKey(iclock, db_column='SN', verbose_name=_('device'), null=True, blank=True)
    roleid = models.IntegerField(_(u'当前审核人'),editable=True)
    process=models.CharField(_(u'审核流程'),max_length=80,null=True,blank=True)
    oldprocess=models.CharField(_(u'审核过的流程'),max_length=80,null=True,blank=True)
    processid=models.IntegerField(_(u'审核流程id'),editable=True)
    procSN=models.IntegerField(_(u'已审序号'),default=0,editable=True)
    deptid=models.IntegerField(_(u'原始单位'),default=0,null=True,blank=True,editable=False)

    def __unicode__(self):
        return unicode(u"%s"%(self.UserID))
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    def Device(self):
        return getDevice(self.SN_id)
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True,'frozen':True},
            {'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN')),'frozen':True},
            {'name':'Workcode', 'index':'UserID__Workcode', 'width':120, 'label':unicode(_('NewPin')), 'frozen':True},
            {'name':'EName','index':'','sortable':False,'width':80,'label':unicode(_('EName')),'frozen':True},
            {'name':'DeptName','index':'UserID__DeptID','sortable':False,'width':120,'label':unicode(_('department name'))},
            {'name':'CHECKTIME','width':120,'label':unicode(checkexact._meta.get_field('CHECKTIME').verbose_name)},
            {'name':'CHECKTYPE','width':80,'sortable':False,'label':unicode(checkexact._meta.get_field('CHECKTYPE').verbose_name)},
            {'name':'process','sortable':False,'index':'process','width':220,'label':unicode(_(u'审核流'))},
            {'name':'YUYIN','width':80,'sortable':False,'label':unicode(checkexact._meta.get_field('YUYIN').verbose_name)},
            {'name':'MODIFYBY','width':120,'sortable':False,'label':unicode(checkexact._meta.get_field('MODIFYBY').verbose_name)},
            {'name':'State','index':'State','width':80,'label':unicode(checkexact._meta.get_field('State').verbose_name)},
            {'name':'ApplyDate','width':160,'sortable':False,'label':unicode(checkexact._meta.get_field('ApplyDate').verbose_name)},
            {'name':'Device','index':'SN','width':180,'label':unicode(_('Device name'))},
            #{'name':'SaveStamp','width':160,'sortable':False,'label':unicode(checkexact._meta.get_field('SaveStamp').verbose_name)}
            ]
    class Admin:
        list_filter =['UserID','CHECKTIME']
        search_fields = ['UserID__PIN','UserID__EName','UserID__Workcode']
        lock_fields=['UserID']
    class Meta:
        db_table = 'checkexact'
        verbose_name=_(u"补记录数据")
        verbose_name_plural=_(u"忘签到\签退")
        unique_together = (("UserID", "CHECKTIME","State"),)
        permissions = (
                        ('TransAudit_checkexact','Audit checkexact'),
            )

class EXCNOTES(models.Model):
    UserID = models.IntegerField(null=True, editable=False)
    AttDate = models.DateTimeField(_('Attendance date'),null=True, blank=True)
    Notes=models.CharField(_('Notes'),max_length=200, null=True, blank=True)
    class Admin:
        pass
    class Meta:
        db_table = 'EXCNOTES'
        unique_together = (("UserID", "AttDate"),)


HOLIDAY_NATIONS=(
    ('0',_('The Han nationality')),
    ('1',_('The Mongol nationality')),
    ('2',_('The Hui nationality')),
    ('3',_('The Tibetan nationality')),
    ('4',_('The Uyghur nationality')),
    ('5',_('The Miao nationality')),
    ('6',_('The Yi nationality')),
    ('7',_('The Chuang nationality')),
    ('8',_('The Puyi nationality')),
    ('9',_('The Korean nationality')),
    ('10',_('The Manchu nationality')),
    ('11',_('The Dongs nationality')),
    ('12',_('The Yao nationality')),
    ('13',_('The Pai nationality')),
    ('14',_('The Tujia nationality')),
    ('15',_('The Hani nationality')),
    ('16',_('The Kazak nationality')),
    ('17',_('The Dai nationality')),
    ('18',_('The Li nationality')),
    ('19',_('The Lisu ethnic Lisu nationality')),
    ('20',_('The Wa nationality')),
    ('21',_('The She nationality')),
    ('22',_('The Gaoshan nationality')),
    ('23',_('The Lahu nationality')),
    ('24',_('The Aquatic animals nationality')),
    ('25',_('The Dongxiang nationality')),
    ('26',_('The Naxi nationality')),
    ('27',_('The Jingpo nationality')),
    ('28',_('The Kirgiz nationality')),
    ('29',_('The Tu nationality')),
    ('30',_('The Daur nationality')),
    ('31',_('The Mulao nationality')),
    ('32',_('The Qiang nationality')),
    ('33',_('The Blang nationality')),
    ('34',_('The Salar nationality')),
    ('35',_('The Gelao nationality')),
    ('36',_('The Xibe nationality')),
    ('37',_('The Achang nationality')),
    ('38',_('The Pumi nationality')),
    ('39',_('The Tajik nationality')),
    ('40',_('The Nu nationality')),
    ('41',_('The Uzbek nationality')),
    ('42',_('The Russians nationality')),
    ('43',_('The Ewenki nationality')),
    ('44',_('The De\'ang nationality')),
    ('45',_('The Bonan nationality')),
    ('46',_('The Yugur nationality')),
    ('47',_('The Gin nationality')),
    ('48',_('The Tatar nationality')),
    ('49',_('The Derung nationality')),
    ('50',_('The Oroqen nationality')),
    ('51',_('The Hezhen nationality')),
    ('52',_('The Monba nationality')),
    ('53',_('The Lhoba nationality')),
    ('54',_('The Jino nationality')),

)

HolidayType_CHOICES=(

    (1,_(u'节日类型1')),
    (2,_(u'节日类型2')),
    (3,_(u'节日类型3')),


)


    ##节假日表##
class holidays(models.Model):
    HolidayID=models.AutoField(primary_key=True,null=False, editable=False)
    HolidayName=models.CharField(_('Holiday name'),max_length=20, null=False, blank=False)
    HolidayYear=models.SmallIntegerField(_('Year'), null=True, blank=True, editable=False)
    HolidayMonth=models.SmallIntegerField(_('Month'), null=True, blank=True, editable=False)
    HolidayDay=models.SmallIntegerField(_('Day'), null=True, default=1,blank=True, editable=False)
    StartTime = models.DateField(_('Beginning date'), null=False, blank=False)#help_text=_('Date format is ')+"ISO;"+ _('for example')+':1999-01-10/1999-1-11')     #请假时间为日期型
    Duration=models.SmallIntegerField(_('Duration times'), null=False, blank=False)
    HolidayType=models.SmallIntegerField(_('Holiday type'), null=True, blank=True,choices=HolidayType_CHOICES, editable=True,help_text=_(u'此选项仅用于门禁时间段设置使用，每个节假日类型最多32个节日'))
    XINBIE=models.CharField(_('Holiday sex'), max_length=4, null=True, blank=True, choices=GENDER_CHOICES, editable=False)
    MINZU=models.CharField(_('Holiday nation'), max_length=50, null=True, blank=True,choices=HOLIDAY_NATIONS, editable=False)
    DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)
    def __unicode__(self):
        return unicode(u"%s"%(self.HolidayName))
    def save(self):
        try:
            h = holidays.objects.get(HolidayName=self.HolidayName)
            if h.DelTag<>0:
                h.DelTag=0
            h.StartTime=self.StartTime
            h.Duration=self.Duration
            h.HolidayType=self.HolidayType
            super(holidays,h).save()
        except:
            super(holidays,self).save()
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'HolidayName','width':200,'label':unicode(holidays._meta.get_field('HolidayName').verbose_name)},
            {'name':'StartTime','width':120,'label':unicode(holidays._meta.get_field('StartTime').verbose_name)},
            {'name':'Duration','width':120,'label':unicode(holidays._meta.get_field('Duration').verbose_name)},
            {'name':'HolidayType','width':120,'label':unicode(holidays._meta.get_field('HolidayType').verbose_name)}
            ]
    class Admin:
        search_fields = ['HolidayName']
    class Meta:
        db_table = 'holidays'
        verbose_name=_('holidays')
        verbose_name_plural=verbose_name
        unique_together = (("HolidayName", "StartTime"),)


##班次排版时段表##

class NUM_RUN_DEIL(models.Model):
    Num_runID=models.ForeignKey("NUM_RUN", verbose_name=_("shift"), db_column='Num_runID', null=False, blank=False)
    StartTime = models.TimeField(_('beginning time'),null=False, blank=False)
    EndTime = models.TimeField(_('ending time'),null=True, blank=False)
    Sdays=models.SmallIntegerField(_('start day'),null=False, blank=False)
    Edays=models.SmallIntegerField(_('finish day'),null=True,blank=True)
    SchclassID=models.ForeignKey("SchClass", verbose_name=_('time-table class'), db_column='SchclassID', null=True,default=-1,blank=True)
    OverTime = models.IntegerField(_('Over time'),null=True,default=0,blank=True)
    def __unicode__(self):
        return unicode(u"%s,%s"%(self.Num_runID,self.SchclassID))

    class Admin:
        pass
    class Meta:
        db_table = 'NUM_RUN_DEIL'
        verbose_name = _('shift detail')
        verbose_name_plural=verbose_name
        unique_together = (("Num_runID", "Sdays","StartTime"),)


CYCLE_UNITS=(
    (0, _('Day')),
    (1, _('Week')),
    (2, _('Month')),
)

    ##班次表##
class NUM_RUN(models.Model):
    Num_runID=models.AutoField(primary_key=True,null=False, editable=False)
    OLDID=models.IntegerField(null=True,default=-1,blank=True, editable=False)
    Name=models.CharField(_('Sch name'),max_length=30,null=False)
    StartDate = models.DateField(_('Beginning date'),null=True,default='2017-01-01', blank=True) #日期型
    EndDate = models.DateField(_('Ending date'),null=True,default='2020-12-31', blank=True)    #日期型
    Cycle=models.SmallIntegerField(_('Cycle number'),null=True, db_column='Cyle', default=1,blank=True,editable=True)
    Units=models.SmallIntegerField(_('Cycle unit'),null=True, default=1,blank=True,editable=True, choices=CYCLE_UNITS)
    Num_RunOfDept=models.IntegerField(_(u'归属单位'),null=True,blank=True, default=0,editable=True)
    DelTag = models.IntegerField(_(u'注销标记'),default=0, editable=False, null=True, blank=True)

    def __unicode__(self):
        return unicode(u"%s"%(self.Name))

    @staticmethod
    def objByID(id):
        if id==None: return None
        d=cache.get("%s_iclock_num_run_%s"%(settings.UNIT,id))
        if d: return d
        try:
            d=NUM_RUN.objects.get(Num_runID=id)
        except:
            d=None
        if d:
            cache.set("%s_iclock_num_run_%s"%(settings.UNIT,id),d)
        return d


    @staticmethod
    def colModels():
        return [
            {'name':'Num_runID','hidden':True},
            {'name':'Name','width':140,'label':unicode(NUM_RUN._meta.get_field('Name').verbose_name)},
            {'name':'StartDate','width':120,'label':unicode(NUM_RUN._meta.get_field('StartDate').verbose_name)},
            {'name':'EndDate','width':120,'label':unicode(NUM_RUN._meta.get_field('EndDate').verbose_name)},
            {'name':'Cycle','width':80,'label':unicode(NUM_RUN._meta.get_field('Cycle').verbose_name)},
            {'name':'Units','width':80,'label':unicode(NUM_RUN._meta.get_field('Units').verbose_name)},
            {'name':'Num_RunOfDept','sortable':False,'width':120,'label':unicode(SchClass._meta.get_field('TimeZoneOfDept').verbose_name)},
            {'name':'shift_detail','sortable':False,'width':100,'label':unicode(_('operation'))},
            {'name':'h_unit','hidden':True}

            ]
    class Admin:
        search_fields = ['Name']
    class Meta:
        db_table = 'NUM_RUN'
        verbose_name=_('shift')
        verbose_name_plural=verbose_name
        permissions = (
                    ('addShiftTimeTable_num_run','Add time-table'),
                    ('deleteAllShiftTimeTbl_num_run','Delete time-table'),
        )
    def Dept(self): #cached employee
        d=department.objByID(self.Num_RunOfDept)
        if d:return d
        else:return _(u'所有部门')

    def save(self):
        super(NUM_RUN,self).save()
        try:
            cache.delete("%s_iclock_num_run_%s"%(settings.UNIT,self.Num_runID))
        except:
            pass
        return self


    ##管理员权限设置表##
class SECURITYDETAILS(models.Model):
    SecuritydetailID=models.AutoField(primary_key=True,null=False, editable=False)
    UserID=models.SmallIntegerField(null=True,blank=True)
    DeptID=models.SmallIntegerField(null=True,blank=True)
    Schedule=models.SmallIntegerField(null=True,blank=True)
    UserInfo=models.SmallIntegerField(null=True,blank=True)
    EnrollFingers=models.SmallIntegerField(null=True,blank=True)
    ReportView=models.SmallIntegerField(null=True,blank=True)
    Report=models.CharField(max_length=10,null=True)
    class Admin:
        pass
    class Meta:
        db_table = 'SECURITYDETAILS'



 ##轮班表##
class SHIFT(models.Model):
    ShiftID=models.AutoField(primary_key=True,null=False, editable=False)
    Name=models.CharField(_('Sch name'),max_length=20,null=True)
    UshiftID=models.IntegerField(null=True,default=-1,blank=True,editable=False)
    StartDate = models.DateField(_('Beginning date'),null=False,default='1900-1-1', blank=True)
    EndDate = models.DateField(_('Ending date'),null=True,default='1900-12-31', blank=True)   #日期型
    RunNum=models.SmallIntegerField(_('Run number'),null=True,default=1,blank=True)         #日期型
    SCH1=models.IntegerField(_('SCH1'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH2=models.IntegerField(_('SCH2'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH3=models.IntegerField(_('SCH3'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH4=models.IntegerField(_('SCH4'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH5=models.IntegerField(_('SCH5'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH6=models.IntegerField(_('SCH6'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH7=models.IntegerField(_('SCH7'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH8=models.IntegerField(_('SCH8'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH9=models.IntegerField(_('SCH9'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH10=models.IntegerField(_('SCH10'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH11=models.IntegerField(_('SCH11'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    SCH12=models.IntegerField(_('SCH12'), editable=False,null=True,default=0,blank=True,choices=BOOLEANS)
    Cycle=models.SmallIntegerField( _('Shift Cycle'),null=True,default=0,blank=True)
    UnitS=models.SmallIntegerField(_('Cycle unit'),null=True,default=0,blank=True,choices=CYCLE_UNITS)
    class Admin:
        pass
    class Meta:
        db_table = 'SHIFT'
        verbose_name = _('Scheduled shift')
        verbose_name_plural=verbose_name

    ##员工排班表##
class USER_OF_RUN(models.Model):
    UserID=models.ForeignKey(employee, verbose_name=_("employee"), db_column='UserID', null=False, blank=False)
    StartDate = models.DateField(_('Beginning date'),null=False, blank=True)
    EndDate = models.DateField(_('Ending date'),null=False,default='2099-12-31', blank=True)
    NUM_OF_RUN_ID=models.ForeignKey(NUM_RUN, verbose_name=_('Shift'), db_column='NUM_OF_RUN_ID', null=False, blank=False)
    ISNOTOF_RUN=models.IntegerField(null=True,default=0,blank=True ,editable=False)
    ORDER_RUN=models.IntegerField(null=True,blank=True,editable=False)
    datest=models.DateTimeField(_(u'datest'), db_column='datest', null=True)
#	def save(self):
#		self.EndDate=datetime.datetime(self.EndDate.year,self.EndDate.month,self.EndDate.day,23,59,59)
#		return models.Model.save(self)
    def get_all_Shift_Name(self):
        datas = NUM_RUN.objects.all()
        s = []
        for row in datas:
            s.append (row["Name"])
        return s
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'DeptNumber','index':'UserID__DeptID__DeptNumber','width':100,'label':unicode(_(u'部门编号'))},
            {'name':'DeptName','index':'UserID__PIN','sortable':False,'width':140,'label':unicode(_('department name'))},
            {'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'Workcode', 'index':'UserID__Workcode', 'width':100, 'label':unicode(_('NewPin'))},
            {'name':'EName','sortable':False,'width':80,'label':unicode(_('EName'))},
            {'name':'StartDate','sortable':False,'index':'StartSpecDay','width':120,'label':unicode(USER_OF_RUN._meta.get_field('StartDate').verbose_name)},
            {'name':'EndDate','sortable':False,'index':'EndSpecDay','width':120,'label':unicode(USER_OF_RUN._meta.get_field('EndDate').verbose_name)},
            {'name':'NUM_OF_RUN_ID','sortable':False,'width':140,'label':unicode(_('Sch name'))}
            ]


    class Admin:
        list_filter = ['UserID','NUM_OF_RUN_ID','StartDate','EndDate']
        search_fields = ['UserID__PIN','UserID__EName','UserID__Workcode']

    class Meta:
        db_table = 'USER_OF_RUN'
        verbose_name = _('empoyee shift')
        verbose_name_plural=verbose_name
        unique_together = (("UserID","NUM_OF_RUN_ID", "StartDate","EndDate"),)
        permissions=(

                   ('Employee_shift_details','Employee shift details'),



        )




    ##员工考勤例外（请假/公出）表##
class USER_SPEDAY(models.Model):
    #id=models.AutoField(primary_key=True,null=False, editable=False)
    UserID=models.ForeignKey(employee, db_column='UserID',verbose_name=_('employee'), default=1,null=False, blank=False)
    StartSpecDay= models.DateTimeField(_('beginning time'), null=False, blank=True)
    EndSpecDay = models.DateTimeField(_('ending time'), null=True, blank=True)
    DateID=models.IntegerField(_('Leave Class'),db_column='DateID', null=False,default=-1,blank=True, editable=True)
    YUANYING=models.CharField(_('reson'), max_length=200,null=True,blank=True)
    ApplyDate=models.DateTimeField(_('apply date'), null=True,  blank=True)
    State=models.SmallIntegerField(_('state'), null=True, default=0, blank=True, choices=AUDIT_STATES, editable=False)
    jiezhuang=models.SmallIntegerField(_(u'是否结转'), null=True, default=0, blank=True, choices=JIEZHUANG_STATES, editable=False)
    tianshu=models.IntegerField(_(u'结转天数'),null=True,default=0,blank=True, editable=True)
    jiezhuangDay= models.DateTimeField(_('jiezhuang time'), null=True, blank=True)
    jieYUANYING=models.CharField(_(u'结转原因'), max_length=200,null=True,blank=True)
    clearance=models.IntegerField(_('Leave clearance'),db_column='clearance', null=True,default=0,blank=True, editable=True)   #是否自动销假
    roleid = models.IntegerField(_(u'当前审核人'),editable=True)
    process=models.CharField(_(u'审核流程'),max_length=80,null=True,blank=True)
    oldprocess=models.CharField(_(u'审核过的流程'),max_length=80,null=True,blank=True)
    processid=models.IntegerField(_(u'审核流程id'),editable=True)
    procSN=models.IntegerField(_(u'已审序号'),default=0,editable=True)
#	operator = models.CharField(_(u'操作'), max_length=20, null=True, blank=True, editable=False)

    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None

    def USER_SPEDAY_DETAILS(self):
        try:
            return USER_SPEDAY_DETAILS.objByID(self.id)
        except:
            return None
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True,'frozen':True},
            {'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN')),'frozen':True},
            {'name':'Workcode', 'index':'UserID__Workcode', 'width':120, 'label':unicode(_('NewPin')), 'frozen':True},
            {'name':'EName','index':'UserID__EName','width':80,'label':unicode(_('EName')),'frozen':True},
            {'name':'StartSpecDay','index':'StartSpecDay','width':120,'label':unicode(USER_SPEDAY._meta.get_field('StartSpecDay').verbose_name)},
            {'name':'EndSpecDay','index':'EndSpecDay','width':120,'label':unicode(USER_SPEDAY._meta.get_field('EndSpecDay').verbose_name)},
            {'name':'DateID','width':80,'label':unicode(USER_SPEDAY._meta.get_field('DateID').verbose_name)},
            {'name':'bstate','sortable':False,'width':80,'label':unicode(_(u'借调状态'))},
            {'name':'DeptID','sortable':False,'width':85,'label':unicode(_(u'借调单位编号'))},
            {'name':'DeptName','sortable':False,'width':120,'label':unicode(_(u'借调单位'))},
            {'name':'Title','sortable':False,'width':60,'label':unicode(_(u'借调职位'))},
            {'name':'State','index':'State','width':80,'label':unicode(USER_SPEDAY._meta.get_field('State').verbose_name)},
            {'name':'process','sortable':False,'index':'process','width':220,'label':unicode(_(u'审核流程'))},
            {'name':'operate','sortable':False,'width':50,'label':unicode(_(u'操作'))},
            {'name':'YUANYING','sortable':False,'width':120,'label':unicode(USER_SPEDAY._meta.get_field('YUANYING').verbose_name)},
            {'name':'Place','sortable':False,'index':'Place','width':120,'label':unicode(_(u'外出地点'))},
            {'name':'mobile','sortable':False,'index':'mobile','width':120,'label':unicode(_(u'联系电话'))},
            {'name':'successor','sortable':False,'width':120,'label':unicode(_(u'工作承接人'))},
            {'name':'file','sortable':False,'width':80,'label':unicode(_(u'附件'))},
            {'name':'remarks','sortable':False,'width':120,'label':unicode(_(u'备注'))},
            {'name':'ApplyDate','index':'ApplyDate','width':120,'label':unicode(USER_SPEDAY._meta.get_field('ApplyDate').verbose_name)},
            {'name':'empid','sortable':False,'width':80,'label':unicode(_('Annual leave'))},
            {'name':'empids','sortable':False,'width':80,'label':unicode(_('Used Annual leave'))},
            {'name':'jiezhuang','width':80,'label':unicode(USER_SPEDAY._meta.get_field('jiezhuang').verbose_name)},
            {'name':'tianshu','width':80,'label':unicode(_(u'结转天数'))},
            {'name':'jiezhuangDay','width':120,'label':unicode(_(u'结转时间'))},
            {'name':'jieYUANYING','width':120,'label':unicode(_(u'结转原因'))}
            ]
    class Admin:
        list_filter =['State','UserID','StartSpecDay','DateID','ApplyDate']
        lock_fields=['UserID']
        search_fields = ['UserID__PIN','UserID__EName','UserID__Workcode','jiezhuang']
    class Meta:
        db_table = 'USER_SPEDAY'
        verbose_name = _('special leave')
        verbose_name_plural=verbose_name
        unique_together = (("UserID", "StartSpecDay","DateID"),)
        permissions = (
                        ('leaveAudit_user_speday','Audit Sepcial Leave'),
                        ('definedReport_user_speday','user-defined report'),
                        ('setprocess','setprocess'),


            )

class USER_SPEDAY_DETAILS(models.Model):
    USER_SPEDAY_ID = models.ForeignKey(USER_SPEDAY,db_column='USER_SPEDAY_ID',default=1,null=False,blank=False)
    Place = models.CharField(_(u'外出地点'),db_column="Place",max_length=120, null=True, blank=True)
    mobile = models.CharField(_(u'联系电话'),db_column="mobile",max_length=20, null=True, blank=True)
    successor = models.CharField(_(u'工作承接人'),db_column="successor",null=True,max_length=40, blank=True, default="")
    remarks=models.CharField(_(u'备注'),max_length=200,null=True,blank=True)
    file=models.CharField(_(u'附件'),max_length=200,null=True,blank=True,default="")
    @staticmethod
    def objByID(id):
        if id==None: return None
        try:
            d=USER_SPEDAY_DETAILS.objects.get(USER_SPEDAY_ID=id)
        except:
            d=None
        return d

class USER_SPEDAY_PROCESS(models.Model):
    USER_SPEDAY_ID = models.ForeignKey(USER_SPEDAY,db_column='USER_SPEDAY_ID',default=1,null=False,blank=False)
    User = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('administrator'), null=True, blank=True)
    comments=models.CharField(_(u'审批意见'),max_length=400,null=True,blank=True)
    ProcessingTime = models.DateTimeField(_(u'审批时间'), null=True, blank=True)
    procSN = models.IntegerField(_(u'审批级别'),db_column='procSN', null=True,blank=True, editable=True)
    State=models.SmallIntegerField(_('state'), null=True, default=0, blank=True, choices=AUDIT_STATES_PROCESS, editable=False)

CONTRACT_STATES=(
    (0, _(u'是')),
    (1, _(u'否')),
)
CONTRACT_TYPE=(
    (0, _(u'合同工')),
    (1, _(u'试用')),
)

    ##用户合同
class USER_CONTRACT(models.Model):
    id=models.AutoField(primary_key=True,null=False, editable=False)
    UserID=models.ForeignKey(employee, db_column='UserID',verbose_name=_('employee'), default=1,null=False, blank=False)
    StartContractDay= models.DateField(_('beginning time'), null=False, blank=True)
    EndContractDay = models.DateField(_('ending time'), null=True, blank=True)
    Notes=models.TextField(_('Notes'), max_length=200,null=True,blank=True)
    ApplyDate=models.DateTimeField(_(u'申请时间'),  null=True,  blank=True)
    State=models.SmallIntegerField(_(u'合同状态'), null=True, default=0, blank=True, choices=CONTRACT_STATES, editable=True)
    Type=models.SmallIntegerField(_(u'类型'), null=True, default=0, blank=True, choices=CONTRACT_TYPE, editable=True)
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'PIN','index':'UserID__PIN','width':80,'label':unicode(_('PIN'))},
            {'name':'EName','index':'UserID__EName','width':80,'label':unicode(_('EName'))},
            {'name':'StartContractDay','index':'StartContractDay','width':120,'label':unicode(USER_CONTRACT._meta.get_field('StartContractDay').verbose_name)},
            {'name':'EndContractDay','index':'EndContractDay','width':120,'label':unicode(USER_CONTRACT._meta.get_field('EndContractDay').verbose_name)},
            {'name':'DeptID','index':'UserID__DeptID','width':60,'label':unicode(_('department number'))},
            {'name':'DeptName','index':'UserID__DeptID__DeptName','width':120,'label':unicode(_('department name'))},
            {'name':'State','index':'State','width':80,'label':unicode(USER_CONTRACT._meta.get_field('State').verbose_name)},
            {'name':'Notes','sortable':False,'width':120,'label':unicode(USER_CONTRACT._meta.get_field('Notes').verbose_name)},
            #{'name':'ApplyDate','index':'ApplyDate','width':120,'label':unicode(USER_CONTRACT._meta.get_field('ApplyDate').verbose_name)},
            {'name':'Type','index':'Type','width':80,'label':unicode(USER_CONTRACT._meta.get_field('Type').verbose_name)}
            ]
    class Admin:
        list_filter =['State','UserID','StartContractDay','ApplyDate']
        lock_fields=['UserID']
        search_fields = ['UserID__PIN','UserID__EName']
    class Meta:
        db_table = 'USER_CONTRACT'
        verbose_name = _('USER_CONTRACT')
        verbose_name_plural=verbose_name
        unique_together = (("UserID", "StartContractDay"),)
#		permissions = (
#						('leaveAudit_user_speday','Audit Sepcial Leave'),
#			)


    ##员工临时排班表##
class USER_TEMP_SCH(models.Model):
    UserID=models.ForeignKey(employee,db_column='UserID',verbose_name=_('employee'), default=1,null=False, blank=False)
    ComeTime = models.DateTimeField(_('Beginning time'),null=False, blank=False)
    LeaveTime = models.DateTimeField(_('Ending time'),null=False, blank=False)
    OverTime = models.IntegerField(_('Over time'),null=False,default=0,blank=True)
    Type=models.SmallIntegerField(_('Type'),null=True,default=0,blank=True)
    Flag=models.SmallIntegerField(null=True,default=1,blank=True,editable=False)
    SchclassID=models.IntegerField(null=True,default=1,db_column='SchClassID',blank=True,editable=False)
#	SchclassID=models.ForeignKey("SchClass",db_column='SchclassID',verbose_name=_('shift time-table'),null=False,default=-1,blank=True)
    def get_all_Sch_Name(self):
        datas = SchClass.objects.all()
        sch = []
        for row in datas:
            sch.append(row["SchName"])
        return sch
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'DeptName','index':'UserID__DeptID','width':120,'label':unicode(_('department name'))},
            {'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'Workcode', 'index':'UserID__Workcode', 'width':100, 'label':unicode(_('NewPin'))},
            {'name':'EName','sortable':False,'width':80,'label':unicode(_('EName'))},
            {'name':'ComeTime','index':'ComeTime','width':120,'label':unicode(USER_TEMP_SCH._meta.get_field('ComeTime').verbose_name)},
            {'name':'LeaveTime','index':'LeaveTime','width':120,'label':unicode(USER_TEMP_SCH._meta.get_field('LeaveTime').verbose_name)},
            {'name':'SchclassID','sortable':False,'width':80,'label':unicode(_('time-table name'))}
            ]

    class Admin:
        list_filter = ('UserID','SchclassID','LeaveTime','ComeTime','OverTime')
        search_fields = ['UserID__PIN','UserID__EName','UserID__Workcode','SchclassID']
    class Meta:
        db_table = 'USER_TEMP_SCH'
        verbose_name=_('temporary schedule')
        verbose_name_plural=verbose_name
        unique_together = (("UserID","ComeTime", "LeaveTime"),)
        permissions=(

                   ('Data_Management','Data Management'),#数据管理
                   ('Init_database','Init database'),#初始化系统
                   ('Clear_Obsolete_Data','Clear Obsolete Data'),#清除过期数据
                   ('Backup_Database','Backup Database'),#备份数据库
                   ('import_department_data','import department data'),#导入部门数据
                   ('import_employee_data','import employee data'),#导入人员数据
                   ('Import_Finger_data','Import Finger data'),#导入指纹数据
                   ('U_Disk_Data_Manager','U_Disk Data Manager'),#U盘数据管理
                   ('Database_Options','Database Options'),#数据库设置
                   ('System_Options','System Options'),#系统设置
                   ('preferences_user','user-Preferences'),#自定义显示字段
                   ('setprocess','set process'),
                   ('user_temp_sch_add','add user_temp_sch'),#系统选项的增加
                   ('user_temp_sch_modify','modify user_temp_sch'),#系统选项的修改
                   ('user_temp_sch_delete','delete user_temp_sch'),#系统选项删除

        )

LEAVE_UNITS=(
    (1, _('Hour')),
    (2, _('Minute')),
    (3, _('Workday')),
    (4, _('')),
)
LEAVETYPE=(
    (1, _('Sick Leave')),
    (2, _('Private Affair Leave')),
    (3, _('Home Leave')),
    (4, _('Maternity Leave')),
    (5, _('Annual leave')),
)

    ##假类表##
class LeaveClass(models.Model):
    LeaveID=models.AutoField(_('Leave ID'),primary_key=True,null=False, editable=False)
    LeaveName=models.CharField(_('Leave Class name'),max_length=20,null=False)
    MinUnit=models.FloatField(_('Min.unit'),null=False,default=1,blank=True)
    Unit=models.SmallIntegerField(_('Unit'),null=False,default=1,blank=True,choices=LEAVE_UNITS)
    RemaindProc=models.SmallIntegerField(_('Round at Acc.'),null=False,default=1,blank=True,choices=BOOLEANS)
    RemaindCount=models.SmallIntegerField(_('Acc. by times'),null=False,default=1,blank=True,choices=BOOLEANS)
    ReportSymbol=models.CharField(_('Symbol in report'),max_length=4,null=False,default='-')
    Deduct=models.FloatField(_('Min. unit deduction'),null=True,default=0,blank=True,editable=False)
    Classify=models.SmallIntegerField(null=False,default=0,blank=True,editable=False)
    clearance=models.IntegerField(_('Leave clearance'),db_column='clearance', null=True,default=0,blank=True, editable=True)   #是否自动销假
    LeaveType=models.IntegerField(_('Leave Class Type'), null=True,default=0,blank=True, editable=True,choices=LEAVETYPE) #0 未知  1 病假 2事假 3产假 4探亲假 5年假
    Color=models.IntegerField(_('display color'),null=True,default=16715535,blank=True,editable=True)
    DelTag = models.IntegerField(default=0, editable=False, null=True, blank=True)
    def __unicode__(self):
        return u"%s"%self.LeaveName
    def save(self):
        if LeaveClass.objects.filter(LeaveName=self.LeaveName,DelTag=0).count()>0:
            raise Exception(u'假类名称重复')
        elif LeaveClass.objects.filter(ReportSymbol=self.ReportSymbol,DelTag=0).count()>0:
            raise Exception(u'报表符号重复')
        elif LeaveClass.objects.filter(LeaveName=self.LeaveName,DelTag=1).count()>0:
            leave = LeaveClass.objects.filter(LeaveName=self.LeaveName,DelTag=1)
            self.LeaveID = leave[0].LeaveID
        super(LeaveClass,self).save()
    class Admin:
        @staticmethod
        def initial_data():
            if LeaveClass.objects.all().count()==0:
                LeaveClass(LeaveName=u'公出',MinUnit=0.5,Unit=3,RemaindProc=1,RemaindCount=1,ReportSymbol='G',Classify=128,DelTag=0).save()
                LeaveClass(LeaveName=u'病假',Unit=1,ReportSymbol='B',Color=3398744,DelTag=0).save()
                LeaveClass(LeaveName=u'事假',Unit=1,ReportSymbol='S',Color=8421631,DelTag=0).save()
                LeaveClass(LeaveName=u'探亲假',Unit=1,ReportSymbol='T',Color=16744576,DelTag=0).save()
                LeaveClass(LeaveName=u'带薪年假',Unit=1,ReportSymbol='N',Color=16715535,LeaveType=5,DelTag=0).save()

    class Meta:
        db_table = 'LeaveClass'
        verbose_name=_('Leave Class')
        verbose_name_plural=verbose_name


    ##统计项目表##
class LeaveClass1(models.Model):
    LeaveID=models.IntegerField(primary_key=True,null=False, editable=False)
    LeaveName=models.CharField(_('Leave Class name'),max_length=20,null=False)
    MinUnit=models.FloatField(_('Min.unit'),null=False,default=1,blank=True)
    Unit=models.SmallIntegerField(_('Unit'),null=False,default=0,blank=True,choices=LEAVE_UNITS)
    RemaindProc=models.SmallIntegerField(_('Round at Acc.'),null=False,default=1,blank=True,choices=BOOLEANS)
    RemaindCount=models.SmallIntegerField(_('Acc. by times'),null=False,default=1,blank=True,choices=BOOLEANS)
    ReportSymbol=models.CharField(_('Symbol in report'),max_length=4,null=False,default='_')
    Deduct=models.FloatField(_('Min. unit deduction'),null=False,default=0,blank=True)
    Color=models.IntegerField(_('display color'),null=False,default=0,blank=True,editable=False)
    Classify=models.SmallIntegerField(null=False,default=0,blank=True,editable=False)
    LeaveType=models.SmallIntegerField(_('Leave Class Type'),null=False,default=0,blank=True)
#	Calc = models.TextField(max_length=2048,null=True,editable=False)
    class Admin:
        @staticmethod
        def initial_data():

            if LeaveClass1.objects.all().count()==0:
                """ 将公出999从leaveclass1中移走,归到假类设置中"""
        #		LeaveClass1(LeaveID=999,LeaveName="%s"%'BL',MinUnit=0.5,Unit=3,RemaindProc=1,RemaindCount=1,ReportSymbol='G',LeaveType="3",Calc='if(AttItem(LeaveType1)=999,AttItem(LeaveTime1),0)+if(AttItem(LeaveType2)=999,AttItem(LeaveTime2),0)+if(AttItem(LeaveType3)=999,AttItem(LeaveTime3),0)+if(AttItem(LeaveType4)=999,AttItem(LeaveTime4),0)+if(AttItem(LeaveType5)=999,AttItem(LeaveTime5),0)').save()
                LeaveClass1(LeaveID=1000,LeaveName="%s"%'OK',MinUnit=0.5,Unit=1,RemaindProc=1,RemaindCount=0,ReportSymbol='/',LeaveType="3").save()
                LeaveClass1(LeaveID=1001,LeaveName="%s"%'Late',MinUnit=10,Unit=2,RemaindProc=2,RemaindCount=1,ReportSymbol='>',LeaveType="3").save()
                LeaveClass1(LeaveID=1002,LeaveName="%s"%'Early',MinUnit=10,Unit=2,RemaindProc="2",RemaindCount="1",ReportSymbol='<',LeaveType="3").save()
                LeaveClass1(LeaveID=1003,LeaveName="%s"%'ALF',MinUnit="1",Unit="1",RemaindProc="1",RemaindCount="1",ReportSymbol='V',LeaveType="3").save()
                LeaveClass1(LeaveID=1004,LeaveName="%s"%'Absent',MinUnit="0.5",Unit="3",RemaindProc="1",RemaindCount="0",ReportSymbol='A',LeaveType="3").save()
                LeaveClass1(LeaveID=1005,LeaveName="%s"%'OT',MinUnit="1",Unit="1",RemaindProc="1",RemaindCount="1",ReportSymbol='+',LeaveType="3").save()
                LeaveClass1(LeaveID=1006,LeaveName="%s"%'OTH',MinUnit="1",Unit="1",RemaindProc="0",RemaindCount="1",ReportSymbol='=',LeaveType="0").save()
                LeaveClass1(LeaveID=1007,LeaveName="%s"%'Hol.',MinUnit="0.5",Unit="3",RemaindProc="2",RemaindCount="1",ReportSymbol='-',LeaveType="2").save()
                LeaveClass1(LeaveID=1008,LeaveName="%s"%'NoIn',MinUnit="1",Unit="4",RemaindProc="2",RemaindCount="1",ReportSymbol='[',LeaveType="2").save()
                LeaveClass1(LeaveID=1009,LeaveName="%s"%'NoOut',MinUnit="1",Unit="4",RemaindProc="2",RemaindCount="1",ReportSymbol=']',LeaveType="2").save()
                LeaveClass1(LeaveID=1010,LeaveName="%s"%'ROT',MinUnit="1",Unit="4",RemaindProc="2",RemaindCount="1",ReportSymbol='{',LeaveType="3").save()
                LeaveClass1(LeaveID=1011,LeaveName="%s"%'BOUT',MinUnit="1",Unit="4",RemaindProc="2",RemaindCount="1",ReportSymbol='}',LeaveType="3").save()
                LeaveClass1(LeaveID=1012,LeaveName="%s"%'OUT',MinUnit="1",Unit="1",RemaindProc="2",RemaindCount="1",ReportSymbol='L',LeaveType="3").save()
                LeaveClass1(LeaveID=1013,LeaveName="%s"%'FOT',MinUnit="1",Unit="1",RemaindProc="2",RemaindCount="1",ReportSymbol='F',LeaveType="3").save()



    class Meta:
        db_table = 'LeaveClass1'
        verbose_name=_('report item')
        verbose_name_plural=verbose_name



ENDTIME_DAYS=(
    (1, _(u'同一天')),
    (2, _(u'第二天')),
)

    ##班次时段类别设置表##
class SchClass(models.Model):
    SchclassID=models.AutoField(primary_key=True,null=False, editable=False)
    SchName=models.CharField(_('time-table name'), max_length=20,null=False)
    StartTime = models.TimeField(_('on duty time'),null=False, blank=False)
    EndTime = models.TimeField(_('off duty time'),null=False, blank=False)
    LateMinutes=models.IntegerField(_(u'允许迟到'),null=True,blank=True, default=0,help_text=_(u'分钟(默认0)'))
    EarlyMinutes=models.IntegerField(_(u'允许早退'),null=True,blank=True, default=0,help_text=_(u'分钟(默认0)'))
    CheckIn = models.SmallIntegerField(_('must C/In'),null=True,default=1,blank=True,choices=BOOLEANS)
    CheckOut = models.SmallIntegerField(_('must C/Out'),null=True,default=1,blank=True,choices=BOOLEANS)
    CheckInTime1 = models.TimeField(_('beginning in'),null=True, blank=True,editable=False)
    CheckInTime2 = models.TimeField(_('ending in'),null=True, blank=True,editable=False)
    CheckOutTime1 = models.TimeField(_('begin out'),null=True, blank=True,editable=False)
    CheckOutTime2 = models.TimeField(_('end out'),null=True, blank=True,editable=False)
    Color=models.IntegerField(_('display color'),null=True,default=16715535,blank=True,editable=True)
    AutoBind=models.SmallIntegerField(null=True,default=1,blank=True,choices=BOOLEANS,editable=False)
    WorkDay=models.FloatField(_(u'折算工作日'), null=False, default=1, blank=True,help_text=_(u'单位:天'))
    IsCalcRest=models.NullBooleanField(_(u'扣除休息'),null=True,default=0,  blank=True,editable=True) #是否扣减休息时间
    StartRestTime = models.TimeField(_('beginning Rest'),null=True, blank=True,editable=True)             #暂时不编辑,
    EndRestTime = models.TimeField(_('ending rest'),null=True, blank=True,editable=True)                  #暂时不编辑
    StartRestTime1 = models.TimeField(_('beginning Rest2'),null=True, blank=True,editable=True)             #暂时不编辑,
    EndRestTime1= models.TimeField(_('ending rest2'),null=True, blank=True,editable=True)                  #暂时不编辑
    CheckInMins1=models.IntegerField(_(u'上班前'),null=True,blank=True, default=120,help_text=_(u'分钟内签到有效(默认120分钟)'))
    CheckInMins2=models.IntegerField(_(u'上班后'),null=True,blank=True, default=120,help_text=_(u'分钟内签到有效(默认120分钟)'))
    CheckOutMins1=models.IntegerField(_(u'下班前'),null=True,blank=True, default=120,help_text=_(u'分钟内签退有效(默认120分钟)'))
    CheckOutMins2=models.IntegerField(_(u'下班后'),null=True,blank=True, default=120,help_text=_(u'分钟内签退有效(默认120分钟)'))
#	RestMins=models.IntegerField(_(u'扣除休息时间(分钟)'),null=True,blank=True, default=0,help_text=_(u'如不填写按下面的设置计算'))
    TimeZoneType=models.IntegerField(_(u'弹性上班'),null=True,default=0,  blank=True,editable=True,choices=BOOLEANS) #暂时不编辑,是否扣减休息时间
    WorkTimeType=models.IntegerField(_(u'工时计算类型'),null=True,default=0,  blank=True,editable=False) #暂时不编辑

    BeforeInMins=models.IntegerField(_(u'可提前上班'),null=True,blank=True, default=120,help_text=_(u'分(默认120分钟)'))
    AfterInMins=models.IntegerField(_(u'可延后上班'),null=True,blank=True, default=120,help_text=_(u'分(默认120分钟)'))
    IsCalcOverTime=models.IntegerField(_(u'班后记加班'),null=True,default=0,  blank=True,editable=True)
    OverTimeMins=models.IntegerField(_(u'下班'),null=True,blank=True, default=60,help_text=_(u'分钟后记加班'))
    IsCalcComeOverTime=models.IntegerField(_(u'班前记加班'),null=True,default=0,  blank=True,editable=True)
    ComeOverTimeMins=models.IntegerField(_(u'上班'),null=True,blank=True, default=60,help_text=_(u'分钟前记加班'))
    NextDay=models.IntegerField(_(u'第几天'),null=True,blank=True, default=1,choices=ENDTIME_DAYS,help_text=_(u'默认同一天'))
    TimeZoneOfDept=models.IntegerField(_(u'归属单位'),null=True,blank=True, default=0,editable=True,help_text=_(u'不建议使用单位的下级单位,非大型或连锁单位忽略此项,仅限超级管理员配置此项'))
    isHidden=models.IntegerField(_(u'是否隐藏'),null=True,blank=True, default=0,editable=True)  #由于时段不能删除，此字段可用于隐藏
#	TimeZoneMins=models.IntegerField(_(u'时长(分)'),null=True,blank=True, default=0,editable=False)
    DelTag = models.IntegerField(_(u'注销标记'),default=0, editable=False, null=True, blank=True)
    Holiday=models.NullBooleanField(_('Rest on Holidays'),null=True,default=True, blank=True,editable=True,help_text=_(u'临时排班不受此控制'))





    def __unicode__(self):
        return unicode(u"%s"%(self.SchName))

    def save(self):
        cache.delete("%s_schclasses"%(settings.UNIT))
        if self.SchclassID:
            cache.delete("%s_iclock_schclass_%s"%(settings.UNIT,self.SchclassID))

        super(SchClass,self).save()

    def Dept(self): #cached employee
        d=department.objByID(self.TimeZoneOfDept)
        if d:return d
        else:return _(u'所有部门')

    @staticmethod
    def objByID(id):
        sch=cache.get("%s_iclock_schclass_%s"%(settings.UNIT, id))
        if sch: return sch
        try:
            schClasses=SchClass.GetSchClasses(id)
        except Exception,e:
            print "schclass=",id,e
            schClasses=[]
        e={}
        if schClasses:
            e=schClasses[0]
            cache.set("%s_iclock_schclass_%s"%(settings.UNIT,id),e)
        return e



    @staticmethod
    def FindSchClassByID(SchId):

        #sch=SchClass.GetSchClasses()
        #for i in range(len( sch)):
        #	if sch[i]['schClassID']==SchId:
        #		return i
        #return -1
        return SchClass.objByID(SchId)
    def GetTimeZoneMins(self):
        schid=self.SchclassID
        #try:
        #	j=self.FindSchClassByID(schid)
        #except Exception,e:
        #	print "99999",e
        #if j==-1:return 0
        #sch=self.GetSchClasses()[j]
        sch=SchClass.FindSchClassByID(schid)
        r=sch['TimeZoneMins']
        if sch['IsCalcRest']:
            r=r-sch['RestMins']
        return r

    @staticmethod
    def GetSchClasses(schID=None,User=None):
        #AttRule=AttParam.LoadAttRule()
        if not schID:
            #sch=cache.get("%s_schclasses"%(settings.UNIT))
            #if sch:	return sch
            if User and (not User.is_superuser) and (User.AutheTimeDept):
                schClass=SchClass.objects.filter(TimeZoneOfDept=User.AutheTimeDept).exclude(DelTag=1).order_by('-SchclassID')
            else:
                schClass=SchClass.objects.all().exclude(DelTag=1).order_by('-SchclassID')

        else:
            schClass=SchClass.objects.filter(SchclassID=schID)
        ss={}
        re=[]
        for sch in schClass:
            sch.StartTime=checkTime(sch.StartTime)
            sch.EndTime=checkTime(sch.EndTime)
            if sch.CheckInTime1!=None:
                sch.CheckInTime1=checkTime(sch.CheckInTime1)
            if sch.CheckInTime2!=None:
                sch.CheckInTime2=checkTime(sch.CheckInTime2)
            if sch.CheckOutTime1!=None:
                sch.CheckOutTime1=checkTime(sch.CheckOutTime1)
            if sch.CheckOutTime2!=None:
                sch.CheckOutTime2=checkTime(sch.CheckOutTime2)

            ss={'TimeZone':{'StartTime':sch.StartTime,'EndTime':sch.EndTime},
                'schClassID':sch.SchclassID,
                'SchName':sch.SchName,
                'MustClockIn':0,
                'MustClockOut':0,
                'MinsLate':sch.LateMinutes,
                'MinsEarly':sch.EarlyMinutes,
                'Color':16715535,
                'WorkDay':1,#折算工作日
                'WorkMins':0,               #sch.WorkMins,\                          #not used
                'OverTime':0,
                'Intime':{'StartTime':0,'EndTime':0},
                'Outtime':{'StartTime':0,'EndTime':0},
                'SchID':sch.SchclassID,
                'IsCalcRest':0,
                'StartRestTime':checkTime(datetime.time(0,0,0)),
                'EndRestTime':checkTime(datetime.time(0,0,0,)),
                'StartRestTime1':checkTime(datetime.time(0,0,0)),
                'EndRestTime1':checkTime(datetime.time(0,0,0,)),
                'RestTime':0,
                'TimeZoneType':0,
                'BeforeInMins':120,
                'AfterInMins':120,
                'IsCalcOverTime':0,
                'OverTimeMins':60,
                'IsCalcComeOverTime':0,
                'ComeOverTimeMins':60,
                #'NextDay':1,
                'TimeZoneOfDept':0,
                'NextDay':0,   #与数据库的数据差1
                'TimeZoneMins':0,
                'RestMins':0,
                'TimeZoneOfDept':0,
            'Holiday':sch.Holiday


            }

            if sch.CheckIn==1:
                ss['MustClockIn']=1
            if sch.CheckOut==1:
                ss['MustClockOut']=1

            #if sch.LateMinutes!=None:	#以时段为准
            #	ss['MinsLate']=sch.LateMinutes
            #else:
            #	ss['MinsLate']=AttRule['MinsLate']
            #if sch.EarlyMinutes!=None:
            #	ss['MinsEarly']=sch.EarlyMinutes
            #else:
            #	ss['MinsEarly']=AttRule['MinsEarly']

            if sch.Color!=None:
                ss['Color']=sch.Color


            try:
                if sch.IsCalcRest!=None:
                    ss['IsCalcRest']=sch.IsCalcRest

                if ss['IsCalcRest']==1:
                    if sch.StartRestTime!=None:                              #add 2009.08.05
                        sch.StartRestTime=checkTime(sch.StartRestTime)
                        ss['StartRestTime']=sch.StartRestTime
                    if sch.EndRestTime!=None:
                        sch.EndRestTime=checkTime(sch.EndRestTime)

                        ss['EndRestTime']=sch.EndRestTime
                        if ss['EndRestTime']<ss['StartRestTime']:
                            ss['EndRestTime']=ss['EndRestTime']+datetime.timedelta(days=1)
                    try:
                        if sch.StartRestTime1!=None:
                            sch.StartRestTime1=checkTime(sch.StartRestTime1)
                            ss['StartRestTime1']=sch.StartRestTime1

                        if sch.EndRestTime1!=None:
                            sch.EndRestTime1=checkTime(sch.EndRestTime1)
                            ss['EndRestTime1']=sch.EndRestTime1

                    except:
                        pass

                    if (sch.StartRestTime==checkTime(datetime.time(0,0,0))) and (sch.EndRestTime==checkTime(datetime.time(0,0,0))):
                        ss['IsCalcRest']=0
            except:
                pass

            if ss['IsCalcRest']==1:
                ms=ss['EndRestTime']-ss['StartRestTime']+(ss['EndRestTime1']-ss['StartRestTime1'])
                ss['RestMins']=ms.days*24*60+ms.seconds/60
                if ss['RestMins']>240:	#说明设置有问题
                    ss['IsCalcRest']=0
                    ss['RestMins']=0
            try:
                if sch.NextDay!=None:
                    ss['NextDay']=int(sch.NextDay)-1
            except:
                pass
            if ss['NextDay']<0 or ss['NextDay']>2:
                ss['NextDay']=0

            if ss['TimeZone']['EndTime']<ss['TimeZone']['StartTime']:
                if ss['NextDay']<1:
                    ss['NextDay']=1
            ss['TimeZone']['EndTime']=ss['TimeZone']['EndTime']+datetime.timedelta(days=ss['NextDay'])
            ms=ss['TimeZone']['EndTime']-ss['TimeZone']['StartTime']
            ss['TimeZoneMins']=ms.days*24*60+ms.seconds/60
            ss['WorkMins']=ss['TimeZoneMins']-ss['RestMins']
            if sch.WorkDay!=None:
                ss['WorkDay']=sch.WorkDay
            try:
                if sch.CheckInMins1!=None:
                    ss['Intime']['StartTime']=ss['TimeZone']['StartTime']-datetime.timedelta(minutes=sch.CheckInMins1)
                else:
                    ss['Intime']['StartTime']=ss['TimeZone']['StartTime']-datetime.timedelta(hours=2)
            except:
                ss['Intime']['StartTime']=ss['TimeZone']['StartTime']-datetime.timedelta(hours=2)

            try:
                if sch.CheckInMins2!=None:
                    ss['Intime']['EndTime']=ss['TimeZone']['StartTime']+datetime.timedelta(minutes=sch.CheckInMins2)
                else:
                    ss['Intime']['EndTime']=ss['TimeZone']['StartTime']+(ss['TimeZone']['EndTime']-ss['TimeZone']['StartTime'])/2
            except:
                ss['Intime']['EndTime']=ss['TimeZone']['StartTime']+(ss['TimeZone']['EndTime']-ss['TimeZone']['StartTime'])/2
            try:
                if sch.CheckOutMins1!=None:
                    ss['Outtime']['StartTime']=ss['TimeZone']['EndTime']-datetime.timedelta(minutes=sch.CheckOutMins1)
                else:
                    ss['Outtime']['StartTime']=ss['TimeZone']['EndTime']-(ss['TimeZone']['EndTime']-ss['TimeZone']['StartTime'])/2
            except:
                ss['Outtime']['StartTime']=ss['TimeZone']['EndTime']-(ss['TimeZone']['EndTime']-ss['TimeZone']['StartTime'])/2
            try:
                if sch.CheckOutMins2!=None:
                    ss['Outtime']['EndTime']=ss['TimeZone']['EndTime']+datetime.timedelta(minutes=sch.CheckOutMins2)
                else:
                    ss['Outtime']['EndTime']=ss['TimeZone']['EndTime']+datetime.timedelta(hours=6)
            except:
                ss['Outtime']['EndTime']=ss['TimeZone']['EndTime']+datetime.timedelta(hours=6)
            try:
                if sch.IsCalcOverTime:
                    ss['IsCalcOverTime']=sch.IsCalcOverTime
                    if sch.OverTimeMins!=None:
                        ss['OverTimeMins']=sch.OverTimeMins

                #else:
                #	ss['IsCalcOverTime']=AttRule['OutOverTime']
                #	ss['OverTimeMins']=AttRule['MinsOutOverTime']
            except:
                pass
            try:
                if sch.IsCalcComeOverTime:
                    ss['IsCalcComeOverTime']=sch.IsCalcComeOverTime
                    if sch.ComeOverTimeMins!=None:
                        ss['ComeOverTimeMins']=sch.ComeOverTimeMins
                #else:
                #	ss['IsCalcComeOverTime']=AttRule['ComeOverTime']
                #	ss['ComeOverTimeMins']=AttRule['MinsComeOverTime']
            except:
                pass
            try:
                if sch.TimeZoneOfDept!=None:
                    ss['TimeZoneOfDept']=sch.TimeZoneOfDept
            except:
                pass
            try:
                if sch.TimeZoneType!=None:
                    ss['TimeZoneType']=sch.TimeZoneType
            except:
                pass

            try:
                if sch.BeforeInMins!=None:
                    ss['BeforeInMins']=sch.BeforeInMins
            except:
                pass
            try:
                if sch.AfterInMins!=None:
                    ss['AfterInMins']=sch.AfterInMins
            except:
                pass
            #if ss['TimeZoneType']:
            #	ss['Intime']['StartTime']=ss['TimeZone']['StartTime']-datetime.timedelta(minutes=ss['BeforeInMins'])
            #	ss['Intime']['EndTime']=ss['TimeZone']['StartTime']+datetime.timedelta(minutes=ss['AfterInMins'])
            #	ss['Outtime']['StartTime']=ss['TimeZone']['StartTime']
            #	ss['Outtime']['EndTime']=ss['TimeZone']['EndTime']+datetime.timedelta(hours=6)
            #


            t=ss.copy()
            re.append(t)
        schClasses=copy.deepcopy(re)
#		if not schID:
#		    cache.set("%s_schclasses"%(settings.UNIT),schClasses)
        return schClasses




    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True,'frozen': True},
            {'name':'SchID','index':'SchclassID','width':60,'sortable':True,'label':unicode(u'编号')},
            {'name':'SchName','width':120,'index':'SchName','sortable':True,'label':unicode(SchClass._meta.get_field('SchName').verbose_name),'frozen': True},
            {'name':'Data','width':60,'sortable':False,'label':unicode(u'数据')},
            {'name':'StartTime','width':70,'label':unicode(SchClass._meta.get_field('StartTime').verbose_name)},
            {'name':'EndTime','width':70,'label':unicode(SchClass._meta.get_field('EndTime').verbose_name)},
            {'name':'LateMinutes','width':60,'label':unicode(_(u'分钟'))},
            {'name':'EarlyMinutes','width':80,'label':unicode(_(u'分钟'))},
            {'name':'CheckIn','width':70,'label':unicode(SchClass._meta.get_field('CheckIn').verbose_name)},
            {'name':'CheckOut','width':70,'label':unicode(SchClass._meta.get_field('CheckOut').verbose_name)},
            {'name':'CheckInMins1','width':60,'label':unicode(SchClass._meta.get_field('CheckInMins1').verbose_name)},
            {'name':'CheckInMins2','width':60,'label':unicode(SchClass._meta.get_field('CheckInMins2').verbose_name)},
            {'name':'CheckOutMins1','width':60,'label':unicode(SchClass._meta.get_field('CheckOutMins1').verbose_name)},
            {'name':'CheckOutMins2','width':60,'label':unicode(SchClass._meta.get_field('CheckOutMins2').verbose_name)},
            {'name':'IsCalcComeOverTime','width':80,'label':unicode(SchClass._meta.get_field('IsCalcComeOverTime').verbose_name)},
            {'name':'IsCalcOverTime','width':80,'label':unicode(SchClass._meta.get_field('IsCalcOverTime').verbose_name)},
            {'name':'Holiday','width':80,'label':unicode(SchClass._meta.get_field('Holiday').verbose_name)},

            {'name':'AutoBind','hidden':True},
            {'name':'IsCalcRest','width':80,'label':unicode(SchClass._meta.get_field('IsCalcRest').verbose_name)},
            {'name':'StartRestTime','width':100,'label':unicode(SchClass._meta.get_field('StartRestTime').verbose_name)},
            {'name':'EndRestTime','width':100,'label':unicode(SchClass._meta.get_field('EndRestTime').verbose_name)},
            {'name':'StartRestTime1','width':100,'label':unicode(SchClass._meta.get_field('StartRestTime1').verbose_name)},
            {'name':'EndRestTime1','width':100,'label':unicode(SchClass._meta.get_field('EndRestTime1').verbose_name)},
            {'name':'TimeZoneType','width':80,'label':unicode(SchClass._meta.get_field('TimeZoneType').verbose_name)},
            {'name':'WorkDay','width':100,'label':unicode(SchClass._meta.get_field('WorkDay').verbose_name)},
            {'name':'TimeZoneMins','sortable':False,'width':80,'label':unicode(_(u'时长(分)'))},
            {'name':'Color','sortable':False,'width':100,'label':unicode(SchClass._meta.get_field('Color').verbose_name)},
            {'name':'TimeZoneOfDept','sortable':False,'width':100,'label':unicode(SchClass._meta.get_field('TimeZoneOfDept').verbose_name)},
            ]
    @staticmethod
    def HeaderModels():
        return [
            {'startColumnName': 'StartTime', 'numberOfColumns': 2, 'titleText': '<em>工作时间</em>'},
            {'startColumnName': 'LateMinutes', 'numberOfColumns': 1, 'titleText': '<em>'+unicode(SchClass._meta.get_field('LateMinutes').verbose_name)+'</em>'},
            {'startColumnName': 'EarlyMinutes', 'numberOfColumns': 1, 'titleText': '<em>'+unicode(SchClass._meta.get_field('EarlyMinutes').verbose_name)+'</em>'},
            {'startColumnName': 'CheckInMins1', 'numberOfColumns': 2, 'titleText': '<em>签到时间范围(分钟)</em>'},
            {'startColumnName': 'CheckOutMins1', 'numberOfColumns': 2, 'titleText': '<em>签退时间范围(分钟)</em>'},

               ]
    class Admin:
        search_fields = ['SchName']
    class Meta:
        db_table = 'SchClass'
        verbose_name=_('shift time-table')
        verbose_name_plural=verbose_name




#class SchClassForm(forms.Form):
#    TimeZoneType = forms.ChoiceField(label='弹性上班类型', choices=(('0', '不是弹性上班'), ('1', '是弹性上班')), widget=forms.RadioSelect(), initial='0')
#    class Meta:
#        model = SchClass
#
#
#
#class SchClassAdmin(admin.ModelAdmin):
#    form = SchClassForm
#
#admin.site.register(SchClass, SchClassAdmin)
#





class UserUsedSClasses(models.Model):
#	ID=models.AutoField(primary_key=True,null=False, editable=False)
    UserID = models.IntegerField("employee", db_column='UserId',blank=True)
    SchId=models.IntegerField(null=True,db_column='SchId',editable=False)
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    class Admin:
        pass

    class Meta:
        db_table = 'UserUsedSClasses'
        unique_together = (("UserID","SchId"),)


class AuditedExc(models.Model):
    AEID=models.AutoField(primary_key=True,null=False, editable=False)
    UserID = models.ForeignKey("employee", db_column='UserId', verbose_name=_('employee'),blank=True)
    CheckTime = models.DateTimeField(_('CheckTime'), db_column='checktime',blank=False)
    UTime = models.DateTimeField(_('UTime'), db_column='Utime',blank=False)
    NewExcID=models.SmallIntegerField(blank=True,default=0)
    IsLeave=models.SmallIntegerField(blank=True)
    UName=models.CharField( max_length=20,blank=True)
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    class Admin:
        pass
    class Meta:
        db_table = 'AuditedExc'


class attCalcLog(models.Model):
    DeptID=models.IntegerField(db_column='DeptID',null=True,blank=True, default=0)
    UserID = models.IntegerField(db_column='UserId', blank=True)
    StartDate = models.DateTimeField( db_column='StartDate',blank=True,null=True)
    EndDate = models.DateTimeField(db_column='EndDate',blank=True)
    OperTime = models.DateTimeField(db_column='OperTime',blank=True)
    Type=models.IntegerField(null=True,default=0,blank=True, editable=False)
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID)
        except:
            return None
    class Admin:
        pass
    class Meta:
        db_table = 'attcalclog'
        unique_together = (("DeptID","UserID","StartDate", "EndDate","Type"),)
        permissions = (
                        ('sys_basic_setting','sys_basic_setting'),
                        ('sys_email_setting','sys_email_setting'),
                        ('sys_state_setting','sys_state_setting'),
                        ('sys_api_setting','sys_api_setting'),
                        ('sys_calc_setting','sys_calc_setting'),
                        ('sys_del_setting','sys_delete_setting'),
                        ('sys_pos_setting','sys_pos_setting'),
                        ('sys_sap_setting','sys_sap_setting'),
                        ('sys_acc_setting','sys_acc_setting'),
                        ('sys_app_setting','sys_app_setting'),


            )


#统计结果用表-异常记录表
class AttException(models.Model):
    UserID = models.ForeignKey(employee, db_column='UserId', verbose_name=_('employee'),blank=True)
    StartTime = models.DateTimeField(_('StartTime'), db_column='StartTime')
    EndTime = models.DateTimeField(_('EndTime'), db_column='EndTime')
    ExceptionID=models.IntegerField(_('Exception'),null=True,blank=True,default=0)
    UserSpedayID=models.IntegerField(_('UserSpeday'),null=True,blank=True,default=0)
    AuditExcID=models.IntegerField(_('AuditExc'),null=True,blank=True,default=0)
    OldAuditExcID=models.IntegerField(_('OldAuditExc'),null=True,blank=True,default=0)
    OverlapTime=models.IntegerField(db_column='OverlapTime',null=True,blank=True,default=0)        #排班时长
    TimeLong=models.IntegerField(_('TotalTimeLong'), db_column='TimeLong',null=True,blank=True,default=0)          #总时长
    InScopeTime=models.IntegerField(_('ValidateTimeLong'), db_column='InScopeTime',null=True,blank=True,default=0)   #有效时长
    AttDate=models.DateTimeField(_('AttDate'),db_column='AttDate',null=True,blank=True)
    OverlapWorkDayTail=models.IntegerField( db_column='OverlapWorkDayTail')
    OverlapWorkDay=models.FloatField(db_column='OverlapWorkDay',null=True,default=1,blank=True)     #排班工作日
    schindex=models.IntegerField(db_column='schindex',null=True,blank=True,default=0)
    Minsworkday=models.IntegerField(db_column='Minsworkday',null=True,blank=True,default=0)
    schid=models.IntegerField(db_column='schid',null=True,blank=True,default=0)

    def __unicode__(self):
        return unicode(u"%s"%(self.UserID))
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    @staticmethod
    def colModels():
        return [
            {'name':'UserID','hidden':True},
            {'name':'DeptName','width':180,'sortable':False,'label':unicode(_('department name'))},
            {'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'Workcode', 'index':'UserID__Workcode', 'width':100, 'label':unicode(_('NewPin'))},
            {'name':'EName','sortable':False,'width':80,'label':unicode(_('EName'))},
            {'name':'AttDate','index':'AttDate','width':120,'label':unicode(_('AttDate'))},
            {'name':'StartTime','sortable':False,'width':80,'label':unicode(_('StartTime'))},
            {'name':'EndTime','sortable':False,'width':80,'label':unicode(_('EndTime'))},
            {'name':'ExceptionID','sortable':False,'width':180,'label':unicode(_('Exception'))},
            {'name':'TimeLong','sortable':False,'width':100,'label':unicode(_('TotalTimeLong(min.)'))},
            {'name':'InScopeTime','sortable':False,'width':100,'label':unicode(_('ValidateTimeLong(min.)'))},
            ]
    class Admin:
        search_fields = ['UserID__PIN','UserID__Workcode']
    class Meta:
        verbose_name=_(u'人员出勤异常详情')
        db_table='attexception'
        unique_together = (("UserID","AttDate", "StartTime"),)

#统计结果用表-记录状态表 作废
class attRecAbnormite(models.Model):
    UserID = models.ForeignKey(employee, db_column='userid', verbose_name=_("employee"))
    checktime = models.DateTimeField(_('CheckTime'), db_column='checktime')
    CheckType = models.CharField(_('CheckType'),db_column='CheckType', max_length=2)
    NewType = models.CharField(_('NewType'), db_column='NewType', max_length=2,null=True,blank=True)
    AbNormiteID=models.IntegerField(db_column='AbNormiteID',  null=True,blank=True)
    SchID=models.IntegerField(_('Schclass'),db_column='SchID',  null=True,blank=True)
    OP=models.IntegerField(_('Operation'),db_column='OP',  null=True,blank=True)
    AttDate=models.DateTimeField(_('AttDate'),db_column='AttDate',null=True,blank=True)
    SN = models.ForeignKey(iclock, db_column='SN', verbose_name=_('device'), null=True, blank=True)
    Verify = models.IntegerField(_('verification'), db_column='verifycode', default=0, choices=VERIFYS)

    def getComVerifys(self):
        try:
            if self.SN:
                iclockObj=iclock.objects.get(SN=self.SN_id)
                if iclockObj.Authentication==2:
                    for i in range(len(COMVERIFYS)):
                        if self.Verify==COMVERIFYS[i][0]:
                            return COMVERIFYS[i][1].title()
                else:
                    return self.get_Verify_display()
            else:
                return ""
        except Exception,e:
            print 99999999,e
            return ""#self.get_Verify_display()
    def __unicode__(self):
        return unicode(u"%s"%(self.UserID))
    def Device(self):
        return getDevice(self.SN_id)
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    @staticmethod
    def colModels():
        return [
            {'name':'UserID','hidden':True},
            {'name':'DeptName','width':180,'sortable':False,'label':unicode(_('department name'))},
            {'name':'PIN','sortable':False,'index':'UserID_PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'Workcode', 'sortable':False, 'index':'UserID_Workcode', 'width':120, 'label':unicode(_('Newpin'))},
            {'name':'EName','sortable':False,'width':80,'label':unicode(_('EName'))},
            {'name':'checktime','sortable':False,'index':'checktime','width':120,'label':unicode(_('CheckTime'))},
            {'name':'Verify','width':80,'label':unicode(_('Verification'))},
            {'name':'CheckType','width':80,'label':unicode(_('CheckType'))},
            {'name':'NewType','sortable':False,'width':180,'label':unicode(_('NewType'))},
            {'name':'AbNormiteID','sortable':False,'width':100,'label':unicode(_('Memo.'))},
            {'name':'Device','sortable':False,'width':100,'label':unicode(_('Device name'))},
            ]

    class Admin:
        list_display=('UserID','checktime','CheckType','AbNormiteID','NewType')
        search_fields = ['UserID__PIN','UserID_Workcode']
    class Meta:
        verbose_name=_("attRecAbnormite")
        verbose_name_plural=_("attRecAbnormite")
        db_table='attrecabnormite'
        unique_together = (("UserID","checktime"),)
#		unique_together = (("UserID","AttDate", "checktime"),)


class attShifts(models.Model):
    UserID = models.ForeignKey("employee", db_column='userid',null=False, verbose_name=_("employee"))
    SchIndex=models.IntegerField(db_column='SchIndex',  null=True,blank=True)
    AutoSch=models.SmallIntegerField(db_column='AutoSch',null=True,default=0,editable=False)
    AttDate = models.DateTimeField(_('AttDate'), db_column='AttDate')
    #SchId=models.IntegerField(_('SchName'),db_column='SchId',  null=True,blank=True)
    SchId=models.ForeignKey("SchClass", verbose_name=_('time-table class'), db_column='SchId', null=True,default=-1,blank=True)

    ClockInTime = models.DateTimeField(_('ClockInTime'), db_column='ClockInTime')
    ClockOutTime = models.DateTimeField(_('ClockOutTime'), db_column='ClockOutTime')
    StartTime = models.DateTimeField(_('On duty'), db_column='StartTime',null=True,blank=True)
    EndTime = models.DateTimeField(_('Off duty'), db_column='EndTime',null=True,blank=True)
    WorkDay=models.FloatField(_('WorkDay'),db_column='WorkDay',null=True,blank=True)
    RealWorkDay=models.FloatField(_('RealWorkDay'),db_column='RealWorkDay',null=True,default=0,blank=True)
    NoIn=models.SmallIntegerField(_('NoIn'),db_column='NoIn',null=True,blank=True)
    NoOut=models.SmallIntegerField(_('NoOut'),db_column='NoOut',null=True,blank=True)
    Late = models.IntegerField(_('LateTimes'), db_column='Late',null=True,blank=True)
    Early = models.IntegerField(_('EarlyTimes'), db_column='Early',null=True,blank=True)
    Absent = models.IntegerField(_('Absent'), db_column='Absent',null=True,blank=True)
    OverTime = models.FloatField(_('OverTime'), db_column='OverTime',null=True,blank=True)
    WorkTime = models.IntegerField(_('WorkTime'), db_column='WorkTime',null=True,blank=True)
    ExceptionID=models.IntegerField(_('Exception'),db_column='ExceptionID',  null=True,blank=True)
    Symbol = models.CharField(_('Symbol'), db_column='Symbol', max_length=10,null=True,blank=True)
    MustIn=models.SmallIntegerField(_('MustIn'),db_column='MustIn',null=True,blank=True)
    MustOut=models.SmallIntegerField(_('MustOut'),db_column='MustOut',null=True,blank=True)
    OverTime1=models.IntegerField(_('OverTime1'),db_column='OverTime1',  null=True,blank=True)
    WorkMins = models.IntegerField(_('WorkMins'), db_column='WorkMins',null=True,blank=True)
    SSpeDayNormal=models.FloatField(_('SSpeDayNorma'),db_column='SSpeDayNormal',null=True,blank=True)
    SSpeDayWeekend=models.FloatField(_('SSpeDayWeekend'),db_column='SSpeDayWeekend',null=True,blank=True)
    SSpeDayHoliday=models.FloatField(_('SSpeDayHoliday'),db_column='SSpeDayHoliday',null=True,blank=True)
    AttTime = models.IntegerField(_('AttTime'), db_column='AttTime',null=True,blank=True)
    SSpeDayNormalOT=models.FloatField(_('SSpeDayNormalOT'),db_column='SSpeDayNormalOT',null=True,blank=True)
    SSpeDayWeekendOT=models.FloatField(_('SSpeDayWeekendOT'),db_column='SSpeDayWeekendOT',null=True,blank=True)
    SSpeDayHolidayOT=models.FloatField(_('SSpeDayHolidayOT'),db_column='SSpeDayHolidayOT',null=True,blank=True)
    AbsentMins=models.IntegerField(db_column='AbsentMins',  null=True,blank=True)
    AttChkTime = models.CharField(db_column='AttChkTime', max_length=10,null=True,blank=True)
    AbsentR=models.FloatField(db_column='AbsentR',null=True,blank=True)
    ScheduleName = models.CharField( db_column='ScheduleName', max_length=20,null=True,blank=True)
    MinsDay = models.IntegerField(null=True,blank=True) #因为时段中取消了记为多少工作日，在这里保存一天的排班时长，单位分钟，折算工作日用

    IsConfirm=models.SmallIntegerField(db_column='IsConfirm',null=True,blank=True)
    IsRead=models.SmallIntegerField(db_column='IsRead',null=True,blank=True)

    deptid=models.IntegerField(_(u'单位'),null=True,blank=True,default=0)
    def __unicode__(self):
        return unicode(u"%s"%(self.UserID))
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    @staticmethod
    def colModels():
        return [
            {'name':'UserID','hidden':True},
            {'name':'DeptName','width':180,'sortable':False,'label':unicode(_('department name'))},
            {'name':'PIN','index':'UserID_PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'EName','sortable':False,'width':80,'label':unicode(_('EName'))},
            {'name':'AttDate','index':'AttDate','width':120,'label':unicode(_('AttDate'))},
            {'name':'SchId','width':80,'label':unicode(_('SchId'))},
            {'name':'Late','width':80,'label':unicode(_('Late'))},
            {'name':'Early','sortable':False,'width':180,'label':unicode(_('Early'))},
            {'name':'StartTime','sortable':False,'width':100,'label':unicode(_('noin'))},
            {'name':'EndTime','sortable':False,'width':100,'label':unicode(_('noout'))},
            {'name':'Absent','sortable':False,'width':100,'label':unicode(_('Absent'))},
            ]

    class Admin:
        pass
    class Meta:
        db_table='attshifts'
        unique_together = (("UserID","AttDate", "SchId"),)
class attpriReport(models.Model):
    UserID = models.ForeignKey(employee, db_column='userid', verbose_name=_("employee"))
    AttDate = models.DateTimeField(_('AttDate'), db_column='AttDate',null=False,blank=False)
    AttChkTime = models.CharField( max_length=100,null=True,blank=True)
    AttAddChkTime = models.CharField( max_length=100,null=True,blank=True)
    AttLeaveTime = models.CharField( max_length=100,null=True,blank=True)
    SchName = models.CharField( max_length=100,null=True,blank=True)
    OP=models.IntegerField(_('Operation'),db_column='OP',  null=True,blank=True)
    Reserved = models.CharField( max_length=50,null=True,blank=True)

    def __unicode__(self):
        return unicode(u"%s"%(self.UserID))
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    @staticmethod
    def colModels():
        return [
            {'name':'UserID','hidden':True},
            {'name':'DeptName','width':180,'sortable':False,'label':unicode(_('department name'))},
            {'name':'PIN','index':'UserID_PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'EName','sortable':False,'width':80,'label':unicode(_('EName'))},
            {'name':'AttDate','index':'AttDate','width':120,'label':unicode(_('AttDate'))},
            {'name':'SchName','width':80,'label':unicode(_('SchName'))},
            {'name':'AttChkTime','width':80,'label':unicode(_('Original Attendance'))},
            {'name':'AttAddChkTime','sortable':False,'width':180,'label':unicode(_('Add Attendance'))},
            {'name':'AttLeaveTime','sortable':False,'width':100,'label':unicode(_('Leave'))},
            ]

    class Admin:
        list_display=('UserID','AttDate')
    class Meta:
        verbose_name=_("attpriReport")
        verbose_name_plural=_("attpriReport")
        db_table='attpriReport'
        unique_together = (("UserID","AttDate"),)


#
#ACCOUNTS_TYPE=(
#	(99,_('All')),
#	(1,_('ReCaluate Report')),
#	(2,_('special leave')),
#	(3,_('Forget Checkin/out')),
#	(4,_('OverTime')),
#	(5,_('Shifts for Employee')),
#	)
#STATUS=(
#	(99,_('No Locking')),
#	(1,_('Locked')),
#	(2,_('UnLocked')),
#	)
#此表建议作废
#class accounts(models.Model):
#	StartTime= models.DateTimeField(_('beginning time'), null=False,default=nextDay(), blank=True,editable=True)  
#	EndTime = models.DateTimeField(_('ending time'), null=False, default=endOfDay(nextDay()),blank=True,editable=True)
#	Type=models.IntegerField(_('Posting Type'), null=False,default=0,blank=True, editable=True,choices=ACCOUNTS_TYPE)         #如99表示全部 1表示重新统计报表,2请假,3忘签到签退,4加班单,5员工排班:(正常排班、临时排班、清除临时排班)
#	Status=models.IntegerField(_('Status'),null=True,blank=True,default=0,choices=STATUS)                     #99表示未锁,1表示锁定 2表示解锁
#	Reserved = models.CharField(_('Reserved'), max_length=20, null=True, blank=True, editable=False)
#	User = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('administrator'), null=True, blank=True, editable=False) 
#	@staticmethod	
#	def colModels():
#		return [
#			{'name':'id','hidden':True},
#			{'name':'StartTime','width':150,'label':unicode(accounts._meta.get_field('StartTime').verbose_name)},
#			{'name':'EndTime','width':150,'label':unicode(accounts._meta.get_field('EndTime').verbose_name)},
#			{'name':'Type','sortable':False,'width':80,'label':unicode(accounts._meta.get_field('Type').verbose_name)},
#			{'name':'Status','sortable':False,'width':80,'label':unicode(accounts._meta.get_field('Status').verbose_name)},
#			{'name':'Reserved','hidden':True},
#			{'name':'User','hidden':True}
#			]	
#	class Meta:
#		verbose_name=_("accounts")
#		verbose_name_plural=_("Posting")
#		db_table='accounts'
#		unique_together = (("StartTime","EndTime","Type","Status"),)



PUBLISHED=(
(0, "NOT SHARE"),
(1, "SHARE READ"),
(2, "SHARE READ/WRITE")
)
#用于保存每个人的统计日期
class calcDate(models.Model):
    UserID = models.ForeignKey("employee")
    ItemValue=models.TextField(null=True)
    class Admin:
        pass
    class Meta:
        verbose_name=_("item define")
        verbose_name_plural=_("item define")
        db_table='calcdate'
        #unique_together = ("UserID",)
    def save(self, *args, **kwargs):
        super(calcDate, self).save(*args, **kwargs)


#用以保存不同管理员设置的个性配置
class ItemDefine(models.Model):
    ItemName=models.CharField(max_length=100,null=False)
    ItemType=models.CharField(max_length=20,null=True)
    Author=models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    ItemValue=models.TextField(max_length=100*1024,null=True)
    Published=models.IntegerField(null=True, choices=PUBLISHED, default=0)
    class Admin:
        pass
    class Meta:
        verbose_name=_("item define")
        verbose_name_plural=_("item define")
        db_table='itemdefine'
        #unique_together = (("ItemName","Author","ItemType"),)
#		permissions = (
#					('Forget_transaction','operate Forget to clock in and out'),
#					('report_transaction','operate reports'),
#					('reCalcaluteReport_transaction','ReCalculate Reports'),
#					('definedReport_user_speday','user-defined report'),
#		)


#	##开门时间段类别设置表##
#class ACTimeZones(models.Model):
#	TimeZoneID=models.IntegerField(_('TimeZoneID'),primary_key=True,null=False,editable=True,choices=TIMEZONES_CHOICES)
#	Name=models.CharField(_('ACTimeZones name'), max_length=30,null=False,blank=True)
#	SunStart = models.TimeField(_('Sunday StartTime'),null=True, blank=True)
#	SunEnd = models.TimeField(_('Sunday EndTime'),null=True, blank=True)
#	MonStart=models.TimeField(_('Monday StartTime'),null=True,blank=True)
#	MonEnd=models.TimeField(_('Monday EndTime'),null=True,blank=True)
#	TuesStart=models.TimeField(_('Tuesday StartTime'),null=True,blank=True)
#	TuesEnd=models.TimeField(_('Tuesday EndTime'),null=True,blank=True)
#	WedStart=models.TimeField(_('Wednesday StartTime'),null=True,blank=True)
#	WedEnd=models.TimeField(_('Wednesday EndTime'),null=True,blank=True)
#	ThursStart=models.TimeField(_('Thursday StartTime'),null=True,blank=True)
#	ThursEnd=models.TimeField(_('Thursday EndTime'),null=True,blank=True)
#	FriStart=models.TimeField(_('Friday StartTime'),null=True,blank=True)
#	FriEnd=models.TimeField(_('Friday EndTime'),null=True,blank=True)
#	SatStart=models.TimeField(_('Saturday StartTime'),null=True,blank=True)
#	SatEnd=models.TimeField(_('Saturday EndTime'),null=True,blank=True)
#	def __unicode__(self):
#		return unicode(u"%s"%(self.Name))
#	@staticmethod
#	def objByID(id):
#		try:
#			act=ACTimeZones.objects.get(TimeZoneID=id)
#		except:
#			act=''
#		return act
#	
#	@staticmethod	
#	def colModels():
#		return [
#			#{'name':'TimeZoneID','hidden':False},
#			{'name':'TimeZoneID','width':80,'label':unicode(ACTimeZones._meta.get_field('TimeZoneID').verbose_name)},
#			{'name':'Name','width':100,'label':unicode(ACTimeZones._meta.get_field('Name').verbose_name)},
#			{'name':'SunStart','width':100,'label':unicode(ACTimeZones._meta.get_field('SunStart').verbose_name)},
#			{'name':'SunEnd','width':100,'label':unicode(ACTimeZones._meta.get_field('SunEnd').verbose_name)},
#			{'name':'MonStart','width':100,'label':unicode(ACTimeZones._meta.get_field('MonStart').verbose_name)},
#			{'name':'MonEnd','width':100,'label':unicode(ACTimeZones._meta.get_field('MonEnd').verbose_name)},
#			{'name':'TuesStart','width':100,'label':unicode(ACTimeZones._meta.get_field('TuesStart').verbose_name)},
#			{'name':'TuesEnd','width':100,'label':unicode(ACTimeZones._meta.get_field('TuesEnd').verbose_name)},
#			{'name':'WedStart','width':100,'label':unicode(ACTimeZones._meta.get_field('WedStart').verbose_name)},
#			{'name':'WedEnd','width':100,'label':unicode(ACTimeZones._meta.get_field('WedEnd').verbose_name)},
#			{'name':'ThursStart','width':100,'label':unicode(ACTimeZones._meta.get_field('ThursStart').verbose_name)},
#			{'name':'ThursEnd','width':100,'label':unicode(ACTimeZones._meta.get_field('ThursEnd').verbose_name)},
#			{'name':'FriStart','width':100,'label':unicode(ACTimeZones._meta.get_field('FriStart').verbose_name)},
#			{'name':'FriEnd','width':100,'label':unicode(ACTimeZones._meta.get_field('FriEnd').verbose_name)},
#			{'name':'SatStart','width':100,'label':unicode(ACTimeZones._meta.get_field('SatStart').verbose_name)},
#			{'name':'SatEnd','width':100,'label':unicode(ACTimeZones._meta.get_field('SatEnd').verbose_name)}
#			]	
#	class Admin:
#		search_fields=['Name']
#	class Meta:
#		db_table = 'ACTimeZones'
#		verbose_name=_('ACTimeZones-table')
#		verbose_name_plural=verbose_name
#	

    ##门禁组类别设置表##
#class ACGroup(models.Model):
#	#GroupID=models.AutoField(primary_key=True,null=False, editable=False)
#	GroupID=models.IntegerField(_('GroupID'),primary_key=True, editable=True,choices=ACGroupS_CHOICES)
#	Name=models.CharField(_('ACGroup name'), max_length=30,null=True,blank=True)
#	TimeZone1 = models.IntegerField(_('TimeZone1'),null=True, blank=True,default=0)
#	TimeZone2 = models.IntegerField(_('TimeZone2'),null=True, blank=True,default=0)
#	TimeZone3 = models.IntegerField(_('TimeZone3'),null=True,blank=True,default=0)
#	VerifyType=models.IntegerField(_('VerifyType'), null=True,editable=True,default=0,choices=ACGroup_VerifyType)
#	HolidayValid=models.SmallIntegerField(_("HolidayValid"), null=True,default=0, editable=True, choices=BOOLEANS)
#	def __unicode__(self):
#		return unicode(u"%s"%(self.Name))
#	@staticmethod
#	def objByID(id):
#		if id==None: return None
#		g=cache.get("%s_iclock_acgroup_%s"%(settings.UNIT,id))
#		if g: return g
#		g=ACGroup.objects.get(GroupID=id)
#		if g:
#			cache.set("%s_iclock_acgroup_%s"%(settings.UNIT,id),g)
#		return g
#	def save(self):
#		cache.delete("%s_iclock_acgroup_%s"%(settings.UNIT,self.GroupID))
#		super(ACGroup,self).save()
#	def delete(self):
#		cache.delete("%s_iclock_acgroup_%s"%(settings.UNIT,self.GroupID))
#		super(ACGroup, self).delete()
#	
#	@staticmethod	
#	def colModels():
#		return [
#			#{'name':'GroupID','hidden':True},
#			{'name':'GroupID','width':80,'label':unicode(ACGroup._meta.get_field('GroupID').verbose_name)},
#			{'name':'Name','width':100,'label':unicode(ACGroup._meta.get_field('Name').verbose_name)},
#			{'name':'TimeZone1','width':100,'label':unicode(ACGroup._meta.get_field('TimeZone1').verbose_name)},
#			{'name':'TimeZone2','width':100,'label':unicode(ACGroup._meta.get_field('TimeZone2').verbose_name)},
#			{'name':'TimeZone3','width':100,'label':unicode(ACGroup._meta.get_field('TimeZone3').verbose_name)},
#			{'name':'VerifyType','width':100,'label':unicode(ACGroup._meta.get_field('VerifyType').verbose_name)},
#			{'name':'HolidayValid','width':100,'label':unicode(ACGroup._meta.get_field('HolidayValid').verbose_name)}
#			]	
#	class Admin:
#		search_fields=['Name']
#	class Meta:
#		db_table = 'ACGroup'
#		verbose_name=_('ACGroup-table')
#		verbose_name_plural=verbose_name
#
#
#	##开锁组合类别设置表##
#class ACUnlockComb(models.Model):
#	#UnlockCombID=models.AutoField(primary_key=True,null=False, editable=False)
#	UnlockCombID=models.IntegerField(_('UnlockCombID'),primary_key=True,null=False, editable=True,choices=ACUnlockCombS_CHOICES)
#	Name=models.CharField(_('ACUnlockComb name'), max_length=30,null=True,blank=True)
#	Group01 = models.IntegerField(_('Group1'),null=True, blank=True)
#	Group02 = models.IntegerField(_('Group2'),null=True, blank=True)
#	Group03=models.IntegerField(_('Group3'),null=True,blank=True)
#	Group04=models.IntegerField(_('Group4'),null=True,blank=True)
#	Group05=models.IntegerField(_('Group5'),null=True,blank=True)
#	
#	def __unicode__(self):
#		return unicode(u"%s"%(self.Name))
#	@staticmethod	
#	def colModels():
#		return [
#			#{'name':'UnlockCombID','hidden':True},
#			{'name':'UnlockCombID','width':80,'label':unicode(ACUnlockComb._meta.get_field('UnlockCombID').verbose_name)},
#			{'name':'Name','width':100,'label':unicode(ACUnlockComb._meta.get_field('Name').verbose_name)},
#			{'name':'Group01','width':100,'label':unicode(ACUnlockComb._meta.get_field('Group01').verbose_name)},
#			{'name':'Group02','width':100,'label':unicode(ACUnlockComb._meta.get_field('Group02').verbose_name)},
#			{'name':'Group03','width':100,'label':unicode(ACUnlockComb._meta.get_field('Group03').verbose_name)},
#			{'name':'Group04','width':100,'label':unicode(ACUnlockComb._meta.get_field('Group04').verbose_name)},
#			{'name':'Group05','width':100,'label':unicode(ACUnlockComb._meta.get_field('Group05').verbose_name)}
#			]	
#	class Admin:
#		search_fields=['Name']
#	class Meta:
#		db_table = 'ACUnlockComb'
#		verbose_name=_('ACUnlockComb-table')
#		verbose_name_plural=verbose_name


#用以保存人员在哪台设备 未用
#class UserInMachines(models.Model):
#	UserID = models.ForeignKey(employee, db_column='userid', verbose_name=u"员工")
#	SN = models.CharField(_('serial number'), max_length=20 )
#	optime=models.DateTimeField(default=datetime.datetime.now)
#	flag = models.IntegerField(null=True, blank=True,default=0)
#	
#
#	
#	def __unicode__(self):
#		return unicode(u"%s"%(self.UserID))
#	def Device(self):
#		return getDevice(self.SN_id)
#	def employee(self): #cached employee
#		try:
#			return employee.objByID(self.UserID_id)
#		except:
#			return None
#		
#	class Admin:
#		pass
#	class Meta:
#		db_table = 'userinmachines'
#		verbose_name=_('userinmachines')
#		verbose_name_plural=verbose_name
#		unique_together = (('UserID', 'SN'),)

    ##公告类别设置表##
class Announcement(models.Model):
    id=models.AutoField(primary_key=True,null=False, editable=False)
    Title=models.CharField(_('headline'), max_length=80,null=False)
    Content = models.TextField(_('Content'),null=True,editable=True)
    PIN = models.CharField(_('number'),max_length=24,null=True,blank=True)
    Author=models.CharField(_('Author'),max_length=30,null=False)
    Pubdate=models.DateTimeField(_('Pubdate'),default=datetime.datetime.now,editable=True)
    Entrydate=models.DateTimeField(_(u'写入时间'),default=datetime.datetime.now,null=True,editable=False)
    Channel=models.IntegerField(_('Channel'),null=True,default=0)
    admin=models.IntegerField(_('admin'),null=True,default=0)
    IsTop=models.NullBooleanField(_(u'是否置顶'),null=True,default=False, blank=True,editable=True)

    def __unicode__(self):
        return unicode(u"%s,%s,%s"%(self.Title,self.Content,self.Author))
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'Title','width':200,'label':unicode(Announcement._meta.get_field('Title').verbose_name)},
            #{'name':'Content','width':500,'label':unicode(Announcement._meta.get_field('Content').verbose_name)},
            #{'name':'PIN','width':100,'label':unicode(Announcement._meta.get_field('PIN').verbose_name)},
            {'name':'Author','width':100,'label':unicode(Announcement._meta.get_field('Author').verbose_name)},
            {'name':'Pubdate','width':120,'label':unicode(Announcement._meta.get_field('Pubdate').verbose_name)}
            #{'name':'Channel','width':100,'label':unicode(Announcement._meta.get_field('Channel').verbose_name)},
            #{'name':'admin','width':100,'label':unicode(Announcement._meta.get_field('admin').verbose_name)}
            ]
    class Admin:
        search_fields=['Title']
    class Meta:
        db_table = 'Announcement'
        verbose_name=_(u'公告')
        verbose_name_plural=verbose_name


AUDIT_STATES=(
    (0,_('Apply')),
#	(1,_('Auditing')),
    (2,_('Accepted')),
    (3,_('Refused')),
#	(4,_('Paused')),
#	(5,_('Re-Apply')),
    (6,_('Again')),
#	(7,_('Cancel_leave'))
)

##加班单类别设置表##
class USER_OVERTIME(models.Model):
    UserID=models.ForeignKey(employee, db_column='UserID',verbose_name=_('employee'), default=1,null=False, blank=False)
    StartOTDay= models.DateTimeField(_(u'beginning time'), null=False, blank=True)
    EndOTDay = models.DateTimeField(_(u'ending time'), null=True,blank=True)
    YUANYING=models.CharField(_(u'reson'), max_length=200,null=True,blank=True)
    ApplyDate=models.DateTimeField(_(u'apply date'), null=True, blank=True)
    State=models.SmallIntegerField(_(u'state'), null=True, default=0, blank=True, choices=AUDIT_STATES, editable=False)
    AsMinute=models.IntegerField(_(u'As Minute'), null=True, default=0, blank=True)
    roleid = models.IntegerField(_(u'当前审核人'),editable=True)
    process=models.CharField(_(u'审核流程'),max_length=80,null=True,blank=True)
    oldprocess=models.CharField(_(u'审核过的流程'),max_length=80,null=True,blank=True)
    processid=models.IntegerField(_(u'审核流程id'),editable=True)
    procSN=models.IntegerField(_(u'已审序号'),default=0,editable=True)
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True,'frozen':True},
            {'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN')),'frozen':True},
            {'name':'Workcode', 'index':'UserID__Workcode', 'width':100, 'label':unicode(_('NewPin')), 'frozen':True},
            {'name':'EName','index':'UserID__EName','width':80,'label':unicode(_('EName')),'frozen':True},
            {'name':'StartOTDay','index':'StartOTDay','width':120,'label':unicode(USER_OVERTIME._meta.get_field('StartOTDay').verbose_name)},
            {'name':'EndOTDay','index':'EndOTDay','width':120,'label':unicode(USER_OVERTIME._meta.get_field('EndOTDay').verbose_name)},
            {'name':'AsMinute','sortable':False,'width':100,'label':unicode(USER_OVERTIME._meta.get_field('AsMinute').verbose_name)},
            {'name':'DeptID','index':'UserID__DeptID','width':70,'label':unicode(_('department number'))},
            {'name':'DeptName','index':'UserID__DeptID__DeptName','width':120,'label':unicode(_('department name'))},
            {'name':'State','index':'State','width':80,'label':unicode(USER_OVERTIME._meta.get_field('State').verbose_name)},
            {'name':'process','sortable':False,'index':'process','width':120,'label':unicode(_(u'审核员'))},
            {'name':'YUANYING','sortable':False,'width':120,'label':unicode(USER_OVERTIME._meta.get_field('YUANYING').verbose_name)},
            {'name':'ApplyDate','index':'ApplyDate','width':120,'label':unicode(USER_OVERTIME._meta.get_field('ApplyDate').verbose_name)}
            ]
    class Admin:
        list_filter =['State','UserID','StartOTDay','ApplyDate']
        lock_fields=['UserID']
        search_fields = ['UserID__PIN','UserID__EName','UserID__Workcode']
    class Meta:
        db_table = 'USER_OVERTIME'
        verbose_name = _('OverTime')
        verbose_name_plural=verbose_name
        unique_together = (("UserID", "StartOTDay"),)
        permissions = (
                                ('overtimeAudit_user_overtime','Audit OverTime'),
                    )

#用户职务表
class userRoles(models.Model):
    roleid=models.IntegerField(_('role id'),db_column='roleid',unique=True)
    roleName=models.CharField(_('role Name'),db_column='roleName',max_length=80,unique=True)
    roleLevel=models.IntegerField(_('role Level'), null=True, blank=True,editable=True,help_text=_(u"数字越大级别越高"))
    State = models.IntegerField(_('state'),default=0,editable=False, choices=BOOLEANS)
    @staticmethod
    def getallrole():
        rol=cache.get("%s_userRoles_all"%(settings.UNIT))
        if rol: return rol
        rols=userRoles.objects.all()
        rol={}
        for r in rols:
            rol[r.roleid]=r.roleName
        cache.set("%s_userRoles_all"%(settings.UNIT), rol, 5*60)
        return rol
    def __unicode__(self):
        try:
            return u"%d %s"%(self.roleid, self.roleName.decode("utf-8"))
        except:
            return u"%d %s"%(self.roleid, unicode(self.roleName))
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'roleid','index':'roleid','width':80,'label':unicode(userRoles._meta.get_field('roleid').verbose_name)},
            {'name':'roleName','index':'roleName','width':200,'label':unicode(userRoles._meta.get_field('roleName').verbose_name)},
            {'name':'roleLevel','index':'roleLevel','width':200,'label':unicode(userRoles._meta.get_field('roleLevel').verbose_name)}
            ]
    class Admin:
        search_fields=['roleid','roleName']
    class Meta:
        db_table = 'userRoles'
        verbose_name = _('userRoles')
        verbose_name_plural=verbose_name

#补签原因表
class forgetcause(models.Model):
    cause_Name=models.CharField(_(u'原因描述'),max_length=255, unique=True)

    @staticmethod
    def colModels():
        return [
            {'name':'cause_Name','index':'cause_Name','align':'center','width':360,'label':unicode(forgetcause._meta.get_field('cause_Name').verbose_name),'editable':True}
            ]
    class Admin:
        pass
    class Meta:
        db_table = 'forgetcause'
        verbose_name = _(u'补签原因')
        verbose_name_plural=verbose_name

#OTHER_STATES=(
#	(0,_('User OverTime')),
#	(1,_('Forget Checkin/out'))
#)

class userRole(models.Model):
    userid=models.ForeignKey(settings.AUTH_USER_MODEL)
    roleid=models.ForeignKey(userRoles,db_column='roleid',null=True,editable=False)
    def __unicode__(self):
        return unicode(self.userid)
    class Admin:
        list_display=("userid","roleid", )
    class Meta:
        verbose_name=_("admin granted userRole")
        verbose_name_plural=verbose_name

#审核流程表
class process(models.Model):
    processName=models.CharField(_('process Name'),db_column='processName',max_length=80,unique=True)
    State = models.IntegerField(_('state'),default=0,editable=True, choices=BOOLEANS)
    notitle=models.IntegerField(_('state'),default=0,editable=True, choices=BOOLEANS)
    smallday = models.IntegerField(_('Shortest'), null=True, blank=True,editable=True)
    bigday = models.IntegerField(_('Longest'), null=True, blank=True,editable=True)
    class Admin:
        pass
    class Meta:
        db_table = 'process'
        verbose_name = _('process')
        verbose_name_plural=verbose_name
#审核流程分配表
class prodeptmapping(models.Model):
    processid = models.ForeignKey(process,db_column='processid',null=True,editable=False)
    DeptID = models.ForeignKey(department,db_column="defaultdeptid", verbose_name=DEPT_NAME, editable=True, null=True)
    class Admin:
        pass
    class Meta:
        db_table = 'prodeptmapping'
        verbose_name = _('prodeptmapping')
        verbose_name_plural=verbose_name
        unique_together = (("processid","DeptID"),)

#审核流程假类表
#10000表示加班、如果还有其他需要审批的选项从10001开始排列。9999及其以下为假类
class proleave(models.Model):
    processid = models.ForeignKey(process,db_column='processid',null=True,editable=False)
    leaveid=models.IntegerField(_('Leave Class'),db_column='leaveid', null=False,default=-1,blank=True, editable=True)
    class Admin:
        pass
    class Meta:
        db_table = 'proleave'
        verbose_name = _('proleave')
        verbose_name_plural=verbose_name
        unique_together = (("processid","leaveid"),)

class protitle(models.Model):
    processid = models.ForeignKey(process,db_column='processid',null=True,editable=False)
    roleid=models.ForeignKey(userRoles,db_column='roleid',null=True,editable=False)
    class Admin:
        pass
    class Meta:
        db_table = 'protitle'
        verbose_name = _('protitle')
        verbose_name_plural=verbose_name
        unique_together = (("processid","roleid"),)


class userRolesDell(models.Model):  
    roleid=models.ForeignKey(userRoles,db_column='roleid',null=True,editable=False)
    processid = models.ForeignKey(process,db_column='processid',null=True,editable=False)
    procSN=models.IntegerField(_(u'顺序号'), null=True, blank=True,editable=True)
    State = models.IntegerField(_('state'),default=0,editable=True, choices=BOOLEANS)
    days=models.FloatField(_('days'), null=True, blank=True,editable=True)
    class Admin:
        pass
    class Meta:
        db_table = 'userRolesDell'
        verbose_name = _('userRolesDell')
        verbose_name_plural=verbose_name
        unique_together = (("roleid","processid","procSN"),)

#地图管理表
class MapManage(models.Model):
    mapid=models.AutoField(primary_key=True, null=False,editable=False)
    MapName = models.CharField(_(u'地图名称'),db_column="MapName",null=False,max_length=80)
    Remarks = models.TextField(_(u'备注'),null=True, blank=True)
    Reserved = models.IntegerField(null=True,default=1, blank=True,editable=False)
    Reserved1 = models.CharField(null=True,max_length=80, blank=True,editable=False)
    Reserved2 = models.CharField(null=True,max_length=80, blank=True,editable=False)
    class Admin:
        pass
    class Meta:
        db_table = 'mapmanage'
        verbose_name=_('mapmanage')
        permissions = (
            ('MapManage_SetMap','Set Map'),#设置地图
            ('MapManage_SaveStyle','Save Style'),#保存样式
            ('MapManage_RemoveMap','Remove Map'),#清除地图
            ('Map_Monitor','Map Monitor'),#电子地图监控
        )

#地图与门禁样式表
class MapIaccessStyle(models.Model):
    id=models.AutoField(primary_key=True, null=False,editable=False)
    iclock_id=models.ForeignKey(iclock,db_column='iclock_id',null=True,editable=True)
    mapmanage_id=models.ForeignKey(MapManage,db_column='mapmanage_id',null=True,editable=True)
    styles = models.CharField(u'样式',max_length=400,null=True, blank=True)
    Reserved = models.IntegerField(null=True,default=1, blank=True,editable=False)
    Reserved1 = models.CharField(null=True,max_length=80, blank=True,editable=False)
    Reserved2 = models.CharField(null=True,max_length=80, blank=True,editable=False)
    class Admin:
        pass
    class Meta:
        db_table = 'mapiaccessstyle'
        unique_together = (("iclock_id","mapmanage_id"),)
        verbose_name=_("mapiaccessstyle")
        verbose_name_plural=verbose_name

class days_off (models.Model):
    id=models.AutoField(primary_key=True, null=False,editable=False)
    DeptID = models.IntegerField(_("department"), db_column='deptid')
    UserID = models.IntegerField(_('employee'),db_column="userid",null=True)
    FromDate = models.DateField(_(u'调休日期'), null=False, blank=False,editable=True)
    ToDate = models.DateField(_(u'调至日期'), null=False, blank=False,editable=True)
    ApplyDate=models.DateTimeField(_('apply date'), null=True, blank=True)
    def department(self): #cached employee
        try:
            return department.objByID(self.DeptID)
        except:
            return None
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID)
        except:
            return None
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'DeptNumber','sortable':False,'width':80,'label':unicode(_('department number'))},
            {'name':'DeptName','sortable':False,'width':120,'label':unicode(_('department name'))},
            {'name':'PIN','width':110,'sortable':False,'label':unicode(_('PIN'))},
            {'name':'EName','width':80,'sortable':False,'label':unicode(_('EName'))},
            {'name':'FromDate','index':'FromDate','width':120,'label':unicode(_(u'调休日期'))},
            {'name':'ToDate','index':'ToDate','width':120,'label':unicode(_(u'调至日期'))},
            {'name':'ApplyDate','index':'ApplyDate','width':120,'label':unicode(_(u'操作时间'))}
            ]
    class Admin:
        my_search_fields =[{'model':employee,'name':u'人员','search_field':['PIN','EName'],'fromsearch_field':'id','tosearch_field':'UserID__in'},{'model':department,'name':u'部门','search_field':['DeptID','DeptName'],'fromsearch_field':'DeptID','tosearch_field':'DeptID__in'}]
    class Meta:
        db_table = 'daysoff'
        verbose_name = _(u'人员调休')
        verbose_name_plural=verbose_name
        unique_together = (("DeptID","UserID","FromDate"),)

class Eventtype(models.Model):
    id=models.AutoField(primary_key=True, null=False,editable=False)
    typename=models.CharField(u'类型名称',max_length=20,null=True, blank=True)
    color=models.IntegerField(_('display color'),null=True,default=16715535,blank=True,editable=True)
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'typename','index':'typename','width':60,'label':unicode(_(u'类型名称'))},
            {'name':'color','index':'color','width':120,'label':unicode(_(u'颜色'))},
            ]
    class Admin:
        pass
    class Meta:
        db_table = 'Eventtype'
        verbose_name = _('Eventtype')
        verbose_name_plural=verbose_name

ALARM_UNITS=(
    (0, _('Email')),
    (1, _('short message')),
)

ALARM_STATE=(
    (0, _(u'未发送')),
    (1, _(u'已发送')),
    (2, _(u'无效')),
)

class Alarmclock(models.Model):
    id=models.AutoField(primary_key=True, null=False,editable=False)
    StartTime = models.DateTimeField(_(u'开始时间'), null=False, blank=False,editable=True)
    AlarmType=models.IntegerField(_(u'提醒方式'),default=0,editable=True, choices=ALARM_UNITS)
    photooremail=models.CharField(_(u'手机或邮箱'),max_length=30,null=True, blank=True)
    description = models.CharField(_(u'事件描述'),max_length=250,null=True, blank=True)
    title=models.CharField(_(u'主题'),max_length=50,null=True, blank=True)
    State = models.IntegerField(_(u'状态'),default=0,editable=True, choices=ALARM_STATE)
    ApplyDate=models.DateTimeField(_(u'生成时间'), null=True,  blank=True)
    sentTime = models.DateTimeField(_(u'发送时间'),null=True, blank=True)
    class Admin:
        pass
    class Meta:
        db_table = 'Alarmclock'
        verbose_name = _('Alarmclock')
        verbose_name_plural=verbose_name

class daysPlanner(models.Model):
    id=models.AutoField(primary_key=True, null=False,editable=False)
    StartDate = models.DateField(_(u'开始日期'), null=False, blank=False,editable=True)
    EndDate = models.DateField(_(u'结束日期'), null=True, blank=False,editable=True)
    StartTime = models.TimeField(_('beginning time'),null=False, blank=False)
    EndTime = models.TimeField(_('ending time'),null=True, blank=False)
    description = models.CharField(u'事件描述',max_length=200,null=True, blank=True)
    allDay=models.IntegerField(_(u'整体标识'),default=0,editable=True, choices=BOOLEANS)
    note=models.CharField(u'备注',max_length=400,null=True, blank=True)
    type=models.ForeignKey(Eventtype,db_column='typeid',null=True,editable=True)
    isalarm= models.IntegerField(_(u'是否提醒'),default=0,editable=True, choices=BOOLEANS)
    notify=models.IntegerField(_(u'提前时间'), null=True, default=0, blank=True)
    Unit =models.IntegerField(_(u'单位'),default=0,editable=True, choices=LEAVE_UNITS)
    AlarmType=models.IntegerField(_(u'提醒方式'),default=0,editable=True, choices=ALARM_UNITS)
    phoneoremail=models.CharField(u'手机或邮箱',max_length=30,null=True, blank=True)
    alarmid=models.ForeignKey(Alarmclock,null=True,editable=True)
    userid=models.ForeignKey(settings.AUTH_USER_MODEL)
    employeeID = models.IntegerField(_('employee'),db_column="userid",null=True)
    class Admin:
        pass
    class Meta:
        unique_together = (("StartDate","StartTime","description"),)
        db_table = 'daysPlanner'
        verbose_name = _('daysPlanner')
        verbose_name_plural=verbose_name

class annual_leave(models.Model):
    UserID = models.ForeignKey("employee", db_column='userid')
    inyear = models.IntegerField(_(u'所在年度'), db_column='in_year',null=True,blank=True)
    months = models.IntegerField(_(u'工龄'), db_column='months',null=True,blank=True)
    annual_calc=models.FloatField(_(u'该年标准年休天数'),db_column='annual_calc',null=True,default=0,blank=True)
    annual_attach=models.FloatField(_(u'该年企业标准天数'),db_column='annual_attach',null=True,default=0,blank=True)
    annual_out=models.FloatField(_(u'该年已休天数'),db_column='annual_out',null=True,default=0,blank=True)
    reserved=models.FloatField(_(u'备注'),db_column='reserved',null=True,default=0,blank=True)

    class Admin:
        pass
    class Meta:
        unique_together = (("UserID","inyear"),)
        db_table = 'annual_leave'
        verbose_name = _('annual leave')
        verbose_name_plural=verbose_name
#		permissions = (
#			('annual_emp','annual emp'),#年休假报表
#		)


    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            #{'name':'DeptID','width':60,'index':'UserID__DeptID','label':unicode(_('department number'))},
            {'name':'DeptName','sortable':False,'width':180,'label':unicode(_('department name'))},
            {'name':'PIN','width':120,'label':unicode(_('PIN'))},
            {'name':'Workcode', 'width':120, 'label':unicode(_('NewPin'))},
            {'name':'EName','width':80,'label':unicode(_('EName'))},
            {'name':'Birthday','search':False,'width':80,'label':unicode(employee._meta.get_field('Birthday').verbose_name)},
            {'name':'Hiredday','search':False,'width':100,'label':unicode(employee._meta.get_field('Hiredday').verbose_name)},
            {'name':'WorkAge','sortable':False,'width':80,'label':unicode(_(u'工龄'))},
            {'name':'annual_std','sortable':False,'width':100,'label':unicode(_(u'法定年休天数'))},
            {'name':'annual_ent','sortable':False,'width':120,'label':unicode(_(u'企业标准年休天数'))}
#			{'name':'TTime','width':120,'search':False,'label':unicode(transaction._meta.get_field('TTime').verbose_name)},
#			{'name':'State','width':80,'search':False,'label':unicode(transaction._meta.get_field('State').verbose_name)},
#			{'name':'Verify','width':80,'search':False,'label':unicode(transaction._meta.get_field('Verify').verbose_name)},
#			{'name':'Device','index':'SN','width':180,'label':unicode(_('Device name'))},
#			{'name':'thumbnailUrl','search':False,'sortable':False,'width':100,'label':unicode(_('Picture'))}
            ]

    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None

class annual_settings(models.Model):
    id=models.AutoField(primary_key=True, null=False,editable=False)
    Name=models.CharField(_('name'),max_length=30,null=False)
    Type=models.CharField(_('type'),max_length=10,null=False)
    Value=models.CharField(_('value'),max_length=100,null=False)
    Sequence= models.CharField(_(u'序号'),max_length=10, null=False,blank=True)
    class Admin:
        @staticmethod
        def initial_data():

            if annual_settings.objects.all().count()==0:
                annual_settings(Name='month_s',Type="",Value="1",Sequence="").save()
                annual_settings(Name='day_s',Type="",Value="1",Sequence="").save()
                annual_settings(Name='type_b',Type="",Value="1",Sequence="").save()
                annual_settings(Name='guize',Type="",Value="1",Sequence="").save()
                annual_settings(Name='type_f',Type="",Value="Hiredday",Sequence="").save()
                annual_settings(Name='type_g',Type="1",Value="Hiredday",Sequence="").save()
                annual_settings(Name='type_g',Type="2",Value="Hiredday",Sequence="").save()
                annual_settings(Name='type_g',Type="3",Value="Hiredday",Sequence="").save()
                annual_settings(Name='type_g',Type="4",Value="Hiredday",Sequence="").save()
                annual_settings(Name='month_g',Type="1",Value="5",Sequence="").save()
                annual_settings(Name='xi_g',Type="2",Value="0",Sequence="").save()
                annual_settings(Name='xi_g',Type="3",Value="0",Sequence="").save()
                annual_settings(Name='xi_g',Type="4",Value="0",Sequence="").save()
                annual_settings(Name='man_g',Type="2",Value="0",Sequence="").save()
                annual_settings(Name='zeng_g',Type="2",Value="0",Sequence="").save()
                annual_settings(Name='max_g',Type="2",Value="0",Sequence="").save()
                annual_settings(Name='day_1_10',Type="3",Value="0",Sequence="").save()
                annual_settings(Name='day_10_20',Type="3",Value="0",Sequence="").save()
                annual_settings(Name='day_20',Type="3",Value="0",Sequence="").save()
                annual_settings(Name='nian_s',Type="4",Value="0",Sequence="1").save()
                annual_settings(Name='nian_e',Type="4",Value="0",Sequence="1").save()
                annual_settings(Name='nian_day',Type="4",Value="0",Sequence="1").save()
                annual_settings(Name='nian_end',Type="4",Value="0",Sequence="").save()
                annual_settings(Name='nian_day_end',Type="4",Value="0",Sequence="").save()
                annual_settings(Name='day_g',Type="1",Value="0",Sequence="").save()
                annual_settings(Name='RemaindProc',Type="",Value="0",Sequence="").save()



    class Meta:
        unique_together = (("Name","Type","Sequence"),)
        db_table = 'annual_settings'
        verbose_name = _('annual settings')
        verbose_name_plural=verbose_name

#设备上的人员
class empofdevice(models.Model):
    #UserID = models.ForeignKey(employee, db_column='userid')
    id=models.AutoField(primary_key=True)
    PIN = models.CharField(_('PIN'),db_column="badgenumber",null=False,max_length=24)
    SN = models.CharField(_('serial number'), max_length=20,db_column='sn')
    pri=models.IntegerField(default=0, choices=PRIV_CHOICES)
    def __unicode__(self):
        return u"%s %s"%(self.PIN, self.SN)
    class Admin:
        pass
    class Meta:
        verbose_name = _('empofdevice')
        verbose_name_plural=verbose_name
        unique_together = (("PIN","SN"),)
        db_table = 'empofdevice'

    def employee(self): #cached employee
        try:
            return employee.objByPIN(self.PIN)
        except:
            return None

    def save(self, *args, **kwargs):
        super(empofdevice, self).save(*args, **kwargs)

    def Device(self):
        return getDevice(self.SN)
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'PIN','index':'PIN','width':110,'label':unicode(_('PIN'))},
            {'name':'EName','sortable':False,'width':100,'label':unicode(_('Emp Name'))},
            {'name':'pri','sortable':False,'width':100,'sortable':True,'label':unicode(_(u'设备权限'))},
            {'name':'DeptName','sortable':False,'width':100,'label':unicode(_('department name'))},
            #{'name':'Card','sortable':False,'width':80,'label':unicode(employee._meta.get_field('Card').verbose_name)},
            {'name':'Title','sortable':False,'width':80,'label':unicode(_('Title'))},
            {'name':'SN','sortable':False,'width':90,'label':unicode(iclock._meta.get_field('SN').verbose_name)},
            {'name':'Alias','sortable':False,'width':140,'label':unicode(iclock._meta.get_field('Alias').verbose_name)}
            ]



def saveEmpInDevice(pin,sn,pri=-1):
    #try:
    #    sql="insert into empofdevice(badgenumber,sn) values(%s,%s)"
    #    params=(pin,sn)
    #    customSqlEx(sql,params)
    #except Exception,e:
    #	#print "saveEmpInDevice",e
    #	pass
    if not pri:pri=0
    objs=empofdevice.objects.filter(PIN=pin,SN=sn)
    if objs:
        obj=objs[0]
        if pri!=-1 and obj.pri!=pri:
            obj.pri=pri
            obj.save()
    else:
        if pri==-1:pri=0

        empofdevice(PIN=pin,SN=sn,pri=pri).save(force_insert=True)





#以下的删除只是删除记录在表empofdevice中相应的数据，和设备的数据没有任何关系
def delEmpInDevice(pin,sn):
    try:
        if pin!=-1 and sn!=-1:# 删除某设备上的某人
            sql="delete from empofdevice where badgenumber=%s and sn=%s"
            params=(pin,sn)
        elif sn!=-1 and pin==-1:# 删除某设备上的所有人
            sql="delete from empofdevice where sn=%s"
            params=(sn,)
        elif sn==-1 and pin!=-1:# 删除所有设备上的某人
            sql="delete from empofdevice where badgenumber=%s"
            params=(pin,)
        elif sn==-1 and pin==-1:# 删除所有数据
            sql="delete from empofdevice"
            params=()

        customSqlEx(sql,params)
    except Exception,e:
        connection.commit()
        print "delEmpInDevice",e
        pass




def batchSql(sqls):
    for s in sqls:
        customSql(s)
#			print "OK1: ", s









def __mci_init__(self, field):
    self.field = field
    q=[]
    try:
        for obj in field.queryset.all():
            q.append(obj)
        self.queryset=q
    except:
        connection.close()
        for obj in field.queryset.all():
            q.append(obj)
    self.queryset=q

def __mci_iter__(self):
    if self.field.empty_label is not None:
        yield (u"", self.field.empty_label)
    if self.field.cache_choices:
        if self.field.choice_cache is None:
            self.field.choice_cache = [
                self.choice(obj) for obj in self.queryset
            ]
        for choice in self.field.choice_cache:
            yield choice
    else:
        for obj in self.queryset:
            yield self.choice(obj)

#if settings.DATABASE_ENGINE=="sql_server":
#	ModelChoiceIterator.__init__=__mci_init__
#	ModelChoiceIterator.__iter__=__mci_iter__







def UpdateDeptCache():
    stamp='%s%s'%(settings.UNIT,datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))
    SetParamValue('DEPTVERSION',stamp)

    settings.DEPTVERSION=stamp











#需要为老版客户升级数据库时使用此函数， db建立数据库时不执行此函数
def UpdateDatabase():  #2009.2.25之后尽量使用此功能升级数据库
#	from iclock.iutils import GetParamValue
    dbVer=int(GetParamValue('ADMSDBVersion',100))
    if dbVer==-10000:
        return
    if dbVer<600:#ZKEcoPro从600开始
        sqls=(
              "ALTER TABLE %s ADD MinsDay integer NULL"%(attShifts._meta.db_table),
              "ALTER TABLE %s ADD AbNormiteID integer NULL" % (transactions._meta.db_table),
              "ALTER TABLE %s ADD SchID integer NULL" % (transactions._meta.db_table),
              "ALTER TABLE %s ADD NewType VARCHAR(3) NULL" % (transactions._meta.db_table),

        )
        batchSql(sqls)

        NewType = models.CharField(_('NewType'), max_length=3, null=True, blank=True)
        AbNormiteID = models.IntegerField(null=True, blank=True)
        SchID = models.IntegerField(_('Schclass'), null=True, blank=True)

        #	if settings.DATABASE_ENGINE == 'oracle':
    #		sqls=("ALTER TABLE %s ADD opStamp TIMESTAMP DEFAULT NULL"%(employee._meta.db_table),
    #		"ALTER TABLE %s ADD StartRestTime TIMESTAMP DEFAULT NULL"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD EndRestTime TIMESTAMP DEFAULT NULL"%(SchClass._meta.db_table),
    #		)
    #	elif settings.DATABASE_ENGINE == 'sql_server':
    #		sqls=("ALTER TABLE %s ADD opStamp datetime DEFAULT NULL"%(employee._meta.db_table),
    #		"ALTER TABLE %s ADD StartRestTime datetime DEFAULT NULL"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD EndRestTime datetime DEFAULT NULL"%(SchClass._meta.db_table),
    #		)
    #	else:
    #		sqls=("ALTER TABLE %s ADD opStamp datetime DEFAULT NULL"%(employee._meta.db_table),
    #		"ALTER TABLE %s ADD StartRestTime time DEFAULT NULL"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD EndRestTime time DEFAULT NULL"%(SchClass._meta.db_table),
    #		)
    #
    #	batchSql(sqls)
    #if dbVer<109:
    #	if settings.DATABASE_ENGINE == 'mysql':
    #		sqls=(
    #			"CREATE TABLE accounts(id int(11) NOT NULL AUTO_INCREMENT,StartTime  datetime NOT NULL,EndTime datetime NOT NULL,"\
    #			"Type int(11) NOT NULL,Status int(11) DEFAULT 0,  Reserved varchar(20) DEFAULT NULL,  User_id int(11) DEFAULT NULL,"\
    #			"PRIMARY KEY (`id`),  UNIQUE KEY StartTime (StartTime,EndTime,Type,Status),  KEY accounts_User_id (User_id)) ENGINE=MyISAM DEFAULT CHARSET=utf8",
    #		)
    #		batchSql(sqls)
    #	if settings.DATABASE_ENGINE == 'sql_server':
    #		sqls=(
    #			"CREATE TABLE accounts(id INT IDENTITY(1,1) NOT NULL ,"\
    #			"StartTime datetime NOT NULL,"\
    #			"EndTime datetime NOT NULL,Type int NOT NULL,Status int DEFAULT 0,Reserved varchar(20) NULL,User_id int NULL,PRIMARY KEY (id),"\
    #			"UNIQUE NONCLUSTERED (StartTime,EndTime,Type,Status),"\
    #			"FOREIGN KEY (User_id) REFERENCES auth_user(id))",
    #			)
    #		batchSql(sqls)
    #	if settings.DATABASE_ENGINE == 'oracle':
    #		sqls=(
    #		    '''CREATE TABLE "ACCOUNTS" ( "ID" NUMBER(11) NOT NULL PRIMARY KEY,"STARTTIME" TIMESTAMP NOT NULL,"ENDTIME" TIMESTAMP NOT NULL,"TYPE" NUMBER(11) NOT NULL,"STATUS" NUMBER(11) NULL,"RESERVED" NVARCHAR2(20) NULL,"USER_ID" NUMBER(11) NULL REFERENCES "AUTH_USER" ("ID") DEFERRABLE INITIALLY DEFERRED,UNIQUE ("STARTTIME", "ENDTIME", "TYPE", "STATUS"))''',
    #	   "DECLARE"\
    #		"   i INTEGER;"\
    #		"BEGIN"\
    #		"   SELECT COUNT(*) INTO i FROM USER_CATALOG"\
    #		"	   WHERE TABLE_NAME = 'ACCOUNTS_SQ' AND TABLE_TYPE = 'SEQUENCE';"\
    #		"   IF i = 0 THEN"\
    #		"	   EXECUTE IMMEDIATE 'CREATE SEQUENCE ACCOUNTS_SQ';"\
    #		"  END IF;"\
    #		"END;"\
    #		"/",
    #
    #		"CREATE OR REPLACE TRIGGER ACCOUNTS_TR"\
    #		"    BEFORE INSERT ON ACCOUNTS"\
    #		"    FOR EACH ROW"\
    #		"    WHEN (new.ID IS NULL)"\
    #		"   BEGIN"\
    #		"	   SELECT ACCOUNTS_SQ.nextval"\
    #		"	   INTO :new.ID FROM dual;"\
    #		"   END;"\
    #		"/",
    #					   )
    #
    #		batchSql(sqls)
    #	checkAndCreateModelPermissions(iclock._meta.app_label)
    #if dbVer<110:
    #	sqls=("ALTER TABLE %s ADD LeaveType integer DEFAULT 0"%(LeaveClass._meta.db_table),
    #	      "ALTER TABLE %s ADD  clearance integer DEFAULT NULL"%(LeaveClass._meta.db_table),
    #	      )
    #	batchSql(sqls)
    #if dbVer<111:
    #	sqls=("ALTER TABLE %s ADD Type integer DEFAULT 0"%(attCalcLog._meta.db_table),
    #	      "update attcalclog set type=0",
    #	      "ALTER TABLE %s alter column  Checktype VARCHAR(5) "%(transactions._meta.db_table),
    #	      )
    #	#batchSql(sqls)
    #if dbVer<112:
    #	checkAndCreateModelPermissions(iclock._meta.app_label)
    #if dbVer<113:
    #	if settings.DATABASE_ENGINE == 'sql_server':
    #		sqls=("CREATE TABLE [iclock_iclockdept] ("\
    #			"[id] int IDENTITY (1, 1) NOT NULL PRIMARY KEY,"\
    #			"[SN_id] varchar(20) NOT NULL REFERENCES [iclock] ([SN]),"\
    #			"[dept_id] int NOT NULL REFERENCES [departments] ([DeptID]))",
    #			)
    #	elif settings.DATABASE_ENGINE == 'oracle':
    #		sqls=('''CREATE TABLE "ICLOCK_ICLOCKDEPT" ( "ID" NUMBER(11) NOT NULL PRIMARY KEY, "SN_ID" NVARCHAR2(20) NOT NULL REFERENCES "ICLOCK" ("SN") DEFERRABLE INITIALLY DEFERRED,"DEPT_ID" NUMBER(11) NOT NULL REFERENCES "DEPARTMENTS" ("DEPTID") DEFERRABLE INITIALLY DEFERRED)''',
    #			 )
    #	else:
    #		sqls=("CREATE TABLE iclock_iclockdept ("\
    #			  "id int(11) NOT NULL AUTO_INCREMENT,"\
    #			  "SN_id varchar(20) NOT NULL,"\
    #			  "dept_id int(11) NOT NULL,"\
    #			  "PRIMARY KEY (id),"\
    #				"FOREIGN KEY (SN_id) REFERENCES iclock (SN),"\
    #				"FOREIGN KEY (dept_id) REFERENCES departments (DeptID)) ENGINE=MyISAM DEFAULT CHARSET=utf8",
    #				)
    #
    #	batchSql(sqls)
    #
#	if dbVer<114:
#		if settings.DATABASE_ENGINE == 'mysql':
#			sqls=("ALTER TABLE %s modify column  badgenumber VARCHAR(24) "%(employee._meta.db_table),
#		      "ALTER TABLE %s modify column  street VARCHAR(80) "%(employee._meta.db_table),
#		      )
#		else:
#			sqls=("ALTER TABLE %s alter column  badgenumber VARCHAR(24) "%(employee._meta.db_table),
#			"ALTER TABLE %s alter column  street VARCHAR(80) "%(employee._meta.db_table),
#		      )
#		batchSql(sqls)
#		if settings.DATABASE_ENGINE == 'mysql':
#			sqls=("CREATE TABLE attpriReport(id int(11) NOT NULL AUTO_INCREMENT,userid int(11) NOT NULL,AttDate datetime NOT NULL,AttChkTime varchar(100) DEFAULT NULL,AttAddChkTime varchar(100) DEFAULT NULL,AttLeaveTime varchar(100) DEFAULT NULL,SchName varchar(100) DEFAULT NULL,OP int(11) DEFAULT NULL,Reserved varchar(50) DEFAULT NULL,PRIMARY KEY (id),UNIQUE KEY userid(userid,AttDate), KEY attpriReport_userid (userid)) ENGINE=MyISAM DEFAULT CHARSET=utf8"),
#		elif settings.DATABASE_ENGINE == 'sql_server':
#			sqls=("CREATE TABLE attpriReport(id INT IDENTITY NOT NULL,userid INT NOT NULL,AttDate DATETIME NOT NULL,AttChkTime VARCHAR (100) NULL,AttAddChkTime VARCHAR (100) NULL,AttLeaveTime VARCHAR (100) NULL,SchName VARCHAR (100) NULL,OP INT NULL,Reserved VARCHAR (50) NULL,PRIMARY KEY (id),UNIQUE (userid,AttDate),FOREIGN KEY (userid) REFERENCES userinfo (userid))"),
#		elif settings.DATABASE_ENGINE == 'oracle':
##			sqls=('''CREATE TABLE "ATTPRIREPORT" ("ID" NUMBER(11) NOT NULL PRIMARY KEY,"USERID" NUMBER(11) NOT NULL REFERENCES "USERINFO" ("USERID") DEFERRABLE INITIALLY DEFERRED,"ATTDATE" TIMESTAMP NOT NULL,"ATTCHKTIME" NVARCHAR2(100),"ATTADDCHKTIME" NVARCHAR2(100),"ATTLEAVETIME" NVARCHAR2(100),"SCHNAME" NVARCHAR2(100),"OP" NUMBER(11),"RESERVED" NVARCHAR2(50),UNIQUE ("USERID", "ATTDATE"));''',)
#			sqls=("CREATE TABLE ATTPRIREPORT (ID NUMBER(11) NOT NULL PRIMARY KEY,"\
#				"USERID NUMBER(11) NOT NULL REFERENCES USERINFO (USERID) DEFERRABLE INITIALLY DEFERRED,"\
#				"ATTDATE TIMESTAMP NOT NULL,"\
#				"ATTCHKTIME NVARCHAR2(100),"\
#				"ATTADDCHKTIME NVARCHAR2(100),"\
#				"ATTLEAVETIME NVARCHAR2(100),"\
#				"SCHNAME NVARCHAR2(100),"\
#				"OP NUMBER(11),"\
#				"RESERVED NVARCHAR2(50),"\
#				"UNIQUE (USERID, ATTDATE));",
#
#				"DECLARE"\
#				"    i INTEGER;"\
#				"BEGIN"\
#				"    SELECT COUNT(*) INTO i FROM USER_CATALOG"\
#				"        WHERE TABLE_NAME = 'ATTPRIREPORT_SQ' AND TABLE_TYPE = 'SEQUENCE';"\
#				"    IF i = 0 THEN"\
#				"        EXECUTE IMMEDIATE 'CREATE SEQUENCE ATTPRIREPORT_SQ';"\
#				"    END IF;"\
#				"END;"\
#				"/",
#
#				"CREATE OR REPLACE TRIGGER ATTPRIREPORT_TR"\
#				"    BEFORE INSERT ON ATTPRIREPORT"\
#				"    FOR EACH ROW"\
#				"    WHEN (new.ID IS NULL)"\
#				"    BEGIN"\
#				"        SELECT ATTPRIREPORT_SQ.nextval"\
#				"        INTO :new.ID FROM dual;"\
#				"    END;"\
#				"/",
#				)
#			
#		batchSql(sqls)
    #if dbVer<115:
    #	checkAndCreateModelPermissions(iclock._meta.app_label)
    #if dbVer<116:
    #	if settings.DATABASE_ENGINE=="mysql":
    #		sqls=("ALTER TABLE %s modify  object VARCHAR(100) NULL"%(adminLog._meta.db_table),
    #			  "ALTER TABLE %s ADD  UserSpedayID integer DEFAULT 0"%(AttException._meta.db_table),
    #			)
    #	elif settings.DATABASE_ENGINE == 'oracle':
    #		sqls=('''ALTER TABLE iclock_adminlog modify ("OBJECT" NVARCHAR2(100))''',
    #			 "ALTER TABLE %s ADD  UserSpedayID integer DEFAULT 0"%(AttException._meta.db_table),
    #			)
    #	else:
    #		sqls=("ALTER TABLE %s alter column  object VARCHAR(100) NULL"%(adminLog._meta.db_table),
    #			   "ALTER TABLE %s ADD  UserSpedayID integer DEFAULT 0"%(AttException._meta.db_table),
    #			)
    #
    #	batchSql(sqls)
    #if dbVer<200:
    #	if settings.DATABASE_ENGINE == 'oracle':
    #		sqls=("ALTER TABLE %s ADD StartRestTime1 TIMESTAMP DEFAULT NULL"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD EndRestTime1 TIMESTAMP DEFAULT NULL"%(SchClass._meta.db_table),
    #		)
    #	elif settings.DATABASE_ENGINE == 'sql_server':
    #		sqls=("ALTER TABLE %s ADD StartRestTime1 datetime DEFAULT NULL"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD EndRestTime1 datetime DEFAULT NULL"%(SchClass._meta.db_table),
    #		)
    #	else:
    #		sqls=("ALTER TABLE %s ADD StartRestTime1 time DEFAULT NULL"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD EndRestTime1 time DEFAULT NULL"%(SchClass._meta.db_table),
    #		)
    #	batchSql(sqls)
    #if dbVer<202:
    #	checkAndCreateModelPermissions(iclock._meta.app_label)
#	if dbVer<205:
#		sqls=("delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('import_employee'),
#			"delete from auth_permission where codename='%s'"%('import_employee'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('optionsDatabase_employee'),
#			"delete from auth_permission where codename='%s'"%('optionsDatabase_employee'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('clearObsoleteData_transaction'),
#			"delete from auth_permission where codename='%s'"%('clearObsoleteData_transaction'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('init_database'),
#			"delete from auth_permission where codename='%s'"%('init_database'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_user_temp_sch'),
#			"delete from auth_permission where codename='%s'"%('add_user_temp_sch'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_user_temp_sch'),
#			"delete from auth_permission where codename='%s'"%('delete_user_temp_sch'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_user_temp_sch'),
#			"delete from auth_permission where codename='%s'"%('change_user_temp_sch'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_useracprivilege'),
#			"delete from auth_permission where codename='%s'"%('change_useracprivilege'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('AuditedTrans_transaction'),
#			"delete from auth_permission where codename='%s'"%('AuditedTrans_transaction'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('definedReport_itemdefine'),
#			"delete from auth_permission where codename='%s'"%('definedReport_itemdefine'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('upgradefw_iclock'),
#			"delete from auth_permission where codename='%s'"%('upgradefw_iclock'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('copyudata_iclock'),
#			"delete from auth_permission where codename='%s'"%('copyudata_iclock'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('resetPwd_iclock'),
#			"delete from auth_permission where codename='%s'"%('resetPwd_iclock'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('restoreData_iclock'),
#			"delete from auth_permission where codename='%s'"%('restoreData_iclock'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_itemdefine'),
#			"delete from auth_permission where codename='%s'"%('add_itemdefine'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_itemdefine'),
#			"delete from auth_permission where codename='%s'"%('delete_itemdefine'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_itemdefine'),
#			"delete from auth_permission where codename='%s'"%('change_itemdefine'),
#			
#			)
#		batchSql(sqls)
#		checkAndCreateModelPermissions(iclock._meta.app_label)
#	if dbVer<500:
    #if dbVer<501:
    #	AttParam.objects.filter(ParaName__startswith='opt_check_').delete()
    #if dbVer<502:
    #	sqls=("ALTER TABLE %s ADD  ProductType integer DEFAULT 1"%(iclock._meta.db_table),
    #		"ALTER TABLE %s ADD  AlgVer integer DEFAULT 0"%(fptemp._meta.db_table),	)
    #
    #	batchSql(sqls)
    #if dbVer<503:
    #	sqls=("ALTER TABLE %s ADD Authentication integer DEFAULT 1"%(iclock._meta.db_table),)
    #	batchSql(sqls)
    #if dbVer<504:
    #	sqls=(" ALTER TABLE %s ADD  VerifyType integer DEFAULT 0"%(ACGroup._meta.db_table),
    #		  "ALTER TABLE %s ADD  HolidayValid integer DEFAULT 0"%(ACGroup._meta.db_table),)
    #	batchSql(sqls)
    #	checkAndCreateModelPermissions(iclock._meta.app_label)
#	if dbVer<505:
#		sqls=(
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_iaccdevitemdefine'),
#			"delete from auth_permission where codename='%s'"%('add_iaccdevitemdefine'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_iaccdevitemdefine'),
#			"delete from auth_permission where codename='%s'"%('delete_iaccdevitemdefine'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_iaccdevitemdefine'),
#			"delete from auth_permission where codename='%s'"%('change_iaccdevitemdefine'),
#			
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_iaccempitemdefine'),
#			"delete from auth_permission where codename='%s'"%('add_iaccempitemdefine'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_iaccempitemdefine'),
#			"delete from auth_permission where codename='%s'"%('delete_iaccempitemdefine'),
#			"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_iaccempitemdefine'),
#			"delete from auth_permission where codename='%s'"%('change_iaccempitemdefine'),
#			
#			)
#		batchSql(sqls)
#		checkAndCreateModelPermissions(iclock._meta.app_label)
    #if dbVer<507:
    #	sqls=("ALTER TABLE %s ADD isFace integer DEFAULT 0"%(iclock._meta.db_table),
    #		"ALTER TABLE %s ADD isFptemp integer DEFAULT 0"%(iclock._meta.db_table),
    #		"ALTER TABLE %s ADD isUSERPIC integer DEFAULT 0"%(iclock._meta.db_table),
    #		"ALTER TABLE %s ADD FaceAlgVer varchar(20) NULL"%(iclock._meta.db_table),
    #		"ALTER TABLE %s ADD faceNumber integer DEFAULT 0"%(iclock._meta.db_table),
    #		"ALTER TABLE %s ADD faceTempNumber integer DEFAULT 0"%(iclock._meta.db_table),
    #		"ALTER TABLE %s ADD pushver varchar(20) NULL"%(iclock._meta.db_table),
    #		"drop index USERFINGER on %s"%(fptemp._meta.db_table),
    #		"drop index userid on %s"%(fptemp._meta.db_table),
    #		"CREATE UNIQUE INDEX USERFINGER ON %s(USERID, FINGERID,ALGVER)"%(fptemp._meta.db_table),
    #		)
    #	batchSql(sqls)
    #	checkAndCreateModelPermissions(iclock._meta.app_label)
    #if dbVer<513:
    #	User=get_user_model()
    #
    #	sqls=("ALTER TABLE %s ADD AutheTimeDept integer DEFAULT NULL"%(User._meta.db_table),
    #		"ALTER TABLE %s ADD ophone varchar(30) NULL"%(User._meta.db_table),
    #		"ALTER TABLE %s ADD is_alldept bit"%(User._meta.db_table),
    #		"ALTER TABLE %s ADD is_public bit"%(User._meta.db_table),
    #		"ALTER TABLE %s ADD CheckInMins1 integer DEFAULT 120"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD CheckInMins2 integer DEFAULT 120"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD CheckOutMins1 integer DEFAULT 120"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD CheckOutMins2 integer DEFAULT 120"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD TimeZoneType integer DEFAULT 0"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD WorkTimeType integer DEFAULT 0"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD BeforeInMins integer DEFAULT 0"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD AfterInMins integer DEFAULT 0"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD IsCalcOverTime integer DEFAULT 0"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD OverTimeMins integer DEFAULT 0"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD NextDay integer DEFAULT 1"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD TimeZoneOfDept integer DEFAULT 0"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD isHidden integer DEFAULT 0"%(SchClass._meta.db_table),
    #		"ALTER TABLE %s ADD Num_RunOfDept integer DEFAULT 0"%(NUM_RUN._meta.db_table),
    #		)
    #	batchSql(sqls)
    ##if dbVer<514:
    #	from mysite.auth_code import auth_code
    #	SetParamValue('InstallDate',auth_code(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'ENCODE'))
    #
    #	#sqls=("ALTER TABLE %s ADD DeptNo integer DEFAULT NULL"%(department._meta.db_table),
    #	#	"ALTER TABLE %s ADD deptid integer DEFAULT 1"%(transactions._meta.db_table),
    #	 #     )
        #batchSql(sqls)
    #if dbVer<515:
    #	sqls=("ALTER TABLE %s ADD Educational varchar(2) DEFAULT NULL"%(employee._meta.db_table),
    #		"ALTER TABLE %s ADD Trialstarttime datetime DEFAULT NULL"%(employee._meta.db_table),
    #		"ALTER TABLE %s ADD Trialendtime datetime DEFAULT NULL"%(employee._meta.db_table),
    #		"ALTER TABLE %s ADD Startwork datetime DEFAULT NULL"%(employee._meta.db_table),
    #		"ALTER TABLE %s ADD Worktime datetime DEFAULT NULL"%(employee._meta.db_table),
    #		"ALTER TABLE %s ADD Contractstarttime datetime DEFAULT NULL"%(employee._meta.db_table),
    #		"ALTER TABLE %s ADD Contractendtime datetime DEFAULT NULL"%(employee._meta.db_table),
    #		"ALTER TABLE %s ADD Employeetype varchar(2) DEFAULT NULL"%(employee._meta.db_table),
    #	      )
    #	batchSql(sqls)

    #if dbVer<516:
    #	if settings.DATABASE_ENGINE=="mysql":
    #		sqls=( "ALTER TABLE %s ADD  DeptNumber varchar(40) not null"%(department._meta.db_table),
    #		    "ALTER TABLE %s modify  column DeptID int auto_increment"%(department._meta.db_table),
    #
    #			)
    #	elif settings.DATABASE_ENGINE == 'oracle':
    #		sqls=("ALTER TABLE %s modify Deptid int"%(department._meta.db_table),
    #			 "ALTER TABLE %s ADD  DeptNumber varchar(40) not null"%(department._meta.db_table),
    #			)
    #	else:
    #		sqls=(
    #		    "ALTER TABLE %s ADD  DeptNumber varchar(40)"%(department._meta.db_table),
    #		    "ALTER TABLE %s alter column  DeptID int IDENTITY (1, 1) NOT NULL"%(department._meta.db_table),
    #
    #			)
    #	batchSql(sqls)
    #	objs=department.objects.all()
    #	for o in objs:
    #	    o.DeptNumber=str(o.DeptID)
    #	    try:
    #		o.save()
    #	    except Exception,e:
    #		print "DeptNumber==",e,o.DeptID
    #if dbVer<517:
    #	sqls=("ALTER TABLE %s ADD roleLevel integer DEFAULT NULL"%(userRoles._meta.db_table),
    #	"ALTER TABLE %s ADD roleid integer"%(USER_OVERTIME._meta.db_table),
    #	"ALTER TABLE %s ADD roleid integer"%(USER_SPEDAY._meta.db_table),
    #	"ALTER TABLE %s ADD process varchar(80)"%(USER_OVERTIME._meta.db_table),
    #	"ALTER TABLE %s ADD process varchar(80)"%(USER_SPEDAY._meta.db_table),
    #	      )
    #	batchSql(sqls)
    #if dbVer<518:
    #	sqls=("ALTER TABLE %s ADD State integer DEFAULT 0"%(userRoles._meta.db_table),
    #		  )
    #	batchSql(sqls)
    #if dbVer<519:
    #	sqls=("ALTER TABLE %s ADD oldprocess varchar(80)"%(USER_OVERTIME._meta.db_table),
    #			"ALTER TABLE %s ADD oldprocess varchar(80)"%(USER_SPEDAY._meta.db_table),
    #		  )
    #	batchSql(sqls)
    #if dbVer<520:
    #	if settings.DATABASE_ENGINE=="mysql":
    #		sqls=( "ALTER TABLE %s modify column AUTHOR_id int DEFAULT NULL"%(ItemDefine._meta.db_table),
    #		    "ALTER TABLE %s ADD datest datetime DEFAULT NULL"%(USER_OF_RUN._meta.db_table),
    #
    #			)
    #	elif settings.DATABASE_ENGINE == 'oracle':
    #		sqls=(
    #		    "ALTER TABLE %s ADD  datest TIMESTAMP DEFAULT NULL"%(USER_OF_RUN._meta.db_table),
    #		    "ALTER TABLE %s modify column  author_id int  NULL"%(ItemDefine._meta.db_table),
    #			)
    #	else:
    #		sqls=(
    #		    "ALTER TABLE %s ADD  datest datetime DEFAULT NULL"%(USER_OF_RUN._meta.db_table),
    #		    "ALTER TABLE %s alter column  author_id int  NULL"%(ItemDefine._meta.db_table),
    #			)
    #	batchSql(sqls)
    #if dbVer<524:
    #	sqls=(
    #		"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_employeelog'),
    #		"delete from auth_permission where codename='%s'"%('change_employeelog'),
    #		"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_employeelog'),
    #		"delete from auth_permission where codename='%s'"%('add_employeelog'),
    #		"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_adminlog'),
    #		"delete from auth_permission where codename='%s'"%('add_adminlog'),
    #		"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_adminlog'),
    #		"delete from auth_permission where codename='%s'"%('change_adminlog'),
    #		)
    #	batchSql(sqls)
    #if dbVer<525:
    #	sqls=(
    #		"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('browse_user_temp_sch'),
    #		"delete from auth_permission where codename='%s'"%('browse_user_temp_sch'),
    #		)
    #	batchSql(sqls)

    #if dbVer<540 and dbVer>0:
    #	User=get_user_model()
    #
    #	sqls=(
    #	"ALTER TABLE %s ADD Purpose integer DEFAULT 0"%(iclock._meta.db_table),
    #	"ALTER TABLE %s ADD emp_pin varchar(30) null"%(User._meta.db_table),
    #	)
    #	#batchSql(sqls)
    #
    #	if settings.DATABASE_ENGINE=="mysql":
    #		sqls=(
    #		"ALTER TABLE %s CHANGE COLUMN templateid id  int(11) NOT NULL AUTO_INCREMENT FIRST"%(facetemp._meta.db_table),
    #		"ALTER TABLE %s CHANGE COLUMN templateid id  int(11) NOT NULL AUTO_INCREMENT FIRST"%(fptemp._meta.db_table),
    #		)
    #		#batchSql(sqls)
    #	elif 'sql_server' in settings.DATABASE_ENGINE:
    #		sqls=(
    #		"EXEC sp_rename '[facetemplate].[templateid]', 'id', 'COLUMN'",
    #		"EXEC sp_rename '[template].[templateid]', 'id', 'COLUMN'",
    #		)
    #		#batchSql(sqls)
    #	elif 'oracle' in settings.DATABASE_ENGINE:
    #		sqls=(
    #		"ALTER TABLE %s RENAME COLUMN TEMPLATEID TO ID"%(facetemp._meta.db_table.upper()),
    #		"ALTER TABLE %s RENAME COLUMN TEMPLATEID TO ID"%(fptemp._meta.db_table.upper()),
    #		)
    #		#batchSql(sqls)
    #elif dbVer<541:
    #	sqls=(
    #	"ALTER TABLE %s ADD roleid integer "%(checkexact._meta.db_table),
    #	"ALTER TABLE %s ADD process varchar(80) null"%(checkexact._meta.db_table),
    #	"ALTER TABLE %s ADD oldprocess varchar(80) null"%(checkexact._meta.db_table),
    #	"ALTER TABLE %s ADD processid integer"%(checkexact._meta.db_table),
    #	"ALTER TABLE %s ADD procSN integer"%(checkexact._meta.db_table),
    #	)
    #	batchSql(sqls)
    #elif dbVer<542:
    #	if settings.DATABASE_ENGINE=="mysql":
    #		sqls=( "ALTER TABLE %s modify column Overtime float DEFAULT 0"%(attShifts._meta.db_table),
    #		)
    #	elif 'sql_server' in settings.DATABASE_ENGINE:
    #		sqls=(
    #		"ALTER TABLE %s  ALTER COLUMN  OverTime float "%(attShifts._meta.db_table),
    #		)
    #		batchSql(sqls)
    #	elif 'oracle' in settings.DATABASE_ENGINE:
    #		pass
    #elif dbVer<543:
    #	from mysite.meeting.models import Meet_order,Meet
    #	if 'oracle' in settings.DATABASE_ENGINE:
    #		sqls=(
    #		    "ALTER TABLE %s ADD  lunchtimestr TIMESTAMP DEFAULT NULL"%(Meet_order._meta.db_table),
    #		    "ALTER TABLE %s ADD  lunchtimeend TIMESTAMP DEFAULT NULL"%(Meet_order._meta.db_table),
    #		    "ALTER TABLE %s ADD  lunchtimestr TIMESTAMP DEFAULT NULL"%(Meet._meta.db_table),
    #		    "ALTER TABLE %s ADD  lunchtimeend TIMESTAMP DEFAULT NULL"%(Meet._meta.db_table),
    #		)
    #	else:
    #		sqls=(
    #		"ALTER TABLE %s ADD lunchtimestr datetime DEFAULT NULL"%(Meet_order._meta.db_table),
    #		    "ALTER TABLE %s ADD lunchtimeend datetime DEFAULT NULL"%(Meet_order._meta.db_table),
    #		    "ALTER TABLE %s ADD lunchtimestr datetime DEFAULT NULL"%(Meet._meta.db_table),
    #		    "ALTER TABLE %s ADD lunchtimeend datetime DEFAULT NULL"%(Meet._meta.db_table),
    #		)
    #	batchSql(sqls)
    #elif dbVer<544:
    #	sqls=(
    #	"ALTER TABLE %s ADD pri integer "%(empofdevice._meta.db_table),
    #	)
    #	batchSql(sqls)
    #
    if dbVer<600:           #更新成最新版本号 要参看base\management\_init_.py中的upgradeDB
        SetParamValue('ADMSDBVersion','600')


try:
    settings.MAX_DEVICES_STATE=int(GetParamValue('Delay',30))+20
    if settings.MAX_DEVICES_STATE<=300:
        settings.MAX_DEVICES_STATE=320
except:
    pass


try:
    UpdateDatabase()    #配合models的对数据库的修改实现对数据库的相应更新
except Exception,e:
    print "updatedatabase=",e
    pass




settings.DEPTVERSION=GetParamValue('DEPTVERSION')
createDir(reportDir())
createDir(photoDir())

class employee_borrow(models.Model):
    id = models.AutoField(primary_key=True)
    userID = models.IntegerField(verbose_name=_(u'借调人员'),null=False)
    toDept = models.IntegerField(verbose_name=_(u'借调单位'),null=False)
    fromDept = models.IntegerField(verbose_name=_(u'被借调单位'),null=False,)
    toTitle = models.CharField(verbose_name=_(u'借调职位'),max_length=20,null=True,blank=True)
    fromTitle = models.CharField(verbose_name=_(u'被借调职位'),max_length=20,null=True,blank=True)
    toDate = models.DateTimeField(verbose_name=_(u'调至日期'),max_length=20,null=True,blank=True)
    fromDate = models.DateTimeField(verbose_name=_(u'借调日期'),max_length=20,null=True,blank=True)
    reason = models.CharField(verbose_name=_(u'借调原因'),max_length=100,null=True,blank=True)
    remark = models.CharField(verbose_name=_(u'备注'),max_length=80,null=True,blank=True)
    OpTime = models.DateTimeField(verbose_name=_(u'操作日期'),max_length=20,null=True,blank=True)
    state = models.IntegerField(verbose_name=_(u'状态'),null=False,editable=False,default=0)

    class Meta:
        verbose_name = _(u"人员借调")
        verbose_name_plural = _(u"人员借调")

    class Admin:
        search_fields = ['userID','fromDate', 'toDate']

    @staticmethod
    def colModels():
        ret=[{'name':'id','hidden':True,'frozen': True},
            {'name':'workcode','index':'userID','width':110,'search':True,'frozen':True,'label':unicode(_(u'考勤编号'))},
            {'name':'PIN', 'sortable':False, 'width': 100, 'label': unicode(_(u'工号')), 'frozen': True},
            {'name':'EName','sortable':False,'width':80,'label':unicode(employee._meta.get_field('EName').verbose_name),'frozen': True},
            {'name':'fromDeptID','index':'fromDept','width':85,'label':unicode(_(u'单位编号'))},
            {'name':'fromDeptName','sortable':False,'width':180,'label':unicode(_(u'单位名称'))},
            {'name':'toDeptID', 'sortable': False, 'width':85 , 'label': unicode(_(u'借调单位编号'))},
            {'name':'toDeptName', 'sortable': False, 'width': 180, 'label': unicode(_(u'借调单位'))},
            {'name':'fromTitle','sortable':False,'width':80,'search':False,'label':unicode(_(u'职位'))},
            {'name':'toTitle','sortable':False,'width':80,'label':unicode(_(u'借调职位'))},
            {'name':'fromDate','index':'fromDate','width':120,'label':unicode(_(u'借调日期'))},
            {'name':'toDate','width':120,'index':'toDate','label':unicode(_(u'调至日期'))},
            {'name':'reason', 'width': 150, 'sortable':False,'search': False,'label': unicode(_(u'借调原因'))},
            #{'name':'operate','search':False,'width':50,'sortable':False,'label':unicode(_(u'操作'))},
            {'name':'remark','sortable':False,'width':150,'label':unicode(_(u'备注'))},
            {'name':'OpTime','index':'OpTime','width':120,'label':unicode(_(u'操作时间'))},
            {'name':'state','index':'state','search':False,'width':60,'label':unicode(_(u'状态'))}
            ]
        return ret