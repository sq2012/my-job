#!/usr/bin/env python
#coding=utf-8
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified, HttpResponseNotFound
from django.shortcuts import render_to_response,render
from django.core.exceptions import ObjectDoesNotExist
import string,os
import datetime
import time
from django.db import models
from django.contrib.auth.decorators import login_required,permission_required
from django import forms
from django.utils.encoding import force_unicode, smart_str
from django.contrib.auth.models import Permission, Group
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.iutils import *
#from django.utils.datastructures import SortedDict
from django.core.cache import cache
from mysite.iclock.datautils import *
#from iclock.dataview import *
from django.forms.fields import *
#from django.forms.widgets import ChoiceWidget,RadioSelect,Select#ChoiceFieldRenderer,RendererMixin,Select,RadioChoiceInput
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text, python_2_unicode_compatible
from collections import OrderedDict

from mysite.iclock.models import *
from django.contrib.auth import get_user_model
from mysite.core.mimi import *
from mysite.base.models import *
from mysite.acc.models import *
from mysite.ipos.models import *
from mysite.core.cmdproc import set_pos_device_option,set_options
#from mysite.renderers import DjangoTemplates as MyRender

from mysite.core.zkwidgets import *


def onlyTime(value):
    if value:
        try:
            return value.strftime('%H:%M')
        except:
            return (value+datetime.timedelta(100)).strftime('%H:%M:%S')
    elif str(value)=='00:00:00':
        return '00:00'
    else:
        return ""





#class RadioSelectEx(RadioSelect):
#    renderer = RadioFieldRenderer
#    _empty_value = ''

#class RadioSelect(ChoiceWidget):
#    input_type = 'radio'
#    template_name = 'radios_input.html'
#    option_template_name = 'django/forms/widgets/radio_option.html'


