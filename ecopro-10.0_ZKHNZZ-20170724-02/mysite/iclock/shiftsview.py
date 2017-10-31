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
from mysite.base.models import *
from mysite.iclock.datasproc import *
from django.core.paginator import Paginator
from mysite.iclock.datas import *
@login_required
def index(request):
	return render(request,'search_shifts.html',{})	
#	return render_to_response('search_shifts.html',	 {},RequestContext(request, {}))	





@login_required
def searchComposite(request):
	"""综合排班查询"""
	from math import ceil
	if request.method=="GET":
		flag=request.GET.get('flag','')
		settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
		limit= int(request.GET.get('l', settings.PAGE_LIMIT))
		if flag=='':
			fieldNames,fieldCaptions,rt=ConstructScheduleFields()
			disabledCols=FetchDisabledFields(request.user,'searchComposite')
			r=[]
			it=0
			for field in fieldCaptions:
				if field=='userid' or field=='UserID':
					r.append({"name":"UserID",'hidden':True})
				else:
					r.append({"name":field,'sortable':False,'label':rt[it],'width':120})
				it=it+1
			rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+","+""""limit":"""+str(limit)+"""}"""
			return getJSResponse(rs)
		else:
			fieldNames,fieldNames,rt=ConstructScheduleFields2(request)
			disabledCols=FetchDisabledFields(request.user,flag)
			r=[]
			it=0
			w=100
			for field in fieldNames:
				if field=='id':
					r.append({"name":"id",'hidden':True,'frozen':True})
				elif field=='userid' or field=='UserID':
					r.append({"name":"UserID",'hidden':True,'frozen':True})
				else:
					if it>=6:
						w=100
						r.append({"name":field,'sortable':False,'label':rt[it],'width':w})
					else:
						r.append({"name":field,'sortable':False,'label':rt[it],'width':120,'frozen':True})
				
				it=it+1
			if flag=='shift3':
				r.insert(6,{"name":'details','sortable':False,'label':u'%s'%(_(u'操作')),'width':50})
			rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+","+""""limit":"""+str(limit)+"""}"""

			return getJSResponse(rs)
			
	else:
		flag=request.GET.get('flag','')
		isContainedChild=request.GET.get("isContainChild","0")
		deptIDs=request.GET.get('deptIDs',"")
		userIDs=request.GET.get('UserID__in',"")
		q=request.GET.get('q',"")
		st=request.GET.get('startDate','')
		et=request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d')+datetime.timedelta(days=1)
		ot=['DeptID','PIN','Workcode']
		q=unquote(q)
		if (et-st).days>60:
			et=st+datetime.timedelta(days=60)
		try:
			Result= getComposite(request,deptIDs,userIDs,flag,isContainedChild,st,et,ot,q)
		except:
			import traceback;traceback.print_exc()
		rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
		return getJSResponse(rs)

