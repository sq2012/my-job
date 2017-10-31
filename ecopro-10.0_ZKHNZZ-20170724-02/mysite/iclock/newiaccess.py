#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.base.models import *
from mysite.core.tools import *
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
#from django.http import HttpResponse
from django.shortcuts import render_to_response,render
import datetime
from mysite.utils import *
from django.contrib.auth.decorators import permission_required, login_required
from mysite.iclock.dataproc import *
#from django.contrib.auth.models import User, Permission
from mysite.iclock.iutils import *
from mysite.iclock.reb	import *
#REBOOT_CHECKTIME, PAGE_LIMIT, ENABLED_MOD, TIME_FORMAT, DATETIME_FORMAT, DATE_FORMAT
from mysite.cab import *
from mysite.iclock.datv import *
from django.utils.translation import ugettext_lazy as _
#from django.contrib.auth.models import User
#from django.contrib.sessions.models import Session
from mysite.iclock.datas import *
#from django.utils import simplejson
from mysite.iclock.datasproc import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
from mysite.iclock.datasproc import *
from mysite.iclock.templatetags.iclock_tags import getSex
from django.utils.encoding import smart_unicode, iri_to_uri
from mysite.iclock.jqgrid import *
from mysite.iclock.clearphotosdata import clearPhotos
from mysite.iclock.sendmail import *
from mysite.acc.models import *
from mysite.core.cmdproc import *
PAGE_LIMIT_VAR = 'l'
@login_required
def MapManageIndex(request):
	request.user.iclock_url_rel='../..'
	request.model = transactions
	unit=GetCalcUnit()
	dc={}
	try:
		colModel=[]
	except:
		colModel=[]
	return render_to_response('acc/MapManage_list.html',
							 {'latest_item_list': smart_str(dumps(dc)),
							'from': 1,
							'page': 1,
							'colModel':dumps(colModel),
							'limit': 10,
							'item_count': 4,
							'page_count': 1,
							'iclock_url_rel': request.user.iclock_url_rel
							},RequestContext(request, {}))
def iaccessIclock(request):#获取设备
	station=request.GET.get("station",0)
	mapid=request.GET.get("mapid",0)
#	if (station==0 or station=='0') and mapid>0:
#		MapIS=MapIaccessStyle.objects.all().values_list('iclock_id', flat=True)
#		iclockObj=iclock.objects.filter(Purpose__in=[1,3]).exclude(SN__in=MapIS)
#	elif mapid==0 or mapid=='0':
	iclockObj=iclock.objects.all().exclude(DelTag=1)#filter(Purpose__in=[1,3])
	ll="<table style='margin-left: 15px;'>"
	map=MapIaccessStyle.objects.all()
	kk={}
	for m in map:
		kk[m.iclock_id.SN]="%s"%m.styles
	for u in iclockObj:
		cmapfile="%sfiles/photo/device/iclock_%s.jpg" %(settings.ADDITION_FILE_ROOT,u.SN)
		if os.path.isfile(cmapfile):
			iclockImg="/iclock/file/photo/device/iclock_%s.jpg"%(u.SN)
		else:
			iclockImg="/media/img/device/iclock-none.jpg"
		if station==1 or station=='1':
			rr=u"<tr><td height='65px'><div style='z-index:1000;border:0px solid;width:50px;position:absolute;cursor:move;text-align:center;' id='station_photo_%s' name='station_%s' onclick=setmouse('station_photo_%s')><img src='%s' /><br/>%s</div></td></tr>"%(u.SN,u.SN,u.SN,iclockImg,u.Alias)
			if u.SN in kk.keys():
				try:
					mai=MapIaccessStyle.objects.get(iclock_id=u.SN,mapmanage_id=mapid)
					rr=u"<tr><td><div id='station_photo_%s' name='station_%s' ondblclick=delMapIclock('%s') onclick=setmouse('station_photo_%s') style='width:50px;z-index:1000;border:0px solid;text-align:center;%s'><img src='%s' alt='%s' title='双击移除该设备' /><br/>%s</div></td></tr>"%(u.SN,u.SN,mai.id,u.SN,mai.styles,iclockImg,mai.id,u.Alias)
				except:
					pass
		else:
			if u.SN in kk.keys():
				try:
					mai=MapIaccessStyle.objects.get(iclock_id=u.SN,mapmanage_id=mapid)
					rr=u"<tr><td><div id='station_photo_%s' name='station_%s' ondblclick=delMapIclock('%s') onclick=setmouse('station_photo_%s') style='width:50px;z-index:1000;border:0px solid;text-align:center;%s'><img src='%s' alt='%s' title='双击移除该设备' /><br/>%s</div></td></tr>"%(u.SN,u.SN,mai.id,u.SN,mai.styles,iclockImg,mai.id,u.Alias)
				except:
					rr=u""
			else:
				rr=u"<tr><td height='65px'><div style='z-index:1000;border:0px solid;width:50px;position:absolute;cursor:move;text-align:center;' id='station_photo_%s' name='station_%s' onclick=setmouse('station_photo_%s')><img src='%s' /><br/>%s</div></td></tr>"%(u.SN,u.SN,u.SN,iclockImg,u.Alias)
		ll+=rr
	ll+="</table>"
	return getJSResponse(smart_str(dumps(ll)))
def saveiclockstation(request):#保存样式
	k=request.POST.get('K').split(",")
	mapid=request.POST.get('mapid')
	for i in k:
		try:
			keys=i.split("@")
			map=MapIaccessStyle.objects.filter(iclock_id=keys[0].split("_")[2],mapmanage_id=mapid)
			styles="position:absolute;cursor:move;"
			if keys[1]!='':
				styles="%sleft:%s;"%(styles,keys[1])
			if keys[2]!='':
				styles="%stop:%s;"%(styles,keys[2])
			if len(map)>0:
				map[0].styles=styles
				map[0].save()
			else:
				sn=iclock.objects.get(SN=keys[0].split("_")[2])
				mapids=MapManage.objects.get(id=mapid)
				MapIaccessStyle(iclock_id=sn,mapmanage_id=mapids,styles=styles).save()
		except Exception,e:
			print e
			return getJSResponse({"ret":1,"message":""})
	return getJSResponse({"ret":0,"message":""})
