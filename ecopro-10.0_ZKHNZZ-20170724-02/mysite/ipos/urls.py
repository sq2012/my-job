#!/usr/bin/env python
#coding=utf-8
from django.conf.urls import include, url
from django.contrib.auth.decorators import permission_required
from mysite.ipos import dataview,cardview,export,getBaseData,reportsview,taskview
"""zket11"""
urlpatterns = [
#数据管理相关
    url(r'^data/(?P<ModelName>[^/]*)/$', dataview.DataList),
    url(r'^issuecard/(?P<ModelName>[^/]*)/$', cardview.issuecard_index),
    url(r'^export/(?P<ModelName>[^/]*)/$', export.exportList),
    url(r'^isys/(?P<ModelName>[^/]*)/$', cardview.index),
    url(r'^data/(?P<ModelName>[^/]*)/_clear_/$', dataview.DataClear),
    url(r'^data/(?P<ModelName>[^/]*)/_del_old_/$', dataview.DataDelOld),
    url(r'^data/(?P<ModelName>[^/]*)/_new_/$', dataview.DataNew),
    url(r'^data/(?P<ModelName>[^/]*)/(?P<DataKey>[^/]*)/$', dataview.DataDetail),
    url(r'^getData/$', getBaseData.getData),
    url(r'^get_sys_card_no/$',cardview.Get_Sys_Card_no),
    url(r'^save_add_card_bak_data/',cardview.funIssueAddCardBakSave),#发卡funIssueAddCardSave
    url(r'^save_issuecard_data/',cardview.funIssueAddCardSave),
    url(r'^save_card_manage/$',cardview.funSaveCardmanage),
    url(r'^save_operate_bak_data/',cardview.funIssueCardBakSave),
    url(r'^save_operate_data/',cardview.funIssueCardSave),
    url(r'^change_card_info/',cardview.funChangeCardInfo),
    url(r'^valid_card/$',cardview.funValidCard),
    url(r'^reports/$',reportsview.index),
    url(r'^report/(?P<ReportName>[^/]*)/$', reportsview.reportIndex),
    url(r'^tasks/import_Allowance/$', taskview.import_Allowance),
    url(r'^tasks/import_Merchandise/$', taskview.import_Merchandise),
    url(r'^tasks/import_IssueCard/$', taskview.import_IssueCard),

]
