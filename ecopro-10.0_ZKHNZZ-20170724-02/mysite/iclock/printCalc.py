#! /usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.core.tools import *
#from django.utils.encoding import smart_str, force_unicode, smart_unicode
from django.utils.encoding import  force_unicode
#from django.utils.translation import ugettext as _
from django.db.models.fields import AutoField, FieldDoesNotExist
from mysite.iclock.datasproc import *
from mysite.iclock.iutils import *
from django.conf import settings
from django.db import  connection
from django.core.paginator import Paginator, InvalidPage
from mysite.iclock.datas import *
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.templatetags.iclock_tags import shortDate4, onlyTime
try:
	from django.db.models import Sum
except:
	pass
#import types

import datetime
import copy
qry_user_of_run=None
Schedules=None
SchDetail=None
qrytempsch=None
Holiday=None
schClass=None
ExcepData=None
CheckInOutData=None
l_CheckInOutData=0  #保存记录数
qryAudit=None
qryLeaveClass1=None
UserID=0
DeptID=0

isCalcing=0
schClasses=[]
LClasses1=[]
LClassesEx=[]

UserSchPlan={}
AttRule={}
LeaveClasses=[]
AttAbnomiteRptItems=[]
AbnomiteRptItems=[]

AttAbnomiteRptIndex={}
WorkTimeZone=[]
AutoWorkTime={}
AutoWorkTime1={}
CheckInOutRecorNo=0
(sbStart, sbEnd)=range(2)
(rmTrunc, rmRound, rmUpTo, rmCount)=range(4)
(auDay, auHour, auMinute, auWorkDay, auTimes)=range(5) #考勤计算单位
(suDay, suWeek, suMonth)=range(3) #班次时长单位
ExceptionIDs=[]
(tsrNoShift, tsrInOut, tsrIn, tsrOut)=range(4)
(caeFreeOT,caeOT,caeOut,caeBOut)=range(-4,0)   #自由加班  加班  外出  因公外出
ExceptionName=transExceptionName()
(ocIgnore, ocOut, ocBOut, ocConfirm)=range(4)
(csShift,csOverTime, csShiftOut, csOpenLock)=range(4)
RecAbnormiteOfState=(csOverTime,csOverTime,csShiftOut,csShiftOut)
(otcIgnore, otcOT, otcConfirm)=range(3)
CCheckName=('上班','加班','外出','开锁')
(raValid, raInvalid, raRepeat, raErrorState,raOut, raOT, raFreeOT, raAutoSch)=range(8)
FirstExceptionID=2
rmdattexception=[]
rmdattabnormite={}
rmlattabnormite=[]
rmdRecAbnormite={}
rmlRecAbnormite=[]
rmdattexceptionEx=[]

ClTA=[]
ChPA=[]
ExceptDataIn=False
WorkTimeIn=False
WorkTimeIndex=0
SpecialIntervals=[]
MinDate=datetime.datetime(2000,1,1,0,0)
MaxDate=datetime.datetime(2099,12,30,0,0)
CCheckInTag=[('O','I'),('o','i'),('0','1'),('u','l')]
AttAbnomiteRptIDs=(1000,1007,1008,1009,1004,1001,1002,1005,1013,1012,1003)
(aaValid, aaHoliday,aaNoIn, aaNoOut, aaAbsent, aaLate, aaEarly,aaOT,aaFOT, aaOut, aaBLeave)=AttAbnomiteRptIDs
AttRecord = {'CheckTime':datetime.datetime(2000,1,1,0,0),
	     'CheckType':'I',
	     'RecordConfirmed': False,
	     'TypeConfirmed':True }
for i in range(4):
	ClTA.append(AttRecord.copy())

AttCheckPoint = {'CCTime':None,
		 'CCStart':None,
		 'CCEnd':None,
		 'CCState': None,
		 'InState':None,
		 'OutState':None,
		 'CCMust':None,
		 'CCAuto':None,
		 'SNo':None,
		 'SSNo':None,
		 'ENo':None,
		 'Index':None
	 }

for i in range(3):
	ChPA.append(AttCheckPoint.copy())

