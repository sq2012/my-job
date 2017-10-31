#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from django.template import  RequestContext 
from django.shortcuts import render_to_response
from django.db import models
from django.contrib.auth.models import  Permission
from django.contrib.auth import get_user_model
#from mysite.iclock.iutils import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from mysite.iclock.datas import *
import datetime
from django.core.paginator import Paginator
#from mysite.iclock.dataview import *
#from pyExcelerator import *
#from mysite.iclock.templatetags.iclock_tags import shortDate4, onlyTime,AbnormiteName,StateName,isYesNo,getSex,schName
import copy
#from mysite.iclock.datasproc import *
from django.core.cache import cache
from django.contrib.auth.decorators import login_required,permission_required
from mysite.iclock.datautils import GetModel,hasPerm,QueryData
#from mysite.iclock.datasproc import *
from mysite.iclock.jqgrid import *
from mysite.base.models import *
from mysite.iclock.templatetags.iclock_tags import *
PAGE_LIMIT_VAR = 'l'


@login_required
def index(request, ModelName):
    if request.method=='POST':
	    if ModelName=='NUM_RUN':
		Result=getNUMRUN(request, ModelName)
		rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
		return getJSResponse(rs)
	    elif ModelName=='department':
		gettype=request.GET.get('gettype',"")
		if gettype=="1":
		    Result=getdptsbySN(request, ModelName)
		elif gettype=="2":
		    Result=getdptsbyID(request, ModelName)
		rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
		return getJSResponse(rs)
	    elif ModelName=='iclock':
		Result=geticlockbyUser(request, ModelName)
		rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
		return getJSResponse(rs)
	    elif ModelName=='zone':
		Result=getzonesbySN(request, ModelName)
		rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
		return getJSResponse(rs)
	    elif ModelName=='Dininghall':
		Result=getdiningsbySN(request, ModelName)
		rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
		return getJSResponse(rs)
	    else:
		dataModel=GetModel(ModelName)
		if not dataModel: return NoFound404Response(request)
		if not hasPerm(request.user, dataModel, "delete"):
		    return NoPermissionResponse()
		jqGrid=JqGrid(request,datamodel=dataModel)
		items=jqGrid.get_items()   #not Paged
		cc=jqGrid.get_json(items)
		tmpFile=ModelName+'_list.js'
		if dataModel.__name__.lower()=='myuser':
		    tmpFile='user_list.js'
    
		tmpFile=request.GET.get(TMP_VAR,tmpFile)
		#y=request.GET.get('y',datetime.datetime.now().year)
		t=loader.get_template(tmpFile)
		try:
		    rows=t.render(RequestContext(request, cc))
		except Exception,e:
		    #print "0000000000",e
		    rows='[]'
		    pass
		rownumber = int(request.POST.get("rows"))

		t_r="{"+""""page":"""+str(cc['page'])+","+""""total":"""+str(cc['total'])+","+""""records":"""+str(cc['records'])+","+""""rows":"""+rows+"""}"""
		return getJSResponse(t_r)
    else:
        request.user.iclock_url_rel='../..'
        settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
        limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
        tmpFile=ModelName+'.html'
        if dataModel.__name__.lower()=='myuser':
            tmpFile='user.html'
        tmpFile=request.GET.get(TMP_VAR, tmpFile)
        try:
                    colModel=dataModel.colModels()
        except Exception,e:
                    colModel=[]

	return render_to_response('simpledata.html',
							{
                                                            'colModel':dumps(colModel),


                                                            'limit':limit
							},RequestContext(request, {}))	

def geticlockbyUser(request, ModelName):
	from mysite.iclock.iutils import AuthedIClockList
	from mysite.iclock.templatetags.iclock_tags import device_memo,deptShowStr
	itemid=request.GET.get('itemid',"")
	User=get_user_model()
	u=User.objects.get(id=itemid)
	iCount=0
	item_count=0
	qs=AuthedIClockList(u)
	qs1=iclock.objects.filter(SN__in=qs)
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 30))
	re=[]
	Result={}
	Result['datas']=re
	item_count = len(qs1)
	qs1=qs1[(offset-1)*limit:offset*limit]
	for id in qs1:
		d={}
		d['SN']=id.SN
		d['Alias']=id.Alias or ''
		d['IPAddress']=id.IPAddress
		d['LastActivity']=id.LastActivity
		d['State']=getStateStr(id.getDynState())
		d['LogStamp']=transLogStamp(id.GetDevice().LogStamp)
		d['UserCount']=id.UserCount
		d['FPCount']=id.FPCount
		d['FWVersion']=id.FWVersion
		d['DeviceName']=id.DeviceName
		d['DeptIDS']=deptShowStr(id)#id.BackupDev
		d['Memo']=device_memo(id)
		re.append(d.copy())
		iCount=iCount+1
	page_count =int(ceil(item_count/float(limit)))
	if offset>page_count:offset=page_count
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

