#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.base.models import *
from django.template import  RequestContext 
from django.shortcuts import render_to_response,render
from django.db import models
from django.contrib.auth.models import  Permission
from mysite.iclock.iutils import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.sessions.models import Session
from mysite.iclock.datas import *
import datetime
from django.core.paginator import Paginator
#from mysite.iclock.dataview import *
#from pyExcelerator import *
from mysite.iclock.templatetags.iclock_tags import *
import copy
#from mysite.iclock.datasproc import *
from django.core.cache import cache
from django.contrib.auth.decorators import login_required,permission_required
from mysite.iclock.datautils import GetModel,hasPerm,QueryData
from mysite.iclock.datasproc import *
from mysite.core.menu import *
from mysite.iclock.jqgrid import *
from mysite.iclock.nomodelview import *
from mysite.meeting.datamisc import *
PAGE_LIMIT_VAR = 'l'



def GetGridCaption(rName,request):
	if request.method=="GET":
		disabledCols=FetchDisabledFields(request.user,rName)
		HeaderNames=[]
		colModel=[]
		
		if rName=='original_records':#原始记录表
			fieldNames,fieldCaptions,rt=ConstructScheduleFields2(request)
			it=0
			w=100
			for field in fieldCaptions:
				if field=='total':
					it=it+1
					continue
				if field=='userid' or field=='UserID' or field=='id':
					colModel.append({"name":"UserID",'hidden':True,'frozen':True})
				elif field=='DeptID'or field=='deptid':
					if field=='deptid':field='DeptID'
					colModel.append({"name":field,'sortable':True,'label':rt[it],'width':120,'frozen':True})
				else:
					if it>=6:
						w=80
					else:
						w=120
					if field =='badgenumber' or field == 'username':
						if field=='badgenumber':field='PIN'
						else:field='EName'
						colModel.append({"name":field,'sortable':True,'label':rt[it],'width':w,'frozen':True})
					else:
						colModel.append({"name":field,'sortable':False,'label':rt[it],'width':w})
				it=it+1
			#rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
			#return getJSResponse(rs)
		elif rName=='checkexact':
			colModel=checkexact.colModels()
			
		elif rName=='earlylatest_records':
			fieldNames,fieldCaptions,rt=ConstructScheduleFields2(request)
			r=[]
			it=0
			w=100
			for field in fieldCaptions:
				if field=='userid' or field=='UserID':
					r.append({"name":"UserID",'hidden':True,'frozen':True})
				elif field=='DeptID'or field=='deptid':
					r.append({"name":field,'sortable':False,'label':rt[it],'width':120,'frozen':True})
				else:
					if it>=6:
						w=80
					else:
						w=120
					if field =='badgenumber' or field == 'username':
						r.append({"name":field,'sortable':False,'label':rt[it],'width':w,'frozen':True})
					else:
						r.append({"name":field,'sortable':False,'label':rt[it],'width':w})
				it=it+1
		elif rName=='USER_OF_RUN':
			disabledCols=[]
			r=USER_OF_RUN.colModels()
		elif rName=='searchComposite':
			flag='shift2'
			fieldNames,fieldCaptions,rt=ConstructScheduleFields2(request)
			#disabledCols=FetchDisabledFields(request.user,flag)
			r=[]
			it=0
			w=100
			for field in fieldCaptions:
				if field=='userid' or field=='UserID':
					r.append({"name":"UserID",'hidden':True,'frozen':True})
				elif field=='deptid' or field=='badgenumber' or field=='username':
					if it>=4:
						w=100
					r.append({"name":field,'sortable':False,'label':rt[it],'width':w,'frozen':True})
				else:
					if it>=4:
						w=100
					r.append({"name":field,'sortable':False,'label':rt[it],'width':w})
				it=it+1
		elif rName=='USER_TEMP_SCH':
			disabledCols=[]
			r=USER_TEMP_SCH.colModels()
		elif rName=='calcAttShiftsReport':
			fieldNames,fieldCaptions,rt=ConstructAttshiftsFields1()
			#disabledCols=FetchDisabledFields(request.user,'calcAttShiftsReport')
			it=0
			for field in fieldNames:
				if field=='userid' or field=='UserID':
					colModel.append({"name":"UserID",'hidden':True})
				elif field=='DeptID' or field=='PIN' or field=='Workcode':
					colModel.append({"name":field,'sortable':False,'label':fieldCaptions[it],'width':120})
				elif field=='SSpeDayHolidayOT':
					colModel.append({"name":field,'sortable':False,'label':fieldCaptions[it],'width':150})
					
				else:
					colModel.append({"name":field,'sortable':False,'label':fieldCaptions[it],'width':80})
				it=it+1
		elif rName=='calcAttExceptionReport':
			#fieldNames,fieldCaptions,rt=ConstructAttshiftsFields1()
			#print fieldNames,fieldCaptions,rt
			
			fieldNames=['userid', 'DeptID', 'PIN','Workcode', 'EName', 'AttDate', 'SchId','Late', 'Early','NoIn','NoOut','Absent']
			
			fieldCaptions=[_("userid"),_('department name'),_('PIN'),_('NewPin'),_('name'),_('AttDate'),_('SchId'),_('Late'),_('Early'),_('NoIn'),_('NoOut'),_('Absent')]
			for i in range(len(fieldCaptions)):
				fieldCaptions[i]=u"%s"%fieldCaptions[i]
			#disabledCols=FetchDisabledFields(request.user,'calcAttShiftsReport')
			it=0
			for field in fieldNames:
				if field=='userid' or field=='UserID':
					colModel.append({"name":"UserID",'hidden':True})
				elif field=='DeptID' or field=='PIN' or field=='Workcode':
					colModel.append({"name":field,'sortable':False,'label':fieldCaptions[it],'width':120})
				elif field=='SSpeDayHolidayOT':
					colModel.append({"name":field,'sortable':False,'label':fieldCaptions[it],'width':150})
					
				else:
					colModel.append({"name":field,'sortable':False,'label':fieldCaptions[it],'width':80})
				it=it+1
		elif rName=='calcLeaveReport':
			rt,FieldNames,FieldCaption=ConstructLeaveFieldsEx()
			#disabledCols=FetchDisabledFields(request.user,'calcLeaveReport')
			it=0
			for field in FieldNames:
				if field.upper()=='USERID':
					colModel.append({"name":""+field,'hidden':True})
				elif field.upper()=='BADGENUMBER':
					colModel.append({"name":"badgenumber",'index':'UserID__PIN','sortable':True,'label':unicode(''+FieldCaption[it]),'width':120})
				else:
					colModel.append({"name":""+field,'sortable':False,'label':unicode(''+FieldCaption[it]),'width':80})
				it+=1
		elif rName=='calcLeaveYReport':
			rt,FieldNames,FieldCaption=ConstructLeaveFieldsEx()
			#disabledCols=FetchDisabledFields(request.user,'calcLeaveReport')
			it=0
			for field in FieldNames:
				if field.upper()=='USERID':
					colModel.append({"name":""+field,'hidden':True})
				elif field.upper()=='BADGENUMBER':
					colModel.append({"name":"badgenumber",'index':'UserID__PIN','sortable':True,'label':unicode(''+FieldCaption[it]),'width':120})
				else:
					colModel.append({"name":""+field,'sortable':False,'label':unicode(''+FieldCaption[it]),'width':80})
				it+=1
		elif rName=='USER_NO_SCH':
			r=[]
			FieldNames=['userid','deptid','badgenumber','username','Title']
			it=0
			FieldCaption=[_("userid"),_('department name'),_('PIN'),_('name'),_('Title')]
			for i in range(len(FieldCaption)):
				FieldCaption[i]=u"%s"%FieldCaption[i]
			for field in FieldNames:
				if field=='userid' or field=='UserID':
					r.append({"name":"UserID",'hidden':True})
				elif field=='deptid':
					r.append({"name":field,'sortable':False,'label':FieldCaption[it],'width':120})
				else:
					r.append({"name":field,'sortable':False,'label':FieldCaption[it],'width':120})
				it=it+1
			disabledCols=[]

		elif rName=='AttException':
			colModel=AttException.colModels()
		elif rName=='attRecAbnormite':
			#colModel=attRecAbnormite.colModels()
			colModel = [
			{'name':'UserID','hidden':True},
			{'name':'DeptName','width':180,'sortable':False,'label':unicode(_('department name'))},
			{'name':'PIN','sortable':False,'index':'UserID_PIN','width':120,'label':unicode(_('PIN'))},
			{'name':'Workcode', 'sortable':False, 'index':'UserID_Workcode', 'width':120, 'label':unicode(_('NewPin'))},
			{'name':'EName','sortable':False,'width':80,'label':unicode(_('EName'))},
			{'name':'TTime','width':120,'search':False,'label':unicode(transactions._meta.get_field('TTime').verbose_name)},
			{'name':'Verify','width':80,'search':False,'label':unicode(transactions._meta.get_field('Verify').verbose_name),'hidden':True},
			{'name':'State','width':80,'search':False,'label':unicode(transactions._meta.get_field('State').verbose_name)},
			{'name':'NewType','sortable':False,'width':180,'label':unicode(_('NewType'))},
			{'name':'AbNormiteID','sortable':False,'width':100,'label':unicode(_('Memo.'))},
			{'name':'Device','sortable':False,'width':200,'label':unicode(_('Device name'))},
			]
		elif rName=='employee_finger':#人员信息采集追踪表
			systag=request.GET.get("Systag")
			if systag=='0':
				colModel=[
					{'name':'id','hidden':True},
					{'name':'pin','sortable':False,'width':120,'label':unicode(_(u'PIN'))},
					{'name':'Workcode', 'sortable':False, 'width':100, 'label':unicode(_(u'NewPin'))},
					{'name':'name','sortable':False,'width':180,'label':unicode(_(u'姓名'))},
					{'name':'DeptNumber','sortable':False,'width':140,'label':unicode(_(u'单位编号'))},
					{'name':'DeptName','sortable':False,'width':180,'label':unicode(_(u'单位名称'))},
					{'name':'is_register','sortable':False,'width':100,'label':unicode(_(u'指纹采集'))},
					{'name':'is_register_face','sortable':False,'width':100,'label':unicode(_(u'面部采集'))},
					{'name':'is_register_card','sortable':False,'width':100,'label':unicode(_(u'卡采集'))},
				]
			else:
				colModel=[
					{'name':'id','hidden':True},
					{'name':'DeptNumber','sortable':False,'width':100,'label':unicode(_(u'单位编号'))},
					{'name':'DeptName','sortable':False,'width':180,'label':unicode(_(u'单位名称'))},
					{'name':'pin','sortable':False,'width':120,'label':unicode(_(u'PIN'))},
					{'name':'Workcode', 'sortable':False, 'width':100, 'label':unicode(_(u'NewPin'))},
					{'name':'name','sortable':False,'width':100,'label':unicode(_(u'姓名'))},
					{'name':'card','sortable':False,'width':80,'label':unicode(_(u'卡号'))},
					{'name':'is_register','sortable':False,'width':80,'label':unicode(_(u'指纹采集'))},
					{'name':'is_register_face','sortable':False,'width':80,'label':unicode(_(u'面部采集'))},
					{'name':'is_register_card','sortable':False,'width':80,'label':unicode(_(u'卡采集'))},
				]
		elif rName=='department_finger':
			colModel=[
				{'name':'id','hidden':True},
				{'name':'DeptNumber','sortable':False,'width':140,'label':unicode(_(u'单位编号'))},
				{'name':'DeptName','sortable':False,'width':180,'label':unicode(_(u'单位名称'))},
				{'name':'count','sortable':False,'width':80,'label':unicode(_(u'实有人数'))},
				{'name':'finger_count','sortable':False,'width':100,'label':unicode(_(u'采集指纹人数'))},
				{'name':'rate','sortable':False,'width':100,'label':unicode(_(u'指纹采集率%'))},
				{'name':'face_count','sortable':False,'width':100,'label':unicode(_(u'采集面部人数'))},
				{'name':'face_rate','sortable':False,'width':100,'label':unicode(_(u'面部采集率%'))},
			]
		elif rName=='device_assignment':
			colModel=[
				{'name':'id','hidden':True},
				{'name':'DeptNumber','sortable':False,'width':140,'label':unicode(_(u'单位编号'))},
				{'name':'DeptName','sortable':False,'width':180,'label':unicode(_(u'单位名称'))},
				{'name':'Devices','sortable':False,'width':90,'label':unicode(_(u'设备数量'))},
				{'name':'DeviceSN','sortable':False,'width':400,'label':unicode(_(u'设备SN号'))}
			]
			r=colModel
		elif rName=='daily_devices':
			colModel=[
				{'name':'id','hidden':True},
				{'name':'DeptNumber','sortable':False,'width':140,'label':unicode(_(u'单位编号'))},
				{'name':'DeptName','sortable':False,'width':180,'label':unicode(_(u'单位名称'))},
				{'name':'device_on','sortable':False,'width':180,'label':unicode(_(u'当日开机数'))},
				{'name':'device_count','sortable':False,'width':180,'label':unicode(_(u'设备数'))},
				{'name':'rate','sortable':False,'width':100,'label':unicode(_(u'开机率%'))}
			]
			r=colModel
		elif rName=='ihrreversedetail':
			colModel=[
				{'name':'id','hidden':True},
				{'name':'DeptNumber','sortable':False,'width':140,'label':unicode(_(u'单位号码'))},
				{'name':'DeptName','sortable':False,'width':180,'label':unicode(_(u'单位名称'))},
				{'name':'pin','sortable':False,'width':180,'label':unicode(_(u'PIN'))},
				{'name':'name','sortable':False,'width':180,'label':unicode(_(u'姓名'))}
			]
			r=colModel
		elif rName=='USER_SPEDAY':
			colModel=USER_SPEDAY.colModels()
			
		elif rName=='dailycalcReport':
			st=request.GET.get('startDate','')
			et=request.GET.get('endDate','')
			st=datetime.datetime.strptime(st,'%Y-%m-%d')
			et=datetime.datetime.strptime(et,'%Y-%m-%d')
			rt,fieldNames,fieldCaptions=ConstructFields1(st,et)
			#disabledCols=FetchDisabledFields(request.user,'dailycalcReport')
			it=0
			for field in fieldNames:
				if field=='userid' or field=='UserID':
					colModel.append({"name":""+field,'hidden':True})
				elif field.lower()=='badgenumber':
					colModel.append({"name":""+field,'sortable':False,'label':u'%s'%(fieldCaptions[it]),'width':110})
				elif field.lower()=='deptid':
					colModel.append({"name":""+field,'sortable':False,'label':u'%s'%_('department name'),'width':150})
				elif field=='SSpeDayHolidayOT':
					colModel.append({"name":field,'sortable':False,'label':u'%s'%_('SSpeDayHolidayOT'),'width':150})
				#elif field in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']:
				#	r.append({"name":""+field,'sortable':False,'label':unicode(''+fieldCaptions[it]),'width':40})
				else:
					colModel.append({"name":""+field,'sortable':False,'label':u'%s'%(fieldCaptions[it]),'width':80})
				it+=1

		elif rName=='calcReport':
			rt,fieldNames,fieldCaptions=ConstructFields()
			#disabledCols=FetchDisabledFields(request.user,rName)
			it=0
			for field in fieldNames:
				if field=='userid' or field=='UserID':
					colModel.append({"name":""+field,'hidden':True})
				elif field.lower()=='badgenumber':
					colModel.append({"name":""+field,'sortable':False,'label':u'%s'%(fieldCaptions[it]),'width':110})
				elif field.lower()=='deptid':
					colModel.append({"name":""+field,'sortable':False,'label':u'%s'%_('department name'),'width':150})
				elif field=='SSpeDayHolidayOT':
					colModel.append({"name":field,'sortable':False,'label':u'%s'%_('SSpeDayHolidayOT'),'width':150})
				else:
					colModel.append({"name":""+field,'sortable':False,'label':u'%s'%(fieldCaptions[it]),'width':80})
				it+=1

		elif rName=='department_report':
			AbnomiteRptItems=GetLeaveClasses()
			AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
			fieldNames=['dept','count','duty','realduty','absent','late','early','timeout','speday','noin','noout','yingqian']
			fieldTitle=[u'%s'%_(u'单位'),u'%s'%_(u'人数')]
			fieldCaptions=[u'%s'%_(u'单位'),u'%s'%_(u'人数'),u'%s'%_('duty'),u'%s'%_('realduty'),u'%s'%_('absent'),u'%s'%_('late'),u'%s'%_('early'),u'%s'%_(u'加班'),u'%s'%_(u'请假'),u'%s'%_('noin'),u'%s'%_('noout'),u'%s'%_(u'应签次数')]
			disabledCols=FetchDisabledFields(request.user,'department_report')
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1000)+"</span>")#应到
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1000)+"</span>")#实到
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1004)+"</span>")#旷工
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1001)+"</span>")#迟到
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1002)+"</span>")#早退
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1005)+"</span>")#加班
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1003)+"</span>")#请假
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1009)+"</span>")#
			#fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1008)+"</span>")#
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1009)+"</span>")#
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+u'%s'%(_(u"次"))+"</span>")
			r=[]
			it=0
			LClasses1=GetLeaveClasses(1)
			for t in LClasses1:
				#if t['LeaveId']==1:
				#	continue
				fName='Leave_'+str(t['LeaveID'])
				fieldNames.append(fName)
				fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,t['LeaveID'])+"</span>")
				fieldCaptions.append(t['LeaveName'])
			fieldNames.append('shijian')
			fieldNames.append('chuqinlv')
			fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+u'%s'%(_(u"小时"))+"</span>")
			fieldTitle.append(u'%s'%_(u'出勤率 %'))
			fieldCaptions.append(u'%s'%_(u'工作时间'))
			fieldCaptions.append(u'%s'%_(u'出勤率\n%'))
			for field in fieldNames:
				if field=='dept' :
					r.append({"name":""+field,'sortable':False,'label':u'%s'%(fieldTitle[it]),'width':120})
				else:
					r.append({"name":""+field,'sortable':False,'label':u'%s'%(fieldTitle[it]),'width':60})
				it+=1
			io=0
			for f in fieldNames:
				if f not in ['dept','count','chuqinlv']:
					HeaderNames.append({'startColumnName': f, 'numberOfColumns': 1, 'titleText': fieldCaptions[io]})
				io+=1
			rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+","+""""groupHeaders":"""+dumps(HeaderNames)+"""}"""
			return getJSResponse(rs)			
		elif rName=='annual_leave':
			disabledCols=[]
			colModel=annual_leave.colModels()
		elif rName=='annualstatic':
			disabledCols=[]
			colModel=[]
			heads,fields=getannualstaticFiled(request)
			index=0
			for field in fields:
				colModel.append({"name":""+field,'sortable':False,"index":""+field,'label':heads[index],'width':110})
				index=index+1
		elif rName=='meeting_sign_report':
			colModel=[
				{'name':'pin','sortable':False,'width':100,'label':unicode(_(u'PIN'))},
				{'name':'name','sortable':False,'width':100,'label':unicode(_(u'姓名'))},
				{'name':'DeptName','sortable':False,'width':120,'label':unicode(_(u'部门名称'))},
				{'name':'checkin','sortable':False,'width':120,'label':unicode(_(u'签到时间'))},
				{'name':'checkout','sortable':False,'width':120,'label':unicode(_(u'签退时间'))},
				{'name':'meetname','sortable':False,'width':180,'label':unicode(_(u'会议名称'))},
				{'name':'note','sortable':False,'width':180,'label':unicode(_(u'参会详情'))}

			]
			r=colModel
		elif rName=='meeting_not_sign_report':
			colModel=[
				{'name':'pin','sortable':False,'width':100,'label':unicode(_(u'工号'))},
				{'name':'name','sortable':False,'width':100,'label':unicode(_(u'姓名'))},
				{'name':'DeptName','sortable':False,'width':120,'label':unicode(_(u'部门名称'))},
				{'name':'meetname','sortable':False,'width':120,'label':unicode(_(u'会议名称'))}
			]
			r=colModel
		elif rName=='meeting_report':
			colModel=[
				{'name':'MeetID','sortable':False,'width':100,'label':unicode(_(u'会议编号'))},
				{'name':'conferenceTitle','sortable':False,'width':120,'label':unicode(_(u'会议名称'))},
				{'name':'Location','sortable':False,'width':120,'label':unicode(_(u'会议室'))},
				{'name':'Starttime','sortable':False,'width':120,'label':unicode(_(u'开始时间'))},
				{'name':'Endtime','sortable':False,'width':120,'label':unicode(_(u'结束时间'))},
				{'name':'duty','sortable':False,'width':50,'label':unicode(_(u'应到'))},
				{'name':'onduty','sortable':False,'width':50,'label':unicode(_(u'实到'))},
				{'name':'late','sortable':False,'width':50,'label':unicode(_(u'迟到'))},
				{'name':'early','sortable':False,'width':50,'label':unicode(_(u'早退'))},
				{'name':'speday','sortable':False,'width':50,'label':unicode(_(u'请假'))},
				{'name':'absent','sortable':False,'width':50,'label':unicode(_(u'缺席'))},
				{'name':'rate','sortable':False,'width':50,'label':unicode(_(u'出席率'))}
			]
			r=colModel
		elif rName=='meeting_user_report':
			colModel=[
				{'name':'pin','sortable':False,'width':80,'label':unicode(_(u'工号'))},
				{'name':'name','sortable':False,'width':100,'label':unicode(_(u'姓名'))},
				{'name':'DeptName','sortable':False,'width':120,'label':unicode(_(u'部门名称'))},
				{'name':'duty','sortable':False,'width':120,'label':unicode(_(u'应参加会议总数'))},
				{'name':'onduty','sortable':False,'width':120,'label':unicode(_(u'实参加会议总数'))},
				{'name':'absent','sortable':False,'width':120,'label':unicode(_(u'未参加会议总数'))},
				{'name':'late','sortable':False,'width':80,'label':unicode(_(u'迟到次数'))},
				{'name':'early','sortable':False,'width':80,'label':unicode(_(u'早退次数'))},
				{'name':'speday','sortable':False,'width':80,'label':unicode(_(u'请假次数'))},
				{'name':'rate','sortable':False,'width':80,'label':unicode(_(u'出席率'))}
			]
		elif rName=='meeting_user_late_report':
			colModel=[
				{'name':'pin','sortable':False,'width':80,'label':unicode(_(u'工号'))},
				{'name':'name','sortable':False,'width':100,'label':unicode(_(u'姓名'))},
				{'name':'DeptName','sortable':False,'width':120,'label':unicode(_(u'部门名称'))},
				{'name':'conferenceTitle','sortable':False,'width':120,'label':unicode(_(u'会议名称'))},
				{'name':'st','sortable':False,'width':120,'label':unicode(_(u'开始时间'))},
				{'name':'et','sortable':False,'width':120,'label':unicode(_(u'结束时间'))},
				{'name':'rst','sortable':False,'width':120,'label':unicode(_(u'签到时间'))},
				{'name':'ret','sortable':False,'width':120,'label':unicode(_(u'签退时间'))},
				{'name':'speday','sortable':False,'width':60,'label':unicode(_(u'请假'))},
				{'name':'absent','sortable':False,'width':60,'label':unicode(_(u'缺席'))},
				{'name':'late','sortable':False,'width':60,'label':unicode(_(u'迟到'))},
				{'name':'early','sortable':False,'width':60,'label':unicode(_(u'早退'))}
			]
			#r=colModel
		elif rName=='meeting_room_report':
			rt,fieldNames,fieldCaptions=ConstructROOMFields(request)
			it=0
			for field in fieldNames:
				if field in ['roomid','roomname','total','total_']:
					colModel.append({"name":field,'sortable':False,'label':u'%s'%(fieldCaptions[it]),'width':100})
				else:
					colModel.append({"name":""+field,'sortable':False,'label':u'%s'%(fieldCaptions[it]),'width':80})
				it+=1
		elif rName=='records':
			colModel=records.colModels()
			#return (disabledCols,colModel,HeaderNames) 
		elif rName=='acc_exception':
			colModel=records.colModels()
			#return (disabledCols,colModel,HeaderNames) 
