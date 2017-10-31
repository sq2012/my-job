#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import department
import datetime
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from mysite.utils import *
from mysite.meeting.models import *

@login_required
def getData(request):
	funid = request.GET.get("func", "")
		
	if funid == 'rooms':
		d={}
		dd={}
		d["id"]=0
		d["name"]=u'所有会议室'
		d["pid"]=-1
		d["value"]=0
		d["open"]=True
		d["isParent"]=False
		d['icon']="/media/img/icons/home.png"
		d["children"]=[]
		rooms=MeetLocation.objects.all().exclude(DelTag=1).order_by('roomNo')
		for t in rooms:
			d["isParent"]=True

			dd["id"]=int(t.id)
			dd["name"]=t.roomName
			dd["pid"]=0
			dd["value"]=t.roomNo
			dd["open"]=False
			dd["isParent"]=False
			d["children"].append(dd.copy())
		return getJSResponse(d)
	elif funid == 'meets':
		d={}
		dd={}
		d["id"]=0
		d["name"]=u'所有会议'
		d["pid"]=-1
		d["value"]=0
		d["open"]=True
		d["isParent"]=False
		d['icon']="/media/img/icons/home.png"
		d["children"]=[]
		meets=Meet.objects.all().exclude(DelTag=1).order_by('-id')
		for t in meets:
			d["isParent"]=True

			dd["id"]=int(t.id)
			dd["name"]=t.conferenceTitle
			dd["pid"]=0
			dd["value"]=t.MeetID
			dd["open"]=False
			dd["isParent"]=False
			d["children"].append(dd.copy())
		return getJSResponse(d)
	elif funid=='latestmeeting':
		st=request.GET.get('start','')
		et=request.GET.get('end','')
		d1=datetime.datetime.strptime(st,'%Y-%m-%d')
		d2=datetime.datetime.strptime(et,'%Y-%m-%d')
		roomNo=request.GET.get('roomNo','')
		meet=Meet.objects.filter(LocationID=roomNo,Starttime__gte=d1,Starttime__lte=d2).exclude(DelTag=1)
		events=[]
		colorlist=['#661166','green','#E22C37','#3B3944','#FF4400','#7A13F3','#006AE0','#D96808','#004CF8','#165C15']
		daylist={}
		for m in meet:
			d=m.Starttime.strftime("%d")
			d=int(d)
			i=d%5
			try:					
				daylist[d]=daylist[d]-1
				i=daylist[d]
			except:
				daylist[d]=10
			color=colorlist[i]
			Dict={'title': m.conferenceTitle,'color':color,'start': m.Starttime.strftime("%Y-%m-%d %H:%M"),'end':m.Endtime.strftime("%Y-%m-%d %H:%M")}
			events.append(Dict)
		return getJSResponse(events)
	elif funid=='latestmeeting_home':
		st=request.GET.get('start','')
		et=request.GET.get('end','')
		d1=datetime.datetime.strptime(st,'%Y-%m-%d')
		d2=datetime.datetime.strptime(et,'%Y-%m-%d')
		meet=Meet.objects.filter(Starttime__gte=d1,Starttime__lte=d2).exclude(DelTag=1)
		isReal=0
		if employee.objects.all()[:1] or iclock.objects.exclude(DelTag=1).count():
			isReal=1
		if isReal==0:#演示数据
			import random
			events=[
					{'id':0,
						'title': u'虚拟会议数据',
						'start': st
					}
			]

			d=d1+datetime.timedelta(hours=9)
			meet_contents=[unicode(_(u'学术研讨会议')),unicode(_(u'工作总结会议')),unicode(_(u'政治学习')),unicode(_(u'技术交流会议')),unicode(_(u'业务学习'))]
			while d<=d2:
				for t in range(random.randint(1,2)):
					j=random.randint(0,4)
					dDict={'id':0,'title': meet_contents[j],'color':'#333333','start': (d+datetime.timedelta(hours=t*2)).strftime("%Y-%m-%dT%H:%M:%S"),'end':(d+datetime.timedelta(hours=(t*2+1))).strftime("%Y-%m-%dT%H:%M:%S")}
					events.append(dDict)
					
					
				d=d+datetime.timedelta(days=1)
		else:
			events=[]
			colorlist=['#661166','green','#E22C37','#3B3944','#FF4400','#7A13F3','#006AE0','#D96808','#004CF8','#165C15']
			daylist={}
			for m in meet:
				d=m.Starttime.strftime("%d")
				d=int(d)
				i=d%5
				try:					
					daylist[d]=daylist[d]-1
					i=daylist[d]
				except:
					daylist[d]=10
				color=colorlist[i]
				dDict={'id':m.id,'title': m.conferenceTitle,'color':color,'start': m.Starttime.strftime("%Y-%m-%d %H:%M:%S"),'end':m.Endtime.strftime("%Y-%m-%d %H:%M:%S")}
				events.append(dDict)
		return getJSResponse(events)
	elif funid=='lastweekmeeting':
		d1=datetime.date.today()
		d2=d1+datetime.timedelta(days=8)
		meet=Meet.objects.filter(Starttime__gte=d1,Starttime__lt=d2).exclude(DelTag=1).order_by("Starttime")
		re=[]
		for m in meet:
			ll={}
			ll['id']=m.MeetID
			ll['name']=m.conferenceTitle
			ll['st']=m.Starttime.strftime("%m-%d %H:%M")
			ll['et']=m.Endtime.strftime("%m-%d %H:%M")
			re.append(ll)
		return getJSResponse(re)
	elif funid=='participants_tpl':
		d={}
		dd={}

		d["id"]=0
		d["name"]=u'所有参会人员模板'
		d["pid"]=-1
		d["value"]=0
		d["open"]=True
		d["isParent"]=False
		d['icon']="/media/img/icons/home.png"
		d["children"]=[]
		meets=participants_tpl.objects.all().exclude(DelTag=1).order_by('-id')
		for t in meets:
			d["isParent"]=True

			dd["id"]=int(t.id)
			dd["name"]=t.Name
			dd["pid"]=0
			dd["value"]=t.id
			dd["open"]=False
			dd["isParent"]=False
			d["children"].append(dd.copy())
		return getJSResponse(d)
	elif funid=='MeetMessages':
		d={}
		dd={}

		d["id"]=0
		d["name"]=u'所有会议通知'
		d["pid"]=-1
		d["value"]=0
		d["open"]=True
		d["isParent"]=False
		d['icon']="/media/img/icons/home.png"
		d["children"]=[]
		MeetMessages=MeetMessage.objects.all().exclude(DelTag=1).order_by('-id')
		for t in MeetMessages:
			d["isParent"]=True

			dd["id"]=int(t.id)
			dd["name"]=t.MessageID+' '+t.MessageNotice
			dd["pid"]=0
			dd["value"]=t.MessageID
			dd["open"]=False
			dd["isParent"]=False
			d["children"].append(dd.copy())
		return getJSResponse(d)
	elif funid=='hasMeets':
		ll=[]
		Meets=Meet.objects.all().exclude(DelTag=1).order_by('-id')
		for i in Meets:
			p={}
			p['id']=i.id
			p['conferenceTitle']=i.conferenceTitle
			ll.append(p)
		return getJSResponse(dumps(ll))
	elif funid=='getEmails':
		ll=[]
		Mid=request.GET.get("Meetid","0")
		userids=Meet_details.objects.filter(MeetID=Mid).values("UserID")
		user=employee.objects.filter(id__in=userids,email__isnull=False)
		emails=''
		for u in user:
			if u.email:
				emails+=u.email+';'
		ll.append(emails)
		return getJSResponse(dumps(ll))
	elif funid=='Minutes':
		d={}
		dd={}

		d["id"]=0
		d["name"]=u'所有会议纪要'
		d["pid"]=-1
		d["value"]=0
		d["open"]=True
		d["isParent"]=False
		d['icon']="/media/img/icons/home.png"
		d["children"]=[]
		Minutes=Minute.objects.all().order_by('-FileNumber')
		for t in Minutes:
			d["isParent"]=True
			dd["id"]=int(t.FileNumber)
			dd["name"]=str(t.FileNumber)+' '+t.FileName
			dd["pid"]=0
			dd["value"]=t.FileNumber
			dd["open"]=False
			dd["isParent"]=False
			d["children"].append(dd.copy())
		return getJSResponse(d)
	elif funid=='showmeeting':
		from mysite.meeting.datamisc import getMeetNum
		ll=[]
		Mid=request.GET.get("Meetid","0")
		objs=Meet.objects.filter(id=Mid)
		html={}
		for t in objs:
			html['t']=t.conferenceTitle
			html['c']=t.MeetContents
			html['st']=t.Starttime.strftime("%Y-%m-%d %H:%M:%S")
			html['et']=t.Endtime.strftime("%Y-%m-%d %H:%M:%S")
			
			Should=Meet_details.objects.filter(MeetID=t.id).count()
			qs=Meet_details.objects.filter(MeetID=Mid).values('UserID')
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
			a=Should-c
			html['sh']=Should
			html['ab']=a
			html['cc']=c
		return getJSResponse(html)