#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.core.tools import *
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from exceptions import AttributeError
import string,os
import datetime
import time
from mysite.utils import *
from django.contrib.auth.decorators import login_required,permission_required
from mysite.iclock.dataproc import *
from django.utils.encoding import force_unicode, smart_str
from mysite.iclock.iutils import *
from mysite.iclock.reb	import *
from django.conf import settings
from mysite.cab import *
from mysite.iclock.devview import checkDevice, getEmpCmdStr
from mysite.iclock.datv import *
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.datautils import *
from mysite.iclock.admin_detail_view import *
from mysite.iclock.datas import *
from mysite.iclock.schedule import *
from mysite.iclock.datasproc import *
from mysite.iclock.jqgrid import *

from pyExcelerator import *
from mysite.iclock.nomodelview import *
from mysite.iclock.newiaccess import *

from mysite.iclock.export import *
from mysite.ipos.reportsview import *



def getMeallist(header,field):
	mealobj = Meal.objects.filter(available=1).exclude(DelTag=1)
	j=0
	for t in mealobj:
		header.insert(6+j,t.name)
		field.insert(6+j,'meal_%s'%t.id)
		j+=1
	return header,field

@login_required
def exportList(request, ModelName):
	n=datetime.datetime.now()
	exporttblname=request.GET.get('exporttblName')
	exporttype=request.GET.get('exporttype','0')
	parameter =2
	user_id=request.user.id

	if ModelName=='Supplement':
		#st=request.GET.get('startDate','')
		#et=request.GET.get('endDate','')
		#st=datetime.datetime.strptime(st,'%Y-%m-%d')
		#et=datetime.datetime.strptime(et,'%Y-%m-%d')
		header=[_(u'工号'),_(u'姓名'),_(u'部门'),_(u'卡号'),_(u'卡账号'),_(u'卡流水号'),_(u'充值金额'),_(u'充值类型'),_(u'卡余额'),_(u'充值时间'),_(u'上传时间'),_(u'操作员'),_(u'设备流水号'),_(u'设备序列号'),_(u'记录类型')]
		field=['user_pin','user_name', 'DeptName', 'card', 'sys_card_no','card_serial_num','money','hide_column','blance','checktime','convey_time','create_operator','serialnum','sn','log_flag']
		disacols=FetchDisabledFields(request.user,'Supplement')
		tables=u'%s'%_(u'充值报表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcSupplement(request)
	elif ModelName=='Refund':
		#st=request.GET.get('startDate','')
		#et=request.GET.get('endDate','')
		#st=datetime.datetime.strptime(st,'%Y-%m-%d')
		#et=datetime.datetime.strptime(et,'%Y-%m-%d')
		header=[_(u'工号'),_(u'姓名'),_(u'部门'),_(u'卡号'),_(u'卡账号'),_(u'卡流水号'),_(u'退款金额'),_(u'卡余额'),_(u'退款时间'),_(u'上传时间'),_(u'操作员'),_(u'设备流水号'),_(u'设备序列号'),_(u'记录类型')]
		field=['user_pin','user_name', 'DeptName', 'card', 'sys_card_no','card_serial_num','money','blance','checktime','convey_time','create_operator','serialnum','sn','log_flag']
		disacols=FetchDisabledFields(request.user,'Refund')
		tables=u'%s'%_(u'退款报表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcRefund(request)
	elif ModelName=='Backcard':
		#st=request.GET.get('startDate','')
		#et=request.GET.get('endDate','')
		#st=datetime.datetime.strptime(st,'%Y-%m-%d')
		#et=datetime.datetime.strptime(et,'%Y-%m-%d')
		header=[_(u'工号'),_(u'姓名'),_(u'部门'),_(u'卡号'),_(u'卡账号'),_(u'卡流水号'),_(u'支出卡成本'),_(u'退款金额'),_(u'退卡时间'),_(u'操作员')]
		field=['user_pin','user_name', 'DeptName', 'cardno', 'sys_card_no','card_serial_num','card_money','back_money','checktime','create_operator']
		disacols=FetchDisabledFields(request.user,'Backcard')
		tables=u'%s'%_(u'退卡报表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcBackcard(request)
	elif ModelName=='Cardcost':
		#st=request.GET.get('startDate','')
		#et=request.GET.get('endDate','')
		#st=datetime.datetime.strptime(st,'%Y-%m-%d')
		#et=datetime.datetime.strptime(et,'%Y-%m-%d')
		header=[_(u'工号'),_(u'姓名'),_(u'部门'),_(u'卡号'),_(u'卡账号'),_(u'成本金额'),_(u'操作时间'),_(u'操作员')]
		field=['user_pin','user_name', 'DeptName', 'card', 'sys_card_no','money','checktime','create_operator']
		disacols=FetchDisabledFields(request.user,'Cardcost')
		tables=u'%s'%_(u'卡成本报表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcCardcost(request)
	elif ModelName=='CardBlance':
		#st=request.GET.get('startDate','')
		#et=request.GET.get('endDate','')
		#st=datetime.datetime.strptime(st,'%Y-%m-%d')
		#et=datetime.datetime.strptime(et,'%Y-%m-%d')
		header=[_(u'工号'),_(u'姓名'),_(u'部门'),_(u'卡号'),_(u'卡账号'),_(u'卡类名称'),_(u'卡余额'),_(u'操作员')]
		field=['user_pin','user_name', 'DeptName', 'card', 'sys_card_no','itype','blance','create_operator']
		disacols=FetchDisabledFields(request.user,'CardBlance')
		tables=u'%s'%_(u'卡余额报表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcCardBlance(request)
	elif ModelName=='EmpSumPos':
		header=[_(u'工号'),_(u'姓名'),_(u'部门'),_(u'消费次数'),_(u'手工补单'),_(u'消费合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次次数'),_(u'结算次数'),_(u'结算金额'),_(u'结算金额（含补单）'),_(u'消费日期')]
		field=['pin','name', 'dept_name', 'pos_count', 'add_single_money','meal_money','back_count','back_money','summary_total_time','summary_count','summary_dev_money','summary_money','pos_date']
		header,field=getMeallist(header,field)
		disacols=FetchDisabledFields(request.user,'EmpSumPos')
		tables=u'%s'%_(u'个人消费汇总表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcEmpSumPos(request)
	elif ModelName=='DeptSumPos':
		header=[_(u'部门'),_(u'消费次数'),_(u'消费合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次次数'),_(u'结算次数'),_(u'结算金额'),_(u'消费日期')]
		field=['dept_name', 'pos_count', 'meal_money','back_count','back_money','summary_total_time','summary_count','summary_money','pos_date']
		header,field=getMeallist(header,field)
		disacols=FetchDisabledFields(request.user,'DeptSumPos')
		tables=u'%s'%_(u'部门消费汇总表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcDeptSumPos(request)
	elif ModelName=='DiningSumPos':
		header=[_(u'餐厅'),_(u'消费次数'),_(u'消费合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次次数'),_(u'手工补单'),_(u'结算次数'),_(u'结算金额'),_(u'结算金额（含补单）'),_(u'消费日期')]
		field=['dining_name', 'pos_count','meal_money','back_count','back_money','summary_total_time', 'add_single_money','summary_count','summary_dev_money','summary_money','pos_date']
		header,field=getMeallist(header,field)
		disacols=FetchDisabledFields(request.user,'DiningSumPos')
		tables=u'%s'%_(u'餐厅消费汇总表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcDiningSumPos(request)
	elif ModelName=='DeviceSumPos':
		header=[_(u'设备'),_(u'设备序列号'),_(u'消费次数'),_(u'消费合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次次数'),_(u'手工补单'),_(u'结算次数'),_(u'结算金额'),_(u'结算金额（含补单）'),_(u'消费日期')]
		field=['device_name', 'device_sn', 'pos_count','meal_money','back_count','back_money','summary_total_time', 'add_single_money','summary_count','summary_dev_money','summary_money','pos_date']
		header,field=getMeallist(header,field)
		disacols=FetchDisabledFields(request.user,'DeviceSumPos')
		tables=u'%s'%_(u'设备消费汇总表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcDeviceSumPos(request)
	elif ModelName=='MealSumPos':
		header=[_(u'餐别名称'),_(u'消费次数'),_(u'消费合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次次数'),_(u'手工补单'),_(u'结算次数'),_(u'结算金额'),_(u'结算金额（含补单）'),_(u'消费日期')]
		field=['dining_name', 'pos_count','meal_money','back_count','back_money','summary_total_time', 'add_single_money','summary_count','summary_dev_money','summary_money','pos_date']
		disacols=FetchDisabledFields(request.user,'MealSumPos')
		tables=u'%s'%_(u'餐别消费汇总表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcMealSumPos(request)
	elif ModelName=='SzSumPos':
		header=[_(u'统计对象'),_(u'充值次数'),_(u'退款次数'),_(u'发卡次数'),_(u'退卡次数'),_(u'无卡退卡'),_(u'有卡退卡'),_(u'清零金额'),_(u'补贴金额'),_(u'充值合计'),_(u'退款合计'),_(u'卡成本合计'),_(u'管理费合计'),_(u'退卡成本合计'),_(u'收支合计'),_(u'汇总时间')]
		field=['operate', 'recharge_count','refund_count','hairpin_count','back_card_count','no_card_back','card_back','clear_card','allow_card','recharge_money', 'refund_money','cost_money','manage_money','back_card_money','sz_money','summary_date']
		disacols=FetchDisabledFields(request.user,'SzSumPos')
		tables=u'%s'%_(u'收支汇总表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcSzSumPos(request)
	elif ModelName=='NoCardBack':
		header=[_(u'工号'),_(u'姓名'),_(u'部门'),_(u'卡号'),_(u'卡账号'),_(u'卡类名称'),_(u'退卡时间'),_(u'退卡金额'),_(u'卡余额')]
		field=['user_pin', 'user_name','DeptName','card','sys_card_no','itype', 'checktime','money','blance']
		disacols=FetchDisabledFields(request.user,'NoCardBack')
		tables=u'%s'%_(u'无卡退卡表')
		exportname='ipos_%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcNoCardBack(request)
	else:
		appName=request.path.split('/')[1]
		try:
			dataModel=GetModel(ModelName,appName)
		except:
			dataModel=None
		if not dataModel:
			mode=[
			{'name':'id','hidden':True},
			{'name':'user_pin','width':80,'label':unicode(_(u'工号'))},
			{'name':'user_name','width':80,'label':unicode(_(u'姓名'))},
			{'name':'DeptName','width':80,'label':unicode(_('department name'))},
			{'name':'card','width':80,'label':unicode(_(u"卡号"))},
			{'name':'money','width':80,'label':unicode(_(u"消费金额"))},
			{'name':'blance','width':80,'label':unicode(_(u"余额"))},
			{'name':'pos_model','width':90,'label':unicode(_(u'消费模式'))},
			{'name':'dining','width':80,'label':unicode(_(u"餐厅"))},
			{'name':'meal','width':80,'label':unicode(_(u"餐别"))},
			{'name':'dev_sn','width':120,'label':unicode(_(u"设备序列号"))},
			{'name':'checktime','width':120,'label':unicode(_(u"消费时间"))},
			]
		else:
			mode=dataModel.colModels()
		if ModelName=='Allowance':
			mode.insert(8,{'name':'clear_money','sortable':False,'width':80,'label':unicode(_(u"清零金额"))})
		header=[]
		field=[]
		for m in mode:
			if 'label' in m.keys():
				if m['name']!='photo'and m['name']!='thumbnailUrl':
					header.append(m['label'])
					field.append(m['name'])
		if dataModel:
			tables=u'%s'%dataModel._meta.verbose_name.capitalize()
			exportname="%s%s"%(dataModel._meta.db_table,n.strftime('%Y%m%d%H%M%S'))
			datas=DataList1(request, ModelName)
		else:
			tables=u'ID卡消费明细'
			exportname=u"ID卡消费明细%s"%(n.strftime('%Y%m%d%H%M%S'))
			userIDs=request.GET.get('UserIDs',"")
			q=request.GET.get('q','')
			q=unquote(q)
			datas=getIDPosListReport(request,userIDs,q)
			datas=datas['datas']
		disacols=FetchDisabledFields(request.user,exporttblname)
	adminLog(time = datetime.datetime.now(), User = request.user, action = u'%s' % _(u"Export") + u'%s' % _(u"Reports"),
			 model = tables[:40],object = request.META["REMOTE_ADDR"]).save(force_insert = True)
	if exporttype=='0':
		response = HttpResponse()
		response['mimetype'] ='application/ms-excel'
		response['Content-Disposition'] = 'attachment; filename=%s-%s.xls'%(exportname,user_id)
		wb = Workbook()
		ws = wb.add_sheet(u'%s'%tables)
		if ModelName=="USER_SPEDAY" or ModelName=="User_OverTime":
			filltable1(header, datas, ws, field,disacols,tables)
		else:
			filltable(header, datas, ws, field,disacols,tables)
		name=u"%sreports/%s.xls"%(settings.ADDITION_FILE_ROOT,exportname)
		url=u"/iclock/file/reports/%s.xls"%exportname
		wb.save(name)
	elif exporttype=='1':
		response = HttpResponse()
		response['mimetype'] ='application/octet-stream'
		response['Content-Disposition'] = 'attachment; filename="%s-%s.txt"'%(exportname,user_id)
		#fn=u"%sreports/%s.txt"%(settings.ADDITION_FILE_ROOT,exportname)
		#url=u"/iclock/file/reports/%s.txt"%exportname
		#f=file(fn, "a+" or "w+")
		filetxtcontents(header, datas, field,disacols,tables,response)
		return response
	else:
		if ModelName=="iclock":
			parameter=2.5
		fn=u"%sreports/%s.pdf"%(settings.ADDITION_FILE_ROOT,exportname)
		url=u"/iclock/file/reports/%s.pdf"%exportname
		p=printTable()
		response=p.printReports(request,tables,header,field,datas,disacols,fn,parameter)
		
	#adminLog(time=datetime.datetime.now(),User=request.user, action=u"Export "+ModelName+u" files",model=ModelName).save()
	return HttpResponse(url)#response#return HttpResponse(url)



@login_required
def calcSupplement(request):
	from mysite.ipos.reportsview import getSupplement
	#deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	#st=request.GET.get('startDate','')
	#et=request.GET.get('endDate','')
	#st=datetime.datetime.strptime(st,'%Y-%m-%d')
	#et=datetime.datetime.strptime(et,'%Y-%m-%d')
	r=getSupplement(request,userIDs,'')
	return r['datas']

@login_required
def calcRefund(request):
	from mysite.ipos.reportsview import getRefund
	#deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	#st=request.GET.get('startDate','')
	#et=request.GET.get('endDate','')
	#st=datetime.datetime.strptime(st,'%Y-%m-%d')
	#et=datetime.datetime.strptime(et,'%Y-%m-%d')
	r=getRefund(request,userIDs,'')
	return r['datas']

@login_required
def calcBackcard(request):
	from mysite.ipos.reportsview import getRetreatCard
	#from mysite.ipos.reportsview import getBackcard
	#deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	#st=request.GET.get('startDate','')
	#et=request.GET.get('endDate','')
	#st=datetime.datetime.strptime(st,'%Y-%m-%d')
	#et=datetime.datetime.strptime(et,'%Y-%m-%d')
	#r=getBackcard(request,userIDs,'')
	r = getRetreatCard(request, userIDs, '')
	return r['datas']
@login_required
def calcCardcost(request):
	from mysite.ipos.reportsview import getCardcost
	#deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	#st=request.GET.get('startDate','')
	#et=request.GET.get('endDate','')
	#st=datetime.datetime.strptime(st,'%Y-%m-%d')
	#et=datetime.datetime.strptime(et,'%Y-%m-%d')
	r=getCardcost(request,userIDs,'')
	return r['datas']
@login_required
def calcCardBlance(request):
	from mysite.ipos.reportsview import getCardBlance
	#deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	#st=request.GET.get('startDate','')
	#et=request.GET.get('endDate','')
	#st=datetime.datetime.strptime(st,'%Y-%m-%d')
	#et=datetime.datetime.strptime(et,'%Y-%m-%d')
	r=getCardBlance(request,userIDs,'')
	return r['datas']
@login_required
def calcEmpSumPos(request):
	userIDs=request.GET.get('UserIDs',"")
	r=getEmpSumPos_Ex(request,userIDs,'')
	return r['datas']

@login_required
def calcDeptSumPos(request):
	r=getDept_Ding_Device_SumPos_Ex(request,'dept')
	return r['datas']

@login_required
def calcDiningSumPos(request):
	r=getDept_Ding_Device_SumPos_Ex(request,'Dininghall')
	return r['datas']

@login_required
def calcDeviceSumPos(request):
	r=getDept_Ding_Device_SumPos_Ex(request,'Device')
	return r['datas']

@login_required
def calcMealSumPos(request):
	r=getDept_Ding_Device_SumPos(request,'Meal')
	return r['datas']

@login_required
def calcSzSumPos(request):
	r=SZ_sum_report(request)
	return r['datas']

@login_required
def calcNoCardBack(request):
	from mysite.ipos.reportsview import getNoCardBack
	userIDs=request.GET.get('UserIDs',"")
	q=request.GET.get('q','')
	q=unquote(q)
	r=getNoCardBack(request,userIDs,q)
	return r['datas']