#		return (disabledCols,colModel,HeaderNames)
		elif rName=='calcAllReport':
			from mysite.iclock.myreportview import getcalcallreportcol,getcalcallreportheader
			colModel = getcalcallreportcol()
			HeaderNames = getcalcallreportheader()
		elif rName=='exceptionReport':
			from mysite.iclock.myreportview import getexceptionreportcol,getexceptionreportheader
			colModel = getexceptionreportcol()
			HeaderNames = getexceptionreportheader()
		elif rName=='backReport':
			from mysite.iclock.myreportview import getbackreportcol,getbackreportheader
			colModel = getbackreportcol()
			HeaderNames = getbackreportheader()
		elif rName=='allexceptionReport':
			from mysite.iclock.myreportview import getallexceptionreportcol
			colModel = getallexceptionreportcol()
		elif rName=='jiezhuan':
			from mysite.iclock.myreportview import getjiezhuancol
			colModel = getjiezhuancol(request)
		d={}
		rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(colModel)+","+""""groupHeaders":"""+dumps(HeaderNames)+"""}"""
		return getJSResponse(rs)

def ConstructROOMFields(request):
	r={}
	FieldNames=['roomid','roomname','total','total_']
	for t in FieldNames:
		r[t]=''
	r['userid']=-1;
	FieldCaption=[u'%s'%_(u'会议室编号'),u'%s'%_(u'会议室名称'),u'%s'%_(u'合计次数'),u'%s'%_(u'合计小时数')]
	for i in range(len(FieldCaption)):
		FieldCaption[i]=u"%s"%FieldCaption[i]

	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	now=datetime.datetime.now()
	if st=='':
		st=datetime.datetime(now.year,now.month,1,0,0)
	else:
		st=datetime.datetime.strptime(st,"%Y-%m-%d")
	if et=='':
		et=now
	else:
		et=datetime.datetime.strptime(et,"%Y-%m-%d")
	t=st
	if (et-st).days>60:
		et=st+datetime.timedelta(days=60)
	while t<=et:
		d=str(t.month)+u'-'+str(t.day)
		FieldNames.append(d)
		d=str(t.month)+u'-'+str(t.day)+u'(小时)'
		FieldCaption.append(d)
		d=str(t.month)+u'-'+str(t.day)+u'_'
		FieldNames.append(d)
		d=str(t.month)+u'-'+str(t.day)+u'(次)'
		FieldCaption.append(d)
		t=t+datetime.timedelta(1)
		
	return [r,FieldNames,FieldCaption]
