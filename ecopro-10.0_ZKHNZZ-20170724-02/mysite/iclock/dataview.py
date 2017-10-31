#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.meeting.models import *
from mysite.iclock.nomodelview import *
from mysite.core.tools import *
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response,render
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
from mysite.iclock.reb  import *
from django.conf import settings
from mysite.cab import *
#from mysite.iclock.devview import checkDevice, getEmpCmdStr
from mysite.iclock.datv import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import  Group,Permission
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
#from pyExcelerator import *
from mysite.iclock.sendmail import *
from django.contrib.auth import get_user_model
from mysite.base.models import *
from mysite.visitors.models import *
from mysite.core.cmdproc import *
from collections import OrderedDict
from django.utils.datastructures import OrderedSet
from mysite.core.zkwidgets import *

#from mysite.iclock.templatetags.iclock_tags import HasPerm


#add_to_builtins('mysite.iclock.templatetags.iclock_tags')

PAGE_LIMIT_VAR = 'l'
TMP_VAR = 't'
deviceStatus={
  0: _("Pause"),
  1:_("Online"),
  2:_("Communicating"),
  3:_("Offline"),
}



def save_instance(form, instance, fields=None, fail_message='saved',commit=True, exclude=None, construct=True):
    """
    Saves bound Form ``form``'s cleaned_data into model instance ``instance``.

    If commit=True, then the changes to ``instance`` will be saved to the
    database. Returns ``instance``.

    If construct=False, assume ``instance`` has already been constructed and
    just needs to be saved.
    """
    from django.forms.models import construct_instance
    if construct:
        instance = construct_instance(form, instance, fields, exclude)
    opts = instance._meta
    if form.errors:
        raise ValueError("The %s could not be %s because the data didn't validate." % (opts.object_name, fail_message))

    # Wrap up the saving of m2m data as a function.
    def save_m2m():
        cleaned_data = form.cleaned_data
        # Note that for historical reasons we want to include also
        # virtual_fields here. (GenericRelation was previously a fake
        # m2m field).
        for f in opts.many_to_many :
            if not hasattr(f, 'save_form_data'):
                continue
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if f.name in cleaned_data:
                f.save_form_data(instance, cleaned_data[f.name])
    if commit:
        # If we are committing, save the instance and the m2m data immediately.
        instance.save()
        save_m2m()
    else:
        # We're not committing. Add a method to the form to allow deferred
        # saving of m2m data.
        form.save_m2m = save_m2m
    return instance



def make_instance_save(instance, fields, fail_message):
    """Returns the save() method for a Form."""
    def save(self, commit=True):
        return save_instance(self, instance, fields, fail_message, commit)
    return save


def form_for_model(model, instance=None, form=forms.BaseForm, fields=None,
        formfield_callback=lambda f, **kwargs: f.formfield(**kwargs)):
    opts = model._meta
    field_list = []
    lock_fields=[]
    to_text_fields=[]
    try:
        lock_fields=model.Admin.lock_fields
    except:
        pass
    try:
        to_text_fields=model.Admin.to_text_fields
    except:
        pass
    for f in opts.fields + opts.many_to_many:
        if not f.editable:
            continue
        if fields and not f.name in fields:
            continue
        fst=str(type(f.formfield()))
        fstl=fst[8:-2].split('.')
        try:
            if isinstance(f.value_from_object(instance),datetime.time):
                current_value=f.value_from_object(instance)
            else:
                if instance:
                    current_value = instance and f.value_from_object(instance)# or None
                else:
                    current_value=None
        except:
            current_value = instance and f.value_from_object(instance) or None
        if 'TimeField' in fstl:
            current_value=onlyTime(current_value)
        if f.name in lock_fields:
            formfield = f.formfield(widget=ForeignKeyInput(),initial=current_value)#form_field_readonly(f, initial=current_value)
        elif f.name in to_text_fields:
            formfield = f.formfield(widget=TextInput(),initial=current_value)

        else:
            formfield = formfield_callback(f, initial=current_value)
        if formfield:
            field_list.append((f.name, formfield))
            if str(type(f))=="<class 'django.db.models.fields.related.ForeignKey'>":
                deltag=True
                state=True
                try:
                    f.related_model._meta.get_field('DelTag')
                except:
                    deltag=False
                try:
                    f.related_model._meta.get_field('State')
                except:
                    state=False
                if deltag and state:
                    formfield.queryset=formfield.queryset.exclude(Q(DelTag=1)|Q(State=2))
                elif deltag and not state:
                    formfield.queryset=formfield.queryset.exclude(DelTag=1)
            #elif f.name in to_text_fields:
            #       formfield.queryset=formfield.queryset.filter(pk=current_value)



    base_fields = OrderedDict(field_list)
    return type(opts.object_name + 'Form', (form,),
        {'base_fields': base_fields, '_model': model,
         'save': make_instance_save(instance or model(), fields, 'created')})

def form_for_instance(instance, form=forms.BaseForm, fields=None,  formfield_callback=lambda f, **kwargs: f.formfield(**kwargs)):
    return form_for_model(instance.__class__, instance, form, fields, formfield_callback)

def changeEmpDept(dept, emp):
    emp.DeptID=dept
    emp.save()

def restoreEmpLeave(emp):
    emp.OffDuty=0
    emp.save()

def appendEmpToDevWithin(devs, emp, startTime, endTime, cursor=None):
    pin=emp.pin()
    #edev=emp.Device()
    #appendEmpToDev(dev, emp, cursor, False, startTime)
    appendEmpToDevNew(devs, emp, cursor,cmdTime=startTime,finger=1,face=1,PIC=1)
    if endTime and (endTime.year>2007):
        appendDevCmdNew(devs, "DATA DEL_USER PIN=%s"%pin, cursor, endTime)
        #delete at endTime
        for d in devs:
            delEmpInDevice(pin,d)
    return cursor
def cheligang(request,ModelName):
    if ModelName=='employee':
        keys = request.POST.getlist("K")
        return cheligang1(keys)
def cheligang1(keys):
    emps = employee.objects.filter(id__in=keys)
    try:
        for emp in emps:
            if emp.OffPosition==0:
               return getJSResponse({"ret":1,"message":u'%s'%_(u'该人员未离岗，无法进行操作')}) 
        employee.objects.filter(id__in=keys).update(OffPosition=0,OffPositionDate=None)
    except:
        return getJSResponse({"ret":1,"message":u'%s'%_(u'离岗恢复失败')})
    return getJSResponse({"ret":0,"message":u'%s'%_(u'离岗恢复成功')})

def ligang(request,ModelName):
    if ModelName=='employee':
        keys = request.POST.getlist("K")
        OffPositionDate = request.POST.get('OffPositionDate')
        return ligang1(keys,OffPositionDate)
def ligang1(keys,OffPositionDate):
    emps = employee.objects.filter(id__in=keys)
    try:
        for emp in emps:
            if emp.OffPosition==1:
               return getJSResponse({"ret":1,"message":u'%s'%_(u'人员已离岗无法进行操作')}) 
        employee.objects.filter(id__in=keys).update(OffPosition=1,OffPositionDate=OffPositionDate)
    except:
        return getJSResponse({"ret":1,"message":u'%s'%_(u'人员离岗失败')})
    return getJSResponse({"ret":0,"message":u'%s'%_(u'人员离岗成功')})

def chejiezhuang(request,ModelName):
    if ModelName=='USER_SPEDAY':
        keys = request.POST.getlist("K")
        return chejiezhuang1(keys)
def chejiezhuang1(keys):
    spedys=USER_SPEDAY.objects.filter(id__in=keys)
    try:
        for spedy in spedys:
            aa=spedy.EndSpecDay-spedy.StartSpecDay
        USER_SPEDAY.objects.filter(id__in=keys).update(jiezhuangDay=None,tianshu=0,jiezhuang=0,jieYUANYING='')
    except:
        return getJSResponse({"ret":1,"message":u'%s'%_(u'撤销结转失败')})
    return getJSResponse({"ret":0,"message":u'%s'%_(u'撤销结转成功')})

def jiezhuang(request,ModelName):
    if ModelName=='USER_SPEDAY':
        keys = request.POST.getlist("K")
        jieTime = request.POST.get('jieTime')
        tianshu = request.POST.get('tianshu')
        jieYUANYING = request.POST.get('jieYUANYING')
        return jiezhuang1(keys,jieTime,tianshu,jieYUANYING)
def jiezhuang1(keys,jieTime,tianshu,jieYUANYING):
    print '777777777777777',keys
    spedys=USER_SPEDAY.objects.filter(id__in=keys)
    try:
        for spedy in spedys:
            print spedy.id
            aa=(spedy.EndSpecDay-spedy.StartSpecDay).total_seconds()
            cc=int(tianshu) * 24*60*60
            if  not tianshu:
                return getJSResponse({"ret":1,"message":u'%s'%_(u'结转天数为空，无法结转')})
            if aa<cc:
                return getJSResponse({"ret":1,"message":u'%s'%_(u'结转失败,结转时间大于请假时间')})
        USER_SPEDAY.objects.filter(id__in=keys).update(jiezhuangDay=jieTime,tianshu=tianshu,jiezhuang=1,jieYUANYING=jieYUANYING)
    except:
        return getJSResponse({"ret":1,"message":u'%s'%_(u'结转失败')})
    return getJSResponse({"ret":0,"message":u'%s'%_(u'结转成功')})

