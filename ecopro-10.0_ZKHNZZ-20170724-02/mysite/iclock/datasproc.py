#coding=utf-8
#from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _
from mysite.utils import *
from mysite.iclock.models import *
from django.db.models.fields import AutoField, FieldDoesNotExist
from django.contrib.auth.models import  Permission, Group
from django.contrib.auth import get_user_model
#from mysite.iclock.datautils import GetModel, hasPerm
import datetime
from mysite.base.models import *

def getLocalText(ID):
	Texts={
		'Trial':u'%s'%_(u'试用版'),
		'TrialDays':u'%s'%_(u'试用天数:'),
		'TrialDay':u'%s'%_(u'试用截止'),
		'ClientID':u'%s'%_(u'客户编号'),
		'Company':u'%s'%_(u'使用单位'),
        'Database': u'%s' % _(u'数据库'),

        'RegisterTime':u'%s'%_(u'授权时间'),
		'Devices':u'%s'%_(u'授权点数'),
		'SoftwareSN':u'%s'%_(u'序列号:'),
		'SupportExplore':u'<span>%s:</span><br>%s'%(_(u'建议使用的浏览器'),u"IE8+/火狐/谷歌/Opera/Baidu/360"),
		'Display':u'<span>%s:</span><br />%s'%(_(u'建议显示器分辨率'),'1366*768'),
		'SupportSystem':u'<span>%s x64位:</span><br />%s'%(_(u'支持的系统'),'Windows 7, Windows 8/8.1, Windows Server 2008/2012'),
		'SupportDB':u'<span>%s:</span><br />%s'%(_(u'支持的数据库'),'MySql,PostgreSQL,DB2,Oracle10g+,SQLServer 2005/2008/2012/2014/2016'),
		'About':u"<a id='id_about' style='text-decoration:underline;color:white;'>%s</a>"%(_(u'关于本系统')),
		'Sorry':u'%s'%_('Sorry'),
		'Authorized0':u'%s'%_(u'Authorized encryption system does not find the lock, try restarting the service!'),
		'Authorized2':u'%s'%_(u'Authorize the use of the system over time, please contact the supplier!'),
		'Authorized3':u'%s'%_(u'System exceeds the number of authorized equipment, please contact the supplier!'),
		'Authorized-1':u'%s'%_('Table is marked as crashed and should be repaired'),
		'Authorized-9':u'%s'%_('Connection Failed'),
		'Authorized-5':u'%s'%_(u'管理员未开启员工自助登陆功能'),
		'Authorized-6':u'%s'%_(u'非法的用户名'),
		'Invalid username':u'%s'%_('Invalid username or passowrd, please try again.'),
		'Login Failed':u'%s'%_('Login Failed'),
		'Login Out':u'%s'%_(u"注销"),
        'copyright':u'Copyright ©2017 ZKTECO CO.,LTD.All Rights Reserved',
		'Password change successful':u'%s'%_('Password change successful'),
		'Password revision failure, please enter again':u'%s'%_('Password revision failure, please enter again'),
		'Not allowed to change passwords':u'%s'%(_('Not allowed to change passwords'))
	}
	try:
		return Texts[ID]
	except:
		return ''



def transLeaName(leaveID):
	LeaName={ #999: _('BL'),
		  1000:unicode(_('OK')),
		  1007:unicode(_('Hol.')),
		  1008:unicode(_('NoIn')),
		  1009:unicode(_('NoOut')),
		  1004:unicode(_('Absent')),
		  1001:unicode(_('Late')),
		  1002:unicode(_('Early')),
		  1010:unicode(_('ROT')),
		  1005:unicode(_('OT')),
		  1013:unicode(_('FOT')),
		  1012:unicode(_('OUT')),
		  1011:unicode(_('BOUT')),
		  1003:unicode(_('ALF'))}
	return LeaName[leaveID]

def transLeaveName(lName):
	if lName=='Sick leave':
		return unicode(_('Sick leave'))
	elif lName=='Private affair leave':
		return unicode(_('Private affair leave'))
	elif lName=='Home leave':
		return unicode(_('Home leave'))
	elif lName=='Business leave':
		return unicode(_('Business leave'))
	else:
		return lName

def transExceptionName():
	#return (u"%s"%_('FOT'),u"%s"%_('OT'),u"%s"%_('OUT'),u"%s"%_('BL'))
	return (_('FOT'),_('OT'),_('OUT'),_('BL'))