#原始记录表
def getoriginRecords(request,isContainedChild,deptIDs,userIDs,st,et,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	sidx=""
	ot=[]
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	if sidx:
		if request.method=='GET':
			sord = request.GET.get('sord')
		else:
			sord = request.POST.get('sord')
		order_by = '%s%s' % (sord == 'desc' and '-' or '', sidx)
		if sord=='-' or sord=='':
			order_by ='%s' % (sidx)
		ot=order_by.split(',')
		
	#ot=['DeptID','PIN']	
		
	if q!='':
		if request.user.is_superuser or request.user.is_alldept:
			objs=employee.objects.filter(OffDuty__lt=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
		else:
			deptids=userDeptList(request.user)
			deptids.sort()
			id=deptids[0]
			dept=department.objByID(id)
			if dept.parent==0:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
	else:
		if len(deptIDs)>0:
			if isContainedChild=='1':
				dept=department.objByID(deptIDs)
				if request.user.is_superuser or request.user.is_alldept:
					dptids=getAllAuthChildDept(dept.DeptID,request)
					objs=employee.objects.filter(DeptID__in=dptids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
				else:
					dids=[]
					deptids_Auth=userDeptList(request.user) #获得用户的授权部门
					deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
					for i in deptids_Subordinate:
						if i in deptids_Auth:
							dids.append(i)
					objs=employee.objects.filter(DeptID__in=dids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID=deptIDs,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)

		else:
			deptids=userDeptList(request.user)
			deptids.sort()
			objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)




	p=Paginator(objs, limit,allow_empty_first_page=True)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	#ids=pp.object_list.values_list('id', flat=True)
	re=[]
	Result={}
	for p in pp.object_list:
		d={}
		d['DeptID']=p.Dept().DeptName
		d['deptname']=p.Dept().DeptName
		d['Workcode'] = p.Workcode
		d['PIN']=p.PIN
		d['EName']=p.EName or ''
		d['card']=p.Card or ''
		st1=st
		while st1<=et:
			dd=str(st1.month)+'-'+str(st1.day)
			d[dd]=''
			st1=st1+datetime.timedelta(1)
		att=transactions.objects.filter(UserID=p.id,TTime__gte=st,TTime__lt=et).order_by('TTime')
		for t in att:
			dd=str(t.TTime.month)+'-'+str(t.TTime.day)
			sTime=t.TTime.strftime('%H:%M')
			if dd in d.keys():
				d[dd]=d[dd]+' '+sTime
			else:
				d[dd]=sTime
		re.append(d.copy())
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	#print "==================",Result
	return Result
		

#补记录表
def getforgetRecords(request):
	
	dataModel=checkexact
	jqGrid=JqGrid(request,datamodel=dataModel)
	items=jqGrid.get_items()   #not Paged
	cc=jqGrid.get_json(items)
	tmpFile=dataModel.__name__+'_list.js'
	t=loader.get_template(tmpFile)
	cc['can_change']=False
	try:
	    rows=t.render(RequestContext(request, cc))
	except Exception,e:
	    rows='[]'
	    pass
	Result={}
	Result['item_count']=cc['records']
	Result['page']=cc['page']
	Result['page_count']=cc['total']
	Result['datas']=loads(rows)
	return Result
	
	
	
	#iCount=0
	#try:
	#	offset = int(request.POST.get('page', 1))
	#except:
	#	offset=1
	#limit= int(request.POST.get('rows', 0))
	#if limit==0:
	#	limit= int(request.GET.get('rows', 30))
	#sidx=""
	#if request.GET.has_key('sidx'):
	#	sidx = request.GET.get('sidx','')
	#else:
	#	sidx = request.POST.get('sidx','')
	#ot=sidx.split(',')
	#if q!='':
	#	if request.user.is_superuser or request.user.is_alldept:
	#		emps=employee.objects.filter(OffDuty__lt=1).filter(Q(PIN=q)|Q(EName=q)).va;ues("id")
	#	else:
	#		deptids=userDeptList(request.user)
	#		deptids.sort()
	#		id=deptids[0]
	#		dept=department.objByID(id)
	#		if dept.parent==0:
	#			emps=employee.objects.filter(OffDuty__lt=1,DelTag=0).filter(Q(PIN=q)|Q(EName=q)).values('id')
	#		else:
	#			emps=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q)).values("id")
	#	objs=checkexact.objects.filter(UserID__in=emps,CHECKTIME__gte=st,CHECKTIME__lt=et).order_by('-CHECKTIME')
	#else:
	#	if len(deptIDs)>0:
	#		isContainedChild=request.GET.get('isContainChild','0')
	#		dept=department.objByID(deptIDs)
	#		if dept.parent==0:
	#			emps=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).values('id')
	#		else:
	#			deptids=getAllAuthChildDept(dept.DeptID,request)
	#			emps=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).values('id')
	#		objs=checkexact.objects.filter(UserID__in=emps,CHECKTIME__gte=st,CHECKTIME__lt=et).order_by('-CHECKTIME')	
	#	else:
	#		Result={}
	#		Result['item_count']=0
	#		Result['page']=1
	#		Result['limit']=30
	#		Result['from']=1
	#		Result['page_count']=0
	#		Result['datas']=[]
	#		return Result
	#p=Paginator(objs, limit,allow_empty_first_page=True)
	#iCount=p.count
	#if iCount<(offset-1)*limit:
	#	offset=1
	#page_count=p.num_pages
	#pp=p.page(offset)
	##ids=pp.object_list.values_list('id', flat=True)
	#re=[]
	#Result={}
	#for p in pp.object_list:
	#	d={}
	#	d['DeptID']=p.employee().Dept().DeptNumber
	#	d['DeptName']=p.employee().Dept().DeptName
	#	d['PIN']=p.employee().PIN
	#	d['EName']=p.employee().EName
	#	d['CHECKTIME']=p.CHECKTIME
	#	d['CHECKTYPE']=StateName(p.CHECKTYPE)
	#	d['YUYIN']=p.YUYIN
	#	re.append(d.copy())
	#if offset>page_count:offset=page_count
	#item_count =iCount
	#Result['item_count']=item_count
	#Result['page']=offset
	#Result['limit']=limit
	#Result['from']=(offset-1)*limit+1
	#Result['page_count']=page_count
	#Result['datas']=re
	#return Result

#人员班次异常详情表
def getcalcAttexceptionReport(request,isContainedChild,deptids,userids,d1,d2,q):
	result=CalcAttShiftsReportItem(request,deptids,userids,d1,d2,1)
	return result

#人员班次详情表
def getAttshiftsDaily(request,isContainedChild,deptids,userids,d1,d2,q):
	result=CalcAttShiftsReportItem(request,deptids,userids,d1,d2,0)
	return result
#	preUserid=0
#	AttRule=LoadAttRule()
#	schClasses=GetSchClasses()
#	AbnomiteRptItems=GetLeaveClasses()
#	AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
#	#排序
#	sidx=""
#	ot=[]
#	if request.GET.has_key('sidx'):
#		sidx = request.GET.get('sidx','')
#	else:
#		sidx = request.POST.get('sidx','')
#	if sidx:	
#		if request.method=='GET':
#		    sord = request.GET.get('sord')
#		else:
#		    sord = request.POST.get('sord')
#		order_by = '%s%s' % (sord == 'desc' and '-' or '', sidx)
#		if sord=='-' or sord=='':
#		    order_by ='%s' % (sidx)
#		ot=order_by.split(',')
#	if ot:
#		ot.append('SchId')
#	if len(userids)>0 and userids!='null':
#		ids=userids.split(',')
#		attshifts=attShifts.objects.filter(UserID__in=ids,AttDate__gte=d1,AttDate__lte=d2)
#		attExcept=AttException.objects.filter(UserID__in=ids,AttDate__gte=d1,AttDate__lte=d2)
#	elif len(deptids)>0:
#		isContainedChild=request.GET.get('isContainChild','0')
#		deptIDS=deptids.split(',')
#		deptids=deptIDS
#		if isContainedChild=="1": #是否包含下级部门
#			deptids=[]
#			for d in deptIDS:#支持选择多部门
#				if int(d) not in deptids :
#					deptids+=getAllAuthChildDept(d,request)
#		attshifts=attShifts.objects.filter(UserID__DeptID__in=deptids,AttDate__gte=d1,AttDate__lte=d2).order_by(*ot)
#		attExcept=AttException.objects.filter(UserID__DeptID__in=deptids,AttDate__gte=d1,AttDate__lte=d2)
#	else:
#		attshifts=attShifts.objects.filter(AttDate__gte=d1,AttDate__lte=d2).order_by(*ot)
#		attExcept=AttException.objects.filter(AttDate__gte=d1,AttDate__lte=d2)
#		
#
#
#
#	Result={}
#	re=[]
#	#分页		
#	try:
#		if request.method=='GET':
#			offset = int(request.GET.get('page', 1))
#		else:
#			offset = int(request.POST.get('page', 1))
#	except:
#		offset=1
#	limit= int(request.POST.get('rows', settings.PAGE_LIMIT))  #导出时使用
#	paginator = Paginator(attshifts, limit)
#	item_count = paginator.count
#	pgList = paginator.page(offset)
#	page_count=paginator.num_pages
#	fieldNames,fieldCaptions,rt=ConstructAttshiftsFields1()
#	disabledCols=FetchDisabledFields(request.user,'attShifts')
#	Result['item_count']=item_count
#	Result['page']=offset
#	Result['limit']=limit
#	Result['from']=(offset-1)*limit+1
#	Result['page_count']=page_count
#	Result['fieldnames']=fieldNames
#	Result['fieldcaptions']=fieldCaptions
#	Result['disableCols']=disabledCols
#	for t in pgList.object_list:
#		r=rt.copy()
#		eid=int(t.UserID_id)
#		e=employee.objByID(eid)
#		r['userid']=eid
#		r['DeptID']=e.Dept().DeptName
#		r['PIN']=e.PIN
#		r['EName']=e.EName
#		r['AttDate']=t.AttDate.date()
#		if t.SchId_id:
#			r['SchId']=FindSchClassByID(t.SchId_id)['SchName']
#		else:
#			r['SchId']=transLeaName(1005)
#		r['Schid']=getValidValue(t.SchId_id)
#		r['ClockInTime']=t.ClockInTime.strftime('%H:%M:%S')
#		r['ClockOutTime']=t.ClockOutTime.strftime('%H:%M:%S')
#		r['StartTime']=""
#		r['EndTime']=""
#		if t.StartTime:
#			r['StartTime']=t.StartTime.strftime('%H:%M:%S')
#		if t.EndTime:	
#			r['EndTime']=t.EndTime.strftime('%H:%M:%S')
#		r['WorkDay']=getValidValue(t.WorkDay)
#		r['RealWorkDay']=getValidValue(t.RealWorkDay)
#		r['Late']=getValidValue(t.Late)
#		r['Early']=getValidValue(t.Early)
#		r['Absent']=IsYesNo(t.Absent)
#		r['OverTime']=getValidValue(t.OverTime)
#		r['WorkTime']=getValidValue(t.WorkTime)
#		r['MustIn']=IsYesNo(t.MustIn)
#		r['MustOut']=IsYesNo(t.MustOut)
#		r['SSpeDayNormal']=getValidValue(t.SSpeDayNormal)
#		r['SSpeDayWeekend']=getValidValue(t.SSpeDayWeekend)
#		r['SSpeDayHoliday']=getValidValue(t.SSpeDayHoliday)
#		r['AttTime']=hourAndMinute(t.AttTime)
#		r['SSpeDayNormalOT']=getValidValue(t.SSpeDayNormalOT)
#		r['SSpeDayWeekendOT']=getValidValue(t.SSpeDayWeekendOT)
#		r['SSpeDayHolidayOT']=getValidValue(t.SSpeDayHolidayOT)
#		#合并各种假
#		excidlist=[]
##		if (r['AttDate']<>preDate) or (t.UserID_id<>preUserid):
#		for tt in attExcept:
#			if (tt.AttDate.date()<>r['AttDate']) or (tt.UserID_id<>t.UserID_id) or (t.SchId_id<>tt.schid):
#				continue
#			if tt.ExceptionID and tt.ExceptionID>0:
#				fname=tt.ExceptionID
#				if AbnomiteRptItems[AttAbnomiteRptIndex[fname]]['Unit']==auTimes:#判断按次计算
#					InScopeTime=NormalAttValue(tt.InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[fname]]['MinUnit'],
#							 AbnomiteRptItems[AttAbnomiteRptIndex[fname]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[fname]]['RemaindProc'])
#					
#					try:
#						r['Leave_'+str(fname)]=int(r['Leave_'+str(fname)])
#						
#					except Exception,ee:
#						r['Leave_'+str(fname)]=0
#					
#					r['Leave_'+str(fname)]=SaveValue(r['Leave_'+str(fname)],InScopeTime)
#				else:
#					InScopeTime=tt.InScopeTime
#					if AbnomiteRptItems[AttAbnomiteRptIndex[fname]]['RemaindCount']==0:#判断先舍入后累计
#						v=NormalAttValue(InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[fname]]['MinUnit'],
#							AbnomiteRptItems[AttAbnomiteRptIndex[fname]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[fname]]['RemaindProc'])
#					else:
#						v=tt.InScopeTime
#						if not tt.ExceptionID in excidlist:
#							excidlist.append(tt.ExceptionID)
#					try:
#						r['Leave_'+str(fname)]=float(r['Leave_'+str(fname)])
#					except Exception,ee:
#						r['Leave_'+str(fname)]=0
#					r['Leave_'+str(fname)]=SaveValue(r['Leave_'+str(fname)],v)
#		for exid in excidlist:
#			ve=r['Leave_'+str(exid)]
#			if ve:
#				r['Leave_'+str(exid)]=NormalAttValue(ve,AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['MinUnit'],
#										 AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['RemaindProc'])
#
#		for ttt in r.keys():              #不显示空的数据
#			if not r[ttt]:r[ttt]=""
#			elif type(r[ttt])==type(1.0):
#				if r[ttt]>int(r[ttt]):
#					r[ttt]=str(r[ttt])
#		
#		preDate=r['AttDate']
#		preUserid=t.UserID_id
#		re.append(r.copy())
#	Result['datas']=re
#	return Result




#未排班人员表
def getUserNoSch(request,isContainedChild,deptids,userids,d1,d2,q):
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	q=request.GET.get('q',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	st=datetime.datetime.strptime(st,'%Y-%m-%d')
	et=datetime.datetime.strptime(et,'%Y-%m-%d')
	iCount=0
	if q:
		deptidlist=deptIDs.split(',')
		deptids=deptidlist
		if isContainedChild=="1": #是否包含下级部门
			deptids=[]
			for d in deptidlist:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		ot=['DeptID','PIN']
		ids=employee.objects.filter(DeptID__in=deptids,PIN__startswith='%s'%(q),OffDuty__lt=1).exclude(DelTag=1).values_list('id', flat=True).order_by(*ot)
	elif len(userIDs)>0 and userIDs!='null':
		ids=userIDs.split(',')
		#iCount=len(ids)
	elif len(deptIDs)>0:
		deptidlist=deptIDs.split(',')
		deptids=deptidlist
		if isContainedChild=="1": #是否包含下级部门
			deptids=[]
			for d in deptidlist:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		ot=['DeptID','PIN']
		ids=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).values_list('id', flat=True).order_by(*ot)
	qs=USER_OF_RUN.objects.filter(UserID__in=ids).exclude(StartDate__gt=d2).exclude(EndDate__lt=d1).values_list('UserID', flat=True)
	qs1=USER_TEMP_SCH.objects.filter(UserID__in=ids).filter(ComeTime__gte=d1).filter(LeaveTime__lt=d2).values_list('UserID', flat=True)
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 30))
	re=[]
	Result={}
	Result['datas']=re
	iCount=len(ids)
	ids=ids[(offset-1)*limit:offset*limit]
	for id in ids:
		if (id not in qs) and (id not in qs1):
			emp=employee.objByID(id)
			if emp:
				d={}
				d['userid']=id
				d['deptid']=emp.DeptID.DeptName
				d['badgenumber']=emp.PIN
				d['username']=emp.EName
				d['Title']=emp.Title
				re.append(d.copy())
				#iCount=iCount+1

	page_count =int(ceil(iCount/float(limit)))
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result


