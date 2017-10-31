#!/usr/bin/env python
#coding=utf-8

from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from datetime import time

import datetime
from mysite.iclock.models import employee,iclock,getDevice,department,customSql
from mysite.base.models import *
from  decimal import Decimal

STATUS_OK = "0"
STATUS_INVALID = "999"
STATUS_PAUSED = "2"
STATUS_STOP = "3"
STATUS_LEAVE = "3"


CARD_VALID = '1'
CARD_LOST = '3'
CARD_OVERDUE = '4'
CARD_STOP = '5'
CARD_INVALID = '6'
CARD_CANCEL = '2'

CARDSTATUS = (
        (CARD_VALID, _(u'有效')),
        (CARD_LOST, _(u'挂失')),
        (CARD_OVERDUE, _(u'过期')),
        (CARD_CANCEL, _(u'注销')),
        (CARD_INVALID, _(u'无效')),
        (CARD_STOP, _(u'停用')),
        ('999', _(u'注销')),
)



YESORNO = (
        (1, _(u'有效')),
        (0, _(u'无效')),
)
ISYESORNO = (
        (1, _(u'是')),
        (0, _(u'否')),
)
POS_CARD = '0'
PRIVAGE_CARD = '1'
OPERATE_CARD = '2'

#if get_option("POS_ID"):
#    PRIVAGE = (
#            (POS_CARD, _(u'普通卡')),
#            (PRIVAGE_CARD, _(u'管理卡')),
#    )
#else:
PRIVAGE = (
    (POS_CARD, _(u'普通卡')),
    (PRIVAGE_CARD, _(u'管理卡')),
    (OPERATE_CARD, _(u'操作卡')),
    )

def updateCardToEmp(obj,cardno):
        """更新卡号至人员表"""
        if cardno:
                cardno=int(cardno)
        obj.Card=cardno
        obj.OpStamp=datetime.datetime.now()
        obj.save()
        #sql="update %s set card='%s' where userid=%s"%(employee._meta.db_table,cardno,obj.id)
        #customSql(sql)
        cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,obj.PIN))
        cache.delete("%s_iclock_emp_%s"%(settings.UNIT,obj.id))


#验证卡类余额
def blance_valid(itype,newblance,user):
        if itype:
                iccardobj= ICcard.objects.filter(pk=itype)
                lessmoney = iccardobj[0].less_money#卡类最小余额
                maxmoney = iccardobj[0].max_money#卡类最大余额
                if lessmoney>=0 and lessmoney>newblance:
                        raise Exception(_(u"人员%s超出卡最小余额")%user)
                if maxmoney>0 and newblance>maxmoney:
                        raise Exception(_(u"人员%s超出卡最大余额")%user)
                if maxmoney==0 and newblance > 10000 :
                        raise Exception(_(u"人员%s超出系统允许最大余额")%user)

#验证卡号有效性
def valid_card(card,oldobj=None):
        import re
        tmpre = re.compile('^[0-9]+$')
        if card and not tmpre.search(card):
                raise Exception(_(u'卡号不正确'))
        if card:#新增或编缉了卡号时
                if int(card) == 0:
                        raise Exception(_(u'卡号不能为0'))
        if card:
                try:
                        tmpcard = IssueCard.objects.filter(cardno=card,cardstatus = CARD_VALID)
                except Exception,e:
                        tmpcard = None
                if oldobj:
                        if tmpcard and tmpcard[0].UserID!= oldobj:#用于前端表单验证
                                raise Exception(_(u'卡号已使用,如果确认将重新发卡,请卡原持卡人 %s 进行退卡操作') % tmpcard[0])
                        else:
                                tmpcard = IssueCard.objects.filter(UserID=oldobj,cardstatus = CARD_VALID).order_by('-id')
                                if tmpcard:
                                        raise Exception(_(u'该人存在有效卡,如果确认将重新发卡,请持卡人 %s 进行退卡或挂失操作') % tmpcard[0].UserID.PIN)


                else:
                        if tmpcard :#用于前端表单验证
                                raise Exception(_(u'卡号已使用,如果确认将重新发卡,请卡原持卡人 %s 进行退卡操作') % tmpcard[0])

def get_sys_card_no():
        cache_count = GetParamValue('pos_sys_card_no',0,'ipos')
        number = int(cache_count)+1
        SetParamValue('pos_sys_card_no',number,'ipos')
        return number

def get_cardserial_from_cache(cardno):
        try:
                obj = CardSerial.objects.get(cardno=cardno)
                number = int(obj.serialnum)+1
                obj.serialnum=number
                obj.save(force_update=True)
        except:
        #        import traceback;traceback.print_exc()
                number =1
                CardSerial(serialnum=number,cardno=cardno).save(force_insert=True)
        return number


class CardSerial(models.Model):
        cardno = models.CharField(_(u'卡号'),max_length=10, null=True, blank=True)
        serialnum = models.CharField(_(u'卡流水号'),max_length=20,null=True,blank=True)
        def __unicode__(self):
                return u"%s,%s"%(self.cardno,self.serialnum)
        def save(self, *args, **kwargs):
                super(CardSerial, self).save(*args, **kwargs)
        class Admin:
                search_fields=[]


class SplitTime(models.Model):
        code = models.CharField(max_length=20,verbose_name=_(u'编号'),editable=True)
        name = models.CharField(max_length=20,verbose_name=_(u'名称'),editable=True)
        starttime= models.TimeField(verbose_name=_(u'开始时间'),  null=False,blank=False,editable=True)
        endtime = models.TimeField(verbose_name=_(u'结束时间'),  null=False, blank=False,editable=True)
        isvalid = models.NullBooleanField(verbose_name=_(u'是否有效'),null=False, default=True, blank=True, editable=True)
        fixedmonery = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'金额(元)'),null=False,blank=False,editable=True)
        remarks = models.CharField(max_length=200,verbose_name=_(u'备注'),null=True,blank=True,editable=True)
        DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)

        def __unicode__(self):
                return u"%s"%self.name
        class Admin:
                search_fields=['name']
                @staticmethod
                def initial_data():
                        if SplitTime.objects.count() == 0:
                                SplitTime(code=1,name=u"%s"%_(u"默认1"),fixedmonery=10,starttime=time(0,0),endtime=time(10,0)).save()
                                SplitTime(code=2,name=u"%s"%_(u"默认2"),fixedmonery=10,starttime=time(10,1),endtime=time(14,0)).save()
                                SplitTime(code=3,name=u"%s"%_(u"默认3"),fixedmonery=10,starttime=time(14,1),endtime=time(20,0)).save()
                                SplitTime(code=4,name=u"%s"%_(u"默认4"),fixedmonery=10,starttime=time(20,1),endtime=time(23,59)).save()
                                SplitTime(code=5,name=u"%s"%_(u"默认5"),fixedmonery=10,starttime=time(0,0),endtime=time(0,0)).save()
                                SplitTime(code=6,name=u"%s"%_(u"默认6"),fixedmonery=10,starttime=time(0,0),endtime=time(0,0)).save()
                                SplitTime(code=7,name=u"%s"%_(u"默认7"),fixedmonery=10,starttime=time(0,0),endtime=time(0,0)).save()
                                SplitTime(code=8,name=u"%s"%_(u"默认8"),fixedmonery=10,starttime=time(0,0),endtime=time(0,0)).save()

        def useiclock(self):
                sn_list=SplitTimemechine.objects.filter(splittime=self).values_list('SN',flat=True)
                iclocks=iclock.objects.filter(SN__in=sn_list).exclude(DelTag=1)
                con=0
                sns=''
                if iclocks:
                        for t in iclocks:
                                sns+=t.SN+','
                                con+=1
                                if con>1:
                                        sns+='...,'
                                        break
                        return sns[:-1]
                return ''

        def save(self, *args, **kwargs):
                key=settings.UNIT+"SplitTime"
                cache.delete(key)
                super(SplitTime, self).save(*args, **kwargs)

        def data_check(self):
                try:
                        self.code = str(int(self.code))
                except:
                        raise Exception(_(u'编号只能为数字'))
                if int(self.code)<=0:
                        raise Exception(_(u'编号不能为0或负数'))
                try:
                        int(self.fixedmonery)
                except:
                        raise Exception(_(u'金额只能为数字'))
                if int(self.fixedmonery)< 0:
                        raise Exception(_(u'金额不能为负数'))
                if len(self.code) > 2:
                        raise Exception(_(u'%(f)s编号长度不能超过%(ff)s位') % {"f":self.code, "ff":2})

                tmp = SplitTime.objects.filter(code=self.code)
                if len(tmp) > 0 and tmp[0].id != self.id:   #编辑状态
                        raise Exception(_(u'编号: %s 已存在') % self.code)
                if int(self.code)<>1:
                        tmp = SplitTime.objects.get(code=int(self.code)-1)
                        minute1 = tmp.endtime.minute+1
                        hour1 = tmp.endtime.hour
                        hour2 = self.starttime.hour
                        if minute1==60:
                                minute1 =0
                                hour1=tmp.endtime.hour+1
                        minute2 = self.starttime.minute
                        if hour1<>hour2 and self.isvalid==1:
                                raise Exception(_(u'开始时间必须是上一段结束时间加一分钟'))
                        if minute2 <> minute1 and self.isvalid==1:
                                raise Exception(_(u'开始时间必须是上一段结束时间加一分钟'))

                if self.starttime>self.endtime:
                        raise Exception(_(u'结束时间不能小于开始时间'))

        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        {'name':'code','width':80,'label':unicode(SplitTime._meta.get_field('code').verbose_name)},
                        {'name':'name','width':80,'label':unicode(SplitTime._meta.get_field('name').verbose_name)},
                        {'name':'isvalid','width':80,'label':unicode(SplitTime._meta.get_field('isvalid').verbose_name)},
                        {'name':'fixedmonery','width':80,'label':unicode(SplitTime._meta.get_field('fixedmonery').verbose_name)},
                        {'name':'starttime','width':120,'label':unicode(SplitTime._meta.get_field('starttime').verbose_name)},
                        {'name':'endtime','width':120,'label':unicode(SplitTime._meta.get_field('endtime').verbose_name)},
                        {'name':'splittimemechine','sortable':False,'width':180,'label':unicode(_(u'可用设备'))},
                        {'name':'remarks','width':200,'label':unicode(SplitTime._meta.get_field('remarks').verbose_name)}
                        ]

        class Meta:
                verbose_name = _(u"分段定值")#上部按钮
                verbose_name_plural = verbose_name
                #unique_together = (("code",),)


TIMENAME =(
('1',_(u'固定时间段')),
('2',_(u'第2批')),
('3',_(u'第3批')),
('4',_(u'第4批')),
('5',_(u'第5批')),
('6',_(u'第6批')),
('7',_(u'第7批')),
('8',_(u'第8批')),
('9',_(u'第9批')),
)

