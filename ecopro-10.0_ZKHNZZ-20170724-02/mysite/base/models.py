#!/usr/bin/env python
#coding=utf-8

from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
import datetime
from django.contrib.auth.models import  Permission, Group

AttRuleStrKeys=('CompanyLogo','CompanyName','ruleName','ApplyName')


def loadAttRuleByID(id):
        AttRule={
            'ruleID':0,
            'ruleName':u'%s'%(_(u'默认考勤规则')),
            'ApplyName':u'%s'%_(u'全部'),
            'DeptID':0,
            'CompanyLogo':'Our Company',
            'CompanyName' :'Our Company',
            #    'DBVersion' : '-1',
            'EarlyAbsent':0,                #一次早退大于   分钟记
            'LateAbsent':0,                 #一次迟到大于   分钟记
            'MaxShiftInterval':1440,         #最长的班次时间不超过
            'MinRecordInterval':5,            #最小的记录间隔
            'MinsEarly' : 0,                  #提前多少分钟记早退  作废，以时段为准
            'MinsLateAbsent':100,
            'MinsEarlyAbsent':100,            #早退大于的分钟
            'MinShiftInterval':120,          #最短的班次时段
            'MinsLate' : 0,                  #超过多长时间记迟到  作废，以时段为准
            'MinsNoIn' : 60,                  #无签到时记? 分钟
            'MinsNoOut' : 60,
            'MinsOutOverTime' : 60,		#下班后60分钟记加班 作废 以时段为准
            'MinsComeOverTime' : 60,	#上班前60分钟记加班  作废 以时段为准
            'MinsWorkDay' : 480,
            'MinsWorkDay1' : 0,            #计算用
            'NoInAbsent':1,                   #上班无签到
            'NoOutAbsent':1,
            'OTCheckRecType':2,               #加班状态
            'OutCheckRecType':3,
            'OutOverTime' :0,                 #下班后记加班
            'ComeOverTime' :0,                 #上班前记加班
            'TwoDay' : '0',
            'WorkMonthStartDay' : 1,
            'WorkWeekStartDay' : 1,
            'RealWorkNoLate':1#实到时间默认减去迟到早退
            }

        qryOptions=AttParam.objects.filter(ParaType='rule_%s'%id)
        for qryOpt in qryOptions:
            for k in AttRule.keys():
                if k==qryOpt.ParaName:
                    if qryOpt.ParaValue=='on':
                        AttRule[k]=1
                    elif k not in AttRuleStrKeys:
                        AttRule[k]=int(qryOpt.ParaValue)
                    else:
                        AttRule[k]=qryOpt.ParaValue
                    break
        return AttRule.copy()




    ##系统参数表##
class AttParam(models.Model):
    ParaName=models.CharField(_('Att parameter name'),max_length=30,null=False)
    ParaType=models.CharField(_('Att parameter type'),max_length=10,null=True)
    ParaValue=models.CharField(_('Att parameter value'),max_length=250,null=False)

    #获取考勤规则
    @staticmethod
    def LoadAttRule(reloadData=False):
        global AttRuleStrKeys
        if not reloadData:
            attrule=cache.get("%s_attrule"%(settings.UNIT))
            if attrule:return attrule
        AttRule=loadAttRuleByID(0)

        objs=attParamDepts.objects.all()
        dDict={}
        for t in objs:
            dDict[t.DeptID]=loadAttRuleByID(t.id)#以部门ID作键值，利于查询使用

        AttRule['customer']=dDict



        cache.set("%s_attrule"%(settings.UNIT),AttRule)
        return AttRule




    class Admin:
        @staticmethod
        def initial_data():
            if AttParam.objects.all().count()<5:
                from mysite.auth_code import auth_code
                authcode=auth_code(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'ENCODE')
                AttParam(ParaName='ruleID',ParaValue="0",ParaType='rule_0').save()
                AttParam(ParaName='DeptID',ParaValue="0",ParaType='rule_0').save()
                AttParam(ParaName='ApplyName',ParaValue=u"全部",ParaType='rule_0').save()
                AttParam(ParaName='ruleName',ParaValue=u"%s"%(_(u'默认考勤规则')),ParaType='rule_0').save()
                AttParam(ParaName='MinsEarly',ParaValue="0",ParaType='rule_0').save()
                AttParam(ParaName='MinsLate',ParaValue="0",ParaType='rule_0').save()
                AttParam(ParaName='MinsNoBreakIn',ParaValue="60",ParaType='rule_0').save()
                AttParam(ParaName='MinsNoBreakOut',ParaValue="60",ParaType='rule_0').save()
                AttParam(ParaName='MinsNoIn',ParaValue="60",ParaType='rule_0').save()
                AttParam(ParaName='MinsNoLeave',ParaValue="60",ParaType='rule_0').save()
                AttParam(ParaName='MinsNotOverTime',ParaValue="60",ParaType='rule_0').save()
                AttParam(ParaName='MinsWorkDay',ParaValue="480",ParaType='rule_0').save()
                AttParam(ParaName='NoBreakIn',ParaValue="1012",ParaType='rule_0').save()
                AttParam(ParaName='NoBreakOut',ParaValue="1012",ParaType='rule_0').save()
                AttParam(ParaName='NoIn',ParaValue="1001",ParaType='rule_0').save()
                AttParam(ParaName='NoLeave',ParaValue="1002",ParaType='rule_0').save()
                AttParam(ParaName='OutOverTime',ParaValue="0",ParaType='rule_0').save()
                AttParam(ParaName='TwoDay',ParaValue="0",ParaType='rule_0').save()
                AttParam(ParaName='CheckInColor',ParaValue="16777151",ParaType='rule_0').save()
                AttParam(ParaName='CheckOutColor',ParaValue="12910591",ParaType='rule_0').save()
                AttParam(ParaName='DBVersion',ParaValue="1000",ParaType='rule_0').save() #通过此参数大小区别新老版计算方法的不同
                AttParam(ParaName='InstallDate',ParaValue=authcode,ParaType='rule_0').save()
                AttParam(ParaName='ADMSDBVersion',ParaValue="544",ParaType='rule_0').save()
                f=file(settings.ADDITION_FILE_ROOT+"_sys.dat","w")
                f.write(authcode)
                f.close()


    class Meta:
        db_table = 'AttParam'
        verbose_name=_('attendance rule')
        verbose_name_plural=verbose_name
        unique_together = (("ParaName","ParaType"),)

    def save(self, *args, **kwargs):
        super(AttParam, self).save(*args, **kwargs)