def getEarlystAndLastest(request,isContainedChild,deptIDs,userIDs,st,et,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	sidx=""
	ot=[]
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	if sidx:
		ot=sidx.split(',')
	if q!='':
		if request.user.is_superuser or request.user.is_alldept:
			objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q))
		else:
			deptids=userDeptList(request.user)
			deptids.sort()
			id=deptids[0]
			dept=department.objByID(id)
			if dept.parent==0:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q)).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q)).order_by(*ot)
	else:
		if len(deptIDs)>0:
			if isContainedChild=='1':
				dept=department.objByID(deptIDs)
				if request.user.is_superuser or request.user.is_alldept:
					dptids=getAllAuthChildDept(dept.DeptID,request)
					objs=employee.objects.filter(DeptID__in=dptids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
				else:
					dids=[]
					deptids_Auth=userDeptList(request.user) #获得用户的授权部门
					deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
					for i in deptids_Subordinate:
						if i in deptids_Auth:
							dids.append(i)
					objs=employee.objects.filter(DeptID__in=dids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID__in=deptIDs,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
		else:
			Result={}
			Result['item_count']=0
			Result['page']=1
			Result['limit']=30
			Result['from']=1
			Result['page_count']=0
			Result['datas']=[]
			return Result
	p=Paginator(objs, limit,allow_empty_first_page=True)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	#ids=pp.object_list.values_list('id', flat=True)
	re=[]
	Result={}
	for p in pp.object_list:
		d={}
		d['deptid']=p.Dept().DeptNumber
		d['deptname']=p.Dept().DeptName
		d['badgenumber']=p.PIN
		d['username']=p.EName
		st1=st
		while st1<=et:
			dd=str(st1.month)+'-'+str(st1.day)
			d[dd]=''
			st1=st1+datetime.timedelta(1)
		att=transactions.objects.filter(UserID=p.id,TTime__gte=st,TTime__lt=et).order_by('TTime')
		lasttime=[]
		for t in att:
			dd=str(t.TTime.month)+'-'+str(t.TTime.day)
			sTime=t.TTime.strftime('%H:%M')
			if dd in d.keys():
				if d[dd]=='':
					d[dd]=sTime
				if lasttime:
					if dd<>lasttime[0] and d[lasttime[0]]<>lasttime[1]:
							d[lasttime[0]]=d[lasttime[0]]+' '+lasttime[1]
				lasttime=[]
				lasttime.append(dd)
				lasttime.append(sTime)
			else:
				pass
		re.append(d.copy())
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

	
	
	
	
#	isContainedChild=request.GET.get("isContainChild","0")
#	deptIDs=request.GET.get('deptIDs',"")
#	userIDs=request.GET.get('UserIDs',"")
#	q=request.GET.get('q',"")
#	st=request.GET.get('startDate','')
#	et=request.GET.get('endDate','')
#	st=datetime.datetime.strptime(st,'%Y-%m-%d')
#	et=datetime.datetime.strptime(et,'%Y-%m-%d')+datetime.timedelta(days=1)
#	
#	iCount=0
#	if q:
#		deptidlist=deptIDs.split(',')
#		deptids=deptidlist
#		if isContainedChild=="1": #是否包含下级部门
#			deptids=[]
#			for d in deptidlist:#支持选择多部门
#				if int(d) not in deptids :
#					deptids+=getAllAuthChildDept(d,request)
#		ot=['DeptID','PIN']
#		emps=employee.objects.filter(DeptID__in=deptids,DelTag=0,PIN__startswith='%s'%(q),OffDuty__lt=1).values('id')
#	elif len(userIDs)>0 and userIDs!='null':
#		emps=userIDs.split(',')
#
#		#iCount=len(ids)
#	elif len(deptIDs)>0:
#		deptidlist=deptIDs.split(',')
#		deptids=deptidlist
#		if isContainedChild=="1": #是否包含下级部门
#			deptids=[]
#			for d in deptidlist:#支持选择多部门
#				if int(d) not in deptids :
#					deptids+=getAllAuthChildDept(d,request)
#		ot=['DeptID','PIN']
#		emps=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).values('id')
#	objs=attRecAbnormite.objects.filter(UserID__in=emps,checktime__gte=st,checktime__lt=et).order_by('checktime')
#	try:
#		offset = int(request.POST.get('page', 1))
#	except:
#		offset=1
#	if request.method=='GET':#导出数据时是GET
#		limit= int(request.GET.get('rows', 30))
#	else:		
#		limit= int(request.POST.get('rows', 30))
#	re=[]
#	Result={}
#	Result['datas']=re
#	
#	
#	p=Paginator(objs, limit,allow_empty_first_page=True)
#	iCount=p.count
#	if iCount<(offset-1)*limit:
#		offset=1
#	page_count=p.num_pages
#	qs1=p.page(offset)
#	
#	for t in qs1:
#		d={}
#		e=employee.objByID(t.UserID_id)
#		d['userid']=t.UserID_id
#		d['DeptName']=e.Dept().DeptName
#		d['PIN']=e.PIN
#		d['EName']=e.EName
#		d['Verify']=t.getComVerifys()
#		d['CheckType']=StateName(t.CheckType)
#		d['checktime']=datetime.datetime.strftime(t.checktime,'%Y-%m-%d %H:%M:%S')
#		d['NewType']=StateName(t.NewType)
#		#d['AbNormiteID']=AbnormiteName(t.AbNormiteID)
#		if t.SN:
#			d['Device']=t.Device().SN
#		else:
#			d['Device']=''
#
#		re.append(d.copy())
#		iCount=iCount+1
#	#page_count =int(ceil(iCount/float(limit)))
##	if offset>page_count:offset=page_count
#	item_count =iCount
#	Result['item_count']=item_count
#	Result['page']=offset
#	Result['limit']=limit
#	Result['from']=(offset-1)*limit+1
#	Result['page_count']=page_count
#	Result['datas']=re
#	return Result
#人员请假汇总表
def getcalcLeaveReport(request,isContainedChild,deptids,userids,d1,d2,q):
	result=CalcLeaveReportItem(request,deptids,userids,d1,d2)
	return result

def getcalcLeaveYReport(request,isContainedChild,deptids,userids,d1,d2,q):
	calcyear=request.GET.get('y','')
	if calcyear=='':
		calcyear=now.year
	else:
		calcyear=int(calcyear)
	st=datetime.datetime(calcyear,1,1,0,0,0)
	et=datetime.datetime(calcyear,12,31,23,59,59)
	result=CalcLeaveReportItem(request,deptids,userids,st,et)
	return result


#	global schClasses
#	AttRule=LoadAttRule()
#	AbnomiteRptItems=GetLeaveClasses()
#	GetRptIndex(AbnomiteRptItems);
#	AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
#	#排序
#	sidx=""
#	if request.GET.has_key('sidx'):
#		sidx = request.GET.get('sidx','')
#	else:
#		sidx = request.POST.get('sidx','')
#	ot=sidx.split(',')
#	if len(userids)>0 and userids!='null':
#		ids=userids.split(',')
#		#emps=employee.objects.filter(id__in=ids,OffDuty__lt=1).values_list('id',flat=True)
#		if len(ot)<=0 or ot[0]=='':
#			ot=['UserID__DeptID','UserID__PIN']
#		ot=['UserID__DeptID','UserID__PIN']
#		emps=AttException.objects.values('UserID').annotate().filter(UserID__in=ids,AttDate__gte=d1,AttDate__lte=d2).order_by(*ot)
#
#	elif len(deptids)>0:
#		deptIDS=deptids.split(',')
#		deptids=deptIDS
#		if isContainedChild=="1": #是否包含下级部门
#			deptids=[]
#			for d in deptIDS:#支持选择多部门
#				if int(d) not in deptids :
#					deptids+=getAllAuthChildDept(d,request)
#		if len(ot)<=0 or ot[0]=='':
#			ot=['UserID__DeptID','UserID__PIN']
#		ot=['UserID__DeptID','UserID__PIN']
#		#emps=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).values_list('id', flat=True)
#		emps=AttException.objects.filter(UserID__DeptID__in=deptids,AttDate__gte=d1,AttDate__lte=d2).order_by(*ot).values('UserID').annotate()
#	else:
#		ot=['UserID__DeptID','UserID__PIN']
#		emps=AttException.objects.values('UserID').annotate().filter(AttDate__gte=d1,AttDate__lte=d2).order_by(*ot)
#	Result={}
#	re=[]
#	
#	try:
#		if request.method=='GET':
#			offset = int(request.GET.get('page', 1))
#		else:
#			offset = int(request.POST.get('page', 1))
#	except:
#		offset=1
#		
#	limit= int(request.POST.get('rows', settings.PAGE_LIMIT))  #导出时使用
#	item_count =len(emps)
#	page_count =int(ceil(item_count/float(limit)))
#	if page_count and offset>page_count:offset=page_count
#	uids=[]
#	k=0
#	ids=emps[(offset-1)*limit:offset*limit]
#
#	Result['item_count']=item_count
#	Result['page']=offset
#	Result['limit']=limit
#	Result['from']=(offset-1)*limit+1
#	Result['page_count']=page_count
##	r,Fields,Capt=ConstructFields()
#	r,FieldNames,FieldCaption=ConstructLeaveFields()
#	
#	LClasses1=GetLeaveClasses(1)
#	for t in LClasses1:
#		fName='Leave_'+str(t['LeaveId'])
#		FieldNames.append(fName)
#		r[fName]=''
#		FieldCaption.append(t['LeaveName'])
#		
#	Result['fieldnames']=FieldNames
#	Result['fieldcaptions']=FieldCaption
#	Result['datas']=r
#	
#	for uid in ids:
#		#emp=employee.objByID(uid)
#		uid=int(uid['UserID'])
#		emp=employee.objByID(uid)
#		rmdAttday=r.copy()
#		attExcept=AttException.objects.filter(UserID=emp,AttDate__gte=d1,AttDate__lte=d2)#.values('ExceptionID')#.annotate(inscopetime=Count('InScopeTime'))
#		for y in rmdAttday.keys():
#			rmdAttday[y]=''
#		rmdAttday['userid']=uid
#		rmdAttday['deptid']=emp.DeptID.DeptName
#		rmdAttday['badgenumber']=emp.PIN
#		rmdAttday['username']=emp.EName
#		rmdAttday['ssn']=emp.SSN
#		excidlist=[]
#		for ex in attExcept:
#			exceptid=ex.ExceptionID
#			if exceptid in [caeFreeOT,caeOT,caeOut,caeBOut]:
#				continue
#			elif exceptid>0:
#				if AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['Unit']==auTimes:#判断按次计算
#					InScopeTime=NormalAttValue(ex.InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['MinUnit'],
#							 AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindProc'])
#					
#					try:
#						rmdAttday['Leave_'+str(exceptid)]=int(rmdAttday['Leave_'+str(exceptid)])
#						
#					except Exception,ee:
#						rmdAttday['Leave_'+str(exceptid)]=0
#					
#					rmdAttday['Leave_'+str(exceptid)]=SaveValue(rmdAttday['Leave_'+str(exceptid)],InScopeTime)
#				else:
#					InScopeTime=ex.InScopeTime
#					if AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindCount']==0:#判断先舍入后累计
#						v=NormalAttValue(InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['MinUnit'],
#							AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindProc'])
#					else:
#						v=ex.InScopeTime
#						if not exceptid in excidlist:
#							excidlist.append(exceptid)
#					try:
#						rmdAttday['Leave_'+str(exceptid)]=float(rmdAttday['Leave_'+str(exceptid)])
#					except Exception,ee:
#						rmdAttday['Leave_'+str(exceptid)]=0
#					rmdAttday['Leave_'+str(exceptid)]=SaveValue(rmdAttday['Leave_'+str(exceptid)],v)
#				if AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['IsLeave']==1:	#只有计为请假时才累计 2009.5.6
#					try:
#						rmdAttday['Leave']=float(rmdAttday['Leave'])
#					except Exception,ee:
#						rmdAttday['Leave']=0
#					if AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['Unit']==auTimes:
#						v=NormalAttValue(InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['MinUnit'],
#								AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['RemaindProc'])
#					else:
#						if AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['RemaindCount']==0:
#							v=NormalAttValue(ex.InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['MinUnit'],
#									 AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['RemaindProc'])
#						else:
#							v=ex.InScopeTime
#					rmdAttday['Leave']=SaveValue(rmdAttday['Leave'],v)
#		if excidlist:
#			for exid in excidlist:
#				try:
#					rmdAttday['Leave_'+str(exid)]=float(rmdAttday['Leave_'+str(exid)])
#				except Exception,ee:
#					rmdAttday['Leave_'+str(exid)]=0
#				ve=rmdAttday['Leave_'+str(exid)]
#				rmdAttday['Leave_'+str(exid)]=NormalAttValue(ve,AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['MinUnit'],
#									 AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['RemaindProc'])
#		if AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['RemaindCount']==1:
#			try:
#				rmdAttday['Leave']=float(rmdAttday['Leave'])
#			except Exception,ee:
#				rmdAttday['Leave']=0
#			ve=rmdAttday['Leave']
#			rmdAttday['Leave']=NormalAttValue(ve,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['MinUnit'],
#					 AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['RemaindProc'])
#		re.append(rmdAttday.copy())
#	Result['datas']=re
#	Result['disableCols']=[]
#	return Result
#



def getemployee_finger(request,isContainedChild,deptIDs,userIDs,st,et,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1

	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	sidx=""
	ot=[]
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	if sidx:
		ot=sidx.split(',')
	septag='1'
	if request.GET.has_key("SEP"):
		septag=request.GET.get('SEP', '1')
	
	if q!='':
		if request.user.is_superuser or request.user.is_alldept:
			objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains = q)).order_by(*ot)
		else:
			deptids=userDeptList(request.user)
			deptids.sort()
			id=deptids[0]
			dept=department.objByID(id)
			if dept.parent==0:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains = q)).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains = q)).order_by(*ot)
	else:
		if len(deptIDs)>0:
			if isContainedChild=='1':
				dept=department.objByID(deptIDs)
				if request.user.is_superuser or request.user.is_alldept:
					dptids=getAllAuthChildDept(dept.DeptID,request)
					emps=employee.objects.filter(DeptID__in=dptids,OffDuty__lt=1).exclude(DelTag=1).values('id')
				else:
					dids=[]
					deptids_Auth=userDeptList(request.user) #获得用户的授权部门
					deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
					for i in deptids_Subordinate:
						if i in deptids_Auth:
							dids.append(i)
					emps=employee.objects.filter(DeptID__in=dids,OffDuty__lt=1).exclude(DelTag=1).values('id')
			else:
				emps=employee.objects.filter(DeptID__in=deptIDs,OffDuty__lt=1).exclude(DelTag=1).values('id')
		else:
			if request.user.is_superuser or request.user.is_alldept:
				emps=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).values('id')
			else:
				deptids=userDeptList(request.user) #获得用户的授权部门
				emps=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).values('id')
				

		fpemps=BioData.objects.filter(UserID__in=emps,bio_type=bioFinger).values('UserID')
		faceemps=BioData.objects.filter(UserID__in=emps,bio_type=bioFace).values('UserID')
		
		if septag == '0':# 未采集
			objs=employee.objects.filter(id__in=emps).exclude(id__in=fpemps).order_by(*ot)
		elif septag =='2':#采集
			objs=employee.objects.filter(id__in=fpemps).order_by(*ot)

		elif septag == '4':# 未采集面部
			objs=employee.objects.filter(id__in=emps).exclude(id__in=faceemps).order_by(*ot)
		elif septag =='3':#采集面部
			objs=employee.objects.filter(id__in=faceemps).order_by(*ot)
		elif septag == '5':# 有卡
			objs=employee.objects.filter(id__in=emps,Card__isnull=False).order_by(*ot)
		elif septag =='6':#无卡
			objs=employee.objects.filter(id__in=emps,Card__isnull=True).order_by(*ot)



		elif septag == '1':
			objs=employee.objects.filter(id__in=emps).order_by(*ot)		




		
	p=Paginator(objs, limit)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	objs=pp.object_list
	re=[]
	Result={}
	Result['datas']=re
	for t in objs:
		d={}
		d['id']=t.id
		d['DeptNumber']=t.Dept().DeptNumber
		d['DeptName']=t.Dept().DeptName
		d['pin']=t.PIN
		d['Workcode'] = t.Workcode
		d['name']=t.EName or ''
		d['card']=t.Card or ''
		#f_count=fptemp.objects.filter(UserID=t.id).count()
		d['is_register']=u'否'
		d['is_register_face']=u'否'
		d['is_register_card']=u'否'
		if t.fpCount()>0:
			d['is_register']=u'是'
		if t.faceCount()>0:	
			d['is_register_face']=u'是'
		if t.Card:
			d['is_register_card']=u'是'
		#if t.SEP==2:
		#	d['is_register']=u'是'
		re.append(d.copy())
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

