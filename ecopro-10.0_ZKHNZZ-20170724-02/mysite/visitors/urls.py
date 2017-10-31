#!/usr/bin/env python
#coding=utf-8
from django.conf.urls import  include, url
from django.contrib.auth.decorators import permission_required
from mysite.iclock import dataview,export
from mysite.visitors import views,tests
from mysite.base import sysview
urlpatterns = [
#数据管理相关
     url(r'^data/(?P<ModelName>[^/]*)/$', dataview.DataList),
    url(r'^export/(?P<ModelName>[^/]*)/$', export.exportList),
    url(r'^data/(?P<ModelName>[^/]*)/_clear_/$', dataview.DataClear),
    url(r'^data/(?P<ModelName>[^/]*)/_del_old_/$', dataview.DataDelOld),
    url(r'^data/(?P<ModelName>[^/]*)/_new_/$', dataview.DataNew),
    url(r'^data/(?P<ModelName>[^/]*)/(?P<DataKey>[^/]*)/$', dataview.DataDetail),
    #(r'^getData/$', 'base.getBaseData.getData'),
    url(r'^vis/hasReasons/$', views.hasReasons),
    url(r'^vis/visitionlogs_his/$', views.visitionlogs_his),
    #(r'^vis/getReasons/$', 'visitors.views.getReasons'),
    url(r'^att/participants_tpl/$',tests.index),
    
    url(r'^isys/(?P<ModelName>[^/]*)/$', sysview.sysList),


]
