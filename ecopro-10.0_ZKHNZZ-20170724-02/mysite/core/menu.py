#coding=utf-8
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.models import *
from mysite.base.models import *

from django.db.models.fields import AutoField, FieldDoesNotExist
from django.contrib.auth.models import Permission, Group
from mysite.iclock.datautils import GetModel, hasPerm
from mysite.iclock.templatetags.iclock_tags import HasPerm
import datetime
from django.conf import settings
from mysite.core.mimi import *

"""主菜单格式：
    <LI><a class=nav_on href='#' onclick=menuclick(); ><SPAN>首页</SPAN></A></LI>
    <LI class="menu_line2"></LI>
    <li><a   class="nav_off" href ='#submenu2'><span>设备管理</span></a></li>
    <LI class="menu_line2"></LI>


二级菜单格式：
    <div id=submenu2 class='submenu'>
                    <UL>
                      <LI><a class="a_icon" onclick=hmenuclick(this);><span>机构维护</span></A></LI>
                      <LI class=menu_line2></LI>
                      <LI><A class="a_icon"><SPAN>人员维护</SPAN></A></LI>
                      <LI class=menu_line2></LI>
                      <LI><A class="a_icon"><SPAN>指纹及面部维护</SPAN></A></LI>
                    </UL>
    </div>

"""