def getdevice_assignment(request,isContainedChild,deptIDs,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
		
	if q!='':
		dept=department.objects.filter(Q(DeptNumber=q)|Q(DeptName=q)).order_by('DeptNumber')
		if request.user.is_superuser or request.user.is_alldept:
			deptlist=[]
		else:
			deptlist=getAllAuthChildDept(dept.DeptID,request)
		deptids=[]
		for d in dept:
			if d.DeptID not in deptlist:
				deptids.append(d.DeptID)
		
	elif len(deptIDs)>0:
		if isContainedChild=='1':
			dept=department.objByID(deptIDs)
			if request.user.is_superuser or request.user.is_alldept:
				deptids=getAllAuthChildDept(dept.DeptID,request)
				
			else:
				deptids=[]
				deptids_Auth=userDeptList(request.user) #获得用户的授权部门
				deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
				for i in deptids_Subordinate:
					if i in deptids_Auth:
						deptids.append(i)
		else:
			deptids=deptIDs
	else:
		if request.user.is_superuser or request.user.is_alldept:
			deptids=list(department.objects.all().exclude(DelTag=1).values_list('DeptID',flat=True).order_by('DeptNumber'))
		else:
			deptids=userDeptList(request.user) 
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	if offset==0:offset=1
	#limit= int(request.POST.get('rows', 30))
	re=[]
	Result={}
	Result['datas']=re
	iCount=len(deptids)
	deptids=deptids[(offset-1)*limit:offset*limit]
	for t in deptids:
		sns=getDeviceListByDept(t)
		dept=department.objByID(t)
		d={}
		d['DeptNumber']=dept.DeptNumber
		d['DeptName']=dept.DeptName
		d['Devices']=len(sns)
		d['DeviceSN']=''
		if sns:
			for sn in sns:
				d['DeviceSN']+=sn+' '
		re.append(d.copy())
		#iCount=iCount+1
	page_count =int(ceil(iCount/float(limit)))
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

def getdepartment_finger(request,isContainedChild,deptIDs):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	q=request.GET.get('q','')
	q=unquote(q)
	if q!='':
		dept=department.objects.filter(Q(DeptNumber=q)|Q(DeptName=q)).order_by('DeptID')
		if request.user.is_superuser or request.user.is_alldept:
			deptlist=[]
		else:
			deptlist=getAllAuthChildDept(dept.DeptID,request)
		deptids=[]
		for d in dept:
			if d.DeptID not in deptlist:
				deptids.append(d.DeptID)
	else:			
		if len(deptIDs)>0:
			if isContainedChild=='1':
				dept=department.objByID(deptIDs)
				if request.user.is_superuser or request.user.is_alldept:
					deptids=getAllAuthChildDept(dept.DeptID,request)
					
				else:
					deptids=[]
					deptids_Auth=userDeptList(request.user) #获得用户的授权部门
					deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
					for i in deptids_Subordinate:
						if i in deptids_Auth:
							deptids.append(i)
			else:
				deptids=department.objects.filter(DeptID__in=deptIDs).exclude(DelTag=1).values_list('DeptID',flat=True).order_by('DeptID')
		else:
			if request.user.is_superuser or request.user.is_alldept:
				deptids=department.objects.exclude(DelTag=1).values_list('DeptID',flat=True).order_by('DeptID')
			else:
				deptids=userDeptList(request.user)
				deptids=department.objects.filter(DeptID__in=deptids).exclude(DelTag=1).values_list('DeptID',flat=True).order_by('DeptID')
				
				
	try:
		offset = int(request.POST.get('page', 1))
		if offset==0:
			offset=1
	except:
		offset=1
	#limit= int(request.POST.get('rows', 30))
	re=[]
	Result={}
	Result['datas']=re
	iCount=len(deptids)
	deptids=deptids[(offset-1)*limit:offset*limit]
	for t in deptids:
		dept=department.objByID(t)
		fpemp=BioData.objects.values('UserID').annotate().filter(UserID__DeptID__exact=t,UserID__OffDuty=0,UserID__DelTag=0,bio_type=bioFinger).distinct()
		faceemp=BioData.objects.values('UserID').annotate().filter(UserID__DeptID__exact=t,UserID__OffDuty=0,UserID__DelTag=0,bio_type=bioFace).distinct()
		d={}
		d['DeptNumber']=dept.DeptNumber
		d['DeptName']=dept.DeptName
		d['count']=dept.empCount()
		d['finger_count']=len(fpemp)
		d['face_count']=len(faceemp)
		if d['count']==0:
			d['rate']="%.1f"%0
		else:
			rate = float(d['finger_count']) / float(d['count'])   
			d['rate'] ="%.1f" %(rate * 100)
			rate = float(d['face_count']) / float(d['count'])   
			d['face_rate'] ="%.1f" %(rate * 100)
			
			
		re.append(d.copy())
		#iCount=iCount+1
	page_count =int(ceil(iCount/float(limit)))
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

def getdaily_devices(request,isContainedChild,deptIDs,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	if q!='':
		dept=department.objects.filter(Q(DeptNumber=q)|Q(DeptName=q)).order_by('DeptID')
		if request.user.is_superuser or request.user.is_alldept:
			deptlist=[]
		else:
			deptlist=getAllAuthChildDept(dept.DeptID,request)
		deptids=[]
		for d in dept:
			if d.DeptID not in deptlist:
				deptids.append(d.DeptID)
				
	else:
		if len(deptIDs)>0:
			if isContainedChild=='1':
				dept=department.objByID(deptIDs)
				if request.user.is_superuser or request.user.is_alldept:
					deptids=getAllAuthChildDept(dept.DeptID,request)
				else:
					deptids=[]
					deptids_Auth=userDeptList(request.user) #获得用户的授权部门
					deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
					for i in deptids_Subordinate:
						if i in deptids_Auth:
							deptids.append(i)
					#objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).order_by(*ot)
			else:
				deptids=deptIDs
		else:
			if request.user.is_superuser or request.user.is_alldept:
				deptids=list(department.objects.all().exclude(DelTag=1).values_list('DeptID',flat=True).order_by('DeptID'))
			else:
				deptids=userDeptList(request.user) 
				



	try:
		offset = int(request.POST.get('page', 1))
		if offset==0:
			offset=1
	except:
		offset=1
	checkDate=request.GET.get('checkDate','')
	et = checkDate + " 23:59:59"
	st = checkDate + " 00:00:00"
	#limit= int(request.POST.get('rows', 30))
	re=[]
	Result={}
	Result['datas']=re
	iCount=len(deptids)
	deptids=deptids[(offset-1)*limit:offset*limit]
	for t in deptids:
		dept=department.objByID(t)
		sns=getDeviceListByDept(t)
		#fpemp=fptemp.objects.values('UserID').annotate().filter(UserID__DeptID__exact=t,DelTag=0)
		snlist=transactions.objects.values('SN').annotate().filter(SN__in=sns,TTime__gte=st,TTime__lt=et).filter(Q(purpose=9)|Q(purpose=None)).distinct()
		d={}
		d['DeptNumber']=dept.DeptNumber
		d['DeptName']=dept.DeptName
		d['device_on']=len(snlist)
		d['device_count']=len(sns)
		if d['device_count']==0:
			d['rate']="%.1f"%0
		else:
			rate = float(d['device_on']) / float(d['device_count'])   
			d['rate'] ="%.1f" %((rate>1 and 1 or rate) * 100)
		re.append(d.copy())
		#iCount=iCount+1
	page_count =int(ceil(iCount/float(limit)))
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result


#人员快捷报表查询
def getihrreversedetail(request,isContainedChild,deptIDs,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1

	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	sidx=""
	ot=[]
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	if sidx:
		ot=sidx.split(',')
	reversetag='1'
	if request.GET.has_key("reversetag"):
		reversetag=request.GET.get('reversetag', '0')
	
	if q!='':
		if request.user.is_superuser or request.user.is_alldept:
			objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q))
		else:
			deptids=userDeptList(request.user)
			deptids.sort()
			id=deptids[0]
			dept=department.objByID(id)
			if dept.parent==0:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q)).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q)).order_by(*ot)
	else:
		if len(deptIDs)>0:
			if isContainedChild=='1':
				dept=department.objByID(deptIDs)
				if request.user.is_superuser or request.user.is_alldept:
					dptids=getAllAuthChildDept(dept.DeptID,request)
					emps=employee.objects.filter(DeptID__in=dptids,OffDuty__lt=1).exclude(DelTag=1).values('id')
				else:
					dids=[]
					deptids_Auth=userDeptList(request.user) #获得用户的授权部门
					deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
					for i in deptids_Subordinate:
						if i in deptids_Auth:
							dids.append(i)
					emps=employee.objects.filter(DeptID__in=dids,OffDuty__lt=1).exclude(DelTag=1)
			else:
				emps=employee.objects.filter(DeptID__in=deptIDs,OffDuty__lt=1).exclude(DelTag=1)
			if reversetag == '1':# 未采集指纹
				objs=emps.extra(where=['UserID NOT IN (%s)'%('select userid from template')]).order_by(*ot)
			elif reversetag == '2': # 无面部指纹
				objs=emps.extra(where=['UserID NOT IN (%s)'%('select userid from facetemplate')]).order_by(*ot)
			elif reversetag == '3': # 今天未出勤
				now=datetime.datetime.now()
				trans=transactions.objects.filter(UserID__in=emps.values('id'),TTime__year=now.year,TTime__month=now.month,TTime__day=now.day).values_list("UserID").order_by(*ot)
				objs=emps.exclude(id__in=trans).order_by(*ot)
			elif reversetag == '4': # 昨天未出勤
				yestoday=datetime.datetime.now()-datetime.timedelta(days=1)
				trans=transactions.objects.filter(UserID__in=emps.values('id'),TTime__year=yestoday.year,TTime__month=yestoday.month,TTime__day=yestoday.day).values_list("UserID")
				objs=emps.exclude(id__in=trans).order_by(*ot)
			elif reversetag == '5': # 本周未出勤
				now=datetime.datetime.now()
				now=datetime.datetime(now.year,now.month,now.day,0,0,0)
				start=now-datetime.timedelta(days=now.weekday())
				end=now+datetime.timedelta(days=7-now.weekday())
				trans=transactions.objects.filter(UserID__in=emps.values('id'),TTime__gte=start,TTime__lt=end).values_list("UserID")
				objs=emps.exclude(id__in=trans).order_by(*ot)
			elif reversetag == '6': # 本月未出勤
				now=datetime.datetime.now()
				trans=transactions.objects.filter(UserID__in=emps.values('id'),TTime__year=now.year,TTime__month=now.month).values_list("UserID")
				objs=emps.exclude(id__in=trans).order_by(*ot)
			elif reversetag == '0':
				
				objs=emps.order_by(*ot)

		else:
			Result={}
			Result['item_count']=0
			Result['page']=1
			Result['limit']=30
			Result['from']=1
			Result['page_count']=0
			Result['datas']=[]
			return Result

		
		
	p=Paginator(objs, limit)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	objs=pp.object_list
	re=[]
	Result={}
	Result['datas']=re
	for o in objs:
		t=employee.objByID(o["id"])
		d={}
		d['id']=t.id
		d['DeptNumber']=t.Dept().DeptNumber
		d['DeptName']=t.Dept().DeptName
		d['pin']=t.PIN
		d['name']=t.EName
		re.append(d.copy())
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

