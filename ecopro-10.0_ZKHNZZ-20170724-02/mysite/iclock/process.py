#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import string
from django.contrib import auth
from django.shortcuts import render_to_response,render
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context, RequestContext
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator
from mysite.iclock.models import *
from mysite.iclock.datas import *
from django.utils.translation import ugettext_lazy as _
from mysite.accounts.admin import MyUser
from iutils import userDeptList
	
@login_required
def setprocess(request):
	allproc=getfirstproc()
	allproc+=getallprocess()
	allproc+=getlastproc()
	return render(request,'process_list.html',{'allproc': smart_str(dumps(allproc))})
	#return render_to_response('process_list.html',
	#						 {'allproc': smart_str(dumps(allproc)),
	#						},RequestContext(request, {}))

@login_required
def showApprovals(request):
	usp_id=request.GET.get('id','-1')
	ll=getspedaydetails(usp_id)
	approval=u"<table cellspacing='0' cellpadding='0' border='1' style='text-align: center;font-size:14px;BORDER-BOTTOM: medium none; BORDER-LEFT: medium none; WIDTH: 100%; BORDER-COLLAPSE: collapse; BORDER-TOP: medium none; BORDER-RIGHT: medium none'><tbody>"
	approval+=u"<tr><td width='16.7%' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: windowtext 2.25pt double; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>姓名</td>"
	approval+=u"<td width='16.7%' height='40' style='text-align: left;BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: windowtext 2.25pt double; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>"+(ll['name'] or '')+"</td>"
	approval+=u"<td width='16.7%' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: windowtext 2.25pt double; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>部门</td>"
	approval+=u"<td width='16.7%' height='40' style='text-align: left;BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: windowtext 2.25pt double; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>"+ll['deptname']+"</td>"
	approval+=u"<td width='16.7%' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: windowtext 2.25pt double; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>职务</td>"
	approval+=u"<td height='40' style='text-align: left;BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: windowtext 2.25pt double; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+ll['title']+"</td></tr>"
	st=ll['st']
	et=ll['et']
	stet=u'  %s 年 %s 月 %s 日 %s 时至 %s 年 %s 月 %s 日 %s 时'%(st.year,st.month,st.day,st.hour,et.year,et.month,et.day,et.hour)
	approval+=u"<tr><td width='15%' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>请假类别</td>"
	approval+=u"<td width='35%' colspan='2' height='40' style='text-align: left;BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>"+ll['leaveclass']+"</td>"
	approval+=u"<td width='15%' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>联系电话</td>"
	approval+=u"<td width='35%' colspan='2' height='40' style='text-align: left;BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+ll['mobile']+"</td></tr>"
	
	approval+=u"<tr><td width='10%' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>请假时间</td>"
	approval+=u"<td height='40' colspan='5' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+stet+"</td></tr>"
	
	approval+=u"<tr><td width='10%' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>外出地点</td>"
	approval+=u"<td width='20%' colspan='2' height='40' style='text-align: left;BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>"+ll['place']+"</td>"
	approval+=u"<td width='10%' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>工作承接人</td>"
	approval+=u"<td height='40' colspan='2' style='text-align: left;BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+ll['successor']+"</td></tr>"
	
	approval+=u"<tr><td width='10%' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>备注</td>"
	approval+=u"<td height='40' colspan='5' style='text-align: left;BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+ll['remarks']+"</td></tr>"
	
	liyou=u"<table width='100%' style='text-align: center;font-size:14px;'>"
	liyou+=u"<tr height=70><td colspan=3 style='text-align: left;'>"+ll['yy']+u"</td></tr><tr><td width='35%'>&nbsp;</td><td width='35%'>申请人签字："+(ll['name'] or '')+u"</td>"
	liyou+=u"<td>&nbsp;&nbsp;%s 年 %s 月 %s 日</td></tr></table>"%(ll['ad'].year,ll['ad'].month,ll['ad'].day)
	approval+=u"<tr><td width='10%' height='100' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>申请人休假理由</td>"
	approval+=u"<td height='100' colspan='5' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+liyou+"</td></tr>"
	processll=[]
	for a in ll.keys():
		if a.find("process_")!=-1:#查找所有的审核流程
			processll.append(a)
	lp= len(processll)
	sortll={}
	processll_=[]
	for x in processll:
		sortll[ll[x]['procSN']]=x#x为ll的key值，通过procSN排序，这里为了实现流程按从小到大排序
	sk=sortll.keys()
	sk.sort()
	for s in sk:
		processll_.append(sortll[s])
	if lp<6:
		for x in processll_:
			pll=ll[x]
			liyou=u"<table width='100%' style='text-align: center;font-size:14px;'>"
			liyou+=u"<tr height=10><td colspan=3 style='text-align:left;'>"+pll['userrole']+u"意见：</td></tr>"
			liyou+=u"<tr height=60><td colspan=3 style='text-align: left;'>&nbsp;&nbsp;&nbsp;&nbsp;"+pll['yijian']+u"</td></tr><tr><td width='50%'>&nbsp;</td><td width='25%' style='text-align:left'>签名："+pll['qianming']+u"</td>"
			if pll['riqi']=="":
				liyou+=u"<td style='text-align:right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;年&nbsp;&nbsp;&nbsp;月&nbsp;&nbsp;&nbsp;&nbsp;日</td></tr></table>"
			else:
				liyou+=u"<td style='text-align:right'>&nbsp;&nbsp;%s 年 %s 月 %s 日</td></tr></table>"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
			if x ==processll_[-1]:
				approval+=u"<tr><td height='100' colspan='6' style='BORDER-BOTTOM: windowtext 2.25pt double; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+liyou+"</td></tr>"
			else:
				approval+=u"<tr><td height='100' colspan='6' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+liyou+"</td></tr>"
	elif lp<10:
		yu=lp%5
		i=1
		for x in processll_:
			pll=ll[x]
			liyou=u"<table width='100%' style='text-align: center;font-size:14px;'>"
			liyou+=u"<tr height=10><td colspan=3 style='text-align:left;'>"+pll['userrole']+u"意见：</td></tr>"
			liyou+=u"<tr height=60><td colspan=3 style='text-align: left;'>&nbsp;&nbsp;&nbsp;&nbsp;"+pll['yijian']+u"</td></tr><tr><td width='50%'>&nbsp;</td><td width='25%' style='text-align:left'>签名："+pll['qianming']+u"</td>"
			if pll['riqi']=="":
				liyou+=u"<td style='text-align:right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;年&nbsp;&nbsp;&nbsp;月&nbsp;&nbsp;&nbsp;&nbsp;日</td></tr></table>"
			else:
				liyou+=u"<td style='text-align:right'>&nbsp;&nbsp;%s 年 %s 月 %s 日</td></tr></table>"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
			if i<=yu*2:
				if i%2==1:
					approval+=u"<tr><td colspan='3' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>"+liyou+"</td>"
				else:
					approval+=u"<td height='40' colspan='3' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+liyou+"</td></tr>"
			else:
				if x ==processll_[-1]:
					approval+=u"<tr><td height='100' colspan='6' style='BORDER-BOTTOM: windowtext 2.25pt double; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+liyou+"</td></tr>"
				else:
					approval+=u"<tr><td height='100' colspan='6' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+liyou+"</td></tr>"
			i+=1
	else:
		i=1
		for x in processll_:
			pll=ll[x]
			liyou=u"<table width='100%' style='text-align: center;font-size:14px;'>"
			liyou+=u"<tr height=10><td colspan=3 style='text-align:left;'>"+pll['userrole']+u"意见：</td></tr>"
			liyou+=u"<tr height=60><td colspan=3 style='text-align:left;'>&nbsp;&nbsp;&nbsp;&nbsp;"+pll['yijian']+u"</td></tr><tr><td width='50%'>&nbsp;</td><td width='25%' style='text-align:left'>签名："+pll['qianming']+u"</td>"
			if pll['riqi']=="":
				liyou+=u"<td style='text-align:right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;年&nbsp;&nbsp;&nbsp;月&nbsp;&nbsp;&nbsp;&nbsp;日</td></tr></table>"
			else:
				liyou+=u"<td style='text-align:right'>&nbsp;&nbsp;%s 年 %s 月 %s 日</td></tr></table>"%(pll['riqi'].year,pll['riqi'].month,pll['riqi'].day)
			if len(processll_)%2==0:
				if x==processll_[-2]:
					approval+=u"<tr><td colspan='3' height='40' style='BORDER-BOTTOM: windowtext 2.25pt double; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>"+liyou+"</td>"
				elif x==processll_[-1]:
					approval+=u"<td height='40' colspan='3' style='BORDER-BOTTOM: windowtext 2.25pt double; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+liyou+"</td></tr>"
				else:
					if i%2==1:
						approval+=u"<tr><td colspan='3' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>"+liyou+"</td>"
					else:
						approval+=u"<td height='40' colspan='3' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+liyou+"</td></tr>"
			else:
				if x==processll_[-1]:
					approval+=u"<tr><td height='100' colspan='6' style='BORDER-BOTTOM: windowtext 2.25pt double; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+liyou+"</td></tr>"
				else:
					if i%2==1:
						approval+=u"<tr><td colspan='3' height='40' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: windowtext 2.25pt double; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 1pt solid; PADDING-TOP: 0cm'>"+liyou+"</td>"
					else:
						approval+=u"<td height='40' colspan='3' style='BORDER-BOTTOM: windowtext 1pt solid; BORDER-LEFT: medium none; PADDING-BOTTOM: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt; BORDER-TOP: medium none; BORDER-RIGHT: windowtext 2.25pt double; PADDING-TOP: 0cm'>"+liyou+"</td></tr>"
			i+=1
	approval+=u"</tbody></table><div style='page-break-after:always'></div>"

	return render(request,'ShowApprovals.html',
							 {'approval': approval,
							  'id':usp_id,
							  'MEDIA_URL':settings.MEDIA_URL
							})

