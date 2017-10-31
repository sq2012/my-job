#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.core.tools import *
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response
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
#from django.contrib.auth.models import User, Permission
from mysite.iclock.iutils import *
from mysite.iclock.reb	import *
from django.conf import settings
from mysite.cab import *
from mysite.iclock.devview import checkDevice, getEmpCmdStr
from mysite.iclock.datv import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group,Permission
from mysite.iclock.datautils import *
from mysite.iclock.admin_detail_view import *
import operator
from mysite.iclock.datas import *
from mysite.iclock.schedule import *
from mysite.iclock.templatetags.iclock_tags import onlyTime
from mysite.iclock.datasproc import *
from django.db import models, connection
from mysite.iclock.jqgrid import *
#from django.template import add_to_builtins
from pyExcelerator import *
from mysite.iclock.nomodelview import *
from mysite.iclock.newiaccess import *

from reportlab.lib.styles import PropertySet, getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics, cidfonts
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch,cm
from reportlab.rl_config import defaultPageSize
from reportlab.platypus import *
from mysite.iclock.reportsview import *
from mysite.iclock.shiftsview import getComposite
from mysite.base.models import *

(PAGE_WIDTH, PAGE_HEIGHT) = defaultPageSize

_W,_H=(21*cm,29.7*cm)
A4=(_W,_H)
A4_H=(_H,_W) 
class printTable(object):
	def __init__(self):
		self.GRID_STYLE1 = TableStyle(
			[('GRID', (0,0), (-1,-1), 0.25, colors.black),
			 ('ALIGN', (0,0), (-1,-1), 'CENTER'),
			('FONTNAME',(0,0),(-1,-1),'STSong-Light'),
			('FONTSIZE',(0,0),(-1,-1),8),
			]
			)
		
		self.styleSheet = getSampleStyleSheet()
		self.styNormal = self.styleSheet['Normal']
		self.styNormal.spaceBefore = 6
		self.styNormal.spaceAfter = 6
		font = cidfonts.UnicodeCIDFont('STSong-Light')
		pdfmetrics.registerFont(font)
			
		self.ps_report_center = ParagraphStyle(name='normal',
									fontName='STSong-Light',
									fontSize=14,
									leading=15,
									spaceAfter=10,
									alignment=TA_CENTER,
									)
	def myFirstPageReport(self,canvas, doc):#页眉，页脚的设置（第一页）
		canvas.saveState()
		canvas.setLineWidth(.3)
		canvas.line(0,40,10000,40)
		canvas.setFont('STSong-Light',7)
		dd=datetime.datetime.today()
		aa=datetime.datetime.strftime(dd,'%Y-%m-%d %H:%M:%S')
		zhong=self.AP[0]/2
		first=zhong-200
		second=zhong-70
		third=zhong+60
		fourth=zhong+200
		
		if self.tableName in ['dailycalcReport',]:
			footer=zhong-900
			canvas.drawString(footer, 0.45 * inch,u"%s    %s"%(_(u"符号:"),GetCalcSymbol()))
		if self.tableName in ['calcReport','department_report']:
			footer=zhong-480
			canvas.drawString(footer, 0.45 * inch,u"%s    %s"%(_(u"单位:"),GetCalcUnit()))
		canvas.drawString(first, 0.25 * inch,u"%s    %s"%(_(u"制表人:"),self.user))
		canvas.drawString(second, 0.25 * inch,u"%s    %s"%(_(u"制表时间:"),aa))
		canvas.drawString(third, 0.25 * inch,u"%s    %s"%(_(u"页码:"),doc.page))
		canvas.drawString(fourth, 0.25 * inch,u"%s    %s%s"%(_(u"每页:"),self.pagelist,_(u"条")))
		canvas.restoreState()
		
	def printReports(self,request,tables,header,field,datas,disacols,exportname,parameter):
		user_id=request.user.id
		pagelist=24
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="%s-%s.pdf"'%(exportname,user_id)
		self.user=request.user.username
		lx=[]
		title=[]
		for h in range(len(header)):
			if field[h] not in disacols:
				header_=u'%s'%header[h]
				title.append(header_)
		lx.append(title)
		lens=0
		lst = []
		lst.append(Paragraph("""%s"""%(tables),  self.ps_report_center))
		try:
			data_=eval(datas)
		except:
			data_=datas
		for d in data_:
			linewidth=0
			if lens%pagelist==0 and lens!=0:
				t1 = Table(lx)
				t1.setStyle(self.GRID_STYLE1)
				lst.append(t1)
				lst.append(Spacer(5,5))
				lst.append(PageBreak())
				lst.append(Paragraph("""%s"""%(tables),  self.ps_report_center))
				lx=[]
				lx.append(title)
			ll=[]
			for f in field:
				if f not in disacols:
					if f in d.keys():
						if type(d[f])==type(""):
							if d[f].find("src='/media/img/icon-yes.gif'")!=-1:
								d[f]=u'%s'%_("Yes")
							if d[f].find("src='/media/img/icon-no.gif'")!=-1:
								d[f]=u'%s'%_("No")
						if type(d[f])==type(">") and ">" in d[f]:
							d[f]=getvaluefromhtml(d[f])
						ll.append(d[f])
					else:
						ll.append("")
			lx.append(ll)
			lens+=1
		if len(header)>0:
			t1 = Table(lx)
			t1.setStyle(self.GRID_STYLE1)
			lst.append(t1)
			lst.append(Spacer(5,5))
			lst.append(PageBreak())
		self.tableName=exportname
		self.lst=lst
		width=parameter*len(header)*cm
		if width<29.7*cm:
			width=29.7*cm
		height=21*cm
		A_p=(width,height)
		self.AP=A_p
		self.pagelist=pagelist
		c = SimpleDocTemplate(self.tableName,pagesize=A_p,bottomMargin=30,topMargin=30).build(self.lst,  onFirstPage=self.myFirstPageReport,onLaterPages=self.myFirstPageReport)
#		return response

class printCalcTable(object):
	def __init__(self):
		self.GRID_STYLE1 = TableStyle(
			[('GRID', (0,0), (-1,-1), 0.25, colors.black),
			 ('ALIGN', (0,0), (-1,-1), 'CENTER'),
			('FONTNAME',(0,0),(-1,-1),'STSong-Light'),
			('FONTSIZE',(0,0),(-1,-1),10),
 			('BACKGROUND',(0,0),(-1,1), colors.lightgrey),
# 			('BACKGROUND',(0,1),(-1,1), colors.grey),
			('SPAN',(20,0),(22,0)),
			('SPAN',(24,0),(27,0)),
			('ALIGN',(0,1),(2,-1),'LEFT'),#对齐
            ('VALIGN',(0,0),(19,0),'MIDDLE'),
            ('VALIGN',(23,0),(24,0),'MIDDLE'),  
			('SPAN',(0,0),(0,1)),
			('SPAN',(1,0),(1,1)),
			('SPAN',(2,0),(2,1)),
			('SPAN',(3,0),(3,1)),
			('SPAN',(4,0),(4,1)),
			('SPAN',(5,0),(5,1)),
			('SPAN',(6,0),(6,1)),
			('SPAN',(7,0),(7,1)),
			('SPAN',(8,0),(8,1)),
			('SPAN',(9,0),(9,1)),
			('SPAN',(10,0),(10,1)),
			('SPAN',(11,0),(11,1)),
			('SPAN',(12,0),(12,1)),
			('SPAN',(13,0),(13,1)),
			('SPAN',(14,0),(14,1)),
			('SPAN',(15,0),(15,1)),
			('SPAN',(16,0),(16,1)),
			('SPAN',(17,0),(17,1)),
			('SPAN',(18,0),(18,1)),
			('SPAN',(19,0),(19,1)),
			('SPAN',(23,0),(23,1)),
			('GRID',(0,0),(-1,-1),1,colors.black),#设置表格框线为红色，线宽为0.5
			]
			)
		
		self.styleSheet = getSampleStyleSheet()
		self.styNormal = self.styleSheet['Normal']
		self.styNormal.spaceBefore = 10
		self.styNormal.spaceAfter = 6
		font = cidfonts.UnicodeCIDFont('STSong-Light')
		pdfmetrics.registerFont(font)
			
		self.ps_report_center = ParagraphStyle(name='normal',
									fontName='STSong-Light',
									fontSize=14,
									leading=15,
									spaceAfter=10,
									alignment=TA_CENTER,
									)
		self.ps_report_left = ParagraphStyle(name='normal',
									fontName='STSong-Light',
									fontSize=10,
									leading=15,
									spaceAfter=10,
									alignment=TA_LEFT,
									)
	def myFirstPageReport(self,canvas, doc):#页眉，页脚的设置（第一页）
		canvas.saveState()
		canvas.setLineWidth(.3)
		canvas.line(0,40,10000,40)
		canvas.setFont('STSong-Light',7)
		dd=datetime.datetime.today()
		aa=datetime.datetime.strftime(dd,'%Y-%m-%d %H:%M:%S')
		zhong=self.AP[0]/2
		first=zhong-200
		second=zhong-70
		third=zhong+60
		fourth=zhong+200
		
		if self.tableName in ['dailycalcReport',]:
			footer=zhong-900
			canvas.drawString(footer, 0.45 * inch,u"%s    %s"%(_(u"符号:"),GetCalcSymbol()))
		if self.tableName in ['calcReport','department_report']:
			footer=zhong-480
			canvas.drawString(footer, 0.45 * inch,u"%s    %s"%(_(u"单位:"),GetCalcUnit()))
		canvas.drawString(first, 0.25 * inch,u"%s    %s"%(_(u"制表人:"),self.user))
		canvas.drawString(second, 0.25 * inch,u"%s    %s"%(_(u"制表时间:"),aa))
		canvas.drawString(third, 0.25 * inch,u"%s    %s"%(_(u"页码:"),doc.page))
		canvas.drawString(fourth, 0.25 * inch,u"%s    %s%s"%(_(u"每页:"),self.pagelist,_(u"条")))
		canvas.restoreState()
		
	def printReports(self,request,tables,header,field,datas,disacols,exportname,parameter):
		user_id=request.user.id
		pagelist=24
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="%s-%s.pdf"'%(exportname,user_id)
		self.user=request.user.username
		lx=[]
		title1=[]
		title=[]
		for h in range(len(header)):
			if field[h] not in disacols:
				headers_=u'%s'%header[h]
				if headers_==u'平日加班':
					headers1_=u'加班'
				elif headers_==u'公出':
					headers1_=u'假类'
				else:
					headers1_=headers_
				title1.append(headers1_)
		lx.append(title1)
		for h in range(len(header)):
			if field[h] not in disacols:
				header_=u'%s'%header[h]
				title.append(header_)
		lx.append(title)
		lens=0
		lst = []
# 		lst1=[]
		lst.append(Paragraph("""%s"""%(tables),  self.ps_report_center))
		try:
			data_=eval(datas)
		except:
			data_=datas
		for d in data_:
			linewidth=0
			if lens%pagelist==0 and lens!=0:
				t1 = Table(lx,colWidths=[110,95,60, 30,30,30,30,30,30,30,50,30,30,32,32,50,50,30,30,32,50,50,50,30,30,30,30,32])
				t1.setStyle(self.GRID_STYLE1)
				lst.append(t1)
				lst.append(Spacer(5,5))
				lst.append(PageBreak())
				lst.append(Paragraph("""%s"""%(tables),  self.ps_report_center))
				lx=[]
				lx.append(title1)
				lx.append(title)
			ll=[]
			for f in field:
				if f not in disacols:
					if f in d.keys():
						if type(d[f])==type(""):
							if d[f].find("src='/media/img/icon-yes.gif'")!=-1:
								d[f]=u'%s'%_("Yes")
							if d[f].find("src='/media/img/icon-no.gif'")!=-1:
								d[f]=u'%s'%_("No")
						if type(d[f])==type(">") and ">" in d[f]:
							d[f]=getvaluefromhtml(d[f])
						ll.append(d[f])
					else:
						ll.append("")
			lx.append(ll)
			lens+=1
		if len(header)>0:
			t1 = Table(lx,colWidths=[100,90,60, 30,30,30,30,30,30,30,50,30,30,30,30,50,50,30,30,30,50,50,50,30,30,30,30,30])
			t1.setStyle(self.GRID_STYLE1)
			lst.append(t1)
			lst.append(Spacer(5,5))
			lst.append(PageBreak())
		self.tableName=exportname
		self.lst=lst
		width=parameter*len(header)*cm
		if width<29.7*cm:
			width=29.7*cm
 		else:
 			width=width-350
		height=21*cm
		A_p=(width,height)
		self.AP=A_p
		self.pagelist=pagelist
		c = SimpleDocTemplate(self.tableName,pagesize=A_p,bottomMargin=30,topMargin=30).build(self.lst,  onFirstPage=self.myFirstPageReport,onLaterPages=self.myFirstPageReport)