def GetCalcUnitDic():
	#d={}
	#lc=LoadCalcItems()
	#for t in lc:
		#d[t['LeaveName']]=GetAttUnitText(int(t['Unit']))

	lc=GetLeaveClasses(0)
	result={}
	uList=[]
	for t in lc:
		result[t['LeaveName']]=GetAttUnitText(int(t['Unit']))
#		uList.append(GetAttUnitText(int(t['Unit'])))
		#d[t['LeaveName']]=GetAttUnitText(int(t['Unit']))
#	result['ulist']=uList
	return result


#考勤统计汇总/每日统计报表
def CalcReportItemPrint(request,deptids,userids,d1,d2,reportType=0):
	global AbnomiteRptItems
	global ExceptionIDs
	global AttRule
	global schClasses
	AttRule=LoadAttRule()
	if AbnomiteRptItems==[]:
		AbnomiteRptItems=GetLeaveClasses()
	AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
	if len(userids)>0 and userids!='null':
		ids=userids.split(',')
#		ids.sort()
	elif len(deptids)>0:
		deptIDS=deptids.split(',')
		deptids=[]
		for d in deptIDS:#支持选择多部门
			if int(d) not in deptids :
				deptids+=getAllAuthChildDept(d,request)
		ot=['DeptID','PIN']
		ids=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).values_list('id', flat=True).order_by(*ot)
		len(ids)
	Result={}
	re=[]

#分页		
#	try:
#		offset = int(request.GET.get('p', 1))
#	except:
#		offset=1
#	limit= int(request.POST.get('l', settings.PAGE_LIMIT))  #导出时使用
#	page_count =len(ids)/limit+1
#	if offset>page_count:offset=page_count
#	item_count =len(ids)
#	ids=ids[(offset-1)*limit:offset*limit]
	uids=[]
	k=0
	for u in ids:
		uids.append(u)
#	Result['item_count']=item_count
#	Result['page']=offset
#	Result['limit']=limit
#	Result['from']=(offset-1)*limit+1
#	Result['page_count']=page_count
	if reportType==0:  #考勤统计汇总
		r,Fields,Capt=ConstructFields()
	elif reportType==1:
		r,Fields,Capt=ConstructFields1(d1,d2)
	elif reportType==2:
		r,Fields,Capt=ConstructBaseFields2(d1,d2)
	Result['fieldnames']=Fields
	Result['fieldcaptions']=Capt
	Result['datas']=re
	if reportType==1:
		lc=LoadCalcItems()
		GetExceptionIDS()

	for uid in uids:
		uid=int(uid)
		attExcept=AttException.objects.filter(UserID=uid,AttDate__gte=d1,AttDate__lte=d2).order_by('UserID')
		len(attExcept)

		sql="""select s.userid as userid,u.badgenumber as pin,u.name as name,u.ssn as ssn,s.schid as schid,s.attdate as attdate,d.deptname as deptname,s.clockInTime as clockintime,s.clockouttime as clockouttime,
		s.starttime as starttime,s.endtime as endtime,s.workday as workday,s.realworkday as realworkday,s.noin as noin,s.noout as noout,
		s.early as early,s.late as late,s.absent as absent,s.absentr as absentr,s.overtime as overtime,s.exceptionid as exceptionid,s.mustin as mustin,s.mustout as mustout,  
		s.worktime as worktime,s.atttime as atttime,s.SSpeDayNormal as SSpeDayNormal,s.SSpeDayWeekend as SSpeDayWeekend,s.SSpeDayHoliday as SSpeDayHoliday ,s.symbol as symbol,
		s.SSpeDayNormalOT as SSpeDayNormalOT,s.SSpeDayWeekendOT as SSpeDayWeekendOT,s.SSpeDayHolidayOT as SSpeDayHolidayOT
		from attshifts s,userinfo u,departments d where u.userid=s.userid and d.deptID=u.defaultdeptid and  """
		if 'oracle' in settings.DATABASE_ENGINE:
			sql=sql+""" s.attdate>=to_date('%s','YYYY-MM-DD HH24:MI:SS') and s.attdate<=to_date('%s','YYYY-MM-DD HH24:MI:SS') and"""%(d1,d2)
		else:
			sql=sql+""" s.attdate>='%s' and s.attdate<='%s' and"""%(d1,d2)
		
		sql=sql+""" s.userid = %s order by u.badgenumber,s.schid,u.defaultdeptid"""%(uid)
