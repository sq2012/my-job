#coding=utf-8
from mysite.iclock.models import *
from mysite.meeting.models import *
from django.utils.encoding import smart_str
from mysite.iclock.datautils import *
from django.shortcuts import render_to_response,render
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from mysite.iclock.dataproc import trunc
from django.core.paginator import Paginator
#import json

MAX_REALTIME_COUNT=50
"""实时会议记录 """
@login_required
def newTransLog(request):
#	device=getDevice(request.REQUEST.get('SN', ""))
	meetingids=request.GET.get('meetingid', "")
	Flag=False
	result={}
	lasttid=int(request.GET.get("lasttid","-1"))
	#lastdid=int(request.REQUEST.get("lastdid","-1"))
	if lasttid==-1:
		recordColModel=[
		{'name':'id','hidden':True},
		{'name':'TTime','sortable':False,'width':120,'align':'center','label':unicode(_(u'时间'))},
		{'name':'PIN','sortable':False,'width':120,'label':unicode(_(u'工号'))},
		{'name':'EName','sortable':False,'width':140,'label':unicode(_(u'姓名'))},
		{'name':'DeptName','sortable':False,'width':240,'label':unicode(_(u'部门名称'))},
		{'name':'Device','sortable':False,'width':200,'label':unicode(_(u'设备名称'))}
		]
		
		meetModel=[
		{'name':'id','hidden':True},
		{'name':'MeetID','sortable':False,'width':100,'label':unicode(_(u'会议编号'))},
		{'name':'conferenceTitle','sortable':False,'width':120,'label':unicode(_(u'会议名称'))},
		{'name':'MeetContents','sortable':False,'width':140,'label':unicode(_(u'会议内容'))},
		{'name':'LocationID','sortable':False,'width':150,'label':unicode(_(u'会议室'))},
		{'name':'Starttime','sortable':False,'width':80,'label':unicode(_(u'开始时间'))},
		{'name':'Endtime','sortable':False,'width':80,'label':unicode(_(u'结束时间'))},
		{'name':'State','sortable':False,'width':80,'label':unicode(_(u'状态'))},
		{'name':'Should','sortable':False,'width':60,'label':unicode(_(u'应到'))},
		{'name':'Real','sortable':False,'width':60,'label':unicode(_(u'实到'))},
		{'name':'absent','sortable':False,'width':60,'label':unicode(_(u'缺席'))},
		]
		
		cc={}
		cc['recordColModel']=dumps(recordColModel)
		cc['meetModel']=dumps(meetModel)
		#print cc
		
		return render(request,"meeting/dlogcheck.html",cc)#render_to_response("meeting/dlogcheck.html",cc,RequestContext(request, {}))
	logs=[]
	meet_id=int(request.GET.get("meet","-1"))
	
#	if (cache.get("%s_haslogs_%s"%(settings.UNIT,request.user.pk))<>cache.get("%s_logstamp_"%(settings.UNIT))) or lasttid==0:
#		cache.set("%s_haslogs_%s"%(settings.UNIT,request.user.pk),cache.get("%s_logstamp_"%(settings.UNIT)))




#	只能监控所能管理的人的实时记录,会议系统取消此严格要求
	SN=iclock.objects.filter(ProductType=1).values("SN")
	logs=transactions.objects.filter(id__gt=lasttid).filter(SN__in=SN).order_by("id")
	if meet_id>0:
		meet=Meet.objByID(meet_id)
		room=meet.LocationID
		qs=Meet_details.objects.filter(MeetID=meet_id).values('UserID')
		logs=logs.filter(UserID__in=qs)
		if room:
			iclockSN=meet_devices.objects.filter(LocationID=room).values('SN')
			if iclockSN:
				logs=logs.filter(SN__in=iclockSN)
	if lasttid==0:
		nt=datetime.datetime.now()
		d1=trunc(nt)
		logs=logs.filter(TTime__gte=d1)
	else:	
		logs=logs[:MAX_REALTIME_COUNT]
	#if logs: lasttid=logs[:-1].id