@login_required
def DataClear(request, ModelName):
    appName=request.path.split('/')[1]
    dataModel=GetModel(ModelName,appName)
    if not dataModel: return NoFound404Response(request)
    if not hasPerm(request.user, dataModel, "delete"):
        return NoPermissionResponse()
    jqGrid=JqGrid(request,datamodel=dataModel)
    items=jqGrid.get_items()   #not Paged
    if dataModel==get_user_model():
        items=items.exclude(id=request.user.id,is_superuser=True).delete()
    elif dataModel==employee:
        userids=items.values_list('id', flat=True)
        for uid in userids:
            cache.delete("%s_iclock_emp_%s"%(settings.UNIT,uid))
    elif dataModel==checkexact:
        for t in items:
            deleteCalcLog(UserID=t.UserID_id,StartDate=t.CHECKTIME,EndDate=t.CHECKTIME)
        sql='delete from checkinout where userid=%s and checktime=%s'
        params=(t.UserID_id,t.CHECKTIME)
        try:
            customSql(sql,params)
        except:
            pass
    elif dataModel==iclock:
        for t in items:
            t.DelTag=1
            t.save()
    elif dataModel==LeaveClass:
        lids = LeaveClass.objects.all().values_list('pk',flat=True)
        if USER_SPEDAY.objects.filter(DateID__in=lids).count()>0:
            return getJSResponse({"ret":1,"message":u"%s"%_(u'有正在使用的假类，无法全部删除')})

    delNum=items.count()
    items.delete()




    #usr=request.user
    #flag=0
    #deptadmin=[]
    #if not (request.user.is_superuser or request.user.is_alldept):
    #    deptadmin=userDeptList(request.user)
    #
    #lookup_params={}
    #opts = dataModel._meta
    #search=request.GET.get('q',"")
    #search=unquote(search);
    #opts = dataModel._meta
    #searchFlag=0
    #ob=''
    #delNum=0
    #if request.GET.has_key('q') and opts.admin.search_fields:
    #       or_queries=[]
    #       qs=dataModel.objects.all()
    #       for bit in search.split():
    #               or_querie = [models.Q(**{construct_search(field_name): bit}) for field_name in opts.admin.search_fields]
    #               or_queries=or_queries+or_querie
    #               other_qs = dataModel.objects.all()
    #               try:
    #                       other_qs.dup_select_related(qs)
    #               except:
    #                       if qs._select_related:
    #                               other_qs = other_qs.select_related()
    #               ob=search
    #               other_qs = other_qs.filter(reduce(operator.or_, or_queries))
    #               qs = qs & other_qs
    #               try:
    #                       delNum=qs.count()
    #                       qs.delete()
    #
    #               except:
    #                       connection.close()
    #                       delNum=0
    #                       qs.delete()
    #
    #               searchFlag=1
    #params = dict(request.POST.items())
    #lookup_params=GetLookup_params(params)
    #if dataModel==days_off:
    #       params = dict(request.GET.items())
    #       lookup_params=GetLookup_params(params)
    #       if 'UserID__id__exact' in lookup_params:
    #               lookup_params['UserID__in']=lookup_params['UserID__id__exact']
    #               del lookup_params['UserID__id__exact']
    #       if 'UserID__id__in' in lookup_params:
    #               lookup_params['UserID__in']=lookup_params['UserID__id__in']
    #               del lookup_params['UserID__id__in']
    #       if 'UserID__DeptID__in' in lookup_params:
    #               lookup_params['DeptID__in']=lookup_params['UserID__DeptID__in']
    #               del lookup_params['UserID__DeptID__in']
    #       if 'deptIDs' in lookup_params:
    #               if type(lookup_params['deptIDs'])==type(u"111") or type(lookup_params['deptIDs'])==type("111"):
    #                       lookup_params['deptIDs']=lookup_params['deptIDs'].split(",")
    #               lookup_params['DeptID__in']=lookup_params['deptIDs']
    #               del lookup_params['deptIDs']
    #if not searchFlag:
    #       if dataModel==User:
    #               delNum=User.objects.exclude(id=request.user.id,is_superuser=True).count()
    #               User.objects.exclude(id=request.user.id,is_superuser=True).delete()
    #       elif dataModel==employee:
    #               if deptadmin:
    #                       for t in deptadmin:
    #                               try:
    #                                       em=employee.objects.filter(DeptID__exact=t)#如此删除为了同时删除cache
    #                                       if lookup_params:
    #                                               em=em.objects.filter(**lookup_params)
    #                                       for t in em:
    #                                               try:
    #                                                       t.delete()
    #                                                       delNum+=1
    #                                               except:
    #                                                       connection.close()
    #                                                       t.delete()
    #                                                       delNum+=1
    #                               except:
    #                                       pass
    #               else:
    #                       flag=1
    #
    #       elif dataModel==iclock:
    #               STATE_V=int(request.POST.get('s', -1))
    #               if not deptadmin:
    #                       devs=iclock.objects.all()
    #                       for o in devs:
    #                               if STATE_V>-1:
    #                                       if o.getDynState()==STATE_V:
    #                                               ob=deviceStatus[STATE_V]
    #                                               cache.delete("iclock_"+o.SN)
    #                                               if o.DelTag!=1:
    #                                                       delNum+=1
    #                                               o.DelTag=1
    #                                               o.save()
    #
    #                               else:
    #                                       cache.delete("iclock_"+o.SN)
    #                                       if o.DelTag!=1:
    #                                               delNum+=1
    #                                       o.DelTag=1
    #                                       o.save()
    #
    #               else:
    #                       for t in deptadmin:
    #                               clk=iclock.objects.filter(DeptID__exact=t)
    #                               for o in clk:
    #                                       if STATE_V>-1:
    #                                               if o.getDynState()==STATE_V:
    #                                                       ob=deviceStatus[STATE_V]
    #                                                       cache.delete("iclock_"+o.SN)
    #                                                       if o.DelTag!=1:
    #                                                               delNum+=1
    #                                                       o.DelTag=1
    #                                                       o.save()
    #
    #                                       else:
    #                                               cache.delete("iclock_"+o.SN)
    #                                               if o.DelTag!=1:
    #                                                       delNum+=1
    #                                               o.DelTag=1
    #                                               o.save()
    #
    #
    #       else:
    #               flag=1
    #       if flag==1:
    #               if lookup_params:
    #                       em=dataModel.objects.filter(**lookup_params)
    #                       if dataModel==days_off:
    #                               for row in em:
    #                                       u=days_off.objects.filter(id=int(row.id))[0]
    #                                       if u.UserID:
    #                                               deleteCalcLog(UserID=u.UserID,StartDate=u.FromDate,EndDate=u.ToDate)
    #                                       else:
    #                                               deleteCalcLog(DeptID=u.DeptID,StartDate=u.FromDate,EndDate=u.ToDate)
    #                       for t in em:
    #                               try:
    #                                       t.delete()
    #                                       delNum+=1
    #                               except:
    #                                       connection.close()
    #                                       t.delete()
    #                                       delNum+=1
    #               else:
    #                       try:
    #                               delNum=dataModel.objects.count()
    #                               dataModel.clear()
    #                       except AttributeError, e:
    #                               delNum=dataModel.objects.all().count()
    #                               if dataModel==days_off:
    #                                       em=dataModel.objects.all()
    #                                       for row in em:
    #                                               u=days_off.objects.filter(id=int(row.id))[0]
    #                                               if u.UserID:
    #                                                       deleteCalcLog(UserID=u.UserID,StartDate=u.FromDate,EndDate=u.ToDate)
    #                                               else:
    #                                                       deleteCalcLog(DeptID=u.DeptID,StartDate=u.FromDate,EndDate=u.ToDate)
    #                               dataModel.objects.all().delete()
    #
    #for k in lookup_params.keys():
    #       if ob=='':
    #               ob='%s'%(lookup_params[k])
    #       else:
    #               ob='%s,%s'%(ob,lookup_params[k])
    #object="delete by %s "%(ob and ob or 'All')
    #object=object[:40]
    adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, action=u'%s'%_(u"Clear All"), object=object,count=delNum).save(force_insert=True)#
    return getJSResponse({"ret":0,"message":u"%s"%_('Operate finish')})

@login_required
def DataDelOld(request, ModelName):
    appName=request.path.split('/')[1]

    dataModel=GetModel(ModelName,appName)
    if not dataModel: return NoFound404Response(request)
    if not hasPerm(request.user, dataModel, "delete"):
        return NoPermissionResponse()
    day=request.GET.get('start','')
    try:
        delParam=dataModel.delOld()
        delOldRecords(dataModel, delParam[0], day)
    except AttributeError, e:
        errorLog(request)

    adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, action=u'%s'%_(u"Clear Obsolete Data"),object = request.META["REMOTE_ADDR"]).save(force_insert=True)#
    return getJSResponse({"ret":0,"message":u"%s"%_('Operate finish')})


def ModifyFields(dataModel):
    fields = dataModel._meta.fields
    dtFields = ''           # 日期时间 字段，加日历和时间
    inputFields = ''        # 必输字段
    for field in fields:
        if "DateTimeField" in str(type(field)):
            dtFields += field.name + ','
        if field.name != 'id':
            if (not field.blank) or field.primary_key:
                inputFields += field.name + ','
    if dtFields:
        dtFields = dtFields[:-1]
    if inputFields:
        inputFields = inputFields[:-1]
    return inputFields, dtFields

def get_level_html(key,itype='employee'):
    objs=level.objects.all()
    lve_list=[]
    if key:
        if itype=='employee':
            lve_list=list(level_emp.objects.filter(UserID=key).values_list('level',flat=True))
        elif itype=='visitionlogs':
            try:
                obj=visitionlogs.objects.get(id=key)
                if obj.levels:
                    lve_list=obj.levels.split(',')
                    for t in range(len(lve_list)):
                        lve_list[t]=int(lve_list[t])
            except:
                lve_list=[]


    else:
        lve_list=[]
    level_list="<input id='id_levels' type='hidden' name='levels' /><ul id='levelSingleBrowser' style='margin:5px 2px 3px 5px;'>"
    if objs:
        for t in objs:
            if t.id in lve_list:
                level_list+="<li><input type='checkbox' checked='checked' name='level' value='%s'/>%s</li>"%(t.id,t.name)
            else:
                level_list+="<li><input type='checkbox' name='level' value='%s'/>%s</li>"%(t.id,t.name)
    else:
        level_list+="<label class='none_selected'>没有可选的门禁权限组！</label>"

    return level_list


def DataDetailResponse(request, dataModel, form, key='', **kargs):
    appName=request.path.split('/')[1]
    if request.POST:
        return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})
    else:
        if not kargs: kargs={}
    #       inputFields, dtFields=ModifyFields(dataModel)
    request.model=dataModel

    kargs["iclock_url_rel"]="../../.."
    request.user.iclock_url_rel=kargs["iclock_url_rel"]
    kargs["form"]=form
    kargs["title"]=(u"%s"%dataModel._meta.verbose_name).capitalize()
    kargs["dataOpt"]=dataModel._meta
    #       kargs["parent_name"]="测试部门"
    #       kargs["inputFields"]=inputFields
    #       kargs["dtFields"]=dtFields
    kargs["add"]=key==''
    kargs["param_value"]=key
    dobj=''
    #if dataModel==Group:
        #   kargs["permissions"]=getAllAuthPermissions(request.user)
        #   print "==========="
        #   print kargs["permissions"]
    if dataModel==department: # 防止把子部门更改成上级部门
        if key:
            o=department.objByID(key)
            parent_name=''
            if o.parent>0:
                p=department.objByID(o.parent)
                parent_name=str(p.DeptNumber)+ '  '+p.DeptName
            kargs["parent_name"]=parent_name
            kargs["param_value"]=o.DeptID
    if dataModel==SchClass:
        if key:
            sch=SchClass.objects.get(SchclassID=key)
            if sch.TimeZoneOfDept:
                dobj=department.objByID(sch.TimeZoneOfDept)
                if not dobj:
                    dobj=_(u"所有部门")
            else:
                dobj=_(u"所有部门")
        else:
            if request.user.is_superuser:
                dobj=""
            else:
                if request.user.AutheTimeDept:
                    dobj=department.objByID(request.user.AutheTimeDept)
                else:
                    dobj=_(u"所有部门")
        kargs["parent_name"]=dobj
    if dataModel==NUM_RUN:
        if key:
            num=NUM_RUN.objects.get(Num_runID=key)
            if num.Num_RunOfDept:
                dobj=department.objByID(num.Num_RunOfDept)
                if not dobj:
                    dobj=_(u"所有部门")
            else:
                dobj=_(u"所有部门")
        else:
            if request.user.is_superuser:
                dobj=""
            else:
                if request.user.AutheTimeDept:
                    dobj=department.objByID(request.user.AutheTimeDept)
                else:
                    dobj=_(u"所有部门")
        kargs["parent_name"]=dobj
    if dataModel==days_off:
        if key:
            days=days_off.objects.get(id=key)
            if days.DeptID:
                dobj=department.objByID(days.DeptID)
                kargs["DeptID_name"]=dobj
            if days.UserID:
                uobj=employee.objByID(days.UserID)
                kargs["UserID_name"]=uobj
    #           kargs["parent_dept_list"]=getAvailableParentDepts(key,request)
    tmpFile=dataModel.__name__+'_edit.html'
    mod_name=request.GET.get('mod_name','att')
    kargs['app']=mod_name
    if appName!='iclock':
        tmpFile=appName+'/'+tmpFile
    if dataModel==USER_SPEDAY:
        if key=='_new_':
            details_form=form_for_instance(USER_SPEDAY_DETAILS())
        else:
            try:
                details_spe=USER_SPEDAY_DETAILS.objByID(key)
                details_form=form_for_instance(details_spe)
            except :
                details_form=form_for_instance(USER_SPEDAY_DETAILS())
            kargs["details_form"]=details_form
    if dataModel==employee:
        if key and key!='_new_':
            fcount = BioData.objects.filter(UserID=key,bio_type = 1).count()
        else:
            fcount = 0
        kargs['fcount']=fcount
        try:
            tmp_emp=employee.objects.get(pk=key)
        except:
            tmp_emp=None
        kargs['img']='/media/img/transaction/noimg.jpg'
        kargs['up_img']='/media/img/transaction/noimg.jpg'
        if tmp_emp:
            import random
            fname="%s.jpg"%tmp_emp.PIN
            imgUrl='/iclock/file/photo/'+fname
            fullName=getStoredFileName("photo", None, fname)
            if os.path.exists(fullName):
                varile = str(random.random()).split('.')[1]
                kargs['img']=imgUrl+'?time=%s'%varile
            try:
                tbName=getStoredFileName("photo/thumbnail", None, tmp_emp.PIN+"_SN.jpg")
                tbUrl=getStoredFileURL("photo/thumbnail", None, tmp_emp.PIN+"_SN.jpg")
                up_varile = str(random.random()).split('.')[1]
                if os.path.exists(tbName):#取路径先判断压缩图是否已经存在
                    kargs['up_img']=tbUrl+'?time=%s'%up_varile
                else:#压缩图不存在 创建
                    up_fullName=getStoredFileName("photo", None, tmp_emp.PIN+"_SN.jpg")
                    if os.path.exists(up_fullName):
                        if createThumbnail(up_fullName, tbName):
                            kargs['up_img']=tbUrl+'?time=%s'%up_varile
            except:
                pass
    if dataModel==employee and mod_name=='acc':
        if key=='_new_':
            acc_form=form_for_instance(acc_employee())
        else:
            try:
                acc_empl=acc_employee.objects.get(UserID=key)
                acc_form=form_for_instance(acc_empl)
            except:
                acc_form=form_for_instance(acc_employee())

        kargs["acc_form"]=acc_form
        level=get_level_html(key)
        kargs['level']=level
    if dataModel==visitionlogs and mod_name=='visitors':
        level_html=get_level_html(key,'visitionlogs')
        kargs['level_html']=level_html
    if dataModel==employee_borrow:
        eb = employee_borrow.objects.get(id=key)
        fdept = eb.fromDept
        tdept = eb.toDept
        uid = eb.userID
        kargs['fdept'] = department.objByID(fdept).DeptName
        kargs['tdept'] = department.objByID(tdept).DeptName
        kargs['uname'] = employee.objByID(uid).EName
    return render(request,tmpFile,kargs)
    #return render_to_response([tmpFile,'data_edit.html'],kargs)