#		print sql
#		elif len(deptids)>0:
#			sql=sql+""" u.defaultdeptid in (%s) order by u.badgenumber,u.defaultdeptid"""%(deptids)
		cs=customSql(sql)
		desc=cs.description
		fldNames={}
		i=0
		for c in desc:
			fldNames[c[0].lower()]=i
			i=i+1
		rmdAttday=r.copy()
		row=0
		rows=cs.fetchall()
#		print "rows==",rows
		if not rows:
			emp=employee.objByID(uid)
			for y in rmdAttday.keys():
				rmdAttday[y]=''
			rmdAttday['userid']=uid
			rmdAttday['deptid']=emp.Dept().DeptName
			rmdAttday['badgenumber']=emp.PIN
			rmdAttday['username']=emp.EName
			rmdAttday['ssn']=emp.SSN
		for t in rows:
			row+=1
			if rmdAttday['userid']==-1:
				rmdAttday['userid']=t[fldNames['userid']]
				rmdAttday['deptid']=t[fldNames['deptname']]
				rmdAttday['badgenumber']=t[fldNames['pin']]
				rmdAttday['username']=t[fldNames['name']]
				rmdAttday['ssn']=t[fldNames['ssn']]
			if reportType==0 or reportType==1:
				rmdAttday['duty']=SaveValue(rmdAttday['duty'],t[fldNames['workday']])
				rmdAttday['realduty']=SaveValue(rmdAttday['realduty'],t[fldNames['realworkday']])
				rmdAttday['late']=SaveValue(rmdAttday['late'],t[fldNames['late']])
				rmdAttday['early']=SaveValue(rmdAttday['early'],t[fldNames['early']])
				rmdAttday['SSpeDayHoliday']=SaveValue(rmdAttday['SSpeDayHoliday'],t[fldNames['sspedayholiday']])
				if t[fldNames['absent']]==1:
					rmdAttday['absent']=SaveValue(rmdAttday['absent'],t[fldNames['absentr']])
				rmdAttday['overtime']=SaveValue(rmdAttday['overtime'],t[fldNames['overtime']])

				rmdAttday['SSpeDayNormalOT']=SaveValue(rmdAttday['SSpeDayNormalOT'],t[fldNames['sspedaynormalot']])
				rmdAttday['SSpeDayWeekendOT']=SaveValue(rmdAttday['SSpeDayWeekendOT'],t[fldNames['sspedayweekendot']])
				rmdAttday['SSpeDayHolidayOT']=SaveValue(rmdAttday['SSpeDayHolidayOT'],t[fldNames['sspedayholidayot']])
				
			if reportType==0:
				if t[fldNames['mustin']]==True:
					rmdAttday['dutyinout']=SaveValue(rmdAttday['dutyinout'],1)
				if t[fldNames['mustout']]==True:
					rmdAttday['dutyinout']=SaveValue(rmdAttday['dutyinout'],1)
				if t[fldNames['mustin']]==True and t[fldNames['starttime']]!=None:
					rmdAttday['clockin']=SaveValue(rmdAttday['clockin'],1)
				if t[fldNames['mustout']]==True and t[fldNames['endtime']]!=None:
					rmdAttday['clockout']=SaveValue(rmdAttday['clockout'],1)
				#rmdAttday['noin']=SaveValue(t[fldNames['noin']],1)
				#rmdAttday['noout']=SaveValue(t[fldNames['noout']],1)
					
				if t[fldNames['mustin']]==True and t[fldNames['starttime']]==None:
					rmdAttday['noin']=SaveValue(rmdAttday['noin'],1)
				if t[fldNames['mustout']]==True and t[fldNames['endtime']]==None:
					rmdAttday['noout']=SaveValue(rmdAttday['noout'],1)
				rmdAttday['worktime']=SaveValue(rmdAttday['worktime'],t[fldNames['worktime']])
				rmdAttday['atttime']=SaveValue(rmdAttday['atttime'],t[fldNames['atttime']])
		
				rmdAttday['SSpeDayNormal']=SaveValue(rmdAttday['SSpeDayNormal'],t[fldNames['sspedaynormal']])
				rmdAttday['SSpeDayWeekend']=SaveValue(rmdAttday['SSpeDayWeekend'],t[fldNames['sspedayweekend']])
			
			if reportType==2:
				dt=t[fldNames['attdate']]
				dof=str(dt.day)
				tt=t[fldNames['schid']]
				if tt:
					try:
						sch=FindSchClassByID(int(tt))
						rmdAttday[dof]=sch['SchName']
					except:
						rmdAttday[dof]=''
						
			if reportType==1:
				dt=t[fldNames['attdate']]
				dof=str(dt.day)
				tt=t[fldNames['symbol']]
				if tt:
					rmdAttday[dof]=rmdAttday[dof]+tt

		if row>0 and (reportType==0 or reportType==1):
			excidlist=[]
			for ex in attExcept:
				if ex.UserID_id!=rmdAttday['userid']:
					continue
				exceptid=ex.ExceptionID
				if exceptid in [caeFreeOT,caeOT,caeOut,caeBOut]:
					pass
				elif exceptid>0:
					if exceptid in AttAbnomiteRptIndex:
						if (reportType==0) or (reportType==1):
							if AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindCount']==0:
								v=NormalAttValue(ex.InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['MinUnit'],
										 AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindProc'])
							else:
								v=ex.InScopeTime
								if not exceptid in excidlist:
									excidlist.append(exceptid)
							rmdAttday['Leave_'+str(exceptid)]=SaveValue(rmdAttday['Leave_'+str(exceptid)],v)
						if AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['IsLeave']==1 and AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindCount']==0:	#只有计为请假时才累计 2009.5.6
							v=NormalAttValue(ex.InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['MinUnit'],
									 AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['RemaindProc'])
							rmdAttday['Leave']=SaveValue(rmdAttday['Leave'],v)
			if excidlist:
				for exid in excidlist:
					ve=rmdAttday['Leave_'+str(exid)]
					rmdAttday['Leave_'+str(exid)]=NormalAttValue(ve,AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['MinUnit'],
										 AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['RemaindProc'])
					if AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['IsLeave']==1:	
						v=NormalAttValue(ve,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['MinUnit'],
								 AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['RemaindProc'])
						rmdAttday['Leave']=SaveValue(rmdAttday['Leave'],v)
		if rmdAttday['userid']>-1:
			if reportType==0:
				rmdAttday['worktime']=rmdAttday['worktime']#formatdTime(rmdAttday['worktime'])
				rmdAttday['atttime']=rmdAttday['atttime']#formatdTime(rmdAttday['atttime'])
			for ttt in rmdAttday.keys():              
				if type(rmdAttday[ttt])==type(1.0):
					if rmdAttday[ttt]>int(rmdAttday[ttt]):
						rmdAttday[ttt]=smart_str(rmdAttday[ttt])
		
			try:
				rmdAttday['Round']=round((float(rmdAttday['realduty'])*1000)/float(rmdAttday['duty']))/10
			except:
				rmdAttday['Round']=round(0)
			
			re.append(rmdAttday.copy())
	Result['datas']=re
	if reportType==0:
		Result['disableCols']=FetchDisabledFields(request.user,'attTotal')
	elif reportType==1:
		Result['disableCols']=FetchDisabledFields(request.user,'attDailyTotal')
	elif reportType==2:
		Result['disableCols']=[]
	return Result
days=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23',
'24', '25', '26', '27', '28', '29', '30','31']

