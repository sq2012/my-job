#coding=utf-8
from mysite.iclock.models import *
from mysite.iclock.devview import checkDevice
from django.shortcuts import render_to_response
import time, datetime
from mysite.iclock.empdevsyn import *
from mysite.utils import errorLog,tmpFile
from django.utils.translation import ugettext as _
from django.conf import settings
#from mysite.settings import *
from mysite.base.models import *
from django.contrib.auth.decorators import permission_required, login_required

#新入职人员的工号,卡号,姓名,employee20080815165451.txt
#SampleEmp="""
#I	10000165	00000000	李三
#I	10000172	87654321	赵四(xjl test)
#D	00000190	00000000	C007100038"""

import os
from ftplib import FTP



FTP_HOST=0
FTP_USER=0
FTP_PASSWORD=0
FTP_EMP_PATH=0
FTP_SCH_PATH=0
FTP_TRANS_PATH=0
FTP_EMP_LOCAL=0
FTP_SCH_LOCAL=0

def ftplink():
	import dict4ini	
	global FTP_HOST
	global FTP_USER
	global FTP_PASSWORD
	global FTP_EMP_PATH
	global FTP_SCH_PATH
	global FTP_TRANS_PATH
	global FTP_EMP_LOCAL
	global FTP_SCH_LOCAL
	
	
	#x = dict4ini.DictIni(settings.APP_HOME+'/attsite.ini')
	#FTP_HOST=x.FTP.HOST
	#FTP_USER=x.FTP.USER
	#FTP_PASSWORD=x.FTP.PASSWORD
	#FTP_EMP_PATH=x.FTP.EMP_PATH
	#FTP_SCH_PATH=x.FTP.SCH_PATH
	#FTP_TRANS_PATH=x.FTP.TRANS_PATH
	#FTP_EMP_LOCAL=settings.WORK_PATH+'/tmp/processed/emp/'
	#FTP_SCH_LOCAL=settings.WORK_PATH+'/tmp/processed/sch/'



def insertEmp(pin, card, name,devNum,sec=0):
	try:
		card="%s"%int(card)
	except:
		card=''

	try:
		devnum=int(devNum)
	except:
		devnum=1
	dep=department.objByNumber(devnum)
	if dep and dep.DelTag==1:
		dep.DelTag=0
		dep.save()
	if dep==None:
		if int(devNum)==0:
			print "depID 0"
			return 
		dep=department(DeptName=devNum, DeptNumber=devnum)
		dep.save()
		#dep = department.objects.get(DeptName=devNum)
	try:
		emp=employee.objects.get(PIN=pin)
		olddept=emp.DeptID
	except:
		emp=employee(PIN=pin, Card=card, EName=name,SECURITYFLAGS=sec,DeptID=dep)
		olddept=None
#		print "New employee: %s, %s"%(pin,name)
	else:
		if emp.EName==name and emp.Card==card and \
			emp.SECURITYFLAGS == sec and dep.DeptID ==emp.DeptID_id and not emp.DelTag :
#			print "Employee %s already exists"%pin
			return
		emp.EName=name
		emp.Card=card
		emp.DelTag=0
		emp.DeptID = dep
		emp.SECURITYFLAGS=sec
#		print "Modify employee: %s"%emp	 
	try:
		emp.save()
#		print "insert",pin,devNum,type(devNum)
		if olddept:
			devs=iclock.objects.all().exclude(DelTag=1)
			for dev in devs:
				try:
					_Alias=int(dev.Alias.split('-')[1])
				except:
					_Alias=0
				if int(olddept.DeptNumber)==_Alias:
					appendDevCmd(dev, "DATA DEL_USER PIN=%s"%int(pin))
				if int(olddept.DeptNumber)==99:
					appendDevCmd(dev, "DATA DEL_USER PIN=%s"%int(pin))

		if devNum=="0099":
			dispatchEmpToAll(emp)
		else:
			dispatchEmpToAppDev(emp,devNum)
	except Exception, e:
		print e.message

def deleteEmp(pin,devNum):
	#deleteEmpFromEnr(pin,devNum)
	deleteEmpFromEnr(pin)
	print "Delete employee %s from devices"%pin
	try:
		emp=employee.objects.get(PIN=pin)
	except:
		print "Employee %s not found"%pin
		return
	emp.DelTag=1
	emp.save()

