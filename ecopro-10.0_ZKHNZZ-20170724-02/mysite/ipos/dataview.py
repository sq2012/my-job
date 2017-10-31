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
from mysite.core.cmdproc import *
from mysite.ipos.models import *
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

def save_instance(form, instance, fields=None, fail_message='saved',
                                  commit=True, exclude=None, construct=True):
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
        raise ValueError("The %s could not be %s because the data didn't"
                                         " validate." % (opts.object_name, fail_message))

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
    try:
        lock_fields=model.Admin.lock_fields
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
        if model==HandConsume and f.name=='meal':
            qs=Meal.objects.filter(available=1)
            mlist=[]
            for t in qs:
                mlist.append((t.id,t.name))
            formfield=ChoiceField(choices=mlist,label=_(u'餐别:'),initial=[],required=True)
        elif model==HandConsume and f.name=='posdevice':
            qs=iclock.objects.filter(ProductType=11).exclude(DelTag=1)
            ilist=[]
            for t in qs:
                ilist.append((t.SN,t.Alias or t.SN))
            formfield=ChoiceField(choices=ilist,label=_(u'设备:'),initial=[],required=True)

        else:
            if f.name in lock_fields:
                formfield = f.formfield(widget=ForeignKeyInput(),initial=current_value)#form_field_readonly(f, initial=current_value)

                #formfield = form_field_readonly(f, initial=current_value)
            else:
                formfield = formfield_callback(f, initial=current_value)
        if formfield:
            field_list.append((f.name, formfield))
    base_fields = OrderedDict(field_list)
    return type(opts.object_name + 'Form', (form,),
            {'base_fields': base_fields, '_model': model,
             'save': make_instance_save(instance or model(), fields, 'created')})

def form_for_instance(instance, form=forms.BaseForm, fields=None,  formfield_callback=lambda f, **kwargs: f.formfield(**kwargs)):
    return form_for_model(instance.__class__, instance, form, fields, formfield_callback)

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
        #cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,self.PIN))
            cache.delete("%s_iclock_emp_%s"%(settings.UNIT,uid))
    elif dataModel==checkexact:
        for t in items:
            deleteCalcLog(UserID=t.UserID_id,StartDate=t.CHECKTIME,EndDate=t.CHECKTIME)
            sql='delete from checkinout where userid=%s and checktime=%s'
            params=(t.UserID_id,t.CHECKTIME)
            try:
                customSqlEx(sql,params)
            except:
                pass
    elif dataModel==iclock:
        for t in items:
            t.DelTag=1
            t.save()

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
    adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, action=u'%s'%_(u"Clear All"), object=request.META["REMOTE_ADDR"],count=delNum).save(force_insert = True)
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

    adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, action=u"%s"%_(u"Clear Obsolete Data"),object = request.META["REMOTE_ADDR"]).save(force_insert = True)
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

def DataDetailResponse(request, dataModel, form, key='', **kargs):
    appName=request.path.split('/')[1]
    if request.POST:
        return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})
    else:
        if not kargs: kargs={}
#       inputFields, dtFields=ModifyFields(dataModel)
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
        tmpFile=dataModel.__name__+'_edit.html'
        if appName!='iclock':
            tmpFile=appName+'/'+tmpFile
        return render(request,tmpFile,kargs)#render_to_response([tmpFile,'data_edit.html'],  RequestContext(request,kargs),)

def DataPostCheck(request, oldObj, newObj):
    if str(type(newObj))=="<class 'iclock.models.USER_CONTRACT'>":
        try:
            emp=employee.objByID(newObj.UserID.id)
            emp.Contractendtime=newObj.EndContractDay
            emp.save()
        except Exception,ex:
            print ex
    if isinstance(newObj, employee):
        pass
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

