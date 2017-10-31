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
from mysite.iclock.models import *
from mysite.acc.models import *
#from mysite.iclock.datasproc import *
from django.core.paginator import Paginator
#from mysite.iclock.datas import *
#from mysite.core.menu import *
from mysite.core.tools import *
from mysite.core.cmdproc import *
from mysite.iclock.models import *
#from django.shortcuts import render
import PIL.Image as Image
from mysite.acc.datamisc import getDoorState
from mysite.acc.getBaseData import userZoneList

@login_required	
def getRTlog(request): 
	cc={}
	if request.user.is_superuser:
		accmap=AccMap.objects.all()
	else:
		zonelist=userZoneList(request.user)
		objs=zone.objects.filter(id__in=zonelist).order_by('parent','code').exclude(DelTag=1).values("id")
		map=AccMap_zone.objects.filter(code__in=objs).values('imap')
		accmap=AccMap.objects.filter(id__in=map)
	maphtml=[]
	doorhtml=[]
	usedoorhtml=[]
	zones=[]
	imap=0
	mul=5
	for a in accmap:
		ll={}
		ll['id']=a.id
		ll['mapname']=a.map_name
		ll['mapurl']=a.map_path
		ll['mapwidth']=mathmulriple(a.width,a.mulriple,1)
		ll['mapheight']=mathmulriple(a.height,a.mulriple,1)
		ll['mulriple']=a.mulriple
		if imap==0:
			imap=a.id
			mul=a.mulriple
			zones=AccMap_zone.objects.filter(imap=imap).values('code')
		maphtml.append(ll)
	if imap!=0:
		usedoor=[]
		door=AccDoorMap.objects.filter(imap=imap)
		for d in door:
			ll={}
			ll['doorid']=d.door.id
			ll['doorname']=d.door.door_name
			ll['doorno']=d.door.door_no
			ll['sn']=d.door.device.Alias or d.door.device.SN
			ll['doorleft']=mathmulriple(d.left,mul,1)
			ll['doortop']=mathmulriple(d.top,mul,1)
			doorstate=getDoorState(d.door.device.SN,d.door.door_no,0)
			ll['doorimg']=doorstate[0]
			usedoorhtml.append(ll)
			usedoor.append(d.door.id)
			
		sn=IclockZone.objects.filter(zone__in=zones).values("SN")
		doorall=AccDoor.objects.filter(device__in=sn,device__DelTag=0)
		for d in doorall:
			if d.id not in usedoor:
				ll={}
				ll['doorid']=d.id
				ll['doorname']=d.door_name
				ll['doorno']=d.door_no
				ll['sn']=d.device.Alias or d.device.SN
				doorstate=getDoorState(d.device.SN,d.door_no,0)
				ll['doorimg']=doorstate[0]
				doorhtml.append(ll)
	cc['map']=dumps(maphtml)
	cc['door']=dumps(doorhtml)
	cc['usedoor']=dumps(usedoorhtml)
	return render(request,"acc/RTlog.html",cc)


def mathmulriple(val,mul,tag):
	"""
	5(level)为照片上传的倍数，点击缩小按钮一次减小1.放大按钮点一次增加1.
	缩小比例(l)为0.8,点击缩小一次变为现有大小的0.8倍。点击放大按钮变为现有大小的1.25倍
	tag表示当前操作类型，1为从数据库中取值显示。其他为从页面保存到数据库中。数据库中存放的left、top、width、height为level为5时的值
	保存时将数据换算成5保存。取数据时换算成数据库accmap中倍数保存。
	"""
	val=float(val)
	mul=int(mul)
	level=5
	flat=True
	s=0
	l=0.8
	b=1.25
	if level>mul:
		flat=False
		s=level-mul
	else:
		s=mul-level
	if tag==1:
		if flat:
			valmul=b**s*val
		else:
			valmul=l**s*val
	else:
		if flat:
			valmul=val/b**s
		else:
			valmul=val/l**s
	return valmul