def creatHeadUnit(headTule):#	重新生成单位的对应关系
	unit1=[]
	unit=GetCalcUnitDic()
	for h in headTule:
		if h in [_("EName"),_("PIN"),_("name"),]:
			continue
		elif h in [_("duty"),_("realduty"),]:
			unit1.append(unit[_("OK")])
		elif h in [_("AttTime"),_("WorkTime")]:
			unit1.append(_("Hour"))
		elif h in [_("late"),]:
			unit1.append(unit[_("Late")])
		elif h in [_("early"),]:
			unit1.append(unit[_("Early")])	
		elif h in [_("absent"),]:
			unit1.append(unit[_("Absent")])
		elif h in [_("overtime"),]:
			unit1.append(unit[_("OT")])
		elif h in [_("clockin"),_("clockout"),_("noin"),_("noout"),]:
			unit1.append(unit[_("NoIn")])
		elif h in [_("Leave"),]:
			unit1.append(unit[_("ALF")])
		elif h in [_("BusinessL"),_("Business leave")]:
			try:
				unit1.append(unit[_("Business leave")])
			except:
				unit1.append(unit[ _("ALF")])
		elif h in [_("SickL"),_("Sick leave")]:
			try:
				unit1.append(unit[_("Sick leave")])
			except:
				unit1.append(unit[_("ALF")])
		elif h in [_("PrivateL"),_("Private affair leave")]:
			try:
				unit1.append(unit[_("Private affair leave")])
			except:
				unit1.append(unit[_("ALF")])
		elif h in [_("HomeL"),_("Home leave")]:
			try:
				unit1.append(unit[_("Home leave")])
			except:
				unit1.append(unit[_("ALF")])
		elif h in [_("Round"),]:
			unit1.append('%')
		elif h in days:
			continue
		else:
			unit1.append(unit[h])
	return unit1

