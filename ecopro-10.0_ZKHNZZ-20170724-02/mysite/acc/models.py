#!/usr/bin/env python
#coding=utf-8

from django.db import models
from django.db.models import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
import datetime
from mysite.iclock.models import employee,iclock,holidays,getDevice,device_options




PUBLISHED=(
(0, "NOT SHARE"),
(1, "SHARE READ"),
(2, "SHARE READ/WRITE")
)




INOUT_CHOICES = (
        (0, _(u'入')), (1, _(u'出')),
)

READER_CHOICES = (
        (1, _(u'卡读头')), (2, _(u'指纹读头')),
)

LCHANNEL_CHOICES = (
    (0, _(u'通道1')),
    (1, _(u'通道2')),
    (2, _(u'通道3')),
    (3, _(u'通道4')),
    (4, _(u'通道5')),
    (5, _(u'通道6')),
    (6, _(u'通道7')),
    (7, _(u'通道8')),
)


#开门方式 即验证方式
OPENDOOR_CHOICES = (
        (3, _(u'仅密码')),
       (1, _(u'仅指纹')),
        (4, _(u'仅卡')),
        (11, _(u'卡加密码')),
           (6, _(u'卡或指纹')),
           (7, _(u'卡或密码')),
           (0, _(u'卡或密码或指纹')),
           (10, _(u'卡加指纹')),
        (21, _(u'指静脉')),
        (22, _(u'指静脉和密码')),
        (23, _(u'指静脉和卡')),
        (24, _(u'指静脉和卡和密码')),
)


OPENDOOR_CHOICES_DEFAULT = 6
#if get_option("IACCESS_5TO4"):
#    OPENDOOR_CHOICES_DEFAULT = 4
#else:
#    OPENDOOR_CHOICES_FINGERPRINT = (
#           (1, _(u'仅指纹')),
#           (6, _(u'卡或指纹')),
#           (10, _(u'卡加指纹')),
#       )
#    OPENDOOR_CHOICES += OPENDOOR_CHOICES_FINGERPRINT
#    OPENDOOR_CHOICES_DEFAULT = 6

STATUS_CHOICES = (
        (0, _(u'无')), (1, _(u'常闭')), (2, _(u'常开')),
)

IS_GLOBAL_ANTIPASSBACK = (
        (0, _(u'否')), (1, _(u'是')),
)

def get_event_point_name(item):
    event_point_name=item.event_point_name
    if item.event_no==6:
        if item.verify in [220,221]:
            return ''
        try:
            obj=linkage_trigger.objects.get(id=item.card_no)
            id=obj.linkage_inout_id
            obj=linkage_inout.objects.get(id=id)
            return u'门%s'%(obj.input_id)
        except:
            try:
                objs=AccDoor.objects.filter(device=item.Device,door_no=item.event_point_name)
                if objs:
                    event_point_name=u'%s(%s)'%(objs[0].door_name,objs[0].door_no)
            except:
                pass

            return event_point_name
        return event_point_name
    if item.event_no in [220,221]:
        return u'辅助输入%s'%(item.event_point_name)

    try:
        objs=AccDoor.objects.filter(device=item.SN,door_no=item.event_point_name)
        if objs:
            event_point_name=u'%s'%(objs[0].door_name)
    except Exception,e:
        pass
    return event_point_name




class zone(models.Model):
    code = models.CharField(_(u'区域编号'),blank=False,null=False,max_length=40,help_text=_(u'最大长度不超过40个字符,修改区域编号后不会改变设备所在的区域。'))
    name = models.CharField(_(u'区域名称'),max_length=40)
    remark = models.CharField(_(u'备注'), null=True, max_length=50, blank=True)
    parent = models.IntegerField(db_column="parent_id",verbose_name=_(u'上级区域'), null=False, blank=True, default=0)
    DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)
    def __unicode__(self):
        return unicode(u"%s"%(self.name))
    def parentname(id):
        if id.parent==0:
            return ''
        else:
            zones=zone.objects.filter(id=id.parent)
            if zones.count()>0:
                return zones[0].name
            else:
                return ''
    class Admin:
        list_display=("name","code", )
        search_fields=['code']
        @staticmethod
        def initial_data():
            if zone.objects.all().count()==0:
                zone(code=u'1',name=u'默认区域',parent=0).save()
    def save(self):
        try:
            obj=zone.objects.get(code=self.code,name=self.name)
            if obj.DelTag==1:
                obj.DelTag=0
                obj.remark=self.remark
                obj.parent=self.parent
                super(zone,obj).save()
            else:
                super(zone,self).save()

        except:
            super(zone,self).save()

    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'code','width':80,'label':unicode(zone._meta.get_field('code').verbose_name)},
                {'name':'name','width':200,'label':unicode(zone._meta.get_field('name').verbose_name)},
                {'name':'remark','width':240,'label':unicode(zone._meta.get_field('remark').verbose_name)},
                {'name':'parent','width':200,'label':unicode(zone._meta.get_field('parent').verbose_name)}
                ]
    class Meta:
        verbose_name = _(u"区域")
        unique_together=['code','name']


class ZoneAdmin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    code = models.ForeignKey(zone,null=False, blank=False)
    iscascadecheck=models.IntegerField(null=True, blank=True,editable=False,default=0)
    def __unicode__(self):
        return unicode(self.user)
    class Admin:
        list_display=("user","code", )
    class Meta:
        verbose_name=_("admin granted zone")
        verbose_name_plural=verbose_name
        unique_together = (("user", "code"),)

class IclockZone(models.Model):
    SN = models.ForeignKey(iclock)
    zone = models.ForeignKey(zone, verbose_name=_(u'区域'), null=False, blank=False)
    iscascadecheck=models.IntegerField(null=True, blank=True,editable=False,default=0)
    def __unicode__(self):
        return unicode(self.SN)
    class Admin:
        list_display=("SN","zone", )
    class Meta:
        verbose_name=_(u"区域")
        verbose_name_plural=verbose_name
        unique_together = (("SN", "zone"),)
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

class timezones(models.Model):
    Name=models.CharField(_(u'时间段名称'), max_length=30,null=False,blank=True)
    remark = models.CharField(_(u'备注'), null=True, max_length=70, blank=True)
    tz = models.TextField(u'时间',null=True,editable=True)
    DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)


    def __unicode__(self):
        return unicode(u"%s"%(self.Name))
    @staticmethod
    def objByID(id):
        try:
            act=timezones.objects.get(id=id)
        except:
            act=''
        return act
    def save(self):
        try:
            tz=timezones.objects.get(Name=self.Name)
            if tz.DelTag==1:
                tz.DelTag=0
                tz.tz=self.tz
                tz.remark=self.remark
                super(timezones,tz).save()
            else:
                super(timezones,self).save()
        except:
            super(timezones,self).save()
    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'tzid','sortable':False,'width':80,'label':unicode(_(u'编号'))},
                {'name':'Name','width':200,'label':unicode(timezones._meta.get_field('Name').verbose_name)},
                {'name':'remark','width':240,'label':unicode(timezones._meta.get_field('remark').verbose_name)}
             #   {'name':'details','sortable':False,'width':100,'label':unicode(_(u'操作'))}
                ]
    class Admin:
        search_fields=['Name']
        @staticmethod
        def initial_data():

            if timezones.objects.all().count()==0:
                tzs=''
                for i in range(10):
                    tzs=tzs+'00:00-23:59;00:00-00:00;00:00-00:00;'
                timezones(Name=u'%s'%_(u'24小时全天通行'),remark=u'%s'%_(u"不允许删除，可以修改"),tz=tzs,DelTag=0).save()


    class Meta:
        verbose_name=_('ACTimeZones-table')
        verbose_name_plural=verbose_name
        unique_together = ("Name","DelTag")

ACGroupS_CHOICES=(
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
        (6,'6'),
        (7,'7'),
        (8,'8'),
        (9,'9'),
        (10,'10'),
        (11,'11'),
        (12,'12'),
        (13,'13'),
        (14,'14'),
        (15,'15'),
        (16,'16'),
        (17,'17'),
        (18,'18'),
        (19,'19'),
        (20,'20'),
        (21,'21'),
        (22,'22'),
        (23,'23'),
        (24,'24'),
        (25,'25'),
        (26,'26'),
        (27,'27'),
        (28,'28'),
        (29,'29'),
        (30,'30'),
        (31,'31'),
        (32,'32'),
        (33,'33'),
        (34,'34'),
        (35,'35'),
        (36,'36'),
        (37,'37'),
        (38,'38'),
        (39,'39'),
        (40,'40'),
        (41,'41'),
        (42,'42'),
        (43,'43'),
        (44,'44'),
        (45,'45'),
        (46,'46'),
        (47,'47'),
        (48,'48'),
        (49,'49'),
        (50,'50'),
        (51,'51'),
        (52,'52'),
        (53,'53'),
        (54,'54'),
        (55,'55'),
        (56,'56'),
        (57,'57'),
        (58,'58'),
        (59,'59'),
        (60,'60'),
        (61,'61'),
        (62,'62'),
        (63,'63'),
        (64,'64'),
        (65,'65'),
        (66,'66'),
        (67,'67'),
        (68,'68'),
        (69,'69'),
        (70,'70'),
        (71,'71'),
        (72,'72'),
        (73,'73'),
        (74,'74'),
        (75,'75'),
        (76,'76'),
        (77,'77'),
        (78,'78'),
        (79,'79'),
        (80,'80'),
        (81,'81'),
        (82,'82'),
        (83,'83'),
        (84,'84'),
        (85,'85'),
        (86,'86'),
        (87,'87'),
        (88,'88'),
        (89,'89'),
        (90,'90'),
        (91,'91'),
        (92,'92'),
        (93,'93'),
        (94,'94'),
        (95,'95'),
        (96,'96'),
        (97,'97'),
        (98,'98'),
        (99,'99'),
)

ACUnlockCombS_CHOICES=(
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
        (6,'6'),
        (7,'7'),
        (8,'8'),
        (9,'9'),
        (10,'10'),
)
ACGroup_VerifyType=(#门禁验证方式
        (0,_('FP/PW/RF/FACE')),
        (1,_('FP')),
        (2,_('PIN')),
        (3,_('PW')),
        (4,_('RF')),
        (5,_('FP/PW')),
        (6,_('FP/RF')),
        (7,_('PW/RF')),
        (8,_('PIN&FP')),
        (9,_('FP&PW')),
        (10,_('FP&RF')),
        (11,_('PW&RF')),
        (12,_('FP&PW&RF')),
        (13,_('PIN&FP&PW')),
        (14,_('FP&RF/PIN')),
        (15,_('FACE')),
        (16,_('FACE&FP')),
        (17,_('FACE&PW')),
        (18,_('FACE&RF')),
        (19,_('FACE&FP&RF')),
        (20,_('FACE&FP&PW')),
)
BOOLEANS=((0,_("No")),(1,_("Yes")),)
AC_Group_BOOLEANS=((0,_(u"自定义时间段")),(1,_(u"使用组设置")),)