def GetUnitText(AttUnit):
	UnitName={0:_('Day'),1:_('Hour'),2:_('Min.'),3:_('WDay'),4:_('Times')}
	if AttUnit>=0 and AttUnit<=4:
		return u"%s"%UnitName[AttUnit]
	else:
		return ''
def get_DEV_STATUS():
	return (_(u"禁用"),_('Online'),_('Communicating'),_('Offline'),_(u'门打开'),_(u'门关闭'),_(u'胁迫报警'),_(u'门被意外打开'),_(u'机器被拆除'),_(u'解除报警'))
	


	
def ConstructBaseFields():
	r={}
	strFieldNames=['deptid','badgenumber','username','ssn']
	FieldNames=['userid','deptid','badgenumber','Workcode','username','duty','realduty','late','early','absent','overtime','out','dutyinout','clockin',
	    'clockout','noin','noout','worktime','atttime','SSpeDayNormal','SSpeDayWeekend','SSpeDayHoliday','SSpeDayNormalOT','SSpeDayWeekendOT','SSpeDayHolidayOT','Leave']
	for t in FieldNames:
		if t in strFieldNames:
			r[t]=''
		else:
			r[t]=''
	r['userid']=-1;
	FieldCaption=[_('userid'),_('department name'),_('PIN'),_('NewPin'),_('name'),_('duty'),_('realduty'),_('late'),_('early'),_('absent'),_('overtime'),_('OUT'),_('dutyinout'),_('clockin'),
		    _('clockout'),_('noin'),_('noout'),_('WorkTime'),_('AttTime'),_('NormalDay'),_('WeekendDay'),_('HolidayDay'),_(u'平加'),_(u'周加'),_(u'节加'),_('Leave')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]
	
def ConstructBaseFields1(d1,d2):
	r={}
	strFieldNames=['deptid','badgenumber','username']
	FieldNames=['userid','deptid','badgenumber','Workcode','username']
	FieldCaption=[_('userid'),_('department name'),_('PIN'),_('NewPin'),_('name'),]
	r1=['duty','realduty','late','early','absent','SSpeDayHoliday','SSpeDayNormalOT','SSpeDayWeekendOT','SSpeDayHolidayOT','overtime','Leave']
	for t in FieldNames:
		if t in strFieldNames:
			r[t]=''
	for t in r1:
		r[t]=''
	t=d1
	
	weeks=[u'周一',u'周二',u'周三',u'周四',u'周五',u'周六',u'周日']
	
	while t<=d2:
		d=str(t.month)+'-'+str(t.day)
		FieldNames.append(d)
		r[d]=''
		d=str(t.month)+'-'+str(t.day)+u'%s'%weeks[t.weekday()]
		FieldCaption.append(d)
		
		
		
		#f=str(t.day)
		#fc='%s %s'%(str(t.day),weeks[t.weekday()])
		#r[]=''
		#FieldNames.append(f)
		#FieldCaption.append(fc)
		t=t+datetime.timedelta(1)
	FieldNames=FieldNames+r1
	FieldCaption=FieldCaption+[_('duty'),_('realduty'),_('late'),_('early'),_('absent'),_('HolidayDay'),_('NormalDayOT'),_('WeekendDayOT'),_('HolidayDayOT'),_('overtime'),_('Leave')]
	r['userid']=-1
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]



def ConstructBaseFields2(d1,d2):
	r={}
	strFieldNames=['deptid','badgenumber','username']
	FieldNames=['userid','deptid','badgenumber','username']
	FieldCaption=[_('userid'),_('department name'),_('PIN'),_('name'),]
#	r1=['duty','realduty','late','early','absent','overtime','Leave']
	for t in FieldNames:
		if t in strFieldNames:
			r[t]=''
#	for t in r1:
#		r[t]=''
	t=d1
	while t<=d2:
		f=str(t.day)
		r[f]=''
		FieldNames.append(f)
		FieldCaption.append(f)
		t=t+datetime.timedelta(1)
#	FieldNames=FieldNames+r1
#	FieldCaption=FieldCaption+[_('duty'),_('realduty'),_('late'),_('early'),_('absent'),_('overtime'),_('Leave')]
	r['userid']=-1
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]

def FetchBaseDisabledFields(user,tblName,itemType='report_fields_define'):
	try:
		item=ItemDefine.objects.filter(Author=user,ItemName=tblName,ItemType=itemType)
		if item:
			if item[0].ItemValue:
				return item[0].ItemValue.split(',')
	except:
		pass
	return []