def GetCalcHead(tableName,fieldcaptions,fieldnames):#获取汇总表字段
#	headTule=(  _("EName"),_("PIN"), _("duty"),_("realduty"),_("late"), _("early"),_("absent"),_("overtime"),_("out"),_("dutyinout"),_("clockin"),_("clockout"),_("noin"),_("noout"),_("Leave"),_("SSpeDayNormal"),_("SSpeDayWeekend"),_("SSpeDayHoliday"),_("SSpeDayNormalOT"),_("SSpeDayWeekendOT"),_("SSpeDayHolidayOT"),_("Business leave"),_("Sick leave"),_("Private affair leave"),_("Home leave"),_("atttime"),_("worktime"),_("Round"))
# 显示的表头
#	headTule=[_("EName"),_("PIN"), _("duty"),_("realduty"),_("late"), _("early"),_("absent"),_("overtime"),_("OUT"),_("noin"),_("noout"),_("Leave"),_("BusinessL"),_("SickL"),_("PrivateL"),_("HomeL"),_("AttTime"),_("WorkTime"),_("Round")]
#	显示的字段
	showable=['username','badgenumber','duty','realduty','late','early','absent','overtime','out','noin','noout','Leave','Leave_1','Leave_2','Leave_3','Leave_4','atttime','worktime','Round']
	showField=[]
	headTule=[]
	i=0
	l=[]
#	print 222,fieldcaptions,fieldnames
	for s in fieldnames:
		if s in showable:
			showField.append(s)
			l.append(i)
		i+=1
	j=0
	for fc in fieldcaptions:
		if j in l:
			if fc=='':
				pass
			headTule.append(fc)
		j+=1
	
	unit1=[]
	headTule.append(_("Round"))
	showField.append('Round')
#	获得单位
	unit1=creatHeadUnit(headTule)
	
	return headTule,unit1,showField



#week={1:_("Round"),2:u'二',3:'三',4:'四',5:'五',6:'六',7:'七'}
weeks={7:_("Su"),1: _("M"),2: _("T"),3: _("W"),4: _("Th"),5: _("F"),6: _("Sa")}

def GetDailyCalcHead(tableName,d1,d2):#获取每日考勤表字段
	unit1=['','',]
	unit3=[]
#	获得单位
#	unit2=GetCalcUnitDic()
	unit=GetCalcSymbol()
#	print 888999,unit
	r,showField,headTule=ConstructBaseFieldsDaily(d1,d2)
	unit2=creatHeadUnit(headTule)
	i=0
	for d in showField:
		if d in ['userid', 'deptid', 'badgenumber', 'username']:
			continue