def readFile(fn):
	f=file(fn, "rb")
	data=f.read()
	if data[:3]=="\xef\xbb\xbf": #UTF-8 tag of a text file
		data=data[3:]
	data=data.decode("utf-8").split('\n')
	f.close()
#	tmpFile("123.txt",u'\r\n'.join(data).encode("GB18030")) 
	return data

def processEmpFile(f, fn):
	print "Process employee file %s"%fn
	data=readFile(fn)
#	empFile=fn.split("\t",-1)
	for line in data:
		if line:
			try:
				emp=line.split("\t")
				if emp[0]=="I":
					if 'special' in fn:
						insertEmp(emp[1], emp[2], emp[3],emp[4][:4].split('\r')[0],1)
					else:
						insertEmp(emp[1], emp[2], emp[3],emp[4][:4].split('\r')[0])
				elif emp[0]=="D":
					deleteEmp(emp[1],emp[4][:4].split('\r')[0])
				else:
					print "Not a valid employee line: %s"%line
			except Exception, e:
				errorLog()
	UpdateDeptCache()

def _readFromFtp(
		ftp_host, 
		ftp_user, 
		ftp_pwd, 
		ftp_path, 
		filePrefix, 
		iwm_e_path, 
		processor=processEmpFile):
	if iwm_e_path[-1] not in ['\\', '/']: 
		iwm_e_path=iwm_e_path+"/"
	try:
		os.makedirs(iwm_e_path)
	except: pass
	try:
		f=FTP(ftp_host)
		f.login(ftp_user,ftp_pwd)
		f.cwd(ftp_path)
	except Exception, e:
		print e.message
		return []
	print "Open FTP %s OK"%ftp_host
	fns=[]
	flist=f.nlst()
	d=datetime.datetime.now()
	minfn=(d-datetime.timedelta(30)).strftime(filePrefix+"%Y%m%d%H%M%S.txt")
	maxfn=(d+datetime.timedelta(0,30)).strftime(filePrefix+"%Y%m%d%H%M%S.txt")
	for fn in flist:
		if fn>minfn and fn<maxfn:
			try:
				datetime.datetime.strptime(fn, filePrefix+"%Y%m%d%H%M%S.txt")
			except:
				pass
			else: #valid filename
				preM=(12 if d.month==1 else d.month -1)
				if len(str(preM))<2:
					preM="0%s"%preM
				if d.month==1:
					preMd=iwm_e_path[:-7]+("%s%s/")%(d.year -1,preM)
				else:
					preMd=iwm_e_path[:-7]+("%s%s/")%(d.year,preM)
				pre=iwm_e_path[:-7]+("%s%s/")%(d.year,preM)
#				print 11111,d.replace(month=d.month-1) #另一种替换的方法
				if not os.path.exists(iwm_e_path+fn) and \
				not os.path.exists(preMd+fn) and not os.path.exists(pre+fn): #检查文件是否处理过
					fns.append(fn)

	if fns:
		fns.sort()
		cachedEmployee={}
		for fn in fns:
			try:
				print "Read file from ftp: ", fn
				try:
					fs=open(iwm_e_path+fn, 'w+b')
					f.retrbinary("RETR %s"%fn, fs.write)
					fs.close()
				except Exception, e:
					print e.message
					fs.close()
					os.remove(iwm_e_path+fn)
				else:
					processor(f, iwm_e_path+fn)
			except Exception, e:
				errorLog()
	try:
		f.quit()
	except: pass
	return fns

def readFromFtp(ftp_host, ftp_user, ftp_pwd, ftp_path, 
		filePrefix, iwm_e_path, processor=processEmpFile):
	print "ftp:", ftp_host, ftp_user, ftp_pwd, ftp_path, filePrefix
	d=datetime.datetime.now()
	mondir=d.strftime("%Y%m")
	iwm_e_path=iwm_e_path+mondir
	print "iwm_e_path:",iwm_e_path
	while(1):
		try:
			fns=_readFromFtp(ftp_host, ftp_user, ftp_pwd, 
				ftp_path, filePrefix, iwm_e_path, processor)
			print "processed file: ", fns
			if not fns:	break
		except Exception, e:
			errorLog()
			pass
	return fns