class adminForm(forms.Form):
    def __init__(self, request, data=None, dataKey=None):
        self.request=request
        User=get_user_model()
        try:
            instance=User.objects.get(pk=dataKey)
            isAdd=False
        except:
            instance=None
            isAdd=True
        self.instance=instance
        opts=User._meta
        self.opts=opts
        self.authedepts=None
        self.zones=None
        if request.POST:
            if isAdd:
                self.authedepts=request.POST.get('AuthedDept')
                self.zones=request.POST.get('AuthedZone')
            self.authedroles=request.POST.getlist('AuthedRole')
        exclude=('user_permissions','password','is_active','logintype','loginid')
        if (not request.user.is_superuser):
            if (not request.user.is_alldept):
                exclude=exclude+('is_alldept',)

        if isAdd:
            exclude=exclude+('last_login','date_joined','logincount')
            if not request.user.is_superuser:
                exclude=exclude+('is_superuser','groups')
        else:
            if request.user.pk==instance.pk:
                exclude=exclude+('is_superuser','is_staff', 'groups','is_alldept')
            else:
                if not request.user.is_superuser:
                    exclude=exclude+('is_superuser',)

        field_list = []
        for f in opts.fields + opts.many_to_many:
            if not f.editable: continue
            if exclude and (f.name in exclude):
                continue
            if not isAdd:
                current_value = f.value_from_object(instance)
                formfield=f.formfield(initial=current_value)
            else:
                formfield=f.formfield()
            if formfield:
                if f.name=='username':
                    field_list.insert(0,(f.name,formfield))
                else:
                    field_list.append((f.name, formfield))
                if f.name in ('last_login','date_joined','logincount'):
                    formfield.widget.attrs['readonly']=True
        c=1
        if not isAdd:
            field_list.insert(c,('is_resetPw',forms.BooleanField(label=_('Reset password'), initial=False, required=False)))

        formfield=forms.CharField(widget=forms.PasswordInput(render_value=True), label=_('Password'), initial=isAdd and "" or "111111")
        field_list.insert(2,('Password',formfield))
        formfield=forms.CharField(widget=forms.PasswordInput(render_value=True), label=_('Password again'), initial=isAdd and "" or "111111")
        field_list.insert(3,('ResetPassword',formfield))
        #if not 'is_alldept' in exclude:
        #    field_list.insert(4,('is_alldept',forms.BooleanField(label=_(u'授权所有部门'), initial=False, required=False)))
        #field_list.insert(8,('Tele',forms.CharField(label=_(u'联系电话'), initial='', required=False)))
        #
        self.depts=None
        self.groups=None
        self.rols=None
        role_init=0
        if not self.request.user.is_superuser:
            self.groups=UserAdmin.objects.filter(user=request.user,dataname=str(Group._meta))
        if (not isAdd):# and ((not self.request.user.is_alldept)):
            try:
                #self.depts=DeptAdmin.objects.filter(user=instance)
                self.roles=userRole.objects.filter(userid=instance.pk)
                if self.roles:
                    role_init=self.roles[0].roleid.roleid
            except: pass
        c=10
        #AUTHE_DEPT=[]
        #if self.depts:#用户仅传递已授权部门
        #	d=self.depts
        #	for i in d:
        #		t=(i.dept_id,i.dept.objByID(i.dept_id).DeptName)
        #		AUTHE_DEPT.append(t)
        #formfield=MultipleChoiceFieldEx(choices=AUTHE_DEPT,label=_('AuthedDept'))
        if isAdd:
            formfield=forms.CharField(label=_('AuthedDept'), initial='', required=True)
            if formfield and (not instance or request.user.pk!=instance.pk):
                field_list.insert(5,('AuthedDept',formfield))
            formfield=forms.CharField(label=_(u'授权区域'), initial='', required=False)
            if formfield and (not instance or request.user.pk!=instance.pk):
                field_list.insert(6,('AuthedZone',formfield))

        #print "------------",field_list
        if not self.request.user.is_superuser:
            objs=UserAdmin.objects.filter(user=request.user,dataname=str(Group._meta)).values('owned')
            if not isAdd:
                if instance.id == request.user.id:
                    objs=[]
                    for t in  self.request.user.groups.values_list():
                        objs.append(t[0])
            qs=Group.objects.filter(id__in=objs)
            self.groups=qs
            grouplist=[]
            for t in qs:
                grouplist.append((t.id,t.name))
            groups=[]
            if not isAdd:
                for t in  instance.groups.values_list():
                    groups.append(t[0])
            formfield=MultipleChoiceField(choices=grouplist,label=_(u'管理组'),initial=groups,required=True)
            field_list.append(('groups',formfield))





        #显示所有职务
        userRoleobj=userRoles.objects.all()
        AUTHE_ROLE=[]
        AUTHE_ROLE.append((0,'------'))
        for u in userRoleobj:
            AUTHE_ROLE.append((u.roleid,u.roleName))
        formfield=ChoiceField(choices=AUTHE_ROLE,initial=role_init,label=_('Role'),required=False)
        field_list.append(('AuthedRole',formfield))
        self.base_fields = OrderedDict(field_list)
        forms.Form.__init__(self, data)
    def clean_ResetPassword(self):
        p1=self.cleaned_data.get('Password', '')
        p2=self.cleaned_data.get('ResetPassword', '')
        if p1==p2: return p2
        raise forms.ValidationError(_("Must be same as Password"))
    def clean_Password(self):

        p1=self.cleaned_data.get('Password', '')
        if len(p1)<4:
            raise forms.ValidationError(_("The length must be great than 4"))
        return p1
    def save(self):
        opts=self.opts
        u=self.instance
        try:
            if self.request.user.pk==self.instance.pk:
                u=self.request.user
        except:
            pass

        if hasattr(settings,'DEMO') and settings.DEMO==1:
            if 'is_superuser' in self.cleaned_data and  self.cleaned_data['is_superuser']:
                raise forms.ValidationError(_('Not allowed to change'))
            if u and u.is_superuser:
                raise forms.ValidationError(_('Not allowed to change'))

        if u and self.cleaned_data['is_resetPw']:
            u.set_password(self.clean_Password())
        if not u:
            User=get_user_model()

            isexist=User.objects.all().filter(username=self.cleaned_data['username'])
            if isexist:
                u=isexist[0]
                if u.DelTag==0:
                    raise forms.ValidationError(_(u"该用户已存在"))
            else:
                User=get_user_model()

                u = User.objects.create_user(self.cleaned_data['username'],
                    self.cleaned_data['email'], self.cleaned_data['Password'])
        for f in opts.fields + opts.many_to_many:
            if not f.editable: continue
            if f.name in self.cleaned_data:
                f.save_form_data(u,self.cleaned_data[f.name])
        if (not u.is_superuser) and (not self.request.user.is_superuser) :
            if not u.AutheTimeDept:
                u.AutheTimeDept=self.request.user.AutheTimeDept
        u.DelTag=0
        u.save()

        v=GetParamValue('DEPTVERSION')
        settings.DEPTVERSION=v

        cache.delete("%s_depttree_%s_%s"%(settings.UNIT, u.id,settings.DEPTVERSION))
        cache.delete("%s_userdepts_%s_%s"%(settings.UNIT, u.id,settings.DEPTVERSION))

        #UpdateDeptCache()
        #保存用户职务
        role_init=0
        if self.authedroles:
            role_init=int(self.authedroles[0])
            if role_init>0:
                userRole.objects.filter(userid=u).delete()
                d=userRoles.objects.get(roleid=role_init)
                userRole(userid=u, roleid=d).save()
            else:
                userRole.objects.filter(userid=u).delete()
        if u.is_superuser: return u
        try:
            if u.is_alldept:return u
        except:
            pass
        if self.depts:
            self.depts.delete()

        zones=self.zones
        if zones:
            try:
                authZone=zone.objects.filter(id__in=loads(zones))
                k=u.id
                ZoneAdmin.objects.filter(user=k).delete()

                for t in authZone:
                    ZoneAdmin(user=u, code=t).save()
            except Exception,e:
                print e

        depts=self.authedepts
        if not depts:return u
        #isContainChild=self.request.POST.get("isContainChild","")

        #if isContainChild=="1":
        #	ChildDepts=[]
        #	for t in depts:
        #		t=int(t)
        #		#d=department.objects.get(DeptID=t)
        #		if t not in ChildDepts:
        #			ChildDepts=getAllChildDepts(t,self.request)
        #			for t in ChildDepts:
        #				DeptAdmin(user=u, dept_id=t).save()
        #
        #else:
        #	for t in depts:
        #		d=department.objects.get(DeptID=t)
        #		DeptAdmin(user=u, dept=d).save()

        authData=loads(depts)
        k=u.id
        DeptAdmin.objects.filter(user=k).delete()
        for t in authData:
            DeptAdmin(user=u, dept_id=t['deptid'],iscascadecheck=t['iscascadecheck']).save()



        return u