def DataPostCheck(request, oldObj, newObj):
    if str(type(newObj))=="<class 'iclock.models.USER_CONTRACT'>":
        try:
            emp=employee.objByID(newObj.UserID.id)
            emp.Contractendtime=newObj.EndContractDay
            emp.save()
        except Exception,ex:
            print ex
    if isinstance(newObj, employee):
        mod_name=request.GET.get('mod_name','att')
        if mod_name=='acc':
            from mysite.acc.accviews import saveToAccEmployee
            try:
                saveToAccEmployee(request,newObj)
            except Exception:
                import traceback;traceback.print_exc()

        #from iclock.datamisc import saveUploadImage
        #f=devicePIN(newObj.PIN)+".jpg"
        #try:
        #    saveUploadImage(request, "fileUpload", fname=getStoredFileName("photo", None, f))
        #    newObj.rmThumbnail()
        #except:
        #    pass #errorLog()
        #if oldObj:  #修改人员数据
        #       if oldObj.Title!=newObj.Title:
        #               DataChangeTitle(newObj.id)
        #       old_dev=oldObj.Device()
        #       if int(oldObj.PIN)<>int(newObj.PIN): #changed the PIN, 需要把原来的PIN从设备中删除
        #               if old_dev:
        #                               delEmpFromDev(None, oldObj, None)
        #dev=newObj.Device()
        #if dev: #需要把新的人员指纹传送到设备上
        #       if not oldObj or (int(oldObj.PIN)<>int(newObj.PIN)): #changed the PIN, 需要把指纹等都传送一遍
        #               appendEmpToDev(dev, newObj)
        #       else:                                           #只需要传送人员信息
        #               cmdStr=getEmpCmdStr(newObj)
        #               appendDevCmd(dev, cmdStr)
#                               backDev=dev.BackupDevice()
#                               if backDev: #把新的数据传送到登记考勤机的备份机上
#                                       appendDevCmd(backDev, cmdStr)

def DataChangeTitle(newObj):#作废
    spedy=USER_SPEDAY.objects.filter(UserID=newObj).exclude(State__in=[2,3,6])
    for sp in spedy:
        et=sp.EndSpecDay
        st=sp.StartSpecDay
        minunit=gettimediff(et,st)
        #minunit=gettimediff_byshift(sp.UserID_id,et,st)
        proc=getprocess(sp.UserID_id,sp.DateID,0,minunit)
        if len(proc)==0:
            roleid=0
            process=''
        else:
            roleid=proc[0]
            process=','.join(str(x) for x in proc)
            process=','+process+','
        sp.State=0
        sp.roleid=roleid
        sp.process=process
        sp.save()
    over=USER_OVERTIME.objects.filter(UserID=newObj).exclude(State__in=[2,3,6])
    for ov in over:
        minunit=ov.AsMinute
        proc=getprocess_EX(ov.UserID_id,10000,1)
        if len(proc)==0:
            roleid=0
            process=''
        else:
            roleid=proc[0]
            process=','.join(str(x) for x in proc)
            process=','+process+','
        ov.State=0
        ov.roleid=roleid
        ov.process=process
        ov.save()

def DataNewGet(request, dataModel):
    if dataModel==get_user_model():
        return retUserForm(request, adminForm(request), isAdd=True)
    if dataModel==iclock:
        return retIclockForm(request, iclockForm(request), isAdd=True)
    try:
        dataForm=form_for_instance(dataModel())
    except:
        dataForm=form_for_model(dataModel)

    return DataDetailResponse(request, dataModel, dataForm())

NON_FIELD_ERRORS = '__all__'

#需要系统自动关联的组权限添加到下面列表中
permissions=['browse_attshifts','browse_department',
        'browse_employee','browse_user_temp_sch',
        'browse_attrecabnormite','browse_attexception','browse_attprireport']
def AutoAddPermissions(dataModel,key):
    if dataModel==Group:
        try:
            perms=Permission.objects.filter(codename__in=permissions )
            for t in perms:
                sql="insert into %s(group_id,permission_id) values(%d,%d)" %('auth_group_permissions',int(key),t.id)
                customSql(sql)
        except:
            pass

def DataNewPost(request, dataModel):
    if dataModel.__name__=="USER_SPEDAY":
        return savespecialday(request,'_new_')
    elif dataModel.__name__=="USER_CONTRACT":
        return saveaddcontract(request,'_new_')
    elif dataModel.__name__=="userRoles":
        cache.delete("%s_userRoles"%(GetParamValue('ROLEVERSION')))
    elif dataModel.__name__=="days_off":
        return savedaysoff(request,'_new_')
    elif dataModel.__name__=="USER_OVERTIME":
        return saveOvertime(request,'_new_')
    elif dataModel==get_user_model():
        return doPostAdmin(request, dataModel, '_new_')
    elif dataModel==iclock:
        return doPostIclock(request, dataModel, '_new_')
    elif dataModel==UserACPrivilege:
        return saveUserACPrivliege(request,'_new_')
    elif dataModel==checkexact:
        return saveCheckForget(request,'_new_')
    elif dataModel==level:
        from mysite.acc.level_door import savelevel
        return savelevel(request,'_new_')
    elif dataModel==linkage:
        from mysite.acc.accviews import save_linkage
        return save_linkage(request,'_new_')
    elif dataModel==combopen_door:
        from mysite.acc.accviews import save_combopen_comb
        return save_combopen_comb(request,'_new_')
    elif dataModel==empleavelog:
        return save_empleave(request,'_new_')

    elif dataModel.__name__=='zone':
        from mysite.acc.models import zone
        code = request.POST.get('code')
        if zone.objects.filter(code=code).filter(DelTag=0):
            return getJSResponse({"ret":1,"message":u"%s"%_(u'区域编号已使用，保存失败')})
    elif dataModel.__name__=='employee':
        Card = request.POST.get('Card')
        if Card:
            if employee.objects.filter(Card=Card):
                return getJSResponse({"ret":1,"message":u"%s"%_(u'该卡号已被使用，保存失败')})
    elif dataModel.__name__=='Minute':
        FileNumber = request.POST.get('FileNumber')
        if len(FileNumber)>9:
            return getJSResponse({"ret":1,"message":u"%s"%_(u'档案编号长度过长，保存失败')})
    elif dataModel.__name__=='Meet_order':
        MeetID = request.POST.get('MeetID')
        d1=request.POST.get("Starttime")
        d2=request.POST.get("Endtime")
        if Meet_order.objects.filter(MeetID=MeetID):
            return getJSResponse({"ret":1,"message":u"%s"%_(u'会议编号已使用，保存失败')})
        if request.POST.get("LocationID"):
            if Meet.objects.filter(LocationID=request.POST.get("LocationID")).filter(DelTag=0).filter(Q(Starttime__gte=d1,Starttime__lte=d2)|Q(Starttime__lt=d1,Endtime__gt=d1)).exclude(MeetID=MeetID).count()>0:
                return getJSResponse({"ret":1,"message":u"%s"%_(u'会议室已被占用')})
    elif dataModel.__name__=='employee_borrow':
        from mysite.iclock.empborrow import save_empborrow
        return save_empborrow(request,'_new_')
    dataForm=form_for_model(dataModel)
    f=dataForm(request.POST)
    if f.is_valid():
        isAdd=True
        if dataModel in [LeaveClass]:
            cache.delete("%s_LeaveClass_0"%(settings.UNIT))
            cache.delete("%s_LeaveClass_1"%(settings.UNIT))
            cache.delete("%s_LeaveClass_2"%(settings.UNIT))
            #InitData(dataModel.__name__)

        #检查通过 DelTag 标记“删除”（隐藏）的数据
        #key=(dataModel._meta.pk.name in f.cleaned_data) and f.cleaned_data[dataModel._meta.pk.name] or None
        #if key:
        #       try:
        #               o=dataModel.objects.get(pk=key)
        #               deleted=True
        #               if fieldVerboseName(dataModel, "DelTag") and o.DelTag:
        #                       o.save()
        #                       return HttpResponseRedirect("../")
        #               #f.errors[dataModel._meta.pk.name]=[_("Duplicated")]
        #               return getJSResponse({"ret":1,"message":u"%s"%_('Duplicated')})#DataDetailResponse(request, dataModel, f)
        #       except ObjectDoesNotExist:
        #               pass
        try:
            #if dataModel==department:#当添加新部门时 只有数据库中没有一级部门时 才允许父部门为空 其它情况返回错误
            #    parent=request.POST['parent']
            #    if parent=='':
            #       if department.objects.filter(parent=0).count()>0:
            #           return getJSResponse({"ret":1,"message":"%s-%s"%(_('save failed'),_('parent is null'))})  #DataDetailResponse(request, dataModel, f)
            try:
                obj=f.save()
                #obj=f.save()
                if dataModel==department:#当添加新部门时 如果不是超级管理员将自动添加到自己的授权部门中
                    if not request.user.is_superuser:
                        DeptAdmin(user=request.user, dept_id=obj.DeptID,iscascadecheck=0).save()
                if dataModel.__name__=='zone':#当添加新区域时 如果不是超级管理员将自动添加到自己的授权区域中
                    if not request.user.is_superuser:
                        ZoneAdmin(user=request.user, code_id=obj.id,iscascadecheck=0).save()
                elif dataModel==SchClass:
                    if not request.user.is_superuser:
                        obj.TimeZoneOfDept=request.user.AutheTimeDept
                        obj.save()
                elif dataModel==NUM_RUN:
                    if not request.user.is_superuser:
                        obj.Num_RunOfDept=request.user.AutheTimeDept
                        obj.save()
                elif dataModel==timezones:
                    sendTimeZonesToAcc([obj],[])
                elif dataModel==InterLock:
                    sendInterLockToAcc([],[obj.device_id])
                elif dataModel==employee:
                    if obj.OffPosition==1:
                        obj.OffPositionDate = datetime.datetime.now()
                        obj.save()
                    saveFingerData(request,obj)
                elif dataModel==IssueCard:
                    if obj.card_privage==PRIVAGE_CARD or obj.card_privage==OPERATE_CARD:
                        obj.issuedate=datetime.datetime.now()
                        obj.save()
            except Exception,e:
                #print "----------",e
                estr=u"%s"%e
                #print "DataNewPost--",estr
                if  ("UNIQUE KEY" in estr)  or ("Duplicate entry" in estr) or ("unique constraint" in estr) or ("Duplicated" in estr):
                    if dataModel == forgetcause:
                        return getJSResponse({"ret":1,"message":u"%s"%_(u'数据重复')})
                    else:
                        return getJSResponse({"ret":1,"message":u"%s:%s"%(u'保存失败',_(u'数据重复'))})
                else:
                    if 'Meeting rooms occupied' in estr:
                        return getJSResponse({"ret":1,"message":u'%s-%s'%(_('save failed'),_(u'会议室被占用'))})

                    return getJSResponse({"ret":1,"message":u'%s %s'%(_('save failed'),estr)})
            key=obj.pk
            #用户新增的部门自动加入授 权表中
#                       if dataModel==department and not request.user.is_superuser:
#                           DeptAdmin(user=request.user, dept_id=int(key)).save()
            if dataModel in [Group,User]:# and (not request.user.is_superuser):
                UserAdmin(user=request.user, owned=int(key),dataname=str(dataModel._meta)).save()
#                           GroupAdmin(user=request.user, group_id=key).save()

        except Exception, e: #通常是不满足数据库的唯一性约束导致保存失败
            estr="%s"%e
            if ('IntegrityError' in estr) or ("UNIQUE KEY" in estr) or ("are not unique" in estr) or ("Duplicate entry" in estr):
                return getJSResponse({"ret":1,"message":u"%s"%_('Duplicated')})

            #f.errors[NON_FIELD_ERRORS]=u'<ul class="errorlist"><li>%s</li></ul>'%unicode(e.message)

            return getJSResponse({"ret":1,"message":u"%s"%e.message})  #DataDetailResponse(request, dataModel, f)
        DataPostCheck(request, None, obj)
        AutoAddPermissions(dataModel,key)
        if dataModel.__name__=='Announcement':
            log=adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name,object = request.META["REMOTE_ADDR"])#
        else:
            log=adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, object=u"%s"%obj)#
        log.action=u'%s'%_("Create")
        log.save(force_insert=True)

        popup = request.GET.get("_popup", "")
        if popup:
            the_add_object = unicode(obj)
            return HttpResponse(u'<script type="text/javascript">\nopener.dismissAddAnotherPopup(window, "%s", "%s");\n</script>' % (key, the_add_object))

        return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})
    return DataDetailResponse(request, dataModel, f)


@login_required
def DataNew(request, ModelName):
    appName=request.path.split('/')[1]

    dataModel=GetModel(ModelName,appName)
    operation=''
    if dataModel in [InterLock,linkage,AntiPassBack,FirstOpen,combopen_door]:
        operation='acc.add_interlock'
    if dataModel in [empleavelog]:
        operation='iclock.empLeave_employee'
    if dataModel!=Announcement and  (not hasPerm(request.user, dataModel, "add")) and (not request.user.has_perm(operation)):
        return getJSResponse(u"<div>%s</div>" % _("You do not have the permission!"),mtype='text/html')#render_to_response("info.html", {"title": title, "content": _("You do not have the permission!")});

        #return NoPermissionResponse()
#       if not dataModel: return NoFound404Response(request)

    if request.method=="POST":
        return DataNewPost(request, dataModel)
    return DataNewGet(request, dataModel)

@login_required
def apply_DataNew(request, ModelName):
    appName=request.path.split('/')[1]
    dataModel=GetModel(ModelName,appName)
    # if dataModel!=Announcement and  (not hasPerm(request.user, dataModel, "add")):
    #       return NoPermissionResponse()
#       if not dataModel: return NoFound404Response(request)

    if request.method=="POST":
        return DataNewPost(request, dataModel)
    return DataNewGet(request, dataModel)