#设备中通过SN获得授权部门
def getdptsbySN(request, ModelName):
	from mysite.iclock.iutils import getDepartmentBySN
	SN=request.GET.get('SN',"")
	sord=request.POST.get('sord',"desc")
	sidx=request.POST.get('sidx',"")
	iCount=0
	item_count=0
	col=[]
	qs=getDepartmentBySN(SN)
	if sidx and sidx!='id':
		if sord=='desc':
			col=['-'+sidx]
		else:
			col=[sidx]
	if -1 in qs:
		if sidx:
			qs1=department.objects.all().exclude(DelTag=1).order_by(*col)
		else:
			qs1=department.objects.all().exclude(DelTag=1)
	else:
		if sidx:
			qs1=department.objects.filter(DeptID__in=qs).order_by(*col)
		else:
			qs1=department.objects.filter(DeptID__in=qs)
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 30))
	re=[]
	Result={}
	Result['datas']=re
	item_count=len(qs1)
	qs1=qs1[(offset-1)*limit:offset*limit]
	for id in qs1:
		d={}
		d['DeptID']=id.DeptID
		d['DeptNumber']=id.DeptNumber
		d['DeptName']=id.DeptName
		if id.Parent():
			d['Parent']=id.Parent().DeptName
		else:
			d['Parent']=''
		d['DeptAddr']=id.DeptAddr
		d['DeptPerson']=id.DeptPerson
		d['DeptPhone']=id.DeptPhone
		d['empCount']=id.empCount()
		re.append(d.copy())
		iCount=iCount+1

	page_count =int(ceil(item_count/float(limit)))
	if offset>page_count:offset=page_count
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

#管理员用户通过用户id获得授权部门
def getdptsbyID(request, ModelName):
	from iutils import userDeptList
	itemid=request.GET.get('itemid',"")
	User=get_user_model()
	u=User.objects.get(id=itemid)
	iCount=0
	item_count=0
	qs=userDeptList(u)
	qs1=department.objects.filter(DeptID__in=qs)
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 30))
	re=[]
	Result={}
	Result['datas']=re
	item_count = len(qs1)
	qs1=qs1[(offset-1)*limit:offset*limit]
	for id in qs1:
		d={}
		d['DeptID']=id.DeptID
		d['DeptNumber']=id.DeptNumber
		d['DeptName']=id.DeptName
		if id.Parent():
			d['Parent']=id.Parent().DeptName
		else:
			d['Parent']=''
		d['DeptAddr']=id.DeptAddr
		d['DeptPerson']=id.DeptPerson
		d['DeptPhone']=id.DeptPhone
		d['empCount']=id.empCount()
		re.append(d.copy())
		iCount=iCount+1

	page_count =int(ceil(item_count/float(limit)))
	if offset>page_count:offset=page_count
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

def getNUMRUN(request, ModelName):

    SchclassID=request.GET.get('SchclassID',"")
    iCount=0
    qs=NUM_RUN_DEIL.objects.filter(SchclassID=SchclassID).values_list("Num_runID").distinct().order_by('Num_runID')
    #qs=NUM_RUN_DEIL.objects.filter(SchclassID=SchclassID).values_list('Num_runID', flat=True)
    qs1=NUM_RUN.objects.filter(Num_runID__in=qs).filter(DelTag=0)
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset=1
    limit= int(request.POST.get('rows', 30))
    re=[]
    Result={}
    Result['datas']=re
    qs1=qs1[(offset-1)*limit:offset*limit]
    for id in qs1:
        d={}
        d['Num_runID']=id.Num_runID
        d['Name']=id.Name
        d['StartDate']=id.StartDate
        d['EndDate']=id.EndDate
        d['Cycle']=id.Cycle
        if id.Units==0:
            d['Units']='天'
        if id.Units==1:
            d['Units']='周'
        if id.Units==2:
            d['Units']='月'
        # d['Units']=id.Units
        if id.Num_RunOfDept:
            d['Num_RunOfDept']=(unicode(str(id.Num_RunOfDept))+u' '+department.objects.get(pk=id.Num_RunOfDept).DeptName)
        else:
            d['Num_RunOfDept']=u'所有部门'
        re.append(d.copy())
        iCount=iCount+1

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
	#rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
	#print rs
	#return getJSResponse(rs)

def getzonesbySN(request, ModelName):
	from iutils import getZoneBySN
	SN=request.GET.get('SN',"")
	iCount=0
	item_count=0
	qs=getZoneBySN(SN)
	qs1=zone.objects.filter(id__in=qs)
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 30))
	re=[]
	Result={}
	Result['datas']=re
	item_count=len(qs1)
	qs1=qs1[(offset-1)*limit:offset*limit]
	for id in qs1:
		d={}
		d['code']=id.code
		d['name']=id.name
		d['remark']=id.remark
		if id.parentname():
			d['parent']=id.parentname()
		else:
			d['parent']=''
		re.append(d.copy())
		iCount=iCount+1

	page_count =int(ceil(item_count/float(limit)))
	if offset>page_count:offset=page_count
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

def getdiningsbySN(request, ModelName):
	from iutils import getDiningBySN
	SN=request.GET.get('SN',"")
	iCount=0
	item_count=0
	qs=getDiningBySN(SN)
	qs1=Dininghall.objects.filter(id__in=qs)
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 30))
	re=[]
	Result={}
	Result['datas']=re
	item_count=len(qs1)
	qs1=qs1[(offset-1)*limit:offset*limit]
	for id in qs1:
		d={}
		d['code']=id.code
		d['name']=id.name
		d['remark']=id.remark
		re.append(d.copy())
		iCount=iCount+1

	page_count =int(ceil(item_count/float(limit)))
	if offset>page_count:offset=page_count
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

@login_required
def gridIndex(request,ReportName):
        if request.method=='GET':
            r=GetGridCaption(ReportName,request)
            return r
        else:
            Result=getsearchRecords(request,ReportName)
            rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
            return getJSResponse(rs)