def retUserForm(request, f, isAdd=False):
    request.user.iclock_url_rel="../../.."
    d=[]
    c=""
    timeDeptName=''
    is_superuser=False
    if not isAdd:
        deptid=f.instance.AutheTimeDept
        is_superuser=f.instance.is_superuser
        if deptid:
            p=department.objByID(deptid)
            if p:
                timeDeptName=str(p.DeptNumber)+ ' '+p.DeptName
            else:
                timeDeptName=''
    #dataModel=User
    #key=(dataModel._meta.pk.name in f.cleaned_data) and f.cleaned_data[dataModel._meta.pk.name]

    if hasattr(f,"depts") and f.depts:
        for t in f.depts:
            d.append(int(t.dept.DeptID))
            c+=t.dept.DeptName+','
    cc={"deptIDs":d,"deptTitle":c[:-1],'parent_name':timeDeptName}
    dataModel=GetModel('User')
    inputFields, dtFields=ModifyFields(dataModel)
    inputFields=inputFields+',AuthedDept'+',Password'+',ResetPassword'
    User=get_user_model()

    r=render(request,'User_edit.html',
        {"form": f,
            "iclock_url_rel": request.user.iclock_url_rel,
            "add":isAdd,
            "is_superuser":is_superuser,
            "inputFields":inputFields,
            #"dtFields":dtFields,
            "dataOpt": User._meta,
            "deptIDs":d,
            "deptTitle":c[:-1],

            'parent_name':timeDeptName,


            "request":request})
    return r

def doCreateAdmin(request, dataModel, dataKey=None):	# 生成 管理员 管理 页面

    if dataKey=="_new_":
        if request.user.has_perm('add_user'):
            f=adminForm(request, dataKey=dataKey)

            return retUserForm(request, f, isAdd=True)
    elif dataKey:
        f=adminForm(request, dataKey=dataKey)
        if not f.instance:
            s=_("Keyword \"%(object_name)s\" Data do not exist!")%{'object_name':dataKey}
            return getJSResponse({"ret":1,"message":u"%s"%s})
        if not request.user.is_superuser:
            if f.instance.is_superuser:
                return getJSResponse({"ret":1,"message":u"%s"%_('No permission')})
        if request.user.is_superuser:
            if f.instance.is_superuser and request.user.username!=f.instance.username:
                return getJSResponse(u"result=1;message=%s"%(_('No permission')))
        return retUserForm(request,f)