def getMapManage(request):#获取地图
	MapM=MapManage.objects.all()
	ll="<ul>"
	i=0
	for m in MapM:
#		li=u"<li><a href='#id_mapmanage_%s' id='mapid_%s' alt='%s' onmouseup='$(\'#mapid_%s\').val(%s)'>%s</a><input type='hidden' id='mapid_%s' value='%s' /></li>"%(m.id,i,m.id,i,m.id,m.MapName,i,m.id)#<input type='hidden' id='mapid_%s' value='%s' />
		li=u"<li><a href='#id_mapmanage_%s' alt='%s' onmouseup='$(\"#mapid_%s\").val(%s);$(\"#mapids\").val(%s)'>%s</a><input type='hidden' id='mapid_%s' value='%s' /><input type='hidden' id='mapname_%s' value='%s' /><input type='hidden' id='maprem_%s' value='%s' /></li>"%(m.id,m.id,i,m.id,i,m.MapName,i,m.id,i,m.MapName,i,m.Remarks)#<input type='hidden' id='mapid_%s' value='%s' />

		ll+=li
		i+=1
	ll+="</ul><div>"
	for m in MapM:
		cmapfile="%sphoto/ditu/ditu_%s.jpg" %(settings.ADDITION_FILE_ROOT,m.id)
		if os.path.isfile(cmapfile):
			div=u"<div id='id_mapmanage_%s' style='z-index:90;'><img src='/iclock/file/photo/ditu/ditu_%s.jpg'></img></div>"%(m.id,m.id)
		else:
			div=u"<div id='id_mapmanage_%s' style='z-index:90;'><img src='/media/img/ditu.jpg'></img></div>"%(m.id)
		ll+=div+"</div>"
	return getJSResponse(smart_str(dumps(ll)))
@permission_required("iclock.MapManage_SetMap")
def saveSetMap(request):    #保存上传地图
	request.user.iclock_url_rel='../..'
	request.model = employee
	mapid=request.POST.get("mapid")
	if request.method == 'POST':
		f=request.FILES["fileToUpload"]
		from iclock.datamisc import saveUploadImage2
		fname=u"%s%s/%s/ditu_%s.jpg"%(settings.ADDITION_FILE_ROOT,'photo','ditu',mapid)
		saveUploadImage2(request, "fileToUpload", fname)
		return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')},mtype="text/plain")
def delMapIclock(request):#从地图移除设备
	try:
		mapStyid=request.POST.get('mapStyid')
		MapIaccessStyle.objects.get(id=mapStyid).delete()
	except Exception,e:
		print e
		return getJSResponse({"ret":1,"message": ""},mtype="text/plain")
	return getJSResponse({"ret":0,"message": ""},mtype="text/plain")
def delMap(request):#删除地图
	import os
	try:
		mapid=request.POST.get('mapid')
		try:
			file=u"%s%s/%s/ditu_%s.jpg"%(settings.ADDITION_FILE_ROOT,'photo','ditu',mapid)
			os.remove(file)
		except:
			pass
		MapIaccessStyle.objects.filter(mapmanage_id=mapid).delete()
		MapManage.objects.filter(id=mapid).delete()
	except Exception,e:
		print e
		return getJSResponse({"ret":1,"message": ""},mtype="text/plain")
	return getJSResponse({"ret":0,"message": ""},mtype="text/plain")
def removeMap(request):#清除地图
	import os
	try:
		mapid=request.POST.get('mapid')
		file=u"%s%s/%s/ditu_%s.jpg"%(settings.ADDITION_FILE_ROOT,'photo','ditu',mapid)
		os.remove(file)
		MapIaccessStyle.objects.filter(mapmanage_id=mapid).delete()
	except Exception,e:
		print e
		return getJSResponse({"ret":1,"message": ""},mtype="text/plain")
	return getJSResponse({"ret":0,"message": ""},mtype="text/plain")
@permission_required("iclock.iclock_SetIclockPhoto")
def saveSetIclock(request):    #上传设备图片
	SNs=request.POST.get("Iclockid").split(",")[1:]
	if request.method == 'POST':
		f=request.FILES["fileToUpload"]
		from iclock.datamisc import saveUploadImage3
		for s in SNs:
			fname=u"%s%s/%s/iclock_%s.jpg"%(settings.ADDITION_FILE_ROOT,'photo','device',s)
			saveUploadImage3(request, "fileToUpload", fname)
		return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')},mtype="text/plain")
@login_required
def Map_Monitor(request):
	request.user.iclock_url_rel='../..'
	request.model = MapManage
	return render_to_response('acc/Map_Monitor.html',
						RequestContext(request, {
						'from': id,
						'page': 1,
						'limit': 10,
						'item_count': 4,
						'page_count': 1,
						'iclock_url_rel': request.user.iclock_url_rel,
						}))