def DataChangeGet(request, dataModel, dataForm, emp):

    f=dataForm()
    if dataModel==iclock:
        backupDevice=""#emp.BackupDevice()
#               print "backupDevice", backupDevice
        if backupDevice:
            backupDevice=backupDevice.SN
        else:
            backupDevice=""
    if dataModel in [SchClass,holidays,NUM_RUN,days_off]:
        InitData(dataModel.__name__)
    return DataDetailResponse(request, dataModel, f, key=emp.pk, instance=emp)

def DataChangePost(request, dataModel, dataForm, emp):
    f=dataForm(request.POST)
    if f.is_valid():
        #检查有没有改变关键字段
        key=(dataModel._meta.pk.name in f.cleaned_data) and f.cleaned_data[dataModel._meta.pk.name] or emp.pk
        key_for_popup = key
        if key and "unicode" not in str(type(key)):
            key = unicode(key)
        if key and ('%s'%emp.pk)!=('%s'%key):
            f.errors[dataModel._meta.pk.name]=_('Keyword "%(object_name)s" can not to be changed!')%{'object_name':fieldVerboseName(dataModel, dataModel._meta.pk.name)};
            #return DataDetailResponse(request, dataModel, f, key=emp.pk)
            return getJSResponse({"ret":1,"message":u"%s"%f.errors[dataModel._meta.pk.name]})
        oldEmp=None
        if dataModel==employee:
            oldEmp=employee.objByID(emp.id)
        if dataModel==userRoles:
            oldrole=userRoles.objects.get(roleid=emp.roleid)
            try:
                f.save()
            except:
                return getJSResponse({"ret":1,"message":u"%s"%_(u'保存失败,职务编号或职务名称已被使用')})
        #if dataModel==department:#当编辑部门时 只有被编辑的部门的父部门为0时 才允许父部门为空 其它情况返回错误
        #       parent=request.POST['parent']
        #       if parent=='':
        #               if department.objects.filter(DeptID=key,parent=0).count()==0:
        #                       return getJSResponse({"ret":1,"message":(_('save failed'),_('parent is null'))})#DataDetailResponse(request, dataModel, f)

        #if dataModel==SchClass:
        #    if (NUM_RUN_DEIL.objects.filter(SchclassID=key).count()>0) or (USER_TEMP_SCH.objects.filter(SchclassID=key).count()>0):
        #       return getJSResponse({"ret":1,"message":_(u"欲删除的时段已被使用，不允许删除和修改！")})


        try:
            newObj=f.save()
        except Exception, e: #通常是不满足数据库的唯一性约束导致保存失败
            #import traceback;traceback.print_exc()
            #print "DataChangePost==",e
            return getJSResponse({"ret":1,"message":u"%s %s"%(_('save failed'),e)})
        #if dataModel==iclock:
        #   if (not newObj.ProductType) or (newObj.ProductType!=5):
        #       appendDevCmd(newObj, "CHECK") #命令设备读取服务器上的配置信息
            #sn=request.POST["BackupDev"]
            #oldsn=emp.BackupDev
            #if sn and oldsn!=sn: #设置了一个新的备份设备，则把该设备登记的指纹复制到新的备份设备上
            #       copyDevEmpToDev(getDevice(sn), emp)
            #if sn!=newObj.BackupDev:
            #       newObj.BackupDev = sn
            #       newObj.save()
        if dataModel in [Group,User] and (not request.user.is_superuser):
            try: #key 为unicode 类型 owned需要 整型 捕获 不满足数据库的唯一性约束导致保存失败 (1062, "Duplicate entry '2-4-auth.group' for key 'user_id'" 异常
                UserAdmin(user=request.user,owned=int(key),dataname=str(dataModel._meta)).save()
            except Exception, e:
                pass
#                               print e
        elif dataModel in [timezones]:
            sendTimeZonesToAcc([newObj],[])
        elif dataModel in [AccDoor]:
            if request.POST.get('_copy','')=='1':
                from mysite.acc.accviews import saveParamsToOtherDoor
                saveParamsToOtherDoor(request,newObj)
            else:
                sendDoorToAcc([newObj],[newObj.device_id])
        elif dataModel in [InterLock]:
            sendInterLockToAcc([],[newObj.device_id])
        elif dataModel==employee:
            if newObj.OffPosition==1:
                newObj.OffPositionDate=datetime.datetime.now()
                newObj.save()
            saveFingerData(request,newObj)
        elif dataModel==userRoles:
            emps=employee.objects.filter(Title=oldrole.roleName)
            for e in emps:
                e.Title=newObj.roleName
                e.save()
#                       GroupAdmin(user=request.user, group_id=key).save()
        DataPostCheck(request, oldEmp or emp, newObj)
        AutoAddPermissions(dataModel,key)
        emp=u"%s"%emp
        if dataModel.__name__=='Announcement':
            log=adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, object=request.META["REMOTE_ADDR"])#
        else:
            log=adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, object=emp[0:100])#
        log.action=u'%s'%_("Modify")
        log.save(force_insert=True)
        return getJSResponse({"ret":0,"message":""})
    return DataDetailResponse(request, dataModel, f, key=emp.pk)

@login_required
def DataDetail(request, ModelName, DataKey):
    dataModel=GetModel(ModelName,request.path.split('/')[1])
    appName=request.path.split('/')[1]


    operation='%s.change_%s'%(appName,dataModel.__name__.lower())
    if dataModel in [AuxIn,AuxOut]:
        operation='%s.change_%s'%(appName,AccDoor.__name__.lower())
    #dataModel=GetModel(ModelName)
    if (not hasPerm(request.user, dataModel, "change")) and (not request.user.has_perm(operation)) and dataModel!=Announcement:#Announcement表用户没有编辑权限时为了方便查询允许弹出编辑对话框
        return NoPermissionResponse()
    if not dataModel:
        return NoFound404Response(request)
    if dataModel.__name__=="userRoles":
        if request.method=="POST":
            cache.delete("%s_userRoles"%(GetParamValue('ROLEVERSION')))
    elif dataModel.__name__=="USER_SPEDAY":
        if request.method=="POST":
            return savespecialday(request,DataKey)
    elif dataModel.__name__=="days_off":
        if request.method=="POST":
            return savedaysoff(request,DataKey)
    elif dataModel.__name__=="USER_OVERTIME":
        if request.method=="POST":
            return saveOvertime(request,DataKey)
    elif dataModel==UserACPrivilege:
        if request.method=="POST":
            return saveUserACPrivliege(request,DataKey)
    elif dataModel==get_user_model():       # 管理员 管理
        from mysite.iclock.admin_detail_view import doPostAdmin,doCreateAdmin
        if request.method=="POST":
            return doPostAdmin(request, dataModel, DataKey)
        else:#编辑管理员
            return doCreateAdmin(request, dataModel, DataKey)
    elif dataModel==iclock: # iclock
        from mysite.iclock.admin_detail_view import doPostIclock,doCreateIclock
        if request.method=="POST":
            return doPostIclock(request, dataModel, DataKey)
        else:
            return doCreateIclock(request, dataModel, DataKey)
    elif dataModel==checkexact:
        if request.method=="POST":
            return saveCheckForget(request,DataKey)
    elif dataModel==level:
        if request.method=="POST":
            from mysite.acc.level_door import savelevel
            return savelevel(request,DataKey)
    elif dataModel in [linkage]:
        if request.method=="POST":
            from mysite.acc.accviews import save_linkage
            return save_linkage(request,DataKey)
    elif dataModel in [combopen_door]:
        if request.method=="POST":
            from mysite.acc.accviews import save_combopen_comb
            return save_combopen_comb(request,DataKey)
    backupDevice=""
    emp=dataModel.objects.in_bulk([DataKey])
    if emp=={}:
        return NoFound404Response(request)
        #render_to_response("info.html", {
        #       "title": _("Edit %(object_name)s")%{"object_name":dataModel._meta.verbose_name},
        #       "content": _("Keyword \"%(object_name)s\" data do not exist!")%{'object_name':DataKey}});
    emp=emp[emp.keys()[0]]
    try:
        dataForm=form_for_instance(emp)
    except:
        dataForm=form_for_model(dataModel)
    if request.method=="POST":
        return DataChangePost(request, dataModel, dataForm, emp)

    return DataChangeGet(request, dataModel, dataForm, emp)

def getValidDevOptions():
    return ["AutoPowerSuspend","COMKey"]

def getDevFromReq(request):
    key=request.GET.get("SN",'')
    keys=key.split(',')
    try:
        if len(keys)>1:
            ddevs=[]
            for k in keys:
                ddev=getDevice(k)
                ddevs.append(ddev)
            return ddevs
        else:
            ddev=getDevice(key)
            return ddev
    except:
        errorLog(request)
        return None

def strToDateDef(s, defTime=None):
    import time
    d=datetime.datetime.now()
    try:
        t=time.strptime(s, settings.STD_DATETIME_FORMAT)
        d=datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday,
                t.tm_hour, t.tm_min, t.tm_sec)
    except:
        try:#只有日期
            t=time.strptime(s, settings.STD_DATETIME_FORMAT.split(" ")[0])
            if defTime:
                d=datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, defTime[0], defTime[1], defTime[2])
            else:
                d=datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday)
        except Exception, e: #只有时间
#                       print e.message
            t=time.strptime(s, settings.STD_DATETIME_FORMAT.split(" ")[1])
            d=datetime.datetime(d.year, d.month, d.day,
                    t.tm_hour, t.tm_min, t.tm_sec)
    return d

def doAction(action, request, dataModel):
    cursor=conn.cursor()
    action=string.strip(action)
    ret=None
    errorInfo=""
    if action=="del":
        try:
            delData(request, dataModel)
        except Exception,e:
            #print "delData=",u"%s"%(e)
            errorInfo=u"%s"%e

    elif action=="pause":
        staData(request, dataModel, DEV_STATUS_PAUSE)
    elif action=="resume":
        staData(request, dataModel, DEV_STATUS_OK)
    elif action=="noalarm":
        batchOp(request, dataModel, lambda d: devNoAlarm(d, request))
    elif action=="cleardata":
        batchOp(request, dataModel, lambda d: clearDevData(d))
    elif action=="clearlog":
        batchOp(request, dataModel, lambda d: appendDevCmd(d, "CLEAR LOG"))
    elif action=="clearpic":
        batchOp(request, dataModel, lambda d: appendDevCmd(d, "CLEAR PHOTO"))
    elif action=="deptEmptoDevbyPIN":
        emp=request.POST.get('PIN__in')
        finger=1
        face=1
        PIC=1
        emplist=emp.split(',')

        if request.method == 'POST':
            keys=request.POST.getlist("K")
        else:
            keys=request.GET.getlist("K")
        t1=datetime.datetime.now()
        settings.DEV_STATUS_SAVE=1
        counts=0
        for emp in emplist:
            try:
                emps=employee.objByPIN(emp)
                appendEmpToDevNew(keys, emps, cursor,finger=finger,face=face,PIC=PIC)
                counts+=1
            except:
                pass
        settings.DEV_STATUS_SAVE=0
        if len(keys)<3:
            for i in keys:
                d=dataModel.objects.in_bulk([i])
                dev=d[d.keys()[0]]
                sendRecCMD(dev)
        t1=datetime.datetime.now()-t1
        #print "batchOp waste time===============",t1
        return getJSResponse({"ret":0,"message":u"%s,共计%s人"%(_('Operation Successful'),counts)})
    elif action=="deptEmptoDev":
        emp=request.POST.get('userids')
        deptid=request.POST.get('deptIDs')
        isalldev=request.POST.get('foralldev','0')
        isContainedChild=request.POST.get('isContainChild',"")
        finger=request.POST.get('finger',0)
        face=request.POST.get('face',0)
        PIC=request.POST.get('PIC',0)
        vein=request.POST.get('vein',0)
        palm=request.POST.get('palm',0)
        # if finger==0 and face==0 and PIC==0:
        #       finger=1
        #       face=1
        #       PIC=1
        if emp=='':
            deptidlist=[int(i) for i in deptid.split(',')]
            deptids=deptidlist
            if isContainedChild=="1":   #是否包含下级部门
                deptids=[]
                for d in deptidlist:#支持选择多部门
                    if int(d) not in deptids :
                        deptids+=getAllAuthChildDept(d,request)
            emps=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1)
        else:
            emplist=emp.split(',')
            emps=employee.objects.filter(id__in=emplist,OffDuty__lt=1).exclude(DelTag=1)
        if request.method == 'POST':
            keys=request.POST.getlist("K")
        else:
            keys=request.GET.getlist("K")
        if isalldev=='1':
            if request.user.is_superuser or request.user.is_alldept:
                keys=iclock.objects.all().exclude(Q(State=0)|Q(DelTag=1)).values_list('SN', flat=True)
            else:
                keys=AuthedIClockList(request.user)
        t1=datetime.datetime.now()
        settings.DEV_STATUS_SAVE=1
        try:
            deptEmptoDev(keys,emps,cursor,finger,face,PIC,palm,vein)
        except:
            pass
        settings.DEV_STATUS_SAVE=0
        if len(keys)<3:
            for i in keys:
                d=dataModel.objects.in_bulk([i])
                dev=d[d.keys()[0]]
                sendRecCMD(dev)
        t1=datetime.datetime.now()-t1
        print "batchOp waste time===============",t1
