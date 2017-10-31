#!/usr/bin/env python
#coding=utf-8
from django.conf.urls import  include, url
from django.contrib.auth.decorators import permission_required
from mysite.iclock import dataview,export,reportsview
from mysite.acc import accviews,getBaseData,combopen_emp,level_emp,combopen_emp,datamisc,accmap,door_emp,emp_door
urlpatterns = [
##数据管理相关
     url(r'^data/(?P<ModelName>[^/]*)/$', dataview.DataList),
    url(r'^export/(?P<ModelName>[^/]*)/$', export.exportList),
    url(r'^data/(?P<ModelName>[^/]*)/_clear_/$', dataview.DataClear),
    url(r'^data/(?P<ModelName>[^/]*)/_del_old_/$', dataview.DataDelOld),
    url(r'^data/(?P<ModelName>[^/]*)/_new_/$', dataview.DataNew),
    url(r'^data/(?P<ModelName>[^/]*)/(?P<DataKey>[^/]*)/$', dataview.DataDetail),
    url(r'^getData/$', getBaseData.getData),
    url(r'^isys/(?P<ModelName>[^/]*)/$', accviews.index),#门禁权限
#    (r'^iacc/MapManageIndex/$', 'iclock.newiaccess.MapManageIndex'),#地图管理页面
#    (r'^iacc/Map_Monitor/$', 'iclock.newiaccess.Map_Monitor'),#电子地图监控
#    (r'^iacc/iaccessDevReports/$', 'iclock.newiaccess.iaccessDevReports'),#门禁设备与记录报表
#    (r'^iacc/iaccessEmpReports/$', 'iclock.newiaccess.iaccessEmpReports'),#门禁人员与记录报表
#    (r'^iacc/getIacc_MonitorReport/$', 'iclock.newiaccess.getIacc_MonitorReport'),#监控记录表
#    (r'^iacc/getIacc_AlarmReport/$', 'iclock.newiaccess.getIacc_AlarmReport'),#报警记录表
#    (r'^iacc/getIacc_UserRightsReport/$', 'iclock.newiaccess.getIacc_UserRightsReport'),#用户权限表
#    (r'^iacc/getIacc_RecordDetailsReport/$', 'iclock.newiaccess.getIacc_RecordDetailsReport'),#记录明细表
#    (r'^iacc/getIacc_SummaryRecordReport/$', 'iclock.newiaccess.getIacc_SummaryRecordReport'),#记录汇总
#    (r'^iacc/getIacc_EmpUserRightsReport/$', 'iclock.newiaccess.getIacc_EmpUserRightsReport'),#用户权限明细表
#    (r'^iacc/getIacc_EmpDeviceReport/$', 'iclock.newiaccess.getIacc_EmpDeviceReport'),#用户设备

    url(r'^SendDoorData/$', accviews.send_doors_data),#开关门等
    url(r'^SyncDoorData/$', accviews.sync_doors_data),#同步数据

    url(r'^employeeforlevel/$', accviews.SaveLevelEmp),
    url(r'^employeelevel/$', accviews.SaveLevel_Emp),
    url(r'^employeeforfirstopen/$', accviews.SaveFirstOpen_Emp),
    url(r'^employeeforcombopen/$', combopen_emp.SaveEmployee_combopen),
    url(r'^level_emp/$',level_emp.index),
 
#    (r'^door_emp/$','acc.door_emp.index'),
    url(r'^door_emp/$',door_emp.index),
#    (r'^emp_door/$','acc.emp_door.index'),
    url(r'^emp_door/$',emp_door.index),
 
    url(r'^combopen/$',combopen_emp.index),
    url(r'^get_level_emp/$',level_emp.get_level_emp),
    url(r'^get_combopen_emp/$',combopen_emp.get_combopen_emp),
    url(r'^reports/$',reportsview.index),
    url(r'^report/(?P<ReportName>[^/]*)/$', reportsview.reportIndex),
    url(r'^_checktranslog_/$', datamisc.newTransLog), #实时记录下载
    url(r'^_checkinoutlog_/$', datamisc.newInoutLog),
#    #url(r'^_checkdevice_/$', 'acc.datamisc.DeviceState'), #设备状态
    url(r'^getRTlog/$', accmap.getRTlog),
    url(r'^applyaccmap/$', accmap.applyaccmap),
    url(r'^deletemap/$', accmap.del_map),
    url(r'^savemap/$', accmap.savemap),
    url(r'^restartsvr2/$', accviews.restartsvr2),
    url(r'^search_device/$', accviews.search_device),
    url(r'^add_devices/$', accviews.add_devices),
    url(r'^showimganddoor/$', accmap.showimganddoor),
    url(r'^etggetdevcesfortcp485/$', getBaseData.get_devices_of_tcp),#获取非PUSH设备，url故意写乱
]