###该表未使用###
    ##门禁组类别设置表##
class ACGroup(models.Model):
    #GroupID=models.AutoField(primary_key=True,null=False, editable=False)
    GroupID=models.IntegerField(_('GroupID'),primary_key=True, editable=True,choices=ACGroupS_CHOICES)
    Name=models.CharField(_('ACGroup name'), max_length=30,null=True,blank=True)
    TimeZone1 = models.IntegerField(_('TimeZone1'),null=True, blank=True,default=0)
    TimeZone2 = models.IntegerField(_('TimeZone2'),null=True, blank=True,default=0)
    TimeZone3 = models.IntegerField(_('TimeZone3'),null=True,blank=True,default=0)
    VerifyType=models.IntegerField(_('VerifyType'), null=True,editable=True,default=0,choices=ACGroup_VerifyType)
    HolidayValid=models.SmallIntegerField(_("HolidayValid"), null=True,default=0, editable=True, choices=BOOLEANS)
    def __unicode__(self):
        return unicode(u"%s"%(self.Name))
    @staticmethod
    def objByID(id):
        if id==None: return None
        g=cache.get("%s_iclock_acgroup_%s"%(settings.UNIT,id))
        if g: return g
        g=ACGroup.objects.get(GroupID=id)
        if g:
            cache.set("%s_iclock_acgroup_%s"%(settings.UNIT,id),g)
        return g
    def save(self):
        cache.delete("%s_iclock_acgroup_%s"%(settings.UNIT,self.GroupID))
        super(ACGroup,self).save()
    def delete(self):
        cache.delete("%s_iclock_acgroup_%s"%(settings.UNIT,self.GroupID))
        super(ACGroup, self).delete()

    @staticmethod
    def colModels():
        return [
                #{'name':'GroupID','hidden':True},
                {'name':'GroupID','width':80,'label':unicode(ACGroup._meta.get_field('GroupID').verbose_name)},
                {'name':'Name','width':100,'label':unicode(ACGroup._meta.get_field('Name').verbose_name)},
                {'name':'TimeZone1','width':100,'label':unicode(ACGroup._meta.get_field('TimeZone1').verbose_name)},
                {'name':'TimeZone2','width':100,'label':unicode(ACGroup._meta.get_field('TimeZone2').verbose_name)},
                {'name':'TimeZone3','width':100,'label':unicode(ACGroup._meta.get_field('TimeZone3').verbose_name)},
                {'name':'VerifyType','width':100,'label':unicode(ACGroup._meta.get_field('VerifyType').verbose_name)},
                {'name':'HolidayValid','width':100,'label':unicode(ACGroup._meta.get_field('HolidayValid').verbose_name)}
                ]
    class Admin:
        search_fields=['Name']
    class Meta:
        db_table = 'ACGroup'
        verbose_name=_('ACGroup-table')
        verbose_name_plural=verbose_name

###该表未使用###
    ##开锁组合类别设置表##
class ACUnlockComb(models.Model):
    #UnlockCombID=models.AutoField(primary_key=True,null=False, editable=False)
    UnlockCombID=models.IntegerField(_('UnlockCombID'),primary_key=True,null=False, editable=True,choices=ACUnlockCombS_CHOICES)
    Name=models.CharField(_('ACUnlockComb name'), max_length=30,null=True,blank=True)
    Group01 = models.IntegerField(_('Group1'),null=True, blank=True)
    Group02 = models.IntegerField(_('Group2'),null=True, blank=True)
    Group03=models.IntegerField(_('Group3'),null=True,blank=True)
    Group04=models.IntegerField(_('Group4'),null=True,blank=True)
    Group05=models.IntegerField(_('Group5'),null=True,blank=True)

    def __unicode__(self):
        return unicode(u"%s"%(self.Name))
    @staticmethod
    def colModels():
        return [
                #{'name':'UnlockCombID','hidden':True},
                {'name':'UnlockCombID','width':80,'label':unicode(ACUnlockComb._meta.get_field('UnlockCombID').verbose_name)},
                {'name':'Name','width':100,'label':unicode(ACUnlockComb._meta.get_field('Name').verbose_name)},
                {'name':'Group01','width':100,'label':unicode(ACUnlockComb._meta.get_field('Group01').verbose_name)},
                {'name':'Group02','width':100,'label':unicode(ACUnlockComb._meta.get_field('Group02').verbose_name)},
                {'name':'Group03','width':100,'label':unicode(ACUnlockComb._meta.get_field('Group03').verbose_name)},
                {'name':'Group04','width':100,'label':unicode(ACUnlockComb._meta.get_field('Group04').verbose_name)},
                {'name':'Group05','width':100,'label':unicode(ACUnlockComb._meta.get_field('Group05').verbose_name)}
                ]
    class Admin:
        search_fields=['Name']
    class Meta:
        db_table = 'ACUnlockComb'
        verbose_name=_('ACUnlockComb-table')
        verbose_name_plural=verbose_name

###门禁组节假日时间段设置表##
#class ACCSetHoliday(models.Model):
#       id=models.AutoField(primary_key=True)
#       HolidayID=models.ForeignKey(holidays, db_column='HolidayID', verbose_name=_(u"假日"))
#       TimeZoneID = models.ForeignKey(timezones,  verbose_name=_(u"时段"))
#       EndTime = models.DateField(_('EndTime'), null=False, blank=False,editable=False)
#       Reserved=models.IntegerField(null=True,default=0,blank=True,editable=False)
#       Reserved1=models.FloatField(null=True,default=0,blank=True,editable=False)
#       Reserved2=models.CharField(max_length=30,null=False,editable=False)
#
#       def __unicode__(self):
#               return unicode(u"%s"%(self.id))
#       def save(self):
#               self.EndTime=self.HolidayID.StartTime+datetime.timedelta(self.HolidayID.Duration)
#               models.Model.save(self)
#       @staticmethod
#       def colModels():
#               return [{'name':'id','hidden':True},
#                               {'name':'HolidayID','index':'HolidayID__HolidayID','width':100,'label':unicode(_('HolidayID'))},
#                               {'name':'HolidayName','index':'HolidayID__HolidayName','width':100,'label':unicode(_('HolidayName'))},
#                               {'name':'StartTime','index':'HolidayID__StartTime','width':100,'label':unicode(_('StartTime'))},
#                               {'name':'EndTime','index':'HolidayID__EndTime','width':100,'label':unicode(_('EndTime'))},
#                               {'name':'TimeZoneID','index':'TimeZoneID__TimeZoneID','width':100,'label':unicode(_('TimeZone ID'))},
#                               {'name':'Name','index':'TimeZoneID__Name','width':100,'label':unicode(_('ACTimeZones name'))}
#
#                               ]
#
#       class Admin:
#               search_fields=['HolidayID__HolidayName']
#       class Meta:
#               db_table = 'ACCSetHoliday'
#               verbose_name=_('ACCSetHoliday-table')
#               verbose_name_plural=verbose_name
#               unique_together = (( 'HolidayID', 'TimeZoneID'),)

###该表未使用###
    ##门禁权限类别设置表##
class UserACPrivilege(models.Model):
    UserID = models.ForeignKey(employee,db_column='userid', null=False,editable=True, verbose_name=u"员工")
    ACGroupID=models.ForeignKey(ACGroup, db_column='GroupID', default=1,editable=True,verbose_name=u"门禁组")
    IsUseGroup=models.IntegerField(_("IsUseGroup"), null=True, default=0, editable=True, choices=AC_Group_BOOLEANS)
    TimeZone1 = models.IntegerField(_('TimeZone1'),null=True, blank=True,editable=True,default=0)
    TimeZone2 = models.IntegerField(_('TimeZone2'),null=True, blank=True,editable=True,default=0)
    TimeZone3=models.IntegerField(_('TimeZone3'),null=True,blank=True,editable=True,default=0)

    def __unicode__(self):
        return "%s"%(self.UserID.__unicode__())
    #@staticmethod
    #def objByID(id):
        #if id==None: return None
        #g=cache.get("%s_iclock_ACPrivilege_%s"%(settings.UNIT,id))
        #if g: return g
        #g=UserACPrivilege.objects.get(UserID=id)
        #if g:
            #cache.set("%s_iclock_ACPrivilege_%s"%(settings.UNIT,id),g)
        #return g
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    def acgroup(self): #cached acgroup
        try:
            return ACGroup.objByID(self.ACGroupID_id)
        except:
            return None
    def save(self):
        cache.delete("%s_iclock_ACPrivilege_%s"%(settings.UNIT,self.UserID_id))
        super(UserACPrivilege,self).save()

    def userDevice(self):
        snlist=UserACCDevice.objects.filter(UserID=self.UserID)#.values_list('SN')
        snstr=''
        for sn in snlist:
            snstr+="%s,"%(sn.SN)#','.join(snlist)
        return snstr
    def delete(self):
        cache.delete("%s_iclock_ACPrivilege_%s"%(settings.UNIT,self.UserID_id))
        super(UserACPrivilege, self).delete()
    @staticmethod
    def clear():
        UserAC=UserACPrivilege.objects.all()
        UserAC.delete()
        #for e in UserAC:
            #e.delete()

    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
                {'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN'))},
                        {'name':'EName','index':'UserID__EName','width':120,'label':unicode(_('EName'))},
                        {'name':'Name','index':'ACGroupID__Name','width':120,'label':unicode(_('ACGroup-table name'))},
                        {'name':'IsUseGroup','width':80,'label':unicode(UserACPrivilege._meta.get_field('IsUseGroup').verbose_name)},
                        {'name':'TimeZone1','width':80,'label':unicode(UserACPrivilege._meta.get_field('TimeZone1').verbose_name)},
                        {'name':'TimeZone2','width':80,'label':unicode(UserACPrivilege._meta.get_field('TimeZone2').verbose_name)},
                        {'name':'TimeZone3','width':80,'label':unicode(UserACPrivilege._meta.get_field('TimeZone3').verbose_name)},
                        {'name':'SN','search':False,'sortable':False,'width':80,'label':unicode(_(u'设备列表'))}
                        #{'name':'SN','width':100,'label':unicode(UserACPrivilege._meta.userDevice())}
                        ]

    class Admin:
        lock_fields=['UserID']
        search_fields=['UserID__PIN','UserID__EName']
    class Meta:
        db_table = 'UserACPrivilege'
        verbose_name=_('UserACPrivilege-table')
        verbose_name_plural=verbose_name

###该表未使用###
    ##用户门禁设备类别设置表##