#               batchOp(request,dataModel,lambda d:deptEmptoDev(d,emps,cursor))
    elif action=="deptEmptoDelete":
        settings.DEV_STATUS_SAVE=1
        deleteEmpFromDevice(request)
        settings.DEV_STATUS_SAVE=0
    elif action=="delFingerFromDev":
        settings.DEV_STATUS_SAVE=1
        delFingerFromDev(request)
        settings.DEV_STATUS_SAVE=0
    elif action=="delFaceFromDev":#按部门删除设备上的人员面部信息
        settings.DEV_STATUS_SAVE=1
        delFaceFromDev(request)
        settings.DEV_STATUS_SAVE=0
    elif action=="info":
        Message="INFO"
        batchOp(request, dataModel, lambda d: appendDevCmd(d, Message))
    elif action=="sendMessage":#sendMessage
        msg=string.strip(request.REQUEST['MSG'])
        ischeck=string.strip(request.REQUEST['ischeck'])
#               tag=int(string.strip(request.REQUEST['TAG']))
        Message="SMS MSG=%s\tTAG=%d"%(msg,253)
#               if(tag==254):
        uid=int(string.strip(request.GET.get('UID')))
        Message+="\tUID=%d"%(uid)
        if(ischeck=="true"):
            min=int(string.strip(request.REQUEST['MIN']))
            st=string.strip(request.REQUEST['StartTime'])
            Message+="\tMIN=%d\tStartTime=%s "%(min,st)
        else:
            st=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Message+="\tMIN=0\tStartTime=%s "%(st)
        batchOp(request, dataModel, lambda d: appendDevCmd(d, Message))
    elif action=="ACCStatus":
        batchOp(request, dataModel, lambda d: appendDevCmd(d, "ACC Status"))
    elif action=="QUERYUSERINFO":

        batchOp(request, dataModel, lambda d: appendDevCmd(d, "QUERY USERINFO PIN="))
    elif action=="check":
        batchOp(request, dataModel, lambda d: devCheckData(d))
    elif action=="restart":
        batchOp(request, dataModel, lambda d: appendDevCmd(d, "RESTART"))
    elif action=="reboot":
        batchOp(request, dataModel, rebootDevice)
    elif action=="reloaddata":
        if request.method == 'POST':
            keys=request.POST.getlist("K")
            empofdevice.objects.filter(SN__in=keys).delete()
        batchOp(request, dataModel, lambda d: reloadDataCmd(d))
#       elif action=="reloadlogdata":
#               batchOp(request, dataModel, lambda d: reloadLogDataCmd(d))
    elif action=="synEmptoDev":
        if request.method == 'POST':
            keys=request.POST.getlist("K")
        else:
            keys=request.GET.getlist("K")
        nt=datetime.datetime.now()
        if settings.PIRELLI:
            devs=iclock.objects.filter(SN__in=keys)
            deptnum=[99,]
            for dev in devs:
                try:
                    _Alias=int(dev.Alias.split('-')[1])
                    deptnum.append(_Alias)
                except:
                    pass
                dep=department.objects.filter(DeptNumber__in=deptnum)
                emps=employee.objects.filter(DeptID__in=dep).exclude(DelTag=1).exclude(OffDuty=1)
                for emp in emps:
                    appendEmpToDevNew([dev.SN], emp, cursor=None,cmdTime=nt,finger=1,face=1,PIC=1)
        else:
            for k in keys:
                depts=getDepartmentBySN(k)
                if -1 not in depts:
                    emps=employee.objects.filter(DeptID__in=depts).exclude(DelTag=1).exclude(OffDuty=1)
                else:
                    emps=employee.objects.all().exclude(DelTag=1).exclude(OffDuty=1)
                for emp in emps:
                    appendEmpToDevNew([k], emp, cursor=None,cmdTime=nt,finger=1,face=1,PIC=1)


    elif action=="loaddata":
        batchOp(request, dataModel, lambda d: appendDevCmd(d, "CHECK"))
    elif action=="upgradefw":
        errorInfo=batchOp(request, dataModel, lambda d: devUpdateFirmware(d))
    elif action=="devoption":
        optName=string.strip(request.REQUEST['name'])
        optVal=string.strip(request.REQUEST['value'])
        if optName in getValidDevOptions():
            #optName="SET OPTION %s=%s"%(optName, optVal)
            batchOp(request, dataModel, lambda d: setOptionCmd(d, optName,optVal))
            #batchOp(request, dataModel, lambda d: appendDevCmd(d, optName))

        else:
            errorInfo=_("Device options \"%s\" Unavailable!")%optName;
    elif action=="resetPwd":
        pin=string.strip(request.POST.get('PIN',''))
        pwd=string.strip(request.POST.get('Passwd'))
        ret=batchOp(request, dataModel, lambda dev: resetPwd(dev, pin, pwd, cursor))
    elif action=="restoreData":
        ret=batchOp(request, dataModel, lambda dev: restoreData(dev, cursor))
    elif action=="unlock":
        ret=batchOp(request, dataModel, lambda dev: appendDevCmd(dev, "AC_UNLOCK"))
    elif action=="unalarm":
        ret=batchOp(request, dataModel, lambda dev: appendDevCmd(dev, "AC_UNALARM"))
    elif (action=="upload_ac" or action=='upload_userac'):#传送门禁基本设置
        if request.method == 'POST':
            keys=request.POST.getlist("K")
        else:
            keys=request.GET.getlist("K")
        if action=="upload_ac":
            uploadACDevCmd(keys)
        else:
            uploadUserACDevCmd(keys)


    elif action=="copy":
        src=string.strip(request.REQUEST['source'])
        src=dataModel.objects.get(pk=src)
        fields=request.REQUEST["fields"].split(";")
        batchOp(request, dataModel, lambda obj: copyFromData(dataModel, obj, src, fields))
    elif action=="copyudata": #备份登记数据到其他设备
        ddev=getDevFromReq(request)
        if not ddev:
            errorInfo=_("Designated device does not exist!")
        else:
            ret=batchOp(request, dataModel, lambda dev: copyDevEmpToDev(ddev, dev, cursor))
    elif action=="reloadAppointlogdata":
        date=request.GET["start"]
        enddate=request.GET["end"]
        is_all=request.GET["is_all"]
        if request.method == 'POST':
            keys=request.POST.getlist("K")
        else:
            keys=request.GET.getlist("K")
        for sn in keys:
            dev=getDevice(sn)
        if is_all=='on' and date=='' and not DevIdentity(dev,"push"):
            batchOp(request, dataModel, lambda d: reloadLogDataCmd(d))
        else:
            batchOp(request, dataModel, lambda d: reloadLogAppointDataCmd(d,date,enddate,is_all))
    elif action=="attdataProof":
        date=request.GET["start"]
        enddate=request.GET["end"]
        if request.method == 'POST':
            keys=request.POST.getlist("K")
        else:
            keys=request.GET.getlist("K")
        for sn in keys:
            dev=getDevice(sn)
            if not DevIdentity(dev,"push"):
                errorInfo+="<span class='Se_Tran_errorlist'>%s%s</span>"%(sn,_(u"Device does not support this function, the operation failed!</br>"))#机器不支持此功能，操作失败！
            else:
                attdataProofCmd(dev,date,enddate)
                errorInfo+="<span class='Se_Tran_cglist'>%s%s!</br></span>"%(sn,_(u"Operation Successful"))
    elif action=="accEmptoDev":#acc module#传送人员到设备
        emplist=request.POST.getlist("K")
        emps=employee.objects.filter(id__in=emplist)
        sendLevelToAccEx(emps,[])
    elif action=="accEmpFromDev_DEL":#acc module
        emplist=request.POST.getlist("K")
        emps=employee.objects.filter(id__in=emplist)
        Levels=list(level_emp.objects.filter(UserID__in=emps).distinct().values_list('level',flat=True))
        try:

            objs=level_emp.objects.filter(UserID__in=emps)
            level_emp_key=[]
            for t in objs:
                level_emp_key.append(t.id,)



            deleteEmpfromAcc(Levels,emps,level_emp_key)
        except Exception,e:
            print "=======",e
    elif action=="toDev":
        key=request.GET.get("SN")
        keys=key.split(',')
        if request.method == 'POST':
            emplist=request.POST.getlist("K")
            emps=employee.objects.filter(id__in=emplist)
        settings.DEV_STATUS_SAVE=1
        try:
            deptEmptoDev(keys,emps,cursor,finger=1,face=1,PIC=1)
        except:
            pass
        settings.DEV_STATUS_SAVE=0
        if len(keys)<3:
            for sn in keys:
                dev=getDevice(sn)
                sendRecCMD(dev)


        #ddevs=getDevFromReq(request)
        #if not ddevs:
            #errorInfo=_("Designated device does not exist!")
        #else:
            #if isinstance(ddevs,list):
                #for ddev in ddevs:
                #ret=batchOp(request, dataModel, lambda emp: appendEmpToDev(ddev, emp, cursor))
            #else:
                #ret=batchOp(request, dataModel, lambda emp: appendEmpToDev(ddevs, emp, cursor))
    elif action=="toDevPic":#传送人员照片到设备
        key=request.GET.get("SN")
        keys=key.split(',')
        if request.method == 'POST':
            emplist=request.POST.getlist("K")
            emps=employee.objects.filter(id__in=emplist)
        settings.DEV_STATUS_SAVE=1
        try:
            deptEmpPICtoDev(keys,emps,cursor,pic=1)
        except:
            pass
        settings.DEV_STATUS_SAVE=0
        if len(keys)<3:
            for sn in keys:
                dev=getDevice(sn)
                sendRecCMD(dev)
    elif action=="toDevWithin":#临时调拨人员到设备
        key=request.GET.get("SN")
        keys=key.split(',')
        if not keys:
            errorInfo=_("Designated device does not exist!")
        else:
            try:
                startTime=strToDateDef(string.strip(request.GET.get('start')), False)
                endTime=strToDateDef(string.strip(request.GET.get('end')), (23,59,59))
                if isinstance(keys,list):
                    ret=batchOp(request, dataModel, lambda emp: appendEmpToDevWithin(keys, emp, startTime, endTime, cursor))
                else:
                    ret=batchOp(request, dataModel, lambda emp: appendEmpToDevWithin(keys, emp, startTime, endTime, cursor))
            except Exception, e:
                errorInfo=e.message
    elif action=="mvToDev":
        key=request.GET.get("SN")
        keys=key.split(',')
        if not keys:
            errorInfo=_("Designated device does not exist!")
        else:
            if isinstance(keys,list):
                ret=batchOp(request, dataModel, lambda emp: moveEmpToDev(keys, emp, cursor))
            else:
                ret=batchOp(request, dataModel, lambda emp: moveEmpToDev(keys, emp, cursor))
    elif action=="delDev":
        key=request.GET.get("SN")
        keys=key.split(',')
        uids=request.POST.getlist("K")
        if not keys:
            errorInfo=_("Designated device does not exist!")
        else:
            emps=employee.objects.filter(id__in=uids)
            for emp in emps:
                for k in keys:
                    device=getDevice(k)
                    zk_delete_user_data(device,emp.pin())

                #appendDevCmdNew(keys, "DATA DEL_USER PIN=%s"%emp.pin(), cursor)
            #if isinstance(keys,list):
            #       print keys
            #       ret=batchOp(request, dataModel, lambda emp: appendDevCmdNew(keys, "DATA DEL_USER PIN=%s"%emp.pin(), cursor))
            #else:
            #       ret=batchOp(request, dataModel, lambda emp: appendDevCmdNew(keys, "DATA DEL_USER PIN=%s"%emp.pin(), cursor))
            #
        # for sn in keys:
        #   for userid in uids:
        #     pin=employee.objByID(userid).PIN
        #     delEmpInDevice(pin,sn)

    elif action=="delDevPic":#从设备中删除人员照片
        key=request.GET.get("SN")
        keys=key.split(',')
        if not keys:
            errorInfo=_("Designated device does not exist!")
        else:
            if isinstance(keys,list):
                ret=batchOp(request, dataModel, lambda emp: appendDevCmdNew(keys, "DATA DELETE USERPIC PIN=%d"%int(emp.pin()), cursor))
            else:
                ret=batchOp(request, dataModel, lambda emp: appendDevCmdNew(keys, "DATA DELETE USERPIC PIN=%d"%int(emp.pin()), cursor))

    elif action=='empLeave':
        errorInfo=batchOp(request, dataModel, lambda emp: empLeave(emp))
        iclocks=iclock.objects.filter(ProductType__in=[5,15,25])
        uids=request.POST.getlist("K")
        emps=employee.objects.filter(id__in=uids)
        for t in emps:
            emppin=t.pin()
            if settings.IDFORPIN==1:
                emppin=t.id
            for dev in iclocks:
                delete_data(dev.SN,'user','Pin=%s'%emppin)
            level_emp.objects.filter(UserID=t).delete()
            try:
                leavelogs=empleavelog.objects.filter(UserID=t)
                if leavelogs:
                    for leavelog in leavelogs:
                        leavelog.deltag = 0
                        leavelog.save()
                else:
                    empleavelog(UserID=t, leavedate=datetime.datetime.now(),leavetype=0, reason='', createtime=datetime.datetime.now(),deltag=0).save()
            except Exception, e:
                print e.message
    elif action=='EmpLeaverestore':#离职恢复
        keys=request.POST.getlist("K")
        leavs=empleavelog.objects.filter(id__in=keys)
        for leave in leavs:
            try:
                restoreEmpLeave(leave.UserID)
                leave.deltag = 1
                leave.save()
            except Exception, e:
                print e.message
    elif action=='Empborrowrestore':
        keys=request.POST.get("id")
        pin=request.POST.get("pin")
        title=request.POST.get("title")
        
        eb = employee_borrow.objects.get(id=keys)
        eb.state=1
        eb.OpTime = datetime.datetime.now()
        eb.save()
        
        userID = eb.userID
        fromDept = eb.fromDept
        user = employee.objByID(userID)
        dept = department.objByID(fromDept)
        user.Workcode = pin
        user.DeptID = dept
        user.Title = title
        user.bstate = 2
        user.save()
    elif action=='restoreEmpLeave':
        uids=request.POST.getlist("K")
        emps=employee.objects.filter(id__in=uids)
        for t in emps:
            leavelogs=empleavelog.objects.filter(UserID=t)
            for leave in leavelogs:
                try:
                    leave.deltag = 1
                    leave.save()
                except Exception, e:
                    print e.message 
        errorInfo=batchOp(request, dataModel, lambda emp: restoreEmpLeave(emp))
    elif action=='enrollAEmp':
        errorInfo=batchOp(request, dataModel, lambda emp: enrollAEmp(None, emp))
    elif action=="toDepart":
        key=string.strip(request.GET["department"])
        if key=='null':
            errorInfo=_("Please select department!")
        else:
            try:
                dept=department.objects.get(DeptID=key)
            except:
                #errorLog(request)
                errorInfo=_("%(name)s %(key)s does not exist!")%{'name':department._meta.verbose_name, 'key':key}
                dept=None
            if dept:
                batchOp(request, dataModel, lambda emp: changeEmpDept(dept, emp))
    elif action=="leaveAudit":
        if request.GET.get("to", "")=="Accept":
            ss=staDataLeave(request, dataModel, 2)
        elif request.GET.get("to", "")=="Refuse":
            ss=staDataLeave(request, dataModel, 3)
        elif request.GET.get("to", "")=="Again":
            ss=staDataLeave(request, dataModel, 6)
        if ss:
            errorInfo=ss
    elif action=="orderAudit":
        if request.GET.get("to", "")=="Accept":
            ss=staDataOrder(request, dataModel, 2)
        elif request.GET.get("to", "")=="Refuse":
            ss=staDataOrder(request, dataModel, 3)
        if ss:
            errorInfo=ss
    elif action=="forgetAudit":
        if request.GET.get("to", "")=="Accept":
            if request.user.is_superuser:
                ss=staDataForget(request, dataModel, 2)
            else:
                keys=request.POST.getlist("K")
                for i in keys:
                    u=checkexact.objects.get(id=int(i))
                    if trunc(u.CHECKTIME)==trunc(datetime.datetime.now()):
                        ss=staDataForget(request, dataModel, 2)
                    else:
                        return getJSResponse({"ret":1,"message":u'%s'%_(u'无权限审核')})
        elif request.GET.get("to", "")=="Refuse":
            ss=staDataForget(request, dataModel, 3)
        elif request.GET.get("to", "")=="Again":
            ss=staDataForget(request, dataModel, 6)
        if ss:
            errorInfo=ss
    elif action=="overtimeAudit":
        if request.GET.get("to", "")=="Accept":
            ss=staDataOver(request, dataModel, 2)
        elif request.GET.get("to", "")=="Refuse":
            ss=staDataOver(request, dataModel, 3)
        elif request.GET.get("to", "")=="Again":
            ss=staDataOver(request, dataModel, 6)
        if ss:
            errorInfo=ss