class MenuList(object):
    """系统菜单,其他日志的permissions都采用iclock.browse_devlog"""
    def __init__(self,request,mod_name):
        self.request=request
        self.mod_name=mod_name
        #SetParamValue('IsUsingModule_%s'%request.user.id,mod_name)

        self.standard_modules=[
                        {'id':'adms','caption':_(u'数据版')},
                        {'id':'att','caption':_(u'考勤')},
                        {'id':'acc','caption':_(u'门禁')},
                        {'id':'ipos','caption':_(u'消费')},
                        {'id':'visitors','caption':_(u'访客')},
                        {'id':'meeting','caption':_(u'会议')},
                        #{'id':'patrol','caption':_(u'巡更')}
                        {'id':'system','caption':_(u'系统')},
]
        self.menus=[
        {'caption':{'title':_(u"常用功能"),'event':"",'permissions':'','_mod':'adms;att;acc;meeting;ipos;visitors;patrol','id':'id_menu_shortcut','img':''},
                        'submenu':[
                                        {'title':_(u"设备管理"),'event':'/iclock/data/iclock/','permissions':'iclock.browse_iclock','_mod':'adms;att;acc;meeting;ipos;patrol;','img':'media/images/button/connect_to_network.png'},
                                        {'title':_(u'卡管理'),'event':'/ipos/isys/IssueCard/','permissions':'ipos.browse_issuecard','_mod':'ipos','img':''},
                                        {'title':_(u'人员'),'event':'/iclock/data/employee/','permissions':'iclock.browse_employee','_mod':'adms;att;acc;meeting;visitors;patrol','img':''},
                                        {'title':_(u'服务器下发命令'),'event':'/iclock/data/devcmds/','permissions':'iclock.browse_devcmds','_mod':'adms;att;acc;meeting;ipos;patrol','img':'media/images/button/arrow_down_48.png'},
                                        # {'title':_('Shifts for Employee'),'event':'/iclock/data/USER_OF_RUN/','permissions':'iclock.browse_user_of_run','_mod':'att','img':''},
                                        # {'title':_("Employee's Leave"),'event':'/iclock/data/USER_SPEDAY/','permissions':'iclock.browse_user_speday','_mod':'att','img':''},
                                        {'title':_("transaction"),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transactions','_mod':'adms;att','img':''},
                                        {'title':_(u'实时监控'),'event':'/iclock/_checktranslog_/','permissions':'iclock.monitor_oplog','_mod':'adms;att','img':''},
                                        {'title':_(u'实时监控'),'event':'/acc/_checktranslog_/','permissions':'acc.monitor_oplog','_mod':'acc','img':''},
                                        {'title':_(u"门禁记录"),'event':'/acc/data/records/','permissions':'acc.acc_records','_mod':'acc','img':''},
                                        {'title':_('Reports'),'event':'/iclock/reports/','permissions':'iclock.IclockDept_reports','_mod':'att','img':''},
                                        {'title':_(u'门禁权限'),'event':'/acc/isys/acc/','permissions':'acc.browse_level','_mod':'acc','img':''},
                                        #{'title':_(u'电子地图监控'),'event':'/iclock/iacc/Map_Monitor/','permissions':'iclock.Map_Monitor','_mod':'acc','img':''},
                                        {'title':_(u"会议室"),'event':'/meeting/data/MeetLocation/','permissions':'meeting.browse_meetlocation','_mod':'meeting','img':''},
                                        {'title':_(u"会议安排"),'event':'/meeting/data/Meet/','permissions':'meeting.browse_meet','_mod':'meeting','img':''},
                                        {'title':_(u'参会记录'),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transactions','_mod':'meeting','img':''},
                                        # {'title':_(u'会议报表'),'event':'/iclock/reports/','permissions':'meeting.meeting_reports','_mod':'meeting','img':''},
                                        {'title':_(u"卡现金收支明细"),'event':'/ipos/data/CardCashSZ/','permissions':'ipos.iclockdininghall_cardcashsz','_mod':'ipos;'},
                                        {'title':_(u"消费明细"),'event':'/ipos/data/ICConsumerList/','permissions':'ipos.iclockdininghall_icconsumerlist','_mod':'ipos;IC_POS','img':''},
                                        {'title':_(u'Reports'),'event':'/ipos/reports/','permissions':'ipos.iclockdininghall_reports','_mod':'ipos','img':''},
                                        {'title':_(u"访客登记"),'event':'/visitors/data/visitionlogs/','permissions':'visitors.browse_visitionlogs','_mod':'visitors','img':''},
                                        {'title':_(u'访客记录查询'),'event':'/visitors/vis/visitionlogs_his/','permissions':'visitors.browse_visitionlogs','_mod':'visitors','img':''},
                                        {'title':_(u"补签记录"),'event':'/iclock/data/checkexact/','permissions':'iclock.browse_checkexact','_mod':'adms','img':''},

                                   ]
                        },

        {'caption':{'title':_(u"基本信息"),'event':'','permissions':'','_mod':'adms;att;acc;meeting;ipos;visitors;patrol','id':'id_maintenance_menu','img':''},
                                        'submenu':[{'title':_(u'单位'),'event':'/iclock/data/department/','permissions':'iclock.browse_department','_mod':'adms;att;acc;meeting;ipos;visitors;patrol','img':''},
                                        {'title':_(u'人员'),'event':'/iclock/data/employee/','permissions':'iclock.browse_employee','_mod':'ipos;','img':''},
                                        #{'title':_(u"设备"),'event':'/iclock/data/iclock/','permissions':'iclock.browse_iclock','_mod':'adms;att;acc;meeting;ipos;patrol;','img':'media/images/button/connect_to_network.png'},
#                                    {'title':_(u'面部维护'),'event':'/iclock/data/facetemp/','permissions':'iclock.browse_facetemp','_mod':'adms;att;acc;meeting;patrol','img':''},
                                        {'title':_(u"餐厅"),'event':'/ipos/data/dininghall/','permissions':'ipos.browse_dininghall','_mod':'ipos;','img':''},
                                        {'title':_(u'职务'),'event':'/iclock/data/userRoles/','permissions':'iclock.browse_userroles','_mod':'adms;att;acc;meeting;ipos;visitors;patrol','img':''},
                                        {'title':_(u'区域'),'event':'/acc/data/zone/','permissions':'acc.browse_zone','_mod':'acc','img':''},
                                        {'title':_(u'公告'),'event':'/iclock/data/Announcement/','permissions':'iclock.browse_announcement','_mod':'adms;att;acc;meeting;visitors;patrol','img':''},
                                        {'title':_(u'合同'),'event':'/iclock/data/USER_CONTRACT/','permissions':'iclock.browse_user_contract','_mod':'nouse','img':''},
                                        {'title':_("Holidays"),'event':'/iclock/data/holidays/','permissions':'iclock.browse_holidays','_mod':'acc'},
                                        {'title':_(u'特征模板'),'event':'/iclock/data/BioData/','permissions':'iclock.browse_biodata','_mod':'adms;att;acc;meeting;patrol','img':''},
                                        {'title':_(u'人员离职'),'event':'/iclock/data/empleavelog/','permissions':'iclock.empLeave_employee','_mod':'adms;att;','img':''},
                                        {'title':_(u'人员借调'),'event':'/iclock/data/employee_borrow/','permissions':'iclock.browse_employee_borrow','_mod':'adms;att;','img':''},
                                        ]},
        {'caption':{'title':_("Staff Schedule"),'event':'','permissions':'','_mod':'att','id':'id_schedule_menu','img':''},
        'submenu':[{'title':_("Time-tables"),'event':'/iclock/data/SchClass/','permissions':'iclock.browse_schclass','_mod':'att','img':''},
                                        {'title':_('shift'),'event':'/iclock/data/NUM_RUN/','permissions':'iclock.browse_num_run','_mod':'att','img':''},
                                        {'title':_('Shifts for Employee'),'event':'/iclock/data/USER_OF_RUN/','permissions':'iclock.browse_user_of_run','_mod':'att','img':''},
                                        #{'title':_(u'家长信息维护'),'event':'/base/data/employee/','permissions':'iclock.browse_employee','_mod':'','img':'media/images/button/user_info_48.png'},
                                        {'title':_(u'人员调休'),'event':'/iclock/data/days_off/','permissions':'iclock.browse_days_off','_mod':'att','img':''},
                                        {'title':_(u'排班详情'),'event':'/iclock/att/USER_SEARCH_SHIFTS/','permissions':'iclock.Employee_shift_details','_mod':'att','img':''}
                                        #{'title':_(u'指纹及面部维护'),'event':'/iclock/att/fpfacemanage/','permissions':'iclock.browse_fptemp','_mod':'fptemp','img':'media/images/button/photo_48.png'}
                                        ]},
        {'caption':{'title':_(u"巡更基本资料"),'event':'','permissions':'','_mod':'patrol','id':'id_basic_patrol_menu','img':''},
        'submenu':[{'title':_(u"巡更点信息维护"),'event':'/patrol/data/xlpoint/','permissions':'patrol.browse_xlpoint','_mod':'patrol','img':''},
                                        {'title':_(u'巡更路线信息维护'),'event':'/patrol/data/xlline/','permissions':'patrol.browse_xlline','_mod':'patrol','img':''}
                                        ]},
        {'caption':{'title':_(u"巡更排班"),'event':'','permissions':'','_mod':'patrol','id':'id_schedule_patrol_menu','img':''},
        'submenu':[{'title':_(u"巡更时段"),'event':'/patrol/data/lineshift/','permissions':'patrol.browse_lineshift','_mod':'patrol','img':''},
                                        {'title':_(u'巡更班次'),'event':'/patrol/data/NUM_RUN/','permissions':'patrol.browse_num_run','_mod':'patrol','img':''},
                                        {'title':_(u'巡更排班'),'event':'/patrol/data/USER_OF_RUN/','permissions':'patrol.browse_user_of_run','_mod':'patrol','img':''},
                                        {'title':_(u'排班详情'),'event':'/patrol/att/USER_SEARCH_SHIFTS/','permissions':'patrol.Employee_shift_details','_mod':'patrol','img':''}
                                        ]},
        {'caption':{'title':_("Attendance"),'event':'','permissions':'','_mod':'att;','id':'id_attendance_menu','img':''},
        'submenu':[{'title':_(u"多级审批设置"),'event':'/iclock/att/setprocess/','permissions':'iclock.setprocess','_mod':'att;mul_approval','img':''},
                                        {'title':_("Employee's Leave"),'event':'/iclock/data/USER_SPEDAY/','permissions':'iclock.browse_user_speday','_mod':'att','img':''},
                                        {'title':_(u"补签记录"),'event':'/iclock/data/checkexact/','permissions':'iclock.browse_checkexact','_mod':'att;','img':''},
                                        {'title':_('User OverTime'),'event':'/iclock/data/User_OverTime/','permissions':'iclock.browse_user_overtime','_mod':'att','img':''},
                                        #{'title':_('Posting'),'event':'/iclock/data/accounts/','permissions':'iclock.browse_accounts','_mod':'att'},
                                        {'title':_('Attendance Rules'),'event':'/base/data/AttParam/','permissions':'base.browse_attparam','_mod':'att','img':''},
                                        {'title':_(u'统计报表'),'event':'/iclock/att/reCalc/','permissions':'iclock.IclockDept_calcreports','_mod':'att','img':''},
                                        ]},

        {'caption':{'title':_(u"假类管理"),'event':'','permissions':'','_mod':'att;meeting','id':'id_leave_menu','img':''},
        'submenu':[
                                        {'title':_('Leave Class'),'event':'/iclock/data/LeaveClass/','permissions':'iclock.browse_leaveclass','_mod':'att;meeting'},
                                        {'title':_("Holidays"),'event':'/iclock/data/holidays/','permissions':'iclock.browse_holidays','_mod':'att;acc;meeting'},
                                        {'title':_("Employee's Leave"),'event':'/iclock/data/USER_SPEDAY/','permissions':'iclock.browse_user_speday','_mod':'meeting','img':''},
                                        {'title':_(u"带薪年假规则"),'event':'/iclock/data/annual_settings/','permissions':'iclock.browse_annual_settings','_mod':'att;'},
                                        {'title':_(u'人员带薪年假标准'),'event':'/iclock/data/annual_leave/','permissions':'iclock.browse_annual_settings','_mod':'att;'},
                                        {'title':_(u'人员带薪年假详情'),'event':'/iclock/att/report_annual/','permissions':'iclock.browse_annual_settings','_mod':'att;'},
                                        {'title':_(u"补签记录"),'event':'/iclock/data/checkexact/','permissions':'iclock.browse_checkexact','_mod':'meeting;','img':''},
                                        ]},



        {'caption':{'title':_(u"会议处理"),'event':'','permissions':'','_mod':'meeting','id':'id_meeting_menu','img':''},
        'submenu':[{'title':_(u"会议室"),'event':'/meeting/data/MeetLocation/','permissions':'meeting.browse_meetlocation','_mod':'meeting','img':''},
                                        {'title':_(u"参会人员模板"),'event':'/meeting/data/participants_tpl/','permissions':'meeting.browse_participants_tpl','_mod':'meeting','img':''},
                                        {'title':_(u"会议预约"),'event':'/meeting/data/Meet_order/','permissions':'meeting.browse_meet_order','_mod':'meeting','img':''},
                                        {'title':_(u"会议安排"),'event':'/meeting/data/Meet/','permissions':'meeting.browse_meet','_mod':'meeting','img':''},
                                        {'title':_(u'会议通知'),'event':'/meeting/data/MeetMessage/','permissions':'meeting.browse_meetmessage','_mod':'meeting','img':''},
                                        {'title':_(u'会议纪要'),'event':'/meeting/data/Minute/','permissions':'meeting.browse_minute','_mod':'meeting'},
                                        ]},


        {'caption':{'title':_(u"访客处理"),'event':'','permissions':'','_mod':'visitors','id':'id_visitors_menu','img':''},
                        'submenu':[{'title':_(u"访客预约"),'event':'/visitors/data/reservation/','permissions':'visitors.browse_reservation','_mod':'visitors','img':''},
                                        {'title':_(u"访客登记"),'event':'/visitors/data/visitionlogs/','permissions':'visitors.browse_visitionlogs','_mod':'visitors','img':''},
                                        {'title':_(u"来访事由"),'event':'/visitors/data/reason/','permissions':'visitors.browse_reason','_mod':'visitors','img':''},
                                        ]},

#{'caption':{'title':_(u"消费基本资料"),'event':'','permissions':'','_mod':'ipos','id':'id_meeting_menu','img':''},
#           'submenu':[{'title':_(u"分段定值"),'event':'/meeting/data/MeetLocation/','permissions':'meeting.browse_meetlocation','_mod':'ipos','img':''},
#                       {'title':_(u"消费时间段设置"),'event':'/meeting/data/participants_tpl/','permissions':'meeting.browse_participants_tpl','_mod':'ipos','img':''},
#                       {'title':_(u"餐厅资料"),'event':'/meeting/data/Meet/','permissions':'meeting.browse_meet','_mod':'ipos','img':''},
#                       {'title':_(u"餐别资料"),'event':'/meeting/data/Meet/','permissions':'meeting.browse_meet','_mod':'ipos','img':''},
#                       {'title':_(u'商品资料'),'event':'/meeting/data/MeetMessage/','permissions':'meeting.browse_meetmessage','_mod':'ipos','img':''},
#                       {'title':_(u'键值资料'),'event':'/meeting/data/MeetMessage/','permissions':'meeting.browse_meetmessage','_mod':'ipos','img':''},
#                       ]},


{'caption':{'title':_(u"消费基本资料"),'event':'','permissions':'','_mod':'ipos','id':'id_attendance_menu','img':''},
                                        'submenu':[{'title':_(u"分段定值"),'event':'/ipos/data/splittime/','permissions':'ipos.browse_splittime','_mod':'ipos','img':''},
                                        {'title':_(u"消费时间段设置"),'event':'/ipos/data/batchtime/','permissions':'ipos.browse_batchtime','_mod':'ipos','img':''},
                                        #{'title':_(u"餐厅资料"),'event':'/ipos/data/dininghall/','permissions':'ipos.browse_dininghall','_mod':'ipos','img':''},
                                        {'title':_(u'餐别资料'),'event':'/ipos/data/meal/','permissions':'ipos.browse_meal','_mod':'ipos','img':''},
                                        {'title':_(u'商品资料'),'event':'/ipos/data/merchandise/','permissions':'ipos.browse_merchandise','_mod':'ipos','img':''},
                                        {'title':_(u'键值资料'),'event':'/ipos/data/keyvalue/','permissions':'ipos.browse_keyvalue','_mod':'ipos','img':''},
                                        {'title':_(u'卡类资料'),'event':'/ipos/data/ICcard/','permissions':'ipos.browse_iccard','_mod':'ipos','img':''}
                                        ]},

#{'caption':{'title':_(u"卡管理"),'event':'/ipos/isys/IssueCard/','permissions':'','_mod':'ipos','id':'id_card_menu','img':''},
#           'submenu':[]},


{'caption':{'title':_(u'门禁管理'),'event':'','permissions':'','_mod':'acc','id':'id_access_menu','img':''},
                                        'submenu':[{'title':_(u"门禁时间段"),'event':'/acc/data/timezones/','permissions':'acc.browse_timezones','_mod':'acc','img':''},
                                        {'title':_(u'门禁权限'),'event':'/acc/isys/acc/','permissions':'acc.browse_level','_mod':'acc','img':''},
                                        {'title':_(u'门禁规则'),'event':'/acc/isys/accessRules/','permissions':'','_mod':'acc','img':''},
                                        #{'title':_(u'门禁一体机'),'event':'/acc/isys/iaccess/','permissions':'','_mod':'acc','img':''},
                                        #{'title':_(u'InBio控制器'),'event':'/acc/isys/inbio/','permissions':'','_mod':'acc','img':''},

                                        #{'title':_(u'门禁规则'),'event':'/iclock/data/accessRules/','permissions':'','_mod':'acc','img':''},
                                        #{'title':_(u'门禁参数'),'event':'/iclock/data/accessOptions/','permissions':'','_mod':'acc','img':''},
                                        #{'title':_(u'地图管理'),'event':'/iclock/iacc/MapManageIndex/','permissions':'iclock.browse_mapmanage','_mod':'iaccess','img':''},
                                        #{'title':_(u'电子地图监控'),'event':'/iclock/iacc/Map_Monitor/','permissions':'iclock.Map_Monitor','_mod':'iaccess','img':''},
                                        ]},
                                        #,{'title':_(u'实时记录监控'),'event':'/iclock/iacc/RealMonitorIaccess/','permissions':'iclock.Real_Monitor_Iaccess','_mod':'acc'}
#{'caption':{'title':_(u"门禁监控"),'event':'','permissions':'','_mod':'acc','id':'id_accessmonitor_menu','img':''},
#            'submenu':[{'title':_(u"设备监控"),'event':'/iclock/data/DeviceMonitor/','permissions':'','_mod':'acc','img':''},
#                        {'title':_(u'门禁实时监控'),'event':'/iclock/data/AccessMonitor/','permissions':'','_mod':'acc','img':''},
#                        {'title':_(u'报警监控'),'event':'/iclock/data/AlarmMonitor/','permissions':'','_mod':'acc','img':''},
#                        {'title':_(u'地图管理'),'event':'/iclock/iacc/MapManageIndex/','permissions':'iclock.browse_mapmanage','_mod':'acc','img':''},
#                        {'title':_(u'电子地图监控'),'event':'/iclock/iacc/Map_Monitor/','permissions':'iclock.Map_Monitor','_mod':'acc','img':''},
#                        ]},


{'caption':{'title':_("Search/Print"),'event':'','permissions':'','_mod':'acc;meeting;ipos;visitors;','id':'id_search_menu','img':''},

                        'submenu':[
                                        {'title':_("transaction"),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transactions','_mod':'adms;att','img':''},
                                        {'title':_(u"门禁记录"),'event':'/acc/data/records/','permissions':'acc.acc_records','_mod':'acc','img':''},
                                        {'title':_(u'实时监控'),'event':'/iclock/_checktranslog_/','permissions':'iclock.monitor_oplog','_mod':'adms;att','img':''},
                                        {'title':_(u'电子地图'),'event':'/acc/getRTlog/','permissions':'iclock.browse_mapmanage','_mod':'acc','img':''},
                                        {'title':_(u'实时监控'),'event':'/acc/_checktranslog_/','permissions':'acc.monitor_oplog','_mod':'acc','img':''},
                                        {'title':_(u'出入监控'),'event':'/acc/_checkinoutlog_/','permissions':'acc.monitor_oplog','_mod':'acc','img':''},
                                        {'title':_('Reports'),'event':'/iclock/reports/','permissions':'iclock.IclockDept_reports','_mod':'adms;att','img':''},

                                        {'title':_(u"卡现金收支明细"),'event':'/ipos/data/CardCashSZ/','permissions':'ipos.iclockdininghall_cardcashsz','_mod':'ipos;'},
                                        {'title':_(u"消费明细"),'event':'/ipos/data/ICConsumerList/','permissions':'ipos.iclockdininghall_icconsumerlist','_mod':'ipos;IC_POS','img':''},
                                        {'title':_(u'Reports'),'event':'/ipos/reports/','permissions':'ipos.iclockdininghall_reports','_mod':'ipos','img':''},
                                        #{'title':_(u"人员日期提醒"),'event':'/iclock/att/ihrreports/','permissions':'iclock.browse_USER_CONTRACT','_mod':'att','img':''},
                                        #{'title':_(u"人员异常查询"),'event':'/iclock/att/reversereports/','permissions':'iclock.browse_itemdefine','_mod':'adms;att','img':''},
                                        #{'title':_(u'设备与记录报表'),'event':'/iclock/iacc/iaccessDevReports/','permissions':'iclock.browse_iaccdevitemdefine','_mod':'acc','img':''},
                                        #{'title':_(u'人员与记录报表'),'event':'/iclock/iacc/iaccessEmpReports/','permissions':'iclock.browse_iaccempitemdefine','_mod':'acc','img':''},
                                        {'title':_(u'会议实时显示'),'event':'/meeting/_checktranslog_/','permissions':'meeting.meeting_monitor','_mod':'meeting','img':''},
                                        {'title':_(u'参会记录'),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transactions','_mod':'meeting','img':''},
                                        #{'title':_(u'会议数据管理'),'event':'','permissions':'iclock.reCalcaluteReport_itemdefine','_mod':'meeting','img':''},
                                        {'title':_(u'会议报表'),'event':'/iclock/reports/','permissions':'meeting.meeting_reports','_mod':'meeting','img':''},
                                        {'title':_('Reports'),'event':'/acc/reports/','permissions':'acc.acc_reports','_mod':'acc','img':''},
                                        {'title':_(u'访客记录查询'),'event':'/visitors/vis/visitionlogs_his/','permissions':'visitors.browse_visitionlogs','_mod':'visitors','img':''},

                                        {'title':_(u"巡更记录"),'event':'/patrol/data/records/','permissions':'patrol.records','_mod':'patrol','img':''},
                                        {'title':_(u'实时监控'),'event':'/patrol/_checktranslog_/','permissions':'patrol.monitor_oplog','_mod':'patrol','img':''},
                                        {'title':_(u'巡更监控'),'event':'/patrol/_checktranslog_/','permissions':'patrol.monitor_oplog','_mod':'patrol','img':''},
                                        {'title':_(u'报表'),'event':'/patrol/reports/','permissions':'patrol.patrol_reports','_mod':'patrol','img':''},
                                        {'title':_(u'短信息'),'event':'/sms/isys/sms/','permissions':'','_mod':'sms','img':''},



                                        ]},
{'caption':{'title':_(u"系统配置"),'event':'','permissions':'','_mod':'system','id':'id_group_menu','img':''},
                'submenu':[{'title':_(u"管理组"),'event':'/iclock/data/group/','permissions':'auth.browse_group','_mod':'system','img':''},
                                        {'title':_(u"用户"),'event':'/iclock/data/user/','permissions':'accounts.browse_myuser','_mod':'system','img':''},
                                        {'title':_(u"系统选项"),'event':'/base/isys/options/','permissions':'','_mod':'','img':'','id':'options'}
                                        ]},
{'caption':{'title':_("System"),'event':'','permissions':'','_mod':'system','id':'id_log_menu','img':''},
                'submenu':[{'title':_(u'服务器下发命令'),'event':'/iclock/data/devcmds/','permissions':'iclock.browse_devcmds','_mod':'system-adms;system-att;system-acc;system-meeting;system-ipos;patrol','img':''},
                                        {'title':_(u'设备上传数据'),'event':'/iclock/data/devlog/','permissions':'iclock.browse_devlog','_mod':'system-adms;system-att;system-acc;system-meeting;system-ipos;patrol','img':''},
                                        #{'title':_(u'门禁设备操作'),'event':'/iclock/data/iaccessoplog/','permissions':'iclock.browse_devlog','_mod':'system-acc','img':''},
                                        {'title':_(u'设备操作'),'event':'/iclock/data/oplog/','permissions':'iclock.browse_devlog','_mod':'system-adms;system-att;system-acc;system-meeting;system-ipos;patrol','img':''},
                                        {'title':_(u'管理员操作'),'event':'/iclock/data/adminLog/','permissions':'iclock.browse_adminlog','_mod':'system-adms;system-att;system-acc;system-meeting;system-ipos;system-visitors;patrol','img':''},
                                        {'title':_(u'个人登录操作'),'event':'/iclock/data/employeeLog/','permissions':'iclock.browse_employeelog','_mod':'system-adms;system-att;system-acc;system-meeting;system-ipos;patrol','img':''},
                                        #{'title':_(u'记录数据校对'),'event':'/iclock/data/AttDataProofCmd/','permissions':'iclock.browse_devlog','_mod':'adms;att;iaccess','img':''}
                                        #{'title':GetModel('checkexact')._meta.verbose_name.capitalize(),'event':'/iclock/data/checkexact/','permissions':'iclock.browse_checkexact','_mod':'','img':''}
                                        ]},
]
    def enable_mod(self,mod_name):
        if mod_name=='':
            return True
        l_mod=mod_name.split(';')
        for m in l_mod:
            if m=='system' and self.mod_name=='system':return True
            if (m==self.mod_name) and (m in settings.ENABLED_MOD) and (m in settings.SALE_MODULE):
                return True
            if ('system-' in m) and (m[7:] in  settings.SALE_MODULE):
                return True
        return False
    def enable_permission(self,menu):
        if self.request.user.is_superuser:
            return True
        permission=menu['caption']['permissions']
        if not permission  or (self.request.user.has_perm(permission)):
            submenu=menu['submenu']
            if not submenu:return True
            for m1 in submenu:
                #print "=========",u'%s'%m1['title']
                permission=m1['permissions']
                #print "=====",permission,self.request.user.has_perm(permission)
                if permission  and (self.request.user.has_perm(permission)):
                    return True
                if not permission:
                    try:
                        id=m1['id']
                    except:
                        id=''
                    ret_html=createmenu(self.request,id)
                    if not ret_html or len(ret_html)<60:
                        return False
                    return True
        return False
#############################################################################################################
    def getMenuForSingleModule(self,mod_name):
        """当系统仅开启一个模块时，弥补模块位置内容太少的问题，将当前模块下的菜单标题作为模块菜单
                             <li><a  rel='acc'  ><span>常用功能</span></a></li>

        """
        self.mod_name=mod_name
        mlist=self.menus
        if not settings.SALE_MODULE:
            getISVALIDDONGLE(reload=1)

        html=''
        menuT=u"""
                        <li><a class='submenutitle' rel='%s'  ><span>%s</span></a></li>
        """



        for m in mlist:
            _mod=m['caption']['_mod']
            if not self.enable_mod(_mod):
                continue
            if not self.enable_permission(m):
                continue
            t=unicode(m['caption']['title'])
            ev=m['caption']['event']
            mid=m['caption']['id']
            html=html+menuT%(mid,t)
        return html
    def getMenuForModule(self,mod_name):
        s="""
                                        <div id=%s class='submenu' >
                                        <ul id="op_menu_" class="sub_op_menu" >
                                        %s
                                        </ul>
                                        </div>
                        """
        self.mod_name=mod_name
        mlist=self.menus
        if not settings.SALE_MODULE:
            getISVALIDDONGLE(reload=1)

        html=''
        menuT="""
                                        <li>
                                        <ul>
                                                %s
                                        </ul>
                                        </li>
                        """



        for m in mlist:
            _mod=m['caption']['_mod']
            if mod_name in _mod:
                if not self.enable_mod(_mod):
                    continue
                if not self.enable_permission(m):
                    continue
                t=unicode(m['caption']['title'])
                ev=m['caption']['event']
                #g=m['caption']['img']
                mid=m['caption']['id']
                hrf=''
                onclick=''
                clas='nav_off'
                if mid=='id_menu_home':
                    clas='nav_on'
                if  ev:
                    onclick="onclick=menuClick('%s',this,'%s')"%(ev,mid)

                else:
                    hrf=mid
                sub_menu=self.getsubMenu(m)
                ss=menuT%(sub_menu)
                html=html+s%(mid,ss)
            #html+="<li class='right'></li>"
            #print "getmenu====",html
        return html







#-----------------------------------------------------------------------------#

    def getMenu(self,mod_name):
        self.mod_name=mod_name
        mlist=self.menus
        if not settings.SALE_MODULE:
            getISVALIDDONGLE(reload=1)

        html=''
        #menuT="""<li><a class='%s' rel='#%s' %s ><span>%s</span></a></li><li class="menu_line2"></li>"""
        menuT="""
                                        <li><span>%s</span>
                                        <ul>
                                                %s
                                        </ul>
                                        </li>
                        """



        for m in mlist:
            _mod=m['caption']['_mod']
            if not self.enable_mod(_mod):
                continue
            if not self.enable_permission(m):
                continue
            t=unicode(m['caption']['title'])
            ev=m['caption']['event']
            #g=m['caption']['img']
            mid=m['caption']['id']
            hrf=''
            onclick=''
            clas='nav_off'
            if mid=='id_menu_home':
                clas='nav_on'
            if  ev:
                onclick="onclick=menuClick('%s',this,'%s')"%(ev,mid)

            else:
                hrf=mid
            sub_menu=self.getsubMenu(m)

            html=html+menuT%(t,sub_menu)
        #html+="<li class='right'></li>"
        #print "getmenu====",html
        return html

    def getsubMenu(self,submenu):
        mlist=submenu['submenu']
        #s="""<a class="abs a_icon" style="left:35px;top:%spx;width:110px;" onclick=menuClick('%s');><img src=%s />%s</a>"""
        #submenuL="""<li><a class="a_icon" %s><span>%s</span></a></li><li class=menu_line2></li>"""
        #submenuD="<div id='%s' class='ui-state-default submenu'><ul>%s</ul></div>"

        submenuL="""
                        <li id='%s' %s ><a href="javascript:void(0)" >%s</a></li>

        """


        d={}
        html=''
        settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
        for m1 in mlist:
            mod=m1['_mod']

            if 'IC_POS' in mod:
                if settings.CARDTYPE==1:continue
            elif 'ID_POS' in mod:
                if settings.CARDTYPE==2:continue
            if not self.enable_mod(mod):
                continue
            #if ('mul_approval' in mod):#多级审批流程设计
            #    if GetParamValue('opt_basic_approval','0')=='0':
            #   continue


            onclick=''
            permission=m1['permissions']
    #               print "=====",u'%s'%m1['title'],permission,self.request.user.has_perm(permission)
            if not permission or self.request.user.is_superuser or (self.request.user.has_perm(permission)):
                t=unicode(m1['title'])
                #g=m1['img']
                try:
                    id=m1['id']
                except:
                    id=''
                ret_html=createmenu(self.request,id)
                if ret_html and len(ret_html)<60:continue
                ev=m1['event']
                if ev:
                    t_ev=ev
                    if (t_ev[0]=="/"):
                        t_ev=ev[1:]
                    if t_ev[-1]=="/":
                        t_ev=t_ev[:-1]
                    tid="%s_%s"%(t_ev.split('/')[0],t_ev.split('/')[-1])


                    onclick='onclick=menuClick("%s",this);'%(ev)
                    if not settings.ACC_TRAN_SHOWBLUE and ev=='/acc/_checkinoutlog_/':
                        continue
                html=html+submenuL%(tid,onclick,t)
        return html
    def getmodulesMenu(self):
        u"""模块菜单
                            <li><a class=nav_on rel='att'  ><span>考勤</span></a></li>
                            <li><a  rel='acc'  ><span>门禁</span></a></li>
                             <li><a  rel='ipos'  ><span>消费</span></a></li>
                             <li><a  rel='visitors'  ><span>访客</span></a></li>
                            <li><a  rel='meeting'  ><span>会议</span></a></li>
                            <li><a  rel='system'  ><span>系统</span></a></li>

        """
        s=u"""
                        <li><a %s rel='%s'  ><span>%s</span></a></li>
        """
        html=''
        show_salemod=0
        sys_menu=''
        sale_menu=''
 
        onlyshow_salemod=GetParamValue('opt_basic_onlyshow_salemod', '0')
        if onlyshow_salemod=='1' and len(settings.SALE_MODULE)==1:
            show_salemod=1
        for m in self.standard_modules:
            id=m['id']
            t=u'%s'%m['caption']
            cls=''
            if not ((id in settings.ENABLED_MOD) and (id in settings.SALE_MODULE)):
                if id!='system':
                    if onlyshow_salemod=='0':
                        cls='class=disabled'
                    else:
                        continue
            elif id==self.mod_name:
                cls='class=nav_on'
            if id=='adms':#当有考勤，数据模块就没必要显示
                if 'att' in settings.SALE_MODULE:
                    continue

            if show_salemod!=1:
                html=html+s%(cls,id,t)
            else:
                if id=='system':
                    sys_menu=s%(cls,id,t)
                else:
                    sale_menu=s%(cls,id,t)
                
        if show_salemod==1:
            html=sale_menu+self.getMenuForSingleModule(settings.SALE_MODULE[0])+sys_menu


        return html


    def getAllMenus(self):
        s="""
                                        <div id=%s class='submenu' >
                                        <ul id="op_menu_" class="sub_op_menu" >
                                        %s
                                        </ul>
                                        </div>
                        """




        html=''
        for m in self.standard_modules:
            id=m['id']
            t=u'%s'%m['caption']
            cls='disabled'
            if id=='adms':#当有考勤或其他模块时，数据模块就没必要显示
                if not ((len(settings.SALE_MODULE)==1) and ('adms' in settings.SALE_MODULE)):
                    continue
            if not ((id in settings.ENABLED_MOD) and (id in settings.SALE_MODULE)):
                if id != 'system':
                    if GetParamValue('opt_basic_onlyshow_salemod','0')=='0':
                        cls='disabled1'
                    else:
                        continue
            elif id==self.mod_name:
                cls='modules_btn1 current1'
            else:
                cls='modules_btn1'
            module_menu=self.getMenu(id)

            html=html+s%(id,module_menu)
        if len(settings.SALE_MODULE)==1:
            onlyshow_salemod = GetParamValue('opt_basic_onlyshow_salemod', '0')
            if onlyshow_salemod=='1':
                html=html+self.getMenuForModule(settings.SALE_MODULE[0])


        return html
    def get_homeurl(self):
        u"""自定义首页"""
        d_homeurl={}

        kkk=GetParamValue('opt_users_start_page','1',self.request.user.id)

        if kkk=='1':

            for m in self.standard_modules:
                t=GetParamValue('opt_users_homeurl','',"%s-%d"%(m['id'],self.request.user.id))
                if t and type(t)==type('abc'):
                    tt=t.split('|||')
                    if len(tt)>2:
                        tab_page=tt[0]
                        caption=tt[1]
                        s_url=tt[2]
                        d_homeurl[m['id']]={'url':s_url,'id':tab_page,'caption':caption}
        return dumps1(d_homeurl)


#用于报表、选项的子菜单配置
def get_Menulist(menuName):
    if menuName=='report':#报表
        return [
        #{'caption':{'title':_(u"人员快捷报表"),'event':'','permissions':'','_mod':'adms;att','id':'id_person_report_menu'},'submenu':[{'title':_(u"人员异常表"),'event':'/iclock/report/ihrreversedetail/','permissions':'','_mod':'adms;att'}]},
        {'caption':{'title':_(u"明细类报表"),'event':'','permissions':'','_mod':'adms;att','id':'id_detail_menu'},'submenu':[{'title':u'%s'%_(u"原始记录表"),'event':'/iclock/report/original_records/','permissions':'','_mod':'adms;att'},{'title':_(u'补签记录表'),'event':'/iclock/report/checkexact/','permissions':'','_mod':'att'},{'title':_(u'人员请假详情'),'event':'/iclock/report/USER_SPEDAY/','permissions':'','_mod':'att'},{'title':_(u'年假标准详情'),'event':'/iclock/report/annual_leave/','permissions':'iclock.browse_annual_settings','_mod':'att'},{'title':_(u'人员年假报表'),'event':'/iclock/report/annualstatic/','permissions':'iclock.browse_annual_settings','_mod':'att'}]},
        #{'caption':{'title':_(u"统计结果类报表"),'event':'','permissions':'','_mod':'adms;att','id':'id_manager_menu'},'submenu':[{'title':_(u'人员班次详情'),'event':'/iclock/report/attshifts_daily/','permissions':'iclock.attDailyTotalReport_itemdefine','_mod':'att'},{'title':_(u'统计结果详情'),'event':'/iclock/report/attRecAbnormite/','permissions':'','_mod':'att'},{'title':_(u'人员出勤异常详情'),'event':'/iclock/reports/calculated_leaves/','permissions':'iclock.attDailyTotalReport_itemdefine','_mod':'att'},{'title':_(u"最早最晚汇总表"),'event':'/iclock/report/earlylatest_records/','permissions':'','_mod':'adms;att'},{'title':_(u'人员每日出勤统计表'),'event':'/iclock/reports/department_finger/?Systag=0','permissions':'','_mod':'att'},{'title':_(u'人员出勤汇总表'),'event':'/iclock/reports/employee_finger/?Systag=0','permissions':'','_mod':'att'},{'title':_(u'部门统计汇总表'),'event':'/iclock/reports/daily_report/?Systag=0','permissions':'','_mod':'att'},{'title':_(u'人员请假汇总表'),'event':'/iclock/report/calcLeaveReport/','permissions':'','_mod':'att'}]},
        {'caption':{'title':_(u"统计结果类报表"),'event':'','permissions':'','_mod':'adms;att','id':'id_manager_menu'},'submenu':[{'title':u'%s'%_(u'人员班次出勤详情'),'event':'/iclock/report/calcAttShiftsReport/','permissions':'','_mod':'att'},{'title':u'%s'%_(u'人员班次异常详情'),'event':'/iclock/report/calcAttExceptionReport/','permissions':'','_mod':'att'},{'title':_(u'人员出勤记录详情'),'event':'/iclock/report/attRecAbnormite/','permissions':'','_mod':'att'},{'title':_(u'人员出勤异常详情'),'event':'/iclock/report/AttException/','permissions':'','_mod':'att'},{'title':_(u'人员每日出勤详情'),'event':'/iclock/report/dailycalcReport/','permissions':'','_mod':'att'},{'title':_(u'人员出勤汇总表'),'event':'/iclock/report/calcReport/','permissions':'','_mod':'att'},{'title':_(u'部门统计汇总表'),'event':'/iclock/report/department_report/','permissions':'','_mod':'att'},{'title':_(u'人员请假汇总表'),'event':'/iclock/report/calcLeaveReport/','permissions':'','_mod':'att'},{'title':_(u'人员年度请假汇总表'),'event':'/iclock/report/calcLeaveYReport/','permissions':'','_mod':'att'},{'title':_(u'人员请假结转汇总表'),'event':'/iclock/report/jiezhuan/','permissions':'','_mod':'att'},{'title':_(u'汇总表'),'event':'/iclock/report/calcAllReport/','permissions':'','_mod':'att'},{'title':_(u'病假、事假和旷工情况统计表'),'event':'/iclock/report/exceptionReport/','permissions':'','_mod':'att'},{'title':_(u'扣发审批表'),'event':'/iclock/report/backReport/','permissions':'','_mod':'att'},{'title':_(u'异常汇总表'),'event':'/iclock/report/allexceptionReport/','permissions':'','_mod':'att'}]},
        #{'caption':{'title':_(u"排班报表"),'event':'','permissions':'','_mod':'att','id':'id_device_report_menu'},'submenu':[{'title':_(u"人员正常排班列表"),'event':'/iclock/report/USER_OF_RUN/','permissions':'','_mod':'att'},{'title':_(u'人员临时排班表'),'event':'/iclock/report/USER_TEMP_SCH/','permissions':'','_mod':'att'},{'title':_(u'人员综合排班表'),'event':'/iclock/report/searchComposite/','permissions':'','_mod':'att'},{'title':_(u'未排班人员表'),'event':'/iclock/report/USER_NO_SCH/','permissions':'','_mod':'att'}]},
        {'caption':{'title':_(u"采集信息报表"),'event':'','permissions':'','_mod':'adms;att;meeting;acc','id':'id_finger_menu'},'submenu':[{'title':u'%s'%_(u'人员信息采集追踪表'),'event':'/iclock/report/employee_finger/','permissions':'','_mod':'adms;att;acc;meeting'},{'title':_(u"人员信息采集汇总表"),'event':'/iclock/report/department_finger/','permissions':'','_mod':'adms;att;acc;meeting'}]},
        {'caption':{'title':_(u"设备类报表"),'event':'','permissions':'','_mod':'adms;att;acc','id':'id_device_report_menu'},'submenu':[{'title':u'%s'%_(u"每日开机统计表"),'event':'/iclock/report/daily_devices/','permissions':'','_mod':'adms;att;acc;meeting'},{'title':_(u'部门管理设备表'),'event':'/iclock/report/device_assignment/','permissions':'','_mod':'adms;att;acc;meeting'}]},
        #{'caption':{'title':_(u"设备报表"),'event':'','permissions':'','_mod':'','id':'id_device_report_menu'},'submenu':[{'title':_(u"日开机统计表"),'event':'/iclock/reports/daily_devices/','permissions':'iclock.dailydevices_itemdefine','_mod':''},{'title':_(u'职场打卡机配置表'),'event':'/iclock/reports/device_assignment/','permissions':'iclock.deviceassignment_itemdefine','_mod':'att'}]},
        #{'caption':{'title':_(u"Access Management"),'event':'','permissions':'','_mod':'adms;iaccess','id':'id_access_menu'},'submenu':[{'title':_("ACTimeZones"),'event':'/iclock/data/ACTimeZones/','permissions':'iclock.browse_actimezones','_mod':''},{'title':_('ACGroup'),'event':'/iclock/data/ACGroup/','permissions':'iclock.browse_acgroup','_mod':''},{'title':_('ACUnlockComb'),'event':'/iclock/data/ACUnlockComb/','permissions':'iclock.browse_acunlockcomb','_mod':''},{'title':_('ACCSetHoliday'),'event':'/iclock/data/ACCSetHoliday/','permissions':'iclock.browse_accsetholiday','_mod':''},{'title':_('UserACPrivilege'),'event':'/iclock/data/UserACPrivilege/','permissions':'iclock.browse_useracprivilege','_mod':''},{'title':_(u'电子地图监控'),'event':'/iclock/iacc/Map_Monitor/','permissions':'iclock.Map_Monitor','_mod':'iaccess'},{'title':_(u'设备与记录报表'),'event':'/iclock/iacc/iaccessDevReports/','permissions':'iclock.browse_iaccdevitemdefine','_mod':'iaccess'},{'title':_(u'人员与记录报表'),'event':'/iclock/iacc/iaccessEmpReports/','permissions':'iclock.browse_iaccempitemdefine','_mod':'iaccess'}]},#,{'title':_(u'实时记录监控'),'event':'/iclock/iacc/RealMonitorIaccess/','permissions':'iclock.Real_Monitor_Iaccess','_mod':'iaccess'}
        {'caption':{'title':_(u"会议类报表"),'event':'','permissions':'','_mod':'meeting','id':'id_meeting_report'},'submenu':[{'title':u'%s'%_(u'人员签到情况报表'),'event':'/meeting/report/meeting_sign_report/','permissions':'','_mod':'meeting'},{'title':_(u'人员未签到情况报表'),'event':'/meeting/report/meeting_not_sign_report/','permissions':'','_mod':'meeting'},{'title':_(u'会议签到情况报表'),'event':'/meeting/report/meeting_report/','permissions':'','_mod':'meeting'},{'title':_(u'人员参会情况统计'),'event':'/meeting/report/meeting_user_report/','permissions':'','_mod':'meeting'},{'title':_(u'人员异常情况报表'),'event':'/meeting/report/meeting_user_late_report/','permissions':'','_mod':'meeting'},{'title':_(u'会议室使用情况报表'),'event':'/meeting/report/meeting_room_report/','permissions':'','_mod':'meeting'}]},
        {'caption':{'title':_(u"门禁类报表"),'event':'','permissions':'','_mod':'acc','id':'id_acc_report'},'submenu':[{'title':u'%s'%_(u'全部记录'),'event':'/acc/report/records/','permissions':'acc.acc_reports','_mod':'acc'},{'title':_(u'异常记录'),'event':'/acc/report/acc_exception/','permissions':'acc.acc_reports','_mod':'acc'}]},
        {'caption':{'title':_(u"巡更类报表"),'event':'','permissions':'','_mod':'patrol','id':'id_patrol_report'},'submenu':[{'title':u'%s'%_(u'正常巡更记录'),'event':'/patrol/report/records/','permissions':'patrol.patrol_reports','_mod':'patrol'},{'title':_(u'人员巡更报表'),'event':'/patrol/report/patrol_xungeng/','permissions':'patrol.patrol_reports','_mod':'patrol'},
                        {'title':_(u'统计报表详情'),'event':'/patrol/report/patrol_details/','permissions':'patrol.patrol_reports','_mod':'patrol'},{'title':_(u'巡更统计汇总'),'event':'/patrol/report/patrol_xungengtotal/','permissions':'patrol.patrol_reports','_mod':'patrol'}
                        ]},
        {'caption':{'title':_(u"消费类报表"),'event':'','permissions':'','_mod':'ipos','id':'id_ipos_consumer_reports'},
         'submenu':[{'title':u'%s'%_(u'发卡表'),'event':'/ipos/report/IssueCard/','permissions':'','_mod':'ipos'},
                                {'title':u'%s'%_(u'充值表'),'event':'/ipos/report/Supplement/','permissions':'','_mod':'ipos'},
                                {'title':u'%s'%_(u'退款表'),'event':'/ipos/report/Refund/','permissions':'','_mod':'ipos'},
                                {'title':u'%s'%_(u'补贴表'),'event':'/ipos/report/Allowance/','permissions':'','_mod':'ipos'},
                                {'title':u'%s'%_(u'退卡表'),'event':'/ipos/report/Backcard/','permissions':'','_mod':'ipos'},
                                {'title':u'%s'%_(u'卡成本表'),'event':'/ipos/report/Cardcost/','permissions':'','_mod':'ipos'},
                                {'title':u'%s'%_(u'卡余额表'),'event':'/ipos/report/CardBlance/','permissions':'','_mod':'ipos'},
                                {'title':u'%s'%_(u'无卡退卡表'),'event':'/ipos/report/NoCardBack/','permissions':'','_mod':'ipos'},
                                {'title':u'%s'%_(u'管理卡表'),'event':'/ipos/report/CardManage/','permissions':'','_mod':'ipos'},
                                {'title':u'%s'%_(u'挂失解挂表'),'event':'/ipos/report/LoseUniteCard/','permissions':'','_mod':'ipos'},
                           # {'title':u'%s'%_(u'异常消费明细表'),'event':'/ipos/report/ErrorPosList/','permissions':'','_mod':'ipos'},
                                {'title':_(u'消费明细表'),'event':'/ipos/report/ICConsumerList/','permissions':'','_mod':'ipos;IC_POS'},
                                {'title':_(u'消费明细表'),'event':'/ipos/report/IDPosListReport/','permissions':'','_mod':'ipos;ID_POS'}]},
        {'caption':{'title':_(u"统计类报表"),'event':'','permissions':'','_mod':'ipos','id':'id_ipos_calc_reports'},
         'submenu':[{'title':u'%s'%_(u'个人消费汇总表'),'event':'/ipos/report/EmpSumPos/','permissions':'','_mod':'ipos'},
                                {'title':_(u'部门消费汇总表'),'event':'/ipos/report/DeptSumPos/','permissions':'','_mod':'ipos'},
                                {'title':_(u'餐厅消费汇总表'),'event':'/ipos/report/DiningSumPos/','permissions':'','_mod':'ipos'},
                                {'title':_(u'设备消费汇总表'),'event':'/ipos/report/DeviceSumPos/','permissions':'','_mod':'ipos'},
                                {'title':_(u'餐别消费汇总表'),'event':'/ipos/report/MealSumPos/','permissions':'','_mod':'ipos'},
                                {'title':_(u'收支汇总表'),'event':'/ipos/report/SzSumPos/','permissions':'','_mod':'ipos'}]},
        ]
    elif menuName=='options':#系统选项
        return [
        {'caption':{'title':_(u"系统设置"),'event':'','permissions':'','_mod':'','id':'id_options'},
                                        'submenu':[{'title':u'%s'%_(u"个性化设置"),'event':'/base/isys/option_users/','permissions':'','_mod':''},{'title':u'%s'%_(u"基本设置"),'event':'/base/isys/option_basic/','permissions':'iclock.sys_basic_setting','_mod':''},{'title':_(u'Email设置'),'event':'/base/isys/option_email/','permissions':'iclock.sys_email_setting','_mod':''},{'title':_(u'记录显示状态设置'),'event':'/base/isys/option_state/','permissions':'iclock.sys_state_setting','_mod':''},{'title':_(u'数据对接设置'),'event':'/base/isys/option_api/','permissions':'iclock.sys_api_setting','_mod':''},{'title':u'%s'%_(u"设备参数设置"),'event':'/base/isys/option_devices/','permissions':'iclock.sys_basic_setting','_mod':''}]},
        {'caption':{'title':_(u"自动任务计划设置"),'event':'','permissions':'','_mod':'','id':'id_tasks'},
                                        'submenu':[{'title':_(u'考勤统计任务设置'),'event':'/base/isys/option_calc/','permissions':'iclock.sys_calc_setting','_mod':''},{'title':_(u'清除数据任务设置'),'event':'/base/isys/option_deldata/','permissions':'iclock.sys_del_setting','_mod':''}]},
        {'caption':{'title':_(u"消费参数设置"),'event':'','permissions':'','_mod':'ipos','id':'id_ipos'},
                                        'submenu':[{'title':_(u'消费参数设置'),'event':'/base/isys/option_ipos/','permissions':'iclock.sys_pos_setting','_mod':'ipos'}]},
        #{'caption':{'title':_(u"考勤相关设置"),'event':'','permissions':'','_mod':'att','id':'id_att_options'},'submenu':[{'title':u'%s'%_("Holidays"),'event':'/iclock/data/holidays/','permissions':'iclock.browse_holidays','_mod':'att'},{'title':_('Leave Class'),'event':'/iclock/data/LeaveClass/','permissions':'iclock.browse_leaveclass','_mod':'att'},{'title':_('Attendance Rules'),'event':'/base/data/AttParam/','permissions':'iclock.browse_attparam','_mod':'att'}]},
        #{'caption':{'title':_(u"数据对接扩展设置"),'event':'','permissions':'','_mod':'att','id':'id_api_expend'},
        #       'submenu':[
        #               {'title':u'%s'%_(u"SAP对接设置"),'event':'/base/isys/option_sap_ftp/','permissions':'iclock.sys_sap_setting','_mod':'att'}]},
        #{'caption':{'title':_(u"数据对接扩展设置"),'event':'','permissions':'','_mod':'att','id':'id_api_expend'},'submenu':[{'title':u'%s'%_(u"SAP对接设置"),'event':'/base/isys/option_sap_ftp/','permissions':'iclock.sys_sap_setting','_mod':'att'},{'title':_(u'U盘数据管理'),'event':'/base/isys/option_upload/','permissions':'','_mod':'','img':''},]},
        {'caption':{'title':_(u"门禁设置"),'event':'','permissions':'iclock.sys_acc_setting','_mod':'acc','id':'id_acc_door'},'submenu':[{'title':u'%s'%_(u"远程开门设置"),'event':'/base/isys/option_acc_open/','permissions':'','_mod':'acc'}]},
        {'caption':{'title':_(u"智勤APP设置"),'event':'','permissions':'iclock.sys_app_setting','_mod':'att','id':'id_app_set'},'submenu':[{'title':u'%s'%_(u"智勤APP设置"),'event':'/base/isys/option_app/','permissions':'','_mod':'app'}]},
        ]
    elif menuName=='iaccess':#一体机菜单
        return [


#'submenu':[{'title':_(u"设备监控"),'event':'/iclock/data/DeviceMonitor/','permissions':'','_mod':'acc','img':''},
#{'title':_(u'门禁实时监控'),'event':'/iclock/data/AccessMonitor/','permissions':'','_mod':'acc','img':''},
#{'title':_(u'报警监控'),'event':'/iclock/data/AlarmMonitor/','permissions':'','_mod':'acc','img':''},
#{'title':_(u'地图管理'),'event':'/iclock/iacc/MapManageIndex/','permissions':'iclock.browse_mapmanage','_mod':'acc','img':''},
#{'title':_(u'电子地图监控'),'event':'/iclock/iacc/Map_Monitor/','permissions':'iclock.Map_Monitor','_mod':'acc','img':''},
#]},


        {'caption':{'title':_(u"一体机设置"),'event':'','permissions':'','_mod':'','id':'id_options'},'submenu':[{'title':_('ACGroup'),'event':'/acc/data/ACGroup/','permissions':'acc.browse_acgroup','_mod':'acc','img':''},
        {'title':_('ACUnlockComb'),'event':'/acc/data/ACUnlockComb/','permissions':'acc.browse_acunlockcomb','_mod':'acc','img':''},
        {'title':_('ACCSetHoliday'),'event':'/acc/data/ACCSetHoliday/','permissions':'acc.browse_accsetholiday','_mod':'acc','img':''},
        {'title':_('UserACPrivilege'),'event':'/acc/data/UserACPrivilege/','permissions':'acc.browse_useracprivilege','_mod':'acc','img':''},
        #{'title':_(u"设备监控"),'event':'/acc/data/DeviceMonitor/','permissions':'acc.monitor_oplog','_mod':'acc','img':''},
        #{'title':_(u"门禁实时监控"),'event':'/acc/data/AccessMonitor/','permissions':'','_mod':'acc','img':''},
        #{'title':_(u"报警监控"),'event':'/acc/data/AlarmMonitor/','permissions':'','_mod':'acc','img':''},
        {'title':_(u"地图管理"),'event':'/acc/iacc/MapManageIndex/','permissions':'iclock.browse_mapmanage','_mod':'acc','img':''}
        #{'title':_(u"电子地图监控"),'event':'/acc/iacc/Map_Monitor/','permissions':'iclock.Map_Monitor','_mod':'acc','img':''}
        ]},
        {'caption':{'title':_(u"数据查询"),'event':'','permissions':'','_mod':'','id':'id_acc_datasearch'},'submenu':[
        {'title':_(u"门禁记录"),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transaction','_mod':'acc','img':''},
        ]},
        {'caption':{'title':_(u"门禁监控"),'event':'','permissions':'','_mod':'','id':'id_acc_monitor'},'submenu':[
        #{'title':_(u"设备监控"),'event':'/acc/data/DeviceMonitor/','permissions':'acc.monitor_oplog','_mod':'acc','img':''},
        {'title':_(u'实时监控'),'event':'/iclock/data/_checkoplog_','permissions':'iclock.monitor_oplog','_mod':'acc','img':''},
        {'title':_(u"电子地图监控"),'event':'/acc/iacc/Map_Monitor/','permissions':'iclock.Map_Monitor','_mod':'acc','img':''}
        ]},
        {'caption':{'title':_(u"门禁报表"),'event':'','permissions':'','_mod':'','id':'id_reports'},'submenu':[
        {'title':_(u'设备与记录报表'),'event':'/acc/iacc/iaccessDevReports/','permissions':'iclock.browse_iaccdevitemdefine','_mod':'acc','img':''},
        {'title':_(u'人员与记录报表'),'event':'/acc/iacc/iaccessEmpReports/','permissions':'iclock.browse_iaccempitemdefine','_mod':'acc','img':''}
        ]},
        {'caption':{'title':_(u"其他设置"),'event':'','permissions':'','_mod':'ipos','id':'id_att_options'},'submenu':[{'title':u'%s'%_("Holidays"),'event':'/iclock/data/holidays/','permissions':'iclock.browse_holidays','_mod':'att'},{'title':_('Leave Class'),'event':'/iclock/data/LeaveClass/','permissions':'iclock.browse_leaveclass','_mod':'att'},{'title':_('Attendance Rules'),'event':'/iclock/data/AttParam/','permissions':'iclock.browse_attparam','_mod':'att'}]},

        ]
#    elif menuName=='inbio':#门禁控制器
#       return [
#
#       {'caption':{'title':_(u"门禁权限"),'event':'','permissions':'','_mod':'','id':'id_options'},'submenu':[{'title':_(u'门禁权限组'),'event':'/acc/data/level/','permissions':'acc.browse_level','_mod':'acc','img':''},
#       {'title':_(u'人员门禁权限'),'event':'/acc/data/ACUnlockComb/','permissions':'acc.browse_acunlockcomb','_mod':'acc','img':''},
#       ]},
#       {'caption':{'title':_(u"门禁规则"),'event':'','permissions':'','_mod':'','id':'id_acc_datasearch'},'submenu':[
#       {'title':_(u"互锁"),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transaction','_mod':'acc','img':''},
#       {'title':_(u"联动"),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transaction','_mod':'acc','img':''},
#       {'title':_(u"反潜"),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transaction','_mod':'acc','img':''},
#       {'title':_(u"首人常开"),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transaction','_mod':'acc','img':''},
#       {'title':_(u"多人开门人员组"),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transaction','_mod':'acc','img':''},
#       {'title':_(u"多人开门"),'event':'/iclock/data/transactions/','permissions':'iclock.browse_transaction','_mod':'acc','img':''},
#       ]},
#       {'caption':{'title':_(u"门禁参数"),'event':'','permissions':'','_mod':'','id':'id_acc_datasearch'},'submenu':[
#       {'title':_(u"门禁参数"),'event':'/acc/isys/inbio_params/','permissions':'','_mod':'acc','img':''},
#       ]},
#
#
#       {'caption':{'title':_(u"门禁监控"),'event':'','permissions':'','_mod':'','id':'id_acc_monitor'},'submenu':[
#       {'title':_(u'实时监控'),'event':'/iclock/data/_checkoplog_','permissions':'iclock.monitor_oplog','_mod':'acc','img':''},
#       {'title':_(u"电子地图监控"),'event':'/acc/iacc/Map_Monitor/','permissions':'iclock.Map_Monitor','_mod':'acc','img':''}
#       ]},
#       {'caption':{'title':_(u"门禁报表"),'event':'','permissions':'','_mod':'','id':'id_reports'},'submenu':[
#       {'title':_(u'设备与记录报表'),'event':'/acc/iacc/iaccessDevReports/','permissions':'iclock.browse_iaccdevitemdefine','_mod':'acc','img':''},
#       {'title':_(u'人员与记录报表'),'event':'/acc/iacc/iaccessEmpReports/','permissions':'iclock.browse_iaccempitemdefine','_mod':'acc','img':''}
#       ]},
#       {'caption':{'title':_(u"其他设置"),'event':'','permissions':'','_mod':'ipos','id':'id_att_options'},'submenu':[{'title':u'%s'%_("Holidays"),'event':'/iclock/data/holidays/','permissions':'iclock.browse_holidays','_mod':'att'},{'title':_('Leave Class'),'event':'/iclock/data/LeaveClass/','permissions':'iclock.browse_leaveclass','_mod':'att'},{'title':_('Attendance Rules'),'event':'/iclock/data/AttParam/','permissions':'iclock.browse_attparam','_mod':'att'}]},
#
#       ]

    elif menuName=='staff':#员工登陆
        return [
        {'caption':{'title':_(u"个人中心"),'event':'','permissions':'','_mod':'','id':'id_staff_info'},'submenu':[{'title':u'%s'%_(u"个人信息"),'event':'/iclock/staff/employee/','permissions':'','_mod':''},{'title':_(u"密码修改"),'event':'/iclock/accounts/password_change/','permissions':'','_mod':''},
                #{'title':_(u"个性化设置"),'event':'/iclock/staff/personalization/','permissions':'','_mod':''}
                ] },
        {'caption':{'title':_(u"数据中心"),'event':'','permissions':'','_mod':'','id':'id_staff_att'},'submenu':[{'title':u'%s'%_(u"我的带薪年假"),'event':'/iclock/staff/Annual/','permissions':'','_mod':''},{'title':u'%s'%_(u"我的记录"),'event':'/iclock/staff/transactions/','permissions':'','_mod':''},{'title':_(u'我的请假'),'event':'/iclock/staff/USER_SPEDAY/','permissions':'','_mod':''},{'title':_(u'我的排班'),'event':'/iclock/staff/USER_OF_RUN/','permissions':'','_mod':''},{'title':_(u'出勤详情'),'event':'/iclock/staff/attshifts/','permissions':'','_mod':''},{'title':_(u'我的异常'),'event':'/iclock/staff/abnormite/','permissions':'','_mod':''}]},
        {'caption':{'title':_(u"申请中心"),'event':'','permissions':'','_mod':'','id':'id_staff_apply'},'submenu':[{'title':u'%s'%_(u"申请请假"),'event':'/iclock/staff/apply_speday/','permissions':'','_mod':''},{'title':_(u'申请加班'),'event':'/iclock/staff/apply_overtime/','permissions':'','_mod':''},{'title':_(u'申请补记录'),'event':'/iclock/staff/apply_forget/','permissions':'','_mod':''}]},
        ]
    elif menuName=='sms':#短信息管理
        return [
        {'caption':{'title':_(u"短信息中心"),'event':'','permissions':'','_mod':'','id':'id_sms_info'},'submenu':[{'title':u'%s'%_(u"待发送信息"),'event':'/sms/report/outbox/','permissions':'','_mod':''},{'title':_(u"已发送信息"),'event':'/sms/report/senderoutbox','permissions':'','_mod':''},{'title':_(u"发送错误的信息"),'event':'/sms/report/badoutbox/','permissions':'','_mod':''}]},
        ]

    elif menuName=='accessRules':#门禁规则
        return[
        {'caption':{'title':_(u"门禁规则"),'event':'','permissions':'','_mod':'','id':'id_acc_datasearch'},'submenu':[
        {'title':_(u"互锁"),'event':'/acc/data/InterLock/','permissions':'acc.browse_interlock','_mod':'acc','img':''},
        {'title':_(u"联动"),'event':'/acc/data/linkage/','permissions':'acc.browse_linkage','_mod':'acc','img':''},
        {'title':_(u"反潜"),'event':'/acc/data/AntiPassBack/','permissions':'acc.browse_antipassback','_mod':'acc','img':''},
        {'title':_(u"首人常开"),'event':'/acc/data/FirstOpen/','permissions':'acc.browse_firstopen','_mod':'acc','img':''},
        {'title':_(u"多人开门人员组"),'event':'/acc/combopen/','permissions':'acc.browse_combopen','_mod':'acc','img':''},
        {'title':_(u"多人开门"),'event':'/acc/data/combopen_door/','permissions':'acc.browse_combopen_door','_mod':'acc','img':''},
        ]},
        #{'caption':{'title':_(u"门禁参数"),'event':'','permissions':'','_mod':'','id':'id_acc_datasearch'},'submenu':[
        #{'title':_(u"门禁参数"),'event':'/acc/isys/inbio_params/','permissions':'','_mod':'acc','img':''},
        #]}
        ]
    elif menuName=='IssueCard':
        return[
        {'caption':{'title':_(u"发卡信息"),'event':'','permissions':'','_mod':'','id':'id_ipos_card'},'submenu':[
        {'title':_(u"发卡信息"),'event':'/ipos/data/IssueCard/','permissions':'ipos.browse_issuecard','_mod':'ipos','img':''},
        ]},
                {'caption':{'title':_(u"卡操作"),'event':'','permissions':'','_mod':'','id':'id_ipos_card'},'submenu':[
                {'title':_(u"发普通卡"),'event':'/ipos/issuecard/IssueCard_IssueCard/','permissions':'ipos.issuecard_issuecard','_mod':'ipos','img':''},
                {'title':_(u"发管理卡"),'event':'/ipos/issuecard/IssueCard_ManageCard/','permissions':'ipos.issuecard_issuecard','_mod':'ipos','img':''},
                {'title':_(u"充值"),'event':'/ipos/issuecard/IssueCard_Supplement/','permissions':'ipos.issuecard_supplement','_mod':'ipos','img':''},
                {'title':_(u"退款"),'event':'/ipos/issuecard/IssueCard_Reimburse/','permissions':'ipos.issuecard_reimburse','_mod':'ipos','img':''},
                {'title':_(u"补卡"),'event':'/ipos/issuecard/IssueCard_ReissueCard/','permissions':'ipos.issuecard_issuecard','_mod':'ipos;IC_POS','img':''},
                {'title':_(u"退卡"),'event':'/ipos/issuecard/IssueCard_RetreatCard/','permissions':'ipos.issuecard_retreatcard','_mod':'ipos','img':''},
                {'title':_(u"卡资料修改"),'event':'/ipos/issuecard/IssueCard_UpdateCard/','permissions':'ipos.issuecard_updatecard','_mod':'ipos;IC_POS','img':''},
                ]},
                {'caption':{'title':_(u"卡初始操作"),'event':'','permissions':'','_mod':'','id':'id_ipos_card'},'submenu':[
                {'title':_(u"初始化卡"),'event':'/ipos/issuecard/IssueCard_InitCard/','permissions':'ipos.issuecard_initcard','_mod':'ipos;IC_POS','img':''},
                ]},
                {'caption':{'title':_(u"补贴及补签"),'event':'','permissions':'','_mod':'','id':'id_ipos_card'},'submenu':[
                {'title':_(u"补贴"),'event':'/ipos/data/Allowance/','permissions':'ipos.browse_allowance','_mod':'ipos','img':''},
                {'title':_(u"手工补消费"),'event':'/ipos/data/HandConsume/','permissions':'ipos.browse_handconsume','_mod':'ipos;IC_POS','img':''},
                ]}

        #{'caption':{'title':_(u"门禁参数"),'event':'','permissions':'','_mod':'','id':'id_acc_datasearch'},'submenu':[
        #{'title':_(u"门禁参数"),'event':'/acc/isys/inbio_params/','permissions':'','_mod':'acc','img':''},
        #]}
        ]

    elif menuName=='acc':
        return [

        {'caption':{'title':_(u"人员门禁权限"),'event':'','permissions':'','_mod':'','id':'id_options'},'submenu':[{'title':_(u'按权限组设置'),'event':'/acc/data/level/','permissions':'acc.browse_level','_mod':'acc','img':''},
        {'title':_(u'按人员设置'),'event':'/acc/level_emp/','permissions':'acc.browse_level','_mod':'acc','img':''},
        #{'title':_(u'门禁权限操作日志'),'event':'/iclock/data/AdminLog/?model=level','permissions':'iclock.browse_adminlog','_mod':'acc','img':''},
        # {'title':_(u'服务器下发命令'),'event':'/iclock/data/devcmds/','permissions':'iclock.browse_devcmds','_mod':'acc','img':''},
        ]},

        {'caption':{'title':_(u"门禁权限查询"),'event':'','permissions':'','_mod':'','id':'id_options'},'submenu':[
        {'title':_(u'以门查询'),'event':'/acc/door_emp/','permissions':'acc.browse_level','_mod':'acc','img':''},
        {'title':_(u'以人员查询'),'event':'/acc/emp_door/','permissions':'acc.browse_level','_mod':'acc','img':''}
        ]}

        ]
    else:
        return []

def enable_mod(mod_name,using_m,menuName=None):
    if mod_name=='':
        return True
    l_mod=mod_name.split(';')
    for m in l_mod:
        if (m==using_m) and (m in settings.ENABLED_MOD) and (m in settings.SALE_MODULE):
            return True
        if (m=='app') and (m in settings.ENABLED_MOD):
            return True
        if menuName and menuName=='options' and (m in settings.ENABLED_MOD) and (m in settings.SALE_MODULE):
            return True
    return False


def createmenu(request,menuName):
    html=''
    if not menuName:return html
    menulist=get_Menulist(menuName)
    using_m=request.GET.get('mod_name','')
#    print "------------",using_m
    if not settings.SALE_MODULE:
        getISVALIDDONGLE(reload=1)
    for t in menulist:
        _mod=t['caption']['_mod']
        if not enable_mod(_mod,using_m,menuName):
            continue
        caption=u'%s'%(t['caption']['title'])
        permission=t['caption']['permissions']
        #print "====",caption,permission,request.user.has_perm(permission)
        if not request.user.is_superuser and permission and (not request.user.has_perm(permission)):
            continue
        event=t['caption']['event']
        div_id=t['caption']['id']
        subhtml=''
        submenu=t['submenu']
        settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
        for sub in submenu:
            _mod=sub['_mod']
            if not enable_mod(_mod,using_m,menuName) and _mod!='mul_approval':
                continue
            if (_mod=='mul_approval'):#多级审批流程设计
                if not enable_mod('att'):continue
                #if GetParamValue('opt_basic_approval','0')=='0':
                #    continue
            if _mod=='udisk':
                u=GetParamValue('opt_basic_udisk','0')
                if u=='0':
                    continue
            if 'IC_POS' in _mod:
                if settings.CARDTYPE==1:continue
            elif 'ID_POS' in _mod:
                if settings.CARDTYPE==2:continue


            stitle=u'%s'%(sub['title'])
            subhtml=subhtml+''
            permission=sub['permissions']
            event=sub['event']
            if not permission  or (request.user.has_perm(permission)):

                #menuid=sub['id']
                if event:
                    if event.find('/')==-1:
                        subhtml=subhtml+"<li  onclick='%s' ><a href='javascript:void(0)'>"%(event)+stitle+"</a></li>"
                    #elif request.user.is_superuser or (not permission) or (HasPerm(request.user,permission)):
                    else:
                        subhtml=subhtml+"<li  onclick=submenuClick('%s',this);><a href='javascript:void(0)'>"%(event)+stitle+"</a></li>"
                    #else:
                 #   subhtml=subhtml#+"<li ><img src='../media/img/menu.png' style='width:12px;height:12px; float:left;left:10px;margin:3px 0 0 0px;' /><a href='#' >"+stitle+"</a></li>"
                else:
                    subhtml=subhtml+"<li><a href='javascript:void(0)' >"+stitle+"</a></li>"
        if subhtml!='':
            subhtml="<div id=%s class='nav'><ul>"%(div_id)+subhtml+'</ul></div>'
        if div_id=='':
            html=html+"""<h3 class='ui-widget-header ui-corner-top'><span class='ui-icon ui-icon-triangle-1-e'></span><a href='javascript:void(0)' >"""+caption+'</a></h3>'
        else:
            if subhtml=='':
                html=html
            else:
                html=html+"""<H3 class='ui-widget-header'><a >"""+caption+"</a></H3>"
        html=html+subhtml
    html="<div  id='menu_div' style='margin:4px;' >%s</div>"%html
    return html


def getMenus(request):
    """主界面切换各模块菜单"""
    mod_name=request.GET.get('mod_name','')
    m=MenuList(request,mod_name);
    menu_t=m.getMenu()
    submenu_t=m.getsubMenu()
    ret={'menu_t':menu_t,'submenu_t':submenu_t}
    #print submenu_t
    return getJSResponse(ret)