def iaccessStateIMG(request):#实时监控门禁状态图片
	MapM=MapManage.objects.all()
	ll="<table style='margin-left: 15px;'>"
	tr=""
	for i in range(4):
		cmapfile1="%smedia/img/iaccessDevice/Not-connected.gif"%(settings.ADDITION_FILE_ROOT)#未连接
		cmapfile2="%smedia/img/iaccessDevice/Doors-closed.gif"%(settings.ADDITION_FILE_ROOT)#门关闭
		cmapfile3="%smedia/img/iaccessDevice/Doors-open.gif"%(settings.ADDITION_FILE_ROOT)#门打开
		cmapfile4="%smedia/img/iaccessDevice/Illegal-open.gif"%(settings.ADDITION_FILE_ROOT)#报警信息
		if os.path.isfile(cmapfile1) and i==0:
			tr+=u"<tr><td style='height:65px;vertical-align:top;'><div style='width:60px;position:absolute;text-align:center;' ><img src='/media/img/iaccessDevice/%s' /><br/>未连接</div></td></tr>"%("Not-connected.gif")
		elif os.path.isfile(cmapfile2) and i==1:
			tr+=u"<tr><td style='height:65px;vertical-align:top;'><div style='width:60px;position:absolute;text-align:center;' ><img src='/media/img/iaccessDevice/%s' /><br/>门关闭</div></td></tr>"%("Doors-closed.gif")
		elif os.path.isfile(cmapfile3) and i==2:
			tr+=u"<tr><td style='height:65px;vertical-align:top;'><div style='width:60px;position:absolute;text-align:center;' ><img src='/media/img/iaccessDevice/%s' /><br/>门打开</div></td></tr>"%("Doors-open.gif")
		elif os.path.isfile(cmapfile4) and i==3:
			tr+=u"<tr><td style='height:65px;vertical-align:top;'><div style='width:60px;position:absolute;text-align:center;' ><img src='/media/img/iaccessDevice/%s' /><br/>报警信息</div></td></tr>"%("Illegal-open.gif")
		else:
			tr+=""
	ll+=tr+"</table>"
	return getJSResponse(smart_str(dumps(ll)))
@login_required
def MapRealLoad(request):#电子地图实时监控
	mapid=request.GET.get("mapid",0)
	iclockObj=iclock.objects.filter(Purpose__in=[1,3]).exclude(DelTag=1)
	ll=""
	bjxx=""
	map=MapIaccessStyle.objects.all()
	kk={}
	for m in map:
		kk[m.iclock_id.SN]="%s"%m.styles
	for u in iclockObj:
		if u.getDynState()==3:
			iclockImg="/media/img/iaccessDevice/Not-connected.gif"
		elif u.getDynState()==1 and u.State!=4 and u.State!=5 and u.State!=6 and u.State!=7 and u.State!=8:
			iclockImg="/media/img/iaccessDevice/Doors-closed.gif"
		elif u.State==4:
			iclockImg="/media/img/iaccessDevice/Doors-open.gif"
		elif u.State==5:
			iclockImg="/media/img/iaccessDevice/Doors-closed.gif"
		elif u.State==6:
			iclockImg="/media/img/iaccessDevice/Illegal-open.gif"
			bjxx=u"胁迫报警"
		elif u.State==7:
			iclockImg="/media/img/iaccessDevice/Illegal-open.gif"
			bjxx=u"门被意外打开"
		elif u.State==8:
			iclockImg="/media/img/iaccessDevice/Illegal-open.gif"
			bjxx=u"机器被拆除"
		else:
			iclockImg="/media/img/iaccessDevice/Not-connected.gif"

		if u.SN in kk.keys():
			try:
				mai=MapIaccessStyle.objects.get(iclock_id=u.SN,mapmanage_id=mapid)
				rr=u"<div name='station_%s' style='border:0px solid;width:60px;z-index:100;text-align:center;%s'><img src='%s' alt='%s' title='' /><br/>%s<br/><font color='red'>%s</font></div>"%(u.SN,mai.styles,iclockImg,mai.id,u.Alias,bjxx)
			except:
				rr=u""
		else:
			rr=u""
		ll+=rr
	try:#添加脱机日志
		nowtime=datetime.datetime.now()
		device=iclock.objects.all().exclude(DelTag=1).exclude(LastActivity=None)
		for de in device:
			aObj=cache.get("iclock_"+de.SN)
			if aObj and aObj.LastActivity>de.LastActivity:
				de.LastActivity=aObj.LastActivity
			d=nowtime-de.LastActivity
			if d>datetime.timedelta(0,settings.MAX_DEVICES_STATE):
				offline=iaccessoplog.objects.filter(SN=de.SN,Message=60,OPTime__gte=de.LastActivity)
				if offline:
					pass
				else:
					oplog(SN=de, admin=0, OP=3, OPTime=nowtime,
								Object=60, Param1=0, Param2=0, Param3=0).save()
					iaccessoplog(SN=de, Message=60, Even=3, OPTime=nowtime,
								Object=0, Param1=0, Param2=0, Param3=0).save()

	except Exception,e:
		print e,'++++++++'

	return getJSResponse(smart_str(dumps(ll)))
@login_required
def RealMonitorIaccess(request):#门禁实时记录监控
	request.user.iclock_url_rel='../..'
#	request.model = MapManage
	return render(request,'RealMonitorIaccess.html',
						 {
						'from': id,
						'page': 1,
						'limit': 10,
						'item_count': 4,
						'page_count': 1,
						'iclock_url_rel': request.user.iclock_url_rel,
						})
@login_required
def iaccessDevReports(request):#门禁设备与记录报表
	request.user.iclock_url_rel='../..'
	settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
	limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
	return render_to_response('acc/iaccessDevReports.html',
						RequestContext(request, {
						'from': id,
						'page': 1,
						'limit': limit,
						'item_count': 4,
						'page_count': 1,
						'iclock_url_rel': request.user.iclock_url_rel,
						}))


@login_required
#门禁上传设置到设备---mah
def setToDevice(request):
	SNS=request.POST.get("SNS",'')
	model=request.POST.get("model",'')
	snlist=[i for i in SNS.split(',')]
	return getJSResponse({"ret":0,"message":u"%s" % _(u"当前版本系统支持自动传输，不需要手动传输")})
	if model=='' or SNS=='':
		return getJSResponse({"ret":1,"message":u"%s" % _("Save Fail")})
	else:
		if model=='ACTimeZones':
			uploadACTimeZones(snlist)
		elif model=='ACGroup':
			uploadACGroup(snlist)
		elif model=='ACUnlockComb':
			uploadACUnlockComb(snlist)
		elif model=='ACCSetHoliday':
			uploadACCSetHoliday(snlist)
	return getJSResponse({"ret":0,"message":u"%s" % _("Save Success")})