class BatchTime(models.Model):
        code = models.CharField(max_length=3,verbose_name=_(u'编号'),null=False,blank=False,editable=False)
        name = models.CharField(max_length=20,verbose_name=_(u'时间段名称'),null=False,blank=False,editable=True)
        starttime= models.TimeField(verbose_name=_(u'开始时间'),  null=False,blank=False,editable=True)
        endtime = models.TimeField(verbose_name=_(u'结束时间'),  null=False, blank=False,editable=True)
        isvalid = models.NullBooleanField(verbose_name=_(u'是否有效'),null=False, default=True, blank=True, editable=True)
        remarks = models.CharField(max_length=200,verbose_name=_(u'备注'),null=True,blank=True,editable=True)
        pos_time = models.CharField(verbose_name=_(u"批次编号"),max_length=10,blank=True,null=True,choices=TIMENAME)
        DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)
        def __unicode__(self):
                return u"%s"%self.name#can't use lazy here
        class Admin:
                search_fields=['name']
                @staticmethod
                def initial_data():
                        if BatchTime.objects.count()==0:
                                BatchTime(starttime=time(0,1),name=u"%s"%_(u"固定时间段"),code="1",pos_time="1",endtime=time(23,59),isvalid=1).save()
                                BatchTime(starttime=time(0,1),name=u"%s"%_(u"固定时间段"),code="1",pos_time="2",endtime=time(23,59),isvalid=1).save()
                                BatchTime(starttime=time(0,1),name=u"%s"%_(u"固定时间段"),code="1",pos_time="3",endtime=time(23,59),isvalid=1).save()
                                BatchTime(starttime=time(0,1),name=u"%s"%_(u"固定时间段"),code="1",pos_time="4",endtime=time(23,59),isvalid=1).save()
                                BatchTime(starttime=time(0,0),name=u"%s"%_(u"固定时间段"),code="1",pos_time="5",endtime=time(0,0),isvalid=0).save()
                                BatchTime(starttime=time(0,0),name=u"%s"%_(u"固定时间段"),code="1",pos_time="6",endtime=time(0,0),isvalid=0).save()
                                BatchTime(starttime=time(0,0),name=u"%s"%_(u"固定时间段"),code="1",pos_time="7",endtime=time(0,0),isvalid=0).save()
                                BatchTime(starttime=time(0,0),name=u"%s"%_(u"固定时间段"),code="1",pos_time="8",endtime=time(0,0),isvalid=0).save()
                                for i in range(2,10):
                                        BatchTime(starttime=time(8,0),name= unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="1",endtime=time(9,0),isvalid=1).save()
                                        BatchTime(starttime=time(10,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="2",endtime=time(14,0),isvalid=1).save()
                                        BatchTime(starttime=time(17,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="3",endtime=time(19,0),isvalid=1).save()
                                        BatchTime(starttime=time(20,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="4",endtime=time(23,59),isvalid=1).save()
                                        BatchTime(starttime=time(0,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="5",endtime=time(0,0),isvalid=0).save()
                                        BatchTime(starttime=time(0,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="6",endtime=time(0,0),isvalid=0).save()
                                        BatchTime(starttime=time(0,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="7",endtime=time(0,0),isvalid=0).save()
                                        BatchTime(starttime=time(0,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="8",endtime=time(0,0),isvalid=0).save()

        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        #{'name':'code','width':80,'label':unicode(BatchTime._meta.get_field('code').verbose_name)},
                        {'name':'name','width':80,'label':unicode(BatchTime._meta.get_field('name').verbose_name)},
                        {'name':'starttime','width':120,'label':unicode(BatchTime._meta.get_field('starttime').verbose_name)},
                        {'name':'endtime','width':120,'label':unicode(BatchTime._meta.get_field('endtime').verbose_name)},
                        {'name':'isvalid','width':80,'label':unicode(BatchTime._meta.get_field('isvalid').verbose_name)},
                        #{'name':'pos_time','width':120,'label':unicode(BatchTime._meta.get_field('pos_time').verbose_name)},
                        {'name':'remarks','width':200,'label':unicode(BatchTime._meta.get_field('remarks').verbose_name)}
                        ]

        class Meta:
                verbose_name = _(u"消费时间段")
                verbose_name_plural = verbose_name
                #unique_together = (("code",),)

        def save(self, *args, **kwargs):
                if self.code:
                        key=settings.UNIT+"BatchTime_"+str(self.code)
                        cache.delete(key)
                super(BatchTime, self).save(*args, **kwargs)
#商品资料
class Merchandise(models.Model):
        code = models.IntegerField(verbose_name=_(u'商品编号'),editable=True)
        name = models.CharField(max_length=10,verbose_name=_(u'商品名称'),editable=True)
        money = models.DecimalField (max_digits=6,decimal_places=2,verbose_name=_(u'单价(元)'),null=False,blank=False,editable=True)
        rebate = models.IntegerField(default=0,verbose_name=_(u'折扣（%）'),null=False,blank=False,editable=True,help_text=_(u'折扣80% 即为8折'))
        barcode = models.CharField(max_length=20,verbose_name=_(u'商品条码'),editable=True,blank=True)
        DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)
        def __unicode__(self):
                return u"%s"%self.name#can't use lazy here
        class Admin:
                search_fields=['name','code']
        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        {'name':'code','width':150,'label':unicode(Merchandise._meta.get_field('code').verbose_name)},
                        {'name':'name','width':240,'label':unicode(Merchandise._meta.get_field('name').verbose_name)},
                        {'name':'barcode','width':240,'label':unicode(Merchandise._meta.get_field('barcode').verbose_name)},
                        {'name':'money','width':80,'label':unicode(Merchandise._meta.get_field('money').verbose_name)},
                        {'name':'rebate','width':80,'label':unicode(Merchandise._meta.get_field('rebate').verbose_name)}
                        ]
        class Meta:
                verbose_name = _(u"商品资料")
                verbose_name_plural = verbose_name
                unique_together = (("code",),)

        def save(self, *args, **kwargs):
                key=settings.UNIT+'Merchandise'
                cache.delete(key)
                super(Merchandise, self).save(*args, **kwargs)

        def delete(self):
                try:
                        key=settings.UNIT+'Merchandise'
                        cache.delete(key)
                        super(Merchandise, self).delete()
                except Exception,e:
                        pass

class Dininghall(models.Model):
        code = models.IntegerField(verbose_name=_(u'餐厅编号'),blank=False)
        name = models.CharField(verbose_name=_(u"餐厅名称"),max_length=100,blank=False)
        remark = models.CharField(verbose_name=_(u"备注"),max_length=200, blank=True)
        DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)
        def __unicode__(self):
                return u"%s"%self.name#can't use lazy here
        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        {'name':'code','width':80,'label':unicode(Dininghall._meta.get_field('code').verbose_name)},
                        {'name':'name','width':200,'label':unicode(Dininghall._meta.get_field('name').verbose_name)},
                        {'name':'dedn','sortable':False,'width':240,'label':unicode(_(u'设备数'))},
                        {'name':'remark','width':240,'label':unicode(Dininghall._meta.get_field('remark').verbose_name)}
                ]
        class Admin:
                search_fields=['name','code']
                list_display=("name","code", )
                @staticmethod
                def initial_data():#初始化数据
                        if Dininghall.objects.count() == 0:
                                Dininghall(code=1,name=u"%s"%_(u"总部餐厅")).save()

        class Meta:
                verbose_name = _(u"餐厅资料")#上部按钮
                verbose_name_plural = verbose_name
                unique_together = (("code",),)


class Meal(models.Model):
        code = models.CharField(verbose_name=_(u'餐别编号'), blank=False,max_length=20,editable=True)
        name = models.CharField(verbose_name=_(u"餐别名称"), max_length=100, blank=False)
        available = models.NullBooleanField(verbose_name=_(u"是否有效"), null=False, default=True)
        money = models.DecimalField (max_digits=8,decimal_places=2,verbose_name=_(u"成本（元）"), blank=False)
        starttime = models.TimeField(verbose_name=_(u"开始时间"),blank=False)
        endtime = models.TimeField(verbose_name=_(u"结束时间"), blank=False)
        remark = models.CharField(verbose_name=_(u"备注"),max_length=100,blank=True)
        DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)
        def __unicode__(self):
                return u"%s"%self.name
        class Admin:
                search_fields=['name','code']
                @staticmethod
                def initial_data():
                        if Meal.objects.count() == 0:
                                Meal(code=1,name=u"%s"%_(u"早餐"),money=2,starttime=time(0,0),endtime=time(10,0,59),available=1).save()
                                Meal(code=2,name=u"%s"%_(u"中餐"),money=3,starttime=time(10,1),endtime=time(14,0,59),available=1).save()
                                Meal(code=3,name=u"%s"%_(u"晚餐"),money=4,starttime=time(14,1),endtime=time(20,0,59),available=1).save()
                                Meal(code=4,name=u"%s"%_(u"夜宵"),money=2,starttime=time(20,1),endtime=time(23,59,59),available=1).save()
                                Meal(code=5,name=u"%s"%_(u"餐别05"),money=2,starttime=time(0,0),endtime=time(0,0),available=0).save()
                                Meal(code=6,name=u"%s"%_(u"餐别06"),money=2,starttime=time(0,0),endtime=time(0,0),available=0).save()
                                Meal(code=7,name=u"%s"%_(u"餐别07"),money=2,starttime=time(0,0),endtime=time(0,0),available=0).save()
                                Meal(code=8,name=u"%s"%_(u"餐别08"),money=2,starttime=time(0,0),endtime=time(0,0),available=0).save()

        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        {'name':'code','width':80,'label':unicode(Meal._meta.get_field('code').verbose_name)},
                        {'name':'name','width':80,'label':unicode(Meal._meta.get_field('name').verbose_name)},
                        {'name':'available','width':80,'label':unicode(Meal._meta.get_field('available').verbose_name)},
                        {'name':'money','width':80,'label':unicode(Meal._meta.get_field('money').verbose_name)},
                        {'name':'starttime','width':150,'label':unicode(Meal._meta.get_field('starttime').verbose_name)},
                        {'name':'endtime','width':150,'label':unicode(Meal._meta.get_field('endtime').verbose_name)},
                        {'name':'remark','width':240,'label':unicode(Meal._meta.get_field('remark').verbose_name)}
                        ]
        class Meta:
                verbose_name = _(u"餐别资料")
                verbose_name_plural = verbose_name
                unique_together = (("code",),)

        def save(self, *args, **kwargs):
                if self.id:
                        key = settings.UNIT+"meals"
                        cache.delete(key)

                super(Meal, self).save(*args, **kwargs)

        @staticmethod
        def get_meals():
                key = settings.UNIT+"meals"
                meals = cache.get(key)
                try:
                        if not meals:
                                objs=Meal.objects.exclude(DelTag=1)
                                meals={}#
                                for t in objs:
                                        if t.starttime and t.endtime:
                                                meals[t.id]=[t.starttime,t.endtime]
                                cache.set(key,meals)
                except:
                        pass
                return meals




class Mealmachine(models.Model):
        meal = models.ForeignKey(Meal)
        SN = models.ForeignKey(iclock)
        def __unicode__(self):
                return unicode(self.SN)
        class Admin:
                list_display=("SN", )
        class Meta:
                verbose_name=_(u"可用设备")
                verbose_name_plural=verbose_name
                unique_together = (("SN", "meal"),)




class KeyValue(models.Model):
        code = models.IntegerField(verbose_name=_(u'键值编号'),editable=True)
        money = models.DecimalField (max_digits=6,decimal_places=2,verbose_name=_(u'单价(元)'),null=False,blank=False,editable=True)
        DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)
        def __unicode__(self):
                return u"%s %s"%(self.code,self.money)
        class Admin:
                search_fields=['code']
        def useiclock(self):
                sn_list=KeyValuemechine.objects.filter(keyvalue=self).values_list('SN',flat=True)
                iclocks=iclock.objects.filter(SN__in=sn_list).exclude(DelTag=1)
                con=0
                sns=''
                if iclocks:
                        for t in iclocks:
                                sns+=t.SN+','
                                con+=1
                                if con>1:
                                        sns+='...,'
                                        break
                        return sns[:-1]
                return ''
        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        {'name':'code','width':100,'label':unicode(KeyValue._meta.get_field('code').verbose_name)},
                        {'name':'money','width':100,'label':unicode(KeyValue._meta.get_field('money').verbose_name)},
                        {'name':'keyvaluemechine','sortable':False,'width':180,'label':unicode(_(u'可用设备'))}
                        ]
        class Meta:
                verbose_name = _(u"键值资料")
                verbose_name_plural = verbose_name
                unique_together = (("code",),)