#               elif request.REQUEST.get("to", "")=="Re-Apply":
#                       staData(request, dataModel, 5)
    elif action=="leaveRemove":
        staData(request, dataModel, 7)
    elif action=="moveDept":
        id=request.GET.get('id',-1)
        pid=request.GET.get('pid',-1)
        if id==-1 or pid==-1:
            errorInfo=u"%s"%_(u"move error")
        else:
            d=department.objByID(id)
            d.parent=pid
            d.save()
    elif action=='setDeviceAuthedDept':
        #print request.POST
        keys=request.POST.getlist("K")
        authData=request.POST.get('authdata','')
        authData=loads(authData)
        for k in keys:
            IclockDept.objects.filter(SN=k).delete()
            for t in authData:
                sql,params=getSQL_insert_new(IclockDept._meta.db_table,SN_id=k,dept_id=t['deptid'],iscascadecheck=t['iscascadecheck'])
                try:
                    customSqlEx(sql,params)
                except Exception,e:
                    connection.commit()
                    print "setDeviceAuthedDept=",e
                    errorInfo=u'%s保存出现错误'%k
            device=getDevice(k)
            reloadDataCmd(device)
            if device:
                device.TransTime=datetime.datetime(2000,1,1,0,0)
                device.save()

        UpdateDeptCache()


    elif action=='setDeviceAuthedZone':
        #print request.POST
        keys=request.POST.getlist("K")
        authData=request.POST.get('authdata','')
        authData=loads(authData)
        for k in keys:
            IclockZone.objects.filter(SN=k).delete()
            for t in authData:
                sql,params=getSQL_insert_new(IclockZone._meta.db_table,SN_id=k,zone_id=t['deptid'],iscascadecheck=t['iscascadecheck'])
                try:
                    customSqlEx(sql,params)
                except Exception,e:
                    connection.commit()
                    print "setDeviceAuthedZone=",e
                    errorInfo=u'%s保存出现错误'%k
    elif action=='setDeviceAuthedDining':
        keys=request.POST.getlist("K")
        authData=request.POST.get('authdata','')
        authData=loads(authData)
        for k in keys:
            IclockDininghall.objects.filter(SN=k).delete()
            for t in authData:
                sql,params=getSQL_insert_new(IclockDininghall._meta.db_table,SN_id=k,dining_id=t['deptid'])
                try:
                    customSqlEx(sql,params)
                except Exception,e:
                    connection.commit()
                    print "setDeviceAuthedDining=",e
                    errorInfo=u'%s保存出现错误'%k

    elif action=='setUserAuthedDept':
    #       print "------",request.POST
        keys=request.POST.getlist("K")
        authData=request.POST.get('authdata','')
        authData=loads(authData)
        for k in keys:
            DeptAdmin.objects.filter(user=k).delete()
            for t in authData:
                sql,params=getSQL_insert_new(DeptAdmin._meta.db_table,user_id=k,dept_id=t['deptid'],iscascadecheck=t['iscascadecheck'])
                try:
                    #print "-----------",sql,params
                    customSqlEx(sql,params)
                except Exception,e:
                    connection.commit()
                    #print "setUserAuthedDept=",e
                    errorInfo=u'%s保存出现错误'%k
                cache.delete("%s_userdepts_%s_%s"%(settings.UNIT, k,settings.DEPTVERSION))
                cache.delete("%s_depttree_%s_%s"%(settings.UNIT, k,settings.DEPTVERSION))
                cache.delete("%s_iclockdepts_%s_%s"%(settings.UNIT, k,settings.DEPTVERSION))

    elif action=='setUserAuthedZone':
    #       print "------",request.POST
        keys=request.POST.getlist("K")
        authData=request.POST.get('authdata','')
        authData=eval(authData)
        for k in keys:
            ZoneAdmin.objects.filter(user=k).delete()
            for t in authData:
                sql,params=getSQL_insert_new(ZoneAdmin._meta.db_table,user_id=k,code_id=t)
                try:
                    #print "-----------",sql,params
                    customSqlEx(sql,params)
                except Exception,e:
                    connection.commit()
                    print "setUserAuthedZone=",e
                    errorInfo=u'%s保存出现错误'%k
    elif action=='roomPause':
        keys=request.POST.getlist("K")
        MeetLocation.objects.filter(id__in=keys).update(State=2)
    elif action=='roomUpload':
        keys=request.POST.getlist("K")
        MeetLocation.objects.filter(id__in=keys).update(State=2)
    elif action=='roomReset':
        keys=request.POST.getlist("K")
        MeetLocation.objects.filter(id__in=keys).update(State=0)
    elif action=='add_meet_devices':
        key=request.GET.get("SN")
        keys=key.split(',')
        if request.method == 'POST':
            roomlist=request.POST.getlist("K")
            for t in roomlist:
                for k in keys:
                    sql,params=getSQL_insert_new(meet_devices._meta.db_table,LocationID_id=t,SN_id=k)
                    try:
                        #print sql,params
                        customSqlEx(sql,params)
                    except Exception,e:
                        #print e
                        pass



    elif action=='participants_del':
        keys=request.POST.getlist("K")
        participants_details.objects.filter(participants_tplID__in=keys).delete()
    elif action=='meet_participants_del':
        keys=request.POST.getlist("K")
        Meet_details.objects.filter(MeetID__in=keys).delete()
    elif action=='meet_participants_sync':
        from mysite.meeting.views import SyncEmployee_meet
        SyncEmployee_meet(request)
    elif action=='level_emp_del':
        keys=request.POST.getlist("K")
        level_emp.objects.filter(level__in=keys).delete()



    elif action=='send_Meet_Email':
        keys=request.POST.getlist("K")
        messages=MeetMessage.objects.filter(id__in=keys)
        toaddr=[]
        ccaddr=[]
        #print "messages--------",messages
        for m in messages:
            if m.Emails:
                toaddr=m.Emails.split(';')
            if m.CopyForEmail:
                ccaddr=m.CopyForEmail.split(',')
            if toaddr or ccaddr:
                try:
                    mail = SendMail(m.MessageNotice,'email/MeetMessage.html',{'MessageContent':m.MessageContent},toaddr+ccaddr,from_addr_name=u"%s"%_(u'时间&安全精细化管理平台'))
                    mail.send_mail()
                except:
                    return getJSResponse({"ret":1,"message":u"发送邮件服务器或邮箱身份验证不正确，发送会议通知失败"})
            else:
                return getJSResponse({"ret":1,"message":u"没有收件箱和抄送地址，发送会议通知失败"})
    elif action=='clearinterlock':
        keys=request.POST.getlist("K")
        clear_interlock(keys)
    elif action=='clearlinkage':
        keys=request.POST.getlist("K")
        clear_linkage(keys)
    elif action=='firstopen_del':
        keys=request.POST.getlist("K")
        FirstOpen_emp.objects.filter(firstopen__in=keys).delete()
        sendFirstCardToAcc(keys)
    elif action=='SyncACTime':
        keys=request.POST.getlist("K")
        SyncACTime(keys)



    elif action=='sync_ipos_data':
        keys=request.POST.getlist("K")
        set_all_pos_data(keys)
    elif action=='upload_ipos_Merchandise':
        keys=request.POST.getlist("K")
        devlist=iclock.objects.filter(SN__in=keys)
        merchandise = Merchandise.objects.all().exclude(DelTag=1)
        update_pos_device_info(devlist,merchandise,'STOREINFO')
    elif action=='upload_ipos_Meal':
        keys=request.POST.getlist("K")
        devlist=iclock.objects.filter(SN__in=keys)
        mealobj = Meal.objects.filter(available=1).exclude(DelTag=1)
        mealobjs=Meal.objects.all().exclude(DelTag=1)
        delete_pos_device_info(devlist,mealobjs,'','MEALTYPE')
        update_pos_device_info(devlist,mealobj,'MEALTYPE')
    elif action=='clearMerchandise':
        keys=request.POST.getlist("K")
        devlist=iclock.objects.filter(SN__in=keys)
        merchandise = Merchandise.objects.all()
        delete_pos_device_info(devlist,merchandise,'','STOREINFO')
    elif action=='clearKeyValue':
        keys=request.POST.getlist("K")
        devlist=iclock.objects.filter(SN__in=keys)
        keyvalue = KeyValue.objects.all()
        delete_pos_device_info(devlist,keyvalue,'','PRESSKEY')
    elif action=='clearMealValue':
        keys=request.POST.getlist("K")
        devlist=iclock.objects.filter(SN__in=keys)
        delete_pos_device_info(devlist,None,'','MEALTYPE')
    elif action=="setExitdata":
        keys=request.POST.getlist("K")
        ET=request.GET.get("ExitTime")
        if len(ET.split(':'))<3:
            ET=ET+":00"
        EA=request.GET.get("ExitArticles")
        EA=unquote(EA);
        for i in keys:
            try:
                Vis=visitionlogs.objects.filter(id=int(i))[0]
                if Vis:
                    if Vis.VisState==0:
                        Vis.ExitTime=datetime.datetime.strptime(ET,'%Y-%m-%d %H:%M:%S')
                        if Vis.EnterTime>Vis.ExitTime:
                            errorInfo=u'离开时间不能早于进入时间！'
                        else:
                            Vis.ExitArticles=u"%s"%EA
                            Vis.VisState=1
                            Vis.save()
            except Exception,e:
                ss=e
                print e
    else:
        errorInfo=u"%s"%_(u"Does not support this feature: \"action=%(object_name)s\"")%{'object_name':action}
    #if ret==cursor:
    #       conn._commit()
    if errorInfo:
        return getJSResponse({"ret":1,"message":u"%s"%errorInfo})
    else:
        return getJSResponse({"ret":0,"message":u"%s"%_('Operation Successful')})


