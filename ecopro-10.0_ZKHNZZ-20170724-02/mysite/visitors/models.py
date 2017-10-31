#!/usr/bin/env python
#coding=utf-8

from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from mysite.iclock.models import *
import datetime
# Create your models here.
class reason(models.Model):#来访事由表
    reasonNo = models.CharField(_(u'来访事由编码'),null=False,max_length=30)
    reasonName = models.CharField(u'来访事由',max_length=80)
    DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.reasonNo)
    class Admin:
        list_display=("reasonNo","reasonName" )
        search_fields = ['reasonNo','reasonName']
    class Meta:
        verbose_name=_(u"来访事由")
        verbose_name_plural=verbose_name
        unique_together = ("reasonNo","DelTag")
    def save(self):
        try:
            re=reason.objects.get(reasonNo=self.reasonNo)
            if re.DelTag==1:
                re.DelTag=0
                re.reasonName=self.reasonName
                super(reason,re).save()
            else:
                super(reason,self).save()
        except:
            super(reason,self).save()
        #self.DelTag=0
        #models.Model.save(self)
    @staticmethod
    def colModels():
        return [
            {'name':'id','hidden':True},
            {'name':'reasonNo','width':100,'label':unicode(reason._meta.get_field('reasonNo').verbose_name)},
            {'name':'reasonName','width':220,'label':unicode(reason._meta.get_field('reasonName').verbose_name)},
            ]

class reservation(models.Model):#预约访客登记
    visDate=models.DateTimeField(_(u'预来访时间'),null=True)
    visempName=models.CharField(_(u'访客姓名'),null=True,max_length=40)
    SSN=models.CharField(_(u'证件号'),max_length=20, null=True)
    visCompany=models.CharField(_(u'来访单位'),null=True,max_length=60,blank=True)
    VisitingNum = models.CharField(_(u'来访人数'),null=True,max_length=40,blank=True)
    InterviewedempName = models.CharField(_(u'拜访对象'),null=True,max_length=40,blank=True)
    VisitedCompany=models.CharField(_(u'拜访单位'),null=True,max_length=60,blank=True)
    visReason=models.CharField(_(u'来访事由'),null=True,max_length=80,blank=True)
    remark=models.CharField(_(u'备注'),null=True,blank=True,max_length=200)
    isvisited=models.NullBooleanField(_(u'已来访'),null=True,default=True,editable=False)
    DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)

    @staticmethod
    def colModels():
        return [{'name':'id','hidden':True,'frozen':True},
            {'name':'visDate','width':120,'label':unicode(reservation._meta.get_field('visDate').verbose_name),'frozen':True},
            {'name':'visempName','index':'visempName','width':140,'label':unicode(reservation._meta.get_field('visempName').verbose_name),'frozen':True},
            {'name':'SSN','index':'SSN','width':120,'label':unicode(reservation._meta.get_field('SSN').verbose_name)},
            {'name':'visCompany','width':120,'label':unicode(reservation._meta.get_field('visCompany').verbose_name)},
            {'name':'VisitingNum','width':80,'label':unicode(reservation._meta.get_field('VisitingNum').verbose_name)},
            {'name':'InterviewedempName','width':150,'label':unicode(reservation._meta.get_field('InterviewedempName').verbose_name)},
            {'name':'VisitedCompany','width':150,'label':unicode(reservation._meta.get_field('VisitedCompany').verbose_name)},
            {'name':'visReason','width':120,'label':unicode(reservation._meta.get_field('visReason').verbose_name)},
            {'name':'remark','width':120,'label':unicode(reservation._meta.get_field('remark').verbose_name)},
            #{'name':'isvisited','width':120,'label':unicode(reservation._meta.get_field('isvisited').verbose_name)},
            ]

    class Admin:
        list_display=("visempName","visempName","InterviewedempName" )
        search_fields = ['visempName','visempName','InterviewedempName']
    class Meta:
        verbose_name=_(u"预约访客")
        verbose_name_plural=verbose_name