@login_required
#监控记录表
def getIacc_MonitorReport(request):
	if request.method=="GET":
		rt,fieldNames,fieldCaptions=getIacc_MonitorFields()
		disabledCols=FetchDisabledFields(request.user,'iacc_Monitor')
		r=[]
		it=0
		for field in fieldNames:
			if field=='userid' or field=='UserID':
				r.append({"name":"UserID",'hidden':True})
			else:
				r.append({"name":field,'label':fieldCaptions[it],'width':150})
			it=it+1
		rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
		return getJSResponse(rs)
	else:
		SNs=request.GET.get('SNs',"")
		Message=request.GET.get('Object',"")
		st=request.GET.get('startDate','')
		et="%s 23:59:59"%request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
		r=getIacc_MonitorReportItem(request,SNs,Message,st,et)
		rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
		return getJSResponse(rs)

def getIacc_MonitorReportItem(request,SNs,Message,d1,d2):
	#排序
	sidx=""
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	ot=sidx.split(',')
	SNid=SNs.split(',')
	if len(ot)<=0 or ot[0]=='':
		ot=['OPTime']
	if Message!='0':
		iacclog=iaccessoplog.objects.filter(SN__in=SNid,OPTime__gte=d1,OPTime__lte=d2,Message=Message).order_by(*ot)
	else:
		iacclog=iaccessoplog.objects.filter(SN__in=SNid,OPTime__gte=d1,OPTime__lte=d2).order_by(*ot)
	Result={}
	re=[]
	#分页
	try:
		if request.method=='GET':
			offset = int(request.GET.get('page', 1))
		else:
			offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', settings.PAGE_LIMIT))  #导出时使用
	paginator = Paginator(iacclog, limit)
	item_count = paginator.count
	pgList = paginator.page(offset)
	page_count=paginator.num_pages
	r,fieldNames,fieldCaptions=getIacc_MonitorFields()
	disabledCols=FetchDisabledFields(request.user,'iacc_Monitor')
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['fieldnames']=fieldNames
	Result['fieldcaptions']=fieldCaptions
	Result['disableCols']=disabledCols
	for t in pgList.object_list:
		rmdAttday=r.copy()
		for y in rmdAttday.keys():
			rmdAttday[y]=''
		ePIN=t.Object
		if ePIN!='0':
			e=employee.objByPIN(ePIN)
			rmdAttday['userid']=e.id
			rmdAttday['badgenumber']=e.PIN
			rmdAttday['username']=e.EName
			rmdAttday['deptid']=e.Dept().DeptName
		else:
			rmdAttday['userid']=""
			rmdAttday['badgenumber']=""
			rmdAttday['username']=""
			rmdAttday['deptid']=""
		rmdAttday['SN']=t.SN.SN
		rmdAttday['Alias']=t.SN.Alias
		rmdAttday['OPTime']=t.OPTime
		rmdAttday['Message']=t.ObjName()
		re.append(rmdAttday.copy())
	Result['datas']=re
	return Result
#报警记录表
@login_required
def getIacc_AlarmReport(request):
	if request.method=="GET":
		rt,fieldNames,fieldCaptions=getIacc_AlarmFields()
		disabledCols=FetchDisabledFields(request.user,'iacc_Alarm')
		r=[]
		it=0
		for field in fieldNames:
			r.append({"name":field,'label':fieldCaptions[it],'width':150})
			it=it+1
		rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
		return getJSResponse(rs)
	else:
		SNs=request.GET.get('SNs',"")
		Message=request.GET.get('Object',"")
		st=request.GET.get('startDate','')
		et="%s 23:59:59"%request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
		r=getIacc_AlarmReportItem(request,SNs,Message,st,et)
		rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
		return getJSResponse(rs)
def getIacc_AlarmReportItem(request,SNs,Message,d1,d2):
	#排序
	sidx=""
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	ot=sidx.split(',')
	SNid=SNs.split(',')
	if len(ot)<=0 or ot[0]=='':
		ot=['OPTime']
	if Message!='0':
		iacclog=iaccessoplog.objects.filter(SN__in=SNid,OPTime__gte=d1,OPTime__lte=d2,Message=Message).order_by(*ot)
	else:
		iacclog=iaccessoplog.objects.filter(SN__in=SNid,OPTime__gte=d1,OPTime__lte=d2,Message__in=[59,54,55]).order_by(*ot)
	Result={}
	re=[]
	#分页
	try:
		if request.method=='GET':
			offset = int(request.GET.get('page', 1))
		else:
			offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', settings.PAGE_LIMIT))  #导出时使用
	paginator = Paginator(iacclog, limit)
	item_count = paginator.count
	pgList = paginator.page(offset)
	page_count=paginator.num_pages
	r,fieldNames,fieldCaptions=getIacc_AlarmFields()
	disabledCols=FetchDisabledFields(request.user,'iacc_Alarm')
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['fieldnames']=fieldNames
	Result['fieldcaptions']=fieldCaptions
	Result['disableCols']=disabledCols
	for t in pgList.object_list:
		rmdAttday=r.copy()
		for y in rmdAttday.keys():
			rmdAttday[y]=''
		rmdAttday['SN']=t.SN.SN
		rmdAttday['Alias']=t.SN.Alias
		rmdAttday['OPTime']=t.OPTime
		rmdAttday['Message']=t.ObjName()
		re.append(rmdAttday.copy())
	Result['datas']=re
	return Result