def getspedaydetails(usp_id):
	ll={}
	try:
		spe=USER_SPEDAY.objects.get(id=usp_id)
		ll['name']=spe.employee().EName
		ll['deptname']=spe.employee().Dept().DeptName
		ll['title']=spe.employee().Title or ''
		dateid=spe.DateID
		ll['leaveclass']=''
		leaveclass=GetLeaveClassesEx(1)
		for l in leaveclass:
			if l['LeaveID']==dateid:
				ll['leaveclass']=l['LeaveName']
		ll['st']=spe.StartSpecDay
		ll['et']=spe.EndSpecDay
		ll['tian']=0
		ll['ad']=spe.ApplyDate
		ll['yy']=spe.YUANYING
		pro=spe.process
		if pro=='' or pro==None:
			pros=[0]
		else:
			pros=pro.split(",")
		i=100
		for p in pros:
			if p==0:
				ll['process_0']={'userrole':u"管理员",'yijian':'','qianming':'','riqi':'','procSN':0}
			else:
				if p!='':
					i+=1
					rolename=""
					try:
						ur=userRoles.objects.get(roleid=p)
						rolename=ur.roleName
					except:
						pass
					ll['process_%s'%p]={'userrole':rolename,'yijian':'','qianming':'','riqi':'','procSN':i}
		details=USER_SPEDAY_DETAILS.objects.filter(USER_SPEDAY_ID=usp_id)
		ll['place']=""
		ll['mobile']=""
		ll['successor']=""
		ll['remarks']=""
		if details:
			ll['place']=details[0].Place
			ll['mobile']=details[0].mobile
			ll['successor']=details[0].successor
			ll['remarks']=details[0].remarks
		process=USER_SPEDAY_PROCESS.objects.filter(USER_SPEDAY_ID=usp_id).order_by("procSN")
		for p in process:
			user=p.User
			if p.procSN==0:
				pll=ll['process_0']
				pll['yijian']=p.comments
				pll['riqi']=p.ProcessingTime
				pll['qianming']=user.first_name
			else:
				roles=userRole.objects.filter(userid=user)
				user_role=0
				if roles.count()>0:
					user_role=roles[0].roleid.roleid
				else:
					continue
				try:
					pll=ll['process_%s'%user_role]
					pll['yijian']=p.comments
					pll['riqi']=p.ProcessingTime
					pll['qianming']=user.first_name
					#pll['procSN']=p.procSN
				except:
					if user.is_superuser==True:
						xl={}
						pll['userrole']=u"系统管理员"
						xl['yijian']=p.comments
						xl['riqi']=p.ProcessingTime
						xl['qianming']=user.first_name
						ll['process_super']=xl
						pll['procSN']=1000 
						
	except Exception,e:
		print e
		pass
	return ll