class UserACMachines(models.Model):
    id=models.AutoField(primary_key=True)
    UserID = models.ForeignKey(employee, db_column='userid', verbose_name=u"员工")
    SN = models.ForeignKey(iclock, db_column='SN', verbose_name=_('device'), null=False)

    def __unicode__(self):
        return unicode(u"%s"%(self.UserID))
    def Device(self):
        return getDevice(self.SN_id)
    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None
    def userACPrivilege(self):
        try:
            return UserACPrivilege.objByID(self.UserID_id)
        except:
            return None
    def delete(self):
        try:
            UserACPrivilege.objects.filter(UserID=self.UserID).delete()
        except Exception,e:
            print "====---%s"%e
        super(UserACMachines, self).delete()
    @staticmethod
    def clear():
        UserAC=UserACMachines.objects.all()
        for e in UserAC:
            e.delete()

    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
                        {'name':'PIN','index':'UserID__PIN','width':100,'label':unicode(_('PIN'))},
                        {'name':'EName','index':'','width':100,'label':unicode(_('EName'))},
                        {'name':'Name','index':'','width':100,'label':unicode(_('ACGroup-table name'))},
                        {'name':'IsUseGroup','width':80,'label':unicode(UserACPrivilege._meta.get_field('IsUseGroup').verbose_name)},
                        {'name':'TimeZone1','width':100,'label':unicode(UserACPrivilege._meta.get_field('TimeZone1').verbose_name)},
                        {'name':'TimeZone2','width':100,'label':unicode(UserACPrivilege._meta.get_field('TimeZone2').verbose_name)},
                        {'name':'TimeZone3','width':100,'label':unicode(UserACPrivilege._meta.get_field('TimeZone3').verbose_name)},
                        {'name':'Device','sortable':False,'width':100,'label':unicode(_('Device name'))}
                        ]

    class Admin:
        pass
    class Meta:
        db_table = 'UserACMachines'
        verbose_name=_('UserACMachines-table')
        verbose_name_plural=verbose_name
        unique_together = (('UserID', 'SN'),)

###该表未使用###
#人员与门禁设备关联表
class UserACCDevice(models.Model):
    id=models.AutoField(primary_key=True)
    UserID=models.ForeignKey(employee, db_column='UserID',  verbose_name=_(u"人员"))
    SN = models.ForeignKey(iclock, db_column='SN',  verbose_name=_(u"设备"))
    setTime = models.DateTimeField(_('SETTime'), null=True, blank=True)
    Reserved=models.IntegerField(null=True,default=0,blank=True,editable=False)
    Reserved1=models.FloatField(null=True,default=0,blank=True,editable=False)
    Reserved2=models.CharField(max_length=30,null=False,editable=False)

    def __unicode__(self):
        return unicode(u"%s"%(self.id))

    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
                        {'name':'PIN','index':'UserID__PIN','width':100,'label':unicode(_('PIN'))},
                        {'name':'EName','index':'UserID__EName','width':100,'label':unicode(_('Emp Name'))},
                        {'name':'DeptName','index':'UserID__DeptID__DeptName','width':100,'label':unicode(_('DeptName'))},
                        {'name':'SN','index':'SN__SN ','width':100,'label':unicode(_('serial number'))},
                        {'name':'Alias','index':'SN__Alias','width':100,'label':unicode(_('Device Alias name'))},
                        {'name':'IP','index':'SN__IPAddress','width':100,'label':unicode(_('IPAddress'))}

                        ]

    class Admin:
        pass
    class Meta:
        db_table = 'UserACCDevice'
        verbose_name=_('UserACCDevice-table')
        verbose_name_plural=verbose_name
        unique_together = (( 'UserID', 'SN'),)


###该表未使用###
#人员与门禁设备关联表  以后所有的下发门权限都从该表查询数据2017-03-14
class UserACDevice(models.Model):
    id=models.AutoField(primary_key=True)
    UserID=models.ForeignKey(employee, db_column='UserID',  verbose_name=_(u"人员"))
    Card=models.CharField(max_length=20,null=False,editable=False)
    SN = models.ForeignKey(iclock, db_column='SN',  verbose_name=_(u"设备"))
    door_no=models.IntegerField(null=True,default=0,blank=True,editable=False)
    TimezoneId=models.IntegerField(null=True,default=0,blank=True,editable=False)
    setTime = models.DateTimeField(null=True, blank=True)
    StartTime = models.DateTimeField( null=True, blank=True)
    EndTime = models.DateTimeField(null=True, blank=True)
    Reserved=models.CharField(max_length=30,null=False,editable=False)

    def __unicode__(self):
        return unicode(u"%s"%(self.id))

    #@staticmethod
    #def colModels():
    #       return [{'name':'id','hidden':True},
    #                       {'name':'PIN','index':'UserID__PIN','width':100,'label':unicode(_('PIN'))},
    #                       {'name':'EName','index':'UserID__EName','width':100,'label':unicode(_('Emp Name'))},
    #                       {'name':'DeptName','index':'UserID__DeptID__DeptName','width':100,'label':unicode(_('DeptName'))},
    #                       {'name':'SN','index':'SN__SN ','width':100,'label':unicode(_('serial number'))},
    #                       {'name':'Alias','index':'SN__Alias','width':100,'label':unicode(_('Device Alias name'))},
    #                       {'name':'IP','index':'SN__IPAddress','width':100,'label':unicode(_('IPAddress'))}
    #
    #                       ]

    class Admin:
        pass
    class Meta:
        verbose_name=_('UserACDevice-table')
        verbose_name_plural=verbose_name
        unique_together = (( 'UserID', 'SN','door_no','TimezoneId'),)


###该表未使用###
class IaccDevItemDefine(models.Model):
    ItemName=models.CharField(max_length=100,null=False)
    ItemType=models.CharField(max_length=20,null=True)
    Author=models.ForeignKey(settings.AUTH_USER_MODEL, null=False)
    ItemValue=models.TextField(max_length=100*1024,null=True)
    Published=models.IntegerField(null=True, choices=PUBLISHED, default=0)
    class Admin:
        pass
    class Meta:
        verbose_name=_("iaccdevitemdefine")
        verbose_name_plural=_("iaccdevitemdefine")
        db_table='iaccdevitemdefine'
        unique_together = (("ItemName","Author","ItemType"),)
        permissions = (
                                ('iaccMonitor_iaccdevitemdefine','iaccMonitor iaccdevitemdefine'),#监控记录表
                                ('iaccAlarm_iaccdevitemdefine','iaccAlarm iaccdevitemdefine'),#报警记录表
                                ('iaccUserRights_iaccdevitemdefine','iaccUserRights iaccdevitemdefine'),#用户权限表
        )
###该表未使用###
class IaccEmpItemDefine(models.Model):
    ItemName=models.CharField(max_length=100,null=False)
    ItemType=models.CharField(max_length=20,null=True)
    Author=models.ForeignKey(settings.AUTH_USER_MODEL, null=False)
    ItemValue=models.TextField(max_length=100*1024,null=True)
    Published=models.IntegerField(null=True, choices=PUBLISHED, default=0)
    class Admin:
        pass
    class Meta:
        verbose_name=_("iaccempitemdefine")
        verbose_name_plural=_("iaccempitemdefine")
        db_table='iaccempitemdefine'
        unique_together = (("ItemName","Author","ItemType"),)
        permissions = (
                                ('iaccRecordDetails_iaccempitemdefine','iaccRecordDetails iaccempitemdefine'),#记录明细
                                ('iaccSummaryRecord_iaccempitemdefine','iaccSummaryRecord iaccempitemdefine'),#记录汇总
                                ('iaccEmpUserRights_iaccempitemdefine','iaccEmpUserRights iaccempitemdefine'),#用户权限明细
                                ('iaccEmpDevice_iaccempitemdefine','iaccEmpDevice iaccempitemdefine'),#用户设备
        )

LEVEL_TYPE_CHOICES =(
    (0,_(u'门禁权限组')),
)


class AccMap(models.Model):
    """
    电子地图 top和left均为0
    """
    map_name = models.CharField(_(u'地图名称'), max_length=30, null=True, blank=False, default="", unique=True)
    map_path = models.CharField(_(u'地图路径'), max_length=30, null=True, blank=True, default="", editable=True)#路径
    #area = AreaForeignKey(verbose_name=_(u'所属区域'), null=True, blank=False, editable=True)# default=1,
    width = models.FloatField(_(u'宽度'), null=True, blank=True, default=0, editable=False)#单位px 0为无效值
    height = models.FloatField(_(u'高度'), null=True, blank=True, default=0, editable=False)#px 0为无效值
    mulriple = models.IntegerField(_(u'倍数'), null=True, blank=True, default=5, editable=False)
    def __unicode__(self):
        return self.map_name
    class Admin:
        pass


class AccWiegandFmt(models.Model):
    u"""
    韦根卡格式
    """
    wiegand_name = models.CharField(_(u'韦根卡格式名称'), null=False, max_length=30, blank=False, default="")
    wiegand_count = models.IntegerField(_(u'总位数'), null=True, blank=True, editable=True)
    odd_start = models.IntegerField(_(u'奇校验开始位'), null=True, blank=True, editable=True)
    odd_count = models.IntegerField(_(u'奇校验结束位'), null=True, blank=True, editable=True)
    even_start = models.IntegerField(_(u'偶校验开始位'), null=True, blank=True, editable=True)
    even_count = models.IntegerField(_(u'偶校验结束位'), null=True, blank=True, editable=True)
    cid_start = models.IntegerField(_(u'CID开始位'), null=True, blank=True, editable=True)#CID (Character identifier)就是字符识别码 or control id
    cid_count = models.IntegerField(_(u'CID结束位'), null=True, blank=True, editable=True)
    comp_start = models.IntegerField(_(u'公司码开始位'), null=True, blank=True, editable=True)
    comp_count = models.IntegerField(_(u'公司码结束位'), null=True, blank=True, editable=True)

    def __unicode__(self):
        return self.wiegand_name
    class Admin:
        list_display=("name","code", )
        search_fields=['code']
        @staticmethod
        def initial_data():
            if AccWiegandFmt.objects.all().count()==0:
                AccWiegandFmt(wiegand_name=_(u'自动匹配'),wiegand_count=26,odd_start=1,odd_count=10,even_start=11,even_count=26).save()
                AccWiegandFmt(wiegand_name=_(u'WIEGAND26'),wiegand_count=34,odd_start=1,odd_count=10,even_start=11,even_count=34).save()

                AccWiegandFmt(wiegand_name=_(u'WIEGAND26a'),wiegand_count=26,odd_start=1,odd_count=10,even_start=11,even_count=26).save()
                AccWiegandFmt(wiegand_name=_(u'WIEGAND34'),wiegand_count=34,odd_start=1,odd_count=10,even_start=11,even_count=34).save()
                AccWiegandFmt(wiegand_name=_(u'WIEGAND34a'),wiegand_count=34,odd_start=1,odd_count=10,even_start=11,even_count=34).save()
                AccWiegandFmt(wiegand_name=_(u'WIEGAND36'),wiegand_count=34,odd_start=1,odd_count=10,even_start=11,even_count=34).save()
                AccWiegandFmt(wiegand_name=_(u'WIEGAND37'),wiegand_count=34,odd_start=1,odd_count=10,even_start=11,even_count=34).save()
                AccWiegandFmt(wiegand_name=_(u'WIEGAND37a'),wiegand_count=34,odd_start=1,odd_count=10,even_start=11,even_count=34).save()
                AccWiegandFmt(wiegand_name=_(u'WIEGAND50'),wiegand_count=34,odd_start=1,odd_count=10,even_start=11,even_count=34).save()
                AccWiegandFmt(wiegand_name=_(u'WIEGAND66'),wiegand_count=34,odd_start=1,odd_count=10,even_start=11,even_count=34).save()

    class Meta:
        db_table = 'acc_wiegandfmt'
        verbose_name = _(u'韦根卡格式')
        verbose_name_plural = verbose_name