#
def FetchDisabledFields(user,tblName,itemType='report_fields_define'):
	re= FetchBaseDisabledFields(user,tblName,itemType)
	#if re:
	#	return re
	#User=get_user_model()
	#admins=User.objects.filter(is_superuser=True)
	#for tadmin in admins:
	#	re= FetchBaseDisabledFields(tadmin,tblName,itemType)
	#	if re:
	#		return re
	
	return re
def FetchModelFields(tbl):
	if tbl=="attShifts":
		attshiftsbasefields= ['DeptID','PIN','Workcode','EName','AttDate','SchId','ClockInTime','ClockOutTime','StartTime','EndTime','WorkDay','RealWorkDay','Late','Early','Absent','OverTime','WorkTime','MustIn','MustOut','SSpeDayNormal','SSpeDayWeekend','SSpeDayHoliday','AttTime','SSpeDayNormalOT','SSpeDayWeekendOT','SSpeDayHolidayOT']
		return attshiftsbasefields
	else:
		return  [f.column for f in tbl._meta.fields if not isinstance(f, AutoField)]
def FetchModelFieldsCaption(tbl):
	if tbl=="attShifts":
		f=[_('department name'),_('PIN'),_('NewPin'),_('EName'),_('AttDate'),_('SchId'),_('ClockInTime'),_('ClockOutTime'),_('attStartTime'),_('attEndTime'),_('WorkDay'),_('RealWorkDay'),_('Late'),_('Early'),_('Absent'),_('OverTime'),_('WorkTime'),_('MustIn'),_('MustOut'),_('SSpeDayNormal'),_('SSpeDayWeekend'),_('SSpeDayHoliday'),_('AttTime'),_('SSpeDayNormalOT'),_('SSpeDayWeekendOT'),_('SSpeDayHolidayOT')]
		for i in range(len(f)):
			f[i]=u"%s"%f[i]
		return f
	else:
		return [f.verbose_name.capitalize() for f in tbl._meta.fields if not isinstance(f, AutoField)]
	return []
def GetdisableFieldsIndex(user,tbl):
	if tbl=="attShifts":
		rFieldNames=FetchModelFields('attShifts')
		dis=FetchDisabledFields(user,'attShifts')
		result=[]
		if dis:
			for t in dis:
				try:
					result.append(rFieldNames.index(t))
				except:
					return []
		return result
	
def GetAnnualleave(userid):   #自动计算年假天数 参数:入职日期
	if not userid: return ''
	t=employee.objByID(int(userid))
	if not t:
		return 0
#	for t in emp:
	Hiredday=t.Hiredday
	Annualleave=t.Annualleave
	if str(type(Hiredday))!="<type 'datetime.date'>" and str(type(Hiredday))!="<type 'datetime.datetime'>":
		return 0
	nowyear=datetime.datetime.now().year
	hireyear=checkTime(Hiredday).year
	if hireyear<1960:
		return 0
	diff=nowyear-hireyear
	re=0
	if diff>=1 and diff<10:
		re=5
	elif diff>=10 and diff<20:
		re=10
	elif diff>=20:
		re=15
	if Annualleave!=None:
		if Annualleave<re:
			re=Annualleave
	return re

def GetLeaveDays(userid,type):
	from mysite.iclock.datas import GetLeaveClasses
	LClass=GetLeaveClasses(1)
	LeaveID=0
	for t in LClass:
		if t['LeaveType']==int(type):
			LeaveID=t['LeaveID']
			break
	if LeaveID==0:
		return 0
	AttExcep=AttException.objects.filter(UserID=userid,ExceptionID=LeaveID)
	return len(AttExcep)

def allowAction(startdate,itype,enddate=None):
	st=checkTime(startdate)
	if enddate!=None:
		et=checkTime(enddate)
	lock_date=GetParamValue('opt_basic_lock_date','0')
	if lock_date=='0':return True
	nt=datetime.datetime.now()
	lock_st=datetime.datetime(nt.year,nt.month,int(lock_date),23,59,59)
	if lock_st>=nt:
		nt1=nt-datetime.timedelta(int(lock_date))
		prev_st=datetime.datetime(nt1.year,nt1.month,1,0,0,0)
		if st<prev_st:
			return False
	else:
		curr_st=datetime.datetime(nt.year,nt.month,1,0,0,0)
		if st<curr_st:
			return False
	#account=accounts.objects.filter(StartTime__gte=st-datetime.timedelta(days=180))
	#if not account:
	#	return True
	#type=int(type)
	#for t in account:
	#	if (st>=checkTime(t.StartTime) and st<=checkTime(t.EndTime)) or (enddate!=None and (et>=checkTime(t.StartTime) and et<=checkTime(t.EndTime))):
	#		if t.Status==1 and (t.Type==99 or t.Type==type):
	#			return False
	return True