def DataChangeTitle(newObj):
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
        proc=getprocess(ov.UserID_id,10000,1,minunit)
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
    elif dataModel==get_user_model():
        return doPostAdmin(request, dataModel, '_new_')
    elif dataModel==iclock:
        return doPostIclock(request, dataModel, '_new_')
    elif dataModel==ICcard:
        from mysite.ipos.views import saveICcard
        return saveICcard(request)
    elif dataModel==KeyValue:
        from mysite.ipos.views import saveKeyValue
        return saveKeyValue(request)
    elif dataModel==Allowance:
        from mysite.ipos.views import saveAllowance
        return saveAllowance(request,'_new_')
    dataForm=form_for_model(dataModel)
    f=dataForm(request.POST)
    if f.is_valid():
        isAdd=True

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
                if dataModel==HandConsume:
                    f.cleaned_data['meal']=Meal.objects.get(pk=f.cleaned_data['meal'])
                    f.cleaned_data['posdevice']=iclock.objects.get(SN=f.cleaned_data['posdevice'])
                obj=f.save()
                settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
                if dataModel==IssueCard:
                    if obj.card_privage==PRIVAGE_CARD or obj.card_privage==OPERATE_CARD:
                        obj.issuedate=datetime.datetime.now()
                        obj.save()
                if settings.CARDTYPE==1:
                    if dataModel==IssueCard:
                        if obj.card_privage in [PRIVAGE_CARD,OPERATE_CARD]:
                            obj_request = request.POST
                            card_dining = obj_request['dining']
                            if card_dining=='0':
                                card_dining=None
                            CardManage(card_no = int(obj_request['cardno']),
                            pass_word = '',
                            dining_id = card_dining,
                            cardstatus = CARD_VALID).save(force_insert=True)
            except Exception,e:
                import traceback;traceback.print_exc()
                estr=u"%s"%e
                #print "DataNewPost--",estr
                                #return getJSResponse({"ret":1,"message":u"%s"%_('Duplicated')})
                #else:
                if ('IntegrityError' in estr) or ("UNIQUE KEY" in estr) or ("are not unique" in estr) or ("Duplicate entry" in estr):
                    return getJSResponse({"ret":1,"message":u"%s"%_(u'数据重复')})
                else:
                    return getJSResponse({"ret":1,"message":u'%s%s'%(_('save failed'),estr)})
            key=obj.pk
            #用户新增的部门自动加入授 权表中
#                       if dataModel==department and not request.user.is_superuser:
#                           DeptAdmin(user=request.user, dept_id=int(key)).save()
            if dataModel in [Group,User] and (not request.user.is_superuser):
                UserAdmin(user=request.user, owned=int(key),dataname=str(dataModel._meta)).save()
#                           GroupAdmin(user=request.user, group_id=key).save()

        except Exception, e: #通常是不满足数据库的唯一性约束导致保存失败
            estr="%s"%e
            if ('IntegrityError' in estr) or ("UNIQUE KEY" in estr) or ("are not unique" in estr) or ("Duplicate entry" in estr):
                return getJSResponse({"ret":1,"message":u"%s"%_('Duplicated')})

                #f.errors[NON_FIELD_ERRORS]=u'<ul class="errorlist"><li>%s</li></ul>'%unicode(e.message)

            return getJSResponse({"ret":1,"message":u"%s"%e})  #DataDetailResponse(request, dataModel, f)
        #DataPostCheck(request, None, obj)
        #AutoAddPermissions(dataModel,key)
        log=adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, object=u"%s"%obj,action=u'%s'%_(u"Append"))
        log.save(force_insert=True)


        return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})
    return DataDetailResponse(request, dataModel, f)


@login_required
def DataNew(request, ModelName):
    appName=request.path.split('/')[1]

    dataModel=GetModel(ModelName,appName)
    if dataModel!=Announcement and  (not hasPerm(request.user, dataModel, "add")):
        return NoPermissionResponse()
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
            f.errors[dataModel._meta.pk.name]=[_("Keyword \"%(object_name)s\" can not to be changed!")%{'object_name':fieldVerboseName(dataModel, dataModel._meta.pk.name)}];
            #return DataDetailResponse(request, dataModel, f, key=emp.pk)
            return getJSResponse({"ret":1,"message":u"%s"%f.errors[dataModel._meta.pk.name]})
        oldEmp=None
        if dataModel==employee:
            oldEmp=employee.objByID(emp.id)
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
            print "------",e
            return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})
        #if dataModel==iclock:
        #    if (not newObj.ProductType) or (newObj.ProductType!=5):
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

        if dataModel==Meal:
            from mysite.ipos.ic_pos_devview import getMealID
            from mysite.ipos.views import save_Meal_Machine
            getMealID()
            # use_machine = request.POST.get('use_machine','')
            # if use_machine:
            save_Meal_Machine(request)

