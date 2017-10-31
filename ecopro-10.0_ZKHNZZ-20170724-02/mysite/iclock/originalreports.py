#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from django.template import  RequestContext 
from django.shortcuts import render_to_response
from django.db import models
from django.contrib.auth.models import User, Permission
from mysite.iclock.iutils import *
from django.conf import settings
#REBOOT_CHECKTIME, PAGE_LIMIT, ENABLED_MOD, TIME_FORMAT, DATETIME_FORMAT, DATE_FORMAT
from django.utils.translation import ugettext_lazy as _
#from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from mysite.iclock.datas import *
import datetime
from django.core.paginator import Paginator
from mysite.iclock.dataview import *
from pyExcelerator import *
from mysite.iclock.templatetags.iclock_tags import shortDate4, onlyTime,AbnormiteName,StateName,isYesNo,getSex
import copy

VERIFYS1={
  3: u'%s'%_("Card"),
  0:u'%s'%_("Password"),
  1:u'%s'%_("Fingerprint"),
  2:u'%s'%_("Card"),
  5:u'%s'%_("Add"),
  9:u'%s'%_("Other"),
}
#ATTSTATES={
#	"I":_("Check in"),
#	"O":_("Check out"),
#	"8":_("Meal start"),
#	"9":_("Meal end"),
#	"2":_("Break out"),
#	"3":_("Break in"),
#	"4":_("Overtime in"),
#	"5":_("Overtime out"),
#	}

def exportXLS(exp,Title,head,head_i18n,content):   #导出xls格式文件
	wb = Workbook()
	ws = wb.add_sheet(exp)
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER
	al.vert = Alignment.VERT_CENTER
	
	
	font0 = Font()
	font0.name = 'Times New Roman'
	font0.bold = True
	
	font1 = Font()
	font1.name = 'Arial'
	font1.bold = True
	font1.height = 400
	
	pat1 = Pattern()
	pat1.pattern = Pattern.SOLID_PATTERN
	pat1.pattern_fore_colour = 0x22
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	borders1 = Borders()
	borders1.top = 0x11
	
	style = XFStyle()
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'
	
	
	style0 = XFStyle()
	style0.font = font0
	style0.alignment = al
	style0.pattern = pat1
	style0.borders = borders
	style0.num_format_str = 'general'
	
	
	style1 = XFStyle()
	style1.alignment = al
	style1.font = font1
	style1.borders = borders
	style1.num_format_str = 'general'

	
	style2 = XFStyle()
	style2.alignment = al
	style2.borders = borders
	style2.num_format_str = 'general'
	
	
	tt=datetime.datetime.now()
	today = datetime.date.today() 
	
	
	ws.write_merge(0, 1, 0, len(head_i18n)-1, Title, style1)
	
	for i in range(0, len(head_i18n)):
		ws.write(2, i, head_i18n[i],style0)
	j=3
	for t in content:
		k=0
		for l in head:
			if t[l] is None:
				t[l]=''
			if type(t[l])==type(today):
				style.num_format_str = 'M/D/YY'
			elif type(t[l])==type(tt):
				style.num_format_str = 'M/D/YY h:mm'
			else:
				style.num_format_str = 'general'
			ws.write(j, k, t[l], style)
			k+=1
		j+=1	
		
	wb.save("mysite/files/reports/%s.xls"%exp)
#	content=open("mysite/files/reports/%s.xls"%exp,'rb').read()
#	response=HttpResponse(mimetype="application/vnd.ms-excel")
#	response["Pragma"]="no-cache"
#	response["Cache-Control"]="no-store"
#	response['Content-Disposition'] = 'attachment; filename=%s.xls'%exp
	return HttpResponseRedirect("/iclock/file/reports/%s.xls"%exp)
#	response.write(content);


def getLeaveClass(id): #获得例外情况名称
	if id==None or id=='':
		return None
	else:
		try:
			
			LeaveC = LeaveClass.objects.select_related().get(LeaveID=id)
			return 	LeaveC.LeaveName	
		except:
			return ''
			