def getallprocess():
	pro=process.objects.all()
	if pro:
		pldict={}
		ptdict={}
		udict={}
		lclass={'10000':u'%s'%_(u'加班'),'10001':u'%s'%_(u'补记录')}
		leaveclass=GetLeaveClassesEx(1)
		for l in leaveclass:
			lclass[str(l['LeaveID'])]=l['LeaveName']
		pl=proleave.objects.all()
		for p in pl:
			try:
				leavename=lclass[str(int(p.leaveid))]
			except:
				leavename=''
			try:
				pldict[p.processid_id].append(leavename)
			except:
				pldict[p.processid_id]=[]
				pldict[p.processid_id].append(leavename)
		pt=protitle.objects.all()
		for p in pt:
			try:
				ptdict[p.processid_id].append(p.roleid.roleName)
			except:
				ptdict[p.processid_id]=[]
				ptdict[p.processid_id].append(p.roleid.roleName)
		urd=userRolesDell.objects.all()
		for u in urd:
			uld={}
			uld['l']=u.procSN
			note=u'<div><table style="text-align:center"><tr><td>第%s级审批</td></tr>'%u.procSN
			text=u'职务为%s的管理员允许审核'%u.roleid.roleName
			if u.State==2:
				text+=u'职务小于自己职务的人员请假'
			elif u.State==1:
				text+=u'职务小于等于自己职务的人员请假'
			else:
				text+=u'请假'
			text+=u',并且能够通过%s天的请假'%u.days
			note+='<tr><td><div style="width:130px;height:104px;">%s</div></td><tr></table></div>'%text
			uld['c']=note
			try:
				udict[u.processid_id].append(uld)
			except:
				udict[u.processid_id]=[]
				udict[u.processid_id].append(uld)
		allproc=''
		for p in pro:
			uld={}
			uld['l']=0
			note=u'<div><table><tr><td width="70px">流程名称：</td><td  width="70px">%s</td></tr>'%p.processName
			note+=u'<tr><td>最小天数：</td><td>%s</td></tr><tr><td>最大天数：</td><td>%s</td></tr>'%(p.smallday,p.bigday)
			try:
				note+=u'<tr><td>应用假类：</td><td><span title=%s>%s...</span></td></tr>'%(','.join(pldict[p.id]),pldict[p.id][0])
			except Exception,e:
				print e
				pass
			try:
				if p.notitle==1:
					try:
						ptdict[p.id].append(u"无职务人员")
					except:
						ptdict[p.id]=[]
						ptdict[p.id].append(u"无职务人员")
				note+=u'<tr><td>应用职务：</td><td><span title=%s>%s...</span></td></tr>'%(','.join(ptdict[p.id]),ptdict[p.id][0])
			except:pass
			uld['c']=note+"</table></div>"
			try:
				udict[p.id].append(uld)
			except:
				udict[p.id]=[]
				udict[p.id].append(uld)
			ll=[]
			try:
				ll=udict[p.id]
			except:pass
			allproc+=gettopandleft(p.id,ll)
	else:
		allproc=''
		r=userRoles.objects.all().count()
		if r>0:
			r=userRole.objects.all().count()
			if r==0:
				allproc+=u"<span style='color:red'>用户中没有配置职务。</span>"	
		else:
			allproc+=u"<span style='color:red'>职务维护中如果没有职务信息，请在用户界面中找到职务设置，新增职务，并且为用户配置职务，以确定审核人的身份。</span>"
	return allproc