#		elif d == :
#			
		if d in days:
			if d==d1.day:
				unit1.append(weeks[d1.isoweekday()])
			else:
				dd=d1+datetime.timedelta(days=i)
				unit1.append(weeks[dd.isoweekday()])
			i+=1
	unit1.extend(unit2)
	return headTule,unit1,unit,showField

def ConstructBaseFieldsDaily(d1,d2):
	r={}
	strFieldNames=['deptid','badgenumber','username']
	#	显示的字段
	FieldNames=['badgenumber','username']
	# 显示的表头
	FieldCaption=[_('PIN'),_('name'),]
#	r1=['duty','realduty','late','early','absent','SSpeDayHoliday','SSpeDayNormalOT','SSpeDayWeekendOT','SSpeDayHolidayOT','overtime','Leave']
	r1=['duty','realduty','late','early','absent','overtime','Leave']
	for t in FieldNames:
		if t in strFieldNames:
			r[t]=''
	for t in r1:
		r[t]=''
	t=d1
	while t<=d2:
		f=str(t.day)
		r[f]=''
		FieldNames.append(f)
		FieldCaption.append(f)
		t=t+datetime.timedelta(1)
	FieldNames=FieldNames+r1
#	FieldCaption=FieldCaption+[_('duty'),_('realduty'),_('late'),_('early'),_('absent'),_('HolidayDay'),_('NormalDayOT'),_('WeekendDayOT'),_('HolidayDayOT'),_('overtime'),_('Leave')]
	FieldCaption=FieldCaption+[_('duty'),_('realduty'),_('late'),_('early'),_('absent'),_('overtime'),_('Leave')]
	r['userid']=-1
	return [r,FieldNames,FieldCaption]

def GetShiftsFiled(fieldcaptions,fieldnames):#获得班次详情表字段
#	print 1111,fieldcaptions,fieldnames
	head=[]
	showField=[]
	disable=['userid','DeptID','WorkTime', 'AttTime','Leave_5', 'Leave_6', 'Leave_7', 'Leave_8', 'Leave_9', 'Leave_10', 'Leave_11','Leave_12']
	showable=['PIN', 'EName', 'AttDate', 'SchId', 'ClockInTime', 'ClockOutTime', 'StartTime', 'EndTime', 'WorkDay', 'RealWorkDay', 'Late', 'Early', 'Absent', 'OverTime', 'MustIn', 'MustOut', 'SSpeDayNormal', 'SSpeDayWeekend', 'SSpeDayHoliday', 'SSpeDayNormalOT', 'SSpeDayWeekendOT', 'SSpeDayHolidayOT', 'Leave_1', 'Leave_2', 'Leave_3', 'Leave_4', ]

	l=[]
	i=0
	for ff in fieldnames:
		if ff in showable:
			l.append(i)
			showField.append(ff)
		i+=1
	j=0
	for fc in fieldcaptions:
		if j in l:
			head.append(fc)
		j+=1
#	print 66222,head,showField
	return head,showField


def GetattTotalLeaveFiled(fieldcaptions,fieldnames):#获得假类汇总表字段
#	print 1111,fieldcaptions,fieldnames
	head=[]
	showField=[]
	disable=['userid','deptid','WorkTime', 'AttTime','Leave_5', 'Leave_6', 'Leave_7', 'Leave_8', 'Leave_9', 'Leave_10', 'Leave_11','Leave_12']
	showable=['badgenumber', 'username', 'Leave', 'Leave_1', 'Leave_2', 'Leave_3', 'Leave_4', 'Leave_5', 'Leave_6', 'Leave_7', 'Leave_8', 'Leave_9', 'Leave_10',  ]
#	showable=fieldnames
#	print fieldnames,type(fieldnames)
	l=[]
	i=0
	for ff in fieldnames[:20]:
		if ff in ['userid','deptid']:
			pass
#		if ff in showable:
		else:
			l.append(i)
			showField.append(ff)
			i+=1
			continue
		i+=1
	j=0
	for fc in fieldcaptions:
		if j in l:
			j+=1
			head.append(fc)
			continue
		j+=1
#	print 66222,head,showField
	return head,showField