#	if lasttid==0:
#		logs=[]
	lines=[]
	lssttid=0
	uid=0
	empdata={}
	devs=''
	times=''
	for l in logs:
		line={}
		line['id']=l.id
		lasttid=max(l.id,lasttid)
		uid=l.UserID_id
		line['PIN']="%s"%l.employee().PIN
		line['EName']="%s"%l.employee().EName
		t=l.employee().Dept()
		if t:
			line['DeptName']="%s"%t.DeptName
		else:
			line['DeptName']=""
		line['TTime']=l.TTime.strftime("%m-%d %H:%M:%S")
		times=l.TTime.strftime("%Y%m%d%H%M%S")
		times1=l.TTime.strftime("%Y%m")
		if l.Device():
			devs=l.SN_id
			line['Device']=smart_str(l.Device().Alias)
		#	cmapfile="%s/upload/%s/%s-%s.jpg" %(settings.ADDITION_FILE_ROOT,l.Device().SN,l.StrTime(),devPIN)
		#	if os.path.exists(cmapfile):
		#		line['urls']="/iclock/file/upload/%s/%s-%s.jpg" %(l.Device().SN,l.TTime.strftime("%Y%m%d%H%M%S"),devPIN)
		#	else :
		#		line['urls']="/media/img/transaction/noimg.jpg"
		else:
			line['Device']=""
		#	line['urls']="/media/img/transaction/noimg.jpg"
		#cmapfile1="%sphoto/%s.jpg"%(settings.ADDITION_FILE_ROOT,l.employee().PIN)
		#if os.path.isfile(cmapfile1):
		#	line['urls1']="/iclock/file/photo/%s.jpg"%l.employee().PIN
		#else :
		#	line['urls1']="/media/img/transaction/noimg.jpg"
		lines.append(line.copy())
	if uid>0:
		emp=employee.objByID(uid)
		empdata={'PIN':emp.PIN,'EName':emp.EName,'DeptName':emp.Dept().DeptName,'Sex':emp.Gender,'Card':emp.Card or '','Title':emp.Title or ''}
		cmapfile="%s/upload/%s/%s/%s-%s.jpg" %(settings.ADDITION_FILE_ROOT,devs,times1,times,emp.PIN)
		devPIN=devicePIN(emp.PIN)
		if os.path.exists(cmapfile):
			empdata['urls']="/iclock/file/upload/%s/%s/%s-%s.jpg" %(devs,times1,times,devPIN)
		else :
			empdata['urls']="/media/img/transaction/noimg.jpg"
		photourl=l.employee().getThumbnailUrl(None,False)
		if photourl!='':
			empdata['urls1']="%s"%photourl
		else:
			empdata['urls1']="/media/img/noimg.jpg"
		#cmapfile1="%sphoto/%s.jpg"%(settings.ADDITION_FILE_ROOT,emp.PIN)
		#if os.path.isfile(cmapfile1):
		#	empdata['urls1']="/iclock/file/photo/%s.jpg"%emp.PIN
		#else :
		#	empdata['urls1']="/media/img/transaction/noimg.jpg"

	result['msg']='OK'
	result['data']=lines
	result['empdata']=empdata	
	result['ret']=len(lines)
	result['lasttId']=lasttid
	result['tm']=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	
	#print result
	return getJSResponse(result)

def shortDTime(value):
	if value:
		return value.strftime('%m-%d %H:%M')
	else:
		return ''

