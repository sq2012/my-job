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
    spedys=USER_SPEDAY.objects.filter(id__in=keys)
    try:
        for spedy in spedys:
            aa=(spedy.EndSpecDay-spedy.StartSpecDay).total_seconds()
            cc=int(tianshu) * 24*60*60-60
            if  not tianshu:
                return getJSResponse({"ret":1,"message":u'%s'%_(u'结转天数为空，无法结转')})
            if aa<cc:
                return getJSResponse({"ret":1,"message":u'%s'%_(u'结转失败,结转时间大于请假时间')})
        USER_SPEDAY.objects.filter(id__in=keys).update(jiezhuangDay=jieTime,tianshu=tianshu,jiezhuang=1,jieYUANYING=jieYUANYING)
    except:
        return getJSResponse({"ret":1,"message":u'%s'%_(u'结转失败')})
    return getJSResponse({"ret":0,"message":u'%s'%_(u'结转成功')})