def gettopandleft(pid,ll):
	html=u"<div id='id_%s_div' class='div_c'>"%(pid)
	rhtml=''
	phtml=''
	maxl=0
	for l in ll:
		if maxl<l['l']:
			maxl=l['l']
	for l in ll:
		rhtml=''
		left=l['l']*240
		top=30
		if l['l']==maxl:
			rhtml="<div id='id_%s_%s_div' class='div_r' style='top:%spx;left:%spx' onclick=javescrip:setdiv('%s','%s')>%s</div>"%(pid,l['l'],top,left+22,pid,l['l'],l['c'])
			rhtml+="<div id='id_%s_%s_div_a' class='div_r_a' style='top:%spx;left:%spx' onclick=javescrip:deldiv('%s','%s')></div>"%(pid,l['l'],top,left,pid,l['l'])
			rhtml+="<div id='id_%s_%s_div_b' class='div_r_b' style='top:%spx;left:%spx' onclick=javescrip:newdiv('%s','%s')></div>"%(pid,l['l'],top,left+176,pid,l['l'])
		else:
			rhtml="<div id='id_%s_%s_div' class='div_r' style='top:%spx;left:%spx' onclick=javescrip:setdiv('%s','%s')>%s</div>"%(pid,l['l'],top,left,pid,l['l'],l['c'])
		if l['l']!=0:
			phtml="<div id='id_%s_%s_div_' class='div_t' style='top:%spx;left:%spx'></div>"%(pid,l['l'],top,left-85)
		else:
			phtml=""
		html=html+phtml+rhtml
	html+="</div>"
	return html
	