def uploadSAPFile(f, logfn,FTP_TRANS_PATH):
	
	fn=logfn.split(('\\' in logfn) and "\\" or "/")[-1] #得到不带目录的文件名
	fn=fn.split(('\\' in fn) and "\\" or "/")[-1] #得到不带目录的文件名
	print "Upload %s to ftp"%fn
	pwd=f.pwd()
	if pwd<>FTP_TRANS_PATH:
		#转到考勤记录目录
		f.cwd(FTP_TRANS_PATH)
	try:
		f.storbinary("STOR "+fn, file(logfn, "rb")) #上传文件
	except IOError:
		fh=file(logfn, "w+b")
		fh.write("\n")
		fh.close()
		f.storbinary("STOR "+fn, file(logfn, "rb")) #上传文件
	#改为规定的文件名
#	d=datetime.datetime.now()
#	logfn=d.strftime("%Y%m%d.txt")
	ftname=fn.split('.')[0]
	ftname=ftname[8:16]
	logfn="%s.txt"%ftname
	print "Rename %s to %s in ftp"%(fn, logfn)
	flist=f.nlst()
#	print "flist",flist,type(flist)
	
	#对同名文件的处理
	try:    
		i=1
		while 1:
			if logfn in flist:
				logfn="%s_%s.txt"%(ftname,i)
				i+=1
			else:
				break
		f.rename(fn, logfn)
	except Exception, e:
		errorLog()
		pass
	
	if pwd<>FTP_TRANS_PATH:
		#恢复到原来的目录
		f.cwd(pwd)

def processSchFile(f, fn):
	print "Process schdule file %s"%fn
	from mysite.iclock.transinout import parseTransState
	logfn=fn+'.trans.log'
	log=fn+'.trans'
	try:
		#根据上下班时间文件生成 带状态的考勤记录文件					 
		parseTransState(fn, logfn)
		os.rename(logfn,log)
	except:
		errorLog()
						   
#下传员工数据，通常该函数每天调用一次
def checkEmpFile():
	calc_data=loads(GetParamValue('sap_ftp','{}','sap'))
	readFromFtp(calc_data['SAPhost'], 
		calc_data['SAPuser'], 
		calc_data['SAPpassword'], 
		calc_data['SAPemp_path'], 
		'employee',
		settings.ADDITION_FILE_ROOT+'tmp/processed/emp/')

#下传特殊人员数据，通常该函数每天调用一次
def checkSpecFile():
	calc_data=loads(GetParamValue('sap_ftp','{}','sap'))
	
	readFromFtp(calc_data['SAPhost'],
		calc_data['SAPuser'], 
		calc_data['SAPpassword'], 
		calc_data['SAPemp_path'], 
		'special',
		settings.ADDITION_FILE_ROOT+'tmp/processed/emp/')



#下载排班数据，并据此生成、上传考勤记录，通常该函数每周调用一次
def checkSchFile():
	global FTP_SCH_LOCAL
	p_s="Start pro Time:%s"%datetime.datetime.now()
	stTime=datetime.datetime.now()
	calc_data=loads(GetParamValue('sap_ftp','{}','sap'))
	FTP_SCH_LOCAL=settings.ADDITION_FILE_ROOT+'tmp/processed/sch/'
	flag=readFromFtp(calc_data['SAPhost'], 
		calc_data['SAPuser'], 
		calc_data['SAPpassword'], 
		calc_data['SAPsch_path'], 
		'schedule', 
		FTP_SCH_LOCAL,
		processSchFile
		)
	if flag==[]:
		checkUpload()
	p_e="End pro Time:%s"%datetime.datetime.now()
	etTime=datetime.datetime.now()
	Toal="Toal Pro time:%s"%(etTime-stTime)
	s=p_s+'\r\n'+p_e+'\r\n'+Toal
	try:
		f=open(FTP_SCH_LOCAL+'TimeLog.txt', 'a+')
	except:
		f=open(FTP_SCH_LOCAL+'TimeLog.txt', 'wb')
	f.write("---%s: "%s)
	f.close()