"""
Door1InTimeAPB:比如设置10分钟，刷卡进去了，又出去了，没超过10分钟是不让进的,暂未实现
"""
class AccDoor(models.Model):
    u"""门表"""
    device = models.ForeignKey(iclock, verbose_name=_(u'设备名称'),  help_text=_(u'不允许修改'),editable=True, null=True, blank=False)
    door_no = models.IntegerField(_(u'门编号'), null=True, blank=False, help_text=_(u'不允许修改'),editable=True)
    door_name = models.CharField(_(u'门名称'), null=True, max_length=30, blank=False, default="")
    lock_delay = models.IntegerField(_(u'锁驱动时长'), help_text=_(u'秒(范围0-254,0代表常闭)'), default=5, null=True, blank=False, editable=True)#锁驱动时长
    back_lock = models.NullBooleanField(_(u'闭门回锁'), null=True,blank=True,default=True, editable=True)
    door_sensor_status = models.IntegerField(_(u'门磁类型'),help_text=_(u'门磁类型为无时，门磁延时不可编辑'), default=0, null=True, blank=False, editable=True, choices=STATUS_CHOICES)
    sensor_delay = models.IntegerField(_(u'门磁延时'), help_text=_(u'秒(范围1-254),门磁延时需大于锁驱动时长'), default=15, null=True, blank=True, editable=True)#门开超时---门磁报警延时
    opendoor_type = models.IntegerField(_(u'验证方式'), null=True, default=OPENDOOR_CHOICES_DEFAULT, blank=False, editable=True, choices=OPENDOOR_CHOICES)#
    #inout_state = models.IntegerField(_(u'出入状态'), default=0, null=True, blank=True, editable=True, choices=INOUT_CHOICES)#该字段暂时废弃 当前已写死
    lock_active = models.ForeignKey(timezones, verbose_name=_(u'门有效时间段'),    related_name='lockactive_set',blank=False, editable=True, null=True,default=1)#default=0,
    long_open = models.ForeignKey(timezones, verbose_name=_(u'门常开时间段'),  blank=True, related_name='longopen_set',help_text=_(u'当门一直处于常开状态时，在该时间段内连续刷卡五次可以解除门常开状态。'), editable=True, null=True)#default=0,
    wiegand_fmt = models.ForeignKey(AccWiegandFmt, verbose_name=_(u'韦根卡格式') ,  null=True, blank=False, editable=True,default=1)#default=0,
    card_intervaltime = models.IntegerField(_(u'刷卡间隔'), help_text=_(u'秒(范围:0-254,0表示无间隔)'), default=1, null=True, blank=False, editable=True)
    reader_type = models.IntegerField(_(u'读头类型'), default=0, null=True, blank=True, editable=True, choices=READER_CHOICES)
    is_att = models.IntegerField(_(u'考勤'), blank=True, null=True,editable=False)
    #force_pwd = models.CharField(_(u'胁迫密码'), help_text=_(u'(最大8位整数)'), null=True, max_length=8, blank=True, default="")
    force_pwd = models.CharField(_(u'胁迫密码'), help_text=_(u'(最大8位整数)'), null=True, max_length=18, blank=True, default="")#存储加密后的密码，将字段的最大长度增加为128
    #supper_pwd = models.CharField(_(u'紧急状态密码'), help_text=_(u'(最大8位整数)'), null=True, max_length=8, blank=True, default="")
    supper_pwd = models.CharField(_(u'紧急状态密码'), help_text=_(u'(最大8位整数)'), null=True, max_length=18, blank=True, default="")#存储加密后的密码，将字段的最大长度增加为128
    #video_linkageio = models.ForeignKey(Device, verbose_name=_(u'硬盘录像机'), related_name='videoserver_set', null=True, blank=True, editable=True)
    #lchannel_num = models.SmallIntegerField(_(u'绑定通道'), default=0, null=True, blank=True, editable=True, choices=LCHANNEL_CHOICES)
    imap = models.ForeignKey(AccMap, verbose_name=_(u'所属地图'), null=True, blank=True, editable=False)#当前门所属地图
    duration_apb = models.IntegerField(_(u'入反潜时长'), help_text=_(u'分(5-120)'), default=0, null=True, blank=True, editable=False)#反潜时长
    global_apb = models.IntegerField(_(u'启用区域反潜'), blank=True, null=True,editable=False, choices=IS_GLOBAL_ANTIPASSBACK)


    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'door_name','width':150,'label':unicode(AccDoor._meta.get_field('door_name').verbose_name)},
                {'name':'door_no','sortable':False,'width':50,'align':'center','label':unicode(AccDoor._meta.get_field('door_no').verbose_name)},
                {'name':'device','sortable':False,'width':150,'label':unicode(AccDoor._meta.get_field('device').verbose_name)},
                {'name':'lock_active','sortable':False,'width':100,'label':unicode(AccDoor._meta.get_field('lock_active').verbose_name)},
                {'name':'opendoor_type','sortable':False,'width':60,'label':unicode(AccDoor._meta.get_field('opendoor_type').verbose_name)},
                {'name':'firstOpenCount','sortable':False,'width':70,'label':unicode(_(u'首人常开'))},
                {'name':'combOpenCount','sortable':False,'width':90,'label':unicode(_(u'多人开门'))}
                ]

    def __unicode__(self):
        return self.door_name
    class Admin:
        lock_fields=["device"]
        #to_text_fields=["device","door_no"]
        search_fields = ['door_name']

    class Meta:
        db_table = 'acc_door'
        verbose_name = _(u'门')
        verbose_name_plural = verbose_name
        unique_together = ["device","door_no"]

    #对密码进行加密
    #def encrypt_password(self,password):
    #   return encryption(password)
    #
    #def check_password(self, raw_password,password):
    #   password = decryption(password)
    #   if raw_password == password:return True
    #   else: return False
    def save(self, *args, **kwargs):


        if self.door_sensor_status == 0:
            self.back_lock = 0#False
            self.sensor_delay = None

        # if self.force_pwd!="" or None:
        #    if accdoor[0].force_pwd == self.force_pwd:
        #        pass
        #    else:
        #        self.force_pwd = self.encrypt_password(self.force_pwd)
        #if self.supper_pwd!="" or None:
        #    if accdoor[0].supper_pwd == self.supper_pwd:
        #        pass
        #    else:
        #        self.supper_pwd = self.encrypt_password(self.supper_pwd)


        super(AccDoor, self).save(*args, **kwargs)

    def firstOpenCount(self):
        firstopen = FirstOpen.objects.filter(door=self).count()
        if firstopen:
            return u'已设置'
        else:
            return u'未设置'

    def combOpenCount(self):
        #combopen_doors = combopen_door.objects.filter(door_id=self).values_list('id',flat=True)
        #combopen_combs = combopen_comb.objects.filter(combopen_door__in=combopen_doors).aggregate(Sum('opener_number'))['opener_number__sum']

        combopen_doors = combopen_door.objects.filter(door_id=self).count()
        if combopen_doors:
            return u'已设置'
        else:
            return u'未设置'


class AuxIn(models.Model):
    u"""输入"""
    device = models.ForeignKey(iclock, verbose_name=_(u'设备名称'),  help_text=_(u'不允许修改'),editable=True, null=True, blank=False)
    aux_no = models.IntegerField(_(u'编号'), null=True, blank=False, help_text=_(u'不允许修改'),editable=True)
    aux_name = models.CharField(_(u'名称'), null=True, max_length=30, blank=False, default="")
    printer_name = models.CharField(_(u'丝印名称'), null=True, max_length=30, blank=False, default="")
    remark = models.CharField(_(u'备注'), max_length=20, null=True, blank=True)


    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'aux_name','width':150,'label':unicode(AuxIn._meta.get_field('aux_name').verbose_name)},
                {'name':'device','sortable':False,'width':150,'label':unicode(AuxIn._meta.get_field('device').verbose_name)},
                {'name':'aux_no','sortable':False,'width':60,'align':'center','label':unicode(AuxIn._meta.get_field('aux_no').verbose_name)},
                {'name':'printer_name','sortable':False,'width':100,'label':unicode(AuxIn._meta.get_field('printer_name').verbose_name)},
                {'name':'remark','sortable':False,'width':100,'label':unicode(AuxIn._meta.get_field('remark').verbose_name)}
                ]

    def __unicode__(self):
        return self.aux_name
    class Admin:
        lock_fields=['device']

    class Meta:
        verbose_name = _(u'输入')
        verbose_name_plural = verbose_name
        unique_together = (("device",'aux_no'),)

    #对密码进行加密
    #def encrypt_password(self,password):
    #   return encryption(password)
    #
    #def check_password(self, raw_password,password):
    #   password = decryption(password)
    #   if raw_password == password:return True
    #   else: return False
    def save(self, *args, **kwargs):



        # if self.force_pwd!="" or None:
        #    if accdoor[0].force_pwd == self.force_pwd:
        #        pass
        #    else:
        #        self.force_pwd = self.encrypt_password(self.force_pwd)
        #if self.supper_pwd!="" or None:
        #    if accdoor[0].supper_pwd == self.supper_pwd:
        #        pass
        #    else:
        #        self.supper_pwd = self.encrypt_password(self.supper_pwd)


        super(AuxIn, self).save(*args, **kwargs)