NATIONAL_CHOICES=(
    ('01',_(u'汉族')),
    ('02',_(u'蒙古族')),
    ('03',_(u'回族')),
    ('04',_(u'藏族')),
    ('05',_(u'维吾尔族')),
    ('06',_(u'苗族')),
    ('07',_(u'彝族')),
    ('08',_(u'壮族')),
    ('09',_(u'布依族')),
    ('10',_(u'朝鲜族')),
    ('11',_(u'满族')),
    ('12',_(u'侗族')),
    ('13',_(u'瑶族')),
    ('14',_(u'白族')),
    ('15',_(u'土家族')),
    ('16',_(u'哈尼族')),
    ('17',_(u'哈萨克族')),
    ('18',_(u'傣族')),
    ('19',_(u'黎族')),
    ('20',_(u'傈僳族')),
    ('21',_(u'佤族')),
    ('22',_(u'畲族')),
    ('23',_(u'高山族')),
    ('24',_(u'拉祜族')),
    ('25',_(u'水族')),
    ('26',_(u'东乡族')),
    ('27',_(u'纳西族')),
    ('28',_(u'景颇族')),
    ('29',_(u'柯尔克孜族')),
    ('30',_(u'土族')),
    ('31',_(u'达斡尔族')),
    ('32',_(u'仫佬族')),
    ('33',_(u'羌族')),
    ('34',_(u'布朗族')),
    ('35',_(u'撒拉族')),
    ('36',_(u'毛南族')),
    ('37',_(u'仡佬族')),
    ('38',_(u'锡伯族')),
    ('39',_(u'阿昌族')),
    ('40',_(u'普米族')),
    ('41',_(u'塔吉克族')),
    ('42',_(u'怒族')),
    ('43',_(u'乌孜别克族')),
    ('44',_(u'俄罗斯族')),
    ('45',_(u'鄂温克族')),
    ('46',_(u'德昴族')),
    ('47',_(u'保安族')),
    ('48',_(u'裕固族')),
    ('49',_(u'京族')),
    ('50',_(u'塔塔尔族')),
    ('51',_(u'独龙族')),
    ('52',_(u'鄂伦春族')),
    ('53',_(u'赫哲族')),
    ('54',_(u'门巴族')),
    ('55',_(u'珞巴族')),
    ('56',_(u'基诺族')),
)

CertificateType_CHOICES=(
    ('0',_(u'一代身份证')),
    ('1',_(u'二代身份证')),
    ('2',_(u'防伪身份证')),
    ('3',_(u'驾照')),
    ('4',_(u'护照')),
)

VIS_STATES=(
    (0,_(u'已进入')),
    (1,_(u'已离开'))
)

