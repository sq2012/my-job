#!/usr/bin/env python
#coding=utf-8
from django.conf.urls import include, url
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from mysite.iclock import devview,customization,dataview,simpledataview,export,datamisc,datasql,datamini,homeview,browsepic,importwm,expview,filemngview,fileprocess,home_attention
from mysite.iclock import nomodelview,reports,reportsview,schedule,shiftsview,departments,originalreports,process,getColModel,dataproc,taskview
from mysite.ipos import ic_pos_devview
urlpatterns = [
#设备连接相关
    url(r'^cdata$', devview.cdata),
    url(r'^event$', devview.events),  #门禁一体机事件
    url(r'^bgdata$', devview.bgdata),
    url(r'^rtdata$', devview.rtdata),

    url(r'^getrequest$', devview.getreq),
    url(r'^devicecmd$', devview.devpost),
    url(r'^fdata$', devview.postPhoto),
    url(r'^registry$', devview.registry),
    url(r'^push$', devview.push),
    url(r'^query_device_params', devview.query_device_params),
    url(r'^querydata$', devview.querydata),
#数据管理相关
    url(r'^cheligang/(?P<ModelName>[^/]*)/$', customization.cheligang),
    url(r'^ligang/(?P<ModelName>[^/]*)/$', customization.ligang),
    url(r'^chejiezhuang/(?P<ModelName>[^/]*)/$', customization.chejiezhuang),
    url(r'^jiezhuang/(?P<ModelName>[^/]*)/$', customization.jiezhuang),
    url(r'^fileDelete/(?P<ModelName>[^/]*)/$', fileprocess.fileDelete),
    url(r'^data/autosendemptodev$', dataview.autoSendEmpToDev),
    url(r'^data/(?P<ModelName>[^/]*)/$', dataview.DataList),
    url(r'^simple_data/(?P<ModelName>[^/]*)/$', simpledataview.index),#提供简单数据
    url(r'^simple_datas/(?P<ModelName>[^/]*)/$', simpledataview.gridIndex),#提供简单数据
    url(r'^export/(?P<ModelName>[^/]*)/$', export.exportList),
    url(r'^data/(?P<ModelName>[^/]*)/_clear_/$', dataview.DataClear),
    url(r'^data/(?P<ModelName>[^/]*)/_del_old_/$', dataview.DataDelOld),
    url(r'^data/(?P<ModelName>[^/]*)/_new_/$', dataview.DataNew),
    url(r'^data/(?P<ModelName>[^/]*)/(?P<DataKey>[^/]*)/$', dataview.DataDetail),
    url(r'^data/(?P<ModelName>[^/]*)/miniData$', datamini.getMiniData),
    url(r'^data/(?P<ModelName>[^/]*)/getCopyInfo$', datamisc.getCopyInfo),
    url(r'^data/(?P<ModelName>[^/]*)/sendnew$', datamisc.sendnew),
    url(r'^_checktranslog_/$', datamisc.newTransLog), #实时记录下载
#    url(r'^data/_checkoplog_$', 'datamisc.newDevLog'), #设备实时记录
#    url(r'^data/ic1ock$', datasql.sql_page),				#执行SQL
    #(r'^data/upload$', 'importdata.uploadData'),				#上传导入数据文件
    url(r'^apply/(?P<ModelName>[^/]*)/_new_/$', dataview.apply_DataNew),#个人申请请假和加班


#考勤相关
    url(r'^att/forget/$', nomodelview.forget),
    url(r'^att/report_annual/$', nomodelview.report_annual),
    url(r'^att/annualstatic/$', nomodelview.annualstatic),
    url(r'^att/deleteAddTrans/$', nomodelview.deleteAddTrans),     #删除补的考勤记录
    #(r'^att/setOptions/$', 'nomodelview.setOptions'),
    url(r'^att/clearUserDefinedRep/$',nomodelview.clearUserDefinedRep), #清除所有自定义报表
    url(r'^att/searchShifts/$', nomodelview.searchShifts),              #查询排班
    url(r'^att/fpfacemanage/$', nomodelview.fpfaceManage),#指纹面部管理
     url(r'^att/searchComposite/$', shiftsview.searchComposite),              #查询综合排班
    url(r'^att/searchNoShift/$', shiftsview.searchNoShift),              #查询综合排班
    url(r'^att/deleteTmpShifts/$', nomodelview.deleteTmpShifts),        #清除临时排班
    url(r'^att/doDeleteTmpShifts/$', schedule.doDeleteTmpShifts),    #清除临时排班操作
    url(r'^att/saveCheckForget/$',nomodelview.saveCheckForget),
    url(r'^att/assignedShifts/$', nomodelview.assignedShifts),
    url(r'^att/shift_detail/$', nomodelview.shift_detail),
    url(r'^att/addShiftTimeTable/$', schedule.addShiftTimeTable),
    url(r'^att/deleteEmployeeShift/$', schedule.deleteEmployeeShift),     #删除员工排班详情
    url(r'^att/deleteAllShiftTime/$', schedule.deleteAllShiftTime),
#    (r'^att/delEmpFromDev/$', 'nomodelview.deleteEmpFromDevice'),        #按部门人员从设备中删除人员
    url(r'^att/delFingerFromDev/$', nomodelview.delFingerFromDev),        #按部门人员从设备中删除人员的指纹
    url(r'^att/tmpshifts/$', schedule.ConvertTemparyShifts),                    #操作临时排班
    url(r'^att/deleteShiftTime/$', schedule.deleteShiftTime),
    url(r'^att/worktimezone/$', nomodelview.worktimezone),
    url(r'^att/ihrreminddetail/$', nomodelview.ihrreminddetail),#人事信息提醒详情
    url(r'^att/ihrreversedetail/$', nomodelview.ihrreversedetail),
    url(r'^att/attrule/$', nomodelview.attrule),
    url(r'^att/specialday/$', nomodelview.savespecialday),
    url(r'^att/auditedTrans/$', nomodelview.auditedTrans),            #考勤记录加备注
    url(r'^att/getLeaveClass/$', nomodelview.getLeaveClass),
    url(r'^att/deleteLeaveClass/$', nomodelview.deleteLeaveClass), 
    url(r'^att/submitLeaveClass/$', nomodelview.submitLeaveClass), 
    url(r'^att/submitAttParam/$', nomodelview.submitAttParam),
    url(r'^att/calcReport/$', nomodelview.calcReport),
    url(r'^att/calcReport/$', nomodelview.calcReport),
    url(r'^att/calcLeaveReport/$', nomodelview.calcLeaveReport),#假类汇总表
    url(r'^att/department_report/$', nomodelview.department_report),
    url(r'^att/dailycalcReport/$', nomodelview.dailycalcReport),
    url(r'^att/ExcepDaily/$', nomodelview.ExcepDaily),#异常表
    url(r'^att/calcAttShiftsReport/$', nomodelview.calcAttShiftsReport),   #新班次明细表
    url(r'^att/hasRoles/$', nomodelview.hasRoles),
    url(r'^att/getRoles/$', nomodelview.getRoles),
    #(r'^att/getDepts/$', 'nomodelview.getDepts'),
    #(r'^att/getUsers/$', 'nomodelview.getUsers'),
    #(r'^att/deleteDeptorUser/$', 'nomodelview.deleteDeptorUser'),
    url(r'^att/saveFields/$', nomodelview.saveFields),
    url(r'^att/checkUsrName/$', nomodelview.checkUsrName),    #检查用户名是否可用
    url(r'^att/resetpassword/$', nomodelview.forgotpassword),    #检查用户名和email是否可用
    url(r'^att/registerFinger/$', nomodelview.registerFinger),
    url(r'^att/NoFingerCount/$', nomodelview.NoFingerCount),
    url(r'^att/saveFingerprint/$', nomodelview.saveFingerprint),
    url(r'^att/savePhoto/$', nomodelview.savePhoto), #上传人员照片
    url(r'^att/saveSSNPhoto/$', nomodelview.saveSSNPhoto),
    url(r'^att/USER_SEARCH_SHIFTS/$',shiftsview.index),
    url(r'^att/reCalc/$', nomodelview.reCaluate),
    url(r'^att/reCalcAction/$', nomodelview.reCaluateAction),
    url(r'^att/FetchSchPlan/$', schedule.FetchSchPlan),
    url(r'^att/getData/$', nomodelview.getData),
    url(r'^att/getDeptData/$', departments.getData),
    url(r'^att/addTemparyShifts/$', schedule.addTemparyShifts),
    url(r'^reports/$',reportsview.index),
    url(r'^report/(?P<ReportName>[^/]*)/$', reportsview.reportIndex),
    url(r'^att/ihrreports/$',reports.ihr_index),
    url(r'^att/reversereports/$',reports.reverse_index),
    url(r'^att/originalreports/$',originalreports.index),    #Laird定制考勤原始表--渲染
    url(r'^att/calcAllReport/$', nomodelview.calcPriReport),         #Laird定制考勤原始表---统计
    #(r'^att/showOriginalReport/$', 'nomodelview.showOriginalReport'),         #Laird定制考勤原始表---显示
    #(r'^att/affairsReports/$','affairsReports.index'),      #人事报表【人员花名册、未采集指纹人员、部门统计人数】
    #(r'^att/exportAffairsReports/$','reports.exportaffairsReports'),      #人事报表【人员花名册、未采集指纹人员、部门统计人数】
    #(r'^att/calcDeptEmp/$','affairsReports.calcDeptEmp'),  #统计部门人数
    url(r'^att/exportReport/$',reports.exportReport),
    #(r'^att/print/(?P<tableName>[^/]*)/$','print.printIndex'),
    url(r'^att/init_database/$',nomodelview.init_database),
    #url(r'^att/saveHome/$',nomodelview.save_Home),
     url(r'^att/original_records/$', nomodelview.searchRecords),              #查询记录横向显示
    url(r'^att/daysplanner/$', nomodelview.days_planner),
    url(r'^att/newplannertype/$', nomodelview.newplannertype),
    url(r'^att/delplannertype/$', nomodelview.delplannertype),
    url(r'^att/colplannertype/$', nomodelview.colplannertype),
    url(r'^att/selplannertype/$', nomodelview.selplannertype),
    url(r'^att/addplanner/$', nomodelview.addplanner),
    url(r'^att/delplanner/$', nomodelview.delplanner),
    url(r'^att/changeplanner/$', nomodelview.changeplanner),
    url(r'^att/selplanner/$', nomodelview.selplanner),
    url(r'^att/selplannerbyid/$', nomodelview.selplannerbyid),
    url(r'^att/moveplannerbyid/$', nomodelview.moveplannerbyid),
    url(r'^att/resizeplannerbyid/$', nomodelview.resizeplannerbyid),
    url(r'^att/saveannualdays/$', nomodelview.saveannualdays),
    url(r'^att/getannualsettings/$', nomodelview.getannualsettings),
    url(r'^att/submitAnnSet/$', nomodelview.submitAnnSet),
    url(r'^att/WebcamAction_picture/$',nomodelview.picturesave),
    url(r'^att/setprocess/$', process.setprocess),
    url(r'^att/setoptionAttParam/$', nomodelview.setoptionAttParam),
    url(r'^att/getoptionAttParam/$', nomodelview.getoptionAttParam),
    url(r'^att/getColModel/$', getColModel.getColModel),             #获取colModel
    url(r'^att/save_deptschedule_set/$', departments.save_deptschedule_set),
    url(r'^att/get_deptschedule_set/$', departments.get_deptschedule_set),
    
    url(r'^att/saveprocessfor/$',process.saveprocessfor),
    url(r'^att/saveprocessl/$',process.saveprocessl),
    url(r'^att/delprocessl/$',process.delprocessl),
    url(r'^att/getprocleave/$',process.getprocleave),
    url(r'^att/getuserRoles/$',process.getuserRoles),
    url(r'^att/getdepartment/$',process.getdepartment),
    url(r'^att/getprocessfor/$',process.getprocessfor),
    url(r'^att/showApprovals/$',process.showApprovals),
    url(r'^att/saveEmpComverify/$',dataproc.saveEmpComverify),
   # url(r'^att/savefingerdata/$',dataproc.savefingerdata),

    
    
#其他功能
    url(r'^homepage/showHomepage/$', homeview.showMsgPage),
    url(r'^homepage/getAttention/$', home_attention.getdata),
    url(r'^homepage/showAnnouncement/(?P<DataKey>[^/]*)/$', homeview.getAnnouncement,name='getAnnouncement'),
    url(r'^filemng/(?P<pageName>.*)$', filemngview.index),
    url(r'^filemng1/(?P<pageName>.*)$', filemngview.getDeviceUser),
    #url(r'^getmsg/(?P<device>.*)$', genmsgview.get),			#查询公共信息(天气预报)
    #url(r'^tasks/genmsg/(?P<device>.*)$', genmsgview.index),		#根据设备生成定制信息(天气预报)命令
#    url(r'^tasks/del_emp$', taskview.FileDelEmp),
#    url(r'^tasks/disp_emp$', taskview.FileChgEmp),
#    url(r'^tasks/name_emp$', taskview.FileChgEmp),
#    url(r'^tasks/disp_emp_log$', taskview.disp_emp_log),
#    url(r'^tasks/del_emp_log$', taskview.del_emp_log),
#    url(r'^tasks/app_emp$', taskview.app_emp),
    url(r'^tasks/import_emp/$', taskview.importEmp),
    url(r'^tasks/import_trans/$', taskview.importTrans),
    url(r'^tasks/import_dept/$', taskview.importDept),
    url(r'^tasks/import_fptemp/$', taskview.importFptemp),
    url(r'^tasks/import_biodata/$', taskview.importBiodata),
    url(r'^tasks/importschclasstmpShift/$', taskview.importschclasstmpShift),
    url(r'^tasks/import_Speday/$', taskview.importSpeday),
    
    url(r'^tasks/upgrade$', taskview.upgrade),
    url(r'^tasks/restart$', taskview.restartDev),
    url(r'^tasks/autorestart$', taskview.autoRestartDev),
    url(r'^tasks/wmsync$', importwm.WMDataSync),
    url(r'^tasks/importclock/$', taskview.importIclock),
    url(r'^data_exp/(?P<pageName>.*)$', expview.index),
    #url(r'^user_list/$', user_list.index),
    url(r'^pics/(?P<path>.*)/$', browsepic.index),
    #url(r'^upload/(?P<path>.*)$', datamisc.uploadFile),
    url(r'^tasks/sap_ftp/$',importwm.index),

#消费
    url(r'^pos_setoptions$', devview.set_pos_options),#消费机修改参数&
    url(r'^pos_getreback$', devview.pos_reback),#消费回滚
    url(r'^pos_getdata$', devview.pos_getdata),#获取消费基本信息
    url(r'^pos_getrequest$', devview.pos_getreq),#消费业务



    
]

dict_urls={
    "ic_pos_devview.cdata":url(r'^cpos$',(ic_pos_devview.cdata)),
    "ic_pos_devview.pos_getreq":url(r'^posrequest$',(ic_pos_devview.pos_getreq)),
    "ic_pos_devview.pos_devpost":url(r'^posdevicecmd$',(ic_pos_devview.pos_devpost)),
}

if 'ipos' in settings.SALE_MODULE:
    for k,v in dict_urls.items():
        #if "mysite.pos" in settings.INSTALLED_APPS:
        urlpatterns.append(v)