@login_required
def MeetState(request): #��
	meet_id=int(request.GET.get("meet","-1"))
	nt=datetime.datetime.now()
	d1=trunc(nt)
	d2=d1+datetime.timedelta(days=1)
	objs=Meet.objects.filter(Starttime__gte=d1,Endtime__lt=d2).exclude(DelTag=1).order_by('id')
	if meet_id>0:
		objs=objs.filter(id=meet_id)
	line={}
	lines=[]
	result={}
	lastmid=-1
	for t in objs:
		line={}
		lastmid=t.id
		line['id']=t.id
		line['MeetID']=t.MeetID
		line['conferenceTitle']=t.conferenceTitle
		line['MeetContents']=t.MeetContents
		if t.LocationID:
			line['LocationID']=t.LocationID.roomName
		else:
			line['LocationID']=''
		line['Starttime']=shortDTime(t.Starttime)
		line['Endtime']=shortDTime(t.Endtime)
		line['Should']=Meet_details.objects.filter(MeetID=t.id).count()
		
		qs=Meet_details.objects.filter(MeetID=t.id).values('UserID')
		c=0
		if t.Starttime and t.Endtime:
			trans=transactions.objects.filter(UserID__in=qs,TTime__gte=t.Starttime-datetime.timedelta(seconds=3600),TTime__lt=t.Endtime)
			room=t.LocationID
			if room:
				iclockSN=meet_devices.objects.filter(LocationID=room).values('SN')
				if iclockSN:
					trans=trans.filter(Q(SN__isnull=True)|Q(SN__in=iclockSN))
			else:
				SN=iclock.objects.filter(ProductType=1).values("SN")
				if SN:
					trans=trans.filter(Q(SN__isnull=True)|Q(SN__in=SN))
				else:
					trans=trans.filter(SN__isnull=True)
			c=trans.values("UserID").distinct().count()#暂假设开会一小时前打卡有效
		line['Real']=c
		line['absent']=line['Should']-c
		lines.append(line.copy())
		
	result['msg']='OK'
	result['data']=lines
	result['lastmid']=lastmid
	#result['lastDId']=lastdid
	result['ret']=len(lines)
#	print result
	return getJSResponse(result)
		
	
@login_required
def MeetDell(request):
	if request.method=='GET':
		r=[
			{'name':'MeetID','width':100,'index':'MeetID__MeetID','label':unicode(_(u'会议编号'))},
			{'name':'PIN','sortable':False,'width':140,'label':unicode(_('PIN'))},
			{'name':'EName','sortable':False,'width':120,'label':unicode(_('EName'))},
			{'name':'DeptName','sortable':False,'width':200,'label':unicode(_('department name'))}
		]
		disabledCols=[]
		rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
		return getJSResponse(rs)
	else:
		meet_id=request.GET.get("MeetID",0)
		tag=int(request.GET.get("tag",0))
		iCount=0
		try:
			offset = int(request.POST.get('page', 1))
		except:
			offset=1
		limit= int(request.POST.get('rows', 0))
		if limit==0:
			limit= int(request.GET.get('rows', 30))
		details=getMeetNum(meet_id,[],0,request.POST.get('sord'))	
		re=[]
		me=Meet.objByID(meet_id)
		for p in details:
			if tag==0 and (p['lid']>0 or p['absent']==1):
				continue
			if tag==1 and p['lid']==0:
				continue
			if tag==2 and p['absent']==0:
				continue
			d={}
			emp=employee.objByID(p['userid'])
			d['MeetID']=me.MeetID
			d['DeptName']=emp.Dept().DeptName
			d['PIN']=emp.PIN
			d['EName']=emp.EName and (emp.DelTag==1 and emp.EName+u'(已删除)' or emp.EName) or ''
			re.append(d.copy())
		p=Paginator(re, limit)
		iCount=p.count
		if iCount<(offset-1)*limit:
			offset=1
		page_count=p.num_pages
		pp=p.page(offset)
		re=pp.object_list
		Result={}
		if offset>page_count:offset=page_count
		item_count =iCount
		Result['item_count']=item_count
		Result['page']=offset
		Result['limit']=limit
		Result['from']=(offset-1)*limit+1
		Result['page_count']=page_count
		Result['datas']=re
		rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
		return getJSResponse(rs)
		


@login_required	
def uploadFile(request, path): 
	if request.method=='GET':
		return render_to_response("uploadfile.html",{"title": "Only for upload file test"})
	if "EMP_PIN" not in request.GET:
		return getJSResponse("result=-1; message='Not specified a target';")
	f=devicePIN(request.GET.get("EMP_PIN"))+".jpg"
	size=saveUploadImage(request, "fileUpload", fname=getStoredFileName("photo", None, f))
	return getJSResponse("result=%s; message='%s';"%(size,getStoredFileURL("photo",None,f)))
	

MAX_PHOTO_WIDTH=400

def saveUploadImage(request, requestName, fname):
	import StringIO
	import os
	try:
		os.makedirs(os.path.split(fname)[0])
	except: pass
	output = StringIO.StringIO()
	f=request.FILES[requestName]
	size=f.size
	for chunk in f.chunks():
		output.write(chunk)
	import PIL.Image as Image
	try:
		output.seek(0)
		im = Image.open(output)
	except IOError, e:
#		print "error to open", imgUrlOrg, e.message
		return getJSResponse("result=-1; message='Not a valid image file';")
	#print f.name
	size=f.size
	if im.size[0]>MAX_PHOTO_WIDTH:
		width=MAX_PHOTO_WIDTH
		height=int(im.size[1]*MAX_PHOTO_WIDTH/im.size[0])
		try:
			im=im.resize((width, height), Image.ANTIALIAS)
		except Exception,e:
			print "6666666666==",e
	try:
		im.save(fname);
	except IOError:
		print "saveUploadImage=="
		im.convert('RGB').save(fname)
	return size
	
	
#这个方法跟上面的唯一区别就是 不压缩上传图片的大小，图片多大上传上去就是多大	
def saveUploadImage2(request, requestName, fname):
	import StringIO
	import os
	try:
		os.makedirs(os.path.split(fname)[0])
	except: pass
	output = StringIO.StringIO()
	f=request.FILES[requestName]
	size=f.size
	for chunk in f.chunks():
		output.write(chunk)
	try:
		import PIL.Image as Image
	except:
		return None
	try:
		output.seek(0)
		im = Image.open(output)
	except IOError, e:
#		print "error to open", imgUrlOrg, e.message
		return getJSResponse("result=-1; message='Not a valid image file';")
	#print f.name
	size=f.size

	try:
		im.save(fname);
	except IOError:
		im.convert('RGB').save(fname)
	return size
MAX_PHOTO_WIDTH3=40

def saveUploadImage3(request, requestName, fname):
	import StringIO
	import os
	try:
		os.makedirs(os.path.split(fname)[0])
	except: pass
	output = StringIO.StringIO()
	f=request.FILES[requestName]
	size=f.size
	for chunk in f.chunks():
		output.write(chunk)
	try:
		import PIL.Image as Image
	except:
		return None
	try:
		output.seek(0)
		im = Image.open(output)
	except IOError, e:
#		print "error to open", imgUrlOrg, e.message
		return getJSResponse("result=-1; message='Not a valid image file';")
	#print f.name
	size=f.size
	if im.size[0]>MAX_PHOTO_WIDTH3:
		width=MAX_PHOTO_WIDTH3
		height=30#int(im.size[1]*MAX_PHOTO_WIDTH3/im.size[0])
		im=im.resize((width, height), Image.ANTIALIAS)
	try:
		im.save(fname);
	except IOError:
		im.convert('RGB').save(fname)
	return size



def photolocation(request):
	request.user.iclock_url_rel='../..'
	request.model = transactions
	id=request.GET.get('id')
	return render(request,'meeting/photolocation_list.html',{'meetid':id})
	# render_to_response('meeting/photolocation_list.html',
	# 						RequestContext(request, {
	# 						'from': 1,
	# 						'page': 1,
	# 						'limit': 10,
	# 						'item_count': 4,
	# 						'page_count': 1,
	# 						'meetid':id,
	# 						'iclock_url_rel': request.user.iclock_url_rel,
	# 						}))
