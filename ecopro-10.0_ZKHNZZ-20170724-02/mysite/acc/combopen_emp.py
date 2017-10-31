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
def index(request):
	if request.method=='GET':
		tmpFile='acc/'+'combopen.html'
		tmpFile=request.GET.get('t', tmpFile)
		cc={}


		settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
		limit= int(request.GET.get('l', settings.PAGE_LIMIT))
		colmodels_level=combopen_emp.colModels()
		colmodels= combopen.colModels()
		
		
		cc['limit']=limit
		cc['colModel']=dumps1(colmodels)
		cc['colModel_level']=dumps1(colmodels_level)
		request.model=level


		return render(request,tmpFile,cc)#render_to_response(tmpFile,cc,RequestContext(request, {}))



def get_combopen_emp(request):
	#print request.POST
	id=request.GET.get('id')
	limit= int(request.POST.get('rows', 0))
	sidx=request.POST.get('sidx')
	sord=request.POST.get('sord')
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	if sord=='desc':
                objs=combopen_emp.objects.filter(combopen=id).exclude(UserID__DelTag=1).order_by('-'+sidx)
        else:
                objs=combopen_emp.objects.filter(combopen=id).exclude(UserID__DelTag=1).order_by(sidx)
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
		d['PIN']=t.UserID.PIN
		d['EName']=t.UserID.EName
		d['DeptName']=t.UserID.Dept().DeptName
		
		
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
	
@login_required	
def SaveEmployee_combopen(request):
	ID=request.GET.get('id','')
	deptIDs=request.POST.get('deptIDs',"")
	userIDs=request.POST.get('UserIDs',"")
	isContainedChild=request.POST.get('isContainChild',"")
	if ID=='':
	    return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})
	#ID=ID.split(',')   
	if userIDs == "":
		isAllDept=0
		deptidlist=deptIDs.split(',')
		if isContainedChild=="1":
			for d in deptidlist:#支持选择多部门
				if(request.user.is_superuser) or ( request.user.is_alldept):
					if department.objByID(int(d)).parent==0:
						isAllDept=1
						deptids=[]
						break
				if int(d) not in deptids:
					deptids+=getAllAuthChildDept(d,request)
		else:
			deptids=deptidlist
			
		if isAllDept==1:
		    emps=employee.objects.all().exclude(OffDuty=1).exclude(DelTag=1)
		else:
		    emps=employee.objects.filter(DeptID__in=deptids).exclude(OffDuty=1).exclude(DelTag=1)
		    
	else:
		userids=userIDs.split(',')
		emps=employee.objects.filter(pk__in=userids)
	for emp in emps:
		try:
			combopen_emp.objects.get(UserID=emp).delete()
		except:
			pass
		sql,params=getSQL_insert_new(combopen_emp._meta.db_table,combopen_id=ID,UserID_id=emp.id)
		try:
			customSql(sql,params)
		except Exception,e:
			#print e
			pass
		try:
			tmp=acc_employee.objects.get(UserID=emp)
			tmp.morecard_group_id=ID
			tmp.save()
			emp_acc=employee.objects.get(id = tmp.UserID_id)
			emp_acc=u'%s'%emp_acc
			adminLog(time=datetime.datetime.now(),User=request.user,object=emp_acc, model=combopen_emp._meta.verbose_name, action=_(u"添加人员")).save(force_insert=True)#
		except:
			acc_employee(UserID=emp,morecard_group_id=ID).save()

		
	return getJSResponse({"ret":0,"message":u"%s"%_('Operation Successful')})

