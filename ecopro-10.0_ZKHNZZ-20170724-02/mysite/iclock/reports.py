#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.base.models import *
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
from mysite.iclock.templatetags.iclock_tags import shortDate4, onlyTime,AbnormiteName,StateName,isYesNo,getSex,schName
import copy
from mysite.iclock.datasproc import *
from django.core.cache import cache

VERIFYS1={
  3: _("Card"),
  0:_("Password"),
  1:_("Fingerprint"),
  2:_("Card"),
  5:_("Add"),
  9:_("Other"),
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
	eee=datetime.datetime.now()
	wb = Workbook()
	ws = wb.add_sheet(exp)
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER
	al.vert = Alignment.VERT_CENTER
	
	a2 = Alignment()
	a2.horz = Alignment.HORZ_LEFT
	a2.vert = Alignment.VERT_CENTER
	
	
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
	
	style3 = XFStyle()
	style3.alignment = a2
	style3.borders = borders
	style3.num_format_str = 'general'
	
	
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
				style.num_format_str = 'YY/MM/DD'
			elif type(t[l])==type(tt):
				style.num_format_str = 'YY/MM/DD hh:mm:ss'
			else:
				style.num_format_str = 'general'
			ws.write(j, k, t[l], style)
			k+=1
		j+=1	
#	if exp=='attDailyTotal':
#		sy=GetCalcSymbol()
#		ws.write_merge(j+3, j+3, 0, len(head_i18n)-1, sy, style3)
	#print "=============",settings.ADDITION_FILE_ROOT
	wb.save("mysite/files/reports/%s.xls"%exp)
	
#	content=open("mysite/files/reports/%s.xls"%exp,'rb').read()
#	response=HttpResponse(mimetype="application/vnd.ms-excel")
#	response["Pragma"]="no-cache"
#	response["Cache-Control"]="no-store"
#	response['Content-Disposition'] = 'attachment; filename=%s.xls'%exp
	return HttpResponseRedirect("/iclock/file/reports/%s.xls"%exp)
#	response.write(content);


LeaveClassD={}
def getLeaveClass(id): #获得例外情况名称
	global LeaveClassD
	if id==None or id=='':
		return None
	else:
		try:
			if LeaveClassD=={}:
				LeaveClassD = LeaveClass.objects.values('LeaveID','LeaveName')
			for k in LeaveClassD:
				if k['LeaveID']==id:
					LeaveNa=k['LeaveName']
					break
			return 	transLeaveName(LeaveNa)	
		except:
			return ''
			
	

def getList(list_C,obj):#组合成传给页面的数据
	kkk=datetime.datetime.now()
	print 'getlistTime:',kkk
	li=[]
	for t in obj:
		d={}
		for k in list_C:
			if k=='PIN':
				try:
					d['PIN']=t.employee().PIN
				except:
					d['PIN']=t.PIN
			elif k=='EName':
				try:
					d['EName']=t.employee().EName
				except:
					d['EName']=t.EName
			elif k=='DeptID':
				try:
					d['DeptID']=t.employee().Dept().DeptName
				except:
					d['DeptID']=t.objByID(t.DeptID).DeptName
			elif k=='SchId':
				d['SchId']=schName(t.SchId_id)
			elif k in ['CheckType','CHECKTYPE']:
				d[k]=t.__getattribute__(k) and transAttState(t.__getattribute__(k)) or ''
			elif k=='NewType':
				d['NewType']=t.NewType and transAttState(t.NewType) or ''
			elif k=='AbNormiteID':
				d['AbNormiteID']=AbnormiteName(t.AbNormiteID).title()
			elif k=='Absent':
				d['Absent']=isYesNo(t.Absent).title()
			elif k=='MustIn':
				d['MustIn']=isYesNo(t.MustIn).title()
			elif k=='MustOut':
				d['MustOut']=isYesNo(t.MustOut).title()
			elif k=='AttDate':
				d['AttDate']=shortDate4(t.AttDate)
			elif k=='ExceptionID':
				d['ExceptionID']=getLeaveClass(t.ExceptionID)
			elif k=='SN':
				try:
					d['SN']=getDevice(t.SN_id).Alias
				except:
					d['SN']=''
			elif k=='State':
				d['State']=t.State and transAttState(t.State) or ''
			elif k=='Verify':
				try:
					d['Verify']=t.getComVerifys()#VERIFYS1[t.Verify]
				except:
					d['Verify']=''
			elif k in ['ClockInTime','ClockOutTime','StartTime','EndTime']:
				d[k]=onlyTime(t.__getattribute__(k))
			elif k=='Gender':
				d[k]=getSex(t.Gender)
			elif k in ['NoIn','NoOut']:
				d[k]=isYesNo(t.__getattribute__(k)).title()
			else:
				d[k]=t.__getattribute__(k)
				if isinstance(d[k],long):
					d[k]=int(d[k])
		li.append(d.copy())
	print 'totallisttime:',datetime.datetime.now()-kkk
	return li
nameDic={"attRecAbnormite":_('Record Details'),
		 "attShifts":_('Shift Details'),
		"LateAndEarly":_('Excep.Att.Report'),
		"AttException":_('Exception Details'),
		"attTotal":_('Calculated items'),
		"transaction":_('Original Records'),
		"addTransaction":_('Forget Records'),
		"attDailyTotal":_('Daily Report'),
		"employeeList":_('Employee Reports'),
		"attTotalLeave":_('Calculated Leaves'),
		"originalReport":_('Original Reports'),
		}
def formatTime(l_st,l_et):#格式化时间
	l_st=datetime.datetime.strptime(l_st,'%Y-%m-%d')
	l_et=datetime.datetime.strptime(l_et,'%Y-%m-%d %H:%M:%S')
	return l_st,l_et
	
@permission_required("iclock.browse_itemdefine")
def exportReport(request):
	request.user.iclock_url_rel='../..'
	request.model = transactions	
	l_user=request.POST.get('UserIDs',"")
	deptID=request.POST.get('deptIDs',"")
	l_st=request.POST['ComeTime']
	l_et=request.POST['EndTime']+" 23:59:59"
	exp=request.POST['tblName']
	sss=datetime.datetime.now()
#	print 'start time:',sss
	userlist=[]
	li=[]
	obj=None
	list_H=[]
	list_C=[]
	list_CA=[]
	dis=[]
	lookup_params={}

	if exp == 'attRecAbnormite':
		lookup_params={'checktime__gte':l_st,'checktime__lte':l_et}
	elif exp == 'transactions':
		lookup_params={'TTime__gte':l_st,'TTime__lte':l_et}
	elif exp == 'addTransaction':
		lookup_params={'TTime__gte':l_st,'TTime__lte':l_et}
#	elif exp == 'attpriReport':
#		lookup_params={'CHECKTIME__gte':l_st,'CHECKTIME__lte':l_et}
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
	
	if exp=='attRecAbnormite':
		obj=attRecAbnormite.objects.all().filter(**lookup_params)
		list_H=[_('department name'),_('PIN'),_('EName'),_('checktime'),_('verification'),_('CheckType'),_('NewType'),_('Memo.'),_('device')]
		list_C=['DeptID','PIN','EName','checktime','Verify','CheckType','NewType','AbNormiteID','SN']
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','checktime']
		obj=obj.order_by(*orderStr)
	elif exp =='LateAndEarly':
		obj=attShifts.objects.all().filter(**lookup_params)
		obj = obj.filter(Q(Late__gt=0)|Q(Early__gt=0)|Q(StartTime__isnull=True)|Q(EndTime__isnull=True)|Q(Absent__exact=1))
		obj = obj.exclude(ExceptionID__gt=0)
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','AttDate']
		obj=obj.order_by(*orderStr)
		list_H=[_('department name'),_('PIN'),_('EName'),_('AttDate'),_('SchId'),_('Late'),_('Early'),_('noin'),_('noout'),_('Absent')]
		list_C=['DeptID','PIN','EName','AttDate','SchId','Late','Early','NoIn','NoOut','Absent']
	
	elif exp =='attShifts':
		l_st,l_et=formatTime(l_st,l_et)
		list_CA,list_H,r=ConstructAttshiftsFields1()
		re=CalcAttShiftsReportItem(request,deptID,l_user,l_st,l_et)
		obj=re['datas']
		list_CA.remove('userid')
		list_H.remove('UserID')
		
		dis=FetchDisabledFields(request.user,exp)
	elif exp == 'AttException':
		obj=AttException.objects.all().filter(**lookup_params)
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','AttDate']
		obj=obj.order_by(*orderStr)

		list_H=[_('department name'),_('PIN'),_('EName'),_('AttDate'),_('StartTime'),_('EndTime'),_('ExceptionID'),_('TimeLong'),_('InScopeTime')]
				
		list_C=['DeptID','PIN','EName','AttDate','StartTime','EndTime','ExceptionID','TimeLong','InScopeTime']
	elif exp=='attTotal':
		l_st,l_et=formatTime(l_st,l_et)
		re=CalcReportItem(request,deptID,l_user,l_st,l_et)
		obj=re['datas']	
		dis=FetchDisabledFields(request.user,exp)
		list_CA=re['fieldnames'][1:]
		list_H=re['fieldcaptions'][1:]
	elif exp=='attDailyTotal':
		l_st,l_et=formatTime(l_st,l_et)
		re=CalcReportItem(request,deptID,l_user,l_st,l_et,1)
		obj=re['datas']	
		dis=FetchDisabledFields(request.user,exp)
		
		list_H=re['fieldcaptions']
		list_CA=re['fieldnames']
	elif exp=='transactions':
		obj=transactions.objects.all().filter(**lookup_params)
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','TTime']
		obj=obj.order_by(*orderStr)
		list_H=[_('department name'),_('PIN'),_('EName'),_('Time'),_('State'),_('Verification'),
							_('Device name')]
						
		list_C=['DeptID','PIN','EName','TTime','State','Verify','SN']
	elif exp=='addTransaction':	
		obj=transactions.objects.all().filter(**lookup_params).filter(Verify=5)
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','TTime']
		list_H=[_('department name'),_('PIN'),_('EName'),_('Time'),_('State'),_('Verification')]
								
		list_C=['DeptID','PIN','EName','TTime','State','Verify']
	elif exp=='attTotalLeave':
		l_st,l_et=formatTime(l_st,l_et)
		re=CalcLeaveReportItem(request,deptID,l_user,l_st,l_et)
		obj=re['datas'] 
		list_H=re['fieldcaptions']
		list_C=re['fieldnames']
	elif exp=='originalReport': 
		obj=attpriReport.objects.filter(**lookup_params)
		list_H=[_('department name'),_('PIN'),_('EName'),_('AttDate'),_('SchName'),_('Original Attendance'),_('Add Attendance'),_('Leave')]
		list_C=['DeptID','PIN','EName','AttDate','SchName','AttChkTime','AttAddChkTime','AttLeaveTime']
		orderStr=['UserID__DeptID__DeptID','UserID__PIN','AttDate']
		obj=obj.order_by(*orderStr)
		
	if exp in ['attShifts','attTotal','attDailyTotal',]:
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
		
	len(obj)
	if exp in ['attTotal','attDailyTotal','attTotalLeave','attShifts']:
		for l in obj:
			for k in l.keys():
				if isinstance(l[k],long):
					l[k]=int(l[k])
		li=obj
	else:
		li=getList(list_C,obj)
#	print 'end time:',datetime.datetime.now()-sss
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
		try:
			lookup_params['DeptID__in']=lookup_params['UserID__DeptID__in']
			del lookup_params['UserID__DeptID__in']
		except:
			pass
		obj=employee.objects.filter(**lookup_params)
		list_H=[_('department name'),_('PIN'),_('EName'),_('Sex'),_('Nationality'),_('Title'),_('Office phone')]
		list_C=['DeptID','PIN','EName','Gender','National','Title','Tele']
		orderStr=["DeptID__DeptID","PIN"]
		obj=obj.order_by(*orderStr)
	elif exp == 'noFingerPrint':
		try:
			lookup_params['DeptID__in']=lookup_params['UserID__DeptID__in']
			del lookup_params['UserID__DeptID__in']
		except:
			pass
#		obj=employee.objects.filter(DeptID__DeptID__in=deptid).extra(where=['UserID NOT IN (%s)'%('select userid from template')])
		obj=employee.objects.filter(**lookup_params).extra(where=['UserID NOT IN (%s)'%('select userid from template')])
		list_H=[_('department name'),_('PIN'),_('EName'),_('Sex'),_('Nationality'),_('Title'),_('Office phone')]
		list_C=['DeptID','PIN','EName','Gender','National','Title','Tele']
		orderStr=["DeptID__DeptID","PIN"]
		obj=obj.order_by(*orderStr)
	li=getList(list_C,obj)
	Title=nameDic[exp]
	return exportXLS(exp,Title,list_C,list_H,li)

PAGE_LIMIT_VAR = 'l'
#@permission_required("iclock.browse_itemdefine")
def index(request):
	request.user.iclock_url_rel='../..'
	#判断首页设为默认页，无权限管理员登录报错
	dataModel=GetModel("ItemDefine")
	if not hasPerm(request.user, dataModel, "browse"):
		return getJSResponse(_("You do not have the browse %s permission!")%(u"报表"))

	request.model = transactions	
	unit=GetCalcUnit()
	symbol=GetCalcSymbol()
#	us=',  '.join([ "%s : %s"% (k,v) for k ,v in unit.items()])
	dc={}
	dc['unit']=unit
	dc['symbol']=symbol
	settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
	limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
	try:
		colModel=transactions.colModels()
	except:
		colModel=[]
	return render(request,'reports.html',
							 {'latest_item_list': smart_str(dumps(dc)),
							'from': 1,
							'page': 1,
							'colModel':dumps(colModel),
							'limit': limit,
							'item_count': 4,
							'page_count': 1,
							'iclock_url_rel': request.user.iclock_url_rel
							})	

#@permission_required("iclock.browse_itemdefine")
def ihr_index(request):
	settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
	limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))

	return render(request,'ihr_reminder_list.html',
							 {
							'from': 1,
							'page': 1,
							'limit': limit,
							'item_count': 4,
							'page_count': 1
							})

#@permission_required("iclock.browse_reverse")
def reverse_index(request):
	settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
	limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))

	return render(request,'ihr_reverse_list.html',
							 {
							'from': 1,
							'page': 1,
							'limit': limit,
							'item_count': 4,
							'page_count': 1
							})