class visitionlogs(models.Model):
    VisempName=models.CharField(_(u'访客姓名'),null=False,max_length=40)
    VisGender= models.CharField(_('sex'),max_length=2, choices=GENDER_CHOICES,default=0, null=True, blank=True)
    CertificateType = models.CharField(_(u'证件类别'),max_length=2,choices=CertificateType_CHOICES,default='1',null=True,blank=True)
    SSN=models.CharField(_(u'证件号码'),max_length=20, null=False)
    Card = models.CharField(_('ID Card'),max_length=20, null=True, blank=True, editable=True)
    National = models.CharField(_('nationality'),db_column="minzu",max_length=8, default='',null=True, blank=True)
    Birthday = models.DateTimeField(_('birthday'),max_length=8, null=True, blank=True)#help_text=unicode(_('Date format is '))+"ISO;"+unicode( _('for example'))+':1999-01-10/1999-1-11')
    Address = models.CharField(_('address'),db_column="street",max_length=80, null=True, blank=True)
    LicenseOrg = models.CharField(_(u'发证机关'),max_length=80, null=True, blank=True)
    VisCompany=models.CharField(_(u'来访单位'),null=True,max_length=60,blank=True)
    VisReason=models.CharField(_(u'来访事由'),null=True,max_length=80,blank=True)
    ValidDate = models.CharField(_(u'到期日期'),null=True,max_length=20,blank=True)
    #remark=models.CharField(_(u'备注'),null=True,blank=True,max_length=200)
    #进入信息
    InterviewedempName = models.CharField(_(u'拜访对象'),null=True,max_length=40,blank=True)
    VisitingNum = models.CharField(_(u'来访人数'),null=True,max_length=40,blank=True)
    Tele = models.CharField(_('office phone'),db_column="ophone",max_length=20, null=True, blank=True)
    VisitedCompany=models.CharField(_(u'拜访部门'),null=True,max_length=60,blank=True)
    EnterArticles = models.CharField(_(u'进入携带物品'),null=True,max_length=180,blank=True)
    #isvisited=models.NullBooleanField(_(u'已来访'),null=True,default=True,editable=True)
    EnterTime = models.DateTimeField(_(u'进入时间'),null=False,blank=True)
    ExitTime = models.DateTimeField(_(u'离开时间'),null=True,blank=True)
    ExitArticles = models.CharField(_(u'离开携带物品'),null=True,max_length=180,blank=True)
    Photourl=models.CharField(_(u'证件照片'),null=True,max_length=200,blank=True)
    Photourlz=models.CharField(_(u'抓拍照片'),null=True,max_length=200,blank=True)
    #Photourl1=models.TextField(_(u'照片'),null=True,blank=True)
    VisState = models.IntegerField(_(u'访问状态'), null=True, default=0, blank=True,choices=VIS_STATES,editable=False)

    levels=models.CharField(_(u'权限组'),null=True,max_length=60,blank=True)





    DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)


    def getImgUrl(self, default=None):
        if self.SSN:
            fname="%s.jpg"%(self.SSN)
            imgUrl='/iclock/file/photo/'+fname
            fullName=getStoredFileName("photo", None, fname)
            if os.path.exists(fullName):
                return imgUrl
        return default

    def getThumbnailUrl(self, default=None):#照片的URL地址信息
        if self.SSN:
            fname="%s.jpg"%(self.SSN)
            imgUrl='/iclock/file/photo/'+fname
            fullName=getStoredFileName("photo", None, fname)
            if os.path.exists(fullName):
            #if os.path.exists(imgUrl):
                return imgUrl
        #print "device, emp", device, emp
        return default
    def getImgUrlz(self, default=None):
        if self.Photourlz:
            fname="%s"%(self.Photourlz)
            imgUrl='/iclock/file/photo/'+fname
            fullName=getStoredFileName("photo", None, fname)
            if os.path.exists(fullName):
                return imgUrl
        return default

    def getThumbnailUrlz(self, default=None):#照片的URL地址信息
        if self.Photourlz:
            fname="%s"%(self.Photourlz)
            imgUrl='/iclock/file/photo/thumbnail/'+fname
            fullName=getStoredFileName("photo/thumbnail", None, fname)
            if os.path.exists(fullName):
            #if os.path.exists(imgUrl):
                return imgUrl
        #print "device, emp", device, emp
        return default
    def save(self):
        if not self.VisState:
            self.VisState=0
        if self.ExitTime and self.ExitTime<self.EnterTime:
            raise Exception(u'离开时间不能早于进入时间')
        super(visitionlogs,self).save()
        from mysite.visitors.views import sendVisitorsToAcc
        sendVisitorsToAcc(self)


    @staticmethod
    def colModels():
        ret= [{'name':'id','hidden':True,'frozen':False},
            #{'name':'visDate','width':120,'label':unicode(visitionlogs._meta.get_field('visDate').verbose_name)},
            {'name':'VisempName','index':'VisempName','width':80,'label':unicode(visitionlogs._meta.get_field('VisempName').verbose_name),'frozen':False},
            {'name':'VisState','width':80,'label':unicode(visitionlogs._meta.get_field('VisState').verbose_name),'frozen':False},
            {'name':'VisGender','width':40,'label':unicode(visitionlogs._meta.get_field('VisGender').verbose_name)},
            {'name':'CertificateType','width':100,'label':unicode(visitionlogs._meta.get_field('CertificateType').verbose_name)},
            {'name':'SSN','index':'SSN','width':120,'label':unicode(visitionlogs._meta.get_field('SSN').verbose_name)},
            {'name':'EnterTime','width':130,'label':unicode(visitionlogs._meta.get_field('EnterTime').verbose_name)},
            {'name':'ExitTime','width':130,'label':unicode(visitionlogs._meta.get_field('ExitTime').verbose_name)},
            {'name':'VisitingNum','width':80,'label':unicode(visitionlogs._meta.get_field('VisitingNum').verbose_name)},
            {'name':'VisitedCompany','width':150,'label':unicode(visitionlogs._meta.get_field('VisitedCompany').verbose_name)},
            {'name':'InterviewedempName','width':80,'label':unicode(visitionlogs._meta.get_field('InterviewedempName').verbose_name)},
            {'name':'VisCompany','width':150,'label':unicode(visitionlogs._meta.get_field('VisCompany').verbose_name)},
            {'name':'VisReason','width':120,'label':unicode(visitionlogs._meta.get_field('VisReason').verbose_name)},
            {'name':'EnterArticles','width':120,'label':unicode(visitionlogs._meta.get_field('EnterArticles').verbose_name)},
            {'name':'ExitArticles','width':120,'label':unicode(visitionlogs._meta.get_field('ExitArticles').verbose_name)},
            {'name':'Tele','width':120,'label':unicode(visitionlogs._meta.get_field('Tele').verbose_name)},
            {'name':'National','width':70,'label':unicode(visitionlogs._meta.get_field('National').verbose_name)},
            {'name':'photo','search':False,'sortable':False,'width':102,'label':unicode(visitionlogs._meta.get_field('Photourl').verbose_name)},
            {'name':'photoz','search':False,'sortable':False,'width':102,'label':unicode(visitionlogs._meta.get_field('Photourlz').verbose_name)}
            #{'name':'Birthday','width':120,'label':unicode(visitionlogs._meta.get_field('Birthday').verbose_name)},
            #{'name':'Address','width':120,'label':unicode(visitionlogs._meta.get_field('Address').verbose_name)},

            #{'name':'isvisited','width':120,'label':unicode(visitionlogs._meta.get_field('isvisited').verbose_name)},
            ]
        

        return ret

    class Admin:
        list_display=("VisempName" )
        search_fields = ['VisempName','SSN','VisCompany','InterviewedempName']
        #lock_fields=['VisempName']
    class Meta:
        verbose_name=_(u"访客登记")
        unique_together = (("SSN", "EnterTime"),)
        verbose_name_plural=verbose_name
        #permissions = (
        #	('search_visitionlogs','search visitionlogs'),
        #)