class AuxOut(models.Model):
    u"""输出"""
    device = models.ForeignKey(iclock, verbose_name=_(u'设备名称'),  help_text=_(u'不允许修改'),editable=True, null=True, blank=False)
    aux_no = models.IntegerField(_(u'编号'), null=True, blank=False, help_text=_(u'不允许修改'),editable=True)
    aux_name = models.CharField(_(u'名称'), null=True, max_length=30, blank=False, default="")
    printer_name = models.CharField(_(u'丝印名称'), null=True, max_length=30, blank=False, default="")
    remark = models.CharField(_(u'备注'), max_length=20, null=True, blank=True)


    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'aux_name','width':150,'label':unicode(AuxOut._meta.get_field('aux_name').verbose_name)},
                {'name':'device','sortable':False,'width':150,'label':unicode(AuxOut._meta.get_field('device').verbose_name)},
                {'name':'aux_no','sortable':False,'width':60,'align':'center','label':unicode(AuxOut._meta.get_field('aux_no').verbose_name)},
                {'name':'printer_name','sortable':False,'width':100,'label':unicode(AuxOut._meta.get_field('printer_name').verbose_name)},
                {'name':'remark','sortable':False,'width':100,'label':unicode(AuxOut._meta.get_field('remark').verbose_name)}
                ]

    def __unicode__(self):
        return self.aux_name
    class Admin:
        lock_fields=['device']

    class Meta:
        verbose_name = _(u'输入')
        verbose_name_plural = verbose_name
        unique_together = (("device",'aux_no'),)

    #对密码进行加密
    #def encrypt_password(self,password):
    #   return encryption(password)
    #
    #def check_password(self, raw_password,password):
    #   password = decryption(password)
    #   if raw_password == password:return True
    #   else: return False
    def save(self, *args, **kwargs):



        # if self.force_pwd!="" or None:
        #    if accdoor[0].force_pwd == self.force_pwd:
        #        pass
        #    else:
        #        self.force_pwd = self.encrypt_password(self.force_pwd)
        #if self.supper_pwd!="" or None:
        #    if accdoor[0].supper_pwd == self.supper_pwd:
        #        pass
        #    else:
        #        self.supper_pwd = self.encrypt_password(self.supper_pwd)


        super(AuxOut, self).save(*args, **kwargs)


class level(models.Model):
    name = models.CharField(_(u'权限组名称'),max_length=30, blank=False, null=False)
    timeseg = models.ForeignKey(timezones, verbose_name=_(u'时间段'), null=False, blank=False, editable=True)
    itype = models.IntegerField(_(u'权限组类型'), choices=LEVEL_TYPE_CHOICES, default=0, null=True, blank=True, editable=False)
    is_visitor = models.IntegerField(_(u'访客门禁权限组'), default=0, choices=BOOLEANS, editable=False)
    irange = models.IntegerField(default=0, null=True, blank=True, editable=False) #特殊标记，当为-1时表示控制所有门，在leavel_door中不再保存门明细
    #        DelTag = models.IntegerField(default=0, editable=False, null=True, blank=True)
    def __unicode__(self):
        return self.name

    class Admin:
        search_fields=['name']
    class Meta:
        verbose_name=_(u"门禁权限组")
        verbose_name_plural=_("AccLevel")
        unique_together = (("name",),)
        permissions = (
                                ('addemps_level','Add emps'),
                                ('delallemps_level','Delete allemps'),
        )
    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'name','width':200,'label':unicode(level._meta.get_field('name').verbose_name)},
                {'name':'TimeZone','sortable':False,'width':300,'label':unicode(level._meta.get_field('timeseg').verbose_name)},
                {'name':'doors','sortable':False,'align':'center','width':100,'label':unicode(_(u'控制门数'))},
                {'name':'emps','sortable':False,'align':'center','width':100,'label':unicode(_(u'相关人员数'))},
                {'name':'action','sortable':False,'width':100,'label':unicode(_(u'操作'))}
                ]
    def save(self, *args, **kwargs):
        super(level, self).save(*args, **kwargs)
    def doorCount(self):
        if self.irange==-1:
            return AccDoor.objects.filter(device__DelTag=0).count()
        return level_door.objects.filter(level=self.id).count()

    def empCount(self):
        return level_emp.objects.filter(level=self.id).exclude(UserID__OffDuty=1).exclude(UserID__DelTag=1).count()



class AccDoorMap(models.Model):
    """
    门所在位置表
    """
    imap = models.ForeignKey(AccMap, verbose_name=_(u'所属地图'), null=True, blank=True, editable=False)
    door = models.ForeignKey(AccDoor, verbose_name=_(u"门"), editable=True)
    left = models.CharField(u'左边距',max_length=40,null=True, blank=True)
    top= models.CharField(u'上边距',max_length=40,null=True, blank=True)

    def __unicode__(self):
        return unicode(self.code)
    class Admin:
        pass

class AccMap_zone(models.Model):
    """
    电子地图与区域表，一个地图可以包含多个区域也可以是区域的一部分
    """
    imap = models.ForeignKey(AccMap, verbose_name=_(u'所属地图'), null=True, blank=True, editable=False)
    code = models.ForeignKey(zone,null=False, blank=False)
    def __unicode__(self):
        return unicode(self.code)
    class Admin:
        pass

#门禁组人员明细
class level_emp(models.Model):
    level = models.ForeignKey(level, verbose_name=_(u"门禁组"), editable=False)
    UserID = models.ForeignKey(employee, verbose_name=_(u"门禁组人员"), editable=False)
    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
                {'name':'level','width':200,'index':'level__name','label':unicode(_(u'权限组'))},
                {'name':'PIN','index':'UserID__PIN','width':140,'label':unicode(_('PIN'))},
                {'name':'EName','sortable':False,'width':120,'label':unicode(employee._meta.get_field('EName').verbose_name)},
                {'name':'DeptName','sortable':False,'width':200,'label':unicode(_('department name'))},
                {'name':'level_detail','sortable':False,'width':120,'label':unicode(_(u'操作'))},
                ]
    class Admin:
        list_display=()
        search_fields = ['UserID__PIN','UserID__EName']
    class Meta:
        verbose_name=_(u'门禁人员')
        verbose_name_plural=_('level_emp')
        unique_together = (("level",'UserID'),)











#门禁组设备明细
class level_door(models.Model):
    level = models.ForeignKey(level, verbose_name=_(u"门禁组"), editable=False)
    door = models.ForeignKey(AccDoor, verbose_name=_(u"门"), editable=False)
    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
                {'name':'level','width':100,'index':'level__id','label':unicode(_(u'门禁编号'))},
                {'name':'level_detail','sortable':False,'width':120,'label':unicode(_(u'操作'))},
                ]
    class Admin:
        list_display=()
        search_fields = []
    class Meta:
        verbose_name=_(u'门禁人员')
        verbose_name_plural=_('level_emp')
        unique_together = (("level",'door'),)


EVENT_LOG_AS_ATT = [0, 1, 2, 3, 14, 15, 16, 17, 18, 19, 21, 22, 23, 26, 32, 35,203]#用来作为考勤用的实时监控记录。20110518 lhj 增加多卡开门事件作为考勤原始记录

#事件选项
#公共事件，即C3和inbio公共的。
EVENT_CHOICES = (
    (-1, _(u'无')),
    (0, _(u'正常刷卡开门')),#2
    (1, _(u'常开时间段内开门')),#1含门常开时段和首卡常开设置的开门时段 （开门后）
    (2, _(u'首人开门(刷卡)')),#2
    (3, _(u'多卡开门(刷卡)')),#2门打开
    (4, _(u'紧急状态密码开门')),#2
    (5, _(u'常开时间段开门')),
    (6, _(u'触发联动事件')),
    (7, _(u'取消报警')),#1远程开关门与扩展输出   ，至于远程开关门与扩展输出等动作执行后还有相应事件记录
    (8, _(u'远程开门')),#1
    (9, _(u'远程关门')),#1
    (10, _(u'禁用当天常开时间段')),#
    (11, _(u'启用当天常开时间段')),#
    (12, _(u'开启辅助输出')),#
    (13, _(u'关闭辅助输出')),#
    (14, _(u'正常按指纹开门')),
    (15, _(u'多卡开门(按指纹)')),
    (16, _(u'常开时间段内按指纹')),
    (17, _(u'卡加指纹开门')),
    (18, _(u'首卡开门(按指纹)')),
    (19, _(u'首卡开门(卡加指纹)')),
    (20, _(u'刷卡间隔太短')),#2
    (21, _(u'门非有效时间段(刷卡)')),#2
    (22, _(u'非法时间段')),#2！！！有权限但是时间段不对。当前时段无合法权限
    (23, _(u'非法访问')),#2当前时段无此门权限----卡已注册，但是没有该门的权限
    (24, _(u'反潜')),#1
    (25, _(u'互锁未通过')),#1
    (26, _(u'多卡验证(刷卡)')),#刷卡
    #(27, _(u'卡未注册')),#2
    (27, _(u'人未登记')),#2
    (28, _(u'门开超时')),#1
    (29, _(u'卡已过有效期')),#2
    (30, _(u'密码错误')),
    (31, _(u'按指纹间隔太短')),
    (32, _(u'多卡验证(按指纹)')),
    (33, _(u'指纹已过有效期')),
#    (34, _(u'指纹未注册')),
    (34, _(u'人未登记')),
    (35, _(u'门非有效时间段(按指纹)')),
    (36, _(u'门非有效时间段(按出门按钮)')),#1
    (37, _(u'常开时间段无法关门')),#1
    (38, _(u'卡已挂失')),#1
    (39, _(u'黑名单')),#1
    (41, _(u'验证方式错误')),#2
    (42, _(u'韦根卡格式不对')),#2
    (44, _(u'反潜验证失败')),
    (48, _(u'多卡开门失败')),
    (100, _(u'防拆报警')),#1
    (101, _(u'胁迫密码开门')),#2
    (102, _(u'门被意外打开')),#1
    #(105, _(u'网络掉线')),

    (200, _(u'门已打开')),#1
    (201, _(u'门已关闭')),#1
    (202, _(u'出门按钮开门')),#1

    (204, _(u'常开时间段结束')),#1
    (205, _(u'远程开门常开')),#1
    (206, _(u'设备启动')),
    (207, _(u'密码开门')),
    (208, _(u'超级用户开门')),
    (209, _(u'触发出门按钮(被锁定)')),
    #(214, _(u'网络恢复')),

    (220, _(u'辅助输入点断开')),
    (221, _(u'辅助输入点短路')),
    (225, _(u'输入点恢复正常')),
    (226, _(u'输入点报警')),


    (222, _(u'反潜验证成功')),
    (223, _(u'反潜验证')),

)

VERIFYS=(
(3, _("Password")),
(1, _("Fingerprint")),
(4, _("Card")),#为控制器
(5, _("Add")),
(6, _(u'卡或指纹')),
(10, _(u'卡+指纹')),

(16, _("Other")),
(11, _(u"卡+密码")),#为控制器
(200,_(u'其他')),
(15,_("FACE")),
)
STATE_CHOICES = (
    (0, _(u'入')),
    (1, _(u'出')),
    (2, _(u'无')),
    #(2, _(u'未知或无或其他')),#即其他
)
def get_EVENT_CHOICES_name(key):
    for t in EVENT_CHOICES:
        if (t[0]==key):
            return u'%s'%t[1]
    return key
