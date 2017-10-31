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

ROOMSTATE=(
	(0,_(u'空闲')),
	(1,_(u'占用')),
	(2,_(u'禁用')),
)
BOOLEANS=((0,_("No")),(1,_("Yes")),)

class MeetLocation(models.Model):#会议室
	roomNo = models.CharField(u'会议室编号',null=False,max_length=10)
	roomName = models.CharField(u'会议室名称',max_length=40)
	Address = models.CharField(u'会议室地址',max_length=80,null=True,blank=True)
	admin = models.CharField(u'负责人',max_length=40,null=True,blank=True)
	Phone = models.CharField(_(u'联系电话'),max_length=20,blank=True,null=True)
	State = models.IntegerField(u'当前状态',default=0, editable=False,choices=ROOMSTATE) #2停用 0空闲
	DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)

	def __unicode__(self):
		return unicode(self.roomName)
	def get_devices(self):
		SNs=meet_devices.objects.filter(LocationID=self).values('SN')
		if not SNs:
			return ''
		else:
			if len(SNs)>1:
				url=(SNs[0]['SN']+u",... <a href='#' onclick='Check_devices(%d);'><img title='%s' src='../media/img/qu.png'/></a>"%(self.pk,_(u'显示使用的设备')))
				return url
			else:
				return SNs[0]['SN']
#	@staticmethod
	def getState(self):
		try:
			if self.State==2:
				return u'停用'
			localList=Meet.objects.filter(Starttime__lt=datetime.datetime.now(),Endtime__gt=datetime.datetime.now(),LocationID=self.id)
			if len(localList)>0:
				return u'占用'
			else:
				return u'空闲'
		except Exception,e:
			print 888,e
			pass
	def getImgUrl(self, default=None):
		if self.id:
			fname="%s"%(str(self.id)+".jpg")
			imgUrl='/iclock/file/meetmap/'+fname
			fullName=getStoredFileName("meetmap", None, str(self.id)+".jpg")
			if os.path.exists(fullName):
				import random
				imgUrl += '?time=%s'%str(random.random()).split('.')[1]
				return imgUrl
		return default
	def rmThumbnail(self):
		# tbName=getStoredFileName("meetmap", None, str(self.id)+".jpg")
		# if os.path.exists(tbName):
		# 	os.remove(tbName)
		try:
			url=MeetLocation.getThumbnailUrl()
			if url:
				try:
					fullUrl=MeetLocation.getImgUrl()
				except: #only have thumbnail, no real picture
					return "<img src='%s' />"%url
			else:
				if not fullUrl:
					return "<img src='%s' />"%url
			return "<a href='#' onmouseover=showphotozdiv(this,'%s') onmouseout='dropphotozdiv()'><img src='%s' /></a>"%(fullUrl, url)
		except Exception,e:
			print ""
			pass
	
		return ""
	def getThumbnailUrl(self, default=None,tag=True):
		import random
		varile = str(random.random()).split('.')[1]

		if not self.id: return default
        # if hasattr(settings,'SHOWEMPPHOTO') and settings.SHOWEMPPHOTO==0:
        #     if facetemp.objects.filter(UserID=self.id).count()==0:
        #         return ""
		if os.path.exists(getStoredFileName("meetmap", None, str(self.id)+".jpg")) :
			tbName=getStoredFileName("meetmap/thumbnail", None, str(self.id)+".jpg")
			tbUrl=getStoredFileURL("meetmap/thumbnail", None, str(self.id)+".jpg")
			if os.path.exists(tbName):#取路径先判断压缩图是否已经存在
				return tbUrl+'?'+varile
			else:#压缩图不存在 创建
				fullName=getStoredFileName("meetmap", None, str(self.id)+".jpg")
				if os.path.exists(fullName):
					if createThumbnail(fullName, tbName):
						return tbUrl+'?'+varile
		return ''
	class Admin:
		list_display=("roomNo","roomName" )
		search_fields = ['roomNo','roomName']
	class Meta:
		verbose_name=_(u"会议室")
		verbose_name_plural=verbose_name
		unique_together = ("roomNo","DelTag")

	def save(self):
		try:
			location = MeetLocation.objects.get(roomNo=self.roomNo)
			if location.DelTag<>0:
				location.DelTag = 0
			location.roomName = self.roomName
			location.Address = self.Address
			location.admin = self.admin
			location.Phone = self.Phone
			super(MeetLocation,location).save()
		except:
			super(MeetLocation,self).save()


	@staticmethod	
	def colModels():
		return [
			{'name':'id','hidden':True},
			{'name':'roomNo','width':100,'label':unicode(MeetLocation._meta.get_field('roomNo').verbose_name)},
			{'name':'roomName','width':220,'label':unicode(MeetLocation._meta.get_field('roomName').verbose_name)},
			{'name':'Address','width':220,'sortable':False,'label':unicode(MeetLocation._meta.get_field('Address').verbose_name)},
			{'name':'admin','width':80,'sortable':False,'label':unicode(MeetLocation._meta.get_field('admin').verbose_name)},
			{'name':'Phone','width':80,'sortable':False,'label':unicode(MeetLocation._meta.get_field('Phone').verbose_name)},
			{'name':'State','sortable':False,'width':80,'label':unicode(MeetLocation._meta.get_field('State').verbose_name)},
			{'name':'latestState','sortable':False,'width':80,'label':unicode(_(u'近期状态'))},
			{'name':'devices','sortable':False,'width':170,'label':unicode(_(u'使用的设备'))},
			{'name':'photo','search':False,'sortable':False,'width':100,'label':unicode(_(u'会议室平面图'))},
			#{'name':'DeptNo','sortable':False,'width':80,'label':unicode(u'序号')}
			]	


