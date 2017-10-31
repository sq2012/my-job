#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.core.tools import *
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
#from django.http import HttpResponse
#from django.shortcuts import render_to_response
import datetime,os
from mysite.utils import *
from django.contrib.auth.decorators import permission_required, login_required
#from iclock.dataproc import *
#from django.contrib.auth.models import User, Permission
from mysite.iclock.iutils import *
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
#from iclock.datasproc import *
#from iclock.templatetags.iclock_tags import getSex
#from django.utils.encoding import smart_unicode, iri_to_uri



def get_dept_items(request,deptid,d_item):
    dept_list=[]
    if (request.user.is_superuser) or (request.user.is_alldept):
        objs=department.objects.filter(parent__exact=deptid).exclude(DelTag=1).order_by('parent','DeptNumber')
    else:
        dept_list=userDeptList(request.user)
        #dept_list=d_item['userDeptList']
        if deptid==0:
            objs=department.objects.filter(DeptID__in=dept_list).exclude(DelTag=1).exclude(parent__in=dept_list).order_by('parent','DeptNumber')
        else:
            objs=department.objects.filter(parent__exact=deptid,DeptID__in=dept_list).exclude(DelTag=1).order_by('parent','DeptNumber')
    return (objs,dept_list)


def get_dept_list_ex(request,d_item,deptid,isall=False,onlyshowsecondDept=False,sub_fun="",lDepts=[],level=0,userDeptList=[]):
    #if deptid not in d_item.keys():
    #	return []
    try:
        d_items=d_item[deptid]
    except:
        return []
    deptObj = []
    d = {}
    level=level+1
    for i in d_items:
        if not ((request.user.is_superuser) or (request.user.is_alldept)):
            if i not in userDeptList:continue
        if sub_fun=='department':
            if not (i in lDepts):continue
        dobj=department.objByID(i)
        d["id"]=int(i)
        d["name"]=dobj.DeptName
        d["value"]=dobj.DeptNumber
        d["pid"]=int(dobj.parent)
        d["open"]=False
        d["level"]=level+1
        tag=True
        try:
            d_item[i]
        except:
            tag=False
        d["isParent"]=tag
        #此行决定默认显示几级部门，默认2级
        if isall or level<1:
            d["open"]=True
            d["children"]=get_dept_list_ex(request,d_item,i,isall,onlyshowsecondDept,sub_fun,lDepts,level,userDeptList)
        else:
            if onlyshowsecondDept:
                d["open"]=True
            d["children"]=[]
        t = d.copy()
        deptObj.append(t)
    return deptObj