class records(models.Model):
    pin = models.CharField(_(u'工号'), max_length=24, null=True, blank=True)
    name = models.CharField(_(u'姓名'), max_length=24, null=True, blank=True)
    card_no = models.CharField(_(u'卡号'), max_length=10, null=True, blank=True)
    TTime = models.DateTimeField(_(u'时间'))
    inorout = models.IntegerField(_(u'进出'),null=True,choices=STATE_CHOICES)  # 门禁功能中表示进出
    verify = models.IntegerField(_(u'verification'),  null=True, choices=VERIFYS,default=200)
    SN = models.ForeignKey(iclock, verbose_name=_(u'device'), null=True, blank=True)
    #purpose = models.IntegerField(u'用途',null=True)#0考勤记录 1 会议记录    2 ...   3 ...
    event_no = models.IntegerField(_(u'事件描述'), null=True, choices=EVENT_CHOICES)
    eventaddr = models.CharField(_(u'work code'), max_length=30, null=True, blank=True)
    event_point_name = models.CharField(_(u'事件点'), max_length=30, null=True, blank=True)
    reader_name = models.CharField(_(u'读头名称'), max_length=30, null=True, blank=True)
    Reserved = models.CharField(_(u'Reserved'), max_length=20, null=True, blank=True)
    dev_serial_num = models.IntegerField(_(u'设备流水号'),null=True,blank=True)

    def employee(self): #cached employee
        try:
            if not self.pin or self.pin=='0':return ''
            return employee.objByPIN(self.pin)
        except Exception,e:
            #print "records==",e
            return ''
    def StrTime(self):
        return self.Time().strftime('%Y%m%d%H%M%S')
    @staticmethod
    def delOld(): return ("TTime", 365)
    def Device(self):
        return getDevice(self.SN_id)
    def __unicode__(self):
        return str(self.event_no)+', '+self.TTime.strftime("%y-%m-%d %H:%M:%S")
    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'TTime','width':120,'sortable':True,'search':False,'label':unicode(records._meta.get_field('TTime').verbose_name)},
                {'name':'Device','index':'SN','width':200,'label':unicode(_('Device name'))},
                {'name':'event_point','index':'','sortable':False,'width':80,'label':unicode(_(u'事件点'))},
                {'name':'event_no','width':80,'search':False,'label':unicode(records._meta.get_field('event_no').verbose_name)},
                {'name':'card_no','index':'','sortable':False,'width':80,'label':unicode(_(u'卡号'))},
                {'name':'pin','sortable':False,'width':120,'label':unicode(_(u'人员'))},
                {'name':'inorout','sortable':False,'width':60,'label':unicode(_(u'出入'))},
                {'name':'verify','width':70,'sortable':False,'search':False,'label':unicode(records._meta.get_field('verify').verbose_name)},
                {'name':'dev_serial_num','width':80,'sortable':False,'search':False,'label':unicode(records._meta.get_field('dev_serial_num').verbose_name)}
                ]
    class Meta:
        verbose_name=_(u"门禁记录")
        verbose_name_plural=_(u"门禁记录")
        unique_together = (("TTime","SN","dev_serial_num"),)
        permissions = (
                        ('monitor_oplog', 'Real Monitor'),
                        ('acc_records', 'Acc Records'),
                        ('acc_reports', 'Acc Reports'),
                        )

    class Admin:
        search_fields = ['pin','name']

INTERLOCK_CHOICES=(
(1, _(u"1-2两门互锁")),
(2, _(u"3-4两门互锁")),#为控制器
(3, _(u"1-2-3三门互锁")),

(4, _(u"1-2两门互锁和3-4两门互锁")),
(5,_(u"1-2-3-4四门互锁"))
)

class InterLock(models.Model):
    u"""
    互锁门 1-2、3-4、1-2 3-4,1-2-3,1-2-3-4
    """
    device = models.ForeignKey(iclock, verbose_name=_(u'设备'), editable=True, null=False, blank=False)
    interlock_rule = models.IntegerField(_(u'互锁规则'), null=True, blank=False)
    remark = models.CharField(_(u'备注'), max_length=20, null=True, blank=True)
    class Admin:
        search_fields=['device__SN']
        lock_fields=['device']
    class Meta:
        verbose_name=_(u"互锁规则")
        verbose_name_plural=_("interlock")
        unique_together = (("device", "interlock_rule"),)
        permissions = ()
    def __unicode__(self):
        return self.device.SN
    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'device','index':'device','width':180,'label':unicode(_('Device name'))},
                {'name':'interlock_rule','index':'','sortable':False,'width':200,'label':unicode(_(u'互锁规则'))},
                {'name':'remark','width':120,'sortable':False,'search':False,'label':unicode(InterLock._meta.get_field('remark').verbose_name)}
                ]

    def get_details(self):
        result = []
        #names=AccDoor.objects.filter(device=self.device).order_by('id').values_list('door_no','door_name')

        door_name_1 = 1#u'%s' % (names[0][0])
        door_name_2 = 2#u'%s' % (names[1][0])
        if self.interlock_rule==1:
            result.append(_(u"%(a)s - %(b)s 两门互锁") % {"a": door_name_1, "b": door_name_2})
        if self.device.LockFunOn == 4:
            door_name_3 = 3#u'%s' % ( names[2][0])
            door_name_4 = 4#u'%s' % (names[3][0])

        if self.interlock_rule==2:
            result.append(_(u"%(a)s - %(b)s 两门互锁") % {"a": door_name_3, "b": door_name_4})
        if self.interlock_rule==3:
            result.append(_(u"%(a)s - %(b)s - %(c)s 三门互锁") % {"a": door_name_1, "b": door_name_2, "c": door_name_3})
        if self.interlock_rule==4:
            result.append(_(u"%(a)s - %(b)s 两门互锁与 %(c)s - %(d)s两门互锁") % {"a": door_name_1, "b": door_name_2, "c": door_name_3, "d": door_name_4})

        if self.interlock_rule==5:
            result.append(_(u"%(a)s - %(b)s - %(c)s - %(d)s 四门互锁") % {"a": door_name_1, "b": door_name_2, "c": door_name_3, "d": door_name_4})
        return result and ','.join(result) or _(u'暂无互锁设置信息')




class  FirstOpen(models.Model):
    u"""首人常开"""
    door = models.ForeignKey(AccDoor, verbose_name=_(u'门名称'), default=1,editable=True, null=True)
    timeseg = models.ForeignKey(timezones, verbose_name=_(u'门禁时间段'), editable=True, null=True)#, default=1
    def __unicode__(self):
        return u"%s"% self.door

    def delete(self):
        #sync_delete_firstcard(self.door)
        super(FirstOpen, self).delete()
        #self.door.device.check_firstcard_options(self.door)
    class Meta:
        verbose_name = _(u'首人常开')
        verbose_name_plural = verbose_name
        unique_together = (("door",'timeseg'),)
    class Admin:
        lock_fields=['door']
        search_fields=['door__door_name']

    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
                {'name':'door','width':200,'index':'door','label':unicode(_(u'门名称'))},
                {'name':'device','sortable':False,'index':'','width':200,'label':unicode(_(u'设备名称'))},
                {'name':'timeseg','sortable':False,'width':120,'label':unicode(_(u'常开时间段'))},
                {'name':'empCount','sortable':False,'width':100,'label':unicode(_(u'人员数'))},
                {'name':'firstopen_detail','sortable':False,'width':120,'label':unicode(_(u'操作'))},
                ]
    def empCount(self):
        return FirstOpen_emp.objects.filter(firstopen=self).exclude(UserID__DelTag=1).count()

#首人常开人员明细
class FirstOpen_emp(models.Model):
    firstopen = models.ForeignKey(FirstOpen, verbose_name=_(u"门"), editable=False)
    UserID = models.ForeignKey(employee, verbose_name=_(u"人员"), editable=False)
    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
                {'name':'door','width':200,'index':'','sortable':False,'label':unicode(_(u'门名称'))},
                {'name':'device','width':200,'index':'','sortable':False,'label':unicode(_(u'设备名称'))},
                {'name':'PIN','index':'UserID__PIN','sortable':False,'width':100,'label':unicode(_('PIN'))},
                {'name':'EName','sortable':False,'width':80,'label':unicode(employee._meta.get_field('EName').verbose_name)},
                {'name':'Card','sortable':False,'width':80,'label':unicode(employee._meta.get_field('Card').verbose_name)},
                {'name':'DeptName','sortable':False,'width':200,'label':unicode(_('department name'))},
                {'name':'firstopen_details','sortable':False,'width':120,'label':unicode(_(u'操作'))},
                ]
    class Admin:
        list_display=()
        search_fields = []
    class Meta:
        verbose_name=_(u'首人常开人员')
        verbose_name_plural=_('FirstOpen_emp')
        unique_together = (("firstopen",'UserID'),)


class linkage(models.Model):
    u"""联动"""
    device = models.ForeignKey(iclock, verbose_name=_(u'设备名称'),  help_text=_(u'不允许修改'),editable=True, null=True, blank=False)
    name = models.CharField(_(u'联动名称'), null=True, max_length=30, blank=False, default="")
    remark = models.CharField(_(u'备注'), max_length=20, null=True, blank=True)
    class Admin:
        list_display=()
        search_fields = ['name']
        lock_fields=['device']

    class Meta:
        verbose_name=_(u'联动')
        verbose_name_plural=_('linkage')
        unique_together = (('name'),)
    def __unicode__(self):
        return u'%s(%s)'%(self.device.Alias,self.device.SN)
    def save(self, *args, **kwargs):
        super(linkage, self).save(*args, **kwargs)

    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'name','index':'','sortable':False,'width':200,'label':unicode(linkage._meta.get_field('name').verbose_name)},
                {'name':'device','index':'device','width':240,'label':unicode(_('Device name'))},
                {'name':'cond','index':'linkage_trigger','sortable':False,'width':240,'label':unicode(_(u'联动触发条件'))},
                {'name':'remark','width':120,'sortable':False,'search':False,'label':unicode(linkage._meta.get_field('remark').verbose_name)}
                ]


class linkage_inout(models.Model):
    u"""联动输入输出input_type:0-any  1-AccDoor  2-Reader  3-AuxIn     output_type:0-AccDoor 1-AuxOut"""
    linkage = models.ForeignKey(linkage,   help_text=_(u'不允许修改'),editable=True, null=True, blank=False)
    input_type = models.IntegerField( null=True, blank=False)
    input_id = models.IntegerField( null=True, blank=False)
    output_type = models.IntegerField( null=True, blank=False)
    output_id = models.IntegerField( null=True, blank=False)
    action_type = models.IntegerField( null=True, blank=False)
    action_time = models.IntegerField( null=True, blank=False)
    class Admin:
        list_display=()
        search_fields = []
    class Meta:
        verbose_name=_(u'联动')
        verbose_name_plural=_('linkage_inout')
        #unique_together = (("device",'name'),)
    def __unicode__(self):
        return self.linkage
    def save(self, *args, **kwargs):
        super(linkage_inout, self).save(*args, **kwargs)



