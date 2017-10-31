#!/usr/bin/python
# -*- coding: utf-8 -*-
from mysite.iclock.models import *
from mysite.core.tools import *
from django.utils.encoding import smart_str, force_unicode, smart_unicode
from django.utils.encoding import  force_unicode
from django.db.models.fields import AutoField, FieldDoesNotExist
from django.utils.translation import ugettext_lazy as _
import datetime
from mysite.iclock.iutils import *
import copy
from mysite.iclock.datas import *
from django.contrib.auth.decorators import permission_required, login_required
from mysite.utils import *
from mysite.iclock.datasproc import *
#global SchedulerShifts
#global FTTimeZones
LastZone = 1
LastZone1 = 2*60                
(TZNormal,TZInner)=range(2)     #TZInner is Inner TimeZone
BaseDate=datetime.datetime(2000,1,1,0,0,0)

@login_required
def addShiftTimeTable(request):
	try:
#		global SchedulerShifts
#		global FTTimeZones
		unit=int(request.POST.get('unit','1'))
		cycle=int(request.POST.get('cycle','1'))
		isOT=request.POST.get('is_OT','off')
		overtime=0
		if isOT=='on':
			overtime=request.POST.get('OverTime','0')
			if overtime!='':
				overtime=int(overtime)
		SchID=int(request.POST.get('shift_id','0'))
#		weekStartDay=int(request.POST.get('weekStartDay','0'))
		attrule=LoadAttRule()
		weekStartDay=attrule['WorkWeekStartDay']
		
		
		if unit==0:
			rc=1
		elif unit==1:
			rc=7
		else:
			rc=31
		rc=rc*cycle
		SchedulerShifts=[]
		FTTimeZones=[]
		chklbSchClass=request.POST['sTimeTbl'].split(',')
		chklbDates=request.POST['sDates'].split(',')
		#schClasses=GetSchClasses()
		SchedulerShifts=getSchedulerShifts(FTTimeZones,SchID,unit,weekStartDay,overtime)
		deleteShiftDetail(SchID) 
		for t in chklbSchClass:
			t=int(t)
			schClass=FindSchClassByID(t)
			st=schClass['TimeZone']['StartTime']
			et=schClass['TimeZone']['EndTime']
			for tt in chklbDates:
				tt=int(tt)
				starttime = st+datetime.timedelta(days=tt)
				endtime = et+datetime.timedelta(days=tt)
				if TestTimeZone(FTTimeZones,starttime,endtime):
					AddScheduleShift(SchedulerShifts, starttime, endtime,t,overtime)
		for i in range(len(SchedulerShifts)):
			if (i==0) or ((i>0) and (SchedulerShifts[i]['TimeZone']['StartTime']>SchedulerShifts[i-1]['TimeZone']['EndTime'])):
				st=SchedulerShifts[i]['TimeZone']['StartTime']
				et=SchedulerShifts[i]['TimeZone']['EndTime']
				d={}
				d['Num_RunID']=SchID
				d['StartTime']=st.time()
				d['EndTime']=et.time()
				if unit==suWeek:
					st=st+datetime.timedelta(days=weekStartDay)
					et=et+datetime.timedelta(days=weekStartDay)
				d['sdays']=(st-datetime.datetime(1900,12,30,0,0)).days
				d['edays']=(et-datetime.datetime(1900,12,30,0,0)).days
				d['schClassID']=SchedulerShifts[i]['schClassID']
				d['overtime']=SchedulerShifts[i]['OverTime']
				sql=getSQL_insert_ex(NUM_RUN_DEIL._meta.db_table,d)
				customSql(sql)
		return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})
	except Exception,e:
		#import  traceback;traceback.print_exc()
		#print "===================",e
		return getJSResponse({"ret":1,"message":u"%s" % _('Operation Failed')})
		#errorLog()
@login_required
def deleteAllShiftTime(request):
	SchIDs=request.GET.get('shift_id','-1').split(',')
	for SchID in SchIDs:
		deleteShiftDetail(SchID)    
	return getJSResponse({"ret":0,"message":""})
#@login_required
#def deleteEmployeeShift(request):
#	pass