@login_required		
def applyaccmap(request):
	zones=request.GET.get('zones','')
	mapname=request.POST.get('map_name',"")
	if (not zones) and (not mapname):
		return getJSResponse({"ret":1,"message":u'%s'%_("Save Failed")})
	try:
		import StringIO
		f=request.FILES["fileToUpload"]
		size=f.size
		try:
			os.makedirs("%saccmap/"%settings.ADDITION_FILE_ROOT)
		except Exception,e:
			pass
		fname="%s%s/%s"%(settings.ADDITION_FILE_ROOT,'accmap','%s.jpg'%mapname)
		output = StringIO.StringIO()
		for chunk in f.chunks():
			output.write(chunk)
		output.seek(0)
		im = Image.open(output)
		width= im.size[0]
		height= im.size[1]
		try:
			im.save(fname);
		except IOError:
			im.convert('RGB').save(fname)
		map_path='/iclock/file/accmap/%s.jpg'%mapname
		ac=AccMap(map_name=mapname,map_path=map_path,width=width,height=height,mulriple=5)
		ac.save()
	except:
		return getJSResponse({"ret":1,"message":u'%s'%_(u"保存失败")})
	zones=zones.split(",")
	zones=zone.objects.filter(id__in=zones)
	for z in zones:
		AccMap_zone(imap=ac,code=z).save()
	return getJSResponse({"ret":0,"message":u'%s'%_("Save Success")})

@login_required
def del_map(request):
	mapid=request.POST.get('mapid','')
	accm=AccMap.objects.filter(id=mapid)
	accm.delete()
	return getJSResponse({"ret":0,"message":u'%s'%_("Save Success")})

@login_required
def savemap(request):
	mapid=request.GET.get('mapid',0)
	mulriple=request.GET.get('mulriple',5)
	door=request.POST.get('door','')
	accmap=AccMap.objects.get(id=mapid)
	accmap.mulriple=mulriple
	accmap.save()
	doors=door.split(",")
	doormap=AccDoorMap.objects.filter(imap=mapid)
	doormap.delete()
	for ds in doors:
		if len(ds)>6:
			dd=ds.split("_")
			acc=AccDoor.objects.get(id=dd[1])
			top=mathmulriple(dd[2],mulriple,0)
			left=mathmulriple(dd[3],mulriple,0)
			AccDoorMap(imap=accmap,door=acc,left=left,top=top).save()
	return getJSResponse({"ret":0,"message":u'%s'%_("Save Success")})


def showimganddoor(request):
	imap=request.GET.get('mapid')
	cc={}
	doorhtml=[]
	usedoorhtml=[]
	zones=[]
	mul=5
	if imap!=0:
		accmap=AccMap.objects.get(id=imap)
		mul=accmap.mulriple
		zones=AccMap_zone.objects.filter(imap=imap).values('code')
		usedoor=[]
		door=AccDoorMap.objects.filter(imap=imap)
		for d in door:
			ll={}
			ll['doorid']=d.door.id
			ll['doorno']=d.door.door_no
			ll['doorname']=d.door.door_name
			ll['sn']=d.door.device.Alias or d.door.device.SN
			ll['doorleft']=mathmulriple(d.left,mul,1)
			ll['doortop']=mathmulriple(d.top,mul,1)

			doorstate=getDoorState(d.door.device.SN,d.door.door_no,0)
			ll['doorimg']=doorstate[0]
			usedoorhtml.append(ll)
			usedoor.append(d.door.id)
			
		sn=IclockZone.objects.filter(zone__in=zones).values("SN")
		doorall=AccDoor.objects.filter(device__in=sn,device__DelTag=0)
		for d in doorall:
			if d.id not in usedoor:
				ll={}
				ll['doorid']=d.id
				ll['doorno']=d.door_no
				ll['doorname']=d.door_name
				ll['sn']=d.device.Alias or d.device.SN
				doorstate=getDoorState(d.device.SN,d.door_no,0)
				ll['doorimg']=doorstate[0]
				doorhtml.append(ll)
	cc['door']=dumps(doorhtml)
	cc['usedoor']=dumps(usedoorhtml)
	return getJSResponse(cc) 
	