def getList(list_C,obj):
	li=[]
	for t in obj:
		d={}
		for k in list_C:
#				if k in ['PIN','EName','DeptID','SchId','CheckType','NewType','AbNormiteID','Absent','AttDate',\
#					'ClockInTime','ClockOutTime','StartTime','EndTime','ExceptionID','SN','State','Verify']:
			if k=='PIN':
				try:
					d['PIN']=t.UserID.PIN
				except:
					d['PIN']=t.PIN
			elif k=='EName':
				try:
					d['EName']=t.UserID.EName
				except:
					d['EName']=t.EName
			elif k=='DeptID':
				try:
					d['DeptID']=t.UserID.DeptID.DeptName
				except:
					d['DeptID']=t.DeptID.DeptName
			elif k=='SchId':
				d['SchId']=t.SchId.SchName
			elif k in ['CheckType','CHECKTYPE']:
				d[k]=t.__getattribute__(k) and transAttState(t.__getattribute__(k)) or ''
			elif k=='NewType':
				d['NewType']=t.NewType and transAttState(t.NewType) or ''
			elif k=='AbNormiteID':
				d['AbNormiteID']=AbnormiteName(t.AbNormiteID).title()
			elif k=='Absent':
				d['Absent']=isYesNo(t.Absent).title()
			elif k=='AttDate':
				d['AttDate']=shortDate4(t.AttDate)
			elif k=='ExceptionID':
				d['ExceptionID']=getLeaveClass(t.ExceptionID)
			elif k=='SN':
				try:
					d['SN']=t.SN.Alias
				except:
					d['SN']=''
			elif k=='State':
				d['State']=t.State and transAttState(t.State) or ''
			elif k=='Verify':
				try:
					d['Verify']=t.Verify and VERIFYS1[t.Verify]  or ''
				except:
					d['Verify']=''
			elif k in ['ClockInTime','ClockOutTime','StartTime','EndTime']:
				d[k]=onlyTime(t.__getattribute__(k))
			elif k=='Gender':
				d[k]=getSex(t.Gender)
			else:
				d[k]=t.__getattribute__(k)
				if isinstance(d[k],long):
					d[k]=int(d[k])
		li.append(d.copy())
	return li
nameDic={"attRecAbnormite":u'%s'%_('Record Details'),
		 "attShifts":u'%s'%_('Shift Details'),
		"LateAndEarly":u'%s'%_('Late and Early'),
		"AttException":u'%s'%_('Exception Details'),
		"attTotal":u'%s'%_('Calculated items'),
		"transaction":u'%s'%_('Original Records'),
		"checkexact":u'%s'%_('Forget Records'),
		"attDailyTotal":u'%s'%_('Daily Report'),
		"employeeList":u'%s'%_('Employee Reports'),
		}

@permission_required("iclock.browse_itemdefine")
def exportReport(request):
	request.user.iclock_url_rel='../..'
	request.model = transactions	
	l_user=request.POST.get('UserIDs',"")
	deptID=request.POST.get('deptIDs',"")
	l_st=request.POST['ComeTime']
	l_et=request.POST['EndTime']+" 23:59:59"
	exp=request.POST['tblName']
	
	userlist=[]
	li=[]
	obj=None
	list_H=[]
	list_C=[]
	list_CA=[]
	dis=[]
	lookup_params={}
	
#	if settings.DATABASE_ENGINE == 'oracle':
#		lookup_params_oracle=creatOracleParam(userlist)
	
	if exp == 'attRecAbnormite':
		lookup_params={'checktime__gte':l_st,'checktime__lte':l_et}
	elif exp == 'transactions':
		lookup_params={'TTime__gte':l_st,'TTime__lte':l_et}
	elif exp == 'checkexact':
		lookup_params={'CHECKTIME__gte':l_st,'CHECKTIME__lte':l_et}
	else:
		lookup_params={'AttDate__gte':l_st,'AttDate__lte':l_et}
	
	if l_user=='null' or l_user=='':
		deptidlist=[int(i) for i in deptID.split(",")]
		deptids=[]
		for d in deptidlist:#支持选择多部门
			if int(d) not in deptids :
				deptids+=getAllAuthChildDept(d,request)
		lookup_params['UserID__DeptID__in']=deptids
		
	else:
		lookup_params['UserID__in']=[int(i) for i in l_user.split(',')]
	