#                   GroupAdmin(user=request.user, group_id=key).save()
        DataPostCheck(request, oldEmp or emp, newObj)
        AutoAddPermissions(dataModel,key)
        emp=u"%s"%emp
        if dataModel.__name__=='Announcement':
            log=adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name)
        else:
            log=adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, action = u'%s'%_(u'Change'), object=emp[0:100])
        log.action=_(u"Modify")
        log.save()
        return getJSResponse({"ret":0,"message":""})
    return DataDetailResponse(request, dataModel, f, key=emp.pk)

@login_required
def DataDetail(request, ModelName, DataKey):
    dataModel=GetModel(ModelName,request.path.split('/')[1])
    #dataModel=GetModel(ModelName)_
    if (not hasPerm(request.user, dataModel, "change")) and dataModel!=Announcement:#Announcement表用户没有编辑权限时为了方便查询允许弹出编辑对话框
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
    elif dataModel==ICcard:
        if request.method=="POST":
            from mysite.ipos.views import saveICcard

            return saveICcard(request,DataKey)
    elif dataModel==SplitTime:
        if request.method=="POST":
            from mysite.ipos.views import saveSplitTime
            return saveSplitTime(request,DataKey)
    elif dataModel==KeyValue:
        if request.method=="POST":
            from mysite.ipos.views import saveKeyValue

            return saveKeyValue(request,DataKey)
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
    key=request.GET.get("SN")
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
    elif action=="deptEmptoDev":
        emp=request.POST.get('userids')
        deptid=request.POST.get('deptIDs')
        isalldev=request.POST.get('foralldev','0')
        isContainedChild=request.POST.get('isContainChild',"")
        finger=request.POST.get('finger',0)
        face=request.POST.get('face',0)
        PIC=request.POST.get('PIC',0)
        if finger==0 and face==0 and PIC==0:
            finger=1
            face=1
            PIC=1
        if emp=='':
            deptidlist=[int(i) for i in deptid.split(',')]
            deptids=deptidlist
            if isContainedChild=="1":   #是否包含下级部门
                deptids=[]
                for d in deptidlist:#支持选择多部门
                    if int(d) not in deptids :
                        deptids+=getAllAuthChildDept(d,request)
            emps=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1)
        else:
            emplist=emp.split(',')
            emps=employee.objects.filter(id__in=emplist)
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
            deptEmptoDev(keys,emps,cursor,finger,face,PIC)
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
        #batchOp(request, dataModel, lambda d: appendDevCmd(d, "DATA QUERY USERINFO PIN=111"))#INFO
        #Message="DATA QUERY ATTPHOTO StartTime=2011-10-12 13:00:00\tEndTime=2011-10-12 17:00:00"
        Message="INFO"#"ACC Status"
        #print
        batchOp(request, dataModel, lambda d: appendDevCmd(d, Message))
    elif action=="sendMessage":#sendMessage
        msg=string.strip(request.REQUEST['MSG'])
        ischeck=string.strip(request.REQUEST['ischeck'])
#               tag=int(string.strip(request.REQUEST['TAG']))
        Message="SMS MSG=%s\tTAG=%d"%(msg,253)