def staDataForget(request,dataModel,val):
    keys=request.POST.getlist("K")
    for i in keys:
        try:
            u=checkexact.objects.get(id=int(i))
            if val==2:
                if u.State==2:
                    continue
#             c,d,b,a=processstand(request,u,2,val)
            c=0
            d=' '
            b=2
            a=0
            if b!=-1:
                deleteCalcLog(UserID=int(u.UserID_id),StartDate=u.CHECKTIME,EndDate=u.CHECKTIME)
                sql='delete from checkinout where userid=%s and checktime=%s'
                params=(u.UserID_id,u.CHECKTIME)
                try:
                    customSqlEx(sql,params)
                except:
                    pass
                if c!='':
                    u.roleid=c
                else:
                    u.roleid=None
                roles=userRole.objects.filter(userid=request.user)
                if roles.count()>0:
                    roleid=roles[0].roleid.roleid
                    if u.oldprocess and u.oldprocess!='':
                        u.oldprocess=u.oldprocess+str(roleid)+','
                    else:
                        u.oldprocess=','+str(roleid)+','
                if d!='':
                    u.process=d
                else:
                    u.process=''
                if val==2:
                    if b==2:
                        sql,params=getSQL_insert_new(transactions._meta.db_table,userid=u.UserID_id, checktime=u.CHECKTIME, checktype=u.CHECKTYPE, verifycode='5',purpose=9,SN=u.SN_id)
                        try:
                            customSqlEx(sql,params)
                        except:
                            pass
                    u.State=b
                else:
                    u.State=val
                u.procSN=a
                u.save()
            else:
                return d
        except:
            pass
    return ''
def staDataLeave(request,dataModel,val):
    keys=request.POST.getlist("K")
    EA=request.GET.get("comments")
    EA=unquote(EA);
    EA=EA.replace("\'","").replace("\"","").replace("\n","").replace("\r","")
    ET=request.GET.get("ProcessingTime")
    ET=datetime.datetime.strptime(ET,'%Y-%m-%d %H:%M:%S')

    cache.delete("%s-%s"%(settings.UNIT,'home_user_speadays'))

    for i in keys:
        try:
            u=USER_SPEDAY.objects.filter(id=int(i))[0]
            if val==2:
                if u.State==2:
                    continue
            c,d,b,a=processstand(request,u,0,val)
            if b!=-1:
                deleteCalcLog(UserID=int(u.UserID_id),StartDate=u.StartSpecDay,EndDate=u.EndSpecDay)
                if c!='':
                    u.roleid=c
                else:
                    u.roleid=None
                u.process=d
                roles=userRole.objects.filter(userid=request.user)
                if request.user.is_superuser:
                    roledell=None
                else:
                    if roles.count()>0:
                        roledell = userRolesDell.objects.filter(roleid=roles[0].roleid,processid=u.processid)
                    else:
                        roledell=None
                if roles.count()>0:
                    roleid=roles[0].roleid.roleid
                    if u.oldprocess and u.oldprocess!='':
                        u.oldprocess=u.oldprocess+str(roleid)+','
                    else:
                        u.oldprocess=','+str(roleid)+','
                if val==2:
                    #邮件发送
                    try:

                        paramvalue= GetParamValue("opt_email_l_mail")
                        if paramvalue=="on":
                            email=[]
                            if u.UserID.email:
                                email.append(u.UserID.email)
                            if request.user.email:
                                email.append(request.user.email)
                            url=u
                            approval=request.user.username
                            #url=u"%s 的请假%s--%s,%s审批通过"%(u.UserID.EName,u.StartSpecDay,u.EndSpecDay,request.user.username)
                            mail = SendMail(u"%s%s"%(u.UserID.EName,_(u'请假审核信息提醒')),'email/userspeday.html',{'u':url,"welcome":u"%s您好：" % u.UserID.EName,"approval":approval,
                            'sitetitle':GetParamValue('opt_basic_sitetitle',u"%s"%_(u'时间&安全精细化管理平台'))},
                            email,from_addr_name=u"%s"%_(u'时间&安全精细化管理平台'))
                            mail.send_mail()

                    except Exception,ee:
                        print ee
                    u.State=b
                else:
                    u.State=val
                u.procSN=a
                u.save()
                if roledell:
                    proSN=roledell[0].procSN
                else:
                    proSN=0
                try:
                    U_Process=USER_SPEDAY_PROCESS.objects.get(USER_SPEDAY_ID=u.id,procSN=proSN)
                except:
                    U_Process=None
                if U_Process:
                    U_Process.User=request.user
                    U_Process.comments=EA
                    U_Process.ProcessingTime=ET
                    U_Process.procSN=proSN
                    U_Process.State=val
                    U_Process.save()
                else:
                    USER_SPEDAY_PROCESS(USER_SPEDAY_ID=u,User=request.user,comments=EA,ProcessingTime=ET,procSN=proSN,State=val).save()
            else:
                return d
        except Exception,e:
            print e
            pass
def staDataOver(request,dataModel,val):
    keys=request.POST.getlist("K")
    for i in keys:
        try:
            u=USER_OVERTIME.objects.filter(id=int(i))[0]
            if val==2:
                if u.State==2:
                    continue
            c,d,b,a=processstand(request,u,1,val)
            if b!=-1:
                deleteCalcLog(UserID=int(u.UserID_id),StartDate=u.StartOTDay,EndDate=u.EndOTDay)
                if c!='':
                    u.roleid=c
                else:
                    u.roleid=None
                roles=userRole.objects.filter(userid=request.user)
                if roles.count()>0:
                    roleid=roles[0].roleid.roleid
                    if u.oldprocess and u.oldprocess!='':
                        u.oldprocess=u.oldprocess+str(roleid)+','
                    else:
                        u.oldprocess=','+str(roleid)+','
                if d!='':
                    u.process=d
                else:
                    u.process=''
                if val==2:
                    u.State=b
                else:
                    u.State=val
                u.procSN=a
                u.save()
            else:
                return d
        except:
            pass

def staDataOrder(request,dataModel,val):
    keys=request.POST.getlist("K")
    for i in keys:
        try:
            u=Meet_order.objects.filter(id=int(i))[0]
            meet=Meet.objects.filter(MeetID=u.MeetID)

            if val==2:
                if u.LocationID:#判断会议有无时间冲突
                    if u.Starttime and u.Endtime:
                        d1=u.Starttime
                        d2=u.Endtime
                        if Meet.objects.filter(LocationID=u.LocationID).filter(Q(Starttime__gte=d1,Starttime__lte=d2)|Q(Starttime__lt=d1,Endtime__gt=d1)).exclude(MeetID=u.MeetID).count()>0:
                            return u'%s'%(_(u'所使用的会议室已经占用！'))
            u.State=val
            u.save()

            if meet:
                if val==2:
                    m=meet[0]
                    m.conferenceTitle=u.conferenceTitle
                    m.MeetContents=u.MeetContents
                    m.LocationID=u.LocationID
                    m.Starttime=u.Starttime
                    m.Endtime=u.Endtime
                    m.CheckIn =u.CheckIn
                    m.CheckOut =u.CheckOut
                    m.Enrolmenttime=u.Enrolmenttime
                    m.EnrolmentLocation=u.EnrolmentLocation
                    m.LastEnrolmenttime=u.LastEnrolmenttime
                    m.EarlySignOfftime=u.EarlySignOfftime
                    m.LastSignOfftime=u.LastSignOfftime
                    m.lunchtimestr=u.lunchtimestr
                    m.lunchtimeend=u.lunchtimeend
                    m.Contact=u.Contact
                    m.ContactPhone=u.ContactPhone
                    m.Sponsor=u.Sponsor
                    m.Coorganizer=u.Coorganizer
                    m.ApplyDate=u.ApplyDate
                    m.user =u.user
                    m.DelTag=0
                    m.save()
                else:
                    meet.update(DelTag=1)
            else:
                if val==2:
                    Meet(MeetID=u.MeetID,conferenceTitle=u.conferenceTitle,MeetContents=u.MeetContents,LocationID=u.LocationID,Starttime=u.Starttime,Endtime=u.Endtime,lunchtimestr=u.lunchtimestr,lunchtimeend=u.lunchtimeend,CheckIn =u.CheckIn,CheckOut =u.CheckOut,Enrolmenttime=u.Enrolmenttime,EnrolmentLocation=u.EnrolmentLocation,LastEnrolmenttime=u.LastEnrolmenttime,EarlySignOfftime=u.EarlySignOfftime,LastSignOfftime=u.LastSignOfftime,Contact=u.Contact,ContactPhone=u.ContactPhone,Sponsor=u.Sponsor,Coorganizer=u.Coorganizer,ApplyDate=u.ApplyDate,user =u.user).save()
        except Exception,e:
            print e
            pass

def processstand(request,u,tag,val):
    if GetParamValue('opt_basic_approval','1')=='0':
        return 0,'',val,0
    if tag==0:
        leaveid=u.DateID
        de=u.EndSpecDay
        ds=u.StartSpecDay
        minunit=gettimediff(de,ds)
        #minunit=gettimediff_byshift(u.UserID_id,de,ds)
    elif tag==2:
        leaveid=10001
        minunit=1
    else:
        leaveid=10000
        minunit=float(u.AsMinute)
        min=float(GetParamValue('MinsWorkDay'))
        minunit=minunit/min
    sn=u.procSN
    state=u.State
    if state==0:
        sn=0
    gp,pid=getprocess_EX(u.UserID_id,leaveid,minunit)
    process=','.join(str(x) for x in gp)
    process=','+process+','#更新职务列表
    if request.user.is_superuser:#超级管理员允许审核
        return  0,process,2,0
    gpp=[]
    for g in gp:
        gpp.append(g+10)#管理员审核后状态为roleid+10
    rolex=0
    r=userRole.objects.filter(userid=request.user.id)
    if r:
        roleidx=r[0].roleid.roleid
        if roleidx not in gp:
            return 0,u'不能审核此假类',-1,0
        else:
            rolex=r[0].roleid_id
    Leapfrog=True
    if not Leapfrog and val==2:
        if u.roleid!=roleidx:
            return 0,u'不能越级审核',-1,0
    urd=userRolesDell.objects.filter(roleid=rolex,processid=pid,procSN__gte=sn)
    if urd.count()>0:
        urd1=urd[0]
        dd=urd1.days
        roleid=urd1.roleid.roleid
        roleids=roleid+10
        procsn=urd1.procSN
        if state not in [0,3,6]:#申请状态和重新申请、拒绝状态不用判断流程自己的上级是否审核过
            if state==2:
                if minunit>dd:
                    return 0,u'记录已经通过只有审核天数大于等于所用天数的管理员才能修改',-1,procsn#已经审核标记为2的记录只允许审核后标记依然为2的人审核通过或拒绝。
        if val==2:
            if minunit>dd:
                dx=0
                urd=userRolesDell.objects.filter(processid=pid,procSN__gt=procsn).order_by("procSN")
                for u in urd:
                    dx1=u.roleid.roleid
                    if dx1 in gp:
                        dx=dx1
                    if dx!=0:
                        break
                return dx,process,roleids,procsn#请假的天数比自己所能审核的天数大，返回下一级审核人员的职务编号，和审核后的state=roleid+10
            else:
                return 0,process,2,procsn#请假通过，''不修改当前职务编号，state=2
        else:
            return 0,process,val,0#拒绝后将审核职务制成空，state=val
    return 0,u'不能审核此假类',-1,0