TIMENAME =(
('1',_(u'固定时间段')),
('2',_(u'第二批')),
('3',_(u'第三批')),
('4',_(u'第四批')),
('5',_(u'第五批')),
('6',_(u'第六批')),
('7',_(u'第七批')),
('8',_(u'第八批')),
('9',_(u'第九批')),
)
class ICcard(models.Model):
        code = models.IntegerField(verbose_name=_(u'卡类编号'),  blank=False, unique=True)
        name = models.CharField(verbose_name=_(u"卡类名称"), max_length=24, blank=False)
        discount = models.IntegerField(verbose_name=_(u"折扣（%）"),default=0,help_text=_(u'折扣80% 即为8折'))#Integer
        #pos_time = TimeSliceForeignKey(verbose_name=_(u"消费时间段"), blank=True,null=True)#从分段消费选择
        pos_time = models.CharField(verbose_name=_(u"消费时间段"),max_length=10, blank=False,null=False,choices=TIMENAME,default=1)
        #DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'金额(元)'),null=False,blank=False,editable=True)
        date_max_money = models.DecimalField(max_digits=8,decimal_places=0,verbose_name=_(u"日消费最大金额（元）"), default=0)
        date_max_count = models.IntegerField(verbose_name=_(u"日消费最大次数"), default=0)
        per_max_money = models.DecimalField(max_digits=8,decimal_places=0,verbose_name=_(u"次消费最大金额（元）"), default=0)
        meal_max_money = models.DecimalField(max_digits=8,decimal_places=0,verbose_name=_(u"餐消费最大金额（元）"), default=0)
        meal_max_count = models.IntegerField(verbose_name=_(u"餐消费最大次数"), default=0)
        less_money = models.DecimalField(max_digits=8,decimal_places=0,verbose_name=_(u"最小卡余额（元）"), default=0)
        max_money = models.DecimalField(max_digits=8,decimal_places=0,verbose_name=_(u"最大卡余额（元）"), default=9999)
        #posmeal = MealManyToManyField(verbose_name=_(u"可用餐别"), blank=True,null=True,editable=True)#从餐厅登记中选择
        use_date = models.IntegerField(verbose_name=_(u"有效使用天数"), default=0)

        #use_mechine = DeviceManyToManyFieldKey(verbose_name=_(u"可用设备"), blank=True, null=True)#从设备登记中获取
        remark = models.CharField(verbose_name=_(u"备注"),max_length=200,blank=True)
        use_fingerprint = models.IntegerField(verbose_name=_(u"使用指纹卡"), null=False, default=0, blank=True, editable=False, choices=YESORNO)
        DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)

        def __unicode__(self):
                return u"%s---%s"%(self.name,self.code)#can't use lazy here
        class Admin:
                search_fields=['code','name']

                @staticmethod
                def initial_data():
                        if ICcard.objects.count()==0:
                                ICcard(code='1',name=u"%s"%_(u"员工卡"),discount=0,date_max_money=0,
                            date_max_count=0,per_max_money=0,meal_max_money=0,meal_max_count=0,
                            less_money=0,max_money=0,use_date=0).save(force_insert=True)

        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        {'name':'code','width':80,'label':unicode(ICcard._meta.get_field('code').verbose_name)},
                        {'name':'name','width':80,'label':unicode(ICcard._meta.get_field('name').verbose_name)},
                        {'name':'discount','width':80,'label':unicode(ICcard._meta.get_field('discount').verbose_name)},
                        {'name':'pos_time','width':120,'label':unicode(ICcard._meta.get_field('pos_time').verbose_name)},
                        {'name':'date_max_money','width':150,'label':unicode(ICcard._meta.get_field('date_max_money').verbose_name)},
                        {'name':'date_max_count','width':150,'label':unicode(ICcard._meta.get_field('date_max_count').verbose_name)},
                        {'name':'per_max_money','width':150,'label':unicode(ICcard._meta.get_field('per_max_money').verbose_name)},
                        {'name':'meal_max_money','width':150,'label':unicode(ICcard._meta.get_field('meal_max_money').verbose_name)},
                        {'name':'meal_max_count','width':120,'label':unicode(ICcard._meta.get_field('meal_max_count').verbose_name)},
                        {'name':'less_money','width':120,'label':unicode(ICcard._meta.get_field('less_money').verbose_name)},
                        {'name':'max_money','width':120,'label':unicode(ICcard._meta.get_field('max_money').verbose_name)},
                        {'name':'use_date','width':100,'label':unicode(ICcard._meta.get_field('use_date').verbose_name)},
                        {'name':'remark','width':120,'label':unicode(ICcard._meta.get_field('remark').verbose_name)}
                        ]
        class Meta:
                verbose_name = _(u"卡类资料")
                verbose_name_plural = verbose_name
                #unique_together = (("code",),)

        def save(self, *args, **kwargs):
                if self.id:
                        cache.delete("%s_iccard_%s"%(settings.UNIT,self.id))
                        key = settings.UNIT+"use_machine_"+str(self.id)
                        cache.delete(key)
                        key = settings.UNIT+"posmeal_"+str(self.id)
                        cache.delete(key)
                try:
                        ic=ICcard.objects.get(code=self.code)
                        if ic.DelTag<>0:
                                ic.DelTag=0
                                ic.name=self.name
                                ic.discount=self.discount
                                ic.pos_time=self.pos_time
                                ic.date_max_money=self.date_max_money
                                ic.date_max_count=self.date_max_count
                                ic.per_max_money=self.per_max_money
                                ic.meal_max_money=self.meal_max_money
                                ic.meal_max_count=self.meal_max_count
                                ic.less_money=self.less_money
                                ic.max_money=self.max_money
                                ic.use_date=self.use_date
                                ic.remark=self.remark or ''
                                super(ICcard,ic).save(*args, **kwargs)
                        else:
                                super(ICcard,self).save(*args, **kwargs)
                except:
                        super(ICcard,self).save(*args, **kwargs)
                #super(ICcard, self).save(*args, **kwargs)

        @staticmethod
        def objByID(id):
                if not id: return None
                obj=cache.get("%s_iccard_%s"%(settings.UNIT,id))
                if obj: return obj
                try:
                        obj=ICcard.objects.get(id=id)
                except:
                        obj=None
                if obj:
                        cache.set("%s_iccard_%s"%(settings.UNIT,id),obj)
                return obj

        def get_device_code(self):
                key = settings.UNIT+"use_machine_"+str(self.pk)
                use_device = cache.get(key)
                try:
                        if not use_device and not type(use_device)==list:
                                use_device=[]
                                objs=ICcardmechine.objects.filter(iccard=self)
                                for t in objs:
                                        use_device.append(t.SN_id)
                                cache.set(key,use_device)
                except:
                        pass
                return use_device

        def get_meal_code(self):
                key = settings.UNIT+"posmeal_"+str(self.pk)
                use_meal = cache.get(key)
                try:
                        if type(use_meal)<>dict:
                                objs=ICcardposmeal.objects.filter(iccard=self)
                                use_meal={'MealID':[],'SNS':[]}#{'MealID':[1,2,3],'SNS':['122121','33223323']}
                                for t in objs:
                                        use_meal['MealID'].append(t.meal_id)
                                objs=ICcardmechine.objects.filter(iccard=self)
                                for t in objs:
                                        use_meal['SNS'].append(t.SN_id)

                                if use_meal['SNS'] and use_meal['MealID']:
                                        cache.set(key,use_meal)
                                else:
                                        use_meal={}
                                        cache.set(key,use_meal)

                except:
                        pass
                return use_meal





class ICcardposmeal(models.Model):
        iccard = models.ForeignKey(ICcard)
        meal = models.ForeignKey(Meal)
        def __unicode__(self):
                return unicode(self.iccard)
        class Admin:
                list_display=("iccard","meal", )
        class Meta:
                verbose_name=_(u"可用餐别")
                verbose_name_plural=verbose_name
                unique_together = (("iccard","meal"),)

class ICcardmechine(models.Model):
        iccard = models.ForeignKey(ICcard)
        SN = models.ForeignKey(iclock)
        def __unicode__(self):
                return unicode(self.SN)
        class Admin:
                list_display=("SN","iccard", )
        class Meta:
                verbose_name=_(u"可用设备")
                verbose_name_plural=verbose_name
                unique_together = (("SN", "iccard"),)

class SplitTimemechine(models.Model):
        splittime = models.ForeignKey(SplitTime)
        SN = models.ForeignKey(iclock)
        def __unicode__(self):
                return unicode(self.SN)
        class Admin:
                list_display=("SN","splittime", )
        class Meta:
                verbose_name=_(u"可用设备")
                verbose_name_plural=verbose_name
                unique_together = (("SN", "splittime"),)

class KeyValuemechine(models.Model):
        keyvalue = models.ForeignKey(KeyValue)
        SN = models.ForeignKey(iclock)
        def __unicode__(self):
                return unicode(self.SN)
        class Admin:
                list_display=("SN","keyvalue", )
        class Meta:
                verbose_name=_(u"可用设备")
                verbose_name_plural=verbose_name
                unique_together = (("SN", "keyvalue"),)

CASHTYPE=(
            (1,_(u'收入')),
            (2,_(u'支出')),
)


class CardCashType(models.Model):
        name = models.CharField(max_length=50,verbose_name=_(u'类型名称'),null=False,blank=False,editable=True)
        itype= models.IntegerField(verbose_name=_(u'类型'),null=False,blank=False,editable=True,choices=CASHTYPE)
        remark= models.CharField(max_length=100,verbose_name=_(u'备注'),blank=True,editable=True,null=True)
        def __unicode__(self):
                return u"%s"%(self.name)
        class Admin:
                search_fields=['name']
                @staticmethod
                def initial_data():
                        if CardCashType.objects.count()==0:
                                CardCashType(id=1,name=u"%s"%_(u"充值"), itype=1).save()#1
                                CardCashType(id=2,name=u"%s"%_(u"补贴"), itype=1).save()#2
                                CardCashType(id=4,name=u"%s"%_(u"支出卡成本"), itype=2).save()#4
                                CardCashType(id=5,name=u"%s"%_(u"退款"), itype=2).save() #5
                                CardCashType(id=6,name=u"%s"%_(u"消费"), itype=2).save()  #6
                                CardCashType(id=7,name=u"%s"%_(u"卡成本"), itype=1).save()  #7
                                CardCashType(id=8,name=u"%s"%_(u"手工补消费"), itype=2).save()  #8
                                CardCashType(id=9,name=u"%s"%_(u"纠错"), itype=1).save()  #9
                                CardCashType(id=10,name=u"%s"%_(u"计次"), itype=2).save()
                                CardCashType(id=11,name=u"%s"%_(u"管理费"), itype=1).save() #11
                                CardCashType(id=12,name=u"%s"%_(u"计次纠错"), itype=1).save()
                                #if get_option("POS_IC"):
                                CardCashType(id=13,name=u"%s"%_(u"优惠充值"), type=1).save()
                                CardCashType(id=21,name=u"%s"%_(u"微信充值"), itype=1).save()#1
                                CardCashType(id=22,name=u"%s"%_(u"支付宝充值"), itype=1).save()#2



        class Meta:
                verbose_name = _(u"卡现金消费类型")
                verbose_name_plural = verbose_name
                unique_together = (("name",),)





#cardtype= int(GetParamValue('ipos_cardtype',0,'ipos'))
#if cardtype==1:
#       CASHTYPE=(
#               (1,_(u'充值')),
#               (2,_(u'补贴')),
#               #(3,_(u'批量充值')),
#               (7,_(u'卡成本')),
#               (4,_(u'支出卡成本')),
#               (5,_(u'退款')),
#               (6,_(u'消费')),
#               (11,_(u'管理费')),
#               (10,_(u'计次')),
#               (8,_(u'手工补消费')),
#               (9,_(u'纠错')),
#               #(10,_(u'计次')),
#               (12,_(u'计次纠错')),
##                (13,_(u'优惠记录')),
#    )
#elif cardtype==2:
#     CASHTYPE=(
#                    (1,_(u'充值')),
#                    (2,_(u'补贴')),
#                    #(3,_(u'批量充值')),
#                    (7,_(u'卡成本')),
#                    (4,_(u'支出卡成本')),
#                    (5,_(u'退款')),
##                    (6,_(u'消费')),
#                    (11,_(u'管理费')),
##                    (10,_(u'计次')),
##                    (8,_(u'手工补消费')),
##                    (9,_(u'纠错')),
##                    (10,_(u'计次')),
##                    (12,_(u'计次纠错')),
#                    (13,_(u'充值优惠')),
#                    (14,_(u'无卡退卡')),
#        )

