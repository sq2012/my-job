#coding=utf-8
from mysite.iclock.models import *
import string
import datetime
import time
from mysite.utils import errorLog,tmpFile

def readTransFrom(UserID, startTime):
#	return transaction.objects.filter(UserID=UserID, TTime__gte=startTime).order_by('TTime').values('TTime','SN')
	str="userid = %s and checktime >= '%s'"%(UserID, startTime)
	row=transactions.objects.extra(where=[str])
	row=row.extra(order_by=['TTime']).values('TTime','SN')
	return row
	
# 人员排班数据下发	
#------------------------------------------------------------------------------
#工号\t日期\t上班时间\t下班时间
#其中日期格式为YYYYMMDD，上班时间、下班时间格式为24小时制HHNNSS

invalid_pins=[]

def transASch(line):
	s=line.split("\t")
	pin=s[0]
	if pin in invalid_pins: return None
	try:	
		sch={'UserID':employee.objByPIN(pin, None).id, 'PIN': pin}
	except:
		invalid_pins.append(pin)
		return None
	startDate=s[1]
	sch['Date']=datetime.datetime.strptime(startDate, "%Y%m%d")
	sch['Start']=datetime.datetime.strptime(startDate+s[2],"%Y%m%d%H%M%S")
	if s[3][:6]=='240000':
		sch['End']=datetime.datetime.strptime('235900',"%H%M%S")
		return sch
	endTime=datetime.datetime.strptime(startDate+s[3][:6],"%Y%m%d%H%M%S")
	if sch['Start']==endTime:
#		对24小班的处理
		if s[2]=='000000':
			return None
		elif s[3]=='240000':
			sch['End']=endTime+datetime.timedelta(1)
		else:
			sch['End']=endTime+datetime.timedelta(1)
	elif endTime<sch['Start']:
		sch['End']=endTime+datetime.timedelta(1)
	else:
		sch['End']=endTime
	return sch

def cmpSch(s1, s2):
	u1=s1["UserID"]
	u2=s2["UserID"]
	if u1<u2: return -1
	if u1>u2: return 1
	t1=s1["Date"]
	t2=s2["Date"]
	if t1<t2: return -1
	if t1>t2: return 1
	t1=s1["Start"]
	t2=s2["Start"]
	if t1<t2: return -1
	if t1>t2: return 1
	return 0
			
def readSchedule(schFile):
	fileData=file(schFile,'rb').read()
	schs=[]
	for line in fileData.split("\n"):
		try:
			if line:
				sch=transASch(line)
				if sch: schs.append(sch)
		except Exception, e:
			print "LINE  :", line
			print "ERROR :", e.message
	schs.sort(cmpSch)
	return schs


# 考勤记录上传: Sap对考勤系统数据格式的要求
#------------------------------------------------------------------------------	
#（上班数据）P10000320080808080000200808080800000006900710000010
#（下班数据）P20000320080808080000200808080800000006900710000010
#SATZA                           CHAR3	上下班表示 P10/P20
#TERID                           CHAR4	刷卡机编号（终端标识） 0003
#LDATE                           CHAR8	日期年月日 20080808
#LTIME                           CHAR6	日期时分秒 080000
#ERDAT                           CHAR8	日期年月日 20080808（重复一次刷卡日期）
#ERTIM                           CHAR6	日期时分秒 080000（重复一次刷卡分秒）
#ZAUSW                           CHAR8	卡号 00069007
#PERNR                           CHAR8	职工编号 10000010 （该字段非必需）
#
CHECK_IN=True
CHECK_OUT=False


def writeATran(f, pin, ttime, overDay, stateIn=CHECK_IN):
	st=ttime.strftime("%Y%m%d%H:%M:%S")
	devSN='0000'
	s="%s%s%s%s%s\r\n"%(
		pin,st,stateIn and "P10" or "P20",
		overDay,devSN
		)
	f.write(s)

def writeATranInOut(f, sch, pin):
	if 'Saved' in sch: return
#	print 'writeATranInOut',pin,sch
	overDay=0
	if sch['Start'].day < sch['End'].day:
		overDay='<'
	else:
		overDay='='
	
	if 'In' in sch:
		writeATran(f, pin, sch['In']['TTime'],  overDay,CHECK_IN)
	if 'Out' in sch:
		writeATran(f, pin, sch['Out']['TTime'],  overDay,CHECK_OUT)
	sch['Saved']=True

