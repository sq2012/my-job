#!/usr/bin/env python
#coding=utf-8
import datetime
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from mysite.utils import *
from mysite.ipos.models import *
from mysite.iclock.models import *
from mysite.iclock.iutils import userIClockList
@login_required
def getData(request):
	funid = request.GET.get("func", "")
	code = request.GET.get("code", "")
	if funid=='posmeal':
		d={}
		dd={}
		meals=Meal.objects.all().exclude(DelTag=1).exclude(available=0)
		d=[]
		meal_list=[]
		if code!='':
			ic=ICcardposmeal.objects.filter(iccard__code=code)
			for i in ic:
				meal_list.append(i.meal.code)
		for m in meals:
			dd["id"]=m.code
			dd["name"]=m.name
			dd["pid"]=0
			dd["value"]=m.name
			dd["open"]=False
			if m.code in meal_list:
				dd["checked"]=True
			else:
				dd["checked"]=False
			dd["isParent"]=False
			d.append(dd.copy())
		return getJSResponse(d)
	elif funid=='use_mechine':
		d={}
		dd={}
		SN_list=[]
		if code!='':
			ic=ICcardmechine.objects.filter(iccard__code=code)
			for i in ic:
				SN_list.append(i.SN.SN)
#		if request.user.is_superuser or request.user.is_alldept:
		iclocks=iclock.objects.filter(ProductType__in=[11])
#		else:
#			sns=userIClockList(request.user)
#			iclocks=iclock.objects.filter(SN__in=sns,ProductType__in=[11])
		iclocks=iclocks.exclude(DelTag=1)
		d=[]
		for t in iclocks:
			dd["id"]=t.SN
			dd["name"]=u'%s(%s)'%(t.SN,t.Alias or '')
			dd["pid"]=0
			dd["value"]=t.SN
			if t.SN in SN_list:
				dd["checked"]=True
			else:
				dd["checked"]=False
			dd["open"]=False
			dd["isParent"]=False
			d.append(dd.copy())
		return getJSResponse(d)
	elif funid=='use_meal_machine':
		d={}
		dd={}
		SN_list=[]
		if code!='':
			ic=Mealmachine.objects.filter(meal__code=code)
			for i in ic:
				SN_list.append(i.SN.SN)
		iclocks=iclock.objects.filter(ProductType__in=[11])
		iclocks=iclocks.exclude(DelTag=1)
		d=[]
		for t in iclocks:
			dd["id"]=t.SN
			dd["name"]=u'%s(%s)'%(t.SN,t.Alias or '')
			dd["pid"]=0
			dd["value"]=t.SN
			if t.SN in SN_list:
				dd["checked"]=True
			else:
				dd["checked"]=False
			dd["open"]=False
			dd["isParent"]=False
			d.append(dd.copy())
		return getJSResponse(d)
	elif funid=='sptime_use_mechine':
		SN_list=[]
		if code!='':
			ic=SplitTimemechine.objects.filter(splittime__code=code)
			for i in ic:
				SN_list.append(i.SN.SN)
		if request.user.is_superuser or request.user.is_alldept:
			iclocks=iclock.objects.filter(ProductType__in=[11,12,13])
		else:
			sns=userIClockList(request.user)
			iclocks=iclock.objects.filter(SN__in=sns,ProductType__in=[11,12,13])
		iclocks=iclocks.exclude(DelTag=1)
		d=[]
		for t in iclocks:
			dd={}
			dd["id"]=t.SN
			dd["name"]=t.SN
			dd["pid"]=0
			dd["value"]=t.SN
			if t.SN in SN_list:
				dd["checked"]=True
			else:
				dd["checked"]=False
			dd["open"]=False
			dd["isParent"]=False
			d.append(dd.copy())
		return getJSResponse(d)
	elif funid=='kv_use_mechine':
		SN_list=[]
		if code!='':
			ic=KeyValuemechine.objects.filter(keyvalue__code=code)
			for i in ic:
				SN_list.append(i.SN.SN)
		if request.user.is_superuser or request.user.is_alldept:
			iclocks=iclock.objects.filter(ProductType__in=[11,12,13])
		else:
			sns=userIClockList(request.user)
			iclocks=iclock.objects.filter(SN__in=sns,ProductType__in=[11,12,13])
		iclocks=iclocks.exclude(DelTag=1)
		d=[]
		for t in iclocks:
			dd={}
			dd["id"]=t.SN
			dd["name"]=t.SN
			dd["pid"]=0
			dd["value"]=t.SN
			if t.SN in SN_list:
				dd["checked"]=True
			else:
				dd["checked"]=False
			dd["open"]=False
			dd["isParent"]=False
			d.append(dd.copy())
		return getJSResponse(d)
	elif funid=='dining':
		SN_list=[]
		if code!='':
			ic=IclockDininghall.objects.filter(SN__SN=code)
			for i in ic:
				SN_list.append(i.dining.id)
		dining=Dininghall.objects.all().exclude(DelTag=1)
		d=''
		#if code!='issue_managecard':#发管理卡时不要下面的
		d="<option value='0'>%s</option>"%(u"所有餐厅")
		for t in dining:
			if t.id in SN_list:
				d+="<option value='%s' selected>%s</option>"%(t.id,t.name)
			else:
				d+="<option value='%s'>%s</option>"%(t.id,t.name)
		return getJSResponse({"ret":1,"message":d})
	elif funid=='IssueCard':
		sys_card_no = request.GET.get("sys_card_no", "")
		card_no = request.GET.get("cardno", "")
		key = request.GET.get("key", "")
		if sys_card_no:
			objs=IssueCard.objects.filter(sys_card_no__exact = sys_card_no)
		elif card_no:
			objs=IssueCard.objects.filter(cardno__exact = card_no).order_by('-id')
		elif key:
			objs=IssueCard.objects.filter(pk = key)
			
		re=[]
		if objs:
			d={}
			d['PIN']=''
			d['Dept']=''
			d['name']=''
			d['cardno']=objs[0].cardno
			d['card_cost']=str(objs[0].card_cost)
			d['mng_cost']=str(objs[0].mng_cost)
			if objs[0].UserID:
				emp=employee.objByID(objs[0].UserID_id)
				d['PIN']=emp.PIN
				d['Dept']=emp.Dept().DeptName
				d['name']=emp.EName
			d['cardstate']=objs[0].cardstatus
			d['blance']=str(objs[0].blance)
			d['pwd']=objs[0].Password
			#d['sys_blance']=0
			re.append(d.copy())
		return getJSResponse(re)
	elif funid=='diningtree':
		#d={}
		rt=[]
		objs=Dininghall.objects.all().order_by('code').exclude(DelTag=1)
		for z in objs:
			d={}
			d["id"]=z.id
			d["name"]=z.name
			d["pid"]=0
			d["value"]=0
			d["open"]=True
			d["isParent"]=False
			d['icon']="/media/img/icons/home.png"
			rt.append(d.copy())
		return getJSResponse(rt)		
	elif funid=='check_card':#检查初始化卡是否合规
		#d={}
		rs={'ret':0}
		card=request.GET.get('card','')
		if card:
			tmpcard = IssueCard.objects.filter(cardno=card,cardstatus = CARD_VALID)
			if not tmpcard:
				rs['ret']=1
		return getJSResponse(rs)		
		
		