SZCASHTYPE=(
        (1,_(u'充值')),
        (2,_(u'补贴')),
        #(3,_(u'批量充值')),
        (7,_(u'卡成本')),
        (4,_(u'支出卡成本')),
        (5,_(u'退款')),
        (6,_(u'消费')),
        (11,_(u'管理费')),
        (8,_(u'手工补消费')),
        (9,_(u'纠错')),
        (10,_(u'计次')),
        (12,_(u'计次纠错')),
        (13,_(u'充值优惠')),
        (14,_(u'无卡退卡')),
        (15,_(u'有卡退卡')),
        (21,_(u'支付宝充值')),   #对应交易方式+20, (1支付宝 2微信)
        (22,_(u'微信充值')),
        )


AllOW_TYPE = (
            (0,_(u'累加补贴')),
            (1,_(u'清零补贴')),

)
LOGFLAG=(
            (1,_(u'设备上传')),
            (2,_(u'系统添加')),
            (3,_(u'纠错补入')),
            (4,_(u'支付宝充值')),    #对应交易方式+3, (1支付宝 2微信)
            (5,_(u'微信充值')),
        )
CONSUMEMODEL=(
            (1,_(u'定值模式')),
            (2,_(u'金额模式')),
            (3,_(u'键值模式')),
            (4,_(u'计次模式')),
            (5,_(u'商品模式')),
            (6,_(u'计时模式')),
            (7,_(u'记账模式')),
            (8,_(u'手工补消费')),
            (9,_(u'设备纠错')),
                  )

class CardCashSZ(models.Model):
        UserID = models.ForeignKey(employee, verbose_name=_(u"人员"), editable=True)
        card = models.CharField(_(u'卡号'), max_length=20, null=False, blank=True, editable=True, default='')
        sys_card_no =  models.IntegerField(verbose_name=_(u"卡账号"),null=True, blank=True,editable=True)
        #    dept_id = models.IntegerField(_(u'部门id'),max_length=10, null=True, blank=True,editable=False)
        dept = models.ForeignKey(department,verbose_name=_(u'部门'), editable=True, null=True)
        sn = models.CharField(_(u'设备序列号'), max_length=20, null=True, blank=True)
        cardserial = models.IntegerField(_(u'卡流水号'), null=True, blank=True)
        serialnum = models.IntegerField(_(u'设备流水号'),null=True,blank=True)
        checktime= models.DateTimeField(verbose_name=_(u'操作时间'),blank=True,editable=True,null=True)
        CashType= models.ForeignKey(CardCashType,verbose_name=_(u'类型'),null=False,blank=False,editable=True)
        money = models.DecimalField (max_digits=10,decimal_places=2,verbose_name=_(u'金额(元)'),null=False,blank=False,editable=True)
        discount = models.IntegerField(verbose_name=_(u"折扣（%）"),default=0,null=True,blank=True,editable=False)#Integer
        hide_column = models.IntegerField(_(u'类型名称'), null=True, blank=True,choices=SZCASHTYPE)
        dining = models.ForeignKey(Dininghall,verbose_name=_(u'餐厅'),editable=True, blank=True,null=True)
        #    dining = models.CharField(_(u'餐厅'),max_length=20,null=True,blank=True,editable=False)
        blance = models.DecimalField(verbose_name=_(u'余额(元)'),max_digits=9,null=True, blank=True,decimal_places=2,editable=True)
        allow_balance = models.DecimalField(verbose_name=_(u'补贴余额(元)'),max_digits=9,null=True, blank=True,decimal_places=2,editable=True)

        convey_time = models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
        allow_type = models.IntegerField(_(u'补贴类型'),  null=True, blank=True,choices=AllOW_TYPE)
        allow_batch = models.IntegerField(_(u'补贴批次'), null=True, blank=True)
        allow_base_batch = models.IntegerField(_(u'补贴基次'), null=True, blank=True)
        log_flag = models.IntegerField(_(u'记录类型'), null=True,default=2, blank=True, editable=False,choices=LOGFLAG)
        create_operator = models.CharField(_(u'操作'), max_length=20, null=True, blank=True, editable=False)
        meal = models.ForeignKey(Meal,verbose_name=_(u"餐别"),null=True,editable=True,blank=True,)
        pos_model = models.IntegerField(_(u'消费类型'),null=True, blank=True,choices=CONSUMEMODEL)

        def __unicode__(self):
                return u""
        class Admin:
                search_fields=['UserID__EName','UserID__PIN']

        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        {'name':'UserID','width':80,'label':unicode(employee._meta.get_field('PIN').verbose_name)},
                        {'name':'UserID__EName','width':80,'label':unicode(employee._meta.get_field('EName').verbose_name)},
                        {'name':'dept','width':80,'label':unicode(_('department name'))},
                        {'name':'card','width':80,'label':unicode(CardCashSZ._meta.get_field('card').verbose_name)},
                        {'name':'sys_card_no','width':80,'label':unicode(CardCashSZ._meta.get_field('sys_card_no').verbose_name)},
                        {'name':'cardserial','width':80,'label':unicode(CardCashSZ._meta.get_field('cardserial').verbose_name)},
                        {'name':'hide_column','width':80,'label':unicode(CardCashSZ._meta.get_field('hide_column').verbose_name)},
                        {'name':'CashType','width':80,'label':unicode(CardCashSZ._meta.get_field('CashType').verbose_name)},
                        {'name':'allow_type','width':80,'label':unicode(CardCashSZ._meta.get_field('allow_type').verbose_name)},
                        {'name':'money','width':80,'label':unicode(CardCashSZ._meta.get_field('money').verbose_name)},
                        {'name':'blance','width':80,'label':unicode(CardCashSZ._meta.get_field('blance').verbose_name)},
                        {'name':'convey_time','width':120,'label':unicode(CardCashSZ._meta.get_field('convey_time').verbose_name)},
                        {'name':'checktime','width':120,'label':unicode(CardCashSZ._meta.get_field('checktime').verbose_name)},
                        {'name':'sn','width':100,'label':unicode(CardCashSZ._meta.get_field('sn').verbose_name)},
                        {'name':'serialnum','width':80,'label':unicode(CardCashSZ._meta.get_field('serialnum').verbose_name)},
                        {'name':'log_flag','width':80,'label':unicode(CardCashSZ._meta.get_field('log_flag').verbose_name)}
                        ]

        class Meta:
                verbose_name = _(u"卡现金收支")
                verbose_name_plural = verbose_name
                unique_together = (("sn","hide_column","sys_card_no","money","checktime"),)

        def save(self, *args, **kwargs):
                settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
                if settings.CARDTYPE==1:
                        serino=get_cardserial_from_cache(self.card)
                        self.cardserial=serino


                super(CardCashSZ, self).save(*args, **kwargs)

class TimeSlice(models.Model):
        code = models.CharField(max_length=20,verbose_name=_(u'时间段编号'),editable=True)
        starttime= models.TimeField(verbose_name=_(u'开始时间'),  null=False,blank=False,editable=True)
        endtime = models.TimeField(verbose_name=_(u'结束时间'),  null=False, blank=False,editable=True)
        isvalid = models.NullBooleanField(verbose_name=_(u'是否有效'),null=False, default=True, blank=True, editable=True, choices=YESORNO)
        remarks = models.CharField(max_length=200,verbose_name=_(u'备注'),null=True,blank=True,editable=True)
        def __unicode__(self):
                return u"%s %s" %(self.starttime,self.endtime)
        class Admin:
                search_fields=[]
                @staticmethod
                def initial_data():
                        if TimeSlice.objects.count()==0:
                                TimeSlice(starttime=time(8,0),code="1",endtime=time(10,0),isvalid=1).save()
                                TimeSlice(starttime=time(10,0),code="2",endtime=time(14,0),isvalid=1).save()
                                TimeSlice(starttime=time(14,0),code="3",endtime=time(20,0),isvalid=1).save()
                                TimeSlice(starttime=time(20,0),code="4",endtime=time(23,0),isvalid=1).save()
                                TimeSlice(starttime=time(0,0),code="5",endtime=time(10,0),isvalid=0).save()
                                TimeSlice(starttime=time(0,0),code="6",endtime=time(10,0),isvalid=0).save()
                                TimeSlice(starttime=time(0,0),code="7",endtime=time(10,0),isvalid=0).save()
                                TimeSlice(starttime=time(0,0),code="8",endtime=time(10,0),isvalid=0).save()







        class Meta:
                verbose_name = _(u"卡现金收支")
                verbose_name_plural = verbose_name


#CARD_VALID = '1'
#CARD_LOST = '3'

#PRIVAGE_CARD = '1'
#OPERATE_CARD = '2'
#PRIVAGE = (
#       (PRIVAGE_CARD, _(u'管理卡')),
#       (OPERATE_CARD, _(u'操作卡')),
#       )

#CARDSTATUS = (
#        (CARD_VALID, _(u'有效')),
#        (CARD_LOST, _(u'挂失')),
#        (CARD_CANCEL, _(u'注销')),
#)

class CardManage(models.Model):
        sys_card_no = models.CharField(max_length=20,verbose_name=_(u'卡账号'),editable=False, null=True, blank=True,)
        card_no = models.CharField(max_length=20,verbose_name=_(u'卡号'),editable=False)
        pass_word = models.CharField(_(u'卡密码'), max_length=6, null=True, blank=True, editable=False)
        dining = models.ForeignKey(Dininghall,verbose_name=_(u'所属餐厅'),editable=True, blank=True,null=True)
        cardstatus = models.CharField(verbose_name=_(u'卡状态'), max_length=3, choices=CARDSTATUS, null=False, blank=True,editable=True)
        time = models.DateTimeField(verbose_name=_(u'发卡日期'), null=True, blank=True, editable=False, auto_now_add=True)
        card_privage = models.CharField(_(u'卡权限'), max_length=20, null=True, blank=True,default=1,choices = PRIVAGE)
        def __unicode__(self):
                return u"%s" %(self.card_no)

        class Admin:
                search_fields=[]
        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        {'name':'card_no','width':80,'label':unicode(CardManage._meta.get_field('card_no').verbose_name)},
                        {'name':'sys_card_no','width':80,'label':unicode(CardManage._meta.get_field('sys_card_no').verbose_name)},
                        {'name':'dining','width':80,'label':unicode(CardManage._meta.get_field('dining').verbose_name)},
                        {'name':'card_privage','width':80,'label':unicode(CardManage._meta.get_field('card_privage').verbose_name)},
                        {'name':'cardstatus','width':80,'label':unicode(CardManage._meta.get_field('cardstatus').verbose_name)},
                        {'name':'time','width':120,'label':unicode(CardManage._meta.get_field('time').verbose_name)}
                        ]
        class Meta:
                verbose_name = _(u"管理卡表")
                verbose_name_plural = verbose_name

        @staticmethod
        def objByCardno(cardno):
                if not cardno: return None
                obj=cache.get("%s_cardmanage_%s"%(settings.UNIT,cardno))
                if obj: return obj
                try:
                        objs=CardManage.objects.filter(card_no=cardno).order_by('-id')
                        if objs:
                                obj=objs[0]
                        else:
                                obj=None
                except:
                        obj=None
                if obj:
                        cache.set("%s_cardmanage_%s"%(settings.UNIT,cardno),obj)
                return obj

        def save(self, *args, **kwargs):
                cache.delete("%s_cardmanage_%s"%(settings.UNIT,self.card_no))
                cache.delete('CardManage')
                super(CardManage, self).save(*args, **kwargs)

#CONSUMEMODEL=(
#            (1,_(u'定值模式')),
#            (2,_(u'金额模式')),
#            (3,_(u'键值模式')),
#            (4,_(u'计次模式')),
#            (5,_(u'商品模式')),
#            (6,_(u'计时模式')),
#            (7,_(u'记账模式')),
#            (8,_(u'手工补消费')),
#            (9,_(u'设备纠错')),
#                  )

LOGFLAG=(
            (1,_(u'设备上传')),
            (2,_(u'系统补入')),
            (3,_(u'纠错补入')),
                  )