def deleteShiftDetail(SchID):
	sql='delete from %s where Num_runID=%s'%(NUM_RUN_DEIL._meta.db_table,SchID)
	customSql(sql)

@login_required
def deleteShiftTime(request):
	#start=float(request.POST.get('start'))
	#end=float(request.POST.get('end'))
	#shift_id=int(request.POST.get('shift_id'))
	#unit=int(request.POST.get('unit'))
	#weekStart=int(request.POST.get('weekStartDay'))
	numid=int(request.POST.get('num_id',0))
	if numid==0:
		return getJSResponse({"ret":1,"message":""})
#	sday=int(start)
#	send=int(end)
	#h=int((start-sday)*24)
	#m=int(((start-sday)*24-h)*60)
	#st=datetime.time(h,m,0)

	#h=int((end-send)*24)
	#m=int(((end-send)*24-h)*60)
	#if m==59:
		#h=h+1
		#m=0
	#else:
		#m=m+1
	
	#et=datetime.time(h,m,0)
	#sd=sday
	#ed=send
	#if unit==1:
		#sd=sday+weekStart
		#ed=send+weekStart
		#if ed<0:
			#sd=sd+7
			#ed=ed+7

	sql="delete from %s where id=%s"%(NUM_RUN_DEIL._meta.db_table,numid)
#	print "-------------",sql
#	sql="delete from %s where sdays=%s and edays=%s and starttime>='%s' and endtime<='%s' and num_runid=%s"%(NUM_RUN_DEIL._meta.db_table,sd,ed,st,et,shift_id)
	customSql(sql)
	return getJSResponse({"ret":0,"message":""})

def getSchedulerShifts(FTTimeZones,schid,unit,WorkWeekStartDay=0,overtime=0):
#	global SchedulerShifts
#	global FTTimeZones
	SchedulerShifts=[]
	FTTimeZones=[]
	SchDetail=NUM_RUN_DEIL.objects.filter(Num_runID=schid).order_by('Num_runID', 'Sdays', 'StartTime')
	for sDetail in SchDetail:
		ot=sDetail.OverTime
		st=checkTime(datetime.time(sDetail.StartTime.hour,sDetail.StartTime.minute,sDetail.StartTime.second))
		et=checkTime(datetime.time(sDetail.EndTime.hour,sDetail.EndTime.minute,sDetail.EndTime.second))
		StartDay=sDetail.Sdays
		EndDay=sDetail.Edays
		if unit==suWeek:
			StartDay=StartDay-WorkWeekStartDay
			EndDay=EndDay-WorkWeekStartDay
			if EndDay<0:
				StartDay=StartDay+7
				EndDay=EndDay+7

		if (AddTimeZone(FTTimeZones,st+datetime.timedelta(days=StartDay), et+datetime.timedelta(days=EndDay))>=0):
			AddScheduleShift(SchedulerShifts, st+datetime.timedelta(days=StartDay)  , et+datetime.timedelta(days=EndDay),sDetail.SchclassID_id,ot)
	return SchedulerShifts

def MergeTimeZone(TimeZones,sTime,eTime,TZProperty=TZNormal):
	Result=-1
	t=eTime-sTime
	if (t.days*24*60*60+t.seconds)<LastZone:
		return Result
	tzl=len(TimeZones)
	tz={'StartTime':sTime,'EndTime':eTime,'TZProperty':TZProperty}
	if TZProperty==TZNormal:
		i=tzl-1
		while i>=0:
			if sTime>TimeZones[i]['StartTime']-datetime.timedelta(seconds=LastZone):
				break
			i=i-1
		if (i>=0) and (eTime<TimeZones[i]['EndTime']):
			return Result
		if (tzl==0) or ((i<0) and (eTime<TimeZones[0]['StartTime'])) or ((i>=0) and (sTime>TimeZones[i]['EndTime']) and
										 ((i==tzl-1) or (eTime<TimeZones[i+1]['StartTime']))):
			Result=i+1
			TimeZones.insert(i+1,tz)
	return Result