#为综合排班列表构造表头			
def ConstructScheduleFields():
	r={}
	FieldNames=['userid','deptid','badgenumber','Workcode','username','starttime','endtime','schname']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=[_('userid'),_('department name'),_('PIN'),_('NewPin'),_('name'),_('StartTime'),_('EndTime'),_('time-table name')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]



def ConstructScheduleFields2(request):
	r={}
	FieldNames=['id','userid','badgenumber','Workcode','username','deptid','total']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=['',_('userid'),_('PIN'),_('NewPin'),_('name'),_('department name'),u'%s'%_(u'合计工时')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]

	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	now=datetime.datetime.now()
	if st=='':
		st=datetime.datetime(now.year,now.month,1,0,0)
	else:
		st=datetime.datetime.strptime(st,"%Y-%m-%d")
	if et=='':
		et=now
	else:
		et=datetime.datetime.strptime(et,"%Y-%m-%d")
	t=st
	if (et-st).days>60:
		et=st+datetime.timedelta(days=60)
	weeks=[u'周一',u'周二',u'周三',u'周四',u'周五',u'周六',u'周日']
	while t<=et:
		d=str(t.month)+'-'+str(t.day)
		FieldNames.append(d)
		d=str(t.month)+'-'+str(t.day)+u'%s'%weeks[t.weekday()]
		FieldCaption.append(d)
		t=t+datetime.timedelta(1)
		
	#FieldNames.append('total')
	#FieldCaption.append(u'%s'%_(u'合计工时'))
	return [r,FieldNames,FieldCaption]



#为报表中的出勤记录			
def ConstructRecordsFields(request):
	r={}
	FieldNames=['userid','deptid','badgenumber','username']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=[_('userid'),_('department name'),_('PIN'),_('name')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]

	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,"%Y-%m-%d")
	et=datetime.datetime.strptime(et,"%Y-%m-%d")
	t=st
	while t<=et:
		d=str(t.month)+'-'+str(t.day)
		FieldNames.append(d)
		FieldCaption.append(d)
		t=t+datetime.timedelta(1)
		
	
	return [r,FieldNames,FieldCaption]

#为假类汇总构造表头	
def ConstructLeaveFields():
	r={}
	FieldNames=['userid','deptid','badgenumber','Workcode','username','Leave']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=[_('userid'),_('department name'),_('PIN'),_('NewPin'),_('name'),_('Leave')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]


#为人事信息提醒构造字段
def createhrremindFields(item):
	r={}
	FieldNames=['pin','name','dept','sex']
	#FieldNames=['id','deptid','badgenumber','username']
	FieldCaption=[_('PIN'),_('name'),_('department name'),_("sex"),]
	if int(item)==1 or int(item)==2 or int(item)==3:
		FieldNames.append('Birthday')
		FieldCaption.append(_("Birthday"))
	elif int(item)==4 or int(item)==5 or int(item)==6:
		FieldNames.append('contractstart')
		FieldCaption.append(_(u"合同开始时间"))
		FieldNames.append('contractend')
		FieldCaption.append(_(u"合同结束时间"))
		
	elif int(item)==7 or int(item)==8 or int(item)==9:
		FieldNames.append('Trialstarttime')
		FieldCaption.append(_(u"试用期开始时间"))
		FieldNames.append('Trialendtime')
		FieldCaption.append(_(u"试用期结束时间"))
		
	elif int(item)==11:
		FieldNames.append('Hiredday')
		FieldCaption.append(_(u"该年新加入员工"))
	
	elif int(item)==12:
		FieldNames.append('Hiredday')
		FieldCaption.append(_(u"该年新加入员工"))
		FieldNames.append('countyear')
		FieldCaption.append(_(u"周年"))
	elif int(item)==13:
		FieldNames.append('StartSpecDay')
		FieldCaption.append(_("beginning time"))
		FieldNames.append('EndSpecDay')
		FieldCaption.append(_("ending time"))
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	
	return [FieldNames,FieldCaption]

