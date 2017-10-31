#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.core.tools import *
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response,render
from django.template.response import TemplateResponse



from django.core.exceptions import ObjectDoesNotExist
from exceptions import AttributeError
from django.core.cache import cache
import string,os
import datetime
import time
from mysite.utils import *
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import login_required,permission_required
from django import forms
from mysite.iclock.dataproc import *
from django.utils.encoding import force_unicode, smart_str
from django.contrib.auth.models import  Permission
from mysite.iclock.iutils import *
#from mysite.iclock.reb  import *
from django.conf import settings
#from mysite.cab import *
#from mysite.iclock.devview import checkDevice, getEmpCmdStr
from mysite.iclock.datv import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import  Group
from mysite.iclock.datautils import *
from mysite.iclock.admin_detail_view import *

from mysite.iclock.datas import *
from mysite.iclock.schedule import *
from mysite.iclock.templatetags.iclock_tags import *
from django.conf.urls import  include, url
from django.contrib.auth import get_user_model
from mysite.core.menu import *
from mysite.accounts.models import MyUser
import itertools
from mysite.iclock.reports import getLeaveClass
from mysite.iclock.nomodelview import getSingleAnnual

ALL_VAR = 'all'
ORDER_VAR = 'o'
ORDER_TYPE_VAR = 'ot'
PAGE_VAR = 'p'
SEARCH_VAR = 'q'
IS_POPUP_VAR = 'pop'
ERROR_FLAG = 'e'
STATE_VAR = 's'
EXPORT_VAR = 'f'
PAGE_LIMIT_VAR = 'l'
TMP_VAR = 't'


def enable_mod(mod_name):
	if mod_name=='':
		return True
	l_mod=mod_name.split(';')
	for m in l_mod:
		if m in settings.ENABLED_MOD:
			return True
	return False
	


@login_required
def index(request):
	tmpFile='staff/staff_portal.html'
	sub_menu="%s"%createmenu(request,'staff')
	cc={}
	LANGUAGE_CODE=settings.LANGUAGE_CODE
	if settings.LANGUAGE_CODE=='zh-Hans':
		LANGUAGE_CODE="zh-CN"
	try:
		uid=request.employee['id']
		pin=request.employee['pin']
	except:
		return HttpResponseRedirect('/accounts/login/')
	cc['loginIP']=request.META["REMOTE_ADDR"]
	cc['loginCount']=employeeLog.objects.filter(PIN=pin).count()
	eLog=employeeLog.objects.filter(PIN=pin).order_by('-id')[1:2]
	person_pic_file="%sphoto/%s.jpg"%(settings.ADDITION_FILE_ROOT,pin)
	if os.path.isfile(person_pic_file):
		cc['person_pics']="/iclock/file/photo/%s.jpg" % pin
	else :
		cc['person_pics']="/media/img/transaction/noimg.jpg"
	if eLog:
		for t in eLog:
			cc['loginTime']=t.LTime.strftime('%Y-%m-%d %H:%M:%S')
	else:
		cc['loginTime']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	cc['sub_menu']=sub_menu
	cc['location']=u'个人中心'
	cc['location_url']='/iclock/staff/'
	cc['LANGUAGE_CODE']=LANGUAGE_CODE
	#return TemplateResponse(request,tmpFile,cc)#render_to_response(tmpFile,cc,RequestContext(request, {}))
	return render(request,tmpFile,cc)

#ATTSTATES={
#"I":_("Check in"),
#"O":_("Check out"),
#"8":_("Meal start"),
#"9":_("Meal end"),
#"2":_("Break out"),
#"3":_("Break in"),
#"4":_("Overtime in"),
#"5":_("Overtime out"),
#}


ATTSTATES={
"I":_("Check in"),
"O":_("Check out"),
"i":_("Overtime in"),
"o":_("Overtime out"),
"0":_("Break out"),
"1":_("Break in"),
#"8":_("Meal start"),
#"9":_("Meal end"),
#"2":_("Break out"),
#"3":_("Break in"),
#"4":_("Overtime in"),
#"5":_("Overtime out"),
}


def getStateStr(s):
	for key in ATTSTATES:
		if key in s:
			return ATTSTATES[key]
	return "" 