#               if(tag==254):
        uid=int(string.strip(request.REQUEST['UID']))
        Message+="\tUID=%d"%(uid)
        if(ischeck=="true"):
            min=int(string.strip(request.REQUEST['MIN']))
            st=string.strip(request.REQUEST['StartTime'])
            Message+="\tMIN=%d\tStartTime=%s "%(min,st)
        else:
            st=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Message+="\tMIN=0\tStartTime=%s "%(st)
        batchOp(request, dataModel, lambda d: appendDevCmd(d, Message))
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
        pin=string.strip(request.REQUEST['PIN'])
        pwd=string.strip(request.REQUEST['Passwd'])
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
        if is_all=='on' and date=='':
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
    elif action=="toDev":
        key=request.REQUEST["SN"]
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
    elif action=="delDev":
        key=request.REQUEST["SN"]
        keys=key.split(',')
        uid=request.REQUEST["K"]
        uids=uid.split(',')
        if not keys:
            errorInfo=_("Designated device does not exist!")
        else:
            if isinstance(keys,list):
                ret=batchOp(request, dataModel, lambda emp: appendDevCmdNew(keys, "DATA DEL_USER PIN=%s"%emp.pin(), cursor))
            else:
                ret=batchOp(request, dataModel, lambda emp: appendDevCmdNew(keys, "DATA DEL_USER PIN=%s"%emp.pin(), cursor))

        for sn in keys:
            for userid in uids:
                pin=employee.objByID(userid).PIN
                delEmpInDevice(pin,sn)


    elif action=='empLeave':
        errorInfo=batchOp(request, dataModel, lambda emp: empLeave(emp))
    elif action=='restoreEmpLeave':
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
    elif action=="allowanceAudit":
        from mysite.ipos.views import staDataAllowance,staDataAllowanceBatch
        if request.GET.get("to", "")=="Accept":
            keys=request.POST.getlist("K")
            datalist=Allowance.objects.filter(id__in=keys)
            for t in datalist:
                if t.is_pass==1:
                    return getJSResponse({"ret":1,"message": u"%s"%_(u'该补贴已经审核')})
            ss=staDataAllowance(request, dataModel, 1)
        elif request.GET.get("to", "")=="Refuse":
            keys=request.POST.getlist("K")
            datalist=Allowance.objects.filter(id__in=keys)
            if datalist:
                for t in datalist:
                    if t.is_pass==1:
                        return getJSResponse({"ret":1,"message": u"%s"%_(u'该补贴已经审核')})
            ss=staDataAllowance(request, dataModel, 0)
        elif request.GET.get("to", "")=="AcceptBacth":
            #keys=request.GET.get("batch")
            #datalist=Allowance.objects.filter(batch=keys)
            #for t in datalist:
            #       if t.is_pass==1:
            #               return getJSResponse({"ret":1,"message": u"%s"%_(u'该补贴已经审核')})
            ss=staDataAllowanceBatch(request, dataModel, 1)
        elif request.GET.get("to", "")=="RefuseBacth":
            #keys=request.GET.get("batch")
            #datalist=Allowance.objects.filter(batch=keys)
            #for t in datalist:
            #       if t.is_pass==1:
            #               return getJSResponse({"ret":1,"message": u"%s"%_(u'该补贴已经审核')})
            ss=staDataAllowanceBatch(request, dataModel, 0)
        if ss:
            errorInfo=ss

    elif action=="AllowanceReUpload":
        from mysite.ipos.views import staDataAllowanceReUpload
        ss=staDataAllowanceReUpload(request,dataModel)
        if ss:
            errorInfo=ss

    elif action=='OpLoseCard':
        from mysite.ipos.views import staDataLoseCard

        ss=staDataLoseCard(request,dataModel,3)
        if ss:
            errorInfo=ss
    elif action=='OprevertCard':
        from mysite.ipos.views import staDataLoseCard
        ss=staDataLoseCard(request,dataModel,1)
        if ss:
            errorInfo=ss
    elif action=='CancelManageCard':
        from mysite.ipos.views import staCancelManageCard
        ss=staCancelManageCard(request,dataModel)
        if ss:
            errorInfo=ss
    elif action=='NoCardRetireCard':
        from mysite.ipos.views import staNoCardRetireCard
        ss=staNoCardRetireCard(request,dataModel)
        if ss:
            errorInfo=ss

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
                    print "setDeviceAuthedDept=",e
                    errorInfo=u'%s保存出现错误'%k
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
                    print "setDeviceAuthedZone=",e
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
                    print "setUserAuthedDept=",e
                    errorInfo=u'%s保存出现错误'%k
            cache.delete("%s_userdepts_%s_%s"%(settings.UNIT, k,settings.DEPTVERSION))
            cache.delete("%s_depttree_%s_%s"%(settings.UNIT, k,settings.DEPTVERSION))
    elif action=='Supplement':#ID卡充值
        from mysite.ipos.views import SaveSupplement
        ss=SaveSupplement(request,dataModel)
        if ss:
            errorInfo=ss
    elif action=='OpSupplement':#ID卡充值,工具条按钮
        from mysite.ipos.views import SaveOpSupplement
        ss=SaveOpSupplement(request,dataModel)
        if ss:
            errorInfo=ss
    elif action=='Reim':#ID卡退款
        from mysite.ipos.views import SaveReim
        ss=SaveReim(request,dataModel)
        if ss:
            errorInfo=ss
    elif action=='Retreat':#ID卡退款
        from mysite.ipos.views import SaveRetreat
        ss=SaveRetreat(request,dataModel)
        if ss:
            errorInfo=ss
    elif action=='OpReimburse':#ID卡退款工具条按钮
        from mysite.ipos.views import SaveOpReim
        ss=SaveOpReim(request,dataModel)
        if ss:
            errorInfo=ss
    elif action=='OpUpdateCard':#ID卡资料修改工具条按钮
        from mysite.ipos.views import SaveOpUpdateCard
        ss=SaveOpUpdateCard(request,dataModel)
        if ss:
            errorInfo=ss
    elif action=='OpChangeCard':#ID换卡工具条按钮
        from mysite.ipos.views import SaveOpChangeCard
        ss=SaveOpChangeCard(request,dataModel)
        if ss:
            errorInfo=ss

    elif action=='deviceLogCheck':
        keys = request.GET.getlist("K")
        from mysite.ipos.views import deviceLogCheck
        st=datetime.datetime.now()-datetime.timedelta(days=100)
        et=datetime.datetime.now()
        error_data = deviceLogCheck(keys[0],st,et)
        if error_data:
            message = u'成功检测到%s条未上传记录，系统已自动下发获取未上传记录命令，请命令执行完之后再核对结果！'%len(error_data)
            savePosLogToFile('checklog',message,keys[0])
            return getJSResponse({"ret":0,"message":u"%s"%_(message)})
        else:
            return getJSResponse({"ret":1,"message":u"%s"%_(u'当前设备的消费数据已经完整上传！')})
    else:
        errorInfo=u"%s"%_(u"Does not support this feature: \"action=%(object_name)s\"")%{'object_name':action}
    #if ret==cursor:
    #       conn._commit()
    if errorInfo:
        return getJSResponse({"ret":1,"message":u"%s"%errorInfo})
    else:
        return getJSResponse({"ret":0,"message":u"%s"%_('Operation Successful')})