def TestTimeZone(TimeZones,sTime,eTime):
	i=len(TimeZones)
	MergeTimeZone(TimeZones,sTime,eTime)
	if i<len(TimeZones):
		return True
	else:
		return False

def AddTimeZone(FTTimeZones,STime, ETime,TZProperty=TZNormal):
	#global FTTimeZones
	Result=MergeTimeZone(FTTimeZones, STime, ETime,TZProperty)
	return Result

@login_required
def FetchSchPlan(request):
	try:
		saveScheduleLogToFile('schedule',dumps(request.POST),request.user)
		schPlan={}
		schPlan['MayUsedAutoIds']=[]
		schPlan['SchArray']=[]
		schPlan['MinAutoPlanInterval']=24
		schPlan['AutoSchPlan']=1
		AutoSchPlan=False
		deptIDs=request.POST.get('deptIDs',"")
		UserIDs=request.POST.get('UserIDs',"")
		isContainedChild=request.POST.get('isContainChild',"")
		if UserIDs=='':
			deptidlist=[int(i) for i in deptIDs.split(',')]
			deptids=deptidlist
			if isContainedChild=="1":   #是否包含下级部门
				deptids=[]
				for d in deptidlist:#支持选择多部门
					if int(d) not in deptids :
						deptids+=getAllAuthChildDept(d,request)
			UserIDs=employee.objects.filter(DeptID__in=deptids,OffDuty=0)  
		else:
			emplist=UserIDs.split(',')
			UserIDs=employee.objects.filter(id__in=emplist,OffDuty=0)  
#		if UserIDs =="":
#			deptIDs=deptIDs.split(',')
#			UserIDs = employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
#			#UserIDs=",".join(["%s" % int(i) for i in userlist])
#		else:
#			UserIDs=UserIDs.split(',')
		AutoSchPlan=(request.POST.get('auto_assign','')=='on')
		if AutoSchPlan:
			try:
				leastdays=int(request.POST.get('least_days','1'))
			except:
				leastdays=0
			try:
				leasthours=int(request.POST.get('least_hours','0'))
			except:
				leasthours=0
			schPlan['MinAutoPlanInterval']=leastdays*24+leasthours
				
		if AutoSchPlan==False:
			schPlan['AutoSchPlan']=0
		s=request.POST['sAssigned_shifts']
		schList=loads(s)
		schclasses=request.POST.get('sTimeTbl','')
		if len(schclasses)>0:
			schclasses=schclasses.split(',')
		for t in schclasses:
			schPlan['MayUsedAutoIds'].append(int(t))
		for t in schList:
			try:
				st=datetime.datetime.strptime(t['StartDate'],"%Y-%m-%d")
				et=datetime.datetime.strptime(t['EndDate'],"%Y-%m-%d")
			except:
				st=datetime.datetime.strptime(t['StartDate'],'%Y-%m-%d %H:%M:%S')
				et=datetime.datetime.strptime(t['EndDate'],'%Y-%m-%d %H:%M:%S')
			if not allowAction(st,5,et):
				return getJSResponse({"ret":2,"message":u"%s"%_('Save Fail,account has been locked!')})
			schPlan['SchArray'].append({'NUM_OF_RUN_ID':t['SchId'],'StartDate':t['StartDate'],'EndDate':t['EndDate']})
		for i in UserIDs:
			saveEmpScheduleLogToFile('emp_schedule','%s\t%s\t%s'%(dumps(schPlan['SchArray']),request.user,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),i.pin())
			u=i.id
			SaveSchPlan(int(u),schPlan)
		adminLog(time=datetime.datetime.now(),User=request.user, model=USER_OF_RUN._meta.verbose_name, action=u'%s'%_(u'周期排班'),object=request.META["REMOTE_ADDR"]).save(force_insert=True)#
		return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})
	except Exception,e:
		print 'FetchSchPlan',e
		return getJSResponse({"ret":-1,"message":u"%s"%_('save failed')})