VERIFYS={
"3": _("Card"),
"0": _("Password"),
"1": _("Fingerprint"),
#"2": _("Card"),
"5": _("Add"),
"9": _("Other"),
}

AUDIT_STATES={
"0":_('Apply'),
"1":_('Auditing'),
"2":_('Accepted'),
"3":_('Refused'),
"4":_('Paused'),
"5":_('Re-Apply'),
"6":_('Again'),
"7":_('Cancel_leave'),
}


def getVERIFYStr(s):
	for key in VERIFYS:
		if key == str(s):
			return VERIFYS[key]
	return "" 

def getAUDIT_STATESStr(s):
	for key in AUDIT_STATES:
		if key == str(s):
			return AUDIT_STATES[key]
	return "" 

@login_required
def staffAnn(request):
	tmpFile='staff/staff_Annual.html'
	cc={}
	uid=request.employee['id']
	cc=getSingleAnnual(request,uid)
	if cc['unit']==1:
		cc['days']=str(cc['days'])+'小时'
		cc['canused']=str(cc['canused'])+'小时'
		cc['Hasused']=str(cc['Hasused'])+'小时'
	else:
		cc['days']=str(cc['days'])+'天'
		cc['canused']=str(cc['canused'])+'天'
		cc['Hasused']=str(cc['Hasused'])+'天'
	cc['location'] = u'我的年假'
	return render(request,tmpFile, cc)
	#return render_to_response(tmpFile, cc,RequestContext(request, {}))

@login_required
def staffTran(request):
	if request.method=='GET':
		tmpFile='staff/staff_records.html'
		cc={}
		cc['ColNames']=dumps([u'考勤号码', u'  姓 名  ',u'时间',u'设备',u'考勤类型',u'更正状态',u'验证方式'])
		#cc['datas']=dumps(datas_list)
		cc['location'] = u'我的记录'
		return render_to_response(tmpFile, cc,RequestContext(request, {}))
	else:
		starttime=request.GET.get('starttime','').split('-')
		endtime=request.GET.get('endtime','').split('-')
		st=datetime.datetime(int(starttime[0]),int(starttime[1]),int(starttime[2]),0,0,0)
		et=datetime.datetime(int(endtime[0]),int(endtime[1]),int(endtime[2]),23,59,59)
		if (et-st).days>100:
			datas_list=[[u'时间范围过长']]
			return getJSResponse(datas_list)
			
		uid=request.employee['id']
		objs=transactions.objects.filter(UserID=uid).filter(TTime__range=(st,et)).order_by('-TTime')
		datas_list=[]
		for t in objs:
			data_list=[]
			data_list.append(t.employee().PIN)
			data_list.append(t.employee().EName or '')
			data_list.append(t.TTime.strftime('%Y-%m-%d %H:%M:%S'))
			if t.SN:
				data_list.append(t.SN.SN or '')
			else:
				data_list.append('')
			data_list.append(getRecordState(t.State))
			data_list.append('')
			data_list.append(t.get_Verify_display())
			datas_list.append(data_list)
		#cc['datas']=dumps(datas_list)
		return getJSResponse(datas_list)
		

