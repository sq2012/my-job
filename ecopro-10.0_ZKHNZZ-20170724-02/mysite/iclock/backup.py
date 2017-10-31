#!/usr/bin/env python
#coding=utf-8
from django.shortcuts import render_to_response
from mysite.utils import *
#from iclock.models import *
import subprocess,sys,os,datetime


def mysqlBackup(request):
	if request.method=='GET':
		return render_to_response('backup.html')
	
	Schtask=""
	if request.GET.has_key("executeVar"):
		backupPath=request.GET.get("backupPath")
		executeVar=request.GET.get("executeVar",1)
		if executeVar==1:
			executeDate=request.POST.get("executeDate").replace('-','/')
			executeTime=request.POST.get("executeTime","00:00:00")
			Schtask="schtasks /create /tn backupmysql /tr F:\zkeco\copyfile.bat /sc ONCE /st %s /sd %s"%(executeTime,executeDate)
		else:
			hzVar=request.POST.get("hzVar",1)
			if hzVar==1:
				dayTime=request.POST.get("dayTime")
			elif hzVar==2:
				weekDays=request.POST.get("weekDays")
				weekTime=request.POST.get("weekTime")
			else:
				monthDays=request.POST.get("monthDays")
				monthTime=request.POST.get("monthTime")
			startTime=request.POST.get("startTime")
			endTime=request.POST.get("endTime")
	else:
		Schtask="call F:\zkeco\copyfile.bat"
		subprocess.Popen([Schtask],shell=True,stdout=True)
		return getJSResponse("1")
				
	print os.path.abspath(os.path.dirname(sys.argv[0]))
	print Schtask
	p=subprocess.Popen([Schtask],shell=True,stdout=True)
	
	return render_to_response('backup.html')
	
	