CASHTYPE1=(
                (1,_(u'充值')),
                (2,_(u'补贴')),
                #(3,_(u'批量充值')),
                (7,_(u'卡成本')),
                (4,_(u'支出卡成本')),
                (5,_(u'退款')),
                (6,_(u'消费')),
                (11,_(u'管理费')),
                (10,_(u'计次')),
                (8,_(u'手工补消费')),
                (9,_(u'纠错')),
                #(10,_(u'计次')),
                (12,_(u'计次纠错')),
#                (13,_(u'优惠记录')),
    )
CCASHTYPE=(
#            (1,_(u'充值')),
#            (2,_(u'补贴')),
            #(3,_(u'批量充值')),
#            (7,_(u'卡成本')),
#            (4,_(u'支出卡成本')),
#            (5,_(u'退款')),
            (6,_(u'消费')),
#            (11,_(u'管理费')),
#            (10,_(u'计次')),
            (8,_(u'补单')),
            (9,_(u'纠错')),
            (10,_(u'计次')),
#            (12,_(u'计次纠错')),
)

class ICConsumerList(models.Model):
        user_id =  models.CharField(_(u'人员ID'),null=False, max_length=20)
        user_pin =  models.CharField(_(u'工号'),null=False, max_length=20)
        user_name = models.CharField(_(u'姓名'),  null=True, max_length=24, blank=True, default="")
        dept = models.ForeignKey(department, verbose_name=_(u'部门'), editable=True, null=True)
        #    user_dept_name = models.CharField(_(u'部门名称'),max_length=100)
        card = models.CharField(_(u'卡号'), max_length=20, null=False, blank=True, editable=True, default='')
        sys_card_no =  models.IntegerField(verbose_name=_(u"卡账号"),null=True, blank=True,editable=True)
        dev_sn = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
        card_serial_num = models.IntegerField(_(u'卡流水号'), null=True, blank=True)
        dev_serial_num = models.IntegerField(_(u'设备流水号'),null=True,blank=True)
        pos_time= models.DateTimeField(verbose_name=_(u'消费时间'),blank=True,editable=True,null=True)
        convey_time= models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
        type_name = models.IntegerField(_(u'类型名称'),  null=True, blank=True,choices=CCASHTYPE)
        money = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'操作金额(元)'),null=False,blank=False,editable=True)
        balance = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'余额(元)'),null=False,blank=False,editable=True)
        allow_balance = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'余额(元)'),null=True,blank=True,editable=True)
        pos_model = models.IntegerField(_(u'消费类型'),null=True, blank=True,choices=CONSUMEMODEL)
        dining = models.ForeignKey(Dininghall,verbose_name=_(u'餐厅'),editable=True, blank=True,null=True)
        meal = models.ForeignKey(Meal,verbose_name=_(u"餐别"),null=True,editable=True)
        meal_data= models.DateTimeField(verbose_name=_(u'记餐日期'),blank=True,editable=True,null=True)
        create_operator =  models.CharField(_(u'操作员'),null=False, max_length=20)
        log_flag = models.IntegerField(_(u'记录标志'), null=True, blank=True, editable=False,choices=LOGFLAG)
        discount = models.IntegerField(verbose_name=_(u"折扣（%）"),default=0,null=True,blank=True,editable=False)#Integer
        def __unicode__(self):
                return u"%s"%self.pk
        class Admin:
                search_fields=['user_pin','user_name']

        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        {'name':'user_pin','width':80,'label':unicode(ICConsumerList._meta.get_field('user_pin').verbose_name)},
                        {'name':'user_name','width':80,'label':unicode(ICConsumerList._meta.get_field('user_name').verbose_name)},
                        {'name':'dept','width':80,'label':unicode(_('department name'))},
                        {'name':'card','width':80,'label':unicode(ICConsumerList._meta.get_field('card').verbose_name)},
                        {'name':'sys_card_no','width':80,'label':unicode(ICConsumerList._meta.get_field('sys_card_no').verbose_name)},
                        {'name':'type_name','width':80,'label':unicode(ICConsumerList._meta.get_field('type_name').verbose_name)},
                        {'name':'money','width':90,'label':unicode(ICConsumerList._meta.get_field('money').verbose_name)},
                        {'name':'balance','width':80,'label':unicode(ICConsumerList._meta.get_field('balance').verbose_name)},
                        {'name':'pos_model','width':80,'label':unicode(ICConsumerList._meta.get_field('pos_model').verbose_name)},
                        {'name':'dining','width':80,'label':unicode(ICConsumerList._meta.get_field('dining').verbose_name)},
                        {'name':'meal','width':50,'label':unicode(ICConsumerList._meta.get_field('meal').verbose_name)},
                        {'name':'dev_sn','width':100,'label':unicode(ICConsumerList._meta.get_field('dev_sn').verbose_name)},
                        {'name':'dev_serial_num','width':100,'label':unicode(ICConsumerList._meta.get_field('dev_serial_num').verbose_name)},
                        {'name':'card_serial_num','width':80,'label':unicode(ICConsumerList._meta.get_field('card_serial_num').verbose_name)},
                        {'name':'pos_time','width':120,'label':unicode(ICConsumerList._meta.get_field('pos_time').verbose_name)},
                        {'name':'convey_time','width':120,'label':unicode(ICConsumerList._meta.get_field('convey_time').verbose_name)},
                        {'name':'log_flag','width':80,'label':unicode(ICConsumerList._meta.get_field('log_flag').verbose_name)},
                        {'name':'create_operator','width':80,'label':unicode(ICConsumerList._meta.get_field('create_operator').verbose_name)}
                        ]
        class Meta:
                verbose_name = _(u"消费明细")
                verbose_name_plural = verbose_name
                unique_together = (("dev_sn", "sys_card_no","money","card_serial_num","dev_serial_num","pos_time","pos_model"),)





CASHTYPE=(
#            (1,_(u'充值')),
#            (2,_(u'补贴')),
            #(3,_(u'批量充值')),
#            (7,_(u'卡成本')),
#            (4,_(u'支出卡成本')),
#            (5,_(u'退款')),
            (6,_(u'消费')),
#            (11,_(u'管理费')),
#            (10,_(u'计次')),
            (8,_(u'补单')),
            (9,_(u'纠错')),
            (10,_(u'计次')),
#            (12,_(u'计次纠错')),
)

CONSUMEMODEL=(
            (1,_(u'定值模式')),
            (2,_(u'金额模式')),
            (3,_(u'键值模式')),
            (4,_(u'计次模式')),
            (5,_(u'商品模式')),
            (6,_(u'计时模式')),
            (7,_(u'记账模式')),
            (9,_(u'设备纠错')),
                  )

LOGFLAG=(
            (1,_(u'设备上传')),
            (2,_(u'手工补单')),
            (3,_(u'纠错补入')),
                  )

class ICConsumerListBak(models.Model):
        user_id =  models.CharField(_(u'人员ID'),null=False, max_length=20)
        user_pin =  models.CharField(_(u'人员编号'),null=False, max_length=20)
        user_name = models.CharField(_(u'姓名'),  null=True, max_length=24, blank=True, default="")
        dept = models.ForeignKey(department, verbose_name=_(u'部门'), editable=True, null=True)
        #    user_dept_name = models.CharField(_(u'部门名称'),max_length=100)
        card = models.CharField(_(u'卡号'), max_length=20, null=False, blank=True, editable=True, default='')
        sys_card_no =  models.IntegerField(verbose_name=_(u"卡账号"),null=True, blank=True,editable=True)
        dev_sn = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
        card_serial_num = models.IntegerField(_(u'卡流水号'), null=True, blank=True)
        dev_serial_num = models.IntegerField(_(u'设备流水号'),null=True,blank=True)
        pos_time= models.DateTimeField(verbose_name=_(u'消费时间'),blank=True,editable=True,null=True)
        convey_time= models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
        type_name = models.SmallIntegerField(_(u'类型名称'), null=True, blank=True,choices=CASHTYPE)
        money = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'操作金额(元)'),null=False,blank=False,editable=True)
        balance = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'余额(元)'),null=False,blank=False,editable=True)
        pos_model = models.IntegerField(_(u'消费类型'),null=True, blank=True,choices=CONSUMEMODEL)
        dining = models.ForeignKey(Dininghall,verbose_name=_(u'餐厅'),editable=True, blank=True,null=True)
        #    dining = models.CharField(_(u'餐厅'),max_length=20,null=True,blank=True,editable=True)
        meal = models.ForeignKey(Meal,verbose_name=_(u"餐别"),null=True,editable=True)
        meal_data= models.DateTimeField(verbose_name=_(u'记餐日期'),blank=True,editable=True,null=True)
        create_operator =  models.CharField(_(u'操作员'),null=False, max_length=20)
        log_flag = models.SmallIntegerField(_(u'记录标志'), null=True, blank=True, editable=False,choices=LOGFLAG)
        discount = models.SmallIntegerField(verbose_name=_(u"折扣"),default=0,null=True,blank=True,editable=False)#Integer

        def __unicode__(self):
                return u"%s"%self.pk
        class Admin:
                search_fields=['user_pin','user_name']

        class Meta:
                verbose_name = _(u"消费明细")
                verbose_name_plural = verbose_name
                unique_together = (("dev_sn", "sys_card_no","money","card_serial_num","dev_serial_num","pos_time","pos_model"),)

class StoreDetail(models.Model):
        list_code_id = models.CharField(verbose_name=_(u'明细编号'),max_length=20, editable=True, null=True, blank=False)
        dev_sn = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
        dev_serial_num = models.IntegerField(_(u'设备流水号'),null=True,blank=True)
        store_code = models.CharField(_(u'商品编号'),max_length=4,null=True,blank=True,editable=False)
        money = models.DecimalField (max_digits=9,decimal_places=2,verbose_name=_(u'金额(元)'),null=False,blank=False,editable=True)
        RecSum =  models.CharField(_(u'序号'),null=False, max_length=20)
        convey_time= models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
        def __unicode__(self):
                return u""

        class Admin:
                search_fields=[]

        class Meta:
                verbose_name = _(u"商品模式明细表")
                verbose_name_plural = verbose_name
                unique_together = (("list_code_id", "RecSum"))


class KeyDetail(models.Model):
        list_code_id = models.CharField(verbose_name=_(u'明细编号'),max_length=20, editable=True, null=True, blank=False)
        dev_sn = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
        dev_serial_num = models.IntegerField(_(u'设备流水号'),null=True,blank=True)
        key_code = models.CharField(_(u'按键编号'),max_length=4,null=True,blank=True,editable=False)
        money = models.DecimalField (max_digits=9,decimal_places=2,verbose_name=_(u'金额(元)'),null=False,blank=False,editable=True)
        RecSum =  models.CharField(_(u'序号'),null=False, max_length=20)
        convey_time= models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)

        def __unicode__(self):
                return ""
        class Admin:
                search_fields=[]

        class Meta:
                verbose_name = _(u"键值消费明细表")
                verbose_name_plural = verbose_name
                unique_together = (("list_code_id", "RecSum",))


#class TimeDetail(models.Model):
#       list_code_id = models.CharField(verbose_name=_(u'明细编号'),max_length=20, editable=True, null=True, blank=False)
#       dev_sn = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
#       dev_serial_num = models.IntegerField(_(u'设备流水号'),max_length=20,null=True,blank=True)
#       begin_time= models.DateTimeField(verbose_name=_(u'开始时间'),blank=True,editable=True,null=True)
#       end_time= models.DateTimeField(verbose_name=_(u'结束时间'),blank=True,editable=True,null=True)
#       begin_money = models.DecimalField (max_digits=9,decimal_places=2,verbose_name=_(u'开始余额(元)'),null=False,blank=False,editable=True)
#       end_money = models.DecimalField (max_digits=9,decimal_places=2,verbose_name=_(u'结束余额(元)'),null=False,blank=False,editable=True)
#       convey_time= models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
#
#       def __unicode__(self):
#               return ""
#       class Admin:
#               search_fields=[]
#
#       class Meta:
#               verbose_name = _(u"计时模式明细表")
#               verbose_name_plural = verbose_name
#               unique_together = (("list_code_id", "dev_sn","dev_serial_num"))