@login_required
def staffattshifts(request):
	if enable_mod("att"):
		if request.method=='GET':

			tmpFile='staff/staff_attshifts.html'
			cc={}
			cc['ColNames']=dumps([u'考勤号码', u'姓名  ',u'日期',u'时段',u'上班时间',u'下班时间',u'上班打卡',u'下班打卡',u'迟到',u'早退',u'加班',u'旷工',u'请假'])
			#cc['datas']=dumps(datas_list)
			cc['location'] = u'出勤详情'
			return render_to_response(tmpFile, cc,RequestContext(request, {}))
		else:
			starttime=request.GET.get('starttime','').split('-')
			endtime=request.GET.get('endtime','').split('-')
			st=datetime.datetime(int(starttime[0]),int(starttime[1]),int(starttime[2]),0,0,0)
			et=datetime.datetime(int(endtime[0]),int(endtime[1]),int(endtime[2]),23,59,59)
			if (et-st).days>60:
				datas_list=[[u'时间范围过长']]
				return getJSResponse(datas_list)
			
			weeks=[u'周一',u'周二',u'周三',u'周四',u'周五',u'周六',u'周日']
			uid=request.employee['id']
			objs=attShifts.objects.filter(UserID=uid).filter(AttDate__range=(st,et)).order_by('-AttDate')
			datas_list=[]
			for t in objs:
				data_list=[]
				data_list.append(t.employee().PIN)
				data_list.append(t.employee().EName or '')
				data_list.append(t.AttDate.strftime('%Y-%m-%d')+u' %s'%weeks[t.AttDate.weekday()])
				if t.SchId:
					data_list.append(t.SchId.SchName)
				elif not t.SchId and t.OverTime>0:
					data_list.append(u'加班')
				data_list.append(t.ClockInTime.strftime('%H:%M:%S'))
				data_list.append(t.ClockOutTime.strftime('%H:%M:%S'))
				if t.StartTime:
					data_list.append(t.StartTime.strftime('%H:%M:%S'))
				else:
					data_list.append('')
				if t.EndTime:
					data_list.append(t.EndTime.strftime('%H:%M:%S'))
				else:
					data_list.append('')				
				if t.Late:
					data_list.append(u'是')
				else:
					data_list.append('')					
				if t.Early:
					data_list.append(u'是')
				else:
					data_list.append('')
				if t.OverTime:
					data_list.append(u'是')
				else:
					data_list.append('')					
				if t.Absent:
					data_list.append(u'是')
				else:
					data_list.append('')	
				if t.ExceptionID:
					data_list.append(getLeaveClass(t.ExceptionID))
				else:
					data_list.append('')	
	
				datas_list.append(data_list)

			return getJSResponse(datas_list)



	else:
		return render_to_response("info.html", {"title":  _(u"提示"), "content": _(u"系统此版本不支持 出勤情况 功能！")});

@login_required
def staffabnormite(request):
	if enable_mod("att"):
		if request.method=='GET':
			tmpFile='staff/staff_abnormite.html'
			cc={}
			
			
			
			cc['ColNames']=dumps([u'考勤号码', u'姓名  ',u'时间',u'迟到',u'早退',u'旷工',u'请假'])
			#cc['datas']=dumps(datas_list)
			cc['location'] = u'我的异常'
			return render(request,tmpFile, cc,{})
	
		else:
			starttime=request.GET.get('starttime','').split('-')
			endtime=request.GET.get('endtime','').split('-')
			st=datetime.datetime(int(starttime[0]),int(starttime[1]),int(starttime[2]),0,0,0)
			et=datetime.datetime(int(endtime[0]),int(endtime[1]),int(endtime[2]),23,59,59)
			if (et-st).days>100:
				datas_list=[[u'时间范围过长']]
				return getJSResponse(datas_list)
			uid=request.employee['id']
			objs=attShifts.objects.filter(UserID=uid).filter(AttDate__range=(st,et)).order_by('-AttDate')[:100]
			datas_list=[]
			emp=employee.objByID(uid)
			for t in objs:
				data_list=[]
				data_list.append(emp.PIN)
				data_list.append(emp.EName or '')
				data_list.append(t.AttDate.strftime('%Y-%m-%d %H:%M:%S'))
				if t.Late:data_list.append(t.Late)
				else:data_list.append('')
				if t.Early:data_list.append(t.Early)
				else:data_list.append('')
				if t.Absent:data_list.append(u'是')
				else:data_list.append('')
				if t.ExceptionID:data_list.append(getLeaveClass(t.ExceptionID))
				else:data_list.append('')
				datas_list.append(data_list)
			return getJSResponse(datas_list)


	else:
		return render_to_response("info.html", {"title":  _(u"提示"), "content": _(u"系统此版本不支持 我的异常 功能！")});