def getfirstproc():
	checked="checked=checked"
	if GetParamValue('opt_basic_approval','1')=='0':
		checked=""
	html=u"<div id='id_first_div' style='height:40px'><div style='padding:25px;'><label for='id_approval'></label><input %s maxlength='30' id='id_approval' name='approval' type='checkbox'>&nbsp;开启多级审批功能(勾选为开启状态)</div></div>"%(checked)
	return html
def getlastproc():
	html=u"<div id='id_new_div' class='div_c'>"
	phtml=''
	rhtml=''
	left=0
	top=30
	rhtml="<style>.div_r:after{content: '';z-index: -1;width: 100px;height: 100px;position:absolute;bottom:0;right:0;background: rgba(0, 0, 0, 0.2);display: inline-block;-webkit-box-shadow: 20px 20px 8px rgba(0, 0, 0, 0.2);-webkit-transform: rotate(0deg)translate(-45px,-20px)skew(20deg);}</style><div id='id_new_0_div' class='div_r' style='top:%spx;left:%spx;position:relative;' onclick=javescrip:setdiv('new','0')>%s</div>"%(top,left+22,u'%s'%_(u'新的审批流程'))
	html+=rhtml
	html+="</div>"
	return html

def gettimediff(et,st):
	"""修改为按天请假，暂时不在计算小时"""
	st1=datetime.datetime(st.year,st.month,st.day,0,0)
	et1=datetime.datetime(et.year,et.month,et.day,0,0)
	days=1
	while True:
		st1+=datetime.timedelta(days=1)
		if st1<=et:
			days+=1
		else:
			break
	return days