#	print lookup_params
	
	if exp=='attRecAbnormite':
		obj=attRecAbnormite.objects.all().filter(**lookup_params)
		list_H=[_('department name'),_('PIN'),_('EName'),_('checktime'),_('verification'),_('CheckType'),_('NewType'),_('Memo.'),_('device')]
		list_C=['DeptID','PIN','EName','checktime','Verify','CheckType','NewType','AbNormiteID','SN']
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','checktime']
		obj=obj.order_by(*orderStr)
	elif exp =='LateAndEarly':
		obj=attShifts.objects.all().filter(**lookup_params)
		obj = obj.filter(Q(Late__gt=0)|Q(Early__gt=0))
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','AttDate']
		obj=obj.order_by(*orderStr)
		list_H=[_('department name'),_('PIN'),_('EName'),_('AttDate'),_('Late'),_('Early')]
		list_C=['DeptID','PIN','EName','AttDate','Late','Early']
	
	elif exp =='attShifts':
		obj=attShifts.objects.all().filter(**lookup_params)
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','AttDate']
		obj=obj.order_by(*orderStr)
		list_H=FetchModelFieldsCaption('attShifts')	
		list_CA=FetchModelFields('attShifts')
		dis=FetchDisabledFields(request.user,exp)
	elif exp == 'AttException':
		obj=AttException.objects.all().filter(**lookup_params)
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','AttDate']
		obj=obj.order_by(*orderStr)
		list_H=[_('department name'),_('PIN'),_('EName'),_('StartTime'),_('EndTime'),_('ExceptionID'),
					_('AuditExcID'),_('OldAuditExcID'),_('TimeLong'),_('InScopeTime'),_('AttDate')]
				
		list_C=['DeptID','PIN','EName','StartTime','EndTime','ExceptionID','AuditExcID',
					'OldAuditExcID','TimeLong','InScopeTime','AttDate']
	elif exp=='attTotal':
		l_st=datetime.datetime.strptime(l_st,'%Y-%m-%d')
		l_et=datetime.datetime.strptime(l_et,'%Y-%m-%d %H:%M:%S')
		re=CalcReportItem(request,deptID,l_user,l_st,l_et)
		obj=re['datas']	
		dis=FetchDisabledFields(request.user,exp)
		list_CA=re['fieldnames'][1:]
		list_H=re['fieldcaptions'][1:]
	elif exp=='attDailyTotal':
		l_st=datetime.datetime.strptime(l_st,'%Y-%m-%d')
		l_et=datetime.datetime.strptime(l_et,'%Y-%m-%d %H:%M:%S')
		re=CalcReportItem(request,deptID,l_user,l_st,l_et,1)
		obj=re['datas']	
		dis=FetchDisabledFields(request.user,exp)
		
		list_H=re['fieldcaptions']
		list_CA=re['fieldnames']
	elif exp=='transactions':
		l_st=datetime.datetime.strptime(l_st,'%Y-%m-%d')
		l_et=datetime.datetime.strptime(l_et,'%Y-%m-%d %H:%M:%S')
		obj=transactions.objects.all().filter(**lookup_params)
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','TTime']
		obj=obj.order_by(*orderStr)
		list_H=[u'%s'%_('department name'),u'%s'%_('PIN'),u'%s'%_('EName'),u'%s'%_('Time'),u'%s'%_('State'),u'%s'%_('Verification'),
							u'%s'%_('Device name')]
						
		list_C=['DeptID','PIN','EName','TTime','State','Verify','SN']
	elif exp=='checkexact':	
		l_st=datetime.datetime.strptime(l_st,'%Y-%m-%d')
		l_et=datetime.datetime.strptime(l_et,'%Y-%m-%d %H:%M:%S')
		obj=checkexact.objects.all().filter(**lookup_params)
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','CHECKTIME']
		obj=obj.order_by(*orderStr)
		list_H=[u'%s'%_('department name'),u'%s'%_('PIN'),u'%s'%_('EName'),u'%s'%_('Check time'),u'%s'%_('Check type'),u'%s'%_('reson'),
							u'%s'%_('Modify by'),u'%s'%_('Modify date')]
						
		list_C=['DeptID','PIN','EName','CHECKTIME','CHECKTYPE','YUYIN','MODIFYBY','DATE']
		
	if exp in ['attShifts','attTotal','attDailyTotal']:
		list_C=copy.copy(list_CA)	
		k=0
		ln=[]
		for f in list_CA:
			if f in dis:
				ln.append(k)
				list_C.remove(f)
			k=k+1
		t=0
		for n in ln:
			num=n-t
			list_H.pop(num)
			t+=1
		

	if exp=='attTotal'or exp=='attDailyTotal':
		for l in obj:
			for k in l.keys():
				if isinstance(l[k],long):
					l[k]=int(l[k])
		li=obj
	else:
		li=getList(list_C,obj)