@login_required
def staffUSER_OF_RUN(request):
	tmpFile='staff/staff_user_of_run.html'
	if enable_mod("att"):
		if request.method=='GET':
			cc={}
			cc['ColNames']=dumps([u'考勤号码', u'姓名',u'开始日期',u'结束日期',u'时段名称'])
			#cc['datas']=dumps(datas_list)
			cc['location'] = u'我的排班'
			return render(request,tmpFile, cc)
		else:
			starttime=request.GET.get('starttime','').split('-')
			endtime=request.GET.get('endtime','').split('-')
			st=datetime.datetime(int(starttime[0]),int(starttime[1]),int(starttime[2]),0,0,0)
			et=datetime.datetime(int(endtime[0]),int(endtime[1]),int(endtime[2]),23,59,59)
			if (et-st).days>100:
				datas_list=[[u'时间范围过长']]
				return getJSResponse(datas_list)
			uid=request.employee['id']
			AttRule=LoadAttRule()
			day_off_count=0#days_off.objects.filter(Q(FromDate__gte=d1,FromDate__lte=d2)|Q(ToDate__lte=d2,ToDate__gte=d1)).count()
			holidays=loadHoliday()
			initParams={'AttRule':AttRule,'day_off_count':day_off_count,'Holiday':holidays}
			emp=employee.objByID(uid)
	
	
			userplan=LoadSchPlan(emp,True,True)
			d1=trunc(st)
			d2=et
			l=GetUserScheduler(emp, d1, d2, userplan['HasHoliday'],initParams)
			datas_list=[]
			for t in l:
				data_list=[]
				data_list.append(emp.PIN)
				data_list.append(emp.EName or '')
				data_list.append(t['TimeZone']['StartTime'].strftime('%Y-%m-%d %H:%M:%S'))
				data_list.append(t['TimeZone']['EndTime'].strftime('%Y-%m-%d %H:%M:%S'))
				data_list.append(t['SchName'])
				datas_list.append(data_list)
			return getJSResponse(datas_list)
			



	else:
		return render_to_response("info.html", {"title":  _(u"提示"), "content": _(u"系统此版本不支持该功能！")});

@login_required
def staffUSER_SPEDAY(request):
	if request.method=='GET':
		tmpFile='staff/staff_user_speday.html'
		cc={}
		cc['ColNames']=dumps([u'考勤号码', u'  姓 名  ',u'开始时间',u'结束时间',u'假类',u'状态',u'审核流程',u'原因',u'申请时间',u'操作'])
		#cc['datas']=dumps(datas_list)
		cc['location'] = u'我的请假'
		return render(request,tmpFile, cc)
	else:
		starttime=request.GET.get('starttime','').split('-')
		endtime=request.GET.get('endtime','').split('-')
		st=datetime.datetime(int(starttime[0]),int(starttime[1]),int(starttime[2]),0,0,0)
		et=datetime.datetime(int(endtime[0]),int(endtime[1]),int(endtime[2]),23,59,59)
		if (et-st).days>1000:
			datas_list=[[u'时间范围过长']]
			return getJSResponse(datas_list)
		uid=request.employee['id']
		objs=USER_SPEDAY.objects.filter(UserID=uid).filter(Q(StartSpecDay__range=(st,et))|Q(EndSpecDay__range=(st,et))).order_by('-ApplyDate')
		datas_list=[]
		for t in objs:
			data_list=[]
			data_list.append(t.employee().PIN)
			data_list.append(t.employee().EName or '')
			data_list.append(t.StartSpecDay.strftime('%Y-%m-%d %H:%M:%S'))
			data_list.append(t.EndSpecDay.strftime('%Y-%m-%d %H:%M:%S'))
			data_list.append(Leave(t.DateID))
			data_list.append(get_State_State(t.get_State_display()))
			data_list.append(showprocess(t))
			data_list.append(t.YUANYING)
			data_list.append(t.ApplyDate.strftime('%Y-%m-%d %H:%M:%S'))
			data_list.append('<a  title="查看审批详情" onclick="getProcessLog('+str(t.id) +')"style="color:green;">详情</a>&nbsp;')
			datas_list.append(data_list)
		return getJSResponse(datas_list)

@login_required
def staffEmployee(request):
	tmpFile='staff\staff_employee.html'
	cc={}
	#params = dict(request.GET.items())
	uid=request.employee['id']
	k=["PIN","EName","DeptID","Gender","Birthday","National","Title","FPHONE","Mobile","Card","Address","Annualleave","email","MVerifyPass","Tele","SSN","PostCode","Hiredday"]
	em=employee.objByID(uid)#.values()
	cc['emp'] = em
	cc['location'] = u'个人信息'
	return render(request,tmpFile, cc)