#会议室设备
class meet_devices(models.Model):
	LocationID = models.ForeignKey(MeetLocation, verbose_name=_(u"会议室"), editable=False)
	SN = models.ForeignKey(iclock, verbose_name=_(u"设备"), editable=False)
	@staticmethod	
	def colModels():
		return [{'name':'id','hidden':True},
			{'name':'LocationID','width':100,'index':'LocationID__roomNo','label':unicode(_(u'会议室编号'))},
			{'name':'SN','index':'SN','width':180,'label':unicode(_(u'设备'))},
		        {'name':'device_detail','sortable':False,'width':120,'label':unicode(_(u'操作'))},

		        ]
	class Admin:
		list_display=()
		search_fields = []
	class Meta:
		verbose_name=_(u'会议室设备')
		verbose_name_plural=_('device_details')
		unique_together = (("LocationID",'SN'),)



class Meet(models.Model):#会议表
	id=models.AutoField(primary_key=True, null=False,editable=False)
	MeetID=models.CharField(u'会议编号',null=False,max_length=24)
	conferenceTitle=models.CharField(u'会议名称',null=False,max_length=40, blank=False, default="")
	MeetContents=models.CharField(u'会议内容',max_length=80, null=True, blank=True)
	LocationID=models.ForeignKey(MeetLocation, db_column='LocationID',verbose_name=u'会议室', null=True,blank=True,default="")
	Starttime=models.DateTimeField(u'开始时间',max_length=8, null=False, blank=False)
	Endtime=models.DateTimeField(u'结束时间',max_length=8, null=False, blank=False)
	CheckIn = models.IntegerField(_(u'must C/In'),null=True,default=1,blank=True,choices=BOOLEANS)
	CheckOut = models.IntegerField(_(u'must C/Out'),null=True,default=1,blank=True,choices=BOOLEANS)
	Enrolmenttime=models.DateTimeField(u'报到时间',max_length=8, null=True, blank=True)
	EnrolmentLocation=models.CharField(u'报到地点',max_length=80, null=True, blank=True)
	LastEnrolmenttime=models.DateTimeField(u'最迟签到时间',max_length=8, null=True, blank=True)
	EarlySignOfftime=models.DateTimeField(u'最早签退时间',max_length=8, null=True, blank=True)
	LastSignOfftime=models.DateTimeField(u'最晚签退时间',max_length=8, null=True, blank=True)
	lunchtimestr=models.DateTimeField(u'午餐开始时间',max_length=8, null=True, blank=True)
	lunchtimeend=models.DateTimeField(u'午餐结束时间',max_length=8, null=True, blank=True)
	Contact=models.CharField(u'会务联系人',null=True,max_length=40, blank=True, default="")
	ContactPhone=models.CharField(u'会务联系电话',max_length=20, null=True, blank=True)
	Sponsor=models.CharField(u'主办单位',max_length=80, null=True, blank=True)
	Coorganizer=models.CharField(u'协办单位',max_length=80, null=True, blank=True)
	Should=models.IntegerField(u'应到', default=0,editable=False)
	Real=models.IntegerField(u'实到',default=0,editable=False)
	Rate=models.FloatField(u'出席率', default=0,editable=False)
	sitOn=models.IntegerField(u'列席',default=0,editable=False)
	leave=models.IntegerField(u'请假人数',default=0,editable=False)
	late=models.IntegerField(u'迟到人数',default=0,editable=False)
	early=models.IntegerField(u'早退人数',default=0,editable=False)
	absent=models.IntegerField(u'缺席人数',default=0,editable=False)
	DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)
	ApplyDate=models.DateTimeField(_(u'apply date'), null=True,  blank=True, editable=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,  blank=True, editable=False)
	def __unicode__(self):
		return unicode(self.conferenceTitle)
	def empCount(self):
		return Meet_details.objects.filter(MeetID=self.id).count()
	@staticmethod	
	def colModels():
		return [
			{'name':'id','hidden':True,'frozen':True},
			{'name':'MeetID','width':80,'label':unicode(Meet._meta.get_field('MeetID').verbose_name),'frozen':True},
			{'name':'conferenceTitle','width':200,'label':unicode(Meet._meta.get_field('conferenceTitle').verbose_name),'frozen':True},
			{'name':'MeetContents','width':220,'sortable':False,'label':unicode(Meet._meta.get_field('MeetContents').verbose_name)},
			{'name':'LocationID','width':80,'sortable':False,'label':unicode(Meet._meta.get_field('LocationID').verbose_name)},
				{'name':'meet_detail','sortable':False,'width':150,'label':unicode(_(u'操作'))},
				{'name':'Starttime','width':100,'sortable':False,'label':unicode(Meet._meta.get_field('Starttime').verbose_name)},
			{'name':'Endtime','sortable':False,'width':100,'label':unicode(Meet._meta.get_field('Endtime').verbose_name)},
			{'name':'Enrolmenttime','sortable':False,'width':100,'label':unicode(Meet._meta.get_field('Enrolmenttime').verbose_name)},
			{'name':'EnrolmentLocation','width':100,'sortable':False,'label':unicode(Meet._meta.get_field('EnrolmentLocation').verbose_name)},
			{'name':'lunchtimestr','width':100,'sortable':False,'label':unicode(Meet._meta.get_field('lunchtimestr').verbose_name)},
			{'name':'lunchtimeend','width':100,'sortable':False,'label':unicode(Meet._meta.get_field('lunchtimeend').verbose_name)},
			{'name':'LastEnrolmenttime','width':100,'sortable':False,'label':unicode(Meet._meta.get_field('LastEnrolmenttime').verbose_name)},
			{'name':'EarlySignOfftime','width':100,'sortable':False,'label':unicode(Meet._meta.get_field('EarlySignOfftime').verbose_name)},
			{'name':'LastSignOfftime','width':100,'sortable':False,'label':unicode(Meet._meta.get_field('LastSignOfftime').verbose_name)},
			{'name':'Contact','width':80,'sortable':False,'label':unicode(Meet._meta.get_field('Contact').verbose_name)},
			{'name':'ContactPhone','width':90,'sortable':False,'label':unicode(Meet._meta.get_field('ContactPhone').verbose_name)},
			{'name':'Sponsor','width':80,'sortable':False,'label':unicode(Meet._meta.get_field('Sponsor').verbose_name)},
			{'name':'Coorganizer','width':80,'sortable':False,'label':unicode(Meet._meta.get_field('Coorganizer').verbose_name)},
			{'name':'Should','sortable':False,'width':60,'label':unicode(u'参会人数')},
			#{'name':'Real','sortable':False,'width':60,'label':unicode(Meet._meta.get_field('Real').verbose_name)},
			#{'name':'Rate','sortable':False,'width':60,'label':unicode(Meet._meta.get_field('Rate').verbose_name)},
			#{'name':'sitOn','sortable':False,'width':60,'label':unicode(Meet._meta.get_field('sitOn').verbose_name)},
			#{'name':'leave','sortable':False,'width':60,'label':unicode(Meet._meta.get_field('leave').verbose_name)},
			#{'name':'late','sortable':False,'width':60,'label':unicode(Meet._meta.get_field('late').verbose_name)},
			#{'name':'early','sortable':False,'width':60,'label':unicode(Meet._meta.get_field('early').verbose_name)},
			#{'name':'absent','sortable':False,'width':60,'label':unicode(Meet._meta.get_field('absent').verbose_name)}




			]	
	@staticmethod
	def objByID(id):
		e=cache.get("%s_iclock_meet_%s"%(settings.UNIT,id))
		if e: return e
		try:
			u=Meet.objects.get(id=id)
		except:
			#connection.close()
			u=Meet.objects.get(id=id)
		cache.set("%s_iclock_meet_%s"%(settings.UNIT,u.id),u)