class IssueCard(models.Model):
    u'''发卡表'''
    UserID = models.ForeignKey(employee,verbose_name=_(u"人员"), null=True, blank=True,editable=True)
    cardno = models.CharField(verbose_name=_(u'卡号'), max_length=20, null=False, blank=False, editable=True)
    effectivenessdate = models.DateField(verbose_name=_(u'有效日期'), null=True, blank=True, editable=False)
    isvalid = models.NullBooleanField(verbose_name=_(u'是否有效'), choices=YESORNO, editable=False, default=1)
    cardpwd = models.CharField(verbose_name=_(u'卡密码'), max_length=20, null=True, blank=True, editable=False)
    failuredate = models.DateTimeField(verbose_name=_(u'失效日期'), null=True, blank=True, editable=False)
    cardstatus = models.CharField(verbose_name=_(u'卡状态'), max_length=3, choices=CARDSTATUS, null=False, blank=True,editable=True)
    issuedate = models.DateTimeField(verbose_name=_(u'发卡日期'), null=True, blank=True, editable=False)
    #pos add_column

    itype=models.ForeignKey(ICcard,verbose_name=_(u'卡类名称'), editable=True,null=True,blank=True,default=1)
    blance = models.DecimalField(verbose_name=_(u'余额'),max_digits=9,null=True, blank=True,default=0,decimal_places=2,editable=True)
    allow_balance = models.DecimalField(verbose_name=_(u'补贴余额'),max_digits=9,null=True, blank=True,default=0,decimal_places=2,editable=True)
    mng_cost = models.DecimalField (max_digits=8,decimal_places=2, verbose_name=_(u"管理费（元）"),null=True, blank=True, default=0)
    card_cost = models.DecimalField (max_digits=8,decimal_places=2, verbose_name=_(u"卡成本（元）"),null=True, blank=True, default=0)
    Password = models.CharField(_(u'超额密码'), max_length=6,default=123456,null=True, blank=True, editable=True)
    card_privage = models.CharField(_(u'卡类型'), max_length=20, null=True, blank=True, choices=PRIVAGE,default=POS_CARD)

    date_money = models.DecimalField(verbose_name=_(u"日消费最大金额"), max_digits=10,null=True, blank=True,default=0,decimal_places=2,editable=False)
    date_count = models.IntegerField(verbose_name=_(u"日消费次数"),default=0,null=True, blank=True,editable=False)
    meal_money = models.DecimalField(verbose_name=_(u"餐消费金额"), max_digits=10,null=True, blank=True,default=0,decimal_places=2,editable=False)
    meal_count = models.IntegerField(verbose_name=_(u"餐消费次数"), default=0,null=True, blank=True,editable=False)
    pos_date = models.DateField(verbose_name=_(u'消费日期'),blank=True,null=True,editable=False)
    pos_time = models.DateTimeField(verbose_name=_(u'最后消费时间'),blank=True,null=True,editable=False)
    meal_type = models.IntegerField(verbose_name=_(u"消费餐别"),null=True,default=0,blank=True,editable=False)
    sys_card_no =  models.IntegerField(verbose_name=_(u"卡账号"),null=True, blank=True,editable=True)
    card_serial_num = models.IntegerField(_(u'卡流水号'),default=0, null=True, blank=True)
    create_operator = models.CharField(_(u'操作'), max_length=20, null=True, blank=True, editable=False)
    def __unicode__(self):
        return u'%s'%self.cardno

    class Admin:
        search_fields=['UserID__PIN','UserID__EName']

    class Meta:
        verbose_name = _(u"发卡表")
        verbose_name_plural = verbose_name
        #unique_together = ()

        permissions = (
                ('issuecard_issuecard','issuecard'),('issuecard_oplosecard','oplosecard'),('issuecard_oprevertcard','oprevertcard'),('issuecard_cancelmanagecard','cancelmanagecard'),
                ('issuecard_nocardretirecard','nocardretirecard'),('issuecard_supplement','supplement'),('issuecard_reimburse','reimburse'),('issuecard_retreatcard','retreatcard'),('issuecard_updatecard','updatecard'),('issuecard_initcard','initcard'))

    def delete(self):
        cache.delete("%s_issuecard_valid_%s"%(settings.UNIT,self.cardno))
        cache.delete("%s_issuecard_%s"%(settings.UNIT,self.cardno))

        super(IssueCard, self).delete()

    def employee(self): #cached employee
        try:
            return employee.objByID(self.UserID_id)
        except:
            return None


    def save(self, *args, **kwargs):

            #is_manager_card = False#是否管理卡
            #is_pos_id_save = False #ID消费通信保存
            is_new = False#是否新增
            self.cardno = int(self.cardno)
            if self.pk == None:
                    is_new = True
            #try:
            #    old_card = IssueCard.objects.get(UserID=self.UserID,cardstatus__in = [CARD_OVERDUE,CARD_VALID])
            #except:
            #    old_card = None
            #
            #if get_option("POS"):#消费
            if is_new:
                    valid_card(str(self.cardno),self.UserID)


            if self.card_privage in [PRIVAGE_CARD,OPERATE_CARD]:#新增管理卡
                    if is_new:
                            #self.card_privage = self.card_privage
                            is_manager_card = True
            else:
                    if settings.CARDTYPE==-1:
                            settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
                    operateType=0
                    if 'operate_type' in kwargs.keys():
                            operateType= kwargs['operate_type']

                            del kwargs['operate_type']
                    if settings.CARDTYPE==1 and  is_new:
                            #try:
                            self.sys_card_no=self.UserID_id#ID 卡时用Userid做为卡账号，为了兼容
                            self.issuedate=datetime.date.today()
                            blance_valid(self.itype_id,self.blance,self.cardno)#验证余额
                            updateCardToEmp(self.UserID,self.cardno)
                            CardCashSZ(UserID=self.UserID,
                                   card = self.cardno,
                                   dept_id=self.UserID.DeptID_id,
                                   checktime = datetime.datetime.now(),
                                   CashType_id = 7,#cost type
                                   money = self.card_cost,
                                   sys_card_no=self.UserID_id,
                                   hide_column = 7,blance = self.blance ).save()
                            if self.blance :#and operateType!=16:
                                    CardCashSZ(UserID = self.UserID,
                                           card = self.cardno,
                                           dept_id=self.UserID.DeptID_id,
                                           checktime = datetime.datetime.now(),
                                           CashType_id =1,#cost type
                                           money = self.blance,
                                           sys_card_no=self.UserID_id,
                                           hide_column = 1,blance = self.blance).save()

                            CardCashSZ(UserID = self.UserID,
                                   card = self.cardno,
                                   dept_id=self.UserID.DeptID_id,
                                   checktime = datetime.datetime.now(),
                                   CashType_id =11,#cost type
                                   money=self.mng_cost,
                                   sys_card_no=self.UserID_id,
                                   hide_column=11,blance=self.blance).save()
                    #except Exception, e:
                            #import traceback;traceback.print_exc()
            #       elif get_option("POS_ID"):
            #           from django.db.models import Model
            #           op=threadlocals.get_current_user()
            #           if op:
            #               self.create_operator = op.username
            #           models.Model.save(self,args)
            #           is_pos_id_save = True
            #
            if is_new:
                    self.cardstatus=CARD_VALID
            #
            #
            #if get_option("ATT") and is_new and not is_manager_card:#考勤
            #    if not is_manager_card:
            #       from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
            #       adj_user_cmmdata(self.UserID, [], self.UserID.attarea.all())
            #
            ##同步卡号到门禁控制器
            #from mysite import settings
            #if get_option("IACCESS") and is_new and not is_manager_card :#门禁
            #    if not is_manager_card:
            #       from mysite.iclock.models.dev_comm_operate import sync_set_user
            #       sync_set_user(self.UserID.search_accdev_byuser(), [self.UserID])




            #cache.delete("%s_issuecard_%s"%(settings.UNIT,self.cardno))
            super(IssueCard, self).save(*args, **kwargs)
            if self.cardstatus==CARD_VALID:
                    cache.set("%s_issuecard_valid_%s"%(settings.UNIT,self.cardno),self)
            else:
                    cache.delete("%s_issuecard_valid_%s"%(settings.UNIT,self.cardno))
            cache.set("%s_issuecard_%s"%(settings.UNIT,self.cardno),self)

    @staticmethod
    def objByCardno(cardno,cardstatus=None):
            if not cardno: return None
            if cardstatus:
                    obj=cache.get("%s_issuecard_valid_%s"%(settings.UNIT,cardno))
            else:
                    obj=cache.get("%s_issuecard_%s"%(settings.UNIT,cardno))

            if obj: return obj
            try:
                    if cardstatus:
                            obj=IssueCard.objects.get(cardno=cardno,cardstatus=cardstatus)
                    else:
                            objs=IssueCard.objects.filter(cardno=cardno).order_by('-id')
                            if objs:
                                    obj=objs[0]

            except:
                    obj=None
            if obj:
                    if cardstatus:
                            cache.set("%s_issuecard_valid_%s"%(settings.UNIT,cardno),obj)
                    else:
                            cache.set("%s_issuecard_%s"%(settings.UNIT,cardno),obj)
            return obj

    @staticmethod
    def colModels():
            return [
                    {'name':'id','hidden':True},
                    {'name':'PIN','index':'','sortable':False,'width':80,'label':unicode(_('PIN'))},
                    {'name':'EName','sortable':False,'width':80,'label':unicode(employee._meta.get_field('EName').verbose_name)},
                    {'name':'DeptName','sortable':False,'width':100,'label':unicode(_('department name'))},
                    {'name':'cardno','width':80,'label':unicode(IssueCard._meta.get_field('cardno').verbose_name)},
                    {'name':'sys_card_no','width':60,'label':unicode(IssueCard._meta.get_field('sys_card_no').verbose_name)},
                    {'name':'card_privage','width':80,'label':unicode(IssueCard._meta.get_field('card_privage').verbose_name)},
                    {'name':'cardstatus','width':80,'label':unicode(IssueCard._meta.get_field('cardstatus').verbose_name)},
                    {'name':'itype','width':80,'label':unicode(IssueCard._meta.get_field('itype').verbose_name)},
                    {'name':'blance','width':100,'label':unicode(IssueCard._meta.get_field('blance').verbose_name)},
                    {'name':'issuedate','width':150,'label':unicode(IssueCard._meta.get_field('issuedate').verbose_name)},

                    ]


class IclockDininghall(models.Model):
    dining = models.ForeignKey(Dininghall)
    SN = models.ForeignKey(iclock)
    def __unicode__(self):
            return unicode(self.SN)
    class Admin:
            list_display=("SN","dining", )
    class Meta:
            verbose_name=_(u"所属餐厅")
            verbose_name_plural=verbose_name
            unique_together = (("SN", "dining"),)

            permissions = (
                    ('iclockdininghall_cardcashsz','cardcashsz'),('iclockdininghall_icconsumerlist','icconsumerlist'),('iclockdininghall_reports','reports'),
                    )