def getphotolocation(request):
	id=request.GET.get('id')
	ji=request.GET.get("local",0)
	lx=getMeetNum(id,[],2)
	me=Meet.objByMeetID(id)
	rs=[]
	if len(lx)>0:
		for m in lx:
			emp=employee.objByID(m['userid'])
			cmapfile1="%sphoto/%s.jpg"%(settings.ADDITION_FILE_ROOT,emp.PIN)
			if os.path.isfile(cmapfile1):
				photo="/iclock/file/photo/%s.jpg"%emp.PIN
			else :
				photo="/media/img/transaction/noimg.jpg"
			html=u"<div style='width:125;height:165;margin:auto;border:0px solid #000;text-align:center'>"
			html+=u"<img id='index_%s' style='width:120;height:160'  src='%s'></img>"%(emp.id,photo)
			#html+=u"<div style='color:red;font-size:20px'>%s</div>"%emp.EName
			html+=u"</div>"
			rs.append(html)
		ret=1
	else:
		for m in range(32):
			photo="/media/img/transaction/noimg.jpg"
			html=u"<div style='width:125;height:165;margin:auto;border:0px solid #000;text-align:center'>"
			html+=u"<img id='index_%s' style='width:120;height:160'  src='%s'></img>"%(m,photo)
			html+=u"</div>"
			rs.append(html)
		ret=0
	title=u"%s未出勤人员照片显示"%me.conferenceTitle
	ll=u"<div style='background-color:#CCD9E8;width:100%;height:130%;padding:5px'><form id='form1' action='' method='POST' ><table align='center' valign='middle'  border=0>"
	#ll+=u"<tr><td colspan=8><div style='width:125;height:20;margin:auto'></td></tr>"
	ll+=u"<tr><td colspan=8><div id='id_title_week' style='height:55;margin:auto;border:0px solid #000;text-align:center;font-size:40px'>%s</div></td></tr>"%title
	if rs:
		ll+=drowE(rs,ji)
	ll+=u"</table></from></div>"
	return  getJSResponse({"ret":ret,"message":ll})

def drowE(ll,ji):
	html=u""
	i=0
	a=len(ll)%32
	b=len(ll)/32
	if a>0:
		b=b+1
	ji=int(ji)%b
	for d in ll:
		if i>=ji*32:
			if i%8==0:
				html+=u"<tr>"
			html+=u"<td>%s</td>"%d
			if i%8==7:
				html+=u"</tr>"
		i=i+1
		if i>=(ji+1)*32:
			break
	return html