#		cache.set("%s_iclock_emp_PIN_%s"%(settings.UNIT,u.PIN),u)
		return u
	@staticmethod
	def objByMeetID(MeetID):
		e=cache.get("%s_iclock_meet_%s"%(settings.UNIT,MeetID))
		if e: return e
		try:
			u=Meet.objects.get(MeetID=MeetID)
		except:
			connection.close()
			u=Meet.objects.get(id=MeetID)
		cache.set("%s_iclock_meet_%s"%(settings.UNIT,u.MeetID),u)
#		cache.set("%s_iclock_emp_PIN_%s"%(settings.UNIT,u.PIN),u)
		return u
	def save(self):
		try:
			cache.delete("%s_iclock_meet_%s"%(settings.UNIT,self.id))
			cache.delete("%s_iclock_meet_%s"%(settings.UNIT,self.MeetID))
		except:
			pass
		if self.LocationID:#判断会议有无时间冲突
			if self.Starttime and self.Endtime:
				d1=self.Starttime
				d2=self.Endtime
				if Meet.objects.filter(LocationID=self.LocationID).filter(Q(Starttime__gte=d1,Starttime__lte=d2)|Q(Starttime__lt=d1,Endtime__gt=d1)).exclude(MeetID=self.MeetID).count()>0:
					raise Exception(u'%s'%(u'会议室被占用'))
		
		super(Meet,self).save()
		
		
		
		
	class Admin:
		list_display=("MeetID","conferenceTitle", )
		search_fields = ['MeetID','conferenceTitle']
	class Meta:
		unique_together = ("MeetID",)
		verbose_name=_(u"会议")
		verbose_name_plural=verbose_name
		permissions = (
					('meeting_reports','meeting_reports'),
					('meeting_monitor','meeting_monitor'),
		)
	def ShouldEmp(self):
		return Meet_details.objects.filter(MeetID_id=self.id).count()