#用户权限表
@login_required
def getIacc_UserRightsReport(request):
	if request.method=="GET":
		rt,fieldNames,fieldCaptions=getIacc_UserRightsFields()
		disabledCols=FetchDisabledFields(request.user,'iacc_UserRights')
		r=[]
		it=0
		for field in fieldNames:
			if field=='userid' or field=='UserID':
				r.append({"name":"UserID",'hidden':True})
			else:
				r.append({"name":field,'label':fieldCaptions[it],'width':100})
			it=it+1
		rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
		return getJSResponse(rs)
	else:
		SNs=request.GET.get('SNs',"")
		st=request.GET.get('startDate','')
		et="%s 23:59:59"%request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
		r=getIacc_UserRightsReportItem(request,SNs,st,et)
		rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
		return getJSResponse(rs)
def getIacc_UserRightsReportItem(request,SNs,d1,d2):
	#排序
	sidx=""
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	ot=sidx.split(',')
	SNid=SNs.split(',')
	if len(ot)<=0 or ot[0]=='':
		ot=['setTime']
	UserACC=UserACCDevice.objects.filter(SN__in=SNid).order_by(*ot)#,setTime__gte=d1,setTime__lte=d2
	Result={}
	re=[]
	#分页
	try:
		if request.method=='GET':
			offset = int(request.GET.get('page', 1))
		else:
			offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', settings.PAGE_LIMIT))  #导出时使用
	paginator = Paginator(UserACC, limit)
	item_count = paginator.count
	pgList = paginator.page(offset)
	page_count=paginator.num_pages
	r,fieldNames,fieldCaptions=getIacc_UserRightsFields()
	disabledCols=FetchDisabledFields(request.user,'iacc_UserRights')
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['fieldnames']=fieldNames
	Result['fieldcaptions']=fieldCaptions
	Result['disableCols']=disabledCols
	for t in pgList.object_list:
		eid=int(t.UserID_id)
		e=employee.objByID(eid)
		rmdAttday=r.copy()
		for y in rmdAttday.keys():
			rmdAttday[y]=''
		rmdAttday['userid']=eid
		rmdAttday['badgenumber']=e.PIN
		rmdAttday['username']=e.EName
		rmdAttday['deptid']=e.Dept().DeptName
		rmdAttday['SN']=t.SN.SN
		rmdAttday['Alias']=t.SN.Alias
		try:
			UserAC=UserACPrivilege.objects.get(UserID=eid)
			if UserAC.IsUseGroup==1:
				rmdAttday['IsUseGroup']=_(u"使用组设置")
				rmdAttday['ACGroupID']=u'%s(%s)'%(UserAC.ACGroupID_id,UserAC.ACGroupID.Name)
				rmdAttday['VerifyType']=UserAC.ACGroupID.get_VerifyType_display()
				ACG=ACGroup.objects.get(GroupID=UserAC.ACGroupID_id)
				try:
					rmdAttday['TimeZone1']=u'%s(%s)'%(timezones.objByID(ACG.TimeZone1).id,timezones.objByID(ACG.TimeZone1).Name)
				except:
					rmdAttday['TimeZone1']=""
				try:
					rmdAttday['TimeZone2']=u'%s(%s)'%(timezones.objByID(ACG.TimeZone2).id,timezones.objByID(ACG.TimeZone2).Name)
				except:
					rmdAttday['TimeZone2']=""
				try:
					rmdAttday['TimeZone3']=u'%s(%s)'%(timezones.objByID(ACG.TimeZone3).id,timezones.objByID(ACG.TimeZone3).Name)
				except:
					rmdAttday['TimeZone3']=""
			else:
				rmdAttday['IsUseGroup']=_(u"自定义时间段")
				rmdAttday['ACGroupID']=""
				rmdAttday['VerifyType']=""
				try:
					rmdAttday['TimeZone1']=u'%s(%s)'%(timezones.objByID(UserAC.TimeZone1).id,timezones.objByID(UserAC.TimeZone1).Name)
				except:
					rmdAttday['TimeZone1']=""
				try:
					rmdAttday['TimeZone2']=u'%s(%s)'%(timezones.objByID(UserAC.TimeZone2).id,timezones.objByID(UserAC.TimeZone2).Name)
				except:
					rmdAttday['TimeZone2']=""
				try:
					rmdAttday['TimeZone3']=u'%s(%s)'%(timezones.objByID(UserAC.TimeZone3).id,timezones.objByID(UserAC.TimeZone3).Name)
				except:
					rmdAttday['TimeZone3']=""
		except Exception,e:
			print 99999999,e
			rmdAttday['IsUseGroup']=""
			rmdAttday['ACGroupID']=""
			rmdAttday['TimeZone1']=""
			rmdAttday['TimeZone2']=""
			rmdAttday['TimeZone3']=""

		re.append(rmdAttday.copy())
	Result['datas']=re
	return Result

@login_required
#存储人员门禁关联
def saveUserACCDevice(request):
	SNS=request.POST.get("SNS",'')
	UserIDs=request.POST.get("UserIDs",'')
	DeptIDs=request.POST.get("DeptIDs",'')
	isContainedChild=request.POST.get("isContainChild",'0')
	lookup_params={}
	snlist=[]
	snlist=[i for i in SNS.split(',')]
	if UserIDs:
		lookup_params['id__in']=[int(i) for i in UserIDs.split(',')]
		emps=employee.objects.filter(**lookup_params)
		sns=iclock.objects.filter(SN__in=snlist)
		for emp in emps:
			UserACCDevice.objects.filter(UserID=emp).delete()
			for sn in sns:
				try:
					uac=UserACCDevice(UserID=emp,SN=sn).save()
					adminLog(time=datetime.datetime.now(),User=request.user, action=_(u"ADD"), object=uac, model=UserACCDevice._meta.verbose_name).save(force_insert = True)#
				except Exception,e:
					print e
					pass
	else:
		deptidlist=[int(i) for i in DeptIDs.split(',')]
		deptids=deptidlist
		if isContainedChild=="1":   #是否包含下级部门
			deptids=[]
			for d in deptidlist:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		emps=employee.objects.filter(DeptID__in=deptids)#.values_list('id', flat=True).order_by('id')
	sns=iclock.objects.filter(SN__in=snlist)
	for emp in emps:
		UserACCDevice.objects.filter(UserID=emp).delete()
		for sn in sns:
			try:
				uac=UserACCDevice(UserID=emp,SN=sn).save()
				adminLog(time=datetime.datetime.now(),User=request.user, action=_(u"ADD"), object=uac, model=UserACCDevice._meta.verbose_name).save(force_insert = True)#
			except Exception,e:
				print 8888,e
				pass

	return getJSResponse({"ret":0,"message":u"%s" % _("Save Success")})

