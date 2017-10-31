#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.core.tools import *
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
import string,os
import time
from mysite.utils import *
from django.db import models
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import login_required,permission_required
from django import forms
from mysite.iclock.dataproc import *
from django.db.models.query import QuerySet, Q
import operator
from mysite.iclock.filterspecs import FilterSpec
from django.utils.encoding import force_unicode, smart_str
from django.contrib.auth.models import User, Permission
from mysite.iclock.iutils import *
from mysite.iclock.reb	import *
from django.conf import settings
#REBOOT_CHECKTIME, PAGE_LIMIT, ENABLED_MOD, TIME_FORMAT, DATETIME_FORMAT, DATE_FORMAT
from mysite.cab import *
from mysite.iclock.devview import checkDevice
#from iclock.importdata import upload_data
from mysite.iclock.datv import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from mysite.iclock.datas import *
from mysite.iclock.dataview import ChangeList
import datetime

PAGE_VAR = 'p'
STATE_VAR = 's'


def index(request):
#	print params
	e=request.session['employee']
#	print e.id
	params = dict(request.GET.items())
	tmpFile=request.GET.get('t', 'test1.html')#user_temp_list.html AttParam_list11.html  test.html
#	print tmpFile
	if tmpFile == 'staff_USER_OF_RUN.html':
		st_date=datetime.datetime.now()-datetime.timedelta(days=1)
		ed_date=datetime.datetime.now()+datetime.timedelta(days=1)
	else:
		st_date=datetime.datetime.now()-datetime.timedelta(days=30)
	#	print st_date
		ed_date=datetime.datetime.now()+datetime.timedelta(days=30)
	#	print ed_date
	l={}
	l=GetUserScheduler(e.id,st_date,ed_date,0)
#	print l
#分页
	offset = int(request.GET.get(PAGE_VAR, 1))
	limit=settings.PAGE_LIMIT
	state = int(request.GET.get(STATE_VAR, -1))
	paginator =Paginator(l, limit)
	item_count = paginator.count
	if offset>paginator.num_pages: offset=paginator.num_pages
	if offset<1: offset=1
	pgList = paginator.page(offset)
#	print pgList.object_list
	dataOpt={}
	dataOpt['verbose_name']=u'%s'%_('empoyee shift')


	return render_to_response(tmpFile,
		RequestContext(request, {'latest_item_list': pgList.object_list,
		'from': (offset-1)*limit+1,
		'page':offset,
		'limit': limit,
		'item_count': item_count,
		'title': _('empoyee shift'),
		'dataOpt': dataOpt,
		'page_count': paginator.num_pages,
		'is_popup': False,
		}))