def SaveSchPlan(userid,dSchPlan):
	sql=getSQL_update("userinfo",whereUserid=userid,AutoSchPlan=dSchPlan['AutoSchPlan'],MinAutoSchInterval=dSchPlan['MinAutoPlanInterval'])
	customSql(sql)
	cache.delete("%s_iclock_emp_%s"%(settings.UNIT,userid))
	sql="delete from %s where userid=%s"%(UserUsedSClasses._meta.db_table,userid)
	customSql(sql)
	for t in dSchPlan['MayUsedAutoIds']:
		sql=getSQL_insert(UserUsedSClasses._meta.db_table,UserID=userid,SchID=t)
		customSql(sql)



#	sql="delete from %s where userid=%s"%(USER_OF_RUN._meta.db_table,userid)
#	customSql(sql)
	
	for t in dSchPlan['SchArray']:
		try:
			st=datetime.datetime.strptime(t['StartDate'],"%Y-%m-%d")
			et=datetime.datetime.strptime(t['EndDate'],"%Y-%m-%d")
		except:
			st=datetime.datetime.strptime(t['StartDate'],'%Y-%m-%d %H:%M:%S')
			et=datetime.datetime.strptime(t['EndDate'],'%Y-%m-%d %H:%M:%S')
		deleteUserShifts(uid=userid,startdate=st,enddate=et)
	
	
	i = 0
	for t in dSchPlan['SchArray']:
		t['userid']=userid
		t['ORDER_RUN']=i
		sql=getSQL_insert_ex(USER_OF_RUN._meta.db_table,t)
		customSql(sql)
		i=i+1
	deleteCalcLog(UserID=userid,StartDate=st,EndDate=et)
	
def deleteUserShifts(**kwargs):
	uid=kwargs['uid']
	st=kwargs['startdate']
	et=kwargs['enddate']+datetime.timedelta(days=1)
	#删除临时排班
	deleteTempData([uid],st,et)
	#USER_TEMP_SCH.objects.filter(UserID=uid,ComeTime__gte=st,ComeTime__lt=et).delete()
#	tmp=USER_TEMP_SCH.objects.filter(UserID=uid)
#	tmp=tmp.filter(Q(ComeTime__lte=st,LeaveTime__gte=st)|Q(ComeTime__lte=et,LeaveTime__gte=et)).delete()
	
	#删除周期排班
	USER_OF_RUN.objects.filter(UserID=uid,StartDate__gte=st,EndDate__lte=et).delete()
	irun=USER_OF_RUN.objects.filter(UserID=uid)
	et=et-datetime.timedelta(days=1)
	iruns=irun.filter(Q(StartDate__lte=st,EndDate__gte=st)|Q(StartDate__lte=et,EndDate__gte=et))
	#print iruns
	#print st,et
	for tt in iruns:
		tt.StartDate=checkTime(tt.StartDate)
		tt.EndDate=checkTime(tt.EndDate)
		d={'NUM_OF_RUN_ID':tt.NUM_OF_RUN_ID_id,'StartDate':tt.StartDate,'EndDate':tt.EndDate,'userid':uid}
		if tt.datest:
			d['datest']=tt.datest
		
		sql='delete from %s where id=%s'%(USER_OF_RUN._meta.db_table,tt.id)
		customSql(sql)
		if tt.StartDate<=st:
			if tt.EndDate<=et:
				d['EndDate']=st-datetime.timedelta(days=1)
				sql=getSQL_insert_ex(USER_OF_RUN._meta.db_table,d)
				customSql(sql)
			else:
				if tt.StartDate!=st:
					d['EndDate']=st-datetime.timedelta(days=1)
					sql=getSQL_insert_ex(USER_OF_RUN._meta.db_table,d)
					customSql(sql)
				d['StartDate']=et+datetime.timedelta(days=1)
				d['datest']=tt.StartDate
				if tt.datest:
					d['datest']=tt.datest
				d['EndDate']=tt.EndDate
				sql=getSQL_insert_ex(USER_OF_RUN._meta.db_table,d)
				customSql(sql)
		else:
			d['datest']=tt.StartDate
			if tt.datest:
				d['datest']=tt.datest
			d['StartDate']=et+datetime.timedelta(days=1)
			sql=getSQL_insert_ex(USER_OF_RUN._meta.db_table,d)
			customSql(sql)
		
	
	
	
	
	