#上传人员到设备
@login_required
def empToDevice(request):
	uploadUserACDevCmd_new()
	return getJSResponse({"ret":0,"message":u"%s" % _("Save Success")})
	#print 1111111
	#users=UserACCDevice.objects.all()#filter(UserID=self.UserID)
	#devs=iclock.objects.all()
	#for dev in devs:
	#	users=UserACCDevice.objects.filter(SN=dev)
	#	uploadUserACDevCmd_new()
@login_required
def iaccessEmpReports(request):#门禁人员与记录报表
	request.user.iclock_url_rel='../..'
	settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
	limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
	return render_to_response('acc/iaccessEmpReports.html',
						RequestContext(request, {
						'from': id,
						'page': 1,
						'limit': limit,
						'item_count': 4,
						'page_count': 1,
						'iclock_url_rel': request.user.iclock_url_rel,
						}))

#记录明细表
@login_required
def getIacc_RecordDetailsReport(request):
	if request.method=="GET":
		rt,fieldNames,fieldCaptions=getIacc_RecordDetailsFields()
		disabledCols=FetchDisabledFields(request.user,'iacc_RecordDetails')
		r=[]
		it=0
		for field in fieldNames:
			if field=='userid' or field=='UserID':
				r.append({"name":"UserID",'hidden':True})
			else:
				r.append({"name":field,'label':fieldCaptions[it],'width':150})
			it=it+1
		rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
		return getJSResponse(rs)
	else:
		deptIDs=request.GET.get('deptIDs',"")
		userIDs=request.GET.get('UserIDs',"")
		st=request.GET.get('startDate','')
		et="%s 23:59:59"%request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
		r=getIacc_RecordDetailsReportItem(request,deptIDs,userIDs,st,et)
		rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
		return getJSResponse(rs)
def getIacc_RecordDetailsReportItem(request,deptids,userids,d1,d2):
	#排序
	sidx=""
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	ot=sidx.split(',')
	icls=iclock.objects.filter(ProductType__in=[4,5,15]).values_list('SN', flat=True)
	if len(userids)>0 and userids!='null':
		ids=userids.split(',')
		if len(ot)<=0 or ot[0]=='':
			ot=['UserID__DeptID','UserID__PIN','-TTime']
		trans=transactions.objects.filter(UserID__in=ids,TTime__gte=d1,TTime__lte=d2,SN__in=icls).order_by(*ot)
	elif len(deptids)>0:
		isContainedChild=request.GET.get('isContainChild','0')
		deptIDS=deptids.split(',')
		deptids=deptIDS
		if isContainedChild=="1": #是否包含下级部门
			deptids=[]
			for d in deptIDS:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		if len(ot)<=0 or ot[0]=='':
			ot=['UserID__DeptID','UserID__PIN','-TTime']
		trans=transactions.objects.filter(UserID__DeptID__in=deptids,TTime__gte=d1,TTime__lte=d2,SN__in=icls).order_by(*ot)
	Result={}
	re=[]
	#分页
	try:
		if request.method=='GET':
			offset = int(request.GET.get('page', 1))
		else:
			offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', settings.PAGE_LIMIT))  #导出时使用
	paginator = Paginator(trans, limit)
	item_count = paginator.count
	pgList = paginator.page(offset)
	page_count=paginator.num_pages
	r,fieldNames,fieldCaptions=getIacc_RecordDetailsFields()
	disabledCols=FetchDisabledFields(request.user,'iacc_RecordDetails')
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['fieldnames']=fieldNames
	Result['fieldcaptions']=fieldCaptions
	Result['disableCols']=disabledCols
	for t in pgList.object_list:
		eid=int(t.UserID_id)
		e=employee.objByID(eid)
		rmdAttday=r.copy()
		for y in rmdAttday.keys():
			rmdAttday[y]=''
		rmdAttday['userid']=eid
		rmdAttday['deptid']=e.Dept().DeptName
		rmdAttday['badgenumber']=e.PIN
		rmdAttday['username']=e.EName
		rmdAttday['TTime']=t.TTime
		rmdAttday['SN']=u'%s'%t.Device()
		rmdAttday['VerifyType']=t.getComVerifys()
		try:
			rmdAttday['Object']=iaccessoplog.objects.get(SN=t.SN.SN,OPTime=t.TTime).ObjName()#,Object__in=[4,5]
		except:
			rmdAttday['Object']=""
		re.append(rmdAttday.copy())
	Result['datas']=re
	return Result
#记录汇总表
@login_required
def getIacc_SummaryRecordReport(request):
	if request.method=="GET":
		rt,fieldNames,fieldCaptions=getIacc_SummaryRecordFields()
		disabledCols=FetchDisabledFields(request.user,'iacc_SummaryRecord')
		r=[]
		it=0
		for field in fieldNames:
			if field=='userid' or field=='UserID':
				r.append({"name":"UserID",'hidden':True})
			else:
				r.append({"name":field,'label':fieldCaptions[it],'width':180})
			it=it+1
		rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
		return getJSResponse(rs)
	else:
		deptIDs=request.GET.get('deptIDs',"")
		userIDs=request.GET.get('UserIDs',"")
		st=request.GET.get('startDate','')
		et="%s 23:59:59"%request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
		r=getIacc_SummaryRecordReportItem(request,deptIDs,userIDs,st,et)
		rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
		return getJSResponse(rs)