#年休假报表构造字段
def createannualFields():
	r={}
	FieldNames=['pin','name','dept','sex','Hiredday','bennianyuefen','gongling','days']
	#FieldNames=['id','deptid','badgenumber','username']
	le=LeaveClass.objects.filter(LeaveType=5)
	unit=3
	if le.count()>0:
		unit=le[0].Unit
	if unit==1:
		FieldCaption=[_('PIN'),_('name'),_('department name'),_("sex"),_(u"入职时间"),_(u"年份"),_(u"工龄"),_(u"年假小时数")]
	else:
		FieldCaption=[_('PIN'),_('name'),_('department name'),_("sex"),_(u"入职时间"),_(u"年份"),_(u"工龄"),_(u"年假天数")]
	ann=annual_settings.objects.filter(Name="month_s")
	val=1
	if ann.count()>0:
		val=ann[0].Value
	i=int(val)
	for x in range(12):
		FieldNames.append(str(i))
		FieldCaption.append(u"%s月"%str(i))
		i=i+1
		if i>12:
			i=1
	FieldNames.append('weiyong')
	if unit==1:
		FieldCaption.append(_(u'未用年假小时数'))
	else:
		FieldCaption.append(_(u'未用年假天数'))
	#FieldNames.append('beizhu')
	#FieldCaption.append(_(u'备注'))
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [FieldNames,FieldCaption]


#从原datas移过来的
def trunc(DTime):
	return datetime.datetime(DTime.year,DTime.month,DTime.day,0,0,0)

def diffTime(diffT):
	return diffT.days*86400+diffT.seconds

def deleteCalcLog(**kwargs):
	now=datetime.datetime.now()
	try:
		d1=trunc(kwargs['StartDate'])
	except:
		d1=datetime.datetime(now.year,now.month,1,0,0)
	try:
		d2=trunc(kwargs['EndDate'])
	except:
		d2=datetime.datetime(now.year,now.month,now.day,23,59,59)
	
	try:
		iflag=kwargs['iflag']
	except:
		iflag=0
	
	if d1==trunc(now) and iflag==1:return  #开始时间是今天的考勤记录不用保存，其他如请假，排班等保存

	deptid=0
	userids=[]
	itype='calculated_date'
	if 'DeptID' in kwargs.keys():
		deptid=kwargs['DeptID']
	if 'UserID' in kwargs.keys():
		userids.append(int(kwargs['UserID']))
	# if deptid==-1:
	# 	calcDate.objects.all().delete()
	if deptid>0:
		userids=list(employee.objects.filter(DeptID=deptid).values_list('id',flat=True))
		#for t in objs:
			#userids.append(t.id)
	for u in userids:
		sDate=d1.strftime("%Y%m%d")
		try:
			item=calcDate.objects.get(UserID_id=u)
			if sDate not in item.ItemValue:
				item.ItemValue=item.ItemValue+','+sDate
				item.save()


		except Exception,e:
			#print "deleteCalcLog==",e
			calcDate(UserID_id=u,ItemValue=sDate).save(force_insert=True)
	
def FieldIsExist(fieldName,DataModel):
	field_names = [f.column for f in DataModel._meta.fields if not isinstance(f, AutoField)]
	if fieldName in field_names:
		return True
	return False

def hourAndMinute(value):
	if value:
		h=str(int(value)/60)
		m=str(int(value)%60)
		if int(m)<10:
			m='0'+str(m)
		return h+':'+m
	return ""

Absent={
	"0":_("No"),
	"1":_("Yes"),
	}
def IsYesNo(value):
	if value:
		return u"%s"%Absent['1']
	return u"%s"%Absent['0']

def IsTrueOrFalse(value):
	if value:
		return u"%s"%Absent['0']
	return u"%s"%Absent['1']