#从attparam表中读取参数
def GetParamValue(PName,defaultvalue='1',PType=''):
    dbValue=defaultvalue
    #else:
    if PName not in ["opt_users_vis_pic","pos_sys_card_no","opt_users_rec_pic"]:
        # if PName!="pos_sys_card_no":
        p=cache.get("%s_%s_%s"%(settings.UNIT, PType,PName))
        # if PName!="opt_users_rec_pic":
        if p is not None:
            return p
    try:
        if PType=='':
            attP=AttParam.objects.filter(ParaName=PName)
        else:
            attP=AttParam.objects.filter(ParaName=PName,ParaType=PType)
            #if PName=='opt_basic_homeurl' and attP.count()==0:
                #attP=AttParam.objects.filter(ParaName=PName)
        if attP:
            if attP[0].ParaValue is not None:
                dbValue=attP[0].ParaValue
    except Exception,e:
        #print "GetParamValue=",e
        return -10000
    if PName=='DEPTVERSION':
        dbValue=datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    cache.set("%s_%s_%s"%(settings.UNIT,PType,PName),dbValue)
    return dbValue
def SetParamValue(PName,PValue,PType=''):
    try:
        if PName=='opt_basic_page_limit':
            try:
                p=int(PValue)
            except:
                return
        objs=AttParam.objects.filter(ParaName=PName,ParaType='%s'%(PType))
        if objs:
            objs[0].ParaValue=PValue
            objs[0].save(force_update=True)

        else:
            AttParam(ParaName=PName,ParaValue='%s'%(PValue),ParaType='%s'%(PType)).save(force_insert=True)
        cache.set("%s_%s_%s"%(settings.UNIT,PType,PName),PValue)
    except  Exception, e:
        #print "SetParamValue",e
        pass
        #print "SetParamValue==%s"%e
def DelParamValue(PName,PType=''):
    AttParam.objects.filter(ParaName=PName,ParaType=PType).delete()
    cache.delete("%s_%s_%s"%(settings.UNIT,PType, PName))
    if PName[:10]=='opt_check_':
        cache.delete("%s_%s"%(settings.UNIT, 'all_record_states'))

PURPOSE_CHOICE=(
    (0,_(u'会议通知')),
)


#规则应用部门表 
class attParamDepts(models.Model):
    ruleName=models.CharField(max_length=40,unique=True)
    DeptID = models.IntegerField(default=0)
    Operator = models.CharField(max_length=20,null=True, blank=True)
    OpTime=models.DateTimeField(null=True,  blank=True)
    class Admin:
        pass
    class Meta:
        verbose_name = _('attParamDepts')
        verbose_name_plural=verbose_name




class SendEmail(models.Model):
    purpose = models.IntegerField(_('purpose'),null=True, blank=True, choices=PURPOSE_CHOICE)
    EmailAddress = models.TextField(_('Content'),null=True,blank=True)
    EmailNotice = models.CharField(u'消息主题',max_length=40)
    EmailContent = models.TextField(_('Content'),null=True,blank=True)
    SendTime = models.DateTimeField(_(u'发送时间'),max_length=8, null=True, blank=True)
    SendTag = models.IntegerField(_(u'发送状态'),null=True, blank=True,)

    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True},
            {'name':'EmailAddress','width':100,'label':unicode(_(u'收件人地址'))},
            {'name':'EmailNotice','width':140,'label':unicode(_(u'主题'))},
            {'name':'EmailContent','sortable':False,'width':200,'label':unicode(SendEmail._meta.get_field('EmailContent').verbose_name)},
            {'name':'SendTime','sortable':False,'width':130,'label':unicode(_(u'发送时间'))},
            {'name':'purpose','sortable':False,'width':80,'label':unicode(_(u'邮件用途'))},
            {'name':'SendTag','sortable':False,'width':80,'label':unicode(_(u'发送状态'))},
        ]
    class Admin:
        list_display=()
        search_fields = []
    class Meta:
        verbose_name=_(u'邮件发送')
        verbose_name_plural=_('SendEmail')


def __permission_unicode__(self):
    ct_id=self.content_type_id
    ckey="%s_ct_%s"%(settings.UNIT,ct_id)
    ct=None#cache.get(ckey)
    #ct=None
    if not ct:
        ct=self.content_type
        cache.set(ckey, ct)

    #print  u"%s | %s | %s" % (unicode(ct.app_label),unicode(ct.model),unicode(self.codename))

    return u"%s | %s | %s" % (
    unicode(ct.app_label),
    unicode(ct.model),
    unicode(self.codename))

Permission.__unicode__=__permission_unicode__
