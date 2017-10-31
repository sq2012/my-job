#coding=utf-8

from mysite.iclock.models import *
#from mysite.iclock.dataproc import appendDevCmd
from mysite.core.cmdproc import appendDevCmd
from mysite.core.cmdproc import appendEmpToDevNew

def dispatchEmpToAll(emp):
	nt=datetime.datetime.now()
	for dev in iclock.objects.all():#.exclude(DelTag=1).exclude(State=0):
		if (dev.State<>DEV_STATUS_PAUSE) and not dev.DelTag:
			#s=getEmpCmdStr(emp)
			#appendDevCmd(dev, s)
			appendEmpToDevNew([dev.SN], emp, cursor=None,cmdTime=nt,finger=1,face=1,PIC=1)

# def deleteEmpFromAll(pin):
# 	for dev in iclock.objects.all():#.exclude(DelTag=1).exclude(State=0):
# 		if (dev.State<>DEV_STATUS_PAUSE) and not dev.DelTag:
# 			appendDevCmd(dev, "DATA DEL_USER PIN=%s"%pin)


def dispatchEmpToAppDev(emp,devNum):
#	devs=iclock.objects.all().filter(DeptID=emp.DeptID)
	devs=iclock.objects.all()#.exclude(DelTag=1).exclude(State=0)
	nt=datetime.datetime.now()
	for dev in devs:
		if (dev.State<>DEV_STATUS_PAUSE) and not dev.DelTag:
			try:
				_Alias=dev.Alias.split('-')[1]
			except:
				_Alias=''
			if devNum==_Alias:
				#s=getEmpCmdStr(emp)
				#appendDevCmd(dev, s)
				appendEmpToDevNew([dev.SN], emp, cursor=None,cmdTime=nt,finger=1,face=1,PIC=1)

#def deleteEmpFromEnr(pin,devNum):
def deleteEmpFromEnr(pin):
	for dev in iclock.objects.all():#.exclude(DelTag=1).exclude(State=0):
			#try:
			#	_Alias=dev.Alias.split('-')[1]
			#except:
			#	_Alias=''
			#
			#if devNum==_Alias:
			#appendDevCmd(dev, "DATA DEL_USER PIN=%s"%int(pin))
		zk_delete_user_data(dev,pin)