class linkage_trigger(models.Model):
    u"""联动触发条件"""
    trigger_cond = models.IntegerField( null=True, blank=False)
    linkage_index = models.IntegerField( null=True, blank=False)
    linkage = models.ForeignKey(linkage, editable=True, null=True, blank=False)
    linkage_inout = models.ForeignKey(linkage_inout, editable=True, null=True, blank=False)

    def save(self, *args, **kwargs):
        super(linkage_trigger, self).save(*args, **kwargs)



    class Admin:
        list_display=()
        search_fields = []
    class Meta:
        verbose_name=_(u'联动')
        verbose_name_plural=_('linkage_trigger')
        #unique_together = (("device",'name'),)
    def __unicode__(self):
        return self.trigger_cond


class combopen(models.Model):
    u"""多人开门人员组"""
    name = models.CharField(_(u'开门人员组名称'), null=True, max_length=30, blank=False, default="")
    remark = models.CharField(_(u'备注'), max_length=20, null=True, blank=True)
    class Admin:
        list_display=()
        search_fields = ['name']

    class Meta:
        verbose_name=_(u'组名称')
        verbose_name_plural=_('combopen')
        unique_together = (('name'),)
    def __unicode__(self):
        return self.name
    def save(self, *args, **kwargs):
        super(combopen, self).save(*args, **kwargs)

    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'name','index':'','sortable':False,'width':200,'label':unicode(combopen._meta.get_field('name').verbose_name)},
                {'name':'empCount','sortable':False,'width':80,'label':unicode(_('EmpCount'))},
                {'name':'remark','width':120,'sortable':False,'search':False,'label':unicode(combopen._meta.get_field('remark').verbose_name)},
                {'name':'detail','sortable':False,'width':120,'label':unicode(_(u'操作'))}
                ]

    def empCount(self):
        return combopen_emp.objects.filter(combopen=self.id).exclude(UserID__DelTag=1).count()


#开门组合人员明细
class combopen_emp(models.Model):
    combopen = models.ForeignKey(combopen, verbose_name=_(u"开门组合"), editable=False)
    UserID = models.ForeignKey(employee, verbose_name=_(u"人员"), editable=False)
    @staticmethod
    def colModels():
        return  [
                        {'name':'id','hidden':True},
                        {'name':'PIN','index':'UserID__PIN','width':80,'label':unicode(employee._meta.get_field('PIN').verbose_name),'frozen':True},
                        {'name':'EName','sortable':False,'width':80,'label':unicode(employee._meta.get_field('EName').verbose_name),'frozen': True},
                        {'name':'DeptName','sortable':False,'index':'DeptID__DeptName','width':200,'label':unicode(_('department name'))},
                        {'name':'detail','sortable':False,'width':120,'label':unicode(_(u'操作'))}
                ]
    class Admin:
        list_display=()
        search_fields = ['UserID_PIN']
    class Meta:
        verbose_name=_(u'开门组合人员')
        verbose_name_plural=_('combopen_emp')
        unique_together = (("combopen",'UserID'),)

#开门组合
class combopen_door(models.Model):
    name = models.CharField(_(u'开门组合名称'),null=True, max_length=30, blank=False, default="")
    door = models.ForeignKey(AccDoor, verbose_name=_(u"门"), editable=True)
    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
                {'name':'name','width':100,'index':'name','label':unicode(_(u'开门组合名称'))},
                {'name':'door_no','sortable':False,'width':60,'align':'center','label':unicode(AccDoor._meta.get_field('door_no').verbose_name)},
                {'name':'door_name','index':'door','width':150,'label':unicode(AccDoor._meta.get_field('door_name').verbose_name)},
                {'name':'device','sortable':False,'width':150,'label':unicode(AccDoor._meta.get_field('device').verbose_name)},
                {'name':'detail','sortable':False,'width':120,'label':unicode(_(u'操作'))},
                ]
    class Admin:
        list_display=()
        search_fields = ['name']
        lock_fields=['door']

    class Meta:
        verbose_name=_(u'开门组合名称')
        verbose_name_plural=_('combopen_door')
        #unique_together = (("name",),)
    def device(self):
        return combopen_door.objects.get(id=self.id).door.device
#开门组合明细
class combopen_comb(models.Model):
    combopen = models.ForeignKey(combopen,  editable=False)
    combopen_door = models.ForeignKey(combopen_door, editable=False)
    opener_number = models.IntegerField( null=True, blank=False)
    sort = models.IntegerField( null=True, blank=False)


    class Admin:
        list_display=()
        search_fields = []
    class Meta:
        verbose_name=_(u'开门组合')
        verbose_name_plural=_('combopen_comb')

SUPER_AUTH = (
        (0, _(u'否')),
        (15, _(u'是')),
)

class acc_employee(models.Model):
    #门禁区
    UserID = models.ForeignKey(employee, verbose_name=_(u"人员"), editable=False)
    morecard_group = models.ForeignKey(combopen, verbose_name=_(u'多人开门人员组'), blank=True, editable=True, null=True)
    set_valid_time = models.BooleanField(_(u'设置有效时间'), default=False, null=False, blank=True)
    acc_startdate = models.DateTimeField(_(u'开始时间'), null=True, blank=True)
    acc_enddate = models.DateTimeField(_(u'结束时间'), null=True, blank=True)
    acc_super_auth = models.SmallIntegerField(_(u'超级用户'), default=0, null=True, blank=True, editable=True, choices=SUPER_AUTH)
    isblacklist = models.BooleanField(_(u'是否黑名单'), default=False,null=False, blank=True, editable=True)
    class Admin:
        list_display=()
        search_fields = []
    class Meta:
        verbose_name=_(u'门禁设置')
        verbose_name_plural=_('acc_employee')
        db_table='acc_employee'


#ONEDOOR_MODE = (
#    ('one_mode', _(u'1号门读头间反潜')),#单门双向（1）
#)
#
#TWODOORS_MODE = (
#    ('one_mode', _(u'1号门读头间反潜')),#两门双向（1）
#    ('two_mode', _(u'2号门读头间反潜')),#两门双向（2）
#    ('three_mode', _(u'1,2号门间反潜')),#两门双向（4）+ 两门单向（1）
#)
#
#FOURDOORS_MODE = (
#    ('one_mode', _(u'1-2门反潜')),#四门单向（1）
#    ('two_mode', _(u'3-4门反潜')),#四门单向（2）
#    ('three_mode', _(u'1/2-3/4门反潜')),#四门单向（4）
#    ('four_mode', _(u'1-2/3门反潜')),#四门单向（5）
#    ('five_mode', _(u'1-2/3/4门反潜')),#四门单向（6）

#)

#综上，五种mode只有four_mode可能存在多个值 ，1和4，即两门双向和四门单向为4，两门单向为1

class AntiPassBack(models.Model):
    u"""
    反潜 两门：1（1-1）、2（2-2）、(1-1，2-2)、1-2互锁 四门：1-2门反潜、3-4门反潜、（1-2 and 3-4）、1/2-3/4门反潜、1-2/3门反潜、1-2/3/4门反潜 ，单门：门自身反潜
    """
    device = models.ForeignKey(iclock, verbose_name=_(u'设备'), null=False, blank=False, editable=True)
    apb_rule = models.IntegerField(_(u'反潜模式'), null=True, blank=False, editable=True)

    def __unicode__(self):
        return _(u'设备 %s 的反潜信息') % self.device.Alias

    class Admin:
        list_display=()
        search_fields = []
        lock_fields=['device']
    class Meta:
        verbose_name=_(u'反潜设置')
        verbose_name_plural=_('antiback')
        #unique_together = (("device"),)
    def save(self, *args, **kwargs):
        super(AntiPassBack, self).save()
        from mysite.core.cmdproc import set_antipassback
        set_antipassback(self)
    def delete(self):
        from mysite.core.cmdproc import clear_antipassback
        clear_antipassback(self.device.SN)
        return super(AntiPassBack,self).delete()

    def getantibackoption(self):
        anti = 0#无反潜
        #if self.one_mode and self.two_mode: #双门双向
           # anti += 3
        #if self.one_mode:#单门双向，双门双向，四门单向
        #    anti += 1
        #if self.two_mode:
        #    anti += 2
        #if self.three_mode:
        #    #if self.device.accdevice.reader_count == 4:#两门双向+四门单向（均为四个读头）
        #    anti += 4
        #    #elif self.device.accdevice.reader_count == 2:#两门单向（两个读头，如C4-200）
        #       # anti = 1
        #if self.four_mode:
        #    anti += 5
        #if self.five_mode:
        #    anti += 6
        #if self.six_mode:
        #    anti += 16
        #if self.seven_mode:
        #    anti += 32
        #if self.eight_mode:
        #    anti += 64
        #if self.nine_mode:
        #    anti += 128
        anti=self.apb_rule
        return anti

    def get_details(self):
        result = []
        names=AccDoor.objects.filter(device=self.device).order_by('id').values_list('door_no','door_name')
        door_name_1 = u'%s(%s)' % (names[0][1], names[0][0])
        reader_Count=1
        if self.device.LockFunOn == 2:
            obj=device_options.objects.filter(SN=self.device,ParaName='ReaderCount')
            if obj:
                reader_Count=int(obj[0].ParaValue)
        if self.device.LockFunOn == 1:#单门双向
            if self.apb_rule==1:
                result.append(_(u"%s 读头间反潜") % door_name_1)

        elif self.device.LockFunOn == 2 and reader_Count == 4:#两门双向 含C4-200和C3400-200
            door_name_2 = u'%s(%s)' % (names[1][1], names[1][0])
            if self.apb_rule==1:
                result.append(_(u"%s 读头间反潜") % door_name_1)
            if self.apb_rule==2:
                result.append(_(u"%s 读头间反潜") % door_name_2)
            if self.apb_rule==3:
                result.append(_(u"%s 读头间反潜") % door_name_1)
                result.append(_(u"%s 读头间反潜") % door_name_2)

            if self.apb_rule==4:
                result.append(_(u"%(a)s 与 %(b)s 反潜") % {"a": door_name_1, "b": door_name_2})

        elif self.device.LockFunOn == 2 and reader_Count == 2:#两门单向
            door_name_2 = u'%s(%s)' % (names[1][1], names[1][0])
            if self.apb_rule==3:
                result.append(_(u"%(a)s 与 %(b)s 反潜") % {"a": door_name_1, "b": door_name_2})

        elif self.device.LockFunOn == 4:
            door_name_2 = u'%s(%s)' % (names[1][1], names[1][0])
            door_name_3 = u'%s(%s)' % (names[2][1], names[2][0])
            door_name_4 = u'%s(%s)' % (names[3][1], names[3][0])
            if self.apb_rule==1:
                result.append(_(u"%(a)s 与 %(b)s 反潜") % {"a": door_name_1, "b": door_name_2})
            if self.apb_rule==2:
                result.append(_(u"%(a)s 与 %(b)s 反潜") % {"a": door_name_3, "b": door_name_4})
            if self.apb_rule==3:
                result.append(_(u"%(a)s与%(b)s 或 %(c)s与%(d)s 反潜") % {"a": door_name_1, "b": door_name_2, "c": door_name_3, "d": door_name_4})
            if self.apb_rule==4:
                result.append(_(u"%(a)s 与 %(b)s或%(c)s 反潜") % {"a": door_name_1, "b": door_name_2, "c": door_name_3})
            if self.apb_rule==5:
                result.append(_(u"%(a)s 与 %(b)s或%(c)s或%(d)s 反潜") % {"a":door_name_1, "b": door_name_2, "c": door_name_3, "d": door_name_4})
            if self.apb_rule==6:
                result.append(_(u"%s 读头间反潜") % door_name_1)
            if self.apb_rule==7:
                result.append(_(u"%s 读头间反潜") % door_name_2)
            if self.apb_rule==8:
                result.append(_(u"%s 读头间反潜") % door_name_3)
            if self.apb_rule==9:
                result.append(_(u"%s 读头间反潜") % door_name_4)

        return result and u','.join(result) or _(u'暂无反潜设置信息')

    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
                {'name':'device','width':200,'index':'device','label':unicode(_(u'设备名称'))},
                {'name':'apb_rule','sortable':False,'width':400,'align':'center','label':unicode(AntiPassBack._meta.get_field('apb_rule').verbose_name)},
                {'name':'detail','sortable':False,'width':120,'label':unicode(_(u'操作'))},
                ]

        if interlock_rule==1:
            result.append()
        if self.device.LockFunOn == 4:
            door_name_3 = u'%s(%s)' % (names[2][1], names[2][0])
            door_name_4 = u'%s(%s)' % (names[3][1], names[3][0])

        if interlock_rule==2:
            result.append(_(u"%(a)s 与 %(b)s 互锁") % {"a": door_name_3, "b": door_name_4})
        if interlock_rule==3:
            result.append()
        if interlock_rule==4:
            result.append()
        return result and ','.join(result) or _(u'暂无互锁设置信息')

