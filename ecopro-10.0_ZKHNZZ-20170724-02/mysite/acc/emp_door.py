#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import string
from django.contrib import auth
from django.shortcuts import render_to_response,render
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context, RequestContext
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from mysite.iclock.models import *
from mysite.acc.models import *
#from mysite.iclock.datasproc import *
from django.core.paginator import Paginator
#from mysite.iclock.datas import *
#from mysite.core.menu import *
from mysite.core.tools import *
from mysite.core.cmdproc import *
from mysite.iclock.models import *
#from django.shortcuts import render


@login_required
def index(request):#门禁权限组设置--按人员设置
	if request.method=='GET':
		tmpFile='acc/'+'emp_door.html'
		tmpFile=request.GET.get('t', tmpFile)
		cc={}


		settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
		limit= int(request.GET.get('l', settings.PAGE_LIMIT))
		colmodels= [
				{'name':'id','hidden':True},
				{'name':'PIN','index':'PIN','width':80,'label':unicode(employee._meta.get_field('PIN').verbose_name),'frozen':True},
				{'name':'EName','width':80,'label':unicode(employee._meta.get_field('EName').verbose_name),'frozen': True},
				{'name':'Gender','width':40,'search':False,'label':unicode(employee._meta.get_field('Gender').verbose_name)},
				{'name':'DeptName','index':'DeptID__DeptName','width':200,'label':unicode(_('department name'))},
				{'name':'Card','width':60,'label':unicode(employee._meta.get_field('Card').verbose_name)},
#				{'name':'Title','width':60,'label':unicode(employee._meta.get_field('Title').verbose_name)},
				#{'name':'level_detail','sortable':False,'width':120,'label':unicode(_(u'操作'))},
			]
		
		colmodels_level= [
				{'name':'id','hidden':True},
				{'name':'door_no','index':'','width':60,'label':unicode(AccDoor._meta.get_field('door_no').verbose_name)},
				{'name':'door_name','sortable':False,'index':'','width':150,'label':unicode(AccDoor._meta.get_field('door_name').verbose_name)},
				{'name':'device','sortable':False,'index':'','width':250,'label':unicode(AccDoor._meta.get_field('device').verbose_name)}
				
			]
		
		
		cc['limit']=limit
		cc['colModel']=dumps1(colmodels)
		cc['colModel_level']=dumps1(colmodels_level)
		request.model=level


		return render(request,tmpFile,cc)#render_to_response(tmpFile,cc,RequestContext(request, {}))



def get_level_emp(request):
	#print request.POST
	id=request.GET.get('id')
	limit= int(request.POST.get('rows', 0))
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	objs=level_emp.objects.filter(UserID=id)
	p=Paginator(objs, limit)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	objs=pp.object_list
	re=[]
	Result={}
	Result['datas']=re
	for t in objs:
		d={}
		d['id']=t.id

		d['name']=t.level.name
		d['tz']=t.level.timeseg.Name
		
		re.append(d.copy())
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
	return getJSResponse(rs)
	