@login_required
def addTemparyShifts(request):
#	global SchedulerShifts
#	global FTTimeZones
	saveScheduleLogToFile('temp_shifts',dumps(request.POST),request.user)


	st=request.POST.get('StartDate','')
	et=request.POST.get('EndDate','')
	yst=request.POST.get('sDates_st','')
	yet=request.POST.get('sDates_et','')
#	print request.POST
	chklbSchClass=request.POST["sTimeTbl"].split(',')
	chklbDates=request.POST["sDates"].split(',')
	OverTime=request.POST.get('OverTime','')
	#deldata=int(request.POST.get('deldata','0'))
	eventname=request.POST.get('eventName','')
	
	deptIDs=request.POST.get('deptIDs',"")
	UserIDs=request.POST.get('UserIDs',"")
	isContainedChild=request.POST.get('isContainChild',"")
	is_OT=request.POST.get('is_OT','')
	is_OT=(is_OT=='on')
	userPins = []
	if '' in chklbSchClass:
		chklbSchClass.remove('')
	if '' in chklbDates:
		chklbDates.remove('')
	if is_OT:
		if OverTime=='':
			OverTime=0
		else:
			OverTime=int(OverTime)
	if eventname=='eventResize' or eventname=='eventdrop':
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d')
		j=st
		chklbDates=[]
		while j<et:
			s=j.strftime("%Y-%m-%d")
			j=j+datetime.timedelta(days=1)
			chklbDates.append(s)
	if eventname=='drop':
		st=datetime.datetime.strptime(chklbDates[0],'%Y-%m-%d')
		et=st+datetime.timedelta(seconds=60*60*23)
		#chklbDates.append(st)
		#if deldata<0:
		#	et=et-datetime.timedelta(days=deldata)
	#schClasses=GetSchClasses()
	if UserIDs=='':
		deptidlist=[int(i) for i in deptIDs.split(',')]
		deptids=deptidlist
		if isContainedChild=="1":   #是否包含下级部门
			deptids=[]
			for d in deptidlist:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		UserIDs=employee.objects.filter(DeptID__in=deptids)  
	else:
		emplist=UserIDs.split(',')
		UserIDs=employee.objects.filter(id__in=emplist)
	for u in UserIDs:
		SchedulerShifts=[]
		FTTimeZones=[]
		UserSchPlan={}
		userPins.append(u.PIN)
		i=u.id
		saveEmpScheduleLogToFile('emp_schedule','%s %s %s temp'%(dumps(request.POST),request.user,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),u.pin())
		if chklbDates<>[] and chklbSchClass<>[]:
			UserSchPlan=LoadSchPlan(u,True,False)
			if eventname=='eventResize' and UserSchPlan:
				SchedulerShifts=[]
				SchedulerShifts=GetUserScheduler(u, st, et,UserSchPlan['HasHoliday'])
				for t in SchedulerShifts:
					if (t['SchID']==int(chklbSchClass[0])) and (t['TimeZone']['StartTime'].date()>=st.date()):
						if (t['TimeZone']['StartTime'].date()==st.date() and t['TimeZone']['EndTime'].date()==et.date()) or ((t['TimeZone']['StartTime'].date()<t['TimeZone']['EndTime'].date()) and t['TimeZone']['StartTime'].date()<=et.date()):
							SchedulerShifts.remove(t)
							break
				SaveTempSch(u.id,st,et,SchedulerShifts)
			
			
			
			
			if eventname=='drop' and UserSchPlan:
				SchedulerShifts=GetUserScheduler(u, st, et,UserSchPlan['HasHoliday'])
		#for t in SchedulerShifts:
		#	AddTimeZone(FTTimeZones,t['TimeZone']['StartTime'],t['TimeZone']['EndTime'])
		if eventname=='eventResize' or eventname=='eventdrop':
			yst=datetime.datetime.strptime(yst,'%Y-%m-%d')
			yet=datetime.datetime.strptime(yet,'%Y-%m-%d')
			deleteTempData([i],yst,yet)
		for t in chklbSchClass:
			t=int(t)
			schClass=FindSchClassByID(t)
			stime=schClass['TimeZone']['StartTime']
			etime=schClass['TimeZone']['EndTime']
			NextDay=schClass['NextDay']
			for tt in chklbDates:
				tt=datetime.datetime.strptime(tt,'%Y-%m-%d')
				starttime = datetime.datetime(tt.year,tt.month,tt.day,stime.hour,stime.minute)
				endtime = datetime.datetime(tt.year,tt.month,tt.day,etime.hour,etime.minute)+datetime.timedelta(days=NextDay)
