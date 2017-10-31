#!/usr/bin/env python
#coding=utf-8
from django.conf.urls import include, url
from django.contrib.auth.decorators import permission_required
from mysite.iclock import devview,dataview,export,nomodelview,reportsview
from mysite.meeting import getBaseData,views,datamisc
urlpatterns = [
##数据管理相关
     url(r'^data/(?P<ModelName>[^/]*)/$', dataview.DataList),
    url(r'^export/(?P<ModelName>[^/]*)/$', export.exportList),
    url(r'^data/(?P<ModelName>[^/]*)/_clear_/$', dataview.DataClear),
    url(r'^data/(?P<ModelName>[^/]*)/_del_old_/$', dataview.DataDelOld),
    url(r'^data/(?P<ModelName>[^/]*)/_new_/$', dataview.DataNew),
    url(r'^data/(?P<ModelName>[^/]*)/(?P<DataKey>[^/]*)/$', dataview.DataDetail),
    #(r'^data/upload$', 'importdata.uploadData'),				#上传导入数据文件
#    #
    url(r'^getData/$', getBaseData.getData),
    url(r'^employeeforparticipants/$', views.SaveParticipants),
    url(r'^saveattachment/$', views.Savemappicture),
    url(r'^photolocation/$', datamisc.photolocation),
    url(r'^getphotolocation/$', datamisc.getphotolocation),
    url(r'^employeeformeet/$', views.SaveEmployee_meet),
    url(r'^_checktranslog_/$', datamisc.newTransLog), #会议实时记录
    url(r'^_checkmeet_/$', datamisc.MeetState), #会议状态
    url(r'^meetDell/$', datamisc.MeetDell), #会议人员情况
    url(r'^Minute/savefile_MeetMinute/$', views.saveMinutefile),
    url(r'^exportfilename/$', views.exportfilename),
    url(r'^reports/$',reportsview.index),
    url(r'^report/(?P<ReportName>[^/]*)/$',reportsview.reportIndex),


]