class HandConsume(models.Model):
    #    user=EmpPoPForeignKey(verbose_name=_(u"人员"),null=False,editable=True)
    pin = models.CharField(verbose_name=_(u'工号'), max_length=20, null=True, blank=True, editable=True)
    name = models.CharField(verbose_name=_(u'姓名'), max_length=20, null=True, blank=True, editable=True)
    sys_card_no = models.CharField(max_length=20,verbose_name=_(u'卡账号'),editable=True, null=True, blank=True,)
    card = models.CharField(verbose_name=_(u'卡号'), max_length=20, null=False, blank=True, editable=True)
    blance = models.DecimalField(verbose_name=_(u'余额'),max_digits=20,null=True, blank=True,decimal_places=2,editable=True)
    card_serial_no = models.IntegerField(_(u'卡流水号'), null=True, blank=True)

    #   pos_type = models.SmallIntegerField(verbose_name=_(u"消费类型"), choices=((1,'设备自动'),(2,'手工补单'),))#choices=...)
    meal = models.ForeignKey(Meal,verbose_name=_(u"餐别"),null=False,editable=True)
    hand_date = models.DateTimeField(verbose_name=_(u"消费时间"),blank=False,null=False)
    money = models.DecimalField (max_digits=8,decimal_places=2,verbose_name=_(u"消费金额"))
    posdevice = models.ForeignKey(iclock,verbose_name=_(u'设备'), null=False,editable=True)#关联设备
    create_operator = models.CharField(_(u'操作'), max_length=20, null=True, blank=True, editable=False)

    def __unicode__(self):
            return ""

    class Meta:
            verbose_name=_(u"手工补消费表")
            verbose_name_plural=verbose_name
    def save(self, *args, **kwargs):
            if self.pk == None:
                    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))

                    try:
                            iscarobj = IssueCard.objByCardno(self.card,cardstatus=CARD_VALID)
                    except:
                            iscarobj = None
                    if iscarobj:
                            from mysite.base import threadlocals

                            #op=threadlocals.get_current_user()
                            ding=IclockDininghall.objects.get(SN=self.posdevice.SN)
                            if settings.CARDTYPE==1:
                                    newblan = iscarobj.blance-self.money
                                    if newblan<0:
                                            raise Exception(_(u"余额不足"))
                                    if iscarobj.itype is not None:
                                            iccardobj= ICcard.objects.get(pk=iscarobj.itype_id)
                                            lessmoney = iccardobj.less_money#卡类最小余额
                                            maxmoney = iccardobj.max_money#卡类最大余额
                                            if lessmoney>newblan and lessmoney>0:
                                                    raise Exception(_(u"编号%s超出卡最小余额")%iscarobj.UserID)
                                            if newblan>maxmoney and maxmoney>0:
                                                    raise Exception(_(u"编号%s超出卡最大余额")%iscarobj.UserID)


                                    CardCashSZ(UserID_id=iscarobj.UserID_id,
                                             dept_id = employee.objByID(iscarobj.UserID_id).DeptID_id,
                                             card=self.card,
                                             checktime=self.hand_date,
                                             CashType=CardCashType.objects.get(id=8),#消费类型
                                             money=self.money,
                                             sn=self.posdevice.SN,
                                             hide_column=8,
                                             dining = ding.dining,
                                             blance = newblan,
                                             pos_model=8,
                                             meal=self.meal,
                                           ).save(force_insert=True)
                                    iscarobj.blance=newblan
                                    iscarobj.save(force_update=True)
                                    self.blance = newblan
                            else:
                                    ICConsumerList(user_id=iscarobj.UserID_id,
                                    dept_id = employee.objByID(iscarobj.UserID_id).DeptID_id,
                                    user_pin=employee.objByID(iscarobj.UserID_id).PIN,
                                    user_name=employee.objByID(iscarobj.UserID_id).EName,
                                    card = self.card,
                                    sys_card_no = self.sys_card_no,
                                    dev_sn = self.posdevice.SN,
                                    card_serial_num =  self.card_serial_no,
                                    pos_time = self.hand_date,
                                    type_name = 8,
                                    money = self.money,
                                    balance = self.blance,
                                    dining = ding.dining,
                                    meal = self.meal,
                                    pos_model = 8,
                                    create_operator = self.create_operator or '',
                                    log_flag = 2
                                    ).save()
                                    #print '--------------++'
                                    #iscarobj.blance=self.blance
                                    #iscarobj.save()
                                    #print '++++++++++++++--'
                            super(HandConsume, self).save(*args, **kwargs)#保存本身
                    else:
                            raise Exception(_(u"当前操作卡片不是有效卡，操作失败"))








    @staticmethod
    def colModels():
            return [
                    {'name':'id','hidden':True},
                    {'name':'pin','width':80,'label':unicode(HandConsume._meta.get_field('pin').verbose_name)},
                    {'name':'name','width':80,'label':unicode(HandConsume._meta.get_field('name').verbose_name)},
                    {'name':'card','width':80,'label':unicode(HandConsume._meta.get_field('card').verbose_name)},
                    {'name':'sys_card_no','width':80,'label':unicode(HandConsume._meta.get_field('sys_card_no').verbose_name)},
                    {'name':'card_serial_no','width':80,'label':unicode(HandConsume._meta.get_field('card_serial_no').verbose_name)},
                    {'name':'money','width':80,'label':unicode(HandConsume._meta.get_field('money').verbose_name)},
                    {'name':'blance','width':80,'label':unicode(HandConsume._meta.get_field('blance').verbose_name)},
                    {'name':'meal','width':80,'label':unicode(HandConsume._meta.get_field('meal').verbose_name)},
                    {'name':'posdevice','width':80,'label':unicode(HandConsume._meta.get_field('posdevice').verbose_name)},
                    {'name':'hand_date','width':120,'label':unicode(HandConsume._meta.get_field('hand_date').verbose_name)},
                    {'name':'create_operator','width':80,'label':unicode(HandConsume._meta.get_field('create_operator').verbose_name)}
                    ]

    class Admin:
            search_fields=['pin','name']

class Allowance(models.Model):
    UserID = models.ForeignKey(employee,verbose_name=_(u"人员"), null=False,blank=False,editable=True)
    #    pin = models.CharField(_(u'人员编号'), db_column="badgenumber", null=False, max_length=20)
    #    ename = models.CharField(_(u'姓名'), db_column="name", null=True, max_length=24, blank=True, default="")
    #    cardno = models.CharField(_(u'卡号'), max_length=20, null=False, blank=True, editable=True, default='')
    money = models.DecimalField (max_digits=8,decimal_places=2,verbose_name=_(u"补贴金额"))
    receive_money = models.DecimalField (max_digits=8,decimal_places=2,verbose_name=_(u"领取金额"),null=True,editable=False)
    is_pass = models.IntegerField(verbose_name=_(u"是否通过审核"), editable=False,default=0,choices=ISYESORNO,blank=True,null=False)
    pass_name = models.CharField(max_length=100,verbose_name=_(u"审核通过人员"),blank=True,null=True,editable=False)
    valid_date = models.DateTimeField(verbose_name=_(u"补贴有效日期"),blank=True,null=True,editable=True)
    allow_date = models.DateTimeField(verbose_name=_(u"补贴时间"),blank=False,null=False,editable=False)
    receive_date = models.DateTimeField(verbose_name=_(u"补贴领取时间"),blank=True,null=True,editable=False)
    remark = models.CharField(max_length=200,verbose_name=_(u"备注"),blank=True,null=True)
    batch = models.CharField(max_length=20,verbose_name=_(u"补贴批次"),blank=True,null=True,editable=True)
    base_batch = models.CharField(max_length=20,verbose_name=_(u"补贴基次"),blank=True,null=True,editable=False)
    is_ok = models.IntegerField(verbose_name=_(u"是否领取"),default=0,choices=ISYESORNO,blank=True,null=True,editable=False)
    is_transfer = models.IntegerField(verbose_name=_(u"是否下发"), editable=False,default=0,choices=ISYESORNO,blank=True,null=True)
    sys_card_no =  models.IntegerField(verbose_name=_(u"卡账号"),default=0,null=True, blank=True,editable=False)
    create_operator = models.CharField(_(u'操作'), max_length=20, null=True, blank=True, editable=False)

    def __unicode__(self):
        return u"%s"%self.UserID

    @staticmethod
    def colModels():
        return [
                {'name':'id','hidden':True},
                {'name':'PIN','index':'','frozen':True,'sortable':False,'width':80,'label':unicode(_('PIN'))},
                {'name':'EName','sortable':False,'frozen':True,'width':80,'label':unicode(employee._meta.get_field('EName').verbose_name)},
                {'name':'DeptName','sortable':False,'width':100,'label':unicode(_('department name'))},
                {'name':'cardno','width':80,'sortable':False,'label':unicode(IssueCard._meta.get_field('cardno').verbose_name)},
                {'name':'sys_card_no','width':80,'label':unicode(Allowance._meta.get_field('sys_card_no').verbose_name)},
                {'name':'money','width':80,'label':unicode(Allowance._meta.get_field('money').verbose_name)},
                {'name':'receive_money','width':80,'label':unicode(Allowance._meta.get_field('receive_money').verbose_name)},
                {'name':'batch','width':80,'label':unicode(Allowance._meta.get_field('batch').verbose_name)},
                {'name':'is_ok','width':80,'label':unicode(Allowance._meta.get_field('is_ok').verbose_name)},
                {'name':'is_pass','width':90,'label':unicode(Allowance._meta.get_field('is_pass').verbose_name)},
                {'name':'pass_name','width':100,'label':unicode(Allowance._meta.get_field('pass_name').verbose_name)},
                {'name':'receive_date','width':120,'label':unicode(Allowance._meta.get_field('receive_date').verbose_name)},
                {'name':'valid_date','width':120,'label':unicode(Allowance._meta.get_field('valid_date').verbose_name)},
                {'name':'allow_date','width':120,'label':unicode(Allowance._meta.get_field('allow_date').verbose_name)},
                {'name':'remark','width':100,'label':unicode(Allowance._meta.get_field('remark').verbose_name)}
                ]

    class Meta:
        verbose_name=_(u"补贴表")
        verbose_name_plural=verbose_name
        unique_together = (("batch", "sys_card_no"))
        permissions = (
                        ('allowanceAudit_allowance','Audit Allowance'),
                )

    class Admin:
        search_fields=['UserID__PIN','UserID__EName']
        lock_fields=['UserID']

    def save(self, *args, **kwargs):
        super(Allowance, self).save(*args, **kwargs)



LOSECARDSTATUS = (
        ('3', _(u'挂失')),
        ('1', _(u'解挂')),
)


class LoseUniteCard(models.Model):
        sys_card_no = models.CharField(max_length=20,verbose_name=_(u'卡账号'),editable=False, null=True, blank=True,)
        UserID = models.ForeignKey(employee,verbose_name=_(u"人员"), null=True, editable=True)
        cardno = models.CharField(verbose_name=_(u'卡号'), max_length=20,null=False, blank=True, editable=True)
        itype=models.ForeignKey(ICcard,verbose_name=_(u'卡类'),editable=True,null=True,blank=True)
        cardstatus = models.CharField(verbose_name=_(u'卡状态'), max_length=3, choices=LOSECARDSTATUS, null=True, blank=True,editable=False)
        Password = models.CharField(_(u'卡密码'), max_length=6, null=True, blank=True, editable=False)
        Losetime = models.DateTimeField(verbose_name=_(u'操作日期'), null=True, blank=True, editable=False, auto_now_add=True)#default=datetime.datetime.now().strftime("%Y-%m-%d"))
        card_privage = models.CharField(_(u'卡类型'), max_length=20, null=True, blank=True, choices=PRIVAGE,default=POS_CARD)
        create_operator = models.CharField(_(u'操作'), max_length=20, null=True, blank=True, editable=False)
        def __unicode__(self):
                try:
                        return u"%s,%s"%(self.UserID,self.cardno)
                except:
                        return u"%s,%s"%(self.UserID,self.cardno)
        @staticmethod
        def colModels():
                return [
                        {'name':'id','hidden':True},
                        {'name':'PIN','index':'','sortable':False,'width':80,'label':unicode(_('PIN'))},
                        {'name':'EName','sortable':False,'width':80,'label':unicode(employee._meta.get_field('EName').verbose_name)},
                        {'name':'cardno','width':80,'label':unicode(LoseUniteCard._meta.get_field('cardno').verbose_name)},
                        {'name':'sys_card_no','width':80,'label':unicode(LoseUniteCard._meta.get_field('sys_card_no').verbose_name)},
                        {'name':'itype','width':80,'label':unicode(LoseUniteCard._meta.get_field('itype').verbose_name)},
                        {'name':'cardstatus','width':80,'label':unicode(LoseUniteCard._meta.get_field('cardstatus').verbose_name)},
                        {'name':'Losetime','width':120,'label':unicode(LoseUniteCard._meta.get_field('Losetime').verbose_name)},
                        {'name':'create_operator','width':80,'label':unicode(LoseUniteCard._meta.get_field('create_operator').verbose_name)}
                        ]
        class Meta:
                verbose_name=_(u"挂失解挂表")
                verbose_name_plural=verbose_name
        class Admin:
                search_fields=['UserID__PIN','UserID__EName']