#				if endtime<starttime:
#					endtime=endtime+datetime.timedelta(days=1)
				if TestTimeZone(FTTimeZones,starttime,endtime):
					AddScheduleShift(SchedulerShifts, starttime, endtime,t,OverTime)
				else:
					return getJSResponse({"ret":1,"message":u"%s"%_(u'该时段可能与已排时段重合')})
				et=et-datetime.timedelta(seconds=1)
				SaveTempSch(i,st,et,SchedulerShifts)
		#用于日历排班时从某一天移到某一天将原来的被移动的时段删除
		#if eventname=='eventdrop'  and UserSchPlan:
		#	SchedulerShifts=[]
		#	#tt=datetime.datetime.strptime(chklbDates[0],'%Y-%m-%d')-datetime.timedelta(days=deldata)
		#	st=tt
		#	et=tt
		#	SchedulerShifts=GetUserScheduler(u, st, et,UserSchPlan['HasHoliday'])
		#	for t in SchedulerShifts:
		#		if (t['SchID']==int(chklbSchClass[0])) and (t['TimeZone']['StartTime'].date()>=st.date()):
		#			if (t['TimeZone']['StartTime'].date()==st.date() and t['TimeZone']['EndTime'].date()==et.date()) or ((t['TimeZone']['StartTime'].date()<t['TimeZone']['EndTime'].date()) and t['TimeZone']['StartTime'].date()<=et.date()):
		#				SchedulerShifts.remove(t)
		#				break
		#	SaveTempSch(i,st,et,SchedulerShifts)
	userCount = len(userPins)
	if userPins:
		userPins = ','.join(userPins)
	else:
		userPins = ''
	adminLog(time=datetime.datetime.now(),User=request.user, model=USER_TEMP_SCH._meta.verbose_name, action=u'%s'%_(u"Create"),object=u'工号%s'%userPins[:100],count = userCount).save(force_insert=True)#
	return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})

def SaveTempSch(userid,st,et,SchedulerShifts):
	if st<>'':
		#sql="delete from %s where userid=%s and leavetime>='%s' and cometime<'%s' and cometime>='%s'"%(USER_TEMP_SCH._meta.db_table,userid,st,et+datetime.timedelta(days=1),st)
		#customSql(sql)
		deleteTempData([userid],st,et)
	
	
	st1=None
	et1=None
	
	for t in SchedulerShifts:
		if st1 is None:
			st1=t['TimeZone']['StartTime']
			et1=t['TimeZone']['EndTime']
		else:
			if st1>t['TimeZone']['StartTime']:
				st1=t['TimeZone']['StartTime']
			if et1<t['TimeZone']['EndTime']:
				et1=t['TimeZone']['EndTime']
		
		
		if (st<>'') and ((t['TimeZone']['EndTime']<st) or (t['TimeZone']['StartTime']>=(et+datetime.timedelta(days=1)))):
			continue
		else:
			tmp=USER_TEMP_SCH.objects.filter(UserID=userid)
			tmp.filter(Q(ComeTime__lte=t['TimeZone']['StartTime'],LeaveTime__gte=t['TimeZone']['StartTime'])|Q(ComeTime__lte=t['TimeZone']['EndTime'],LeaveTime__gte=t['TimeZone']['EndTime'])|Q(ComeTime__lte=t['TimeZone']['EndTime'],ComeTime__gte=t['TimeZone']['StartTime'])).delete()
			
			
			sql=getSQL_insert(USER_TEMP_SCH._meta.db_table,userid=userid,comeTime=t['TimeZone']['StartTime'].strftime("%Y-%m-%d %H:%M:%S"),leavetime=t['TimeZone']['EndTime'].strftime("%Y-%m-%d %H:%M:%S"),
				      schclassid=t['schClassID'],overtime=t['OverTime'])
			customSql(sql)
	if st:
		j=st
		
		while j<=et:
			m=0
			for t in SchedulerShifts:
				m=0
				if (j<=t['TimeZone']['StartTime']) and (j+datetime.timedelta(days=1)>t['TimeZone']['StartTime']):
					m=1
					break	
			if m==0:
				sql=getSQL_insert(USER_TEMP_SCH._meta.db_table,userid=userid,comeTime=(j+datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),leavetime=(j+datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),overtime=0)
				customSql(sql)
			j=j+datetime.timedelta(days=1)
	if st and et:
		pass
	else:
		if st1 and et1:
			st=st1
			et=et1
			
	deleteCalcLog(UserID=userid,StartDate=st,EndDate=et)