def getUser_speday(request):
	dataModel=USER_SPEDAY
	jqGrid=JqGrid(request,datamodel=dataModel)
	items=jqGrid.get_items()   #not Paged
	cc=jqGrid.get_json(items)
	tmpFile=dataModel.__name__+'_list.js'
	t=loader.get_template(tmpFile)
	cc['can_change']=False
	try:
	    rows=t.render(RequestContext(request, cc))
	except Exception,e:
	    rows='[]'
	    pass
	Result={}
	Result['item_count']=cc['records']
	Result['page']=cc['page']
	Result['page_count']=cc['total']
	Result['datas']=loads(rows)
	return Result
	
	
	
	#iCount=0
	#try:
	#	offset = int(request.POST.get('page', 1))
	#except:
	#	offset=1
	#
	#limit= int(request.POST.get('rows', 0))
	#if limit==0:
	#	limit= int(request.GET.get('rows', 30))
	#sidx=""
	#ot=[]
	#if request.GET.has_key('sidx'):
	#	sidx = request.GET.get('sidx','')
	#else:
	#	sidx = request.POST.get('sidx','')
	#if sidx:
	#	ot=sidx.split(',')
	#if q!='':
	#	if request.user.is_superuser or request.user.is_alldept:
	#		objs=employee.objects.filter(OffDuty__lt=1,DelTag=0).filter(Q(PIN=q)|Q(EName=q))
	#	else:
	#		deptids=userDeptList(request.user)
	#		deptids.sort()
	#		id=deptids[0]
	#		dept=department.objByID(id)
	#		if dept.parent==0:
	#			objs=employee.objects.filter(OffDuty__lt=1,DelTag=0).filter(Q(PIN=q)|Q(EName=q)).order_by(*ot)
	#		else:
	#			objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1,DelTag=0).filter(Q(PIN=q)|Q(EName=q)).order_by(*ot)
	#else:
	#	if len(deptIDs)>0:
	#		if isContainedChild=='1':
	#			dept=department.objByID(deptIDs)
	#			if request.user.is_superuser or request.user.is_alldept:
	#				dptids=getAllAuthChildDept(dept.DeptID,request)
	#				emps=employee.objects.filter(DeptID__in=dptids,OffDuty__lt=1,DelTag=0).values('id')
	#			else:
	#				dids=[]
	#				deptids_Auth=userDeptList(request.user) #获得用户的授权部门
	#				deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
	#				for i in deptids_Subordinate:
	#					if i in deptids_Auth:
	#						dids.append(i)
	#				emps=employee.objects.filter(DeptID__in=dids,OffDuty__lt=1,DelTag=0).values('id')
	#		else:
	#			emps=employee.objects.filter(DeptID__in=deptIDs,OffDuty__lt=1,DelTag=0).values('id')
	#
	#	else:
	#		Result={}
	#		Result['item_count']=0
	#		Result['page']=1
	#		Result['limit']=30
	#		Result['from']=1
	#		Result['page_count']=0
	#		Result['datas']=[]
	#		return Result
	#objs=USER_SPEDAY.objects.filter(UserID__in=emps,State=2)
	#p=Paginator(objs, limit)
	#iCount=p.count
	#if iCount<(offset-1)*limit:
	#	offset=1
	#page_count=p.num_pages
	#pp=p.page(offset)
	#objs=pp.object_list
	#re=[]
	#Result={}
	#Result['datas']=re
	#LClass=GetLeaveClassesEx(1)
	#for t in objs:
	#	d={}
	#	d['id']=t.id
	#	#d['UserID']=t.UserID
	#	d['DeptID']=t.employee().Dept().DeptNumber
	#	d['DeptName']=t.employee().Dept().DeptName
	#
	#	d['PIN']=t.employee().PIN
	#	d['EName']=t.employee().EName
	#	d['StartSpecDay']=t.StartSpecDay
	#	d['EndSpecDay']=t.EndSpecDay
	#	for s in  LClass:
	#		if t.DateID==s["LeaveId"]:
	#			d['DateID']= s["LeaveName"]
	#	d['process']=t.process
	#	d['YUANYING']=t.YUANYING
	#	d['ApplyDate']=t.ApplyDate
	#	d['State']='已通过'
	#	d['clearance']=t.clearance
	#	d['roleid']=t.roleid
	#	
	#	re.append(d.copy())
	#if offset>page_count:offset=page_count
	#item_count =iCount
	#Result['item_count']=item_count
	#Result['page']=offset
	#Result['limit']=limit
	#Result['from']=(offset-1)*limit+1
	#Result['page_count']=page_count
	#Result['datas']=re
	#return Result



#人员出勤异常详情
def getExcepDaily(request):
	dataModel=AttException
	jqGrid=JqGrid(request,datamodel=dataModel)
	items=jqGrid.get_items()   #not Paged
	cc=jqGrid.get_json(items)
	tmpFile=dataModel.__name__+'_list.js'
	t=loader.get_template(tmpFile)
	cc['can_change']=False
	try:
	    rows=t.render(RequestContext(request, cc))
	except Exception,e:
	    rows='[]'
	    pass
	Result={}
	Result['item_count']=cc['records']
	Result['page']=cc['page']
	Result['page_count']=cc['total']
	Result['datas']=loads(rows)
	return Result
	
	
	
	
	
	
	#iCount=0
	#try:
	#	offset = int(request.POST.get('page', 1))
	#except:
	#	offset=1
	#
	#limit= int(request.POST.get('rows', 0))
	#if limit==0:
	#	limit= int(request.GET.get('rows', 30))
	#sidx=""
	#ot=[]
	#if request.GET.has_key('sidx'):
	#	sidx = request.GET.get('sidx','')
	#else:
	#	sidx = request.POST.get('sidx','')
	#if sidx:
	#	ot=sidx.split(',')
	#if q!='':
	#	if request.user.is_superuser or request.user.is_alldept:
	#		objs=employee.objects.filter(OffDuty__lt=1,DelTag=0).filter(Q(PIN=q)|Q(EName=q))
	#	else:
	#		deptids=userDeptList(request.user)
	#		deptids.sort()
	#		id=deptids[0]
	#		dept=department.objByID(id)
	#		if dept.parent==0:
	#			objs=employee.objects.filter(OffDuty__lt=1,DelTag=0).filter(Q(PIN=q)|Q(EName=q)).order_by(*ot)
	#		else:
	#			objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1,DelTag=0).filter(Q(PIN=q)|Q(EName=q)).order_by(*ot)
	#else:
	#	if len(deptIDs)>0:
	#		if isContainedChild=='1':
	#			dept=department.objByID(deptIDs)
	#			if request.user.is_superuser or request.user.is_alldept:
	#				dptids=getAllAuthChildDept(dept.DeptID,request)
	#				emps=employee.objects.filter(DeptID__in=dptids,OffDuty__lt=1,DelTag=0).values('id')
	#			else:
	#				dids=[]
	#				deptids_Auth=userDeptList(request.user) #获得用户的授权部门
	#				deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
	#				for i in deptids_Subordinate:
	#					if i in deptids_Auth:
	#						dids.append(i)
	#				emps=employee.objects.filter(DeptID__in=dids,OffDuty__lt=1,DelTag=0).values('id')
	#		else:
	#			emps=employee.objects.filter(DeptID__in=deptIDs,OffDuty__lt=1,DelTag=0).values('id')
	#
	#	else:
	#		Result={}
	#		Result['item_count']=0
	#		Result['page']=1
	#		Result['limit']=30
	#		Result['from']=1
	#		Result['page_count']=0
	#		Result['datas']=[]
	#		return Result
	#objs=AttException.objects.filter(UserID__in=emps)
	#p=Paginator(objs, limit)
	#iCount=p.count
	#if iCount<(offset-1)*limit:
	#	offset=1
	#page_count=p.num_pages
	#pp=p.page(offset)
	#objs=pp.object_list
	#re=[]
	#Result={}
	#Result['datas']=re
	#for t in objs:
	#	d={}
	#	d['UserID']=t.id
	#	d['DeptName']=t.employee().Dept().DeptName
	#	d['PIN']=t.employee().PIN
	#	d['EName']=t.employee().EName
	#	d['AttDate']=shortDate4(t.AttDate)
	#	d['StartTime']=onlyTime(t.StartTime)
	#	d['EndTime']=onlyTime(t.EndTime)
	#	d['ExceptionID']=ExceptionStr(t.ExceptionID)
	#	d['TimeLong']=t.TimeLong
	#	d['InScopeTime']=t.InScopeTime
	#	re.append(d.copy())
	#if offset>page_count:offset=page_count
	#item_count =iCount
	#Result['item_count']=item_count
	#Result['page']=offset
	#Result['limit']=limit
	#Result['from']=(offset-1)*limit+1
	#Result['page_count']=page_count
	#Result['datas']=re
	#return Result

#人员每日出勤统计表
def getdailycalcReport(request,isContainedChild,deptIDs,userIDs,st,et,q):
	#deptIDs=request.GET.get('deptIDs',"")
	#userIDs=request.GET.get('UserIDs',"")
	#st=request.GET.get('startDate','')
	#et=request.GET.get('endDate','')
	#st=datetime.datetime.strptime(st,'%Y-%m-%d')
	#et=datetime.datetime.strptime(et,'%Y-%m-%d')
	Result=CalcReportItem(request,deptIDs,userIDs,st,et,1)
	return Result

#人员出勤汇总表
def getcalcReport(request,isContainedChild,deptIDs,userIDs,st,et,q):
	#deptIDs=request.GET.get('deptIDs',"")
	#userIDs=request.GET.get('UserIDs',"")
	#st=request.GET.get('startDate','')
	#et=request.GET.get('endDate','')
	#st=datetime.datetime.strptime(st,'%Y-%m-%d')
	#et=datetime.datetime.strptime(et,'%Y-%m-%d')
	Result=CalcReportItem(request,deptIDs,userIDs,st,et,0)
	return Result

##部门统计汇总表
def getdepartment_report(request,isContainChild,deptIDs,userIDs,st,et,q):
	result=departmentreportItem(request,deptIDs,isContainChild,st,et)	
	return result

#	
#	if type(deptIDs)==list:
#		deptidlist=deptIDs
#		deptIDs=','.join(deptIDs)
#	elif deptIDs == '':
#		if request.user.is_superuser or request.user.is_alldept:
#			deptidlist=list(department.objects.all().exclude(DelTag=1).values_list('DeptID',flat=True).order_by('DeptNumber'))
#		else:
#			deptidlist=userDeptList(request.user) 		
#	else:
#		deptidlist=[int(i) for i in deptIDs.split(',')]
#		
#		
#	depts=[]
#	if isContainChild=="1":   #是否包含下级部门
#		for d in deptidlist:#支持选择多部门
#			if int(d) not in depts:
#				depts+=getAllAuthChildDept(d,request)
#	else:
#		depts=copy.deepcopy(deptidlist)
#	try:
#		offset = int(request.POST.get('page', 1))
#	except:
#		offset=1
#	limit = 10000#int(request.POST.get('rows', 30))
#	r={}
#	r['item_count']=len(depts)
#	page_count =int(ceil(len(depts)/float(limit))) 
#	depts=depts[(offset-1)*limit:offset*limit]
#	r['page_count']=page_count
#	r['page']=offset
#	r['limit']=limit
#	lx=[]
#	rl=CalcReportItem(request,deptIDs,'',st,et,0,100000)
#	dets={}
#	for t in rl['datas']:
#		if not t['deptid_id']:
#			continue
#		if t['duty']:
#			try:
#				dets['%s_duty'%t['deptid_id']]+=float(t['duty'])
#			except:
#				dets['%s_duty'%t['deptid_id']]=float(t['duty'])
#		if t['realduty']:
#			try:
#				dets['%s_realduty'%t['deptid_id']]+=float(t['realduty'])
#			except:
#				dets['%s_realduty'%t['deptid_id']]=float(t['realduty'])
#		if t['absent']:
#			try:
#				dets['%s_Absent'%t['deptid_id']]+=float(t['absent'])
#			except:
#				dets['%s_Absent'%t['deptid_id']]=float(t['absent'])
#		if t['late']:
#			try:
#				dets['%s_Late'%t['deptid_id']]+=float(t['late'])
#			except:
#				dets['%s_Late'%t['deptid_id']]=float(t['late'])
#		if t['early']:
#			try:
#				dets['%s_Early'%t['deptid_id']]+=float(t['early'])
#			except:
#				dets['%s_Early'%t['deptid_id']]=float(t['early'])
#		if t['overtime']:
#			try:
#				dets['%s_OverTime'%t['deptid_id']]+=float(t['overtime'])
#			except:
#				dets['%s_OverTime'%t['deptid_id']]=float(t['overtime'])
#		if t['noin']:
#			try:
#				dets['%s_noin'%t['deptid_id']]+=float(t['noin'])
#			except:
#				dets['%s_noin'%t['deptid_id']]=float(t['noin'])
#		if t['noout']:
#			try:
#				dets['%s_noout'%t['deptid_id']]+=float(t['noout'])
#			except:
#				dets['%s_noout'%t['deptid_id']]=float(t['noout'])
#		if t['dutyinout']:
#			try:
#				dets['%s_dutyinout'%t['deptid_id']]+=float(t['dutyinout'])
#			except:
#				dets['%s_dutyinout'%t['deptid_id']]=float(t['dutyinout'])
#		if t['worktime_de']:
#			try:
#				dets['%s_worktime'%t['deptid_id']]+=float(t['worktime_de'])
#			except:
#				dets['%s_worktime'%t['deptid_id']]=float(t['worktime_de'])
#		if t['Leave']:
#			try:
#				dets['%s_Leave'%t['deptid_id']]+=float(t['Leave'])
#			except:
#				dets['%s_Leave'%t['deptid_id']]=float(t['Leave'])
#		LClasses1=GetLeaveClasses(2)
#		for t1 in LClasses1:
#			fName='Leave_'+str(t1['LeaveId'])
#			if t[fName]:
#				try:
#					dets['%s_%s'%(t['deptid_id'],fName)]+=float(t[fName])
#				except:
#					dets['%s_%s'%(t['deptid_id'],fName)]=float(t[fName])
#	for d in depts:
#		ll={}
#		ll['dept']=department.objByID(d).DeptName
#		ll['count']=employee.objects.filter(DeptID=d,OffDuty=0).count()
#		try:
#			ll['duty']=dets['%s_duty'%d]
#		except:
#			ll['duty']=''
#		try:
#			ll['realduty']=dets['%s_realduty'%d]
#		except:
#			ll['realduty']=''
#		try:
#			ll['absent']=dets['%s_Absent'%d]
#		except:
#			ll['absent']=''
#		try:
#			ll['late']=dets['%s_Late'%d]
#		except:
#			ll['late']=''
#		try:
#			ll['early']=dets['%s_Early'%d]
#		except:
#			ll['early']=''
#		try:
#			ll['timeout']=dets['%s_OverTime'%d]
#		except:
#			ll['timeout']=''
#		try:
#			ll['noin']=dets['%s_noin'%d]
#		except:
#			ll['noin']=''
#		try:
#			ll['noout']=dets['%s_noout'%d]
#		except:
#			ll['noout']=''
#		try:
#			ll['yingqian']=dets['%s_dutyinout'%d]
#		except:
#			ll['yingqian']=''
#		try:
#			ll['shijian']=formatdTime(dets['%s_worktime'%d])
#		except:
#			ll['shijian']=''
#		try:
#			ll['speday']=dets['%s_Leave'%d]
#		except:
#			ll['speday']=''
#		for t in LClasses1:
#			fName='Leave_'+str(t['LeaveId'])
#			if fName=='Leave_1':
#				try:
#					ll['gongchu']=dets['%s_%s'%(d,str(fName))]
#				except:
#					ll['gongchu']=''
#			else:
#				try:
#					ll[fName]=dets['%s_%s'%(d,str(fName))]
#				except:
#					ll[fName]=''
#		if ll['realduty'] and ll['duty'] and ll['duty']!=0:
#			ll['chuqinlv']='%.1f'%(ll['realduty']*100/ll['duty'])
#		lx.append(ll)
#	r['datas']=lx
#	return r
#
#
#      

