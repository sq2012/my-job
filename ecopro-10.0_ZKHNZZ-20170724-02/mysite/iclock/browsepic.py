#!/usr/bin/env python
#coding=utf-8
from django.template import Context, RequestContext, Template, TemplateDoesNotExist
from mysite.utils import *
from mysite.cab import listFile
import os
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from mysite.iclock.models import createThumbnail, formatPIN,employee
from django.contrib.auth.decorators import login_required,permission_required
from mysite.iclock.iutils import userIClockList 
#imgUrlOrg=getUploadFileName(device.SN, pin, fname)
from django.core.paginator import Paginator
from mysite.iclock.datautils import hasPerm
def listPic(path, pattern):
	picPath=os.path.split(getUploadFileName(path,"",""))[0]
	flist=listFile(picPath, pattern)
	flist.sort(reverse=True)
	return flist

def listDir(request, path):
	sn_list=None
	valid_sn=None
	if not request.user.is_superuser:
		sn_list=AuthedIClockList(request.user)
	if not path[0]:
		valid_sn=sn_list
	elif (sn_list!=None) and (path[0] not in sn_list):
		return []
	path="/".join(path)
	path=getUploadFileName(path,"","")
	for root,dirs,files in os.walk(path):
		if "thumbnail" in dirs:
			dirs.remove("thumbnail")
		if valid_sn==None: return dirs
		return [i for i in dirs if i in valid_sn]
	return []

def get_pictures_of_device(request):
	Result={}
	datas=[]
	d={}
	d['id']=1
	
#		line['urls']="<img src=/iclock/file/upload/%s/%s/%s-%s.jpg  style='height:120px;'/>" %(l.Device().SN,l.TTime.strftime("%Y%m"),l.TTime.strftime("%Y%m%d%H%M%S"),devPIN)

	ttime=request.GET.get('ttime')
	sn=request.GET.get('key')
	mon=ttime[:6]
	cmap_path="%s/%s/" %(sn,mon)
	flist=listPic(cmap_path,'*.jpg')
	if len(ttime)==8:
		templist=[]
		for t in flist:
			if ttime in t:
				templist.append(t)
		flist=templist
	offset = int(request.GET.get('page', 1))

	limit= int(request.GET.get('rows', 30))
	
	p=Paginator(flist, limit,allow_empty_first_page=True)
	item_count=p.count
	if item_count<(offset-1)*limit:
		offset=1
	page_count=p.num_pages
	pp=p.page(offset)
	j=0
	for t in pp:
		fname=os.path.split(t)[1]
		s_name=os.path.splitext(fname)[0]
		lname=s_name.split('-')
		tm=lname[0]
		pin=''
		stime='%s-%s %s:%s:%s'%(tm[4:6],tm[6:8],tm[8:10],tm[10:12],tm[12:14])
		if len(lname)==2:#通过照片
			pin=lname[1]
			try:
				obj=employee.objByPIN(pin)
			except:
				obj=None
			if obj:
				pin=pin+'  '+obj.EName or ''
			d['p%d'%j]=u"<div><img src=/iclock/file/upload/%s/%s/%s  style='height:160px;'/></div><div>%s<br>%s</div>" %(sn,mon,fname,pin,stime)
		else:
			d['p%d'%j]=u"<div style='border:1px solid red;'><img src=/iclock/file/upload/%s/%s/%s  style='height:160px;'/></div><div>%s<br>%s</div>" %(sn,mon,fname,'',stime)
						
		j+=1
		if j==6:
			datas.append(d.copy())
			d={}
			j=0
			d['id']=item_count/6
	if d:
		datas.append(d.copy())
	
	Result['page']=offset
	Result['records']=item_count
	Result['total']=page_count
	Result['rows']=datas
	return Result

def get_pictures_of_employee(request,cc):

	datas=[]
	j=0
	d={'id':j}
	can_edit=hasPerm(request.user, employee, 'change')
	for t in cc['latest_item_list']:
		fname=t.PIN+'.jpg'
		pin=u'%s %s'%(t.PIN,t.EName or '')
		if can_edit:
			pin="""<a class='can_edit'  href='#' onclick='javascript:editclick(%s);'>%s</a>"""%(t.id,pin)
		
		
		
		cmapfile="%s/photo/%s" %(settings.ADDITION_FILE_ROOT,fname)



		if os.path.exists(cmapfile):
			d['p%d'%j]=u"<div><img src=/iclock/file/photo/%s  style='height:180px;'/></div><div>%s</div>" %(fname,pin)
			#以下为泰康保险定制
			#if hasattr(settings,'SHOWEMPPHOTO') and settings.SHOWEMPPHOTO==0:
			#	if BioData.objects.filter(UserID=t.id,bio_type=bioFace).count()==0:
			#		d['p%d'%j]=u"<div><img src=/media/img/transaction/user_default.gif style='height:180px;'/></div><div>%s</div>"%(pin)



		else:
			d['p%d'%j]=u"<div><img src=/media/img/transaction/user_default.gif style='height:180px;'/></div><div>%s</div>"%(pin)
		
		
		
						
		j+=1
		if j==6:
			datas.append(d.copy())
			d={}
			j=0
			d['id']=j
	if d:
		datas.append(d.copy())
	return dumps1(datas)

@login_required	
def index(request, path):
	if request.method=='POST':
		Result={}
		if path=='devpictures':
			Result=get_pictures_of_device(request)
		else:
			pass
		
		
		#rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
		return getJSResponse(Result)