#		return response


@login_required
def DataList1(request, ModelName):#查找含有/data/样式得url所得到的数据和不显示的字段
	appName=request.path.split('/')[1]

	if ModelName!='attshifts_except':
		if ModelName=='transactions':
			appName='iclock'
		dataModel=GetModel(ModelName,appName)
	else:
		dataModel=GetModel('attShifts')  #用于异常报表
	if not dataModel: return NoFound404Response(request)
	if (dataModel==IclockMsg) and ("msg" not in settings.ENABLED_MOD):
		return render_to_response("info.html", {"title":  _("Error"), "content": _("The server is not installed information services module!")});
	request.model=dataModel
	jqGrid=JqGrid(request,datamodel=dataModel)
	items=jqGrid.get_items()   #not Paged
	
	d_sum={'money__sum':0}
	
	if dataModel==HandConsume or dataModel==ICConsumerList or dataModel==Allowance:
	  d_sum=items.aggregate(Sum('money'))
	
	
	cc=jqGrid.get_json(items)
#    	if ModelName=='user':
#	      tmpFile='user_list.js'
#	
#	elif ModelName!='attshifts_except':
#		tmpFile=dataModel.__name__+'_list.js'
#	else:
#		tmpFile=request.GET.get('t','')


	tmpFile=dataModel.__name__+'_list.js'
	if dataModel.__name__.lower()=='myuser':
	      tmpFile='user_list.js'
	tmpFile=request.GET.get(TMP_VAR,tmpFile)
	if appName!='iclock':
		tmpFile=appName+'/'+tmpFile
	t=loader.get_template(tmpFile)
	#by lfg--由于底层修改Django版本，直接传参就行
	cc['user']=request.user
	
	rows=t.render(cc)
	if dataModel==HandConsume or dataModel==ICConsumerList or dataModel==Allowance:
		ll=loads(rows)
		d={}
		d['pin']=u'总计'
		d['PIN']=u'总计'
		d['user_pin']=u'总计'
		d['money']=str(d_sum['money__sum'] or 0)

		if dataModel==Allowance:
			#计算清零补贴合计
			q=request.GET.get('q','')
			userids=request.GET.get('UserID__id__in',"")
			objs=None
			if q!='':
				objs=employee.objects.filter(Q(PIN=q)|Q(EName=q))
			else:
				if userids:
					userids=userids.split(',')
					objs=employee.objects.filter(id__in=userids)
		
		
			st=request.GET.get('receive_date__gte','')
			et=request.GET.get('receive_date__lte','')
			if st:
				st=datetime.datetime.strptime(st,"%Y-%m-%d")
			if et:
				et=datetime.datetime.strptime(et,"%Y-%m-%d %H:%M:%S")	
				et=et+datetime.timedelta(days=1)
			if st and et:
				if objs:
					ts=CardCashSZ.objects.filter(UserID__in=objs,checktime__gte=st,checktime__lte=et,allow_type=1,CashType=2)
				else:
					ts=CardCashSZ.objects.filter(checktime__gte=st,checktime__lte=et,allow_type=1,CashType=2)
			else:
				if objs:
					ts=CardCashSZ.objects.filter(UserID__in=objs,allow_type=1,CashType=2)
				else:
					ts=CardCashSZ.objects.filter(allow_type=1,CashType=2)
			a_sum=ts.aggregate(Sum('money'))
			sum_money=str(a_sum['money__sum'] or 0)
			d_sum={'money__sum':0,'receive_money__sum':0,'clear_money__sum':0}
			d_sum=items.aggregate(Sum('money'),Sum('receive_money'))
			d={'PIN':u'总计','money':str(d_sum['money__sum'] or 0),'receive_money':str(d_sum['receive_money__sum'] or 0),'clear_money':sum_money}
			

		if dataModel==ICConsumerList:
			t_money=items.filter(pos_model=9).aggregate(Sum('money'))
			d['money']=str((d_sum['money__sum'] or 0)-(t_money['money__sum'] or 0))
		
		
		ll.append(d.copy())
		rows=ll
	
	
	
	return rows