#	print "No permissions"
    return getJSResponse({"ret":1,"message":u"%s"%_('No permission')})

def doPostAdmin(request, dataModel, dataKey=None): # 管理员 管理
    f=adminForm(request, data=request.POST, dataKey=dataKey)
    if not f.is_valid():
        s=f.errors.as_text()
        return getJSResponse({"ret":1,"message":u"%s"%s})
    else:
        try:
            u=f.save()
            k="user_id_%s"%u.pk
            try:
                cache.delete(k)
            except:
                pass
            log=adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, object=f.cleaned_data['username'])#
            if dataKey=="_new_": log.action=_(u"新增")
            log.save(force_insert=True)
        except Exception,e:
            #import traceback;traceback.print_exc()
            estr="%s"%e
            if  ("Duplicated" in estr):
                return getJSResponse({"ret":1,"message":u"%s%s"%(_('save failed'),_(u'用户名重复'))})

            if "Not allowed to change" in estr:
                return getJSResponse({"ret":1,"message":u"%s%s"%(_('save failed'),estr)})

            return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})


            #return getJSResponse({"ret":1,"message":u"%s-%s"%(f.cleaned_data['username'],_('Duplicated'))})

            #return render_to_response("info.html", {"title":  u"用户",
                            #"content": u"%s用户已经存在"%f.cleaned_data['username']
                            #})
        try:
            UserAdmin(user=request.user, owned=u.pk,dataname=str(dataModel._meta)).save()
        except Exception,e:
            pass
            #print "UserAdmin====",e
        return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})

#		return HttpResponseRedirect("../")

class iclockForm(forms.Form):
    def __init__(self, request, data=None, dataKey=None):
        self.request=request
        try:
            instance=iclock.objects.get(pk=dataKey)
            self.isAdd=False
        except:
            instance=None
            self.isAdd=True
        lock_fields=[]
        try:
            lock_fields=iclock.Admin.lock_fields
        except:
            pass
        self.instance=instance
        opts=iclock._meta
        self.opts=opts
        self.authedepts=None
        if request.POST:
            if self.isAdd:
                self.authedepts=request.POST.get('AuthedDept')
        field_list = []
        exclude=('LockFunOn',)
        using_m=request.GET.get('mod_name','att')
        if using_m=='ipos':
            PRODUCTTYPE=(
                (11,_(u'消费机')),
                (12,_(u'出纳机')),
                (13,_(u'补贴机')),)

        for f in opts.fields + opts.many_to_many:
            if not f.editable: continue

            fst=str(type(f.formfield()))
            fstl=fst[8:-2].split('.')
            if exclude and using_m!='acc' and (f.name in exclude): continue
            if using_m=='ipos' and f.name=='Authentication':continue
            if using_m!='acc' and f.name.lower()=='ipaddress':continue
            if using_m!='acc' and f.name.lower()=='purpose':continue
            if not self.isAdd:
#				current_value = f.value_from_object(instance)
                try:
                    if isinstance(f.value_from_object(instance),datetime.time):
                        current_value=f.value_from_object(instance)
                    else:
                        current_value = instance and f.value_from_object(instance) or None
                except:
                    current_value = instance and f.value_from_object(instance) or None
                if 'TimeField' in fstl:
                    current_value=onlyTime(current_value)
                #if  f.name=='DeptID':
                    #formfield = form_field_readonly(f, initial=current_value)
                if f.name.lower()=='producttype':
                    if current_value in [5,15]:
                        formfield = f.formfield(widget=ForeignKeyInput,initial=5)#form_field_readonly(f, initial=5)
                    elif current_value in [11,12,13]:

                        #formfield=forms.IntegerField(label=_(u'消费机类型'),initial=current_value,widget=forms.Select(choices=PRODUCTTYPE))


                        formfield = f.formfield(label=_(u'消费机类型'),initial=current_value,choices=PRODUCTTYPE)
                    else:
                        formfield=f.formfield(initial=current_value)

                elif f.name.lower()=='dz_money':
                    if current_value and current_value==int(current_value):
                        formfield=f.formfield(initial=int(current_value))
                    else:
                        formfield=f.formfield(initial=current_value)



                else:
                    formfield=f.formfield(initial=current_value)
            else:
                #if  f.name=='DeptID':
                #	formfield = form_field_readonly(f)
                if f.name.lower()=='producttype':
                    current_value=settings.MOD_DICT[using_m]
                    if using_m=='ipos':
                        formfield=forms.IntegerField(label=_(u'消费机类型'),widget=forms.Select(choices=PRODUCTTYPE))
                    else:
                        formfield=f.formfield(initial=current_value)
                else:
                    formfield=f.formfield()
            if formfield:
                field_list.append((f.name, formfield))

        self.depts=None
        #if not isAdd:
        #	try:
        #		self.depts=IclockDept.objects.filter(SN=instance)
        #	except: pass
        c=6
        if self.isAdd:
            #AUTHE_DEPT=[]
            #if self.depts:#设备仅传递已授权部门
            #	d=self.depts
            #	for i in d:
            #		t={'deptid':i.dept_id,'iscascadecheck':i.iscascadecheck}
            #		AUTHE_DEPT.append(t)
            #formfield=MultipleChoiceFieldEx(choices=AUTHE_DEPT,label=_('AuthedDept'))
            #if formfield and (not instance or request.user.pk!=instance.pk):
            #	field_list.insert(c,('AuthedDept',formfield))
            #if self.depts:
            #	for dept in self.depts:
            #		formfield=dept._meta.get_field('dept').formfield(initial=dept.dept_id)
            #		if formfield :
            #			field_list.insert(c,('AuthedDept',formfield))
            #			c+=1
            #else:
            #	formfield=IclockDept._meta.get_field('dept').formfield()
    #			if formfield and (not instance):#or request.SN.pk!=instance.pk
            auth_lbl=_(u'归属部门')
            if using_m=='acc':auth_lbl=_(u'归属区域')
            if using_m!='ipos':
                field_list.insert(c,('AuthedDept',forms.CharField(label=auth_lbl, initial='', required=True)))
                #field_list.insert(c,('AuthedDept',formfield))
        if using_m=='ipos':
            if self.isAdd:
                isover=0
            else:
                isover=GetParamValue('IsOverCheck_%s'%instance.SN,'0')
            if isover=='1':
                isover=True
            else:
                isover=False
            field_list.append(('IsOverCheck',forms.BooleanField(label=_(u'超额验证'),initial=isover,  required=False)))

            dinings=Dininghall.objects.all().exclude(DelTag=1)
            dd=[]
            for d in dinings:
                dd.append((int(d.id),d.name))
            DINING=tuple(dd)
            self.dining=request.POST.get('dining')
            if self.isAdd:

                field_list.append(('dining',forms.IntegerField(label=_(u'归属餐厅'),widget=forms.Select(choices=DINING))))
            else:
                dininghall=IclockDininghall.objects.filter(SN=instance)
                dining=0
                if dininghall.count()>0:
                    dining=dininghall[0].dining.id
                field_list.append(('dining',forms.IntegerField(label=_(u'归属餐厅'),initial=dining,widget=forms.Select(choices=DINING))))
        if using_m=='acc':

            auth_lbl=_(u'通讯方式')
            #field_list.insert(1,('CommType',forms.CharField(label=auth_lbl, initial='', required=True)))
            choices=((u'1', u'HTTP'), (u'2', u'%s'%_(u'TCP/IP')),(u'3', u'%s'%_(u'RS485')))
            if self.isAdd:
                formfield=forms.ChoiceField(widget=RadioSelectEx, label=auth_lbl, initial=u'1',choices=choices,help_text=_(u'(TCP/IP和RS485是指不具备WEB功能的设备的通讯方式)'))
            else:
                initial_value=1
                if self.instance.ProductType==15:
                    initial_value=2
                    if ':' in self.instance.IPAddress:
                        initial_value=3
                formfield=forms.ChoiceField(widget=RadioSelectEx, label=auth_lbl, initial=initial_value,choices=choices,help_text=_(u'(TCP/IP和RS485是指不具备WEB功能的设备的通讯方式)'))

            field_list.insert(1,('CommType',formfield))
            if not self.isAdd:
                f4to2i=GetParamValue('f4to2_%s'%dataKey,'0')
                if f4to2i=='on':
                    f4to2i=1
                f4to2i=int(f4to2i)
                f4to2=False
                if f4to2i==1:
                    f4to2=True

                field_list.append(('four_to_two',forms.BooleanField(label=_(u'四门转2门双向'), initial=f4to2, required=False,help_text=_(u'仅对四门控制器有效'))))


                AutoServerMode=GetParamValue('AutoServer_%s'%dataKey,'0')
                if AutoServerMode=='on':
                    AutoServerMode=1
                AutoServerMode=int(AutoServerMode)
                AutoServer=False
                if AutoServerMode==1:
                    AutoServer=True

                field_list.append(('AutoServerMode',forms.BooleanField(label=_(u'启用反潜'), initial=AutoServer, required=False,help_text=_(u'仅对支持PUSH控制器有效,全局反潜需要开启此参数'))))



        self.base_fields = OrderedDict(field_list)
        forms.Form.__init__(self, data)
    def save(self):
        opts=self.opts
        u=self.instance
        using_m=self.request.GET.get('mod_name','')
        is_restart_pull=0
        if not u:
            isexist=iclock.objects.filter(SN=self.cleaned_data['SN'])
            if isexist:
                k=isexist[0]
                if k.DelTag==1:
                    u=iclock(DelTag=0)
                else:
                    raise Exception("Duplicated Iclock SN: %s"%self.cleaned_data['SN'])
            else:
                if using_m=='ipos':
                    if not self.cleaned_data['ProductType']:
                        self.cleaned_data['ProductType']=11
                u=iclock(TransInterval=1,TransTimes='00:00;14:05',UpdateDB='1111100000',Alias=self.cleaned_data['Alias'],SN=self.cleaned_data['SN'],TZAdj=8,LogStamp=0,OpLogStamp=0,PhotoStamp=0,DelTag=0,ProductType=self.cleaned_data['ProductType'],State=1,CreateTime=datetime.datetime.now())
        for f in opts.fields + opts.many_to_many:
            if not f.editable:
                continue
            if f.name in self.cleaned_data:
                #print f.name,self.cleaned_data[f.name]
                f.save_form_data(u,self.cleaned_data[f.name])
        f4to2=0
        f4to2i=0
        AutoServer=0
        AutoServeri=0
        if using_m=='acc':
            cType=int(self.request.POST.get('CommType',1))
            pType=5
            if cType!=1:
                pType=15
            if u.ProductType!=pType or u.IPAddress!= self.request.POST.get('IPAddress',''):
                cache.set(settings.UNIT + '_restart_pull', 1)#30秒后pull服务自动重启标记

            if u.ProductType!=4 and u.ProductType!=9:
                u.ProductType=pType
            if u.ProductType in [5,15]:
                f4to2=self.request.POST.get('four_to_two',0)
                if f4to2=='on':f4to2=1
                f4to2i=GetParamValue('f4to2_%s'%self.cleaned_data['SN'],'0')
                if f4to2i=='on':
                    f4to2i=1
                f4to2i=int(f4to2i)
                SetParamValue('f4to2_%s'%self.cleaned_data['SN'],f4to2)

                AutoServer=self.request.POST.get('AutoServerMode',0)
                if AutoServer=='on':AutoServer=1
                AutoServeri=GetParamValue('AutoServer_%s'%self.cleaned_data['SN'],'0')
                if AutoServeri=='on':
                    AutoServeri=1
                AutoServeri=int(AutoServeri)
                SetParamValue('AutoServer_%s'%self.cleaned_data['SN'],AutoServer)





        u.save()
        if u.ProductType in [4,5,15,25]:
            auto_add_door(u,0,0)
            #if u.ProductType in [4,15]:
            #	auto_add_door(u,0,0)
            #else:
            #	if f4to2i!=f4to2:
            #		auto_add_door(u,0,0)
        if f4to2i!=f4to2 and u.ProductType in [5,15]:

            t_obj=device_options.objects.filter(SN=u.SN,ParaName='LockFunOn')
            if t_obj:
                if t_obj[0].ParaValue and int(t_obj[0].ParaValue)==4:
                    optstr="Door4ToDoor2=%d"%f4to2
                    set_options(u.SN,optstr)