AUDIT_STATES=(
	(0,_('Apply')),
	(2,_('Accepted')),
	(3,_('Refused')),
)

class Meet_order(models.Model):#会议表
	id=models.AutoField(primary_key=True, null=False,editable=False)
	MeetID=models.CharField(u'会议编号',null=False,max_length=24)
	conferenceTitle=models.CharField(u'会议名称',null=False,max_length=40, blank=False, default="")
	MeetContents=models.CharField(u'会议内容',max_length=80, null=True, blank=True)
	LocationID=models.ForeignKey(MeetLocation, db_column='LocationID',verbose_name=u'会议室', null=True,blank=True,default="")
	Starttime=models.DateTimeField(u'开始时间',max_length=8, null=False, blank=False)
	Endtime=models.DateTimeField(u'结束时间',max_length=8, null=False, blank=False)
	CheckIn = models.IntegerField(_(u'must C/In'),null=True,default=1,blank=True,choices=BOOLEANS)
	CheckOut = models.IntegerField(_(u'must C/Out'),null=True,default=1,blank=True,choices=BOOLEANS)
	Enrolmenttime=models.DateTimeField(u'报到时间',max_length=8, null=True, blank=True)
	EnrolmentLocation=models.CharField(u'报到地点',max_length=80, null=True, blank=True)
	LastEnrolmenttime=models.DateTimeField(u'最迟签到时间',max_length=8, null=True, blank=True)
	EarlySignOfftime=models.DateTimeField(u'最早签退时间',max_length=8, null=True, blank=True)
	LastSignOfftime=models.DateTimeField(u'最晚签退时间',max_length=8, null=True, blank=True)
	lunchtimestr=models.DateTimeField(u'午餐开始时间',max_length=8, null=True, blank=True)
	lunchtimeend=models.DateTimeField(u'午餐结束时间',max_length=8, null=True, blank=True)
	Contact=models.CharField(u'会务联系人',null=True,max_length=40, blank=True, default="")
	ContactPhone=models.CharField(u'会务联系电话',max_length=20, null=True, blank=True)
	Sponsor=models.CharField(u'主办单位',max_length=80, null=True, blank=True)
	Coorganizer=models.CharField(u'协办单位',max_length=80, null=True, blank=True)
	State=models.SmallIntegerField(_('state'), null=True, default=0, blank=True, choices=AUDIT_STATES, editable=False)
	ApplyDate=models.DateTimeField(_('apply date'), null=True,  blank=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,  blank=True)
	def __unicode__(self):
		return unicode(self.MeetID)
	def empCount(self):
		return Meet_details.objects.filter(MeetID=self.id).count()
	@staticmethod	
	def colModels():
		return [
			{'name':'id','hidden':True,'frozen':True},
			{'name':'MeetID','width':80,'label':unicode(Meet_order._meta.get_field('MeetID').verbose_name),'frozen':True},
			{'name':'conferenceTitle','width':200,'label':unicode(Meet_order._meta.get_field('conferenceTitle').verbose_name),'frozen':True},
			{'name':'State','index':'State','width':80,'label':unicode(Meet_order._meta.get_field('State').verbose_name)},
			{'name':'MeetContents','width':220,'sortable':False,'label':unicode(Meet_order._meta.get_field('MeetContents').verbose_name)},
			{'name':'LocationID','width':80,'sortable':False,'label':unicode(Meet_order._meta.get_field('LocationID').verbose_name)},
			{'name':'Starttime','width':100,'sortable':False,'label':unicode(Meet_order._meta.get_field('Starttime').verbose_name)},
			{'name':'Endtime','sortable':False,'width':100,'label':unicode(Meet_order._meta.get_field('Endtime').verbose_name)},
			{'name':'Enrolmenttime','sortable':False,'width':100,'label':unicode(Meet_order._meta.get_field('Enrolmenttime').verbose_name)},
			{'name':'EnrolmentLocation','width':80,'sortable':False,'label':unicode(Meet_order._meta.get_field('EnrolmentLocation').verbose_name)},
			{'name':'LastEnrolmenttime','width':100,'sortable':False,'label':unicode(Meet_order._meta.get_field('LastEnrolmenttime').verbose_name)},
			{'name':'lunchtimestr','width':100,'sortable':False,'label':unicode(Meet_order._meta.get_field('lunchtimestr').verbose_name)},
			{'name':'lunchtimeend','width':100,'sortable':False,'label':unicode(Meet_order._meta.get_field('lunchtimeend').verbose_name)},
			{'name':'EarlySignOfftime','width':100,'sortable':False,'label':unicode(Meet_order._meta.get_field('EarlySignOfftime').verbose_name)},
			{'name':'LastSignOfftime','width':100,'sortable':False,'label':unicode(Meet_order._meta.get_field('LastSignOfftime').verbose_name)},
			{'name':'Contact','width':80,'sortable':False,'label':unicode(Meet_order._meta.get_field('Contact').verbose_name)},
			{'name':'ContactPhone','width':90,'sortable':False,'label':unicode(Meet_order._meta.get_field('ContactPhone').verbose_name)},
			{'name':'Sponsor','width':80,'sortable':False,'label':unicode(Meet_order._meta.get_field('Sponsor').verbose_name)},
			{'name':'Coorganizer','width':80,'sortable':False,'label':unicode(Meet_order._meta.get_field('Coorganizer').verbose_name)},
			{'name':'ApplyDate','sortable':False,'width':120,'label':unicode(Meet_order._meta.get_field('ApplyDate').verbose_name)}
			]	
	
	class Admin:
		list_display=("MeetID","conferenceTitle", )
		search_fields = ['MeetID','conferenceTitle']
	class Meta:
		verbose_name=_(u"会议预约")
		verbose_name_plural=verbose_name
		permissions = (
					('orderAudit_meet_order','meeting_order_Audit'),
		)
		
	def save(self):
			if self.LocationID:#判断会议有无时间冲突
				if self.Starttime and self.Endtime:
					d1=self.Starttime
					d2=self.Endtime
					if Meet.objects.filter(LocationID=self.LocationID).filter(Q(Starttime__gte=d1,Starttime__lte=d2)|Q(Starttime__lt=d1,Endtime__gt=d1)).exclude(MeetID=self.MeetID).count()>0:
						raise Exception(u'%s'%(u'会议室被占用'))
			
			super(Meet_order,self).save()
		
		
		