def getInterLockInfo(device):
    result = []
    #names=AccDoor.objects.filter(device=device).order_by('id').values_list('door_no','door_name')
    door_name_1 = 1#u'%s(%s)' % (names[0][1], names[0][0])
    door_name_2 = 2#u'%s(%s)' % (names[1][1], names[1][0])
    d={}
    d['id']=0
    d['name']='--------------------------'
    result.append(d.copy())
    if device.LockFunOn == 2:
        d['id']=1
        d['name']=_(u"%(a)s - %(b)s 两门互锁") % {"a": door_name_1, "b": door_name_2}
        result.append(d.copy())
    elif device.LockFunOn == 4:
        d['id']=1
        d['name']=_(u"%(a)s - %(b)s 两门互锁") % {"a": door_name_1, "b": door_name_2}
        result.append(d.copy())
        d['id']=2
        d['name']=_(u"%(a)s - %(b)s 两门互锁") % {"a": 3, "b": 4}
        result.append(d.copy())
        d['id']=3
        d['name']=_(u"%(a)s - %(b)s - %(c)s 三门互锁") % {"a": door_name_1, "b": door_name_2, "c": 3}
        result.append(d.copy())
        d['id']=4
        d['name']=_(u"%(a)s - %(b)s两门互锁,%(c)s - %(d)s 两门互锁") % {"a": door_name_1, "b": door_name_2, "c": 3,"d": 4}
        result.append(d.copy())


        d['id']=5
        d['name']=_(u"%(a)s - %(b)s - %(c)s - %(d)s 互锁") % {"a": door_name_1, "b": door_name_2, "c": 3, "d": 4}
        result.append(d.copy())
    return result


def getAntiPassBackInfo(device):
    result = []
    names=AccDoor.objects.filter(device=device).order_by('id').values_list('door_no','door_name')
    door_name_1 = u'%s(%s)' % (names[0][1], names[0][0])
    reader_Count=1
    d={}
    d['rule']=0
    d['name']='--------------------------'
    result.append(d.copy())
    if device.LockFunOn == 2:
        obj=device_options.objects.filter(SN=device,ParaName='ReaderCount')
        if obj:
            reader_Count=int(obj[0].ParaValue)
    if device.LockFunOn == 1:#单门双向
        d['rule']=1
        d['name']=_(u"%s 读头间反潜") % door_name_1
        result.append(d.copy())

    elif device.LockFunOn == 2 and reader_Count == 4:#两门双向 含C4-200和C3400-200
        door_name_2 = u'%s(%s)' % (names[1][1], names[1][0])
        d['rule']=1
        d['name']=_(u"%s 读头间反潜") % door_name_1
        result.append(d.copy())

        d['rule']=2
        d['name']=_(u"%s 读头间反潜") % door_name_2
        result.append(d.copy())

        d['rule']=3
        d['name']=_(u"%s 读头间反潜") % door_name_1+','+_(u"%s 读头间反潜") % door_name_2
        result.append(d.copy())

        d['rule']=4
        d['name']=_(u"%(a)s 与 %(b)s 反潜") % {"a": door_name_1, "b": door_name_2}
        result.append(d.copy())

    elif device.LockFunOn == 2 and reader_Count == 2:#两门单向
        door_name_2 = u'%s(%s)' % (names[1][1], names[1][0])
        d['rule']=4
        d['name']=_(u"%(a)s 与 %(b)s 反潜") % {"a": door_name_1, "b": door_name_2}
        result.append(d.copy())

    return result

class searchs(models.Model):
    SN = models.CharField(_('serial number'), max_length=20,null=False)
    Alias = models.CharField(_('Device Alias name'),max_length=20,null=True, blank=True)
    State = models.IntegerField(_(u'状态'),default=1, editable=False)
    Protype = models.CharField(max_length=10, null=True, blank=True, editable=False,help_text=_(u'通讯类型'))
    MAC = models.CharField(_('MAC'),max_length=20, null=True, blank=True,editable=False)
    IPAddress = models.CharField(_('IPAddress'),max_length=20, null=True, blank=True,editable=True)
    NetMask = models.CharField(_('NetMask'),max_length=20, null=True, blank=True,editable=True)
    GATEIPAddress = models.CharField(_('GATEIPAddress'),max_length=20, null=True, blank=True,editable=True)
    DeviceName = models.CharField(_('Device Name'),max_length=30, null=True, blank=True,editable=False)
    FWVersion = models.CharField(_('FW Version'),max_length=50, null=True, blank=True,editable=False)
    WebServerIP = models.CharField(_('WebServerIP'),max_length=20, null=True, blank=True,editable=True)
    WebServerURL = models.CharField(_('WebServerURL'),max_length=100, null=True, blank=True,editable=True)
    WebServerPort = models.CharField(_('WebServerPort'),max_length=20, null=True, blank=True,editable=True)
    IsSupportSSL = models.IntegerField(_('IsSupportSSL'), null=True, blank=True,editable=False,default=0)
    DNSFunOn = models.IntegerField(_('DNSFunOn'), null=True, blank=True,editable=False,default=0)
    DNS = models.CharField(_('WebServerURL'),max_length=100, null=True, blank=True,editable=True)
    OpStamp = models.DateTimeField(null=True, blank=True,editable=False)
    Style = models.CharField(_('style'),max_length=20, null=True, blank=True, default="", editable=False)#门禁中表示不同设备，见文件开头定义
    isAdd = models.IntegerField( null=True, blank=True,editable=False,default=0)
    Reserved = models.CharField(max_length=210,null=True, blank=True)

    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
                {'name':'SN','width':85,'label':unicode(_(u'序列号')),'frozen':True},
                {'name':'Alias','sortable':False,'width':100,'label':unicode(_(u'设备别名'))},
                {'name':'MAC','sortable':False,'width':100,'label':unicode(_(u'MAC地址'))},
                {'name':'IPAddress','width':90,'editable':True,'label':unicode(_(u'IP地址'))},
                {'name':'NetMask','sortable':False,'editable':True,'width':90,'label':unicode(_(u'子网掩码'))},
                {'name':'GATEIPAddress','width':90,'editable':True,'label':unicode(_(u'网关'))},
                {'name':'WebServerIP','width':100,'editable':True,'label':unicode(_(u'服务器IP'))},
                {'name':'WebServerPort','width':50,'editable':True,'label':unicode(_(u'端口号'))},
                {'name':'OP','width':150,'sortable':False,'label':unicode(_(u'操作'))},

                {'name':'WebServerURL','width':100,'label':unicode(_(u'服务器URL'))},
                {'name':'DeviceName','width':100,'label':unicode(_(u'设备名'))},
                {'name':'FWVersion','width':120,'label':unicode(_(u'固件版本'))},
                {'name':'State','sortable':False,'index':'State','width':60,'label':unicode(_(u'状态'))},
                #{'name':'IsSupportSSL','width':60,'label':unicode(_(u'支持SSL'))},
                {'name':'Protype','sortable':False,'width':80,'label':unicode(_(u'通讯类型'))},
                {'name':'DNSFunOn','width':60,'label':unicode(_(u'开启DNS'))},
                {'name':'isAdd','width':60,'label':unicode(_(u'已添加'))},
                {'name':'DNS','width':100,'label':unicode(_(u'DNS'))},
                {'name':'Reserved','width':500,'label':unicode(_(u'备注'))},
                ]

    class Admin:
        list_display=()
        search_fields = ['SN']

    class Meta:
        verbose_name=_(u'设备')
        verbose_name_plural=_('device')
        unique_together = (('SN'),)
    def __unicode__(self):
        return self.SN

    def getDynState(self):
        from mysite.iclock.models import DEV_STATUS_OFFLINE,DEV_STATUS_OK,DEV_STATUS_PAUSE
        try:
            if self.State==1:
                return DEV_STATUS_OK
            aObj=getDevice(self.SN)#cache.get("iclock_"+self.SN)
            if aObj:
                return aObj.getDynState()
            else:
                return DEV_STATUS_PAUSE

            if aObj and not aObj.LastActivity: return DEV_STATUS_OFFLINE
            if aObj and not self.LastActivity:self.LastActivity=aObj.LastActivity
            if aObj  and aObj.LastActivity>self.LastActivity:
                self.LastActivity=aObj.LastActivity
#               if self.SN in ["521463"]: print "LastActivity", self.LastActivity
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
            if self.State==1:
                return DEV_STATUS_OK
            return DEV_STATUS_OFFLINE