def panduan(request,u,tag,val):
    if GetParamValue('opt_basic_approval','1')=='0':
        return 0,'',val
    if tag==0:
        leaveid=u.DateID
        de=u.EndSpecDay
        ds=u.StartSpecDay
        minunit=gettimediff(de,ds)
        #minunit=gettimediff_byshift(u.UserID_id,de,ds)
    else:
        leaveid=10000
        minunit=u.AsMinute
    state=u.State
    gp=getprocess(u.UserID_id,leaveid,tag,minunit)
    process=','.join(str(x) for x in gp)
    process=','+process+','#更新职务列表
    gpp=[]
    for g in gp:
        gpp.append(g+10)#管理员审核后状态为roleid+10
    r=userRole.objects.filter(userid=request.user.id).values_list("roleid", flat=True)
    urd=userRolesDell.objects.filter(roleid__in=r,State=1).filter(Q(leaveid=leaveid)|Q(leaveid=10001))
    if urd.count()>0:
        dd=urd[0].days
        roleid=urd[0].roleid.roleid
        roleids=roleid+10
        if state not in [0,3,6]:#申请状态和重新申请、拒绝状态不用判断流程自己的上级是否审核过
            if state==2:
                if minunit>dd:
                    return 0,u'记录已经通过只有审核天数大于等于所用天数的管理员才能修改',-1#已经审核标记为2的记录只允许审核后标记依然为2的人审核通过或拒绝。
            else:
                try:
                    gi=gpp.index(state)
                except:
                    gi=0
                try:
                    ui=gpp.index(roleids)
                except:
                    ui=0
                if ui<gi:
                    return 0,u'更高级别的管理员已经审核',-1#比自己级别高的人已经审核过通过，不允许在审核
        if val==2:
            if minunit>dd:
                dx=0
                try:
                    if roleids==gpp[-1]:
                        dx=0
                    else:
                        gi=gp.index(roleid)
                        ird=gi+1
                        dx=gp[ird]#计算下一级职务编号
                except:
                    pass
                return dx,process,roleids#请假的天数比自己所能审核的天数大，返回下一级审核人员的职务编号，和审核后的state=roleid+10
            else:
                return 0,process,2#请假通过，''不修改当前职务编号，state=2
        else:
            return 0,process,val#拒绝后将审核职务制成空，state=val
    return 0,u'不能审核此假类',-1