class MeetMessage(models.Model):#会议通知
	id=models.AutoField(primary_key=True,null=False,editable=False)
	MessageID = models.CharField(u'消息编号',null=False,max_length=24)
	MessageNotice = models.CharField(u'消息标题',max_length=40)
	MessageContent = models.TextField(_('Content'),null=True,blank=True)
	Meet_ID = models.ForeignKey(Meet, db_column='Meet_ID',verbose_name=u'会议', null=True,blank=True,default="")
	#MessageContent = models.CharField(u'消息内容',max_length=40)
	Emails = models.TextField(u'邮件地址',null=True,blank=True)
	CopyForEmail = models.CharField(u'抄送地址',max_length=1024,null=True,blank=True)
	SendTime = models.DateTimeField(u'发送时间',max_length=8, null=True, blank=True)
	Reserved =models.CharField(max_length=40, editable=False, null=True, blank=True)
	Reserved2 =models.IntegerField(default=1, editable=False, null=True, blank=True)
	DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)

	def __unicode__(self):
		return unicode(self.MessageID)
	class Admin:
		list_display=("MessageID","MessageNotice" )
		search_fields = ['MessageID','MessageNotice']
	class Meta:
		#db_table = 'MeetMessage'
		verbose_name=_(u"会议通知")
		verbose_name_plural=verbose_name
	@staticmethod	
	def colModels():
		return [
			{'name':'id','hidden':True,'frozen':True},
			{'name':'MessageID','width':80,'label':unicode(MeetMessage._meta.get_field('MessageID').verbose_name),'frozen':True},
			{'name':'MessageNotice','width':200,'label':unicode(MeetMessage._meta.get_field('MessageNotice').verbose_name),'frozen':True},
			#{'name':'MessageContent','width':220,'sortable':False,'label':unicode(MeetMessage._meta.get_field('MessageContent').verbose_name)},
			{'name':'Meet_ID','width':80,'sortable':False,'label':unicode(MeetMessage._meta.get_field('Meet_ID').verbose_name)},
			{'name':'Emails','width':220,'sortable':False,'label':unicode(MeetMessage._meta.get_field('Emails').verbose_name)},
			{'name':'CopyForEmail','width':220,'sortable':False,'label':unicode(MeetMessage._meta.get_field('CopyForEmail').verbose_name)},
			{'name':'SendTime','width':130,'sortable':False,'label':unicode(MeetMessage._meta.get_field('SendTime').verbose_name)},
		]




