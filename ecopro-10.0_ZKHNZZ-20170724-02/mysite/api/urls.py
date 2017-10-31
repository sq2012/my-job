#!/usr/bin/env python
#coding=utf-8
from django.conf.urls import include, url
from django.contrib.auth.decorators import permission_required
from mysite.api import views,tests
urlpatterns = [
##数据管理相关
#     url(r'^data/(?P<ModelName>[^/]*)/$', 'iclock.dataview.DataList'),
    url(r'^login/$',views.auth_login),
    url(r'^data/$',views.update_data),
    url(r'^query/$',views.query_data),
    url(r'^delete/$',views.delete_data),
    url(r'^weiang/$',views.weiang_data),
    url(r'^system/$',tests.index),
#    
#    
#    #(r'^report/(?P<ReportName>[^/]*)/$', 'iclock.reportsview.reportIndex'),

]