def outALine(s):
	return
	print s

#将上班前1个小时到下班后3个小时作为一个时间段统一考虑，
#例如每天上班08:30—17:30，那将落在7:30—第二天20:30这个时间段内的刷卡资料来进行判断，
#并且结合上下班时间进行判断：在下班卡时间内如果有多条记录，
#且刷卡数据的时间间隔超过一个小时，在这个时间段内的第一条数据默认为“上班签到”，
#最后一条默认为“下班签退”； 如果员工在这个时间段内只有一条刷卡记录,
#如果在上班前1个小时到上班后1小时之间,则为“上班签到”,
#如果在上班1小时后到下班后3个小时之间,则为“下班签退”.
#					 
# p0----in---p3-----------out------------p1
def adjustState(t, sch, p0, p1, p2, log,inMiddFlag):
#	print 122,p0,p1,p2,log,inMiddFlag
	if t < p0:#解决没有排班但是正常刷卡,记录的考勤状态的上班时间为非排班第一次刷卡的时间
		return
#	print "sch",sch
	if inMiddFlag:
		sche20=sch['End']+datetime.timedelta(0, 1*60*20)#下班20分钟后
	
		if 'Out' not in sch['cache']:
			sch['cache']['Out']=log
		else:
			if 'In' not in sch['cache']:
				sch['cache']['In']=log
			else:
#				print 'tt',t,sche20,t <= sche20,sch['cache']['In']['TTime'],type(sch['cache']['In']['TTime'])
				if t <= sche20:
					sch['cache']['Out']=t
				else:
					if sch['cache']['In']['TTime']<=sche20:#取上午班签退最晚一条,下午班签到最早的一条,其它不要
						sch['cache']['Out']=sch['cache']['In']
						sch['cache']['In']=log
					
				
		
		return 
	else:
		if 'In' not in sch:
			if 'Out' not in sch:
				if t<p2:
					sch['In']=log
					outALine( "In : %s"%log['TTime'])
				else:
					sch['Out']=log
					outALine( "Out: %s"%log['TTime'])
				return
			#已经有了一个签退记录
			t2=sch['Out']['TTime']
			if (t-t2).seconds>=1*60*60: #超过1小时
				sch['In']=sch['Out']
				sch['Out']=log
				outALine("In-: %s"%sch['In']['TTime'])
				outALine("Out: %s"%log['TTime'])
				return
			#没有超过1小时, 用新记录替代旧记录
			sch['Out']=log
			outALine("Out: %s"%log['TTime'])
			return
	
	t2=sch['In']['TTime']
#		对24小班的处理
	if (t-t2).seconds>=1*60*60 or (t-t2).days >=1: #超过1小时为签退时间
		sch['Out']=log
		outALine("Out: %s"%log['TTime'])
		return
	outALine( "!!!: %s"%log['TTime'])
	

def adjustStateSp(t, sch, p0, p1,log):
	if t < p0:#解决没有排班但是正常刷卡,记录的考勤状态的上班时间为非排班第一次刷卡的时间
		return
	if 'In' not in sch:
		if 'Out' not in sch:
			sch['In']=log
			outALine( "In : %s"%log['TTime'])
			return
		#已经有了一个签退记录
		t2=sch['Out']['TTime']
#		if (t-t2).seconds>=1*60*60: #超过1小时
		sch['In']=sch['Out']
		sch['Out']=log
		outALine("In-: %s"%sch['In']['TTime'])
		outALine("Out: %s"%log['TTime'])
		return
		
	sch['Out']=log
	return
	



def writeTransState(f, logs, schs, lastEmp,spFlag=0):
#	print "\n\nwriteTransState", lastEmp
	if not logs: return
	if not schs: return
	
	pin=schs[0]["PIN"]
#	print "logs:",logs
#	print "shcs:",schs
	week=[0,1,2,3,4,5,6]
	dayOfWeek=[0]
	schi=0
	outFlag=0
	inMiddFlag=0
	
	schl=len(schs)
	sch=schs[schi]
	sch['cache']={}
	if spFlag:      #特殊人员的规则
		sp0=sch['Start']
		sp1=sch['End']
	else:
		sp0=sch['Start']-datetime.timedelta(0, 2*60*60)
		sp1=sch['End']+datetime.timedelta(0, 3*60*60)
		sp2=sch['Start']+datetime.timedelta(0, 1*60*60)
	sa=schi+1