#参会人员明细
class Meet_details(models.Model):
	MeetID = models.ForeignKey(Meet, verbose_name=_(u"会议"), editable=False)
	UserID = models.ForeignKey(employee, verbose_name=_(u"参会人员"), editable=False)
	@staticmethod	
	def colModels():
		return [{'name':'id','hidden':True},
			{'name':'MeetID','width':100,'index':'MeetID__MeetID','label':unicode(_(u'会议编号'))},
			{'name':'PIN','index':'UserID__PIN','width':140,'label':unicode(_('PIN'))},
			{'name':'EName','sortable':False,'width':120,'label':unicode(employee._meta.get_field('EName').verbose_name)},
			{'name':'DeptName','sortable':False,'width':200,'label':unicode(_('department name'))},
			{'name':'meet_detail','sortable':False,'width':120,'label':unicode(_(u'操作'))},
			]
	class Admin:
		list_display=()
		search_fields = []
	class Meta:
		verbose_name=_(u'参会人员')
		verbose_name_plural=_('meet_details')
		unique_together = (("MeetID",'UserID'),)





#参会人员模板
class participants_tpl(models.Model):
	Name = models.CharField(_(u'模板名称'), max_length=100,null=False,blank=False,editable=True)
	DelTag = models.IntegerField(_(u'删除标记'),default=0, editable=False, null=True, blank=True)
	def __unicode__(self):
		return unicode(self.Name)
	def save(self):
		try:
			tpl=participants_tpl.objects.get(Name=self.Name)
			if tpl.DelTag==1:
				print 'okokok'
				tpl.DelTag=0
				tpl.Name=self.Name
				super(participants_tpl,tpl).save()
			else:
				super(participants_tpl,self).save()
		except:
			super(participants_tpl,self).save()
	def empCount(self):
		return participants_details.objects.filter(participants_tplID=self.id).count()
	@staticmethod	
	def colModels():
		return [{'name':'id','hidden':True},
			{'name':'tplID','width':100,'index':'id','label':unicode(_(u'模板编号'))},
			{'name':'Name','width':300,'label':unicode(_(u'模板名称'))},
			{'name':'empCount','sortable':False,'width':80,'label':unicode(_('EmpCount'))},
			{'name':'participants_detail','sortable':False,'width':120,'label':unicode(_(u'操作'))}
			]
	class Admin:
		list_display=()
		search_fields = ['Name']
	class Meta:
		verbose_name=_(u'参会人员模板')
		verbose_name_plural=_('participants_tpl')
		unique_together = ("Name","DelTag")