def getComposite(request,deptIDs,userIDs,flag,isContainedChild,st,et,ot,q):
	iCount=0
	if q:
		if deptIDs!='':
			deptidlist=deptIDs.split(',')
			deptids=deptidlist
			if isContainedChild=="1": #是否包含下级部门
				deptids=[]
				for d in deptidlist:#支持选择多部门
					if int(d) not in deptids :
						deptids+=getAllAuthChildDept(d,request)
			
			objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1,DelTag__lt=1).filter(Q(PIN__contains=q)|Q(PIN__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
		else:
			objs=employee.objects.filter(OffDuty__lt=1,DelTag__lt=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
	elif len(userIDs)>0 and userIDs!='null':
		ids=userIDs.split(',')
		#iCount=len(ids)
		objs=employee.objects.filter(id__in=ids).exclude(OffDuty=1).exclude(DelTag=1).order_by(*ot)
		
	elif len(deptIDs)>0:
		deptidlist=deptIDs.split(',')
		deptids=deptidlist
		alldept_flag=False
		if isContainedChild=="1": #是否包含下级部门
			deptids=[]
			if 1 in deptidlist: #如果选择的是总公司，理解为是全部部门
				if(request.user.is_superuser) or ( request.user.is_alldept):
					alldept_flag=True
			
			if not alldept_flag:
				for d in deptidlist:#支持选择多部门
					if int(d) not in deptids :
						deptids+=getAllAuthChildDept(d,request)
		if alldept_flag:				
			objs=employee.objects.all().exclude(OffDuty=1).exclude(DelTag=1).order_by(*ot)
		else:
			objs=employee.objects.filter(DeptID__in=deptids).exclude(OffDuty=1).exclude(DelTag=1).order_by(*ot)
	else:
		if(request.user.is_superuser) or ( request.user.is_alldept):
			objs=employee.objects.all().exclude(OffDuty=1).exclude(DelTag=1).order_by(*ot)
		else:
			deptids=userDeptList(request.user)
			objs=employee.objects.filter(DeptID__in=deptids).exclude(OffDuty=1).exclude(DelTag=1).order_by(*ot)
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 30))
	re=[]
	Result={}
	Result['datas']=re

	if flag=='':
		for id in ids:
			userplan=LoadSchPlanEx(id,True,True)
			l=GetUserScheduler(int(id), st, et, userplan['HasHoliday'])
			d={}
			for t in l:
				d['userid']=id
				d['deptid']=userplan['DeptName']
				d['badgenumber']=userplan['BadgeNumber']
				d['username']=userplan['UserName']
				d['starttime']=t['TimeZone']['StartTime']
				d['endtime']=t['TimeZone']['EndTime']
				d['schname']=t['SchName']
				re.append(d.copy())
#		limit= int(request.POST.get('l', settings.PAGE_LIMIT))
		#page_count =len(re)/limit+1
		page_count =int(ceil(len(re)/float(limit)))


#			if offset>page_count:offet=page_count
		item_count =len(re)
		res=re[(offset-1)*limit:offset*limit]
		Result['item_count']=item_count
		Result['page']=offset
		Result['limit']=limit
		Result['from']=(offset-1)*limit+1
		Result['page_count']=page_count
		Result['datas']=res

	else:
		#ids=ids[(offset-1)*limit:offset*limit]
		p=Paginator(objs, limit,allow_empty_first_page=True)
		iCount=p.count
		if iCount<(offset-1)*limit:
			offset=1
		page_count=p.num_pages
		pp=p.page(offset)
		
		AttRule=LoadAttRule()
		day_off_count=days_off.objects.filter(Q(FromDate__gte=st,FromDate__lte=et)|Q(ToDate__lte=et,ToDate__gte=st)).count()
		holidays=loadHoliday()
		initParams={'AttRule':AttRule,'day_off_count':day_off_count,'Holiday':holidays}
		for emp in pp.object_list:
			t1=datetime.datetime.now()
			userplan=LoadSchPlanEx(emp.id,True,True)
			l=GetUserScheduler(emp, st, et, userplan['HasHoliday'],initParams)
			d={}
			d['id']=emp.id
			d['userid']=emp.id
			d['card']=emp.Card or ''
			d['Workcode'] = emp.Workcode
			d['deptid']=emp.Dept().DeptName
			d['badgenumber']=emp.PIN
			d['username']=emp.EName or ''
			d['total']=0
			mins=0
			rest=0
			tt=0
			if flag=='shift3':#人员排班的数据
				d['details']="""%s %s"""%("<a href='#' onclick='showWorkTime(%s);'><img title='显示排班详情'  src='../media/img/Calendar.png' /></a>"%(emp.id),"<a href='#' onclick='showWorkTime(%s,1);'><img title='显示排班原始数据'  src='../media/img/all.gif' /></a>"%(emp.id))
			for t in l:
				if t['TimeZone']['StartTime']<st or t['TimeZone']['StartTime']>et :
					continue
				dd=str(t['TimeZone']['StartTime'].month)+'-'+str(t['TimeZone']['StartTime'].day)
#					dd=str(t['TimeZone']['StartTime'].day)
				if flag=='shift3':
					if dd in d.keys():
						d[dd]=d[dd]+' '+t['SchName']
					else:
						d[dd]=t['SchName']
				else:
					if dd in d.keys():
						d[dd]=d[dd]+' '+t['TimeZone']['StartTime'].strftime('%H:%M')+'-'+t['TimeZone']['EndTime'].strftime('%H:%M')+'('+t['SchName']+')'
					else:
						d[dd]=t['TimeZone']['StartTime'].strftime('%H:%M')+'-'+t['TimeZone']['EndTime'].strftime('%H:%M')+'('+t['SchName']+')'
				if t['TimeZone']['StartTime'] and t['TimeZone']['EndTime']:
					mins=(t['TimeZone']['EndTime']-t['TimeZone']['StartTime']).total_seconds()/60
					if t['IsCalcRest'] and t['StartRestTime'] and t['EndRestTime']:
						rest=(t['EndRestTime']-t['StartRestTime']).total_seconds()/60
					mins=mins-rest
				tt+=mins
			d['total']=round(float(tt)/60,2)
			re.append(d.copy())

		#page_count =int(ceil(iCount/float(limit)))
		#if offset>page_count:offset=page_count
		item_count =iCount
		Result['item_count']=item_count
		Result['page']=offset
		Result['limit']=limit
		Result['from']=(offset-1)*limit+1
		Result['page_count']=page_count
		Result['datas']=re
	return Result

@login_required
def searchNoShift(request):#未排班人员表
	if request.method=="GET":
		settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
		limit= int(request.GET.get('l', settings.PAGE_LIMIT))
		r=[]
		FieldNames=['userid','deptid','badgenumber','Workcode','username','Title']
		it=0
		FieldCaption=[_("userid"),_('department name'),_('PIN'),_('NewPin'),_('name'),_('Title')]
		for i in range(len(FieldCaption)):
			FieldCaption[i]=u"%s"%FieldCaption[i]
		for field in FieldNames:
			if field=='userid' or field=='UserID':
				r.append({"name":"UserID",'hidden':True})
			elif field=='deptid':
				r.append({"name":field,'sortable':False,'label':FieldCaption[it],'width':120})
			else:
				r.append({"name":field,'sortable':False,'label':FieldCaption[it],'width':120})
			it=it+1
		disabledCols=[]
		rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+","+""""limit":"""+str(limit)+"""}"""
		#rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
		return getJSResponse(rs)
	else:
		isContainedChild=request.GET.get("isContainChild","0")
		deptIDs=request.GET.get('deptIDs',"")
		userIDs=request.GET.get('UserID__in',"")
		q=request.GET.get('q',"")
		st=request.GET.get('startDate','')
		et=request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d')
		q=unquote(q)
		Result=getNoshift(request,deptIDs,userIDs,isContainedChild,st,et,q)
		rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
		return getJSResponse(rs)
	
def getNoshift(request,deptIDs,userIDs,isContainedChild,st,et,q):
	iCount=0
	ids=[]
	if q:
		deptidlist=deptIDs.split(',')
		deptids=deptidlist
		if isContainedChild=="1": #是否包含下级部门
			deptids=[]
			for d in deptidlist:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		ot=['DeptID','PIN','Workcode']
		qs=USER_OF_RUN.objects.filter(UserID__DeptID__in=deptids).exclude(StartDate__gt=et).exclude(EndDate__lt=st).values('UserID')
		qs1=USER_TEMP_SCH.objects.filter(UserID__DeptID__in=deptids,SchclassID__gt=0).filter(ComeTime__gte=st).filter(LeaveTime__lt=et).values('UserID')
		ids=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).exclude(id__in=qs).exclude(id__in=qs1).order_by(*ot)
	elif len(userIDs)>0 and userIDs!='null':
		ids=userIDs.split(',')
		iCount=len(ids)
		ot=['DeptID','PIN']
		tmp_ids=USER_OF_RUN.objects.filter(UserID__in=ids).exclude(StartDate__gt=et).exclude(EndDate__lt=st).values_list('UserID',flat=True)
		ids=employee.objects.filter(id__in=ids).exclude(id__in=tmp_ids).exclude(OffDuty=1).exclude(DelTag=1).order_by(*ot)

	elif len(deptIDs)>0:
		deptidlist=deptIDs.split(',')
		deptids=deptidlist
		if isContainedChild=="1": #是否包含下级部门
			deptids=[]
			for d in deptidlist:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		ot=['DeptID','PIN']
		qs=USER_OF_RUN.objects.filter(UserID__DeptID__in=deptids).exclude(StartDate__gt=et).exclude(EndDate__lt=st).values('UserID')
		qs1=USER_TEMP_SCH.objects.filter(UserID__DeptID__in=deptids,SchclassID__gt=0).filter(ComeTime__gte=st).filter(LeaveTime__lt=et).values('UserID')
		ids=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1,DelTag=0).exclude(id__in=qs).exclude(id__in=qs1).order_by(*ot)
		
		#ids=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1,DelTag=0).values_list('id', flat=True).order_by(*ot)
	#qs=USER_OF_RUN.objects.filter(UserID__in=ids).exclude(StartDate__gt=et).exclude(EndDate__lt=st).values_list('UserID', flat=True)
	#qs1=USER_TEMP_SCH.objects.filter(UserID__in=ids).filter(ComeTime__gte=st).filter(LeaveTime__lt=et).values_list('UserID', flat=True)
	try:
		offset = int(request.POST.get('page', 1))
		if offset==0:
			offset=1
	except:
		offset=1
	limit= int(request.POST.get('rows', 50))
	re=[]
	Result={}
	Result['datas']=re
	iCount=len(ids)
	ids=ids[(offset-1)*limit:offset*limit]
	for emp in ids:
#			if (id not in qs) and (id not in qs1):
#				emp=employee.objByID(id)
		d={}
		d['userid']=emp.id
		d['deptid']=emp.Dept().DeptName
		d['badgenumber']=emp.PIN
		d['Workcode'] = emp.Workcode
		d['username']=emp.EName or ' '
		d['Title']=emp.Title or ' '
		re.append(d.copy())
	page_count =int(ceil(iCount/float(limit)))
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result