@login_required
def exportList(request, ModelName):
	n=datetime.datetime.now()
	exporttblname=request.GET.get('exporttblName')
	exporttype=request.GET.get('exporttype','0')
	parameter =2
	user_id=request.user.username
	
	# if hasattr(settings,'DEMO') and settings.DEMO==1:
	# 	response = HttpResponse()
	# 	response['mimetype'] ='application/ms-excel'
	# 	response['Content-Disposition'] = 'attachment; filename=%s-%s.xls'%('test',user_id)
	# 	exportname='%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
	# 	wb = Workbook()
	# 	ws = wb.add_sheet(u'%s_%s'%('demo',1))
	# 	ws.write(0,0,u'为保证演示系统的稳定性，限制使用导出功能，抱歉！')
	# 	#wb.save(response)
	# 	name=u"%sreports/%s.xls"%(settings.ADDITION_FILE_ROOT,exportname)
	# 	url=u"/iclock/file/reports/%s.xls"%exportname
	# 	wb.save(name)
	# 	return HttpResponse(url)
	
	
	
	
	if ModelName=='exportspeday':
		exportname='%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		#response = HttpResponse()
		#response['mimetype'] ='application/ms-excel'
		#response['Content-Disposition'] = 'attachment; filename=%s-%s.xls'%(exportname,user_id)
		wb = Workbook()
		ws = wb.add_sheet(u'员工假期申请单')
		id=request.GET.get("id",0)
		fillprocesstable(ws,id)
		#wb.save(response)
		#return response
		name=u"%sreports/%s.xls"%(settings.ADDITION_FILE_ROOT,exportname)
		url=u"/iclock/file/reports/%s.xls"%exportname
		wb.save(name)
		return HttpResponseRedirect(url)
		
		
		
	elif ModelName=='calcAttShiftsReport':
		field,header,rt=ConstructAttshiftsFields1()
		del field[0]
		del header[0]
		disacols=FetchDisabledFields(request.user,'calcAttShiftsReport')
		tables=u'%s'%_(u"人员班次出勤详情")
		exportname='%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcshiftReport(request)
	elif ModelName=='calcAttExceptionReport':
		field=['DeptID', 'PIN', 'EName', 'AttDate', 'SchId','Late', 'Early','NoIn','NoOut','Absent']
		
		header=[_('department name'),_('PIN'),_('name'),_('AttDate'),_('SchId'),_('Late'),_('Early'),_('NoIn'),_('NoOut'),_('Absent')]
		for i in range(len(header)):
			header[i]=u"%s"%header[i]
		disacols=FetchDisabledFields(request.user,'calcAttExceptionReport')
		tables=u'%s'%_(u"人员班次异常详情")
		exportname='%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcAttExceptionReport(request)
	elif ModelName=='calcReport':
		r,field,header=ConstructFields()
		del field[0]
		del header[0]
		st=request.GET.get('startDate','')
		et=request.GET.get('endDate','')
		tables=u'%s'%_(u"人员出勤汇总表")
		tables=tables+'('+str(st)+'---'+str(et)+')'
		exportname='%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,'calcReport')
		datas=calcReport(request)
		footer=u'%s'%GetCalcUnit()
	elif ModelName=='dailycalcReport':
		st=request.GET.get('startDate','')
		et=request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d')
		rt,field,header=ConstructFields1(st,et)
		del field[0]
		del header[0]
		disacols=FetchDisabledFields(request.user,'dailycalcReport')
		tables=u'%s'%_(u"人员每日出勤详情")
		exportname='%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcdailyReport(request)
		footer=u'%s'%GetCalcSymbol()
	elif ModelName=='ExcepDaily':
		st=request.GET.get('startDate','')
		et=request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d')
		header=[_('department name'),_('PIN'),_('EName'),_('AttDate'),_('SchId'),_('Exception'),_('time'),_('Notes')]
		field=['deptid','badgenumber', 'username', 'AttDate', 'schid','exception','times','memo']
		disacols=FetchDisabledFields(request.user,'excep_att_report')
		tables=u'%s'%_('Excep Daily Report')
		exportname='%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcExcepDaily(request)
	elif ModelName=='searchComposite':
		fieldNames,fieldCaptions,rt=ConstructScheduleFields2(request)
		del rt[0]
		del fieldCaptions[0]
		del rt[0]
		del fieldCaptions[0]
		header=rt
		field=fieldCaptions
		disacols=FetchDisabledFields(request.user,'excep_att_report')
		exportname="%s%s"%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=exportComposite(request)
		disacols=FetchDisabledFields(request.user,'searchComposite_report')
		tables=u'%s'%_(u'综合排班表')
		#exportname=ModelName
	elif ModelName=='searchNoShift':
		field=['deptid','badgenumber','username','Title']
		header=[_('department name'),_('PIN'),_('name'),_('Title')]
		tables=u'%s'%_(u"未排班人员表")
		exportname="%s%s"%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,exporttblname)
		datas=searchnoshifts(request)
	elif ModelName=='annual_leave':
		isContainedChild=request.GET.get("isContainChild","0")
		deptIDs=request.GET.get('deptIDs',"")
		userIDs=request.GET.get('UserIDs',"")
		st=request.GET.get('startDate','')
		et=request.GET.get('endDate','')
		q=request.GET.get('q','')



		appName=request.path.split('/')[1]
		dataModel=GetModel(ModelName,appName)
		mode=dataModel.colModels()
		header=[]
		field=[]
		for m in mode:
			if 'label' in m.keys():
				if m['name']!='photo'and m['name']!='thumbnailUrl':
					header.append(m['label'])
					field.append(m['name'])
		tables=u'%s'%_(u"年假标准")
		exportname="%s%s"%(dataModel._meta.db_table,n.strftime('%Y%m%d%H%M%S'))
		from mysite.iclock.reportsview import getannual_leave
		datas=getannual_leave(request,isContainedChild,deptIDs,userIDs,st,et,q)['datas']
		disacols=[]
		
	elif ModelName=='original_records':
		rt,field,header=ConstructScheduleFields2(request)
		del_field=('id','userid','total')
		for t in del_field:
			i=field.index(t)
			del field[i]
			del header[i]
		for i in range(len(field )):
			if field[i]=='badgenumber':
				field[i]='PIN'
			elif field[i]=='username':
				field[i]='EName'
			elif field[i]=='deptid':
				field[i]='DeptID'			
		disacols=FetchDisabledFields(request.user,'original_records')
		tables=u'%s'%_('Original Records')
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=expsearchRecords(request)
	elif ModelName=='calcLeaveReport':
		r,field,header=ConstructLeaveFields()
		LClasses1=GetLeaveClasses(1)
		for t in LClasses1:
			fName='Leave_'+str(t['LeaveID'])
			field.append(fName)
			r[fName]=''
			header.append(t['LeaveName'])
		del field[0]
		del header[0]
		disacols=FetchDisabledFields(request.user,'calcLeaveReport')
		tables=u'%s'%_(u"人员请假汇总表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcLeaveReport(request)
	elif ModelName=='calcLeaveYReport':
		r,field,header=ConstructLeaveFields()
		LClasses1=GetLeaveClasses(1)
		for t in LClasses1:
			fName='Leave_'+str(t['LeaveID'])
			field.append(fName)
			r[fName]=''
			header.append(t['LeaveName'])
		del field[0]
		del header[0]
		disacols=FetchDisabledFields(request.user,'calcLeaveReport')
		calcyear=request.GET.get('y','')
		if calcyear=='':
			calcyear=str(now.year)
		tables=u'%s(%s%s)'%(_(u"人员年度请假汇总表"),calcyear,_(u"年"))
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas=calcLeaveYReport(request)
	elif ModelName=='group':
		header=[_("GroupID"),_("Group name"),_(u"创建者")]
		field=['id','name','Creator']
		tables=u'%s'%_("Group")
		exportname="%s%s"%('group',n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,exporttblname)
		datas=DataList1(request, ModelName)
	elif ModelName=='user':
		header=[_("Username"),_("first name"),_("Activate"),_("Supervisor"),_("e-mail address"),_("admin granted department"),_("Groups"),_("Userroles"),_(u"创建者")]
		field=['username','first_name','is_staff','is_superuser','email','deptadmin_set','groups','Userroles','Creator']
		tables=u'%s'%_("User")
		exportname="%s%s"%('User',n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,exporttblname)
		datas=DataList1(request, ModelName)
	elif ModelName=="getIacc_MonitorReport":#_('监控记录表'),
		r,field,header=getIacc_MonitorFields()
		del field[0]
		del header[0]
		tables=u'%s'%_(u"监控记录表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,'iacc_Monitor')
		datas=iacc_MonitorExport(request)
		
	elif ModelName=="getIacc_AlarmReport":#_('报警记录表'),
		r,field,header=getIacc_AlarmFields()
		tables=u'%s'%_(u"报警记录表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,'iacc_Alarm')
		datas=iacc_AlarmExport(request)
		
	elif ModelName=="getIacc_UserRightsReport":#_('用户权限表'),
		r,field,header=getIacc_UserRightsFields()
		del field[0]
		del header[0]
		tables=u'%s'%_(u"用户权限表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,'iacc_UserRights')
		datas=iacc_UserRightsExport(request)
		
	elif ModelName=="getIacc_RecordDetailsReport":#_('记录明细'),
		r,field,header=getIacc_RecordDetailsFields()
		del field[0]
		del header[0]
		tables=u'%s'%_(u"记录明细")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,'iacc_RecordDetails')
		datas=iacc_RecordDetailsExport(request)
		
	elif ModelName=="getIacc_SummaryRecordReport":#_('记录汇总'),
		r,field,header=getIacc_SummaryRecordFields()
		del field[0]
		del header[0]
		tables=u'%s'%_(u"记录汇总")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,'iacc_SummaryRecord')
		datas=iacc_SummaryRecordExport(request)
		
	elif ModelName=="getIacc_EmpUserRightsReport":#_('用户权限明细'),
		r,field,header=getIacc_EmpUserRightsFields()
		del field[0]
		del header[0]
		tables=u'%s'%_(u"用户权限明细")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,'iacc_EmpUserRights')
		datas=iacc_EmpUserRightsExport(request)
		
	elif ModelName=="getIacc_EmpDeviceReport":#_('用户设备'),
		r,field,header=getIacc_EmpDeviceFields()
		del field[0]
		del header[0]
		tables=u'%s'%_(u"用户设备")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		disacols=FetchDisabledFields(request.user,'iacc_EmpDevice')
		datas=iacc_EmpDeviceExport(request)
		
	elif ModelName=="ihrreports":
		try:
			uid=request.POST.get("uid",-1)
		except:
			uid=request.GET.get("uid",-1)
		try:
			cometime=request.POST.get("cometime","")
		except:
			cometime=request.GET.get("cometime","")
		tables=u'%s'%_(u"信息表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		field,header=ConstructhrremindFields(int(uid))
		try:
			datas=calchrreminddata(request,uid,cometime)
		except Exception,ee:
			print ee
		
		disacols=[]
	elif ModelName=="ihrreversedetail":
		uid=request.GET.get("uid",-1)
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		if uid=="1":
			tables=u'%s'%_(u"无指纹人员")
			if (request.user.is_superuser) or (request.user.is_alldept):
				qs=employee.objects.all().extra(where=['UserID NOT IN (%s)'%('select userid from template')])
			else:
				deptid=userDeptList(request.user)
				qs=employee.objects.filter(DeptID__DeptID__in=deptid).extra(where=['UserID NOT IN (%s)'%('select userid from template')])
		elif uid=="2":
			tables=u'%s'%_(u"无面部人员")
			if (request.user.is_superuser) or (request.user.is_alldept):
				qs=employee.objects.all().extra(where=['UserID NOT IN (%s)'%('select userid from facetemplate')])
			else:
				deptid=userDeptList(request.user)
				qs=employee.objects.filter(DeptID__DeptID__in=deptid).extra(where=['UserID NOT IN (%s)'%('select userid from facetemplate')])
		elif uid=='3':
			tables=u'%s'%_(u"今天未考勤人员")
			now=datetime.datetime.now()
			tables=tables+"(%s)"%now.strftime('%Y-%m-%d')
			if (request.user.is_superuser) or (request.user.is_alldept):
				trans=transactions.objects.filter(TTime__year=now.year,TTime__month=now.month,TTime__day=now.day).values_list("UserID")
				qs=employee.objects.all().exclude(id__in=trans)
			else:
				deptid=userDeptList(request.user)
				trans=transactions.objects.filter(UserID__DeptID__in=deptid,TTime__year=now.year,TTime__month=now.month,TTime__day=now.day).values_list("UserID")
				qs=employee.objects.filter(DeptID__DeptID__in=deptid).exclude(id__in=trans)
		elif uid=='4':
			tables=u'%s'%_(u"昨天未考勤人员")
			yestoday=datetime.datetime.now()-datetime.timedelta(days=1)
			tables=tables+"(%s)"%yestoday.strftime('%Y-%m-%d')
			if (request.user.is_superuser) or (request.user.is_alldept):
				trans=transactions.objects.filter(TTime__year=yestoday.year,TTime__month=yestoday.month,TTime__day=yestoday.day).values_list("UserID")
				qs=employee.objects.all().exclude(id__in=trans)
			else:
				deptid=userDeptList(request.user)
				trans=transactions.objects.filter(UserID__DeptID__in=deptid,TTime__year=yestoday.year,TTime__month=yestoday.month,TTime__day=yestoday.day).values_list("UserID")
				qs=employee.objects.filter(DeptID__DeptID__in=deptid).exclude(id__in=trans)
		elif uid=='5':
			tables=u'%s'%_(u"本周未考勤人员")
			now=datetime.datetime.now()
			now=datetime.datetime(now.year,now.month,now.day,0,0,0)
			start=now-datetime.timedelta(days=now.weekday())
			end=now+datetime.timedelta(days=7-now.weekday())
			zhoumo=now+datetime.timedelta(days=6-now.weekday())
			tables=tables+"(%s--%s)"%(start.strftime('%Y-%m-%d'),zhoumo.strftime('%Y-%m-%d'))
			if (request.user.is_superuser) or (request.user.is_alldept):
				trans=transactions.objects.filter(TTime__gte=start,TTime__lt=end).values_list("UserID")
				qs=employee.objects.all().exclude(id__in=trans)
			else:
				deptid=userDeptList(request.user)
				trans=transactions.objects.filter(UserID__DeptID__in=deptid,TTime__gte=start,TTime__lt=end).values_list("UserID")
				qs=employee.objects.filter(DeptID__DeptID__in=deptid).exclude(id__in=trans)
		elif uid=='6':
			tables=u'%s'%_(u"本月未考勤人员")
			now=datetime.datetime.now()
			tables=tables+u"(%s年%s月)"%(now.year,now.month)
			if (request.user.is_superuser) or (request.user.is_alldept):
				trans=transactions.objects.filter(TTime__year=now.year,TTime__month=now.month).values_list("UserID")
				qs=employee.objects.all().exclude(id__in=trans)
			else:
				deptid=userDeptList(request.user)
				trans=transactions.objects.filter(UserID__DeptID__in=deptid,TTime__year=now.year,TTime__month=now.month).values_list("UserID")
				qs=employee.objects.filter(DeptID__DeptID__in=deptid).exclude(id__in=trans)
		else:
			qs=None
		
		header=[_("PIN"),_("Emp Name"),_("department"),_("sex")]
		field=['pin','name','dept','sex']
		datas=[]
		for p in qs:
			uu={}
			uu['id']=p.id
			uu['pin']=p.PIN
			uu['name']=p.EName
			uu['dept']=p.Dept().DeptName
			uu['sex']=p.get_Gender_display()
			datas.append(uu)
		disacols=[]
	elif ModelName=="annualdays":
		field=["DeptName","PIN","EName","Birthday","Hiredday","WorkAge","annual_std","annual_ent"]
		header=[_('department name'),_('PIN'),_('Emp Name'),_("Birthday"),_('participate in the working date'),_(u'工龄'),_(u'标准年休天数'),_(u'企业标准年休天数')]
		tables=u'%s'%_(u"员工年假标准")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		y=request.GET.get('y')
		ys=datetime.datetime.strptime(y,"%Y-%m-%d")
		months=1
		days=1
		ann=annual_settings.objects.filter(Name="month_s")
		if ann.count()>0:
			months=int(ann[0].Value)
		ann=annual_settings.objects.filter(Name="day_s")
		if ann.count()>0:
			days=int(ann[0].Value)
		biao=datetime.datetime(ys.year,months,days,0,0)
		disacols=[]
		deptid=request.GET.get("DeptID",1)
		if deptid=="":
			deptid=1
		isContainChild=request.GET.get("isContainChild","0")
		deptids=[]
		if isContainChild=="1":
			deptids=getAllAuthChildDept(deptid,request)
		else:
			deptids.append(deptid)
		emp=employee.objects.filter(DeptID__in=deptids,OffDuty=0)
		datas=[]
		for e in emp:
			ll={}
			ll["DeptName"]=e.Dept().DeptName
			ll["PIN"]=e.PIN
			ll["EName"]=e.EName
			bri=e.Birthday
			if type(bri)==type(datetime.datetime.now()):
				bri=bri.strftime("%Y-%m-%d")
			else:
				bri=""
			ll["Birthday"]=bri
			ll["Hiredday"]=e.Hiredday
			ll["WorkAge"]=getWorkAge_(e.Hiredday,biao)
			ll["annual_std"]=getannual_f(e.id,biao.strftime("%Y-%m-%d"))
			ll["annual_ent"]=getuserannual(e.id,biao.strftime("%Y-%m-%d"))
			datas.append(ll)
	elif ModelName=="annualstatic":
		tables=u'%s'%_(u"年休假报表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		header,field=getannualstaticFiled(request)
		disacols=[]


		isContainedChild=request.GET.get("isContainChild","0")
		deptIDs=request.GET.get('deptIDs',"")
		q=request.GET.get('q','')
		q=unquote(q)
		from mysite.iclock.reportsview import getannualstatic
		datas=getannualstatic(request,isContainedChild,deptIDs,q)['datas']
		disacols=[]





	elif ModelName=="employee_finger":
		tables=u'%s'%_(u"人员信息采集追踪表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		header=[_(u'单位编号'),_(u'单位名称'),_(u'PIN'),_(u'姓名'),_(u'卡号'),_(u'指纹采集'),_(u'面部采集'),_(u'卡采集')]
		for i in range(len(header)):
			header[i]=u"%s"%header[i]
		field=['DeptNumber','DeptName','pin','name','card','is_register','is_register_face','is_register_card']
		datas=exportemployee_finger(request)
		disacols=[]
	elif ModelName=='department_finger':
		tables=u'%s'%_(u"人员信息采集汇总表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		header=[_(u'单位编号'),_(u'单位名称'),_(u'实有人数'),_(u'采集指纹人数'),_(u'指纹采集率%'),_(u'采集面部人数'),_(u'面部采集率%')]
		for i in range(len(header)):
			header[i]=u"%s"%header[i]
		field=['DeptNumber','DeptName','count','finger_count','rate','face_count','face_rate']
		datas=exportdepartment_finger(request)
		disacols=[]
	elif ModelName=='device_assignment':
		tables=u'%s'%_(u"单位管理设备表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		header=[_(u'单位编号'),_(u'单位名称'),_(u'设备数量'),_(u'设备SN号')]
		for i in range(len(header)):
			header[i]=u"%s"%header[i]
		field=['DeptNumber','DeptName','Devices','DeviceSN']
		datas=exportdevice_assignment(request)
		disacols=[]
	elif ModelName=='daily_devices':
		tables=u'%s'%_(u"每日开机统计表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		header=[_(u'单位编号'),_(u'单位名称'),_(u'当日开机数'),_(u'设备数'),_(u'开机率%')]
		for i in range(len(header)):
			header[i]=u"%s"%header[i]
		field=['DeptNumber','DeptName','device_on','device_count','rate']
		datas=exportdaily_devices(request)
		disacols=[]
	elif ModelName=='earlylatest_records':
		tables=u'%s'%_(u"最早最晚汇总表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		r,field,header=ConstructScheduleFields2(request)
		del field[0]
		del header[0]
		datas=exportEarlystAndLastest(request)
		disacols=[]
	elif ModelName=="department_report":
		tables=u'%s'%_(u"单位统计汇总表")
		exportname="%s%s"%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		AbnomiteRptItems=GetLeaveClasses()
		AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
		fieldNames=['dept','count','duty','realduty','absent','late','early','timeout','speday','gongchu','noin','noout','yingqian']
		fieldTitle=[_(u'单位'),_(u'人数')]
		fieldCaptions=[_(u'单位'),_(u'人数'),_('duty'),_('realduty'),_('absent'),_('late'),_('early'),_(u'加班'),_(u'请假'),_(u'公出'),_('noin'),_('noout'),_(u'应签次数')]
		disacols=FetchDisabledFields(request.user,'department_report')
		fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1000))
		fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1000))
		fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1004))
		fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1001))
		fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1002))
		fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1005))
		fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1003))
		fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1))
		fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1008))
		fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1009))
		fieldTitle.append(_(u"次"))
		r=[]
		it=0
		LClasses1=GetLeaveClasses(1)
		for t in LClasses1:
			if t['LeaveID']==1:
				continue
			fName='Leave_'+str(t['LeaveID'])
			fieldNames.append(fName)
			fieldTitle.append(getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,t['LeaveID']))
			fieldCaptions.append(t['LeaveName'])
		fieldNames.append('shijian')
		fieldNames.append('chuqinlv')
		fieldTitle.append(_(u'小时'))
		fieldTitle.append(_(u'出勤率 %'))
		fieldCaptions.append(_(u'工作时间'))
		fieldCaptions.append(_(u'出勤率 %'))
		header=fieldCaptions
		field=fieldNames
		datas=departmentreportItemExport(request)
		footer=u'%s'%GetCalcUnit()
		#wb = Workbook()
		#ws = wb.add_sheet(tables)
		#filltableDept(fieldCaptions, datas, ws, fieldTitle,disacols,fieldNames,tables)
		#applytime=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
		#name=u"%sreports/%s%s.xls"%(settings.ADDITION_FILE_ROOT,exportname,applytime)
		#url=u"/iclock/file/reports/%s%s.xls"%(exportname,applytime)
		#wb.save(name)
		#adminLog(time=datetime.datetime.now(),User=request.user, action=u"Export "+ModelName+u" files",model=ModelName).save()
		#return HttpResponse(url)
	elif ModelName=="forget_records":
		tables=u'%s'%_(u"补记录表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		field=['DeptID','DeptName','PIN','EName','CHECKTIME','CHECKTYPE','YUYIN']
		header=[_(u'单位编号'),_(u'单位名称'),_(u'身份证号'),_(u'姓名'),_(u'时间'),_(u'考勤类型'),_(u'原因')]
		datas=exportforget_records(request)
		disacols=[]
	elif ModelName=="attRecAbnormite":
		isContainedChild=request.GET.get("isContainChild","0")
		deptIDs=request.GET.get('deptIDs',"")
		userIDs=request.GET.get('UserIDs',"")
		st=request.GET.get('startDate','')
		et=request.GET.get('endDate','')
		q=request.GET.get('q','')



		appName=request.path.split('/')[1]
		dataModel=GetModel(ModelName,appName)
		mode=dataModel.colModels()
		header=[]
		field=[]
		for m in mode:
			if 'label' in m.keys():
				if m['name'] == 'checktime':
					m['name'] = 'TTime'
				if m['name']!='photo'and m['name']!='thumbnailUrl':
					header.append(m['label'])
					field.append(m['name'])
		tables=u'%s'%_(u"出勤记录详情")
		exportname="%s%s"%(dataModel._meta.db_table,n.strftime('%Y%m%d%H%M%S'))
		from mysite.iclock.reportsview import getModelRecords
		datas=getModelRecords(request,attRecAbnormite)['datas']
		disacols=[]
	elif ModelName=="meeting_sign_report":
		tables=u'%s'%_(u"人员签到情况报表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		field=['pin','name','DeptName','checkin','checkout','meetname','note']
		header=[_(u'工号'),_(u'姓名'),_(u'部门名称'),_(u'签到时间'),_(u'签退时间'),_(u'会议名称'),_(u'参会详情')]
		datas=export_meeting_sign_report(request)
		disacols=[]	
	elif ModelName=="meeting_not_sign_report":
		tables=u'%s'%_(u"人员未签到情况报表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		field=['pin','name','DeptName','meetname']
		header=[_(u'工号'),_(u'姓名'),_(u'部门名称'),_(u'会议名称')]
		datas=export_meeting_not_sign_report(request)
		disacols=[]
	elif ModelName=="meeting_report":
		tables=u'%s'%_(u"会议签到情况报表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		field=['MeetID','conferenceTitle','Location','Starttime','Endtime','duty','onduty','late','early','speday','absent','rate']
		header=[_(u'会议编号'),_(u'会议名称'),_(u'会议室'),_(u'开始时间'),_(u'结束时间'),_(u'应到'),_(u'实到'),_(u'迟到'),_(u'早退'),_(u'请假'),_(u'缺席'),_(u'出席率')]
		datas=export_meeting_report(request)
		disacols=[]
	elif ModelName=="meeting_user_report":
		tables=u'%s'%_(u"人员参会情况统计")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		field=['pin','name','DeptName','duty','onduty','absent','late','early','speday','rate']
		header=[_(u'工号'),_(u'姓名'),_(u'部门名称'),_(u'应参加会议总数'),_(u'实参加会议总数'),_(u'未参加会议总数'),_(u'迟到次数'),_(u'早退次数'),_(u'请假次数'),_(u'出席率')]
		datas=export_meeting_user_report(request)
		disacols=[]
	elif ModelName=="meeting_user_late_report":
		tables=u'%s'%_(u"人员迟到及早退情况报表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		field=['pin','name','DeptName','conferenceTitle','st','et','rst','ret','speday','absent','late','early']
		header=[_(u'工号'),_(u'姓名'),_(u'部门名称'),_(u'会议名称'),_(u'开始时间'),_(u'结束时间'),_(u'签到时间'),_(u'签退时间'),_(u'请假'),_(u'缺席'),_(u'迟到'),_(u'早退')]
		datas=export_meeting_user_late_report(request)
		disacols=[]
	elif ModelName=="meeting_room_report":
		tables=u'%s'%_(u"会议室使用情况报表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		rt,field,header=ConstructROOMFields(request)
		datas=export_meeting_room_report(request)
		disacols=[]
	elif ModelName=='transactions':
		appName=request.path.split('/')[1]
		dataModel=GetModel(ModelName)
		mode=dataModel.colModels()
		request.model=dataModel
		jqGrid=JqGrid(request,datamodel=dataModel)
		items=jqGrid.get_items()   #not Paged
		cc=jqGrid.get_json(items)
		itemlist=cc['latest_item_list']
		datas=[]
		lines=0
		sheet=1
		header=[]
		field=[]
		for m in mode:
			if 'label' in m.keys():
				if m['name']!='photo'and m['name']!='thumbnailUrl':
					header.append(m['label'])
					field.append(m['name'])
		tables=u'%s'%dataModel._meta.verbose_name.capitalize()
		exportname="%s%s"%(dataModel._meta.db_table,n.strftime('%Y%m%d%H%M%S'))
		row=request.GET.get("rows")
		disacols=FetchDisabledFields(request.user,exporttblname)
		if exporttype=='0':
			response = HttpResponse()
			response['mimetype'] ='application/ms-excel'
			response['Content-Disposition'] = 'attachment; filename=%s-%s.xls'%(exportname,user_id)
			wb = Workbook()
			for t in itemlist:
				lines+=1
				d={}
				emp=t.employee()
				d['id']=t.id
				d['DeptID']=emp.Dept().DeptNumber
				d['DeptName']=emp.Dept().DeptName
				d['PIN']=emp.PIN
				d['EName']=emp.EName
				d['TTime']=t.TTime.strftime('%Y-%m-%d %H:%M:%S')
				d['State']=getRecordState(t.State)
				try:
					d['Device']=t.SN_id
				except:
					d['Device']=''
				if lines>sheet*20000:
					ws = wb.add_sheet(u'%s_%s'%(tables,sheet))
					filltable(header, datas, ws, field,disacols,tables)
					datas=[]
					datas.append(d.copy())
					sheet+=1
				else:
					datas.append(d.copy())
			#if datas:
			ws = wb.add_sheet(u'%s_%s'%(tables,sheet))
			filltable(header, datas, ws, field,disacols,tables)
#			wb.save(response)
			name=u"%sreports/%s.xls"%(settings.ADDITION_FILE_ROOT,exportname)
			url=u"/iclock/file/reports/%s.xls"%exportname
			wb.save(name)
			return HttpResponse(url)


		elif exporttype=='1':
			#fn=u"%sreports/%s.txt"%(settings.ADDITION_FILE_ROOT,exportname)
			#url=u"/iclock/file/reports/%s.txt"%exportname
			#f=file(fn, "a+" or "w+")
			response = HttpResponse()
			response['mimetype'] ='application/octet-stream'
			response['Content-Disposition'] = 'attachment; filename="%s-%s.txt"'%(exportname,user_id)
			for t in itemlist:
				lines+=1
				d={}
				emp=t.employee()
				d['id']=t.id
				d['DeptID']=emp.Dept().DeptNumber
				d['DeptName']=emp.Dept().DeptName
				d['PIN']=emp.PIN
				d['EName']=emp.EName or ''
				d['TTime']=t.TTime.strftime('%Y-%m-%d %H:%M:%S')
				d['State']=getRecordState(t.State)
				try:
					d['Device']=t.SN_id or ''
				except:
					d['Device']=''
				# if lines>sheet*20000:
					# filetxtcontents(header, datas, field,disacols,tables,f)
					# datas=[]
					# datas.append(d.copy())
					# sheet+=1
				# else:
				datas.append(d.copy())
			filetxtcontents(header, datas, field,disacols,tables,response)
			return response#HttpResponse(url)
				
		else:
			if ModelName=="iclock":
				parameter=2.5
# 			if ModelName=='calcReport':
# 				p=printCalcTable()
# 				print 'rrrrrrrrrrrrrrrrrrrrrrrr'
# 			else:
# 				p=printTable()
# 				print 'oooooooooooooooooooo'
			p=printTable()
			if cc['records']>20000:
				tables=u'记录条数大于两万条，请选择导出excel方式！'
				wb = Workbook()
				ws = wb.add_sheet(u'%s_%s'%('sheet1',1))
				ws.write(0,0,tables)
				
				name=u"%sreports/%s.xls"%(settings.ADDITION_FILE_ROOT,exportname)
				url=u"/iclock/file/reports/%s.xls"%exportname
				wb.save(name)
				return HttpResponse(url)
		
				
				
				#response=p.printReports(request,tables,[],field,[],disacols,ModelName,parameter)
				#return response
			else:
				for t in itemlist:
					lines+=1
					d={}
					emp=t.employee()
					d['id']=t.id
					d['DeptID']=emp.Dept().DeptNumber
					d['DeptName']=emp.Dept().DeptName
					d['PIN']=emp.PIN
					d['EName']=emp.EName
					d['TTime']=t.TTime.strftime('%Y-%m-%d %H:%M:%S')
					d['State']=getRecordState(t.State)
					try:
						d['Device']=t.SN_id
					except:
						d['Device']=''
					datas.append(d.copy())
				fn=u"%sreports/%s.pdf"%(settings.ADDITION_FILE_ROOT,exportname)
				url=u"/iclock/file/reports/%s.pdf"%exportname
				p=printTable()
				p.printReports(request,tables,header,field,datas,disacols,fn,parameter)
				adminLog(time=datetime.datetime.now(),User=request.user, action=u'%s' % _(u"Export") + u'%s' % _(u"Reports"),model=tables[:40],object = request.META["REMOTE_ADDR"]).save(force_insert=True)
				return HttpResponse(url)	
	elif ModelName=='calcAllReport':
		tables=u'%s'%_(u"汇总表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas = export_calcallreport(request)
		if exporttype=='0':
			response = HttpResponse()
			response['mimetype'] ='application/ms-excel'
			response['Content-Disposition'] = 'attachment; filename=%s-%s.xls'%(exportname,user_id)
			wb = Workbook()
			ws = wb.add_sheet(u'%s'%tables)
			from mysite.iclock.myreportview import exportcalcallreport
			exportcalcallreport(ws,datas)
			name=u"%sreports/%s.xls"%(settings.ADDITION_FILE_ROOT,exportname)
			url=u"/iclock/file/reports/%s.xls"%exportname
			wb.save(name)
			return HttpResponse(url)
	elif ModelName=='exceptionReport':
		tables=u'%s'%_(u"病假、事假和旷工情况统计表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas = export_calcexceptionreport(request)
		if exporttype=='0':
			response = HttpResponse()
			response['mimetype'] ='application/ms-excel'
			response['Content-Disposition'] = 'attachment; filename=%s-%s.xls'%(exportname,user_id)
			wb = Workbook()
			ws = wb.add_sheet(u'%s'%tables)
			from mysite.iclock.myreportview import exportcalcexceptionreport
			exportcalcexceptionreport(ws,datas)
			name=u"%sreports/%s.xls"%(settings.ADDITION_FILE_ROOT,exportname)
			url=u"/iclock/file/reports/%s.xls"%exportname
			wb.save(name)
			return HttpResponse(url)
	elif ModelName=='backReport':
		tables=u'%s'%_(u"扣发审批表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas = export_backreport(request)
		if exporttype=='0':
			response = HttpResponse()
			response['mimetype'] ='application/ms-excel'
			response['Content-Disposition'] = 'attachment; filename=%s-%s.xls'%(exportname,user_id)
			wb = Workbook()
			ws = wb.add_sheet(u'%s'%tables)
			from mysite.iclock.myreportview import exportbackreport
			exportbackreport(ws,datas)
			name=u"%sreports/%s.xls"%(settings.ADDITION_FILE_ROOT,exportname)
			url=u"/iclock/file/reports/%s.xls"%exportname
			wb.save(name)
			return HttpResponse(url)
	elif ModelName=='allexceptionReport':
		tables=u'%s'%_(u"异常汇总表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		datas = export_allexceptionreport(request)
		if exporttype=='0':
			response = HttpResponse()
			response['mimetype'] ='application/ms-excel'
			response['Content-Disposition'] = 'attachment; filename=%s-%s.xls'%(exportname,user_id)
			wb = Workbook()
			ws = wb.add_sheet(u'%s'%tables)
			from mysite.iclock.myreportview import exportallexceptionreport
			exportallexceptionreport(ws,datas)
			name=u"%sreports/%s.xls"%(settings.ADDITION_FILE_ROOT,exportname)
			url=u"/iclock/file/reports/%s.xls"%exportname
			wb.save(name)
			return HttpResponse(url)
	elif ModelName=='jiezhuan':
		year = request.GET.get('y')
		tables=u'%s'%_(u"人员请假结转汇总表")
		exportname=u'%s%s'%(ModelName,n.strftime('%Y%m%d%H%M%S'))
		field=['PIN','workcode','ename','dept','qall','now','all']
		header=[_(u'身份证号'),_(u'考勤编号'),_(u'姓名'),_(u'单位名称'),_(str(int(year)-1)+u'年假期结转值'),_(year+u'年结转'),_(year+u'年假期结转值')]
		datas=export_jiezhuanreport(request)
		disacols=[]
	else:
		appName=request.path.split('/')[1]
		if ModelName!='attshifts_except':
			if ModelName=='transactions':
				appName='iclock'
			if ModelName=='acc_exception':
				ModelName='records'
			dataModel=GetModel(ModelName,appName)
		else:
			dataModel=GetModel('attShifts')
		if ModelName=='iclock':
			mode=dataModel.colModels(request)
		else:
			mode=dataModel.colModels()
		header=[]
		field=[]
		BackupDev = u'%s'%_(u'标准机构代码') #泰康保险用来保存总公司定义的机构代码
		if request.GET.get('mod_name')=='ipos':
			modeipos=mode[0:12]
			for m in modeipos:
				if 'label' in m.keys():
					if m['name']!='photo'and m['name']!='thumbnailUrl':
						if m['name'] == 'Dept' and m['label'] == BackupDev and settings.TAIKANG == 0:
							continue
						else:
							header.append(m['label'])
							field.append(m['name'])
		else:
			for m in mode:
				if 'label' in m.keys():
					if m['name']!='photo'and m['name']!='thumbnailUrl':
						if m['name'] == 'Dept' and m['label'] == BackupDev and settings.TAIKANG == 0:
							continue
						else:
							header.append(m['label'])
							field.append(m['name'])
		tables=u'%s'%dataModel._meta.verbose_name.capitalize()
		exportname="%s%s"%(dataModel._meta.db_table,n.strftime('%Y%m%d%H%M%S'))
		datas=DataList1(request, ModelName)
		disacols=FetchDisabledFields(request.user,exporttblname)
	adminLog(time = datetime.datetime.now(), User = request.user,
			action = u'%s' % _(u"Export") + u'%s' % _(u"Reports"), model = tables[:40],
			object = request.META["REMOTE_ADDR"]).save(force_insert = True)  #
	if exporttype=='0':
		response = HttpResponse()
		response['mimetype'] ='application/ms-excel'
		response['Content-Disposition'] = 'attachment; filename=%s-%s.xls'%(exportname,user_id)
		wb = Workbook()
		ws = wb.add_sheet(u'%s'%tables)
		if ModelName=="USER_SPEDAY" or ModelName=="User_OverTime":
			disacols.append('operate')
			disacols.append('file')
			filltable1(header, datas, ws, field,disacols,tables)
		elif ModelName=="dailycalcReport" or ModelName=="department_report":
			filltablehasfooter(header, datas, ws, field,disacols,tables,footer)
		elif ModelName=="calcReport":
			filltablehasfooter_new(header, datas, ws, field,disacols,tables,footer)
		else:
			filltable(header, datas, ws, field,disacols,tables)
		#wb.save(response)
		
		#适应IE8
		name=u"%sreports/%s.xls"%(settings.ADDITION_FILE_ROOT,exportname)
		url=u"/iclock/file/reports/%s.xls"%exportname
		wb.save(name)
		return HttpResponse(url)
		
	elif exporttype=='1':
		#fn=u"%sreports/%s.txt"%(settings.ADDITION_FILE_ROOT,exportname)
		#url=u"/iclock/file/reports/%s.txt"%exportname
		
		#f=file(fn, "a+" or "w+")
		
		
		
		response = HttpResponse()
		response['mimetype'] ='application/octet-stream'
		response['Content-Disposition'] = 'attachment; filename="%s-%s.txt"'%(exportname,user_id)
		filetxtcontents(header, datas, field,disacols,tables,response)
		return response
	else:
		if ModelName=="iclock":
			parameter=2.5
		fn=u"%sreports/%s.pdf"%(settings.ADDITION_FILE_ROOT,exportname)
		url=u"/iclock/file/reports/%s.pdf"%exportname
		if ModelName=='calcReport':
			p=printCalcTable()
		else:
			p=printTable()
		p.printReports(request,tables,header,field,datas,disacols,fn,parameter)
	return HttpResponse(url)
    
def filetxtcontents(header, data, field,disacols,tables,f):
	text=u"\r\n"
	text+=u"%s\r\n"%tables
	j=0
	i=0
	while j<len(header):
		if field[j] not in disacols:
			if field[j]=='Parent':
				text+=u"%s,"%_("ParentID")
				text+=u"%s,"%_("ParentName")
			else:
				text+=u"%s,"%header[j]
		j+=1
	text=text.encode('gb18030')
	text=text[:-1]
	f.write(text)
	try:
		data_=eval(data)
	except:
		data_=data
	for i in data_:
		text=u"\r\n"
		for k in field:
			if k not in disacols:
				try:
						
					if (type(i[k])==int) or (type(i[k])==datetime.date):
						i[k]=str(i[k])
					try:
						if i[k].find("src='/media/img/icon-yes.gif'")!=-1:
							i[k]=u'%s'%_("Yes")
						if i[k].find("src='/media/img/icon-no.gif'")!=-1:
							i[k]=u'%s'%_("No")
						if ">" in i[k]:
							#i[k]=i[k].split(">")[1]
							#if "<" in i[k]:
							#	i[k]=i[k].split("<")[0]
							i[k]=getvaluefromhtml(i[k])
					except:
						pass
					if k=='Parent':
						dept=i[k].split(" ")
						if len(dept)>1:
							text+="%s\t"%dept[0]
							if len(dept)>2:
								depp=dept[1].decode('utf-8')+u" "+dept[2].decode('utf-8')
								text+=u"%s\t"%depp
							else:
								text+=u"%s\t"%dept[1].decode('utf-8')
						else:
							text+=u" \t \t"
						continue
					#if i[k]==None or i[k]=='None':
					#	i[k]=u''
					try:
						i[k] = i[k].decode('utf-8')
					except:
						i[k]=i[k]
					text+=u"%s\t"%i[k]	
				except Exception,e:
					print e
					text+=u" \t"
		text=text.replace(u",",u"，").replace(u"\t",u',')
		text=text.encode('gb18030')
		text=text[:-1]
		f.write(text)
		
def getvaluefromhtml(value):
	if len(value)>3 and '<' in value:
		valuelist=value.split(">")
		result=""
		for v in valuelist:
			if '<' in v:
				result+=" "+v.split("<")[0]
		result=result.replace("&nbsp;"," ")
	else:
		result=value
	return result

def filltablehasfooter(header, data, ws,field,disacols,tables,footer):
	style = Fields_date_css()
	field_style=Fields_css()
	title_style=Title_css()
	footer_style=footer_css()
	title_col_style=title_col_css()
	j=0
	i=0
	while j<len(header):
		if field[j] not in disacols:
			if field[j]=='Parent':
				ws.write(1,i,u'%s'%_("ParentID"),title_col_style)
				ws.write(1,i+1,u'%s'%_("ParentName"),title_col_style)
				ws.col(i).width=0x1000
				ws.col(i+1).width=0x1000
				i+=2
			else:
				ws.write(1,i,u'%s'%header[j],title_col_style)
				ws.col(i).width=0x1000
				i+=1
		j+=1
	ws.write_merge(0,0,0,i-1,u'%s'%tables,title_style)
	w=i-1
	line=2
	column=0
	ll=[]
	try:
		data_=eval(data)
	except:
		data_=data
	for i in data_:
		column=0
		for k in field:
			if k not in disacols:
				try:
						
					if (type(i[k])==int) or (type(i[k])==datetime.date):
						i[k]=str(i[k])
					try:
						if i[k].find("src='/media/img/icon-yes.gif'")!=-1:
							i[k]=u'%s'%_("Yes")
						if i[k].find("src='/media/img/icon-no.gif'")!=-1:
							i[k]=u'%s'%_("No")
						if ">" in i[k]:
							i[k]=getvaluefromhtml(i[k])
					except:
						pass
					if k=='Parent':
						dept=i[k].split(" ")
						if len(dept)>1:
							ws.write(line, column, dept[0],field_style)
							if len(dept)>2:
								depp=dept[1].decode('utf-8')+u" "+dept[2].decode('utf-8')
								ws.write(line, column+1,depp,field_style )
							else:
								ws.write(line, column+1, dept[1].decode('utf-8'),field_style)
						else:
							ws.write(line, column, 0,field_style)
							ws.write(line, column+1, "",field_style)
						column+=2
						continue
					if type(i[k])==datetime.datetime:
						ws.write(line, column, i[k], style)
					else:
						if i[k]==None or i[k]=='None':
							i[k]=''
						try:
							i[k] = i[k].decode('utf-8')
						except:
							i[k]=i[k]
							
						ws.write(line, column, i[k],field_style)
				except:
					ws.write(line, column,'',field_style)
				column+=1
		line+=1
	if footer:
		ws.write_merge(line,line,0,w,u'%s'%footer,footer_style)

def filltablehasfooter_new(header, data, ws,field,disacols,tables,footer):
	style = Fields_date_css2()
	field_style2=Fields_css2()
	title_style=Title_css2()
	footer_style=footer_css2()
	title_col_11=title_col_css11()
	j=0
	i=0
	while j<len(header):
		if field[j] not in disacols:
			if i<20 or i==23:
				ws.write_merge(1,2,i,i,u'%s'%header[j].lstrip().rstrip(),title_col_11)
			else:
				ws.write(2,i,u'%s'%header[j].lstrip().rstrip(),title_col_11)
			i+=1
		j+=1
	ws.write_merge(1,1,20,22,u'加班',title_col_11)
	ws.write_merge(1,1,24,len(header)-1,u'假类',title_col_11)

	ws.col(0).width = 0xE00
	ws.col(1).width = 0xE00
	ws.col(2).width = 0x800
	ws.col(3).width = 0x800
	for index in range(len(header)):
		if len(header[index].lstrip().rstrip())==2 and index not in [0,1,2,3]:
			ws.col(index).width = 0x300
		elif len(header[index].lstrip().rstrip())==3 and index not in [0,1,2,3]:
			ws.col(index).width = 0x300
	ws.col(10).width = 0x500
	ws.col(16).width = 0x500
	
	ws.write_merge(0,0,0,len(header)-1,u'%s'%tables,title_style)
	w=i-1
	line=3
	column=0
	ll=[]
	try:
		data_=eval(data)
	except:
		data_=data
	for i in data_:
		column=0
		for k in field:
			if k not in disacols:
				try:
						
					if (type(i[k])==int) or (type(i[k])==datetime.date):
						i[k]=str(i[k])
					try:
						if i[k].find("src='/media/img/icon-yes.gif'")!=-1:
							i[k]=u'%s'%_("Yes")
						if i[k].find("src='/media/img/icon-no.gif'")!=-1:
							i[k]=u'%s'%_("No")
						if ">" in i[k]:
							i[k]=getvaluefromhtml(i[k])
					except:
						pass
					if type(i[k])==datetime.datetime:
						ws.write(line, column, i[k], style)
					else:
						if i[k]==None or i[k]=='None':
							i[k]=''
						try:
							i[k] = i[k].decode('utf-8')
						except:
							i[k]=i[k]
							
						ws.write(line, column, i[k],field_style2)
				except:
					ws.write(line, column,'',field_style2)
				column+=1
		line+=1
	if footer:
		ws.write_merge(line,line+1,0,len(header)-1,u'%s'%footer,footer_style)

def fillprocesstable(ws,id):
	from mysite.iclock.process import getspedaydetails
	ll=getspedaydetails(id)
	title_style1=Title_css1()
	title_col_style=title_col_css()
	title_col_style1=title_col_css1()#左下
	title_col_style7=title_col_css7()#中上
	title_col_style3=title_col_css3()#中3
	title_col_style4=title_col_css4()#中下
	title_col_style5=title_col_css5()#中上右
	title_col_style6=title_col_css6()#中上左
	title_col_style8=title_col_css8()#中上右
	title_col_style9=title_col_css9()#下
	title_col_style10=title_col_css10()#右
	ws.write_merge(0,3,0,5,u'员工假期申请单',title_style1)
	
	ws.write_merge(4,6,0,0,u'姓名',title_col_style)
	ws.write_merge(4,6,1,1,ll['name'],title_col_style1)
	ws.write_merge(4,6,2,2,u'部门',title_col_style)
	ws.write_merge(4,6,3,3,ll['deptname'],title_col_style1)
	ws.write_merge(4,6,4,4,u'职务',title_col_style)
	ws.write_merge(4,6,5,5,ll['title'],title_col_style1)
	ws.col(0).width=0x1000
	ws.col(1).width=0x1000
	ws.col(2).width=0x1000
	ws.col(3).width=0x1000
	ws.col(4).width=0x1000
	ws.col(5).width=0x1000
	ws.row(4).height=0x1000
	ws.write_merge(7,9,0,0,u'请假类别',title_col_style)
	ws.write_merge(7,9,1,2,ll['leaveclass'],title_col_style1)
	ws.write_merge(7,9,3,3,u'联系电话',title_col_style)
	ws.write_merge(7,9,4,5,ll['mobile'],title_col_style1)
	
	st=ll['st']
	et=ll['et']
	stet=u'  %s 年 %s 月 %s 日 %s 时至 %s 年 %s 月 %s 日 %s 时'%(st.year,st.month,st.day,st.hour,et.year,et.month,et.day,et.hour)
	ws.write_merge(10,12,0,0,u'请假时间',title_col_style)
	ws.write_merge(10,12,1,5,stet,title_col_style)
	
	ws.write_merge(13,15,0,0,u'外出地点',title_col_style)
	ws.write_merge(13,15,1,2,ll['place'],title_col_style1)
	ws.write_merge(13,15,3,3,u'工作承接人',title_col_style)
	ws.write_merge(13,15,4,5,ll['successor'],title_col_style1)
	
	ws.write_merge(16,18,0,0,u'备注',title_col_style)
	ws.write_merge(16,18,1,5,ll['remarks'],title_col_style1)
	
	ws.write_merge(19,25,0,0,u'申请人休假理由',title_col_style)
	ws.write_merge(19,24,1,5,ll['yy'],title_col_style1)
	shen=u"申请人签字：%s"%ll['name']
	nian=u"%s年%s月%s日"%(ll['ad'].year,ll['ad'].month,ll['ad'].day)
	ws.write_merge(25,25,1,1,'',title_col_style5)
	ws.write_merge(25,25,2,3,shen,title_col_style3)
	ws.write_merge(25,25,4,5,nian,title_col_style6)
	
	processll=[]
	for a in ll.keys():
		if a.find("process_")!=-1:#查找所有的审核流程
			processll.append(a)
	lp= len(processll)
	sortll={}
	processll_=[]
	for x in processll:
		sortll[ll[x]['procSN']]=x#x为ll的key值，通过procSN排序，这里为了实现流程按从小到大排序
	sk=sortll.keys()
	sk.sort()
	for s in sk:
		processll_.append(sortll[s])
	if lp<6:
		i=0
		for x in processll_:
			pll=ll[x]
			yijian=u"%s意见："%pll['userrole']
			ws.write_merge(26+6*i,26+6*i,0,5,yijian,title_col_style1)
			ws.write_merge(27+6*i,30+6*i,0,5,'    '+pll['yijian'],title_col_style10)
			shen=u"签名：%s"%pll['qianming']
			if pll['riqi']=="":
				nian=u"      年   月   日"
			else:
				nian=u"%s年%s月%s日"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
			ws.write_merge(31+6*i,31+6*i,0,2,'',title_col_style5)
			ws.write_merge(31+6*i,31+6*i,3,4,shen,title_col_style9)
			ws.write_merge(31+6*i,31+6*i,5,5,nian,title_col_style8)
			i+=1
			
	elif lp<10:
		yu=lp%5
		i=0
		j=0
		for x in processll_:
			pll=ll[x]
			if i<yu:
				if j%2==0:
					yijian=u"%s意见："%pll['userrole']
					ws.write_merge(26+6*i,26+6*i,0,2,yijian,title_col_style1)
					ws.write_merge(27+6*i,30+6*i,0,2,'    '+pll['yijian'],title_col_style10)
					shenu=u"签名：%s"%pll['qianming']
					if pll['riqi']=="":
						nian=u"      年   月   日"
					else:
						nian=u"%s年%s月%s日"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
					ws.write_merge(31+6*i,31+6*i,0,1,shen,title_col_style3)
					ws.write_merge(31+6*i,31+6*i,2,2,nian,title_col_style6)
				else:
					yijian=u"%s意见："%pll['userrole']
					ws.write_merge(26+6*i,26+6*i,3,5,yijian,title_col_style1)
					ws.write_merge(27+6*i,30+6*i,3,5,pll['yijian'],title_col_style10)
					shen=u"签名：%s"%pll['qianming']
					if pll['riqi']=="":
						nian=u"      年   月   日"
					else:
						nian=u"%s年%s月%s日"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
					ws.write_merge(31+6*i,31+6*i,3,4,shen,title_col_style3)
					ws.write_merge(31+6*i,31+6*i,5,5,nian,title_col_style6)
					i+=1
				j+=1
			else:
				yijian=u"%s意见："%pll['userrole']
				ws.write_merge(26+6*i,26+6*i,0,5,yijian,title_col_style1)
				ws.write_merge(27+6*i,30+6*i,0,5,pll['yijian'],title_col_style10)
				shen=u"签名：%s"%pll['qianming']
				if pll['riqi']=="":
					nian=u"      年   月   日"
				else:
					nian=u"%s年%s月%s日"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
				ws.write_merge(31+6*i,31+6*i,0,3,shen,title_col_style3)
				ws.write_merge(31+6*i,31+6*i,4,5,nian,title_col_style6)
				i+=1
	else:
		i=0
		j=0
		for x in processll_:
			pll=ll[x]
			if len(processll_)%2==0:
				if j%2==0:
					yijian=u"%s意见："%pll['userrole']
					ws.write_merge(26+6*i,26+6*i,0,2,yijian,title_col_style1)
					ws.write_merge(27+6*i,30+6*i,0,2,pll['yijian'],title_col_style10)
					shen=u"签名：%s"%pll['qianming']
					if pll['riqi']=="":
						nian=u"      年   月   日"
					else:
						nian=u"%s年%s月%s日"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
					ws.write_merge(31+6*i,31+6*i,0,1,shen,title_col_style3)
					ws.write_merge(31+6*i,31+6*i,2,2,nian,title_col_style6)
				else:
					yijian=u"%s意见："%pll['userrole']
					ws.write_merge(26+6*i,26+6*i,3,5,yijian,title_col_style1)
					ws.write_merge(27+6*i,30+6*i,3,5,pll['yijian'],title_col_style10)
					shen=u"签名：%s"%pll['qianming']
					if pll['riqi']=="":
						nian=u"      年   月   日"
					else:
						nian=u"%s年%s月%s日"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
					ws.write_merge(31+6*i,31+6*i,3,4,shen,title_col_style3)
					ws.write_merge(31+6*i,31+6*i,5,5,nian,title_col_style6)
					i+=1
				j+=1
			else:
				if x==processll_[-1]:
					yijian=u"%s意见："%pll['userrole']
					ws.write_merge(26+6*i,26+6*i,0,5,yijian,title_col_style1)
					ws.write_merge(27+6*i,30+6*i,0,5,pll['yijian'],title_col_style10)
					shen=u"签名：%s"%pll['qianming']
					if pll['riqi']=="":
						nian=u"      年   月   日"
					else:
						nian=u"%s年%s月%s日"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
					ws.write_merge(31+6*i,31+6*i,0,3,shen,title_col_style3)
					ws.write_merge(31+6*i,31+6*i,4,5,nian,title_col_style6)
					i+=1
				else:
					if j%2==0:
						yijian=u"%s意见："%pll['userrole']
						ws.write_merge(26+6*i,26+6*i,0,2,yijian,title_col_style1)
						ws.write_merge(27+6*i,30+6*i,0,2,pll['yijian'],title_col_style10)
						shen=u"签名：%s"%pll['qianming']
						if pll['riqi']=="":
							nian=u"      年   月   日"
						else:
							nian=u"%s年%s月%s日"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
						ws.write_merge(31+6*i,31+6*i,0,1,shen,title_col_style3)
						ws.write_merge(31+6*i,31+6*i,2,2,nian,title_col_style6)
					else:
						yijian=u"%s意见："%pll['userrole']
						ws.write_merge(26+6*i,26+6*i,3,5,yijian,title_col_style1)
						ws.write_merge(27+6*i,30+6*i,3,5,pll['yijian'],title_col_style10)
						shen=u"签名：%s"%pll['qianming']
						if pll['riqi']=="":
							nian=u"      年   月   日"
						else:
							nian=u"%s年%s月%s日"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
						ws.write_merge(31+6*i,31+6*i,3,4,shen,title_col_style3)
						ws.write_merge(31+6*i,31+6*i,5,5,nian,title_col_style6)
						i+=1
					j+=1
						
						
def filltable(header, data, ws,field,disacols,tables):
	style = Fields_date_css()
	field_style=Fields_css()
	title_style=Title_css()
	title_col_style=title_col_css()
	j=0
	i=0
	while j<len(header):
		if field[j] not in disacols:
			if field[j]=='Parent':
				ws.write(1,i,u'%s'%_("ParentID"),title_col_style)
				ws.write(1,i+1,u'%s'%_("ParentName"),title_col_style)
				ws.col(i).width=0x1000
				ws.col(i+1).width=0x1000
				i+=2
			else:
				ws.write(1,i,u'%s'%header[j],title_col_style)
				ws.col(i).width=0x1000
				i+=1
		j+=1
	ws.write_merge(0,0,0,i-1,u'%s'%tables,title_style)
	line=2
	column=0
	ll=[]
	try:
		data_=eval(data)
	except:
		data_=data
	for i in data_:
		column=0
		for k in field:
			if k not in disacols:
				try:
						
					if (type(i[k])==int) or (type(i[k])==datetime.date):
						i[k]=str(i[k])
					try:
						if i[k].find("src='/media/img/icon-yes.gif'")!=-1:
							i[k]=u'%s'%_("Yes")
						if i[k].find("src='/media/img/icon-no.gif'")!=-1:
							i[k]=u'%s'%_("No")
						if ">" in i[k]:
							i[k]=getvaluefromhtml(i[k])
					except:
						pass
					if k=='Parent':
						dept=i[k].split(" ")
						if len(dept)>1:
							ws.write(line, column, dept[0],field_style)
							if len(dept)>2:
								depp=dept[1].decode('utf-8')+u" "+dept[2].decode('utf-8')
								ws.write(line, column+1,depp,field_style )
							else:
								ws.write(line, column+1, dept[1].decode('utf-8'),field_style)
						else:
							ws.write(line, column, 0,field_style)
							ws.write(line, column+1, "",field_style)
						column+=2
						continue
					if type(i[k])==datetime.datetime:
						ws.write(line, column, i[k], style)
					else:
						if i[k]==None or i[k]=='None':
							i[k]=''
						try:
							i[k] = i[k].decode('utf-8')
						except:
							i[k]=i[k]
							
						ws.write(line, column, i[k],field_style)
				except:
					ws.write(line, column,'',field_style)
				column+=1
		line+=1

def filltableDept(header, data, ws,field,disacols,fieldNames,tables):
	style = Fields_date_css()
	field_style=Fields_css()
	title_style=Title_css()
	title_col_style=title_col_css()
	j=0
	h=len(header)-1
	while j<len(header):
		if field[j] not in disacols and j not in [0,1,h]:
			ws.write(1,j,u'%s'%header[j],title_col_style)
			ws.write(2,j,u'%s'%field[j],title_col_style)
			ws.col(j).width=0x1000
		elif j in [0,1,h] and field[j] not in disacols:
			ws.write_merge(1,2,j,j,u'%s'%header[j],title_col_style)
		j+=1
	ws.write_merge(0,0,0,h,u'%s'%tables,title_style)
	line=3
	column=0
	ll=[]
	try:
		data_=eval(data)
	except:
		data_=data
	for i in data_:
		column=0
		for k in fieldNames:
			if k not in disacols:
				try:
						
					if (type(i[k])==int) or (type(i[k])==datetime.date):
						i[k]=str(i[k])
					try:
						if i[k].find("src='/media/img/icon-yes.gif'")!=-1:
							i[k]=_("Yes")
						if i[k].find("src='/media/img/icon-no.gif'")!=-1:
							i[k]=_("No")
						if ">" in i[k]:
							i[k]=getvaluefromhtml(i[k])
					except:
						pass
					if k=='Parent':
						dept=i[k].split(" ")
						if len(dept)>1:
							ws.write(line, column, dept[0],field_style)
							if len(dept)>2:
								depp=dept[1].decode('utf-8')+u" "+dept[2].decode('utf-8')
								ws.write(line, column+1,depp,field_style)
							else:
								ws.write(line, column+1, dept[1].decode('utf-8'),field_style)
						else:
							ws.write(line, column, 0,field_style)
							ws.write(line, column+1, "",field_style)
						column+=2
						continue
					if type(i[k])==datetime.datetime:
						ws.write(line, column, i[k], style)
					else:
						if i[k]==None or i[k]=='None':
							i[k]=''
						try:
							i[k] = i[k].decode('utf-8')
						except:
							i[k]=i[k]
							
						ws.write(line, column, i[k],field_style)
				except:
					ws.write(line, column,'',field_style)
				column+=1
		line+=1

def filltable1(header, data, ws,field,disacols,tables):
	if GetParamValue('opt_basic_approval','1')=='0' or GetParamValue('opt_basic_approval','1')==0:
		disacols.append("process")
	style = Fields_date_css()
	field_style=Fields_css()
	title_style=Title_css()
	title_col_style=title_col_css()
	j=0
	i=0
	while j<len(header):
		if field[j] not in disacols:
			ws.write(1,i,u'%s'%header[j],title_col_style)
			ws.col(i).width=0x1000
			i+=1
		j+=1
	ws.write_merge(0,0,0,i-1,tables,title_style)
	line=2
	column=0
	ll=[]
	try:
		data_=eval(data)
	except:
		data_=data
	role=userRoles.objects.all()
	xl={}
	xz=[]
	for i in role:
		xl[i.roleid]=i.roleName
		xz.append(i.roleid)
	for i in data_:
		column=0
		for k in field:
			if k not in disacols:
				try:
					#if k=='process':
					#	if i[k]!='None' and i[k] and i[k]!='':
					#		for it in xz:
					#			dd=","+xl[it]+","
					#			cc=","+str(it)+","
					#			i[k]=i[k].replace(cc,dd)
					#		i[k]=i[k][1:-1]
					#		i[k]=i[k].replace(","," --> ")
					if (type(i[k])==int) or (type(i[k])==datetime.date):
						i[k]=str(i[k])
					if type(i[k])==datetime.datetime:
						ws.write(line, column, i[k], style)
					else:
						if i[k]==None or i[k]=='None':
							i[k]=''
						try:
							i[k] = i[k].decode('utf-8')
						except:
							i[k]=i[k]
						if k=='process':
							tmp = i[k]
							tmp = tmp.replace("<font color='red'>",'')
							tmp = tmp.replace("</font>",'')
							ws.write(line, column, tmp,field_style)
						else:
							ws.write(line, column, i[k],field_style)
				except:
					ws.write(line, column,'',field_style)
				column+=1
		line+=1

def Title_css():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 18*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def Title_css2():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 18*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def Title_css1():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 18*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0
	borders.right = 0
	borders.top = 0
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x16
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css1():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_LEFT#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css7():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0
	borders.bottom = 0
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css3():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0
	borders.right = 0
	borders.top = 0
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css4():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css5():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0
	borders.top = 0
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css6():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0
	borders.right = 0x11
	borders.top = 0
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css8():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_RIGHT#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0
	borders.right = 0x11
	borders.top = 0
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css9():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_LEFT#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0
	borders.right = 0
	borders.top = 0
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css10():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_LEFT#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0
	borders.right = 0x11
	borders.top = 0
	borders.bottom = 0
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def title_col_css11():#表头样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 10*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x16
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def Fields_css():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def Fields_css2():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 10*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def footer_css():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_LEFT#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = True
	font.height = 10*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def footer_css2():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_LEFT#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = True
	font.height = 10*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def footer_css3():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_RIGHT#左右居中
	al.vert = Alignment.VERT_BOTTOM#上下居中

	font = Font()
	font.name = 'Arial'
	font.bold = True
	font.height = 10*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0
	borders.right = 0x11
	borders.top = 0
	borders.bottom = 0
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def footer_css4():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = True
	font.height = 10*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = 'general'

	return style

def Fields_date_css():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = "YYYY/MM/DD hh:mm:ss"
	return style

def Fields_date_css2():#内容样式
	al = Alignment()
	al.horz = Alignment.HORZ_CENTER#左右居中
	al.vert = Alignment.VERT_CENTER#上下居中
	al.wrap = Alignment.WRAP_AT_RIGHT#自动换行

	font = Font()
	font.name = 'Arial'
	font.bold = False
	font.height = 11*0x14
	
	pattern=Pattern()
	pattern.pattern=1
	pattern.pattern_fore_colour=0x01
	pattern.pattern_back_colour=0x01
	
	borders = Borders()
	borders.left = 0x11
	borders.right = 0x11
	borders.top = 0x11
	borders.bottom = 0x11
	
	style = XFStyle()
	style.pattern=pattern
	style.font=font
	style.height=200
	style.alignment = al
	style.borders = borders
	style.num_format_str = "YYYY/MM/DD hh:mm:ss"
	return style

def exportComposite(request):
	fieldNames,fieldCaptions,rt=ConstructScheduleFields2(request)
	flag=request.GET.get('flag','')
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserID__in',"")
	q=request.GET.get('q',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')+datetime.timedelta(days=1)
	iCount=0
	ot=['DeptID','PIN']
	r=  getComposite(request,deptIDs,userIDs,flag,isContainedChild,st,et,ot,q)
	#print r,type(r)
	return r['datas']
	
def gettransactiondata(request,offset):
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserID__in',"")
	q=request.GET.get('q',"")
	st=request.GET.get('TTime__gte','')
	et=request.GET.get('TTime__lt','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')+datetime.timedelta(days=1)
	using_m=request.GET.get('mod_name','att')
	iCount=0
	limit=20000
	if q!='':
		userlist=[]
		emp=employee.objects.filter(Q(PIN=q)|Q(EName=q))
		if request.user.is_superuser or request.user.is_alldept:
			deptlist=[]
		else:
			deptlist=getAllAuthChildDept(dept.DeptID,request)
		deptids=[]
		for e in emp:
			if e.Dept().DeptID not in deptlist:
				userlist.append(e.id)
		trans=transactions.objects.filter(UserID__in=userlist,TTime__gte=st,TTime__lt=et)
				
	else:
		if len(deptIDs)>0:
			if isContainedChild=='1':
				dept=department.objByID(deptIDs)
				if request.user.is_superuser or request.user.is_alldept:
					deptids=getAllAuthChildDept(dept.DeptID,request)
				else:
					deptids=[]
					deptids_Auth=userDeptList(request.user) #获得用户的授权部门
					deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
					for i in deptids_Subordinate:
						if i in deptids_Auth:
							deptids.append(i)
			else:
				deptids=deptIDs
		else:
			if request.user.is_superuser or request.user.is_alldept:
				deptids=list(department.objects.all().exclude(DelTag=1).values_list('DeptID',flat=True))
			else:
				deptids=userDeptList(request.user) 
		trans=transactions.objects.filter(UserID__DeptID__in=deptids,TTime__gte=st,TTime__lt=et)
	trans=transactions.objects.filter(TTime__gte=st,TTime__lt=et)
	pType=settings.MOD_DICT[using_m]
	trans=trans.filter(Q(purpose=None)|Q(purpose=pType))
	p=Paginator(trans, limit)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	data=[]
	for t in pp.object_list:
		d={}
		d['id']=t.id
		d['DeptID']=t.employee().Dept().DeptID
		d['DeptName']=t.employee().Dept().DeptName
		d['PIN']=t.employee().PIN
		d['EName']=t.employee().EName
		d['TTime']=t.TTime.strftime('%Y-%m-%d %H:%M:%S')
		d['State']=getRecordState(t.State)
		sn=t.Device()
		if sn:
			d['Device']=sn.Alias
		else:
			d['Device']=''
		data.append(d.copy())
	return data

@login_required
def calcReport(request):
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')
	r=CalcReportItem(request,deptIDs,userIDs,st,et)
	return r['datas']

@login_required
def calcshiftReport(request):
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')
	r=CalcAttShiftsReportItem(request,deptIDs,userIDs,st,et)
	return r['datas']

def calcAttExceptionReport(request):
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')
	r=CalcAttShiftsReportItem(request,deptIDs,userIDs,st,et,1)
	return r['datas']

@login_required
def calcdailyReport(request):
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')
	r=CalcReportItem(request,deptIDs,userIDs,st,et,1)
	return r['datas']

@login_required
def calcLeaveReport(request):
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')
	r=CalcLeaveReportItem(request,deptIDs,userIDs,st,et)
	return r['datas']

@login_required
def calcLeaveYReport(request):
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	calcyear=request.GET.get('y','')
	if calcyear=='':
		calcyear=now.year
	else:
		calcyear=int(calcyear)
	st=datetime.datetime(calcyear,1,1,0,0,0)
	et=datetime.datetime(calcyear,12,31,23,59,59)
	r=CalcLeaveReportItem(request,deptIDs,userIDs,st,et)
	return r['datas']

@login_required
def calcExcepDaily(request):
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')
#	r=CalcReportItem(request,deptIDs,userIDs,st,et,1)
	r=CalcReportItemEx(request,deptIDs,userIDs,st,et,3)
	r=cacleExcepDaily(request,r,1)
	return r['datas']

@login_required
def expsearchRecords(request):
	#isContainedChild=request.GET.get("isContainChild","0")
	#deptIDs=request.GET.get('deptIDs',"")
	#userIDs=request.GET.get('UserIDs',"")
	#st=request.GET.get('startDate','')
	#et=request.GET.get('endDate','')
	#st=datetime.datetime.strptime(st,'%Y-%m-%d')
	#et=datetime.datetime.strptime(et,'%Y-%m-%d')
	#et=et+datetime.timedelta(1)
	#re=getsearchRecordsr(request,isContainedChild,deptIDs,userIDs,st,et)
	re=getsearchRecordsr(request,'original_records')
	return re['datas']

@login_required
def iacc_MonitorExport(request):#:_(u'监控记录表'),
	SNs=request.GET.get('SNs',"")
	Object=request.GET.get('Object',"")
	st=request.GET.get('startDate','')
	et="%s 23:59:59"%request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
	r=getIacc_MonitorReportItem(request,SNs,Object,st,et)
	
	return r['datas']
@login_required
def iacc_AlarmExport(request):#:_(u'报警记录表'),
	SNs=request.GET.get('SNs',"")
	Object=request.GET.get('Object',"")
	st=request.GET.get('startDate','')
	et="%s 23:59:59"%request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
	r=getIacc_AlarmReportItem(request,SNs,Object,st,et)
	
	return r['datas']
@login_required
def iacc_UserRightsExport(request):#:_(u'用户权限表'),
	SNs=request.GET.get('SNs',"")
	st=request.GET.get('startDate','')
	et="%s 23:59:59"%request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
	r=getIacc_UserRightsReportItem(request,SNs,st,et)
	
	return r['datas']
@login_required
def iacc_RecordDetailsExport(request):#:_(u'记录明细'),
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et="%s 23:59:59"%request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
	r=getIacc_RecordDetailsReportItem(request,deptIDs,userIDs,st,et)
	
	return r['datas']
@login_required
def iacc_SummaryRecordExport(request):#:_(u'记录汇总'),
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et="%s 23:59:59"%request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
	r=getIacc_SummaryRecordReportItem(request,deptIDs,userIDs,st,et)
	
	return r['datas']
@login_required
def iacc_EmpUserRightsExport(request):#:_(u'用户权限明细'),
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et="%s 23:59:59"%request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
	r=getIacc_EmpUserRightsReportItem(request,deptIDs,userIDs,st,et)
	return r['datas']
@login_required
def iacc_EmpDeviceExport(request):#:_(u'用户设备'),
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et="%s 23:59:59"%request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
	r=getIacc_EmpDeviceReportItem(request,deptIDs,userIDs,st,et)
	return r['datas']

@login_required
def departmentreportItemExport(request):#:_(u'用户设备'),
	deptIDs=request.GET.get('deptIDs',"")
	isContainChild=request.GET.get('isContainChild',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')
	r=departmentreportItem(request,deptIDs,isContainChild,st,et)
	return r['datas']

@login_required
def exportemployee_finger(request):#:_(u'用户设备'),
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	q=request.GET.get('q','')
	now=datetime.datetime.now()
	if st=='':
		st=datetime.datetime(now.year,now.month,1,0,0)
	else:
		st=datetime.datetime.strptime(st,"%Y-%m-%d")
	if et=='':
		et=now
	else:
		et=datetime.datetime.strptime(et,"%Y-%m-%d")
		et=et+datetime.timedelta(1)
	q=unquote(q)
	r=getemployee_finger(request,isContainedChild,deptIDs,userIDs,st,et,q)
	return r['datas']


@login_required
def exportdepartment_finger(request):#:_(u'用户设备'),
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	r=getdepartment_finger(request,isContainedChild,deptIDs)
	return r['datas']
	
	
@login_required
def exportdevice_assignment(request):#:_(u'用户设备'),
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	q=request.GET.get('q','')
	q=unquote(q)
	r=getdevice_assignment(request,isContainedChild,deptIDs,q)
	return r['datas']
	
	
@login_required
def exportdaily_devices(request):#:_(u'用户设备'),
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	q=request.GET.get('q','')
	q=unquote(q)
	r=getdaily_devices(request,isContainedChild,deptIDs,q)
	return r['datas']
	
	
@login_required
def exportEarlystAndLastest(request):#:_(u'用户设备'),
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	q=request.GET.get('q','')
	now=datetime.datetime.now()
	if st=='':
		st=datetime.datetime(now.year,now.month,1,0,0)
	else:
		st=datetime.datetime.strptime(st,"%Y-%m-%d")
	if et=='':
		et=now
	else:
		et=datetime.datetime.strptime(et,"%Y-%m-%d")
		et=et+datetime.timedelta(1)
	q=unquote(q)
	r=getEarlystAndLastest(request,isContainedChild,deptIDs,userIDs,st,et,q)
	return r['datas']
	
@login_required
def exportforget_records(request):#:_(u'用户设备'),
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	q=request.GET.get('q','')
	now=datetime.datetime.now()
	if st=='':
		st=datetime.datetime(now.year,now.month,1,0,0)
	else:
		st=datetime.datetime.strptime(st,"%Y-%m-%d")
	if et=='':
		et=now
	else:
		et=datetime.datetime.strptime(et,"%Y-%m-%d")
		et=et+datetime.timedelta(1)
	q=unquote(q)
	r=getforgetRecords(request,isContainedChild,deptIDs,userIDs,st,et,q)
	return r['datas']

def searchnoshifts(request):
	from mysite.iclock.shiftsview import getNoshift
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserID__in',"")
	q=request.GET.get('q',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')
	q=unquote(q)
	
	r=getNoshift(request,deptIDs,userIDs,isContainedChild,st,et,q)
	return r['datas']

@login_required
def export_meeting_sign_report(request):
	deptIDs=request.GET.get('deptIDs',"")
	q=request.GET.get('q','')
	r=getmeetingsign(request,deptIDs,q)
	return r['datas']

@login_required
def export_meeting_not_sign_report(request):
	deptIDs=request.GET.get('deptIDs',"")
	q=request.GET.get('q','')
	r=getmeetingnotsign(request,deptIDs,q)
	return r['datas']

@login_required
def export_meeting_report(request):
	deptIDs=request.GET.get('deptIDs',"")
	q=request.GET.get('q','')
	r=getmeetreport(request,deptIDs,q)
	return r['datas']
@login_required
def export_meeting_user_report(request):
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	q=request.GET.get('q','')	
	r=getmeetuserreport(request,isContainedChild,deptIDs,userIDs,st,et,q)
	return r['datas']
@login_required
def export_meeting_user_late_report(request):
	deptIDs=request.GET.get('deptIDs',"")
	q=request.GET.get('q','')	
	r=getmeetuserlatereport(request,deptIDs,q)
	return r['datas']
@login_required
def export_meeting_room_report(request):
	q=request.GET.get('q','')
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	if st and et:
		st +=' 00:00:00'
		et +=' 23:59:59'
		deptIDs=request.GET.get('deptIDs',"")
		r=getmeetroomreport(request,deptIDs,st,et,q)
		return r['datas']
	else:
		return []

def export_calcallreport(request):
	from mysite.iclock.myreportview import calcallreport
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	if st and et:
		st +=' 00:00:00'
		et +=' 23:59:59'
		deptIDs=request.GET.get('deptIDs',"")
		isContainedChild=request.GET.get("isContainChild","0")
		r = calcallreport(request,isContainedChild,deptIDs,st,et)
		datas = r['datas']
		datas.extend([r['userData']])
		return datas
	else:
		return []

def export_calcexceptionreport(request):
	from mysite.iclock.myreportview import calcexceptionreport
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	q=request.GET.get('q','')
	if st and et:
		st +=' 00:00:00'
		et +=' 23:59:59'
		st = datetime.datetime.strptime(st,'%Y-%m-%d %H:%M:%S')
		et = datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
		deptIDs=request.GET.get('deptIDs',"")
		isContainedChild=request.GET.get("isContainChild","0")
		r = calcexceptionreport(request,isContainedChild,deptIDs,st,et,q)
		datas = r['datas']
		return datas
	else:
		return []

def export_backreport(request):
	from mysite.iclock.myreportview import backreport
	et=request.GET.get('endDate','')
	q=request.GET.get('q','')
	if et:
		et +=' 23:59:59'
		et = datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
		deptIDs=request.GET.get('deptIDs',"")
		isContainedChild=request.GET.get("isContainChild","0")
		r = backreport(request,isContainedChild,deptIDs,'',et,q)
		datas = r['datas']
		return datas
	else:
		return []

def export_allexceptionreport(request):
	from mysite.iclock.myreportview import allexceptionreport
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	if st and et:
		st +=' 00:00:00'
		et +=' 23:59:59'
		st = datetime.datetime.strptime(st,'%Y-%m-%d %H:%M:%S')
		et = datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
		deptIDs=request.GET.get('deptIDs',"")
		isContainedChild=request.GET.get("isContainChild","0")
		r = allexceptionreport(request,isContainedChild,deptIDs,st,et)
		datas = r['datas']
		return datas
	else:
		return []

def export_jiezhuanreport(request):
	from mysite.iclock.myreportview import jiezhuanreport
	deptIDs=request.GET.get('deptIDs',"")
	isContainedChild=request.GET.get("isContainChild","0")
	q=request.GET.get('q','')
	r = jiezhuanreport(request,isContainedChild,deptIDs,q)
	datas = r['datas']
	return datas