@login_required
def DataList(request, ModelName):
    appName=request.path.split('/')[1]
    if ModelName!='attshifts_except':
        dataModel=GetModel(ModelName,appName)
        if not dataModel:
            dataModel=GetModel(ModelName,'iclock')
    else:
        dataModel=GetModel('attShifts','iclock')  #用于异常报表

    if not dataModel: return NoFound404Response(request)
    if (dataModel==IclockMsg) and ("msg" not in settings.ENABLED_MOD):
        return render_to_response("info.html", {"title":  _("Error"), "content": _("The server is not installed information services module!")});
    action=request.GET.get("action", "")
    if action:
        #检查执行该动作的权限
        checkAction=action
        if action=='del':
            checkAction='delete'
        if action=='reloadAppointlogdata':
            checkAction='reloaddata'
        if action in ['setExitdata','setUserAuthedZone','setDeviceAuthedDining','add_meet_devices','setDeviceAuthedDept','setDeviceAuthedZone','setUserAuthedDept']:
            checkAction='add'
        if action =='forgetAudit':
            checkAction='TransAudit'
        if action =='level_emp_del':
            checkAction='delallemps'
        if action =='accEmptoDev':
            checkAction='deptEmptoDev'
            dataModel=iclock
        if action =='accEmpFromDev_DEL':
            checkAction='deptEmptoDelete'
            dataModel=iclock
        if action =='upload_ac':
            checkAction='Upload_AC_Options'
        if action =='upload_userac':
            checkAction='Upload_User_AC_Options'
        if action =='deptEmptoDevbyPIN':
            checkAction='deptEmptoDev'
        if action == 'sync_ipos_data':
            checkAction='Upload_pos_all_data'
        if action == 'upload_ipos_Merchandise':
            checkAction='Upload_pos_Merchandise'
        if action == 'upload_ipos_Meal':
            checkAction='Upload_pos_Meal'
        dModel=dataModel
        if dataModel in [level_emp]:
            dModel=level
        if dataModel in [empleavelog]:
            dModel=employee
            checkAction='restoreEmpLeave'
        if action in ['clearinterlock','clearlinkage','clearMerchandise','clearKeyValue','clearMealValue']:
            checkAction='cleardata'
        if action in ['clearpic','delFingerFromDev','delFaceFromDev']:
            checkAction='deptEmptoDelete'
        if not hasPerm(request.user, dModel, checkAction):
            return getJSResponse({"ret":-2,"message":u"%s"%_('You do not have the permission!')}) #NoPermissionResponse()
        adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, action=_(action),
        object=("%s"%(request.POST.get("K", "")))[:40]).save(force_insert=True)#
        return doAction(action, request, dataModel)
    request.user.iclock_url_rel='../..'
    #检查浏览该数据的权限
    operation='%s.IclockDept_%s'%(appName,dataModel.__name__.lower())
    if dataModel in [InterLock,linkage,AntiPassBack,FirstOpen,combopen_door]:
        operation='acc.browse_interlock'
    if dataModel in [USER_TEMP_SCH]:
        operation='iclock.IclockDept_reports'
    if dataModel in [records]:
        operation='acc.acc_records'
    if dataModel in [AuxIn,AuxOut,level_emp]:
        operation='acc.browse_accdoor'
    if dataModel in [empleavelog]:
        operation='iclock.empLeave_employee'
    if dataModel in [FirstOpen_emp]:
        operation='acc.browse_firstopen'
    if (not hasPerm(request.user, dataModel, "browse")) and (not request.user.has_perm(operation)):
        #t=request.GET.get('t','')
        return getJSResponse(u"%s"%(_("You do not have the browse %s permission!")%(dataModel._meta.verbose_name)))
#               if t=='':
#               return render_to_response('welcome_sys.html',RequestContext(request,{'iclock_url_rel': request.user.iclock_url_rel,}))
#               else:
#return getJSResponse(_("You do not have the browse %s permission!")%(dataModel._meta.verbose_name))
    request.model=dataModel
    if request.method=='POST': #post 表示获取自动化的json数据
        oper=request.POST.get('oper')
        if oper=='edit':#使用jqGrid自带的编辑提交保存
            if dataModel==searchs:
                from mysite.acc.accviews import save_modify_device
                return save_modify_device(request)
            return getJSResponse({"ret":0,"message":u"%s"%_('Operation Successful')})

        jqGrid=JqGrid(request,datamodel=dataModel)
        items=jqGrid.get_items()   #not Paged
        if dataModel==iclock:
#               pType=settings.MOD_DICT[using_m]
#               items=items.filter(Q(ProductType=None)|Q(ProductType=pType))
            state = int(request.GET.get(STATE_VAR, -1))
            limit = int(request.POST.get('rows', 50))
            offset = int(request.POST.get('page', 1))
            #checkReboot(items)
            if state!=-1: #由于设备状态需要计算后确定，根据设备状态过滤的页面数据不能直接从数据库获得，只能单独生成
                cc=iclockPage(request,items, offset, limit, state)
            else:
                cc=jqGrid.get_json(items)
        else:
            cc=jqGrid.get_json(items)
        tmpFile=dataModel.__name__+'_list.js'
        if dataModel.__name__.lower()=='myuser':
            tmpFile='User_list.js'
        tmpFile=request.GET.get(TMP_VAR,tmpFile)
        if appName!='iclock':
            tmpFile=appName+'/'+tmpFile
        #y=request.GET.get('y',datetime.datetime.now().year)

        show_style=request.GET.get('show_style','')
        if show_style=='photo':#人员维护以照片显示
            from mysite.iclock.browsepic import get_pictures_of_employee
            rows=get_pictures_of_employee(request,cc)
        else:
            t=loader.get_template(tmpFile)
            isedit=int(request.GET.get('e',-1))
            if isedit==0:
                cc['can_change']=False
            else:
                if dataModel in [level_emp]:
                    cc['can_change']=hasPerm(request.user, level, 'change')
                else:
                    cc['can_change']=hasPerm(request.user, dataModel, 'change')


            try:
                cc['user']=request.user
                rows=t.render(cc)
            except Exception,e:
                #import traceback; traceback.print_exc();

                print "DataList=====",e
                rows='[]'
                pass
        #rownumber = int(request.POST.get("rows"))
        try:
            t_r="{"+""""page":"""+str(cc['page'])+","+""""total":"""+str(cc['total'])+","+""""records":"""+str(cc['records'])+","+""""rows":"""+rows+"""}"""
        except Exception,e:
            print "===========",e
        #t_r={}
        #t_r['page']=cc['page']
        #t_r['total']=cc['total']
        #t_r['records']=cc['records']
        #t_r['rows']=loads(rows)
        #print "-------",t_r
        return getJSResponse(t_r)
    else:
        if ModelName!='attshifts_except':
            try:
                if ModelName=='iclock' or ModelName=='transactions':
                    colModel=dataModel.colModels(request)
                else:
                    colModel=dataModel.colModels()
            except Exception,e:
                colModel=[]
        else:
            colModel=attShifts.colModels()  #这样写法有利于将来有多个基于attShifts表的查询,可在attShifts中写多个colModl以供调用
        if ModelName=='user':
            using_m=request.GET.get('mod_name','att')
            #if using_m in ['att','adms']:
            colModel.insert(6,{'width': 120, 'sortable': False, 'name': 'iclock_set', 'label': u'授权设备'})
        try:
            HeaderNames=dataModel.HeaderModels()
        except:
            HeaderNames=[]
        tblname=ModelName
        if request.GET.has_key("tblName"):
            tblname=request.GET.get("tblName")
        mod_name=request.GET.get("mod_name","")
        if tblname=='iclock':
            tblname='iclock_'+mod_name
        disabledCols=FetchDisabledFields(request.user, tblname)
        flagpage=request.GET.get("flagpage","10")
        settings.PAGE_LIMIT=GetParamValue('opt_users_page_limit','50',request.user.id)
        limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
        if limit<0:limit=50
        if flagpage!="10":
            dds="{"+""""colModel":"""+dumps(colModel)+","+""""disabledcols":"""+dumps(disabledCols)+","+""""limit":"""+str(limit)+"""}"""
            return getJSResponse(dds)

        tmpFile=dataModel.__name__+'_list.html'
        if dataModel.__name__.lower()=='myuser':
            tmpFile='User_list.html'
        tmpFile=request.GET.get(TMP_VAR, tmpFile)
        if appName!='iclock':
            tmpFile=appName+'/'+tmpFile
        try:
            delOldCount=0
            cl=ChangeList(request, dataModel)
            inputFields, dtFields=ModifyFields(dataModel)
            if dataModel== USER_SPEDAY or dataModel== USER_OVERTIME:
                if GetParamValue('opt_basic_approval','1')=='0' or GetParamValue('opt_basic_approval','1')==0:
                    disabledCols.append("process")
            states={}
            if dataModel==checkexact:
                ll=GetRecordStatus()
                states={'states':ll}
            elif dataModel in [empleavelog, employee] :
                ll=GetLeavetype()
                states={'states':ll}
            elif dataModel in [visitionlogs]:
                if GetParamValue('opt_users_vis_pic','0',request.user.id)!='1':
                    for t in colModel:
                        if t['name']=='photo':
                            t['hidden']=True
                        if t['name']=='photoz':
                            t['hidden']=True
                        if t['name'] in ['id','VisempName','VisState']:
                            t['frozen']=True
            cc={
                    'app':mod_name,
                    'limit':limit,
                    #'reg':settings.REGISTER,
                    'title': dataModel._meta.verbose_name.capitalize(),
                    'cl':cl,
                    'ForgetAtt_list': dumps1(states),
                    'disabledcols':dumps1(disabledCols),
                    'colModel':dumps1(colModel),
                    'groupHeaders':dumps(HeaderNames),
                    'dataOpt': dataModel._meta,
                    'dtFields':dtFields,
                    'Caption':dataModel._meta.verbose_name_plural.capitalize(),
                    'delOldRecDays': delOldCount,
                    'iclock_url_rel': request.user.iclock_url_rel,
            }
            if dataModel== USER_SPEDAY or dataModel== USER_OVERTIME or dataModel== checkexact:
                if GetParamValue('opt_basic_approval','1')=='0' or GetParamValue('opt_basic_approval','1')==0:
                    cc['approval']=0
                else:
                    cc['approval']=1
            elif dataModel==Group:
                cc["permissions"]=getAllAuthPermissions(request.user)
            elif dataModel==iclock and mod_name=='acc':
                cc['subgrid0_colModel']=dumps1(AccDoor.colModels())
                cc['subgrid1_colModel']=dumps1(AuxIn.colModels())
                cc['subgrid2_colModel']=dumps1(AuxOut.colModels())
            elif dataModel==transactions:
                cc['IMPORT_TRANS']=settings.IMPORT_TRANS
                cc['PIRELLI']=settings.PIRELLI
            #r=render_to_response(tmpFile, cc,RequestContext(request, {}))
            r=render(request,tmpFile,cc)
            return r

        except Exception,e:
            #import traceback;traceback.print_exc()
            pass

#               t=defListTemp(dataModel)
#               t=Template(t)
        #print "DataList GET------------",e
        return render_to_response("info.html", {"title":  _("Error"), "content": _("render to response error %s")%(e)})


def iclockPage(request, items, offset, limit, state):
    from math import ceil
    pgList=[]
    count=0
    curCount=0
    total=0
    minIndex=(offset-1)*limit
    t1=datetime.datetime.now()-datetime.timedelta(seconds=settings.MAX_DEVICES_STATE)

#       if request.user.is_superuser or request.user.is_alldept or request.user.ilevel==1:
    #if state==0:
    #       items=items.filter(State=0)
    #elif state==1:
    #       items=items.filter(LastActivity__gte=t1).exclude(State=2)
    #elif state==2:
    #       items=items.filter(LastActivity__gte=t1,State=state)
    #elif state==3:
    #       items=items.filter(Q(LastActivity=None)|Q(LastActivity__lt=t1)).exclude(State=0)

    #p=Paginator(items, limit)
    #count=p.count
    #total=p.num_pages
    #pp=p.page(offset)
    #pgList=pp.object_list
    #else:
    for i in items:
        if i.getDynState()==state:
            pgList.append(i)
    count=len(pgList)
    total=int(ceil(count/float(limit)))
    if offset>total:
        offset=1
    pgList=pgList[(offset-1)*limit:offset*limit]

    return {
            'page': offset,
            'total': total,
            'latest_item_list': pgList,
            'records': count
    }

def timeStamp(t):
    dif=t-datetime.datetime(2007,1,1)
    return "%06X%06X"%(dif.days,dif.seconds)

def stampToTime(stamp):
    dif=datetime.timedelta(string.atoi(stamp[0:3],16),string.atoi(stamp[3:],16))
    return datetime.datetime(2007,1,1)+dif

from mysite.iclock.validdata import checkRecData,checkALogData

def checkAndRunSql(cursor, sqlList, sql=None):
    error=[]
    if sql:
        sqlList.append(sql)
    if cursor and sqlList:
        if (not sql) or (len(sqlList)>=100):
            print "Post:", len(sqlList)
            try:
                commitLog(cursor, '; '.join(sqlList))
            except Exception, er:
#                               print er
                for s in sqlList:
                    try:
                        from django.db import connection as conn
#                                               cursor=conn.cursor()
                        cursor.execute(s)
#                                               conn._commit()
                    except Exception, e:
                        emsg="SQL '%s' Failed: %s"%(s,e)
#                                               print emsg
                        error.append(emsg)
            for s in range(len(sqlList)): sqlList.pop()
    return error

def checkReboot(iclocks):
    if not settings.REBOOT_CHECKTIME: return
    iclocks=iclocks.filter(LastActivity__lt=datetime.datetime.now()-datetime.timedelta(0,settings.REBOOT_CHECKTIME*60))
    ips=updateLastReboot(iclocks)
    rebDevs(ips)
#自动发送人员到设备 2011-02-12 cg
@login_required
def autoSendEmpToDev(request):
    authdept=userDeptList(request.user)
    if authdept:
        for deptid in authdept:
            devs=None
            emps=None
            sns=[]
            sns=IclockDept.objects.filter(dept=deptid).values('SN').values_list('SN', flat=True)
            if sns:
                emps=employee.objects.filter(DeptID=deptid)
                for e in emps:
                    cmdStr=getEmpCmdStr(e)
                    appendDevCmdNew(sns,cmdStr)
            else:
                continue
        adminLog(time=datetime.datetime.now(),User=request.user, action=_(u"autoSebdEmpToDev"), model=employee._meta.verbose_name,object = request.META["REMOTE_ADDR"]).save(force_insert=True)#
        return getJSResponse({'ret':0,'message':u"%s"%_(u'Operation Success')})
    else:
        return getJSResponse({'ret':1,'message':u"%s"%_(u'No AuthDept')})