@login_required
def getData(request):
    settings.DEPTVERSION=GetParamValue('DEPTVERSION')
    funid = request.GET.get("func", "")
    page = request.GET.get("page", "")
    deptObj = []
    if page and page=='iclock_taikang':#为一些特殊需求预留,传送非标准部门数据
        fn='taikang.txt'
        if  os.path.exists("%s/%s"%(settings.ADDITION_FILE_ROOT,fn)):
            f = open("%s/%s"%(settings.ADDITION_FILE_ROOT,fn),'r')
            j=0
            for eachline in f:
                j=j+1
                #eachline=eachline[:-1]
                try:
                    line1=safe_unicode(eachline,'GB18030')
                    eachline=line1
                except Exception,e:
                    pass
                line=[]
                if '\t' in eachline:
                    line=eachline.split('\t')
                elif ',' in line:
                    line=eachline.split(',')
                if len(line)>1 and line[0]:
                    d={}
                    d["id"]=j
                    d["name"]="%s %s"%(line[0],line[1])
                    d["value"]=line[0]
                    d["open"]=True
                    d["level"]=0
                    t = d.copy()
                    deptObj.append(t)


        return getJSResponse(deptObj)

    if funid == 'department':

        deptid=int(request.POST.get("id",0))
        sub_fun=request.GET.get("m","")
        lDepts=[]
        if sub_fun=='department':#编辑部门时判断
            dataKey=int(request.GET.get("deptid",0))
            lDepts=getAvailableParentDepts(dataKey,request)
            #for i in pdepts:
                #lDepts.append(int(i.DeptID))
        d = {}
        #expand_dept=GetParamValue('opt_basic_expanddept','1')
        isall=False
        #if expand_dept=='1' or expand_dept=='on':
        #	isall=True
        t1=datetime.datetime.now()
        IsOnlyShowSecondDept=False
        if sub_fun=='OnlyShowSecondDept':  #当只需要显示一二级部门时
            isall=False
            IsOnlyShowSecondDept=True
        if (deptid==0) and (not IsOnlyShowSecondDept) and (sub_fun<>'department'):
            c_deptObj=cache.get("%s_depttree_%s_%s"%(settings.UNIT, request.user.id,settings.DEPTVERSION))
            if c_deptObj:
                return getJSResponse(c_deptObj)
        d_item=get_dept_as_dict(request.user)
        if not d_item:return getJSResponse(d_item)

        t2=datetime.datetime.now()
        #print "33333333333333==",t2-t1
        #if d_item['count']<500:
        #	isall=True
        items=get_dept_items(request,deptid,d_item)
        userDeptList=items[1]
        objs=items[0]
        for t in objs:
            level=0
            if sub_fun=='department':
                if not (t.DeptID in lDepts):continue
            d["id"]=int(t.DeptID)
            d["name"]=t.DeptName
            d["pid"]=int(t.parent)
            d["value"]=t.DeptNumber
            d["open"]=True
            d["level"]=0
            #if d['pid']==0:
            #	d['icon']="/media/img/icons/home.png"

            tag=True
            try:
                d_item[int(t.DeptID)]
            except:
                tag=False
            d["isParent"]=tag
            if deptid==0 and tag:#自动取得第一级部门
                d["drag"]=False
                d["children"]=get_dept_list_ex(request,d_item,t.DeptID,isall,IsOnlyShowSecondDept,sub_fun,lDepts,level,userDeptList)
                d["open"]=True
                if not d["children"]:
                    d["isParent"]=False
            else:
                d["children"]=[]
            t = d.copy()
            deptObj.append(t)
        if (deptid==0) and (not IsOnlyShowSecondDept)  and (sub_fun<>'department'):
            cache.set("%s_depttree_%s_%s"%(settings.UNIT, request.user.id,settings.DEPTVERSION),deptObj,timeout=86400)
        return getJSResponse(deptObj)


@login_required
def save_deptschedule_set(request):
    deptid=request.POST.get('deptid','')
    schclassid=request.POST.get('schclassid','')
    num_runid=request.POST.get('num_runid','')
    defaultid=request.POST.get('defaultid','')
    num_runid=num_runid.split(',')
    schclassid=schclassid.split(',')

    if deptid=="":
        return getJSResponse({"ret":1,"message":u"%s"%_('Save Failed')})
    ItemName=deptid
    ItemDict={'num_runid':num_runid,'schclassid':schclassid,'defaultid':defaultid}
    ItemValue=dumps1(ItemDict)
    u=request.user
    try:
        item=ItemDefine.objects.get(ItemName=deptid,ItemType='deptschedule_set')
    except:
        item=ItemDefine(Author=u,ItemName=deptid,ItemValue=ItemValue,ItemType='deptschedule_set')
    item.ItemValue=ItemValue
    item.Author=u
    item.save()
    return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})
@login_required
def get_deptschedule_set(request):
    deptid=request.POST.get('deptid','')
    result={}
    try:
        item=ItemDefine.objects.get(ItemName=deptid,ItemType='deptschedule_set')
    except:
        return getJSResponse({'defaultid':'','defaultname':'','num_runid':[],'schclassid':[]})
    result=loads(item.ItemValue)
    result['defaultname']=''
    if result['defaultid']!='':
        try:
            n=NUM_RUN.objects.get(Num_runID=result['defaultid'])
            result['defaultname']=n.Name
        except:
            result['defaultid']=''
            pass
#	print "result=",result
    return getJSResponse(result)