def deleteTempData(uids,d1,d2):
	d1=trunc(d1)
	d2=trunc(d2)
	tmp_t = d2 + datetime.timedelta(days=1)-datetime.timedelta(seconds=1)
	#attrule=LoadAttRule()
	USER_TEMP_SCH.objects.filter(UserID__in=uids,ComeTime__range=(d1, tmp_t)).delete()
	
	
@login_required
def doDeleteTmpShifts(request):     #清除指定日期、人员的临时排班 result=0成功;result=1失败

	saveScheduleLogToFile('clear_shifts',dumps(request.POST),request.user)

	if request.method=="POST":
#		print request.POST
		UserIDs=request.POST.get("UserIDs"," ")
		d1=request.POST.get("StartDate"," ")
		d2=request.POST.get("EndDate"," ")
		deptIDs=request.POST.get('deptIDs',"")
		isContainedChild=request.POST.get('isContainChild',"")
		delshift=request.POST.get("delshift","")
		d1=datetime.datetime.strptime(d1,'%Y-%m-%d')
		d2=datetime.datetime.strptime(d2,'%Y-%m-%d')
		userPins = []
		if not allowAction(d1,5,d2):
			return getJSResponse({"ret":2,"message":""})
		if UserIDs=='':
			deptidlist=[int(i) for i in deptIDs.split(',')]
			deptids=deptidlist
			if isContainedChild=="1":   #是否包含下级部门
				deptids=[]
				for d in deptidlist:#支持选择多部门
					if int(d) not in deptids :
						deptids+=getAllAuthChildDept(d,request)
			UserIDs=employee.objects.filter(DeptID__in=deptids)
		else:
			emplist=UserIDs.split(',')
			UserIDs=employee.objects.filter(id__in=emplist)  
		
		uids=[]
		for u in UserIDs:
			saveEmpScheduleLogToFile('emp_schedule','%s %s %s clear'%(dumps(request.POST),request.user,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),u.pin())
			userPins.append(u.PIN)
			u=u.id
			uids.append(u)
			deleteCalcLog(UserID=int(u),StartDate=d1,EndDate=d2)
			if delshift=='shifts':
				deleteUserShifts(uid=u,startdate=d1,enddate=d2)
		if delshift<>'shifts':
			tmp_t = d2 + datetime.timedelta(days=0,hours=23,minutes=59,seconds=0)
			USER_TEMP_SCH.objects.filter(UserID__in=uids,ComeTime__range=(d1, tmp_t)).delete()
		deleteTempData(uids,d1,d2)
		j=d1
		while j<=d2:
			for userid in uids:
				sql=getSQL_insert(USER_TEMP_SCH._meta.db_table,userid=userid,comeTime=(j+datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),leavetime=(j+datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),overtime=0)
				customSql(sql)
			j=j+datetime.timedelta(days=1)
		userCount = len(userPins)
		if userPins:
			userPins = ','.join(userPins)
		else:
			userPins = ''
		adminLog(time=datetime.datetime.now(),User=request.user, model=USER_TEMP_SCH._meta.verbose_name, action=u'%s'%_(u"Clear"),object=u'工号%s'%userPins[:100],count = userCount).save(force_insert=True)#
		return getJSResponse({"ret":0,"message":""})
	