@login_required
def DataList(request, ModelName):
    appName=request.path.split('/')[1]
    dataModel=GetModel(ModelName,appName)
    if not dataModel and ModelName=='iclock':
        dataModel=GetModel(ModelName,'iclock')
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
        if action == 'deviceLogCheck':
            checkAction='browse'
        if not hasPerm(request.user, dataModel, checkAction):
            return getJSResponse({"ret":-2,"message":u"%s"%_('You do not have the permission!')}) #NoPermissionResponse()
        adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, action=_(action),
        object=("%s"%(request.POST.get("K", "")))[:40]).save(force_insert = True)
        return doAction(action, request, dataModel)
    request.user.iclock_url_rel='../..'
    #检查浏览该数据的权限
    if dataModel in [CardCashSZ,ICConsumerList]:
        operation='ipos.iclockdininghall_%s'%(dataModel.__name__.lower())
        if not request.user.has_perm(operation):
            return getJSResponse(u"%s"%("You do not have the browse %s permission!")%(dataModel._meta.verbose_name))
    else:
        if not hasPerm(request.user, dataModel, "browse"):
            return getJSResponse(u"%s"%(_("You do not have the browse %s permission!")%(dataModel._meta.verbose_name)))
    request.model=dataModel
    if request.method=='POST': #post 表示获取自动化的json数据
        userData={}

        jqGrid=JqGrid(request,datamodel=dataModel)
        items=jqGrid.get_items()   #not Paged
        d_sum={'money__sum':0}
        if dataModel==HandConsume or dataModel==ICConsumerList or dataModel==Allowance:
            if dataModel!=ICConsumerList:
                d_sum=items.aggregate(Sum('money'))
            else:
                d_sum=items.exclude(pos_model=9).aggregate(Sum('money'))

            d={}
            d['pin']=u'总计'
            d['PIN']=u'总计'
            d['user_pin']=u'总计'
            d['money']=str(d_sum['money__sum'] or 0)
            if dataModel==ICConsumerList:
                t_money=items.filter(pos_model=9).aggregate(Sum('money'))
                d['money']=str((d_sum['money__sum'] or 0)-(t_money['money__sum'] or 0))
            userData=d#[{'pin':u'总计'},{'user_pin':u'总计'},{'money':str(d_sum['money__sum'] or 0)}]
        cc=jqGrid.get_json(items)
        tmpFile=dataModel.__name__+'_list.js'
        if dataModel.__name__.lower()=='myuser':
            tmpFile='user_list.js'
        tmpFile=request.GET.get(TMP_VAR,tmpFile)
        if appName!='iclock':
            tmpFile=appName+'/'+tmpFile
        t=loader.get_template(tmpFile)
        isedit=int(request.GET.get('e',-1))
        if isedit==0:
            cc['can_change']=False
        else:
            cc['can_change']=hasPerm(request.user, dataModel, 'change')
        try:
            cc['user']=request.user
            rows=t.render(cc)
        except Exception,e:
            print "DataList=====",e
            rows='[]'
            pass
        try:
            t_r="{"+""""userdata":"""+dumps(userData)+","+""""page":"""+str(cc['page'])+","+""""total":"""+str(cc['total'])+","+""""records":"""+str(cc['records'])+","+""""rows":"""+rows+"""}"""
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
                colModel=dataModel.colModels()
            except Exception,e:
                colModel=[]
        else:
            colModel=attShifts.colModels()  #这样写法有利于将来有多个基于attShifts表的查询,可在attShifts中写多个colModl以供调用
        try:
            HeaderNames=dataModel.HeaderModels()
        except:
            HeaderNames=[]
        tblname=ModelName
        if request.GET.has_key("tblName"):
            tblname=request.GET.get("tblName")
        disabledCols=FetchDisabledFields(request.user, tblname)
        flagpage=request.GET.get("flagpage","10")
        settings.PAGE_LIMIT=GetParamValue('opt_users_page_limit','50',request.user.id)
        limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
        if flagpage!="10":
            dds="{"+""""colModel":"""+dumps(colModel)+","+""""disabledcols":"""+dumps(disabledCols)+","+""""limit":"""+str(limit)+"""}"""
            return getJSResponse(dds)

        tmpFile=dataModel.__name__+'_list.html'
        if dataModel.__name__.lower()=='myuser':
            tmpFile='user_list.html'
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
            using_m=request.GET.get('mod_name','')
            cc={
            'app':using_m,
            'limit':limit,
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
            if dataModel==Group:
                cc["permissions"]=getAllAuthPermissions(request.user)
            if dataModel==HandConsume or dataModel==ICConsumerList:

                data=GetParamValue('ipos_params',{},'ipos')
                if data:
                    from mysite.auth_code import auth_code
                    data=auth_code(data.encode("gb18030"))
                    data=loads(data)
                else:
                    data={'pwd':'','main':1,'itype':0,'max_money':'999','pass_key':''}
                cc['params']=dumps1(data)
            if dataModel==IssueCard:
                dataForm=form_for_instance(dataModel())
                cc['form']=dataForm()
            r=render(request,tmpFile,cc)#render_to_response(tmpFile, cc,RequestContext(request, {}))
            return r

        except Exception,e:
#               t=defListTemp(dataModel)
#               t=Template(t)
            print "DataList GET------------",e
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
    if state==0:
        items=items.filter(State=0)
    elif state==1:
        items=items.filter(LastActivity__gte=t1).exclude(State=2)
    elif state==2:
        items=items.filter(LastActivity__gte=t1,State=state)
    elif state==3:
        items=items.filter(Q(LastActivity=None)|Q(LastActivity__lt=t1)).exclude(State=0)

    p=Paginator(items, limit)
    count=p.count
    total=p.num_pages
    pp=p.page(offset)
    pgList=pp.object_list
    #else:
    #    for i in items:
    #           if i.getDynState()==state:
    #                   pgList.append(i)
    #    count=len(pgList)
    #    total=int(ceil(count/float(limit)))
    #    if offset>total:
    #           offset=1
    #    pgList=pgList[(offset-1)*limit:offset*limit]


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
                    if not cmdStr:
                        continue
                    appendDevCmdNew(sns,cmdStr)
            else:
                continue
        adminLog(time=datetime.datetime.now(),User=request.user, action=_(u"autoSebdEmpToDev"), model=employee._meta.verbose).save(force_insert = True)
        return getJSResponse({'ret':0,'message':u"%s"%_(u'Operation Success')})
    else:
        return getJSResponse({'ret':1,'message':u"%s"%_(u'No AuthDept')})