#年休假标准详情
def getannual_leave(request,isContainedChild,deptIDs,userIDs,st,et,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	sidx=""
	ot=[]
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	if sidx:
		if request.method=='GET':
			sord = request.GET.get('sord')
		else:
			sord = request.POST.get('sord')
		order_by = '%s%s' % (sord == 'desc' and '-' or '', sidx)
		if sord=='-' or sord=='':
			order_by ='%s' % (sidx)
		ot=order_by.split(',')
	if q!='':
		q=unquote(q)
		if request.user.is_superuser or request.user.is_alldept:
			objs=employee.objects.filter(OffDuty__lt=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
		else:
			deptids=userDeptList(request.user)
			deptids.sort()
			id=deptids[0]
			dept=department.objByID(id)
			if dept.parent==0:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
	else:
		if len(userIDs)>0:
			userIDs=userIDs.split(",")
			objs=employee.objects.filter(id__in=userIDs,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)	
		elif len(deptIDs)>0:
			if isContainedChild=='1':
				dept=department.objByID(deptIDs)
				if request.user.is_superuser or request.user.is_alldept:
					dptids=getAllAuthChildDept(dept.DeptID,request)
					objs=employee.objects.filter(DeptID__in=dptids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
				else:
					dids=[]
					deptids_Auth=userDeptList(request.user) #获得用户的授权部门
					deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
					for i in deptids_Subordinate:
						if i in deptids_Auth:
							dids.append(i)
					objs=employee.objects.filter(DeptID__in=dids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID=deptIDs,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)

		else:
			if request.user.is_superuser or request.user.is_alldept:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
			else:
				deptids=userDeptList(request.user)
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)

	p=Paginator(objs, limit,allow_empty_first_page=True)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	#ids=pp.object_list.values_list('id', flat=True)
	re=[]
	Result={}
	for p in pp.object_list:
		d={}
		d['id']=p.id
		d['DeptID']=p.Dept().DeptNumber
		d['DeptName']=p.Dept().DeptName
		d['PIN']=p.PIN
		d['Workcode'] = p.Workcode
		d['EName']=p.EName or ''
		d['Birthday']=shortDate4(p.Birthday)
		d['Hiredday']=shortDate4(p.Hiredday)
		d['WorkAge']=getWorkAge(p.id,request)
		d['annual_std']=getannual_fading(p.id,request)
		d['annual_ent']=getannual_gongsi(p.id,request)
		re.append(d.copy())
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result
		
#会议--人员签到情况报表
def getmeetingsign(request,deptIDs,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	
	objs=[]
	if q!='':
		q=unquote(q)
		if request.user.is_superuser or request.user.is_alldept:
			objs=employee.objects.filter(OffDuty__lt=1).filter(Q(PIN=q)|Q(EName=q)).values_list('id', flat=True)
		else:
			deptids=userDeptList(request.user)
			deptids.sort()
			id=deptids[0]
			dept=department.objByID(id)
			if dept.parent==0:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q)).values_list('id', flat=True)
			else:
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q)).values_list('id', flat=True)
		if objs:
			pass
		else:
			objs=[-1]
	lx=[]
	if deptIDs=='0' or deptIDs=='':
		deptIDs=Meet.objects.all().values_list('MeetID', flat=True)
		for d in deptIDs:
			lx.extend(getMeetNum(d,objs,1))
	else:
		lx=getMeetNum(deptIDs,objs,1)
	p=Paginator(lx, limit,allow_empty_first_page=True)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	re=[]
	Result={}
	for p in pp.object_list:
		d={}
		emp=employee.objByID(p['userid'])
		note=u""
		d['DeptName']=emp.Dept().DeptName
		d['pin']=emp.PIN
		d['name']=emp.EName or ''
		d['checkin']=p['st']
		d['checkout']=p['et']
		d['meetname']=p['meetname']
		try:
			if p['late']>0:
				note+=u'迟到'
		except:
			pass
		try:
			if p['early']>0:
				if note!='':
					note+=u",早退"
				else:
					note=u"早退"
		except:
			pass
		try:
			if p['lid']>0:
				if note!='':
					note+=u",请假"
				else:
					note=u"请假"
		except:
			pass
		d['note']=note
		re.append(d.copy())
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result
	
		
#会议--人员未签到情况报表
def getmeetingnotsign(request,deptIDs,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	
	objs=[]
	if q!='':
		q=unquote(q)
		if request.user.is_superuser or request.user.is_alldept:
			objs=employee.objects.filter(OffDuty__lt=1).filter(Q(PIN=q)|Q(EName=q)).values_list('id', flat=True)
		else:
			deptids=userDeptList(request.user)
			deptids.sort()
			id=deptids[0]
			dept=department.objByID(id)
			if dept.parent==0:
				objs=employee.objects.filter(OffDuty__lt=1,DelTag=0).filter(Q(PIN=q)|Q(EName=q)).values_list('id', flat=True)
			else:
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1,DelTag=0).filter(Q(PIN=q)|Q(EName=q)).values_list('id', flat=True)
		if objs:
			pass
		else:
			objs=[-1]
	lx=[]
	if deptIDs=='0' or deptIDs=='':
		deptIDs=Meet.objects.all().values_list('MeetID', flat=True)
		for d in deptIDs:
			lx.extend(getMeetNum(d,objs,2))
	else:
		lx=getMeetNum(deptIDs,objs,2)
	p=Paginator(lx, limit,allow_empty_first_page=True)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	re=[]
	Result={}
	for p in pp.object_list:
		d={}
		emp=employee.objByID(p['userid'])
		note=u""
		d['DeptName']=emp.Dept().DeptName
		d['pin']=emp.PIN
		d['name']=emp.EName or ''
		d['meetname']=p['meetname']
		re.append(d.copy())
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result
	
		
#会议--会议签到情况报表
def getmeetreport(request,deptIDs,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	objs=[]
	Result={}
	re=[]
	lx=[]
	if deptIDs=='0' or deptIDs=='':
		deptIDs=Meet.objects.filter(DelTag=0).values_list('MeetID', flat=True)
		for d in deptIDs:
			lx=getMeetNum(d,objs,0)
			duty=0
			onduty=0
			late=0
			early=0
			speday=0
			absent=0
			for l in lx:
				try:
					if l['absent']>0:
						absent+=1
				except:
					pass
				duty+=1
				try:
					if l['st']!='':
						onduty+=1
				except:
					pass
				try:
					if l['late']>0:
						late+=1
				except:
					pass
				try:
					if l['early']>0:
						early+=1
				except:
					pass
				try:
					if l['lid']>0:
						speday+=1
				except:
					pass
			meet=Meet.objByID(d)
		
			d={}
			note=u""
			d['MeetID']=meet.MeetID
			d['conferenceTitle']=meet.conferenceTitle
			location=meet.LocationID
			if location:
				d['Location']=location.roomName
			else:
				d['Location']=''
			d['Starttime']=meet.Starttime
			d['Endtime']=meet.Endtime
			d['duty']=duty
			d['onduty']=onduty
			d['late']=late
			d['early']=early
			d['speday']=speday
			d['absent']=absent
			if duty>0:
				d['rate']=str(int(float(onduty)*100/float(duty)))+'%'
			else:
				d['rate']='0%'
			re.append(d.copy())		
			
	else:
		lx=getMeetNum(deptIDs,objs,0)
		duty=0
		onduty=0
		late=0
		early=0
		speday=0
		absent=0
		for l in lx:
			try:
				if l['absent']>0:
					absent+=1
			except:
				pass
			duty+=1
			try:
				if l['st']!='':
					onduty+=1
			except:
				pass
			try:
				if l['late']>0:
					late+=1
			except:
				pass
			try:
				if l['early']>0:
					early+=1
			except:
				pass
			try:
				if l['lid']>0:
					speday+=1
			except:
				pass
		meet=Meet.objByID(deptIDs)
	
		d={}
		note=u""
		d['MeetID']=meet.MeetID
		d['conferenceTitle']=meet.conferenceTitle
		location=meet.LocationID
		if location:
			d['Location']=location.roomName
		else:
			d['Location']=''
		d['Starttime']=meet.Starttime
		d['Endtime']=meet.Endtime
		d['duty']=duty
		d['onduty']=onduty
		d['late']=late
		d['early']=early
		d['speday']=speday
		d['absent']=absent
		if duty>0:
			d['rate']=str(int(float(onduty)*100/float(duty)))+'%'
		else:
			d['rate']='0%'
		re.append(d.copy())
	p=Paginator(re, limit,allow_empty_first_page=True)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

		
#会议--人员参会情况报表
def getmeetuserreport(request,isContainedChild,deptIDs,userIDs,st,et,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1

	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	sidx=""
	ot=[]
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	if sidx:
		ot=sidx.split(',')
	if q!='':
		q=unquote(q)
		if request.user.is_superuser or request.user.is_alldept:
			objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q))
		else:
			deptids=userDeptList(request.user)
			deptids.sort()
			id=deptids[0]
			dept=department.objByID(id)
			if dept.parent==0:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q)).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN=q)|Q(EName=q)).order_by(*ot)
	else:
		if len(deptIDs)>0:
			if isContainedChild=='1':
				dept=department.objByID(deptIDs)
				if request.user.is_superuser or request.user.is_alldept:
					dptids=getAllAuthChildDept(dept.DeptID,request)
					objs=employee.objects.filter(DeptID__in=dptids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
				else:
					dids=[]
					deptids_Auth=userDeptList(request.user) #获得用户的授权部门
					deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
					for i in deptids_Subordinate:
						if i in deptids_Auth:
							dids.append(i)
					objs=employee.objects.filter(DeptID__in=dids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID__in=deptIDs,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)

		else:
			if request.user.is_superuser or request.user.is_alldept:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
			else:
				deptids_Auth=userDeptList(request.user) #获得用户的授权部门
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
	p=Paginator(objs, limit)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	objs=pp.object_list
	re=[]
	Result={}
	userids=objs.values_list('id', flat=True)
	meet=Meet.objects.filter(Q(Starttime__gte=st,Starttime__lte=et)|Q(Endtime__gte=st,Endtime__lte=et))
	ll={}
	for me in meet:
		lx=getMeetNum(me.id,userids,0)
		for l in lx:
			keyduty='%s_duty'%l['userid']
			keyonduty='%s_onduty'%l['userid']
			keyabsent='%s_absent'%l['userid']
			keylate='%s_late'%l['userid']
			keyearly='%s_early'%l['userid']
			keyspeday='%s_speday'%l['userid']
			try:
				ll[keyduty]+=1
			except:
				ll[keyduty]=1
			try:
				if l['absent']>0:
					try:
						ll[keyabsent]+=1
					except:
						ll[keyabsent]=1
			except:
				pass
			try:
				if l['st']!='':
					try:
						ll[keyonduty]+=1
					except:
						ll[keyonduty]=1
			except:
				pass
			try:
				if l['late']>0:
					try:
						ll[keylate]+=1
					except:
						ll[keylate]=1
			except:
				pass
			try:
				if l['early']>0:
					try:
						ll[keyearly]+=1
					except:
						ll[keyearly]=1
			except:
				pass
			try:
				if l['lid']>0:
					try:
						ll[keyspeday]+=1
					except:
						ll[keyspeday]=1
			except:
				pass
			
	for t in objs:
		keyduty='%s_duty'%t.id
		keyonduty='%s_onduty'%t.id
		keyabsent='%s_absent'%t.id
		keylate='%s_late'%t.id
		keyearly='%s_early'%t.id
		keyspeday='%s_speday'%t.id
		d={}
		d['DeptName']=t.Dept().DeptName
		d['pin']=t.PIN
		d['name']=t.EName or ''
		try:
			d['duty']=ll[keyduty]
		except:
			d['duty']=0
		try:
			d['onduty']=ll[keyonduty]
		except:
			d['onduty']=0
		try:
			d['absent']=ll[keyabsent]
		except:
			d['absent']=0
		try:
			d['late']=ll[keylate]
		except:
			d['late']=0
		try:
			d['early']=ll[keyearly]
		except:
			d['early']=0
		try:
			d['speday']=ll[keyspeday]
		except:
			d['speday']=0
		try:
			d['rate']=str(int(float(d['onduty'])*100/d['duty']))+'%'
		except:
			d['rate']='0%'
		re.append(d.copy())
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result

	
#会议--人员参会情况报表
def getmeetuserlatereport(request,deptIDs,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	objs=[]
	Result={}
	re=[]
	lx=[]
	leaveclass={}
	LClasses1=GetLeaveClasses(1)
	for t in LClasses1:
		fName='Leave_'+str(t['LeaveID'])
		leaveclass[fName]=t['LeaveName']
	if deptIDs=='0' or deptIDs=='':
		deptIDs=Meet.objects.filter(DelTag=0).values_list('MeetID', flat=True)
		for d in deptIDs:
			lx=getMeetNum(d,objs,0)
			meet=Meet.objByID(d)
			for l in lx:
				if l['late']>0 or l['early']>0 or l['absent']>0 or l['lid']>0:
					d={}
					em=employee.objByID(l['userid'])
					d['pin']=em.PIN
					d['name']=em.EName or ''
					d['DeptName']=em.Dept().DeptName
					d['conferenceTitle']=meet.conferenceTitle
					d['st']=l['lst'].strftime("%Y-%m-%d %H:%M:%S")
					d['et']=l['let'].strftime("%Y-%m-%d %H:%M:%S")
					if l['st']!='':
						d['rst']=l['st'].strftime("%Y-%m-%d %H:%M:%S")
					else:
						d['rst']=''
					if l['et']!='':
						d['ret']=l['et'].strftime("%Y-%m-%d %H:%M:%S")
					else:
						d['ret']=''
					if l['late']>0:
						d['late']=u'%s'%_(u"是")
					if l['early']>0:
						d['early']=u'%s'%_(u"是")
					if l['absent']>0:
						d['absent']=u'%s'%_(u"是")
					if l['lid']>0:
						fName='Leave_'+str(l['lid'])
						d['speday']=leaveclass[fName]
					re.append(d.copy())
	else:
		lx=getMeetNum(deptIDs,objs,0)
		meet=Meet.objByID(deptIDs)
		for l in lx:
			if l['late']>0 or l['early']>0 or l['absent']>0 or l['lid']>0:
				d={}
				em=employee.objByID(l['userid'])
				d['pin']=em.PIN
				d['name']=em.EName or ''
				d['DeptName']=em.Dept().DeptName
				d['conferenceTitle']=meet.conferenceTitle
				d['st']=l['lst'].strftime("%Y-%m-%d %H:%M:%S")
				d['et']=l['let'].strftime("%Y-%m-%d %H:%M:%S")
				if l['st']!='':
					d['rst']=l['st'].strftime("%Y-%m-%d %H:%M:%S")
				else:
					d['rst']=''
				if l['et']!='':
					d['ret']=l['et'].strftime("%Y-%m-%d %H:%M:%S")
				else:
					d['ret']=''
				if l['late']>0:
					d['late']=u'%s'%_(u"是")
				if l['early']>0:
					d['early']=u'%s'%_(u"是")
				if l['absent']>0:
					d['absent']=u'%s'%_(u"是")
				if l['lid']>0:
					fName='Leave_'+str(l['lid'])
					d['speday']=leaveclass[fName]
				re.append(d.copy())
	p=Paginator(re, limit,allow_empty_first_page=True)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result


def getmeetroomreport(request,deptIDs,d1,d2,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	Result={}
	re={}
	meet=Meet.objects.filter(Starttime__gte=d1,Starttime__lte=d2).exclude(DelTag=1)
	if deptIDs and deptIDs!='0':
		meet=meet.filter(LocationID__pk=deptIDs)
	for me in meet:
		if me.LocationID:
			hour=me.Endtime-me.Starttime
			hour=hour.days*24+hour.seconds/3600
			day=str(me.Starttime.month)+u'-'+str(me.Starttime.day)
			try:
				lx=re[me.LocationID.roomNo]
				try:
					lx[day]=lx[day]+hour
					lx[day+'_']=lx[day+'_']+1
				except:
					lx[day]=hour
					lx[day+'_']=1
				lx['total']+=1
				lx['total_']+=hour
			except:
				lx={}
				lx['roomid']=me.LocationID.roomNo
				lx['roomname']=me.LocationID.roomName
				lx['total']=1
				lx['total_']=hour
				lx[day]=hour
				lx[day+'_']=1
				re[me.LocationID.roomNo]=lx
	res=[]
	for r in re.keys():
		lx=re[r]
		res.append(lx)
	p=Paginator(res, limit,allow_empty_first_page=True)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=p.object_list
	return Result

#人员年假报表
def getannualstatic(request,isContainedChild,deptIDs,q):
	iCount=0
	try:
		offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', 0))
	if limit==0:
		limit= int(request.GET.get('rows', 30))
	sidx=""
	ot=[]
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	if sidx:
		ot=sidx.split(',')
	if q!='':
		q=unquote(q)
		if request.user.is_superuser or request.user.is_alldept:
			objs=employee.objects.filter(OffDuty__lt=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
		else:
			deptids=userDeptList(request.user)
			deptids.sort()
			id=deptids[0]
			dept=department.objByID(id)
			if dept.parent==0:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).filter(Q(PIN__contains=q)|Q(EName__contains=q)|Q(Workcode__contains=q)).order_by(*ot)
	else:
		if len(deptIDs)>0:
			if isContainedChild=='1':
				dept=department.objByID(deptIDs)
				if request.user.is_superuser or request.user.is_alldept:
					dptids=getAllAuthChildDept(dept.DeptID,request)
					objs=employee.objects.filter(DeptID__in=dptids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
				else:
					dids=[]
					deptids_Auth=userDeptList(request.user) #获得用户的授权部门
					deptids_Subordinate=getAllAuthChildDept(dept.DeptID,request) #或得下级部门
					for i in deptids_Subordinate:
						if i in deptids_Auth:
							dids.append(i)
					objs=employee.objects.filter(DeptID__in=dids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
			else:
				objs=employee.objects.filter(DeptID=deptIDs,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
		else:
			if request.user.is_superuser or request.user.is_alldept:
				objs=employee.objects.filter(OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)
			else:
				deptids=userDeptList(request.user)
				objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).order_by(*ot)

	p=Paginator(objs, limit,allow_empty_first_page=True)
	iCount=p.count
	if iCount<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	re=[]
	Result={}
	y=request.GET.get('y')
	ys=datetime.datetime.strptime(y,"%Y-%m")
	yearstr=ys.year
	months=1
	days=1
	ann=annual_settings.objects.filter(Name="month_s")
	if ann.count()>0:
		months=int(ann[0].Value)
	ann=annual_settings.objects.filter(Name="day_s")
	if ann.count()>0:
		days=int(ann[0].Value)
	biao=datetime.datetime(ys.year,months,days,0,0)
	re=[]
	le=LeaveClass.objects.filter(LeaveType=5)
	unit=3
	minunit=1
	remaindproc=1
	if le.count()>0:
		unit=le[0].Unit
		minunit=le[0].MinUnit
		minunit=le[0].MinUnit
		remaindproc=le[0].RemaindProc
	for e in pp.object_list:
		ll={}
		ll['pin']=e.PIN
		ll['name']=e.EName or ''
		ll['Workcode'] = e.Workcode
		ll['dept']=e.Dept().DeptName
		ll['sex']=getSex(e.Gender)
		ll['Hiredday']=e.Hiredday or ''
		ll['bennianyuefen']=yearstr
		ll['gongling']=getWorkAge_(e.Hiredday,biao)
		ll['days']=getuserannual(e.id,biao.strftime("%Y-%m-%d"))
		if ll['days']:
			ll['days']=getzhuang(ll['days'],unit)
		else:
			ll['days']=''
		yy= getUserAnn(e.id,biao,minunit,unit,remaindproc)
		cc=0
		for x in yy.keys():
			ll[x]=yy[x]
			cc+=ll[x]
		try:
			dd=float(ll['days'])
		except :
			dd=0
		ll['weiyong']=dd-cc
		re.append(ll)
	if offset>page_count:offset=page_count
	item_count =iCount
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['datas']=re
	return Result
		

def getcalcAllReport(request,isContainedChild,deptIDs,st,et):
	from mysite.iclock.myreportview import calcallreport
	Result = calcallreport(request,isContainedChild,deptIDs,st,et)
	return Result

def getcalcExceptionReport(request,isContainedChild,deptIDs,st,et,q):
	from mysite.iclock.myreportview import calcexceptionreport
	Result = calcexceptionreport(request,isContainedChild,deptIDs,st,et,q)
	return Result

def getbackReport(request,isContainedChild,deptIDs,st,et,q):
	from mysite.iclock.myreportview import backreport
	Result = backreport(request,isContainedChild,deptIDs,st,et,q)
	return Result

def getallexceptionReport(request,isContainedChild,deptIDs,st,et):
	from mysite.iclock.myreportview import allexceptionreport
	Result = allexceptionreport(request,isContainedChild,deptIDs,st,et)
	return Result

def getjiezhuan(request,isContainedChild,deptIDs,q):
	from mysite.iclock.myreportview import jiezhuanreport
	Result = jiezhuanreport(request,isContainedChild,deptIDs,q)
	return Result

def getsearchRecordsr(request,ReportName):
	isContainedChild=request.GET.get("isContainChild","0")
	deptIDs=request.GET.get('deptIDs',"")
	userIDs=request.GET.get('UserIDs',"")
	st=request.GET.get('startDate','')
	et=request.GET.get('endDate','')
	q=request.GET.get('q','')
	now=datetime.datetime.now()
	if st=='':
		st=datetime.datetime(now.year,now.month,1,0,0)
	else:
		st=datetime.datetime.strptime(st,"%Y-%m-%d")
	if et=='':
		et=now
	else:
		et=datetime.datetime.strptime(et,"%Y-%m-%d")
		et=et+datetime.timedelta(days=0,hours=23,minutes=59,seconds=59)
	q=unquote(q)
	ReportName=ReportName.lower()
	if ReportName=='original_records':#原始记录表
		r=getoriginRecords(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='checkexact':   #补记录表
		r=getModelRecords(request,checkexact)
	elif ReportName=='calcattshiftsreport':
		r=getAttshiftsDaily(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='calcattexceptionreport':
		r=getcalcAttexceptionReport(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='user_no_sch':
		r=getUserNoSch(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='earlylatest_records':
		r=getEarlystAndLastest(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='attrecabnormite':  #人员出勤记录详情
		#r=getModelRecords(request,attRecAbnormite)
		r=getModelRecords(request,attRecAbnormite)
	elif ReportName=='calcleavereport':
		r=getcalcLeaveReport(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='calcleaveyreport':
		r=getcalcLeaveYReport(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='employee_finger':
		r=getemployee_finger(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='device_assignment':
		r=getdevice_assignment(request,isContainedChild,deptIDs,q)
	elif ReportName=='department_finger':
		r=getdepartment_finger(request,isContainedChild,deptIDs)
	elif ReportName=='daily_devices':
		r=getdaily_devices(request,isContainedChild,deptIDs,q)
	elif ReportName=='ihrreversedetail':
		r=getihrreversedetail(request,isContainedChild,deptIDs,q)
	elif ReportName=='user_speday':	   #人员请假详情
		r=getModelRecords(request,USER_SPEDAY)
	elif ReportName=='attexception':  #人员出勤异常详情
		r=getModelRecords(request,AttException)
	elif ReportName=='dailycalcreport':
		r=getdailycalcReport(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='calcreport':
		r=getcalcReport(request,isContainedChild,deptIDs,userIDs,st,et,q)		
	elif ReportName=='department_report':
		r=getdepartment_report(request,isContainedChild,deptIDs,userIDs,st,et,q)			
	elif ReportName=='annual_leave':
		r=getannual_leave(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='annualstatic':
		r=getannualstatic(request,isContainedChild,deptIDs,q)
	elif ReportName=='meeting_sign_report':
		r=getmeetingsign(request,deptIDs,q)
	elif ReportName=='meeting_not_sign_report':
		r=getmeetingnotsign(request,deptIDs,q)
	elif ReportName=='meeting_report':
		r=getmeetreport(request,deptIDs,q)
	elif ReportName=='meeting_user_report':
		r=getmeetuserreport(request,isContainedChild,deptIDs,userIDs,st,et,q)
	elif ReportName=='meeting_user_late_report':
		r=getmeetuserlatereport(request,deptIDs,q)
	elif ReportName=='meeting_room_report':
		r=getmeetroomreport(request,deptIDs,st,et,q)
	elif ReportName=='records':   #门禁记录表
		r=getModelRecords(request,records)
	elif ReportName=='acc_exception':   #门禁异常记录表
		r=getModelRecords(request,records)
	elif ReportName=='calcallreport':
		r=getcalcAllReport(request,isContainedChild,deptIDs,st,et)
	elif ReportName=='exceptionreport':
		r=getcalcExceptionReport(request,isContainedChild,deptIDs,st,et,q)
	elif ReportName=='backreport':
		r=getbackReport(request,isContainedChild,deptIDs,st,et,q)
	elif ReportName=='allexceptionreport':
		r=getallexceptionReport(request,isContainedChild,deptIDs,st,et)
	elif ReportName=='jiezhuan':
		r=getjiezhuan(request,isContainedChild,deptIDs,q)
	return r




#获取Model类型报表 
def getModelRecords(request,dataModel):
	appName=request.path.split('/')[1]
	tmpFile=dataModel.__name__+'_list.js'
	if dataModel == attRecAbnormite:
		dataModel=transactions
	jqGrid=JqGrid(request,datamodel=dataModel)
	items=jqGrid.get_items()   #not Paged
	cc=jqGrid.get_json(items)
	if appName!='iclock':
		tmpFile=appName+'/'+tmpFile
			
	
	t=loader.get_template(tmpFile)
	cc['can_change']=False
	try:
	    rows=t.render(cc)
	except Exception,e:
	    rows='[]'
	    pass
	Result={}
	Result['item_count']=cc['records']
	Result['page']=cc['page']
	Result['page_count']=cc['total']
	Result['datas']=loads(rows)
	return Result
	


#@permission_required("iclock.IclockDept_reports")
def index(request):
	request.user.iclock_url_rel='../..'
	sub_menu='"%s"'%createmenu(request,'report')
	appName=request.path.split('/')[1]
#	print "===============================",sub_menu
#	dataModel=GetModel("ItemDefine")
#	if not hasPerm(request.user, dataModel, "browse"):
#		return getJSResponse(_("You do not have the browse %s permission!")%(u"报表"))
	settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
	limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
	tmpFile="reports_list.html"
	if appName!='iclock':
		tmpFile=appName+'/'+tmpFile
	else:
		tmpFile='att'+'/'+tmpFile
	return render_to_response(tmpFile,
							 {
							  'sub_menu':sub_menu,
							  'limit':limit
							},RequestContext(request, {}))



@login_required
def gridIndex(request,ReportName):
	if request.method=='GET':
		r=GetGridCaption(ReportName,request)
		return r
	else:
		Result=getsearchRecordsr(request,ReportName)
		rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
		return getJSResponse(rs)


#未来样式，每一个报表一个html
@login_required
def reportIndex(request,ReportName):
	appName=request.path.split('/')[1]
	tmpFile="%s.html"%ReportName
	settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
	limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
	if appName!='iclock':
		tmpFile=appName+'/report_'+tmpFile
	else:
		tmpFile='att'+'/report_'+tmpFile
	if request.method=='GET':
		#print "-------------------------------",tmpFile
		if 'title' in request.GET.keys():
			r=GetGridCaption(ReportName,request)
			return r
		cc={}
			
			
			#r=GetGridCaption(ReportName,request)
			#cc['colModel']=dumps1(r[1])
			#cc['disabledcols']=dumps1(r[0])
			#cc['groupHeaders']=dumps(r[2])
			#cc['limit']=limit
		if ReportName=='dailycalcReport':
			cc['reportSymbol']='%s'%GetCalcSymbol()
		elif ReportName=='calcReport':
			cc['reportSymbol']='%s'%GetCalcUnit()
		cc['reportName']=ReportName
		return render(request,tmpFile,cc)#render_to_response(tmpFile,cc,RequestContext(request, {}))
	else:
		Result=getsearchRecordsr(request,ReportName)
		if not 'userData' in Result:Result['userData']={}
		rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+","+""""userdata":"""+dumps(Result['userData'])+"""}"""
		return getJSResponse(rs)