def getMeetNum(id,userid=[],tag=0,sord='desc'):
	"""
	tag =0 显示全体人员
	tag =1 显示签到人员
	tag =2 显示未签到人员
	"""
	me=Meet.objByMeetID(id)
	if userid:
		userPresenceList=[int(i) for i in userid]
		userListPresence=Meet_details.objects.filter(MeetID=me,UserID__in=userPresenceList)
	else:
		userListPresence=Meet_details.objects.filter(MeetID=me)
	if sord=='desc':
		userPresenceList=[int(i) for i in userListPresence.values_list('UserID', flat=True).order_by('-UserID__PIN')]
	else:
		userPresenceList=[int(i) for i in userListPresence.values_list('UserID', flat=True).order_by('UserID__PIN')]
	if me.Enrolmenttime==None:
		inStartTime=me.Starttime-datetime.timedelta(0, 1*60*60)
	else:
		inStartTime=me.Enrolmenttime
	if me.LastEnrolmenttime==None:#最迟签到时间为空
		if me.EarlySignOfftime==None:#最早签退时间为空
			inEndTime=me.Endtime#如果最迟签到时间为空，最早签退时间为空则默认为此会议不记迟到，签到结束时间为会议结束时间
		else:
			inEndTime=me.Starttime+(me.EarlySignOfftime-me.Starttime)/2#如果最迟签到时间为空，有最早签退时间，则结束签到时间取开始时间+（最迟签到时间-开始时间）/2
	else:
		if me.EarlySignOfftime==None:#最早签退时间为空
			inEndTime=me.LastEnrolmenttime+(me.Endtime-me.LastEnrolmenttime)/2#如果最早签退时间为空，则结束签到时间取最迟签到时间+（结束时间-迟签到时间）/2
		else:
			inEndTime=me.LastEnrolmenttime+(me.EarlySignOfftime-me.LastEnrolmenttime)/2#结束签到时间取最迟签到时间+（最早签退时间- 最迟签到时间）/2
	outStartTime=inEndTime+datetime.timedelta(0, 1)#开始签退时间为结束签到时间+1秒
	if me.LastSignOfftime==None:
		outEndTime=me.Endtime+datetime.timedelta(0, 1*60*60)
	else:
		outEndTime=me.LastSignOfftime
	ilst=''
	ilet=''
	olst=''
	olet=''
	if me.lunchtimestr:
		ilst=me.lunchtimestr-datetime.timedelta(0, 30*60)
		ilet=me.lunchtimestr+datetime.timedelta(0, 30*60)
	if me.lunchtimeend:
		olst=me.lunchtimeend-datetime.timedelta(0, 30*60)
		olet=me.lunchtimeend+datetime.timedelta(0, 30*60)
	
	starttime=me.Starttime
	endtime=me.Endtime
	trans = transactions.objects.filter(UserID__id__in=userPresenceList,TTime__gte=inStartTime,TTime__lte=outEndTime).order_by("id")
	room=me.LocationID
	if room:
		iclockSN=meet_devices.objects.filter(LocationID=room).values('SN')
		if iclockSN:
			trans=trans.filter(Q(SN__isnull=True)|Q(SN__in=iclockSN))
	else:
		SN=iclock.objects.filter(ProductType=1).values("SN")
		if SN:
			trans=trans.filter(Q(SN__isnull=True)|Q(SN__in=SN))
		else:
			trans=trans.filter(SN__isnull=True)
	ll={}
	for t in trans:
		if t.TTime>=inStartTime and t.TTime<=inEndTime:
			key='%s-s'%t.employee().id
			try:
				if t.TTime<ll[key]:
					ll[key]=t.TTime
			except:
				ll[key]=t.TTime
		elif t.TTime>=outStartTime and t.TTime<=outEndTime:
			key='%s-e'%t.UserID_id
			try:
				if t.TTime>ll[key]:
					ll[key]=t.TTime
			except:
				ll[key]=t.TTime
		elif t.TTime>=ilst and t.TTime<=ilet:
			key='%s-2s'%t.UserID_id
			try:
				if t.TTime>ll[key]:
					ll[key]=t.TTime
			except:
				ll[key]=t.TTime
		elif t.TTime>=olst and t.TTime<=olet:
			key='%s-2e'%t.UserID_id
			try:
				if t.TTime>ll[key]:
					ll[key]=t.TTime
			except:
				ll[key]=t.TTime
	leave=USER_SPEDAY.objects.filter(UserID__in=userPresenceList,State=2).filter(Q(StartSpecDay__gte=inStartTime,StartSpecDay__lte=outEndTime+datetime.timedelta(1))|Q(StartSpecDay__lt=inStartTime,EndSpecDay__gt=inStartTime))
	for l in leave:
		key='%s-lid'%l.employee().id
		try:
			ll[key]=l.DateID
		except:
			pass
	re=[]
	for u in userPresenceList:
		lx={}
		lx['userid']=u
		lx['st']=''
		lx['et']=''
		lx['absent']=0
		lx['lid']=0
		lx['late']=0
		lx['early']=0
		lx['meetname']=me.conferenceTitle
		lx['lst']=me.Starttime
		lx['let']=me.Endtime
		lx['l2st']=me.lunchtimestr
		lx['l2et']=me.lunchtimeend
		try:
			lx['st']=ll['%s-s'%u]
			if lx['st']>starttime:
				lx['late']=1
		except:
			lx['absent']=1
		try:
			lx['et']=ll['%s-e'%u]
			if lx['et']<endtime:
				lx['early']=1
		except:
			pass
		try:
			lx['st2']=ll['%s-2s'%u]
			if lx['st2']>lx['l2st']:
				lx['late']=1
		except:
			pass
		try:
			lx['et2']=ll['%s-2e'%u]
			if lx['et2']<lx['l2et']:
				lx['early']=1
		except:
			pass
		speday=False
		try:
			speday=ll['%s-lid'%u]
		except:
			pass
		if speday:
			lx['lid']=speday
			lx['absent']=0
		if tag==1 and lx['absent']==0:
			re.append(lx)
		elif tag==2 and lx['absent']==1:
			re.append(lx)
		elif tag==0:
			re.append(lx)
	return re