#	if exp=="attRecAbnormite":
#		Title=[_('Record Details')]
#	elif exp=="attShifts":
#		Title=[_('Shift Details')]
#	elif exp=="LateAndEarly":
#		Title=[_('Late and Early')]
#	elif exp=="AttException":
#		Title=[_('Exception Details')]
#	elif exp=="attTotal":
#		Title=[_('Calculated items')]
#	elif exp=="transaction":
#		Title=[_('Original Records')]
#	elif exp=="checkexact":
#		Title=[_('Forget Records')]
#	else:
#		Title=[_('Daily Report')]
	Title=nameDic[exp]
	return exportXLS(exp,Title,list_C,list_H,li)


@permission_required("iclock.browse_itemdefine")
def exportaffairsReports(request):
	request.user.iclock_url_rel='../..'
	request.model = transactions	
	l_user=request.GET.get('UserIDs',"")
	deptID=request.GET.get('deptIDs',"")
	exp=request.GET['tblName']
	userlist=[]
	li=[]
	obj=None
	list_H=[]
	list_C=[]
	list_CA=[]
	dis=[]
	lookup_params={}
	if l_user=='null' or l_user=='':
		deptidlist=[int(i) for i in deptID.split(",")]
		deptids=[]
		for d in deptidlist:#支持选择多部门
			if int(d) not in deptids :
				deptids+=getAllAuthChildDept(d,request)
		lookup_params['UserID__DeptID__in']=deptids
		
	else:
		lookup_params['UserID__in']=[int(i) for i in l_user.split(',')]
	if exp=='employeeList':
		lookup_params['DeptID__in']=lookup_params['UserID__DeptID__in']
		del lookup_params['UserID__DeptID__in']
		obj=employee.objects.all().filter(**lookup_params)
		list_H=[u'%s'%_('department name'),u'%s'%_('PIN'),u'%s'%_('EName'),u'%s'%_('Sex'),u'%s'%_('Nationality'),u'%s'%_('Title'),u'%s'%_('Office phone')]
		list_C=['DeptID','PIN','EName','Gender','National','Title','Tele']
		orderStr=["DeptID__DeptID","PIN"]
		obj=obj.order_by(*orderStr)
	li=getList(list_C,obj)
	Title=nameDic[exp]
	return exportXLS(exp,Title,list_C,list_H,li)


@permission_required("iclock.OriginalReport_itemdefine")
def index(request):
	request.user.iclock_url_rel='../..'
	request.model = transactions	
	return render_to_response('originalreports.html',
							RequestContext(request, {'latest_item_list': "",
							'from': 1,
							'page': 1,
							'limit': 10,
							'item_count': 4,
							'page_count': 1,
							'iclock_url_rel': request.user.iclock_url_rel,
							}))
	