def getprocess_EX(UserID,leaveid,day):
	"""UserID：用户编号；leaveid：假类，10000为加班，10001为补记录；st：开始时间；et：结束时间"""
	ll=[]
	if GetParamValue('opt_basic_approval','1')=='0':#判断是否支持多级审批
		return ll,0
	emp=employee.objByID(UserID)
	if emp:
		title=0
		titleX=0
		try:
			uR=userRoles.objects.filter(roleName=emp.Title)
			if uR.count()>0:
				title=uR[0].id#获得当前请假人员的职务编号
				titleX=uR[0].roleLevel#当前请假人员的职务级别
		except:
			pass
		processids=proleave.objects.filter(leaveid=leaveid).values("processid")
		pro=process.objects.filter(id__in=processids).filter(smallday__lte=day,bigday__gte=day)
		if title==0:
			pro=pro.filter(notitle=1)
		else:
			pts=protitle.objects.filter(roleid=title).values("processid")
			pro=pro.filter(id__in=pts)
		pms=prodeptmapping.objects.filter(processid__in=pro.values("id"))
		prolist={}
		for p in pms:
			if p.DeptID:
				try:
					prolist[p.processid_id].append(p.DeptID_id)
				except:
					prolist[p.processid_id]=[]
					prolist[p.processid_id].append(p.DeptID_id)
		processid=0
		pro=pro.order_by("id")
		for p in pro:
			if p.id in prolist.keys():#流程属于某个部门
				if emp.Dept().DeptID in prolist[p.id]:#包括请假人的部门直接赋值
					processid=p.id
					break
			else:
				if processid==0:#首次赋值
					processid=p.id
		if processid==0:#没有符合的流程
			return ll,0
		#获取人员
		Result=[]
		deptid=emp.Dept().DeptID
		us=MyUser.objects.all()#
		for t in us:
			ut=t.id
			if t.is_superuser==True:#获取超级管理员和授权所有部门的用户编号
				Result.append(ut)
			else:
				if leaveid==10000:
					if t.has_perm('iclock.overtimeAudit_user_overtime'):
						qs=userDeptList(t)
						if deptid in qs: 
							Result.append(ut)
				elif leaveid==10001:
					if t.has_perm('iclock.TransAudit_checkexact'):
						qs=userDeptList(t)
						if deptid in qs: 
							Result.append(ut)
				else:
					if t.has_perm('iclock.leaveAudit_user_speday'):
						qs=userDeptList(t)
						if deptid in qs:
							Result.append(ut)
		#上面为取出所有授权管理UserID并且有审核功能的管理员
		r=userRole.objects.filter(userid__in=Result).values_list("roleid", flat=True)#获取所有管理员职务
		urd={}
		ur=userRolesDell.objects.filter(processid=processid)
		for u in ur:
			if u.roleid_id not in r:#职务是否在所有管理员中。
				continue
			if u.State==1:#允许审核小于等于自己职务级别的人员
				if u.roleid.roleLevel<titleX:
					continue
			elif u.State==2:#允许审核小于于自己职务级别的人员
				if u.roleid.roleLevel<=titleX:
					continue
			#0表示无论什么样职务的人员全部需要审批
			urd[u.procSN]=[u.roleid.roleid,u.days]#所有符合标准的职务
	
		ull=urd.keys()
		ull.sort()#使用procSN进行排序
		for l in ull:
			ll.append(urd[l][0])
			if urd[l][1]>=day:#审核人员允许审核天数大于请假天数结束循环
				break
		return ll,processid
	else:
		return ll,0
