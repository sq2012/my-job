#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.core.tools import *
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
import datetime
from mysite.utils import *
from django.contrib.auth.decorators import permission_required, login_required
from mysite.iclock.iutils import *
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
from django.utils.encoding import smart_unicode, iri_to_uri
from mysite.iclock.datautils import *

@login_required
def getColModel(request):
	"""用于各种特殊情况获取Grid列标题"""
	datamodel=request.GET.get('dataModel','')
	appName='iclock'
	if datamodel in ['participants_details','Meet_details','meet_devices']:
		appName='meeting'
	elif datamodel in ['level_emp','FirstOpen_emp','level','searchs']:
		appName='acc'
	HeaderModels=[]
	if datamodel:
		if datamodel == 'employee':
			colmodels= [
				{'name':'id','hidden':True},
				{'name':'PIN','index':'PIN','width':120,'label':unicode(employee._meta.get_field('PIN').verbose_name),'frozen':True},
				{'name':'Workcode', 'width':100, 'label':unicode(employee._meta.get_field('Workcode').verbose_name),'frozen':True},
				{'name':'EName','width':60,'label':unicode(employee._meta.get_field('EName').verbose_name),'frozen': True},
				#{'name':'Card','width':60,'search':False,'label':unicode(employee._meta.get_field('Card').verbose_name)},
				{'name':'Privilege','width':90,'search':False,'label':unicode(employee._meta.get_field('Privilege').verbose_name)},
				{'name':'Gender','width':40,'search':False,'label':unicode(employee._meta.get_field('Gender').verbose_name)},
				{'name':'DeptName','index':'DeptID__DeptName','width':100,'label':unicode(_('department name'))},
				{'name':'Title','width':40,'label':unicode(employee._meta.get_field('Title').verbose_name)},
				{'name':'fingers','sortable':False,'width':40,'label':unicode(u'指纹')},
				{'name':'faces','sortable':False,'width':40,'label':unicode(u'面部')},
			]
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))
		elif datamodel == 'employeeForIssueCard':
			colmodels= [
				{'name':'id','hidden':True},
				{'name':'PIN','index':'PIN','sortable':True,'width':100,'label':unicode(employee._meta.get_field('PIN').verbose_name),'frozen':True},
				{'name':'EName','width':60,'sortable':False,'label':unicode(employee._meta.get_field('EName').verbose_name)},
				{'name':'Card','width':100,'sortable':False,'search':False,'label':unicode(employee._meta.get_field('Card').verbose_name)},
				{'name':'DeptName','index':'DeptID__DeptName','width':100,'label':unicode(_('department name'))},
				{'name':'Gender','index':'','sortable':False,'width':40,'label':unicode(employee._meta.get_field('Gender').verbose_name)},
			]
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))
		elif datamodel == 'employeeForReissueCard':
			colmodels= [
				{'name':'id','hidden':True},
				{'name':'PIN','index':'PIN','sortable':True,'width':80,'label':unicode(employee._meta.get_field('PIN').verbose_name),'frozen':True},
				{'name':'EName','width':60,'sortable':False,'label':unicode(employee._meta.get_field('EName').verbose_name)},
				{'name':'cardno','width':60,'sortable':False,'search':False,'label':unicode(employee._meta.get_field('Card').verbose_name)},
				{'name':'sys_card_no','width':50,'sortable':False,'search':False,'label':unicode(IssueCard._meta.get_field('sys_card_no').verbose_name)},
				{'name':'DeptName','index':'DeptID__DeptName','width':80,'label':unicode(_('department name'))},
				{'name':'blance','width':80,'label':unicode(IssueCard._meta.get_field('blance').verbose_name)},
			]
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))
		elif datamodel=='devices':
			colmodels=[{'name':'id','hidden':True},
			{'name':'SN','width':125,'label':unicode(iclock._meta.get_field('SN').verbose_name),'frozen':True},
			{'name':'Alias','width':120,'label':unicode(iclock._meta.get_field('Alias').verbose_name)},
			{'name':'IPAddress','width':100,'label':unicode(iclock._meta.get_field('IPAddress').verbose_name)},
			{'name':'State','index':'State','sortable':False,'width':80,'label':unicode(iclock._meta.get_field('State').verbose_name)},
			{'name':'LastActivity','width':120,'label':unicode(iclock._meta.get_field('LastActivity').verbose_name)},
			{'name':'LogStamp','width':120,'label':unicode(iclock._meta.get_field('LogStamp').verbose_name)},
			{'name':'FWVersion','width':120,'label':unicode(iclock._meta.get_field('FWVersion').verbose_name)},
			{'name':'DeviceName','width':120,'label':unicode(iclock._meta.get_field('DeviceName').verbose_name)},
			{'name':'UserCount','width':50,'sortable':False,'label':unicode(iclock._meta.get_field('UserCount').verbose_name)},
			{'name':'FPCount','width':50,'sortable':False,'label':unicode(iclock._meta.get_field('FPCount').verbose_name)},
# 			{'name':'DeptIDs','sortable':False,'width':120,'label':unicode(u'部门')},
			{'name':'DeptIDS','sortable':False,'width':150,'label':unicode(_(u'归属部门')),'mod':'adms;att;meeting;patrol'},
			{'name':'AlgVer','sortable':False,'hidden':True,'width':80,'label':unicode(u'指纹算法')},
			{'name':'Memo','sortable':False,'width':500,'label':unicode(u'备注')}
			]	
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))
		elif datamodel=='level':
			colmodels=[
			{'name':'id','hidden':True},
			{'name':'name','width':200,'label':unicode(_(u'权限组名称'))},
			{'name':'TimeZone','sortable':False,'width':300,'label':unicode(_(u'时间段'))},
			{'name':'doors','sortable':False,'align':'center','width':100,'label':unicode(_(u'控制门数'))},
			{'name':'emps','sortable':False,'align':'center','width':100,'label':unicode(_(u'相关人员数'))}
			]
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))

		elif datamodel=='zone':
			colmodels=[
			{'name':'id','hidden':True},
			{'name':'code','width':80,'label':unicode(zone._meta.get_field('code').verbose_name)},
			{'name':'name','width':200,'label':unicode(zone._meta.get_field('name').verbose_name)},
			{'name':'remark','width':240,'label':unicode(zone._meta.get_field('remark').verbose_name)},
			{'name':'parent','width':200,'label':unicode(zone._meta.get_field('parent').verbose_name)}
			]
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))
		elif datamodel=='Dininghall':
			colmodels=[
			{'name':'id','hidden':True},
			{'name':'code','width':80,'label':unicode(Dininghall._meta.get_field('code').verbose_name)},
			{'name':'name','width':200,'label':unicode(Dininghall._meta.get_field('name').verbose_name)},
			{'name':'remark','width':240,'label':unicode(Dininghall._meta.get_field('remark').verbose_name)}
			]
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))
		elif datamodel=='records':
			colmodels=[
			{'name':'id','hidden':True},
			{'name':'TTime','width':120,'search':False,'label':unicode(records._meta.get_field('TTime').verbose_name)},
			{'name':'Device','sortable':False,'index':'SN','width':180,'label':unicode(_('Device name'))},
			{'name':'event_point','index':'','sortable':False,'width':120,'label':unicode(_(u'事件点'))},
			{'name':'event_no','width':80,'search':False,'label':unicode(records._meta.get_field('event_no').verbose_name)},
			{'name':'card_no','index':'','sortable':False,'width':120,'label':unicode(_(u'卡号'))},
			{'name':'pin','sortable':False,'width':120,'label':unicode(_(u'人员'))},
			{'name':'inorout','sortable':False,'width':80,'label':unicode(_(u'出入状态'))},
			{'name':'verify','width':80,'sortable':False,'search':False,'label':unicode(records._meta.get_field('verify').verbose_name)}
			]
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))

		elif datamodel=='ICConsumerList':
			colmodels=[
			{'name':'id','hidden':True},
			{'name':'user_pin','width':80,'label':unicode(ICConsumerList._meta.get_field('user_pin').verbose_name)},
			{'name':'user_name','width':60,'label':unicode(ICConsumerList._meta.get_field('user_name').verbose_name)},
			{'name':'dept','width':60,'label':unicode(_('department name'))},
			{'name':'card','width':80,'label':unicode(ICConsumerList._meta.get_field('card').verbose_name)},
			{'name':'sys_card_no','width':50,'label':unicode(ICConsumerList._meta.get_field('sys_card_no').verbose_name)},
			{'name':'type_name','width':60,'label':unicode(ICConsumerList._meta.get_field('type_name').verbose_name)},
			{'name':'money','width':90,'label':unicode(ICConsumerList._meta.get_field('money').verbose_name)},
			{'name':'balance','width':60,'label':unicode(ICConsumerList._meta.get_field('balance').verbose_name)},
			{'name':'pos_model','width':60,'label':unicode(ICConsumerList._meta.get_field('pos_model').verbose_name)},
			{'name':'dining','width':60,'label':unicode(ICConsumerList._meta.get_field('dining').verbose_name)},
			{'name':'meal','width':50,'label':unicode(ICConsumerList._meta.get_field('meal').verbose_name)},
			{'name':'dev_sn','width':100,'label':unicode(ICConsumerList._meta.get_field('dev_sn').verbose_name)},
			{'name':'dev_serial_num','width':70,'label':unicode(ICConsumerList._meta.get_field('dev_serial_num').verbose_name)},
			{'name':'card_serial_num','width':60,'label':unicode(ICConsumerList._meta.get_field('card_serial_num').verbose_name)},
			{'name':'pos_time','width':120,'label':unicode(ICConsumerList._meta.get_field('pos_time').verbose_name)},
			{'name':'convey_time','width':120,'label':unicode(ICConsumerList._meta.get_field('convey_time').verbose_name)},
			{'name':'log_flag','width':60,'label':unicode(ICConsumerList._meta.get_field('log_flag').verbose_name)},
			{'name':'create_operator','width':60,'label':unicode(ICConsumerList._meta.get_field('create_operator').verbose_name)}
			]
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))
		elif datamodel=='transactions':
			colmodels=[
			{'name':'id','hidden':True},
			{'name':'DeptID','width':80,'index':'UserID__DeptID','label':unicode(_('department number'))},
			{'name':'DeptName','width':180,'index':'UserID__DeptID__DeptName','label':unicode(_('department name'))},
			{'name':'PIN','index':'UserID__PIN','width':120,'label':unicode(_('PIN'))},
			{'name':'EName','index':'UserID__EName','width':80,'label':unicode(_('EName'))},
			{'name':'TTime','width':120,'search':False,'label':unicode(transactions._meta.get_field('TTime').verbose_name)},
			{'name':'State','width':80,'search':False,'label':unicode(transactions._meta.get_field('State').verbose_name)},
			{'name':'Device','index':'SN','width':180,'label':unicode(_('Device name'))},
			]
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))
		elif datamodel=='NUM_RUN':
			colmodels=[
			{'name':'Num_runID','sortable':False,'hidden':True},
			{'name':'Name','width':140,'sortable':False,'label':unicode(NUM_RUN._meta.get_field('Name').verbose_name)},
			{'name':'StartDate','width':120,'sortable':False,'label':unicode(NUM_RUN._meta.get_field('StartDate').verbose_name)},
			{'name':'EndDate','width':120,'sortable':False,'label':unicode(NUM_RUN._meta.get_field('EndDate').verbose_name)},
			{'name':'Cycle','width':80,'sortable':False,'label':unicode(NUM_RUN._meta.get_field('Cycle').verbose_name)},
			{'name':'Units','width':80,'sortable':False,'label':unicode(NUM_RUN._meta.get_field('Units').verbose_name)},
			{'name':'Num_RunOfDept','sortable':False,'width':120,'label':unicode(SchClass._meta.get_field('TimeZoneOfDept').verbose_name)}
			]
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))
		else:
			dataModel=GetModel(datamodel,appName)
			colmodels=dataModel.colModels()
			cc={'colModel':colmodels,'groupHeaders':HeaderModels}
			return getJSResponse(dumps(cc))


