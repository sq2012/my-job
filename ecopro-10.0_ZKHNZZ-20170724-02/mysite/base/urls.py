#!/usr/bin/env python
#coding=utf-8
from django.conf.urls import  url
#from django.contrib.auth.decorators import permission_required
from mysite.iclock import dataview,export
from mysite.base import sysview
from mysite.base import register_view

urlpatterns = [
##数据管理相关
     url(r'^data/(?P<ModelName>[^/]*)/$', dataview.DataList),
    url(r'^export/(?P<ModelName>[^/]*)/$', export.exportList),
    url(r'^data/(?P<ModelName>[^/]*)/_clear_/$', dataview.DataClear),
    url(r'^data/(?P<ModelName>[^/]*)/_del_old_/$', dataview.DataDelOld),
    url(r'^data/(?P<ModelName>[^/]*)/_new_/$', dataview.DataNew),
    url(r'^data/(?P<ModelName>[^/]*)/(?P<DataKey>[^/]*)/$', dataview.DataDetail),
    url(r'^isys/(?P<ModelName>[^/]*)/$', sysview.sysList),
 
    #软件授权用到的接口
    url(r'^get_regional_data', register_view.get_regional_data),
    url(r'^do_active_licence', register_view.do_active_licence),
    url(r'^do_import_licence', register_view.do_import_licence),
    url(r'^download_upk_file', register_view.download_upk_file),
]