@login_required
def ConvertTemparyShifts(request):
	if request.POST:
#		global SchedulerShifts
#		global FTTimeZones
		st=request.POST['StartDate']
		et=request.POST['EndDate']
		UserIDs=request.POST['UserIDs']
		deptIDs=request.POST.get('deptIDs',"")
		isContainedChild=request.POST.get('isContainChild',"")
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d')
		if not allowAction(st,5,et):
			return getJSResponse({"ret":2,"message":""})
		if UserIDs=='':
			deptidlist=[int(i) for i in deptIDs.split(',')]
			deptids=deptidlist
			if isContainedChild=="1":   #是否包含下级部门
				deptids=[]
				for d in deptidlist:#支持选择多部门
					if int(d) not in deptids :
						deptids+=getAllAuthChildDept(d,request)
			UserIDs=employee.objects.filter(DeptID__in=deptids)  
		else:
			emplist=UserIDs.split(',')
			UserIDs=employee.objects.filter(id__in=emplist)  
		
#		if UserIDs =="":
#			deptIDs=deptIDs.split(',')
#			UserIDs = employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
#			#UserIDs=",".join(["%s" % int(i) for i in userlist])
#		else:
#			UserIDs=UserIDs.split(',')
		
		for i in UserIDs:
			id=i.id
			SchedulerShifts=[]
			FTTimeZones=[]
			UserSchPlan=LoadSchPlan(i,True,False)
			SchedulerShifts=GetUserScheduler(i, st, et,UserSchPlan['HasHoliday'])
			SaveTempSch(id,st,et,SchedulerShifts)
		return getJSResponse({"ret":0,"message":""})
@login_required
def deleteEmployeeShift(request):
	saveScheduleLogToFile('del_shifts',dumps(request.POST),request.user)
	st=request.POST['StartDate']
	et=request.POST['EndDate']
	iscl=request.POST.get('isContainChild','0')
	deptids=request.POST.get('deptIDs','')
	UserIDs=request.POST['UserIDs'].split(',')
	flag=request.POST.get('flag','')
	try:
		st1=datetime.datetime.strptime(st,'%Y-%m-%d %H:%M:%S')
		et1=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
	except:
		st1=datetime.datetime.strptime(st,'%Y-%m-%d')
		pass
	

	st=datetime.datetime(int(st[0:4]),int(st[5:7]),int(st[8:10]),0,0)
	et=datetime.datetime(int(et[0:4]),int(et[5:7]),int(et[8:10]),0,0)
	chklbSchClass=request.POST.get('sTimeTbl','').split(',')
	if UserIDs==['']:
		if iscl=="1":
			deptids=getAllAuthChildDept(deptids,request)
		UserIDs=employee.objects.filter(DeptID__in=deptids)
	else:
		UserIDs=employee.objects.filter(id__in=UserIDs)
	if not allowAction(st,5,et):
		return getJSResponse({"ret":2,"message":""})
	for i in UserIDs:
		if chklbSchClass!=[''] and len(chklbSchClass)!=0:
			saveEmpScheduleLogToFile('emp_schedule','%s %s %s delete'%(dumps(request.POST),request.user,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),i.pin())
			SchedulerShifts=[]
			UserSchPlan=LoadSchPlan(i,True,False)
			SchedulerShifts=GetUserScheduler(i, st, et,UserSchPlan['HasHoliday'])
			schs=[]
			for t in SchedulerShifts:
				if t['SchID']!=int(chklbSchClass[0]):
					schs.append(t)
				# else:
					# if t['TimeZone']['StartTime']<>st1:
					# 	schs.append(t)
		
			if flag=='del_temp':
				USER_TEMP_SCH.objects.filter(UserID=i.id,ComeTime__range=(st, et+datetime.timedelta(days=1)),SchclassID__in=chklbSchClass).delete()
	
			else:
				SaveTempSch(i.id,st,et,schs)
	return getJSResponse({"ret":0,"message":""})
