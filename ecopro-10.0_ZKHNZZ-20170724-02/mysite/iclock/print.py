#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from django.db import models
from mysite.iclock.iutils import *
from django.conf import settings
from django.utils.translation import ugettext_lay as _
from mysite.iclock.datas import *
import datetime
from mysite.iclock.dataview import *
from mysite.iclock.templatetags.iclock_tags import *
from reportlab.platypus import *
from reportlab.lib.styles import PropertySet, getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.flowables import PageBreak
import os
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.codecharts import KutenRowCodeChart, hBoxText
from reportlab.pdfbase import pdfmetrics, cidfonts
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
import operator
from mysite.iclock.printCalc import *
from reportlab.lib.units import inch,cm
from reportlab.rl_config import defaultPageSize
from reportlab.lib.pagesizes import letter
from reportlab.lib.testutils import  outputfile
from mysite.iclock.reports import getLeaveClass
from mysite.iclock.jqgrid import *
from mysite.iclock.newiaccess import *
from mysite.iclock.export import *
from mysite.iclock.jqgrid import *

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
		
		self.style1=ParagraphStyle(
				name="base",
				fontName="STSong-Light",
				leading=12,
				leftIndent=0,
				firstLineIndent=0,
				spaceBefore =100,
				fontSize=24,
				)
		self.ps_report_right = ParagraphStyle(name='normal',
									fontName='STSong-Light',
									fontSize=30,
									leading=10,
									spaceAfter=10,
									alignment=TA_RIGHT,
									)
		self.ps_report_center1 = ParagraphStyle(name='normal',
									fontName='STSong-Light',
									fontSize=12,
									leading=10,
									spaceBefore=10,
									spaceAfter=10,
									leftIndent=350,
									alignment=TA_CENTER,
									)
		
		self.ps_report_center = ParagraphStyle(name='normal',
									fontName='STSong-Light',
									fontSize=14,
									leading=10,
									spaceAfter=0,
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
		canvas.drawString(first, 0.25 * inch,"%s    %s"%(_(u"制表人:"),self.user))
		canvas.drawString(second, 0.25 * inch,"%s    %s"%(_(u"制表时间:"),aa))
		canvas.drawString(third, 0.25 * inch,"%s    %s"%(_(u"页码:"),doc.page))
		canvas.drawString(fourth, 0.25 * inch,"%s    %s%s"%(_(u"每页:"),self.pagelist,_(u"条")))
		canvas.restoreState()
		
	def printReports(self,request,tables,header,field,datas,disacols,exportname,pagelist=24):
		user_id=request.user.id
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="%s-%s.pdf"'%(exportname,user_id)
		self.user=request.user
		lx=[]
		title=[]
		for h in range(len(header)):
			if field[h] not in disacols:
				title.append(header[h])
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
					ll.append(d[f])
			lx.append(ll)
			lens+=1
		t1 = Table(lx)
		t1.setStyle(self.GRID_STYLE1)
		lst.append(t1)
		lst.append(Spacer(5,5))
		lst.append(PageBreak())
		self.tableName=exportname
		self.lst=lst
		width=.25*5*cm
		if width<29.7*cm:
			width=29.7*cm
		height=21*cm
		A_p=(width,21*cm)
		self.AP=A_p
		c = SimpleDocTemplate(response,pagesize=A_p,bottomMargin=30,topMargin=30).build(self.lst,  onFirstPage=self.myFirstPageReport,onLaterPages=self.myFirstPageReport)
		return response