class CardCashSZBak(models.Model):    #卡现金收支备份表
        user_pin =  models.CharField(_(u'人员编号'),null=False, max_length=20)
        user_name = models.CharField(_(u'姓名'),  null=True, max_length=24, blank=True, default="")
        user_dept_name = models.CharField(_(u'部门名称'),db_column="DeptName",max_length=100)
        physical_card_no = models.CharField(_(u'原始卡号'), max_length=20, null=False, blank=True, editable=True, default='')
        sys_card_no = models.CharField(_(u'卡账号'), max_length=20, null=False, blank=True, editable=True, default='')
        cardserial = models.IntegerField(_(u'卡流水号'), null=True, blank=True)
        blance = models.DecimalField(verbose_name=_(u'余额'),max_digits=20,null=True, blank=True,decimal_places=2,editable=True)
        money = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'操作金额(元)'),null=False,blank=False,editable=True)
        #    type= CashTypeForeignKey(verbose_name=_(u'类型'),null=False,blank=False,editable=True)
        hide_column = models.SmallIntegerField(_(u'操作类型'), null=True, blank=True) #1:充值;2:补贴;4:支出卡成本;5:退款;6:发卡;7:卡成本;8:工补消费;9:纠错;10:计次;11:管理费;12:换卡;13:值优惠;14:无卡退卡
        checktime= models.DateTimeField(verbose_name=_(u'操作时间'),blank=True,editable=True,null=True)

        # convey_time = models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
        sn_name = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
        serialnum = models.IntegerField(_(u'设备流水号'),null=True,blank=True)
        convey_time = models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
        allow_type = models.SmallIntegerField(_(u'补贴类型'), null=True, blank=True)#0:累加补贴;1:清零补贴;
        allow_batch = models.SmallIntegerField(_(u'补贴批次'), null=True, blank=True)
        allow_base_batch = models.SmallIntegerField(_(u'补贴基次'), null=True, blank=True)
        log_flag = models.SmallIntegerField(_(u'记录类型'), null=True,default=2, blank=True, editable=False)#1:设备上传;2:系统添加;8888:纠错补入;5:日期异常

        def __unicode__(self):
                return ""
        class Meta:
                verbose_name=_(u'卡现金收支备份表')
                verbose_name_plural=verbose_name


class ReplenishCard(models.Model):
        UserID = models.ForeignKey(employee,verbose_name=_(u"人员"), null=True, editable=True)
        oldcardno = models.CharField(verbose_name=_(u'原卡号'), max_length=20,null=True, blank=True, editable=True)
        newcardno = models.CharField(verbose_name=_(u'现卡号'), max_length=20,null=True, blank=True, editable=True)
        blance = models.DecimalField(verbose_name=_(u'卡金额'),max_digits=20,null=True, blank=True,decimal_places=2,editable=True)
        time = models.DateTimeField(verbose_name=_(u'补卡日期'), null=True, blank=True, editable=False,auto_now_add=True)
        create_operator = models.CharField(_(u'操作'), max_length=20, null=True, blank=True, editable=False)
        def __unicode__(self):
                return ""
        class Meta:
                verbose_name=_(u"换卡表")
                verbose_name_plural=verbose_name
        class Admin:
                search_fields=[]


class TimeBrush(models.Model):
        sn = models.CharField(_(u'设备序列号'), max_length=20, null=True, blank=True)
        serialnum = models.IntegerField(_(u'设备流水号'),null=True,blank=True)
        carno = models.CharField(max_length=10,verbose_name=_(u'卡号'),editable=True)
        begintime = models.DateTimeField(verbose_name=_(u'开始时间'),null=True,blank=True,editable=True)
        endtime = models.DateTimeField(verbose_name=_(u'结束时间'),null=True,blank=True,editable=True)
        itype = models.IntegerField(verbose_name=_(u'状态'),null=True,blank=True,editable=True)

        def __unicode__(self):
                return u"%s" %(self.carno)
        class Meta:
                verbose_name=_(u"计时消费表")
                verbose_name_plural=verbose_name
        def save(self,*args, **kwargs):
                super(TimeBrush, self).save(*args, **kwargs)

class TimeDetail(models.Model):
        list_code_id = models.CharField(verbose_name=_(u'明细编号'),max_length=20, editable=True, null=True, blank=False)
        sn = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
        serial_num = models.IntegerField(_(u'设备流水号'),null=True,blank=True)
        begintime= models.DateTimeField(verbose_name=_(u'开始时间'),blank=True,editable=True,null=True)
        endtime= models.DateTimeField(verbose_name=_(u'结束时间'),blank=True,editable=True,null=True)
        begin_money = models.DecimalField (max_digits=9,decimal_places=2,verbose_name=_(u'开始余额(元)'),null=False,blank=False,editable=True)
        end_money = models.DecimalField (max_digits=9,decimal_places=2,verbose_name=_(u'结束余额(元)'),null=False,blank=False,editable=True)
        convey_time= models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)

        def __unicode__(self):
                return ""
        class Meta:
                verbose_name=_(u"计时消费表")
                verbose_name_plural=verbose_name
                unique_together = (("list_code_id", "sn","serial_num"))



IDCONSUMEMODEL=(
            (2,_(u'金额模式')),
            (1,_(u'定值模式')),
            (4,_(u'计次模式')),

            (3,_(u'键值模式')),
            (5,_(u'商品模式')),
            (6,_(u'计时模式')),
            (7,_(u'消费纠错')),
            (8,_(u'计次纠错')),
            (9,_(u'计时开始纠错')),
            (10,_(u'计时结束纠错')),
                  )


class PosLog(models.Model):
        devname= models.CharField(_(u'设备名称'),max_length=20,null=True,blank=True)
        sn= models.CharField(_(u'序列号'),max_length=20,null=True,blank=True)
        serialnum = models.CharField(_(u'设备流水号'),max_length=20,null=True,blank=True)
        pin = models.CharField(_(u'人员编号'), db_column="badgenumber", null=True, max_length=20)
        carno = models.CharField(_(u'卡号'),max_length=10, null=True, blank=True)
        posmodel = models.IntegerField(_(u'消费操作'),null=True, blank=True,choices=IDCONSUMEMODEL)
        posmoney = models.DecimalField(verbose_name=_(u'消费金额'),max_digits=20,null=True, blank=True,decimal_places=2)
        blance = models.DecimalField(verbose_name=_(u'卡上余额'),max_digits=20,null=True, blank=True,decimal_places=2)
        posOpTime = models.DateTimeField(verbose_name=_(u'消费时间'),blank=True,editable=True,null=True)
        def __unicode__(self):
                return u"%s,%s"%(self.sn,self.carno)
        def save(self, *args,**kwargs):
                super(PosLog, self).save(*args, **kwargs)

        class Admin:
                pass

class ZfbWxFulllog(models.Model):
        sn= models.CharField(_(u'序列号'),max_length=20,null=True,blank=True)
        devname= models.CharField(_(u'设备名称'),max_length=20,null=True,blank=True)
        serialnum = models.CharField(_(u'设备流水号'),max_length=20,null=True,blank=True)
        pin = models.CharField(_(u'人员编号'), db_column="badgenumber", null=True, max_length=20)
        carno = models.CharField(_(u'卡号'),max_length=10, null=True, blank=True)
        posoptime = models.DateTimeField(verbose_name=_(u'消费时间'),blank=True,editable=True,null=True)
        posmoney = models.DecimalField(verbose_name=_(u'消费金额'),max_digits=20,null=True, blank=True,decimal_places=2)
        blance = models.DecimalField(verbose_name=_(u'卡上余额'),max_digits=20,null=True, blank=True,decimal_places=2)
        logtype = models.IntegerField(_(u'交易类型'),null=True, blank=True)
        opid = models.IntegerField(_(u'操作ID'),null=True, blank=True)
        paysource = models.IntegerField(_(u'交易方式'),null=True, blank=True)
        tradeno = models.CharField(_(u'订单号'),max_length=100, null=True, blank=True)

        def __unicode__(self):
                return u"%s,%s"%(self.sn,self.carno)
        def save(self, *args,**kwargs):
                super(ZfbWxFulllog, self).save(*args, **kwargs)

        class Admin:
                pass

class BackCard(models.Model):
        UserID = models.ForeignKey(employee,verbose_name=_(u"人员"), null=True, editable=True)
        cardno = models.CharField(verbose_name=_(u'卡号'), max_length=20, null=False, blank=False, editable=True)
        sys_card_no =  models.IntegerField(verbose_name=_(u"卡账号"),null=True, blank=True,editable=True)
        card_serial_num = models.IntegerField(verbose_name=_(u'卡流水号'),null=True,blank=True)
        operate_type = models.IntegerField(_(u'退卡类型'), null=True, blank=True,default=15,choices=SZCASHTYPE)#15:'有卡退卡' 14:'无卡退卡'
        card_money = models.DecimalField (max_digits=8,decimal_places=2, verbose_name=_(u"支出卡成本(元)"),null=True, blank=True, default=0)
        back_money = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'退款金额(元)'),null=True,blank=True,editable=True)
        checktime = models.DateTimeField(verbose_name=_(u'退卡时间'),blank=True,editable=True,null=True)
        create_operator = models.CharField(_(u'操作员'), max_length=20, null=True, blank=True, editable=False)
        
        def __unicode__(self):
                return u"%s"%(self.carno)
        @staticmethod
        def colModels():
                return [
                        {'name':'user_pin','index':'','sortable':False,'width':80,'label':unicode(_(u'工号'))},
                        {'name':'user_name','sortable':False,'width':80,'label':unicode(_(u'姓名'))},
                        {'name':'DeptName','sortable':False,'width':100,'label':unicode(_(u'部门'))},
                        {'name':'cardno','sortable':False,'width':80,'label':unicode(_(u'卡号'))},
                        {'name':'sys_card_no','sortable':False,'width':80,'label':unicode(_(u'卡账号'))},
                        {'name':'card_serial_num','sortable':False,'width':80,'label':unicode(_(u'卡流水号'))},
                        {'name':'card_money','sortable':False,'width':80,'label':unicode(_(u'支出卡成本'))},
                        {'name':'back_money','sortable':False,'width':80,'label':unicode(_(u'退款金额'))},
                        {'name':'checktime','sortable':False,'width':120,'label':unicode(_(u'退卡时间'))},
                        {'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
                        ]
        class Meta:
                verbose_name=_(u"退卡表")
                verbose_name_plural=verbose_name
        class Admin:
                search_fields=[]
        def save(self, *args, **kwargs):
                super(BackCard, self).save(*args, **kwargs)

#为客户定制表
if hasattr(settings,'OEM_CODE') and settings.OEM_CODE=='20160811-01':
        class details(models.Model):
                SN = models.CharField(  max_length=20,verbose_name=_('registration device'), null=True, blank=True, editable=False)
                name = models.CharField(_('Emp Name'),null=True,max_length=24, blank=True, default="")
                Card = models.CharField(max_length=20, null=True, blank=True)
                PosTime = models.DateTimeField(null=True, blank=True)
                serialnum = models.CharField(_(u'设备流水号'),max_length=20,null=True,blank=True)
                RESERVED=models.CharField(max_length=20,null=True, blank=True)
                class Admin:
                        pass
                class Meta:
                        unique_together = (("Card", "PosTime"))

        class books(models.Model):
                SN = models.CharField(  max_length=20,verbose_name=_('registration device'), null=True, blank=True, editable=False)
                name = models.CharField(_('Emp Name'),null=True,max_length=24, blank=True, default="")
                Card = models.CharField(max_length=20, null=True, blank=True)
                BookDate= models.DateField(null=True, blank=True)
                StartTime=models.DateTimeField( null=True, blank=True)
                EndTime=models.DateTimeField(null=True, blank=True)
                BookCount = models.IntegerField(null=True, blank=True)
                sCount = models.IntegerField(null=True, blank=True)
                RESERVED=models.CharField(max_length=20,null=True, blank=True)
                class Admin:
                        pass