CmdContentNames={'DATA USER PIN=':_('Personnel information'),
	'DATA FP PIN=':_('Fingerprint'),
	'DATA DEL_USER PIN=':_('Del employee'),
	'DATA DEL_FP PIN=':_('Del fingerprint'),
	'CHECK':_('Check the server configuration'),
	'INFO':_('Updated device information on the server'),
	'CLEAR LOG':_('Remove transaction'),
	'RESTART':_('restart device'),
	'REBOOT':_('reboot device'),
#	'LOG':_('Check and upload the new data'),
	'PutFile':_('Send file to the device'),
	'GetFile':_('Get file from the equipment'),
	'Shell':_('Run a device shell command'),
	'SET OPTION':_('Change configuration'),
	'CLEAR DATA':_('Clear all data'),
	'AC_UNLOCK':_('Output unlock signal'),
	'AC_UNALARM':_('Terminate alarm signal'),
	'ENROLL_FP':_('Enroll employee\'s fingerprint'),
	'VERIFY':_(u'记录数据校对'),
	'DATA QUERY ATTLOG':_(u'重新传送设备上的考勤记录'),
	'CONTROL DEVICE 0300':_(u'重启设备'),
	'DATA UPDATE USERINFO':_(u'新增或更新人员'),
	'DATA UPDATE timezone':_(u'新增或更新时间段'),
	'DATA UPDATE FINGERTMP':_(u'新增或更新指纹')
}
def getContStr(cmdData):
	for key in CmdContentNames:
		if key in cmdData:
			return u"%s"%CmdContentNames[key]
	return "" #_("Unknown command")

def get_State_States(value):
	try:
		id= int(value)-10
		role=userRoles.objects.get(roleid=id)
		return u'%s%s'%(role.roleName,_('Accepted'))
	except:
		return value
def getother_process(value):
	if value=='':
		return ''
	elif value=='1':
		return _('User OverTime')
	elif value=='2':
		return _('Forget Checkin/out')
	elif value=='1,2':
		return '%s %s'%(_('User OverTime'),_('Forget Checkin/out'))
	else:
		return ''

#为监控记录表构造表头	
def getIacc_MonitorFields():
	r={}
	FieldNames=['userid','badgenumber','username','deptid','SN','Alias','OPTime','Message']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=[_('userid'),_('PIN'),_('name'),_('department name'),_(u'设备编号'),_(u'设备名称'),_(u'时间'),_(u'事件')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]
#为报警记录表构造表头	
def getIacc_AlarmFields():
	r={}
	FieldNames=['SN','Alias','OPTime','Message']
	for t in FieldNames:
		r[t]=''
	FieldCaption=[_(u'设备编号'),_(u'设备名称'),_(u'时间'),_(u'事件')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]

#为用户权限表构造表头	
def getIacc_UserRightsFields():
	r={}
	FieldNames=['userid','badgenumber','username','deptid','SN','Alias','IsUseGroup','ACGroupID','VerifyType','TimeZone1','TimeZone2','TimeZone3']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=[_('userid'),_('PIN'),_('name'),_('department name'),_(u'设备编号'),_(u'设备名称'),_("IsUseGroup"),_(u'门禁组'),_(u'验证方式'),_('TimeZone1'),_('TimeZone2'),_('TimeZone3')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]
#为记录明细构造表头	
def getIacc_RecordDetailsFields():
	r={}
	FieldNames=['userid','deptid','badgenumber','username','TTime','SN','VerifyType','Object']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=[_('userid'),_('department name'),_('PIN'),_('name'),_('time'),_(u'设备'),_(u'验证方式'),_(u'事件')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]
#为记录汇总构造表头	
def getIacc_SummaryRecordFields():
	r={}
	FieldNames=['userid','deptid','badgenumber','username','OutCount','SN']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=[_('userid'),_('department name'),_('PIN'),_('name'),_(u'出入次数'),_(u'设备')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]

#为用户权限明细构造表头	
def getIacc_EmpUserRightsFields():
	r={}
	FieldNames=['userid','badgenumber','username','deptid','SN','IsUseGroup','ACGroupID','VerifyType','TimeZone1','TimeZone2','TimeZone3']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=[_('userid'),_('PIN'),_('name'),_('department name'),_(u'设备'),_("IsUseGroup"),_(u'门禁组'),_(u'验证方式'),_('TimeZone1'),_('TimeZone2'),_('TimeZone3')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]
#为用户权限明细构造表头	
def getIacc_EmpDeviceFields():
	r={}
	FieldNames=['userid','badgenumber','username','deptid','SN']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=[_('userid'),_('PIN'),_('name'),_('department name'),_(u'设备')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]
	return [r,FieldNames,FieldCaption]
def getFlagValue(id):
	if int(id)==-1:
		return u"%s%s%s"%("<div style='color:red;width:55px;text-align:center;'>",_("Abnormal"),"</div>")
	return u"%s%s%s"%("<div style='color:#22BB00;width:55px;text-align:center;'>",_("Online"),"</div>")