#参会人员模板详细记录
class participants_details(models.Model):
	participants_tplID = models.ForeignKey(participants_tpl, verbose_name=_(u"模板编号"), editable=False)
	UserID = models.ForeignKey(employee, verbose_name=_(u"参会人员"), editable=False)
	@staticmethod	
	def colModels():
		return [{'name':'id','hidden':True},
			{'name':'tplID','width':100,'index':'participants_tplID','label':unicode(_(u'模板编号'))},
			{'name':'PIN','index':'UserID__PIN','width':140,'label':unicode(_('PIN'))},
			{'name':'EName','sortable':False,'width':120,'label':unicode(employee._meta.get_field('EName').verbose_name)},
			{'name':'DeptName','sortable':False,'width':200,'label':unicode(_('department name'))},
			{'name':'participants_detail','sortable':False,'width':120,'label':unicode(_(u'操作'))},
			]
	class Admin:
		list_display=()
		search_fields = []
	class Meta:
		verbose_name=_(u'人员模板')
		verbose_name_plural=_('participants_details')
		unique_together = (("participants_tplID",'UserID'),)


class Minute(models.Model):#会议纪要
	FileNumber = models.IntegerField(u'档案编号',primary_key=True)
	FileName = models.CharField(u'档案名称',max_length=40,null=True, blank=True)
	MeetID = models.ForeignKey(Meet,  verbose_name=_(u"会议编号"),)
	Content = models.TextField(u'档案内容',max_length=2048,null=True,blank=True)
	SubmitUser = models.CharField(u'记录人',max_length=40,null=True,blank=True)
	SubTime = models.DateTimeField(u'提交时间',max_length=8, null=True, blank=True)
	Appendixes = models.CharField(u'附件',max_length=40,editable=False)
	Reserved1 =models.CharField(max_length=40, editable=False)
	Reserved2 =models.IntegerField(default=0, editable=False)
	def __unicode__(self):
		return unicode(self.FileNumber)
	@staticmethod	
	def colModels():
		return [{'name':'id','hidden':True},
			{'name':'FileNumber','width':80,'label':unicode(Minute._meta.get_field('FileNumber').verbose_name),'frozen':True},
			{'name':'FileName','width':120,'label':unicode(Minute._meta.get_field('FileName').verbose_name),'frozen':True},
			{'name':'MeetID','width':80,'sortable':False,'label':unicode(Minute._meta.get_field('MeetID').verbose_name)},
			{'name':'conferenceTitle','width':120,'sortable':False,'label':unicode(Meet._meta.get_field('conferenceTitle').verbose_name)},
			##{'name':'Content','width':220,'sortable':False,'label':unicode(Minute._meta.get_field('Content').verbose_name)},
			{'name':'SubmitUser','width':120,'sortable':False,'label':unicode(Minute._meta.get_field('SubmitUser').verbose_name)},
			{'name':'SubTime','width':130,'sortable':False,'label':unicode(Minute._meta.get_field('SubTime').verbose_name)},
			{'name':'Appendixes','width':280,'sortable':False,'label':unicode(Minute._meta.get_field('Appendixes').verbose_name)},
		]
	class Admin:
		list_display=("FileNumber","FileName" )
		search_fields = ['FileNumber','MeetID__MeetID']
	class Meta:
		verbose_name=_(u"会议纪要")
		verbose_name_plural=verbose_name
	