def saveprocessfor(request):
	id=request.POST.get("id",'new')
	rid=request.POST.get("role",'')
	lea=request.POST.get("leave",'')
	pn=request.POST.get("pname",'')
	sd=request.POST.get("smallday",0)
	bd=request.POST.get("bigday",0)
	nt=request.POST.get("notitle",0)
	state=request.POST.get("state",0)
	dept=request.POST.get("dept",'')
	if id=='new':#新增
		if pn!='':
			try:
				p=process(processName=pn,smallday=sd,bigday=bd,notitle=nt)
				p.save()
				#title=u"新增审批流程%s"%pn
				title=u'%s' % _("Append") + u'%s' % _("process")
			except:
				return getJSResponse({"ret":1,"message":u'%s'%_(u'保存失败')})
		else:
			return getJSResponse({"ret":1,"message":u'%s'%_(u'保存失败')})
	else:
		p=process.objects.get(id=id)
		p.processName=pn
		p.smallday=sd
		p.bigday=bd
		p.notitle=nt
		p.save()
		title=u'%s' % _("Change") + u'%s' % _("process")
	adminLog(time=datetime.datetime.now(),User=request.user,object=u"%s"%pn, model=process._meta.verbose_name, action=title).save(force_insert=True)#
	
	try:
		proleave.objects.filter(processid=p).delete()
		leave=lea.split(",")
		for l in leave:
			proleave(processid=p,leaveid=l).save()
	except:
		pass
	try:
		protitle.objects.filter(processid=p).delete()
		ri=rid.split(",")
		ru=userRoles.objects.filter(id__in=ri)
		for u in ru:
			protitle(processid=p,roleid=u).save()
	except:
		pass
	try:
		prodeptmapping.objects.filter(processid=p).delete()
		if int(state)==1:
			depts=dept.split(",")
			for d in depts:
				l=department.objByID(d)
				if l:
					prodeptmapping(processid=p,DeptID=l).save()
	except:
		pass
	allproc=getfirstproc()
	allproc+=getallprocess()
	allproc+=getlastproc()
	changeforprocess()
	return getJSResponse({"ret":0,"message":allproc})

def saveprocessl(request):
	rid=request.POST.get("role",'')
	day=request.POST.get("day",'')
	state=request.POST.get("state",0)
	id=request.POST.get("id")
	lid=request.POST.get("lid")
	try:
		userRolesDell.objects.filter(processid=id,procSN=lid).delete()
		p=process.objects.get(id=id)
		ru=userRoles.objects.get(id=rid)
		userRolesDell(roleid=ru,processid=p,State=state,days=day,procSN=lid).save()
	except Exception,e:
		return getJSResponse({"ret":1,"message":u'%s'%_(u'保存失败')})
	note=u'<div><table style="text-align:center"><tr><td>第%s级审批</td></tr>'%lid
	text=u'职务为%s的管理员允许审核'%ru.roleName
	state=int(state)
	if state==2:
		text+=u'职务小于自己职务的人员请假'
	elif state==1:
		text+=u'职务小于等于自己职务的人员请假'
	else:
		text+=u'请假'
	text+=u',并且能够通过%s天的请假'%day
	note+='<tr><td><div style="width:130px;height:104px;">%s</div></td><tr></table></div>'%text
	changeforprocess()
	title=u"保存审批流程%s第%s级审批"%(id,lid)
	processName = p.processName or ''
	adminLog(time=datetime.datetime.now(),User=request.user,object=u'%s'%processName, model=process._meta.verbose_name, action=title).save(force_insert=True)#
	return getJSResponse({"ret":0,"message":u'%s'%note})
	
def delprocessl(request):
	id=request.POST.get("id")
	lid=request.POST.get("lid")
	try:
		if int(lid)==0:
			p = process.objects.get(id=id)
			processName = p.processName or ''
			p.delete()
			title=u"删除审批流程%s"%id
		else:
			processName = process.objects.get(id=id).processName or ''
			userRolesDell.objects.filter(processid=id,procSN=lid).delete()
			title=u"删除审批流程%s第%s级审批"%(id,lid)
		adminLog(time=datetime.datetime.now(),User=request.user,object=u'%s'%processName, model=process._meta.verbose_name, action=title).save(force_insert=True)#
	except:pass
	changeforprocess()
	return getJSResponse({"ret":0,"message":u''})