#检查是否存在数据需要上传，通常该函数每小时调用一次
def checkUpload():
	global FTP_SCH_LOCAL
	calc_data=loads(GetParamValue('sap_ftp','{}','sap'))
	FTP_SCH_LOCAL=settings.ADDITION_FILE_ROOT+'tmp/processed/sch/'
	FTP_HOST=calc_data['SAPhost']
	FTP_USER=calc_data['SAPuser']
	FTP_PASSWORD=calc_data['SAPpassword']
	FTP_TRANS_PATH=calc_data['SAPtrans_path']
	from mysite.cab import listFile
	d=datetime.datetime.now()
	mondir=d.strftime("%Y%m")
	local=FTP_SCH_LOCAL+mondir+'/'
	files=listFile(local, ['*.trans'])
	preM=(12 if d.month==1 else d.month -1)
	if len(str(preM))<2:
		preM="0%s"%preM
	
	preMonDir=("%s%s/")%(d.year,preM)
	preLocal=FTP_SCH_LOCAL+preMonDir+'/'
	preFiles=listFile(preLocal, ['*.trans'])
	files.extend(preFiles)
	#print "logs:",files,preMonDir,preFiles
	
	if files:
		try:
			ftp=FTP(FTP_HOST)
			ftp.login(FTP_USER, FTP_PASSWORD)
			ftp.cwd(FTP_TRANS_PATH)
		except Exception, e:
			print 'trans_ftp====',e
			return
		for f in files:
			uploadSAPFile(ftp, f,FTP_TRANS_PATH)
			#上传完成后删除 考勤记录文件
			os.remove(f)
		ftp.quit()

def write_Data(fn,text):
	f=file(fn, "a+")
	try:
		f.write(text)
	except:
		pass
	f.write("\n")
	f.close()			 
	return fn
	
def read_Data(fn):
	f=file(fn, "rb")
	data=f.read()
	if data[:3]=="\xef\xbb\xbf": #UTF-8 tag of a text file
		data=data[3:]
	#data=data.decode("utf-8").split('\n')
	f.close()
#	tmpFile("123.txt",u'\r\n'.join(data).encode("GB18030")) 
	return data


def checkDeviceOffline():
	from mysite.iclock.sendmail import SendMail
	print "checkDeviceOffline",datetime.datetime.now()
	nt=datetime.datetime.now()
	last=nt-datetime.timedelta(seconds=3600)
	snlist=[]
	sns=''
	createDir(settings.ADDITION_FILE_ROOT+'/sap/')
	fn='%s.txt'%(settings.ADDITION_FILE_ROOT+'/sap/offline_'+nt.strftime('%Y-%m-%d'))
	try:
		file_sns=read_Data(fn)
	except:
		file_sns=''
	for dev in iclock.objects.filter(LastActivity__lt=last).exclude(DelTag=1).exclude(State=0):
		if dev.SN not in file_sns:
			snlist.append(dev.SN)
	if snlist:
		sns=','.join(sn for sn in snlist)

		calc_data=loads(GetParamValue('sap_email','{}','sap'))
		emails=calc_data['emails']
		mail = SendMail(u"%s"%(_(u'如下设备超过1小时未联机')),'email/offline_warn.html',{'content':sns,'sdate':datetime.datetime.now().strftime('%Y-%m-%d')},[emails],from_addr_name=u"")  
		try:
			mail.send_mail()
			write_Data(fn,sns)
		except Exception,e:
			print "send_mail",e

#通过Web服务器进行数据同步								 
def WMDataSync(request):
	if request.method=="POST":
		from mysite.tasks import installTasks
		ftplink()
		installTasks()
		checkUpload()
		checkSchFile()
		checkEmpFile()
		checkSpecFile()
#		checkUpload()
		return render_to_response("info.html", {"title":  _('Data synchronization'), 
			"content": u"OK!"
			})
	else:
		return render_to_response("info.html", {"title":  _('Data synchronization'), 
			"content": u"""
<form action="" method="POST" >
<input type='submit' value='RUN'/>
</form>
"""
			})

#def relodTrans():
#	from mysite.iclock.dataproc import *
#	iclock_list=iclock.objects.all()
#	try:
#		for li in iclock_list:
##			print 253,li,li.getDynState()
#			if li.getDynState()==1:
#				reloadLogDataCmd(li)
#	except Exception, e:
#		print e.message

@login_required
def index(request):
	action=request.GET.get('action')
	#print "----",action
	if action=='download_emp':
		checkEmpFile()
		checkSpecFile()
	elif action=='download_sch':
		checkSchFile()
	return getJSResponse({'ret':0,'message':u'执行完毕'})	


	
if __name__=='__main__':
	processEmpFile(1,'c:\shandong\employee20081201052652.txt') #'C:\shandong\\tran200809010.txt','C:\shandong\st200809010.txt')