def getIacc_SummaryRecordReportItem(request,deptids,userids,d1,d2):
	#排序
	sidx=""
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	ot=sidx.split(',')
	icls=iclock.objects.filter(ProductType__in=[4,5,15]).values_list('SN', flat=True)
	if len(userids)>0 and userids!='null':
		ids=userids.split(',')
		if len(ot)<=0 or ot[0]=='':
			ot=['UserID__DeptID','UserID__PIN','-TTime']
		trans=transactions.objects.filter(UserID__DeptID__in=deptids,TTime__gte=d1,TTime__lte=d2,SN__in=icls).order_by(*ot)
	elif len(deptids)>0:
		isContainedChild=request.GET.get('isContainChild','0')
		deptIDS=deptids.split(',')
		deptids=deptIDS
		if isContainedChild=="1": #是否包含下级部门
			deptids=[]
			for d in deptIDS:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		if len(ot)<=0 or ot[0]=='':
			ot=['UserID__DeptID','UserID__PIN','-TTime']
		trans=transactions.objects.filter(UserID__DeptID__in=deptids,TTime__gte=d1,TTime__lte=d2,SN__in=icls).order_by(*ot)
	trans=trans.extra(where=['id IN ( SELECT MIN(id) FROM checkinout GROUP BY userid,SN)'])
	Result={}
	re=[]
	#分页
	try:
		if request.method=='GET':
			offset = int(request.GET.get('page', 1))
		else:
			offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', settings.PAGE_LIMIT))  #导出时使用
	paginator = Paginator(trans, limit)
	item_count = paginator.count
	pgList = paginator.page(offset)
	page_count=paginator.num_pages
	r,fieldNames,fieldCaptions=getIacc_SummaryRecordFields()
	disabledCols=FetchDisabledFields(request.user,'iacc_SummaryRecord')
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['fieldnames']=fieldNames
	Result['fieldcaptions']=fieldCaptions
	Result['disableCols']=disabledCols
	for t in pgList.object_list:
		eid=int(t.UserID_id)
		e=employee.objByID(eid)
		rmdAttday=r.copy()
		for y in rmdAttday.keys():
			rmdAttday[y]=''
		rmdAttday['userid']=eid
		rmdAttday['deptid']=e.Dept().DeptName
		rmdAttday['badgenumber']=e.PIN
		rmdAttday['username']=e.EName
		rmdAttday['OutCount']=transactions.objects.filter(UserID=eid,SN=t.SN.SN).count()
		rmdAttday['SN']=u'%s'%t.Device()

		re.append(rmdAttday.copy())
	Result['datas']=re
	return Result

#用户权限明细
@login_required
def getIacc_EmpUserRightsReport(request):
	if request.method=="GET":
		rt,fieldNames,fieldCaptions=getIacc_EmpUserRightsFields()
		disabledCols=FetchDisabledFields(request.user,'iacc_EmpUserRights')
		r=[]
		it=0
		for field in fieldNames:
			if field=='userid' or field=='UserID':
				r.append({"name":"UserID",'hidden':True})
			elif field=='SN':
				r.append({"name":field,'label':fieldCaptions[it],'width':170})
			else:
				r.append({"name":field,'label':fieldCaptions[it],'width':100})
			it=it+1
		rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
		return getJSResponse(rs)
	else:
		deptIDs=request.GET.get('deptIDs',"")
		userIDs=request.GET.get('UserIDs',"")
		st=request.GET.get('startDate','')
		et="%s 23:59:59"%request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
		r=getIacc_EmpUserRightsReportItem(request,deptIDs,userIDs,st,et)
		rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
		return getJSResponse(rs)
def getIacc_EmpUserRightsReportItem(request,deptids,userids,d1,d2):
	#排序
	sidx=""
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	ot=sidx.split(',')
	#,TTime__gte=d1,TTime__lte=d2,SN__in=icls
	if len(userids)>0 and userids!='null':
		ids=userids.split(',')
		if len(ot)<=0 or ot[0]=='':
			ot=['UserID__DeptID','UserID__PIN']
		UserACP=UserACPrivilege.objects.filter(UserID__in=ids).order_by(*ot)
	elif len(deptids)>0:
		isContainedChild=request.GET.get('isContainChild','0')
		deptIDS=deptids.split(',')
		deptids=deptIDS
		if isContainedChild=="1": #是否包含下级部门
			deptids=[]
			for d in deptIDS:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		if len(ot)<=0 or ot[0]=='':
			ot=['UserID__DeptID','UserID__PIN']
		UserACP=UserACPrivilege.objects.filter(UserID__DeptID__in=deptids).order_by(*ot)
	Result={}
	re=[]
	#分页
	try:
		if request.method=='GET':
			offset = int(request.GET.get('page', 1))
		else:
			offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', settings.PAGE_LIMIT))  #导出时使用
	paginator = Paginator(UserACP, limit)
	item_count = paginator.count
	pgList = paginator.page(offset)
	page_count=paginator.num_pages
	r,fieldNames,fieldCaptions=getIacc_EmpUserRightsFields()
	disabledCols=FetchDisabledFields(request.user,'iacc_EmpUserRights')
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['fieldnames']=fieldNames
	Result['fieldcaptions']=fieldCaptions
	Result['disableCols']=disabledCols
	for t in pgList.object_list:
		eid=int(t.UserID_id)
		e=employee.objByID(eid)
		rmdAttday=r.copy()
		for y in rmdAttday.keys():
			rmdAttday[y]=''
		rmdAttday['userid']=eid
		rmdAttday['badgenumber']=e.PIN
		rmdAttday['username']=e.EName
		rmdAttday['deptid']=e.Dept().DeptName
		try:
			UserACC=UserACCDevice.objects.filter(UserID=eid)
			sn=""
			i=0
			for ua in UserACC:
				if i>=1:
					sn+=","
				sn+=(u'%s(%s)'%(ua.SN_id,ua.SN.Alias))
				i+=1
			rmdAttday['SN']=sn
		except:
			rmdAttday['SN']=""
		if t.IsUseGroup==1:
			rmdAttday['IsUseGroup']=_(u"使用组设置")
			rmdAttday['ACGroupID']=u'%s(%s)'%(t.ACGroupID_id,t.ACGroupID.Name)
			rmdAttday['VerifyType']=t.ACGroupID.get_VerifyType_display()
			ACG=ACGroup.objects.get(GroupID=t.ACGroupID_id)
			try:
				rmdAttday['TimeZone1']=u'%s(%s)'%(timezones.objByID(ACG.TimeZone1).id,timezones.objByID(ACG.TimeZone1).Name)
			except:
				rmdAttday['TimeZone1']=""
			try:
				rmdAttday['TimeZone2']=u'%s(%s)'%(timezones.objByID(ACG.TimeZone2).id,timezones.objByID(ACG.TimeZone2).Name)
			except:
				rmdAttday['TimeZone2']=""
			try:
				rmdAttday['TimeZone3']=u'%s(%s)'%(timezones.objByID(ACG.TimeZone3).id,timezones.objByID(ACG.TimeZone3).Name)
			except:
				rmdAttday['TimeZone3']=""
		else:
			rmdAttday['IsUseGroup']=_(u"自定义时间段")
			rmdAttday['ACGroupID']=""
			rmdAttday['VerifyType']=""
			try:
				rmdAttday['TimeZone1']=u'%s(%s)'%(timezones.objByID(t.TimeZone1).id,timezones.objByID(t.TimeZone1).Name)
			except:
				rmdAttday['TimeZone1']=""
			try:
				rmdAttday['TimeZone2']=u'%s(%s)'%(timezones.objByID(t.TimeZone2).id,timezones.objByID(t.TimeZone2).Name)
			except:
				rmdAttday['TimeZone2']=""
			try:
				rmdAttday['TimeZone3']=u'%s(%s)'%(timezones.objByID(t.TimeZone3).id,timezones.objByID(t.TimeZone3).Name)
			except:
				rmdAttday['TimeZone3']=""
		re.append(rmdAttday.copy())
	Result['datas']=re
	return Result