#		if AutoServeri!=AutoServer and u.ProductType in [5,15]:
        if u.ProductType in [5,15]:
            optstr="AutoServerFunOn=%d"%AutoServer
            set_options(u.SN,optstr)

        if self.isAdd:

            if using_m=='ipos':
                pass
            elif u.ProductType in [4,5,25] or using_m=='acc' :
                authData=loads(self.authedepts)
                k=self.cleaned_data['SN']
                IclockZone.objects.filter(SN=k).delete()
                for t in authData:
                    if t['deptid']==0:continue
                    IclockZone(SN=u, zone_id=t['deptid']).save()

                if u.ProductType in [4,5,15,25]:
                    from mysite.core.cmdproc import sendTimeZonesToAcc,sendHolidayToAcc
                    sendTimeZonesToAcc(None,[u])
                    sendHolidayToAcc(None,[u.SN])


            else:
                authData=loads(self.authedepts)
                k=self.cleaned_data['SN']
                IclockDept.objects.filter(SN=k).delete()
                for t in authData:
                    IclockDept(SN=u, dept_id=t['deptid'],iscascadecheck=t['iscascadecheck']).save()
        if using_m=='ipos':
            isover=self.request.POST.get('IsOverCheck','')
            if isover=='on':
                isover='1'
            else:
                isover='0'
            SetParamValue('IsOverCheck_%s'%u.SN,isover)
            if self.dining:
                try:
                    dining=Dininghall.objects.get(id=self.dining)
                    IclockDininghall.objects.filter(SN=u).delete()
                    IclockDininghall(SN=u,dining=dining).save()
                except Exception,e:
                    print e
                    pass
            set_pos_device_option(u)




        return u