def getMeetNumByDay(st,et,userid=[]):
	xx={}
	meet=Meet.objects.filter(Starttime__gte=st,Endtime__lte=et)
	for me in meet:
	#me=Meet.objByMeetID(id)
		if userid:
			userPresenceList=userid
			userListPresence=Meet_details.objects.filter(MeetID=me,UserID__in=userPresenceList)
		else:
			userListPresence=Meet_details.objects.filter(MeetID=me)
		userPresenceList=[int(i) for i in userListPresence.values_list('UserID', flat=True)]
		if me.Enrolmenttime==None:
			inStartTime=me.Starttime-datetime.timedelta(0, 1*60*60)
		else:
			inStartTime=me.Enrolmenttime
		if me.LastEnrolmenttime==None:#最迟签到时间为空
			if me.EarlySignOfftime==None:#最早签退时间为空
				inEndTime=me.Endtime#如果最迟签到时间为空，最早签退时间为空则默认为此会议不记迟到，签到结束时间为会议结束时间
			else:
				inEndTime=me.Starttime+(me.EarlySignOfftime-me.Starttime)/2#如果最迟签到时间为空，有最早签退时间，则结束签到时间取开始时间+（最迟签到时间-开始时间）/2
		else:
			if me.EarlySignOfftime==None:#最早签退时间为空
				inEndTime=me.LastEnrolmenttime+(me.Endtime-me.LastEnrolmenttime)/2#如果最早签退时间为空，则结束签到时间取最迟签到时间+（结束时间-迟签到时间）/2
			else:
				inEndTime=me.LastEnrolmenttime+(me.EarlySignOfftime-me.LastEnrolmenttime)/2#结束签到时间取最迟签到时间+（最早签退时间- 最迟签到时间）/2
		outStartTime=inEndTime+datetime.timedelta(0, 1)#开始签退时间为结束签到时间+1秒
		if me.LastSignOfftime==None:
			outEndTime=me.Endtime+datetime.timedelta(0, 1*60*60)
		else:
			outEndTime=me.LastSignOfftime
		starttime=me.Starttime
		endtime=me.Endtime
		trans = transactions.objects.filter(UserID__id__in=userPresenceList,TTime__gte=inStartTime,TTime__lte=outEndTime).order_by("id")
		room=me.LocationID
		if room:
			iclockSN=meet_devices.objects.filter(LocationID=room).values('SN')
			if iclockSN:
				trans=trans.filter(Q(SN__isnull=True)|Q(SN__in=iclockSN))
		else:
			SN=iclock.objects.filter(ProductType=1).values("SN")
			if SN:
				trans=trans.filter(Q(SN__isnull=True)|Q(SN__in=SN))
			else:
				trans=trans.filter(SN__isnull=True)
		ll={}
		for t in trans:
			if t.TTime>=inStartTime and t.TTime<=inEndTime:
				key='%s-s'%t.UserID__id
				try:
					if t.TTime<ll[key]:
						ll[key]=t.TTime
				except:
					ll[key]=t.TTime
			if t.TTime>=outStartTime and t.TTime<=outEndTime:
				key='%s-e'%t.UserID__id
				try:
					if t.TTime>ll[key]:
						ll[key]=t.TTime
				except:
					ll[key]=t.TTime
		leave=USER_SPEDAY.objects.filter(StartSpecDay__gte=inStartTime,EndSpecDay__lte=outEndTime,UserID__in=userPresenceList,State=2)
		for l in leave:
			key='%s-lid'%t.UserID__id
			try:
				ll[key]=l.DateID
			except:
				pass
		for u in userPresenceList:
			lx={}
			lx['userid']=u
			lx['st']=''
			lx['et']=''
			lx['absent']=0
			lx['lid']=0
			try:
				lx['st']=ll['%s-s'%u]
				if lx['st']>starttime:
					lx['late']=1
			except:
				lx['absent']=1
			try:
				lx['et']=ll['%s-e'%u]
				if lx['et']<endtime:
					lx['early']=1
			except:
				pass
			speday=False
			try:
				speday=ll['%s-lid'%u]
			except:
				pass
			if speday:
				lx['lid']=speday
				lx['absent']=0
				try:
					xx['%s-s'%u]+=1
				except:
					xx['%s-s'%u]=1
			try:
				xx['%s-z'%u]+=1
			except:
				xx['%s-z'%u]=1
			if lx['late']==1:
				try:
					xx['%s-l'%u]+=1
				except:
					xx['%s-l'%u]=1
			if lx['early']==1:
				try:
					xx['%s-e'%u]+=1
				except:
					xx['%s-e'%u]=1
			if lx['absent']==1:
				try:
					xx['%s-a'%u]+=1
				except:
					xx['%s-a'%u]=1
	#print xx				
	return xx
	