#用户设备
@login_required
def getIacc_EmpDeviceReport(request):
	if request.method=="GET":
		rt,fieldNames,fieldCaptions=getIacc_EmpDeviceFields()
		disabledCols=FetchDisabledFields(request.user,'iacc_EmpDevice')
		r=[]
		it=0
		for field in fieldNames:
			if field=='userid' or field=='UserID':
				r.append({"name":"UserID",'hidden':True})
			elif field=='SN':
				r.append({"name":field,'label':fieldCaptions[it],'width':170})
			else:
				r.append({"name":field,'label':fieldCaptions[it],'width':100})
			it=it+1
		rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
		return getJSResponse(rs)
	else:
		deptIDs=request.GET.get('deptIDs',"")
		userIDs=request.GET.get('UserIDs',"")
		st=request.GET.get('startDate','')
		et="%s 23:59:59"%request.GET.get('endDate','')
		st=datetime.datetime.strptime(st,'%Y-%m-%d')
		et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
		r=getIacc_EmpDeviceReportItem(request,deptIDs,userIDs,st,et)
		rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
		return getJSResponse(rs)
def getIacc_EmpDeviceReportItem(request,deptids,userids,d1,d2):
	#排序
	sidx=""
	if request.GET.has_key('sidx'):
		sidx = request.GET.get('sidx','')
	else:
		sidx = request.POST.get('sidx','')
	ot=sidx.split(',')
	#,TTime__gte=d1,TTime__lte=d2,SN__in=icls
	if len(userids)>0 and userids!='null':
		ids=userids.split(',')
		if len(ot)<=0 or ot[0]=='':
			ot=['UserID__DeptID','UserID__PIN']
		UserACC=UserACCDevice.objects.filter(UserID__in=ids).order_by(*ot)
	elif len(deptids)>0:
		isContainedChild=request.GET.get('isContainChild','0')
		deptIDS=deptids.split(',')
		deptids=deptIDS
		if isContainedChild=="1": #是否包含下级部门
			deptids=[]
			for d in deptIDS:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		if len(ot)<=0 or ot[0]=='':
			ot=['UserID__DeptID','UserID__PIN']
		UserACC=UserACCDevice.objects.filter(UserID__DeptID__in=deptids).order_by(*ot)
	Result={}
	re=[]
	#分页
	try:
		if request.method=='GET':
			offset = int(request.GET.get('page', 1))
		else:
			offset = int(request.POST.get('page', 1))
	except:
		offset=1
	limit= int(request.POST.get('rows', settings.PAGE_LIMIT))  #导出时使用
	paginator = Paginator(UserACC, limit)
	item_count = paginator.count
	pgList = paginator.page(offset)
	page_count=paginator.num_pages
	r,fieldNames,fieldCaptions=getIacc_EmpDeviceFields()
	disabledCols=FetchDisabledFields(request.user,'iacc_EmpDevice')
	Result['item_count']=item_count
	Result['page']=offset
	Result['limit']=limit
	Result['from']=(offset-1)*limit+1
	Result['page_count']=page_count
	Result['fieldnames']=fieldNames
	Result['fieldcaptions']=fieldCaptions
	Result['disableCols']=disabledCols
	for t in pgList.object_list:
		eid=int(t.UserID_id)
		e=employee.objByID(eid)
		rmdAttday=r.copy()
		for y in rmdAttday.keys():
			rmdAttday[y]=''
		rmdAttday['userid']=eid
		rmdAttday['badgenumber']=e.PIN
		rmdAttday['username']=e.EName
		rmdAttday['deptid']=e.Dept().DeptName
		rmdAttday['SN']=u'%s(%s)'%(t.SN_id,t.SN.Alias)
		re.append(rmdAttday.copy())
	Result['datas']=re
	return Result