@login_required
def staff_basic_save(request):
	uid=request.employee['id']
	upin = request.employee['pin']
	dict = {}
	fieldVariable=["genders","Mobiles","Teles","Address_s","insurances","emails"]
	fieldNames=["gender","Mobile","Tele","Address","insurance","email"]
	try:
		if request.method == 'POST':
			for keys,val in itertools.izip(fieldVariable,fieldNames):
				dict[keys] = request.POST.get(val,'')
			try:
				employee.objects.filter(id=uid).update(Gender=dict["genders"],Mobile=dict["Mobiles"],Tele=dict["Teles"],Address=dict["Address_s"],SSN=dict["insurances"],email=dict["emails"])
				cache.delete("%s_iclock_emp_%s"%(settings.UNIT,uid))
				cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,upin))
			except Exception,ee:
				pass
			return getJSResponse({"ret":0,"message": u"%s"%_('Save Success'),"color":"Green"},mtype="text/plain")
	except Exception,ee:
		print ee

@login_required
def staffpersonalization(request):
	tmpFile='staff/staff_personalization.html'
	cc={}
	uid=request.employee['id']
	#em=stafflogin.objByID(uid)
	try:
		em=stafflogin.objects.get(UserID=uid)
	except:
		em=None
	cc['emp'] = em
	cc['location'] = u'个性化设置'
	return render(request,tmpFile, cc)

@login_required
def staffpersonalization_save(request):
	uid=request.employee['id']
	emp = employee.objByID(uid)
	staff_obj = stafflogin.objects.filter(UserID = uid)
	Method=-1
	dDict={}
	fieldVariable=["LoginMethoda","LoginMethodb","StaffUsernames"]
	fieldNames=["pin_pw","username_pw","StaffUsername"]
	try:
		if request.method == 'GET':
			for keys,val in itertools.izip(fieldVariable,fieldNames):
				dDict[keys] = request.GET.get(val,'')
			login_username = dDict["StaffUsernames"]
			login_pin = dDict["LoginMethoda"]
			login_u = dDict["LoginMethodb"]
			is_only_auth_user = MyUser.objects.filter(username__exact = login_username)
			is_only = stafflogin.objects.filter(StaffUsername__exact = login_username)
			if login_pin and login_u:
				Method = 2
			elif login_pin:
				Method = 0
			elif login_u:
				Method = 1
			if staff_obj:
				if staff_obj[0].StaffUsername == login_username:
					try:
						stafflogin.objects.filter(UserID = uid).update(StaffUsername = login_username,LoginMethod = Method)
					except Exception,ee:
						pass
				else:
					if is_only or is_only_auth_user:
						return getJSResponse({"ret":0,"message": u"%s"%_(u'此用户名已经被使用!请重新命名！'),"color":"red"},mtype="text/plain")
					else:
						try:
							stafflogin.objects.filter(UserID = uid).update(StaffUsername = login_username,LoginMethod = Method)
						except Exception,ee:
							# print ee
							pass
			else:
				if is_only or is_only_auth_user:
					return getJSResponse({"ret":0,"message": u"%s"%_(u'此用户名已经被使用!请重新命名！',),"color":"red"},mtype="text/plain")
				stafflogin(UserID = emp,StaffUsername = login_username,LoginMethod = Method).save()
			return getJSResponse({"ret":0,"message": u"%s"%_('Save Success'),"color":"Green"},mtype="text/plain")
	except Exception,ee:
		print ee
	

@login_required
def apply_speday(request):
	tmpFile = 'staff/staff_apply_speday.html'
	if enable_mod("att"):
		cc={}
		uid=request.employee['id']
		try:
			em=stafflogin.objects.get(UserID=uid)
		except:
			em=None
		LeaveClass_objs = GetLeaveClasses(2)
		Ann=getSingleAnnual(request,uid)
		cc['emp'] = em
		cc['emp_id'] = uid
		if Ann['unit']==1:
			cc['Annual'] = str(Ann['canused'])+'小时'
		else:
			cc['Annual'] = str(Ann['canused'])+'天'
		cc['leaveClass_s'] = dumps(LeaveClass_objs)
		# cc['causes'] = dumps(cause_objs)
		cc['location'] = u'申请请假'
		return render(request,tmpFile, cc)
	else:
		return render_to_response("info.html", {"title":  _(u"提示"), "content": _(u"系统此版本不支持 申请请假 功能！")});