def ModifyFields(dataModel):
    fields = dataModel._meta.fields
    dtFields = ''		# 日期时间 字段，加日历和时间
    inputFields = ''	# 必输字段
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

def retIclockForm(request, f, isAdd=False):
    request.user.iclock_url_rel="../../.."
    d=[]
    #c=""
    #if f.depts:
    #	for t in f.depts:
    #		d.append(int(t.dept.DeptID))
    #		c+=t.dept.DeptName+','
    #cc={"deptIDs":d,"deptTitle":c[:-1]}
    dataModel=GetModel('iclock')



#	inputFields, dtFields=ModifyFields(dataModel)
#	inputFields=inputFields+',AuthedDept'
    return render(request,iclock.__name__+'_edit.html',
        {"form": f,
            "iclock_url_rel": request.user.iclock_url_rel,
            "isAdd": isAdd,
            "add":isAdd,
#			"inputFields":inputFields,
#			"dtFields":dtFields,
            "dataOpt": dataModel._meta,
            "request":request})


def doCreateIclock(request, dataModel, dataKey=None):	# 生成 管理员 管理 页面
    if dataKey=="_new_":
#		if request.user.has_perm('add_user'):
        f=iclockForm(request, dataKey=dataKey)
        return retIclockForm(request, f, isAdd=True)
    elif dataKey:
        f=iclockForm(request, dataKey=dataKey)
        if not f.instance:
            s=_("Keyword \"%(object_name)s\" Data do not exist!")%{'object_name':dataKey}
            return getJSResponse({"ret":1,"message":u"%s"%s})
        return retIclockForm(request,f)
#	print "No permissions"
    return getJSResponse({"ret":1,"message":u"%s"%_('No permission')})
def doPostIclock(request, dataModel, dataKey=None):	# 生成 管理员 管理 页面
    f=iclockForm(request, data=request.POST, dataKey=dataKey)
    ic=iclock.objects.all().exclude(DelTag=1).count()
    getISVALIDDONGLE()
    if dataKey=="_new_" and  ic>=settings.MAX_DEVICES:

        return getJSResponse({"ret":1,"message":u"%s%s"%(_('save failed'),_(u'设备超过点数'))})

    if not f.is_valid():
        print "doPostIclock==",f.errors.as_text(),f.cleaned_data
        return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})
        #return retUserForm(request,f, isAdd=(dataKey=="_new_"))
    else:
        try:

            u=f.save()
            log=adminLog(time=datetime.datetime.now(),User=request.user, model=dataModel._meta.verbose_name, object=f.cleaned_data['SN'])#
            if dataKey=="_new_": log.action=u"%s"%_(u"新增")
            log.save()

        except Exception,e:
            estr="%s"%e
            if  ("Duplicated" in estr):
                return getJSResponse({"ret":1,"message":u"%s%s"%(_('save failed'),_(u'序列号重复'))})
            return getJSResponse({"ret":1,"message":u"%s"%_('save failed')})

        return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})