#	print 'sclen',schl,sa
	if sa < schl: #小于排班长度，取下一排班开始时间
		sNextS = schs[sa]['Start']-datetime.timedelta(0, 2*60*60)
	else:
		sNextS=sp1

#	print "SCH: %s - %s"%(sch['Start'], sch['End'])
	for log in logs:
		t=log['TTime']
#		print "LOG: %s"%t
		if t<sp0:
#			print "SKIP LOG"
			pass
		else:
			if t<sp1 and t >=sNextS:
#				print '++++++'
				inMiddFlag=1
			
			if t>=sp1: # out the range
				try:
					if 'Out'  in sch['cache']:
						sch['Out']=sch['cache']['Out']
				except:
					sch['cache']={}
				writeATranInOut(f, sch, pin)
				if 'In' in sch['cache']:
					sin=sch['cache']['In']
				else:
					sin=None
				
				#查找下一个包含t的时间段
				schi+=1
#				print '////',schi,schl
				while schi<schl:
#					print '------'
					sch=schs[schi]
					dw=sch['Start'].weekday()
					inMiddFlag=0
#					print "dw",dw,dayOfWeek
#					if dw in dayOfWeek:#这个星期几有没有出现过，出现过就退出
#						break
#					else:
#						dayOfWeek.append(dw)#没有出现过就添加列表中
					if spFlag:
						sp0=sch['Start']
						sp1=sch['End']
					else:
						if sin!=None:
							sch['In']=sin
						sp0=sch['Start']-datetime.timedelta(0, 2*60*60)
						sp1 =sch['End']+datetime.timedelta(0, 3*60*60)
						sp2=sch['Start']+datetime.timedelta(0, 1*60*60)
						sa=schi+1
						if sa < schl: #小于排班长度，取下一排班开始时间
							sNextS = schs[sa]['Start']-datetime.timedelta(0, 2*60*60)
						else:
							sNextS=sp1
#					print 'sss',sp1,sNextS,t
					if t<sp1 :
						if t<sp1 and t >=sNextS:
#							print '++++++'
							inMiddFlag=1
						break #找到一时间段包含t
					schi+=1
#					print "SKIP this SCH"
				if t>=sp1: #已经超过了所有的时间段
#					print "Out of Schedule range"
					break
			if spFlag:
				adjustStateSp(t, sch, sp0, sp1,log)
			else:
				adjustState(t, sch, sp0, sp1, sp2, log,inMiddFlag)
	writeATranInOut(f, sch, pin)	


def outLogs(logs):
	return
	for l in logs:
		print "%s"%l['TTime']

def parseTransState(schFile, fileName="l.txt"):
	schs=readSchedule(schFile)
	#schs 是按照人、日期、时间排序的，从而保证了同一个人的时间段在一起
	if not schs: return
	f=file(fileName,"w+b")
	lastEmp=""
#	logs=[]
	lastSchs=[]
	s=[]
	splEmp=employee.objects.filter(SECURITYFLAGS=1).values_list('id', flat=True).order_by('id')
	for e in splEmp:
		s.append(int(e))
	spFlag=0
	for sch in schs:
		emp=sch['UserID']
		if emp in s:
			spFlag=1
			
		if emp<>lastEmp:
			if lastEmp<>"":
				if spFlag==1:
					spFlag=0
					writeTransState(f, logs, lastSchs, lastEmp,spFlag)
				else:
					writeTransState(f, logs, lastSchs, lastEmp)
			logs=readTransFrom(emp, sch['Date']-datetime.timedelta(1))
#			outLogs(logs)
			lastEmp=emp
			lastSchs=[]
		lastSchs.append(sch)
	if lastSchs:
		writeTransState(f, logs, lastSchs, lastEmp)
	f.close()

if __name__=='__main__':
	parseTransState('c:\shandong\schedule20080916231250.txt ') #'C:\shandong\\tran200809010.txt','C:\shandong\st200809010.txt')

			 