@login_required
def apply_overtime(request):
	tmpFile = 'staff/staff_apply_overtime.html'
	if enable_mod("att"):
		cc={}
		uid=request.employee['id']
		try:
			em=stafflogin.objects.get(UserID=uid)
		except:
			em=None
		cc['emp'] = em
		cc['emp_id'] = uid
		cc['location'] = u'申请加班'
		return render(request,tmpFile, cc)
	else:
		return render_to_response("info.html", {"title":  _(u"提示"), "content": _(u"系统此版本不支持 申请加班 功能！")});

@login_required
def apply_forget(request):
	tmpFile = 'staff/staff_apply_forget.html'
	if enable_mod("att"):
		cc={}
		states={}
		uid=request.employee['id']
		try:
			em=stafflogin.objects.get(UserID=uid)
		except:
			em=None
		ll=GetRecordStatus()
		states={'states':ll}
		cc['emp'] = em
		cc['emp_id'] = uid
		cc['ForgetAtt_list'] = dumps(states)
		cc['location'] = u'申请补记录'
		return render(request,tmpFile, cc)
	else:
		return render_to_response("info.html", {"title":  _(u"提示"), "content": _(u"系统此版本不支持 申请补给录 功能！")});



def staffQueryData(request, dataModel,params):
	opts = dataModel._meta
#   params = dict(request.GET.items())
	if not opts.admin: 
		try:
			opts.admin=dataModel.Admin
		except: pass

	if fieldVerboseName(dataModel, "DelTag"):
		qs=dataModel.objects.filter(Q(DelTag__isnull=True)|Q(DelTag=0))
	else:
		qs=dataModel.objects.all()
	lookup_params = params.copy() # a dictionary of the query string
	for i in (ALL_VAR, ORDER_VAR, ORDER_TYPE_VAR, SEARCH_VAR, IS_POPUP_VAR, PAGE_VAR, STATE_VAR, EXPORT_VAR,PAGE_LIMIT_VAR,TMP_VAR):
		if i in lookup_params:
			del lookup_params[i]
	for key, value in lookup_params.items():
		if not isinstance(key, str):
		# 'key' will be used as a keyword argument later, so Python
		# requires it to be a string.
			del lookup_params[key]
			k=smart_str(key)
			lookup_params[k] = value
		else:
			k=key
		if (k.find("__in")>0) or (k.find("__exact")>0 and value.find(',')>0):
			del lookup_params[key]
			lookup_params[k.replace("__exact","__in")]=value.split(",")
		if key=='fromTime':
			lookup_params["TTime__gt"]=value
			del lookup_params[key]
		if key=='toTime':
			lookup_params["TTime__lt"]=value
			del lookup_params[key]
	# Apply lookup parameters from the query string.
	if lookup_params:
		qs = qs.filter(**lookup_params)
			
	cl=ChangeList(request, dataModel)
	if cl.orderStr:
		ot=cl.orderStr.split(",")
		qs=qs.order_by(*ot)
	return qs, cl


urlpatterns = [
	url(r'^$', index),				#个人中心主页
	url(r'employee/', staffEmployee),		#个人信息
	url(r'staff_basic_save/', staff_basic_save),		#个人信息
	url(r'personalization/', staffpersonalization),		#个性化设置
	url(r'save_staff_username/', staffpersonalization_save),	#个性化设置保存
	url(r'Annual/', staffAnn),		#我的年假
	url(r'transactions/', staffTran),		#我的记录
	url(r'USER_SPEDAY/', staffUSER_SPEDAY),	#我的请假
	url(r'USER_OF_RUN/', staffUSER_OF_RUN),	#我的排班
	url(r'attshifts/', staffattshifts),	#出勤情况
	url(r'abnormite/', staffabnormite),	#我的异常
	url(r'apply_speday/', apply_speday),	#申请请假
	url(r'apply_overtime/', apply_overtime),	#申请加班
	url(r'apply_forget/', apply_forget),	#申请补记录
]