def changeforprocess():
	changedate=datetime.datetime.now()
	spedy=USER_SPEDAY.objects.filter(StartSpecDay__lte=changedate,EndSpecDay__gte=changedate).exclude(State__in=[2,3])#修改所有未通过的请假
	for sp in spedy:
		et=sp.EndSpecDay
		st=sp.StartSpecDay
		minunit=gettimediff(et,st)
		proc,pid=getprocess_EX(sp.UserID_id,sp.DateID,minunit)
		if len(proc)==0:
			roleid=0
			process=''
		else:
			roleid=proc[0]
			process=','.join(str(x) for x in proc)
			process=','+process+','
		sp.State=0
		sp.processid=pid
		sp.roleid=roleid
		sp.process=process
		sp.save()


def getprocleave(request):
	leave=LeaveClass.objects.all().exclude(DelTag=1)
	ll=[]
	for l in leave:
		le={}
		le['id']=l.LeaveID
		le['LeaveName']=u'%s'%_(l.LeaveName)
		ll.append(le)
	le={}
	le['id']=10000
	le['LeaveName']=u'加班'
	ll.append(le)
	le={}
	le['id']=10001
	le['LeaveName']=u'补记录'
	ll.append(le)
	Result={}
	Result['item_count']=len(ll)
	Result['page']=1
	Result['limit']=100
	Result['from']=1
	Result['page_count']=1
	Result['datas']=ll
	rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
	return getJSResponse(rs)


def getdepartment(request):
	dept=department.objects.all().exclude(DelTag=1)
	ll=[]
	for l in dept:
		le={}
		le['id']=l.DeptID
		le['DeptID']=l.DeptID
		le['DeptNumber']=l.DeptNumber
		le['DeptName']=u'%s'%_(l.DeptName)
		ll.append(le)
	Result={}
	Result['item_count']=len(ll)
	Result['page']=1
	Result['limit']=100
	Result['from']=1
	Result['page_count']=1
	Result['datas']=ll
	rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
	return getJSResponse(rs)


def getuserRoles(request):
	lid=request.GET.get("procSN",'0')
	ur=userRoles.objects.all().order_by("roleLevel")
	if lid=='0':
		ll=[{'id':-1,'roleid':0,'roleLevel':0,'roleName':u'无职务人员'}]
	else:
		ll=[]
	for l in ur:
		le={}
		le['id']=l.id
		le['roleid']=l.roleid
		le['roleLevel']=l.roleLevel
		le['roleName']=u'%s'%_(l.roleName)
		ll.append(le)
	Result={}
	Result['item_count']=len(ll)
	Result['page']=1
	Result['limit']=100
	Result['from']=1
	Result['page_count']=1
	Result['datas']=ll
	rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
	return getJSResponse(rs)

def getprocessfor(request):
	pid=request.POST.get("pid")
	lid=request.POST.get("lid")
	rs={}
	if int(lid)==0:
		p=process.objects.get(id=pid)
		rs['pn']=p.processName
		rs['sd']=p.smallday
		rs['bd']=p.bigday
		rs['nt']=p.notitle
		pleave=''
		ptitle=''
		pdept=''
		pl=proleave.objects.filter(processid=p)
		for l in pl:
			pleave+=','+str(l.leaveid)+','
		pt=protitle.objects.filter(processid=p)
		for l in pt:
			ptitle+=','+str(l.roleid.roleid)+','
		pd=prodeptmapping.objects.filter(processid=p)
		for l in pd:
			if l.DeptID:
				pdept+=','+str(l.DeptID.DeptID)+','
		rs['pleave']=pleave
		rs['ptitle']=ptitle
		rs['pdept']=pdept
	else:
		ur=userRolesDell.objects.filter(processid=pid,procSN=lid)
		for u in ur:
			rs['roleid']=u.roleid.roleid
			rs['days']=u.days
			rs['state']=u.State
	return getJSResponse(rs)
