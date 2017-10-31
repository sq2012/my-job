#!/usr/bin/env python
#coding=utf-8
import datetime
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from mysite.utils import *
from mysite.acc.models import *
from mysite.iclock.models import *
from mysite.iclock.iutils import *
@login_required
def getData(request):
	funid = request.GET.get("func", "")
	if funid == 'timezones_edit':
		if request.method=='GET':
			d={}
			colModels=[
				{'name':'id','width':100,'sortable':False,'align':'right','title':False,'label':""},
				{'name':'StartTime0','width':100,'sortable':False,'title':False,'align':'center','label':unicode(_(u'开始时间'))},
				{'name':'EndTime0','width':100,'sortable':False,'title':False,'align':'center','label':unicode(_(u'结束时间'))},
				{'name':'StartTime1','width':100,'sortable':False,'title':False,'align':'center','label':unicode(_(u'开始时间'))},
				{'name':'EndTime1','width':100,'sortable':False,'title':False,'align':'center','label':unicode(_(u'结束时间'))},
				{'name':'StartTime2','width':100,'sortable':False,'title':False,'align':'center','label':unicode(_(u'开始时间'))},
				{'name':'EndTime2','width':100,'sortable':False,'title':False,'align':'center','label':unicode(_(u'结束时间'))}
			]
			groupHeaders=[
				{'startColumnName': 'StartTime0', 'numberOfColumns': 2, 'titleText': '<em><font color="red">时间区间1</font></em>'},
				{'startColumnName': 'StartTime1', 'numberOfColumns': 2, 'titleText': '<em><font color="red">时间区间2</font></em>'},
				{'startColumnName': 'StartTime2', 'numberOfColumns': 2, 'titleText': '<em><font color="red">时间区间3</font></em>'},

			]

			d['colModel']=colModels
			d['groupHeaders']=groupHeaders

			return getJSResponse(d)
		else:
			key=request.GET.get('key','')
			rows=[]
			s_input="<input type='text'   id='timezone%s_%s' maxlength='2'  value='%s'  class='hour acctimezone'/>:<input type=text  id='timezone%s_%s' maxlength='2' value='%s' class='min acctimezone'/>"
			weeks=[u'周一',u'周二',u'周三',u'周四',u'周五',u'周六',u'周日',u'节日类型1',u'节日类型2',u'节日类型3']
			if key=='_new_':
				for i in range(10):
					row={'id':weeks[i]}
					for j in range(3):
						row['StartTime%s'%j]=s_input%(i,j*4,'00',i,j*4+1,'00')
						row['EndTime%s'%j]=s_input%(i,j*4+2,'00',i,j*4+3,'00')
					rows.append(row.copy())
			else:
				tzobj=timezones.objects.get(id=key)
				tz=tzobj.tz
				c=0
				for i in range(10):
					row={'id':weeks[i]}
					for j in range(3):
						s1=tz[c*12:c*12+2]
						s2=tz[c*12+3:c*12+3+2]
						row['StartTime%s'%j]=s_input%(i,j*4,s1,i,j*4+1,s2)
						e1=tz[c*12+6:c*12+6+2]
						e2=tz[c*12+9:c*12+9+2]


						row['EndTime%s'%j]=s_input%(i,j*4+2,e1,i,j*4+3,e2)
						c+=1
					rows.append(row.copy())



			#print "----------",rows
			t_r={}
			#rows=[{'id':"1",'StartTime1':"<input type='text'   id='timezone11_1' maxlength='2'  value='00'  class='hour acctimezone'/>:<input type=text value=23 id='timezone11_2' maxlength='2'  class='hour acctimezone'/>",'EndTime1':"<input type='text'  id='timezone12_1' maxlength='2'  value='00'  class='hour acctimezone'/>:<input type=text id='timezone12_2' value=23 maxlength='2'  class='hour acctimezone'/>"},{'id':'22','StartTime1':'12:00','EndTime1':'1221'}]
			t_r['page']=1
			t_r['total']=1
			t_r['records']=10
			t_r['rows']=rows
			return getJSResponse(t_r)
	elif funid=='devs':
		if request.method=='POST':
			q=request.POST.get("q","")
			if q=="":
				q=request.GET.get("q","")
			if request.user.is_superuser or request.user.is_alldept:
				if q!="":
					iclocks=iclock.objects.filter(Q(SN__contains=q)|Q(Alias__contains=q)).filter(Q(DelTag__isnull=True)|Q(DelTag=0))
				else:
					iclocks=iclock.objects.all()
			else:
				sns=userIClockList(request.user)
				if q!="":
					iclocks=iclock.objects.filter(SN__in=sns).filter(Q(SN__contains=q)|Q(Alias__contains=q)).filter(Q(DelTag__isnull=True)|Q(DelTag=0))
				else:
					iclocks=iclock.objects.filter(SN__in=sns)
			items=iclocks.filter(ProductType__in=[4,5,15]).exclude(DelTag=1)
			re=[]
			r={}
			for dev in items:
				r['SN']=dev.SN
				r['Alias']=dev.Alias
				re.append(r.copy())
			return getJSResponse(dumps(re))
	elif funid=='devs_tree':
		d={}
		dd={}
		ptype=request.GET.get('ptype','')

		if request.user.is_superuser or request.user.is_alldept:
			iclocks=iclock.objects.all()
		else:
			zonelist=userZoneList(request.user)
			sn_list=IclockZone.objects.filter(zone__in =zonelist).values_list("SN",flat=True)
			iclocks=iclock.objects.filter(SN__in=sn_list)		
		if ptype=='acc' or ptype=='AntiPassBack':
			if ptype=='acc':
				iclocks=iclocks.filter(ProductType__in=[4,5,15,25])
			else:
				devs=AntiPassBack.objects.all().values('device')
				iclocks=iclocks.filter(ProductType__in=[4,5,15,25]).exclude(SN__in=devs)
				
		#else:
		#	iclocks=iclocks.filter(Q(ProductType__isnull=True)|Q(ProductType=0))
		iclocks=iclocks.exclude(DelTag=1).exclude(State=0)
		d=[]
		for t in iclocks:

			dd["id"]=t.SN
			dd["name"]=u'%s(%s)'%(t.Alias or '',t.SN)
			dd["pid"]=0
			dd["value"]=t.SN
			dd["open"]=False
			dd["isParent"]=False
			d.append(dd.copy())
		return getJSResponse(d)
	elif funid=='devstree':
		d={}
		dd={}
		ptype=request.GET.get('ptype','')
		deptName=u'所有设备'
			
		if request.user.is_superuser or request.user.is_alldept:
			iclocks=iclock.objects.all()
		else:
			zonelist=userZoneList(request.user)
			sn_list=IclockZone.objects.filter(zone__in =zonelist).values_list("SN",flat=True)
			iclocks=iclock.objects.filter(SN__in=sn_list)	
		if ptype=='acc':
			iclocks=iclocks.filter(ProductType__in=[4,5,15,25])
		elif ptype=='patrol':
			iclocks=iclocks.filter(ProductType__in=[2])
			
		else:
			iclocks=iclocks.exclude(ProductType__in=[2,4,5,15,25])
		#	iclocks=iclocks.filter(Q(ProductType__isnull=True)|Q(ProductType=0))
		iclocks=iclocks.exclude(DelTag=1)
		d["id"]=0
		d["name"]=deptName
		d["pid"]=-1
		d["value"]=0
		d["open"]=True
		d["isParent"]=False
		d['icon']="/media/img/icons/home.png"
		d['nocheck']=True
		d["children"]=[]
		#meets=participants_tpl.objects.all().exclude(DelTag=1).order_by('-id')
		for t in iclocks:
			d["isParent"]=True

			dd["id"]=t.SN
			dd["name"]="%s(%s)"%(t.SN,t.Alias or '')
			dd["pid"]=0
			dd["value"]=t.SN
			dd["open"]=False
			dd["isParent"]=False
			d["children"].append(dd.copy())
		return getJSResponse(d)


	elif funid=='door_first':
		dd={}
		ptype=request.GET.get('ptype','')

		if request.user.is_superuser or request.user.is_alldept:
			iclocks=iclock.objects.all().exclude(DelTag=1).exclude(State=0).values("SN")
			accd=AccDoor.objects.filter(device__in=iclocks)
		else:
			iclocks=iclock.objects.all().exclude(DelTag=1).exclude(State=0).values("SN")
			accd=AccDoor.objects.filter(device__in=iclocks)
		if  ptype=='FirstOpen':
			doors=FirstOpen.objects.all().values_list("door",flat=True)
			accd=accd.exclude(id__in=doors)
		d=[]
		for t in accd:

			dd["id"]=t.id
			dd["name"]=t.door_name
			dd["pid"]=0
			dd["value"]=t.door_name
			dd["open"]=False
			dd["isParent"]=False
			d.append(dd.copy())
		return getJSResponse(d)

	elif funid=='ACTimeZones':
		timezone = timezones.objects.exclude(DelTag=1).order_by('id')
		re = []
		ss = {}
		for t in timezone:
			ss['TimeZoneID'] = t.id
			ss['Name'] = t.Name
			t = ss.copy()
			re.append(t)
		return getJSResponse(dumps(re))
	elif funid=='ACGroup':
		group=ACGroup.objects.all().order_by('GroupID')
		re = []
		ss = {}
		for g in group:
			ss['GroupID'] = g.GroupID
			ss['Name'] = g.Name
			g = ss.copy()
			re.append(g)
		return getJSResponse(dumps(re))
	elif funid=='level_door':
		key=request.GET.get('key','')
		ExistedDoor=[]
		chk=False
		if key:
			obj=level.objects.get(id=key)
			if obj.irange==-1:
				chk=True	#表示所有门
			else:
				objs=level_door.objects.filter(level=key)
				for t in objs:
					try:
						ExistedDoor.append(t.door_id)
					except:
						continue
		if not request.user.is_superuser:
			za = ZoneAdmin.objects.filter(user=request.user)
			zacode = za.values_list('code__code',flat=True)
			child=[]
			for a in za:
				child.append(a.code)
			iz=IclockZone.objects.filter(zone__DelTag=0,zone__in=child)
			sns = iz.values_list('SN__SN',flat=True)
			accs=AccDoor.objects.filter(device__DelTag=0,device__SN__in=sns).order_by('id')
			iclo=iclock.objects.filter(ProductType__in=[4,5,15,25],DelTag=0,SN__in=sns).order_by('SN')
			zo=zone.objects.filter(DelTag=0,code__in=zacode)
		else:
			iz=IclockZone.objects.filter(zone__DelTag=0)
			accs=AccDoor.objects.filter(device__DelTag=0).order_by('id')
			iclo=iclock.objects.filter(ProductType__in=[4,5,15,25]).order_by('SN')
			zo=zone.objects.filter(DelTag=0)
		zlist={}
		for z in iz:
			try:
				zlist[z.SN.SN]=z.zone.id
			except:
				continue

		re = [{'id':-1,'name':u'全部区域','pid':0,'open':True,'checked':chk,'Attribute':''}]
		ss = {}
		for t in accs:
			ss={}
			ss['id']=t.id
			ss['name']=t.door_name
			ss['pid']='i_'+t.device.SN
			if ss['id'] in ExistedDoor or chk:
				ss['checked']=True
			ss['Attribute']='door'
			re.append(ss.copy())

		for t in iclo:
			ss={}
			ss['id']='i_'+t.SN
			ss['name']='%s(%s)'%(t.SN,t.Alias or '')
			pid=-1
			try:
				pid=str(zlist[t.SN])
				pid='z_'+pid
			except:pass
			ss['pid']=pid
			ss['checked']=False
			ss['open']=True
			ss['Attribute']='iclock'
			re.append(ss.copy())

		for t in zo:
			ss={}
			ss['id']='z_'+str(t.id)
			ss['name']=t.name
			pid=-1
			if t.parent:
				pid='z_'+str(t.parent)
			ss['pid']=pid
			ss['checked']=False
			ss['open']=True
			ss['Attribute']='zone'
			re.append(ss.copy())
		
		return getJSResponse(re)
	elif funid=='antipassback':
		dd={}
		flag=request.GET.get('flag','')
		key=request.GET.get('keys','')
		linkid=request.GET.get('id','')
		isExistEvents=[]
		isExistInputs=[]
		isExistOutputs=[]
		re=[]
#		if flag=='add':
		dev=iclock.objects.get(SN=key)
		re=getAntiPassBackInfo(dev)

		return getJSResponse(re)
	elif funid=='interlock':
		dd={}
		flag=request.GET.get('flag','')
		key=request.GET.get('keys','')
		linkid=request.GET.get('id','')
		isExistEvents=[]
		isExistInputs=[]
		isExistOutputs=[]
		re=[]
#		if flag=='add':
		dev=iclock.objects.get(SN=key)
		re=getInterLockInfo(dev)
		#print "---------",re
		return getJSResponse(re)

		
	elif funid=='door_events':
		#from mysite.acc.models import EVENT_CHOICES
		dd={}
		flag=request.GET.get('flag','')
		key=request.GET.get('keys','')
		linkid=request.GET.get('id','')
		isExistEvents=[]
		isExistInputs=[]
		isExistOutputs=[]

		isExistEvents_in=[]
		isExistInputs_in=[]
		isExistOutputs_in=[]

		isExistEvents_reader=[]
		isExistInputs_reader=[]
		isExistOutputs_reader=[]
		door_events=[5,7,8,9,24,25,28,36,37,38,100,102,200,201,202,204,205,209]
		door_reader_events=[0,2,3,4,20,21,22,23,27,29,41,42,101]
		
		action_time=0
		if flag=='edit' and linkid!='':
			trigobjs=linkage_trigger.objects.filter(linkage_id=linkid)
			for t in trigobjs:
				if t.trigger_cond in door_events:
					isExistEvents.append(t.trigger_cond)
				elif t.trigger_cond in [220,221]:
					isExistEvents_in.append(t.trigger_cond)
				elif t.trigger_cond in door_reader_events:
					isExistEvents_reader.append(t.trigger_cond)
					

			inoutobjs=linkage_inout.objects.filter(linkage_id=linkid)
			for t in inoutobjs:
				if t.input_type in [0,1]:#暂未考虑读头输入
					isExistInputs.append(t.input_id)

					if t.output_type==0:
						isExistOutputs.append(t.output_id)
					if t.output_type==1:
						isExistOutputs.append(t.output_id*(-1))

				elif t.input_type in [2,100]:#辅助输入
					if t.input_type==100:
						isExistInputs_reader.append(0)
					else:
						isExistInputs_reader.append(t.input_id)
					
					if t.output_type==0:
						isExistOutputs_reader.append(t.output_id)
					if t.output_type==1:
						isExistOutputs_reader.append(t.output_id*(-1))


				elif t.input_type in [3,1000]:#辅助输入
					if t.input_type==1000:
						isExistInputs_in.append(0)
					else:
						isExistInputs_in.append(t.input_id)
					
					if t.output_type==0:
						isExistOutputs_in.append(t.output_id)
					if t.output_type==1:
						isExistOutputs_in.append(t.output_id*(-1))
					
				#print "----------------------",t.action_time,linkid
				action_time=t.action_time
		d = {'id':-10,'name':'门事件','pid':-100,'open':True,'checked':False,'children':[]}
		d_in = {'id':-10,'name':'辅助输入事件','pid':-100,'open':True,'checked':False,'children':[]}
		reader = {'id':-10,'name':'门和读头事件','pid':-100,'open':True,'checked':False,'children':[]}
		re={}
		#ex_events=[-1,5,6,10,11,12,13,14,15,16,17,18,19,25,26,30,31,32,33,34,35,206,222,223]
		for t in EVENT_CHOICES:
			dd={}
			dd["id"]=t[0]
			dd["name"]=u'%s'%t[1]
			dd["pid"]=-10
			dd["value"]=t[0]

			dd["open"]=False
			dd["isParent"]=False
			if t[0] in [220,221]:
				if dd['id'] in isExistEvents_in:
					dd['checked']=True
				d_in['children'].append(dd.copy())
			elif t[0] in door_events:
				if dd['id'] in isExistEvents:
					dd['checked']=True

				d['children'].append(dd.copy())
			elif t[0] in door_reader_events:
				if dd['id'] in isExistEvents_reader:
					dd['checked']=True

				reader['children'].append(dd.copy())
				

		re['ret']=len(d['children'])
		re['events']=d
		re['in_events']=d_in
		re['reader_events']=reader
		#dev=getDevice(key)
		inputs = {'id':-10,'name':u'输入点','pid':-100,'open':True,'chkDisabled':True,'children':[{'id':0,'name':u'任意','pid':-10,'value':0}]}
		
		doors=AccDoor.objects.filter(device=key).order_by('door_no')
		for t in doors:
			dd={}
			dd["id"]=t.id
			dd["name"]=u'%s'%t.door_name
			dd["pid"]=-10
			dd["value"]=t.id
			dd["open"]=False
			dd["isParent"]=False


			inputs['children'].append(dd.copy())
		for t in inputs['children']:
			t['checked']=False
			if t['id'] in isExistInputs:
				t['checked']=True

		re['inputs']=copy.deepcopy(inputs)
		
		
		in_inputs = {'id':-10,'name':u'输入点','pid':-100,'open':True,'chkDisabled':True,'children':[{'id':0,'name':u'任意','pid':-10,'value':0}]}
		
		auxins=AuxIn.objects.filter(device=key).order_by('aux_no')
		#in_inputs['children']=in_inputs['children'][1:100]
		for t in auxins:
			dd["id"]=t.id
			dd["name"]=u'%s'%t.aux_name
			dd["pid"]=-10
			dd["value"]=t.id
			dd["open"]=False
			dd["isParent"]=False
			in_inputs['children'].append(dd.copy())
		for t in in_inputs['children']:
			t['checked']=False
			if t['id'] in isExistInputs_in:
				t['checked']=True
		re['in_inputs']=in_inputs

		reader_inputs = {'id':-10,'name':u'输入点','pid':-100,'open':True,'chkDisabled':True,'children':[{'id':0,'name':u'任意','pid':-10,'value':0}]}
		
		readers=device_options.objects.filter(SN=key,ParaName='ReaderCount')
		readerCount=0
		if readers:
			readerCount=int(readers[0].ParaValue)
		#in_inputs['children']=in_inputs['children'][1:100]
		for i in range(readerCount):
			dd["id"]=i+1
			dd["name"]=u'Reader %s'%(i+1)
			dd["pid"]=-10
			dd["value"]=i+1
			dd["open"]=False
			dd["isParent"]=False
			reader_inputs['children'].append(dd.copy())
		for t in reader_inputs['children']:
			t['checked']=False
			if t['id'] in isExistInputs_reader:
				t['checked']=True
		re['reader_inputs']=reader_inputs








		
		auxouts=AuxOut.objects.filter(device=key).order_by('aux_no')
		outputs = {'id':-10,'name':u'输出点','pid':-100,'open':True,'chkDisabled':True,'children':[{'id':0,'name':u'任意','pid':-10,'value':0}]}
		#inputs['name']=u'输出点'
		outputs['children']=copy.deepcopy(inputs['children'][1:100])
		for t in auxouts:
			dd["id"]=t.id*(-1)
			dd["name"]=u'%s'%t.aux_name
			dd["pid"]=-10
			dd["value"]=t.id
			dd["open"]=False
			dd["isParent"]=False
			outputs['children'].append(dd.copy())
			
		outputs_in=copy.deepcopy(outputs)			
		outputs_reader=copy.deepcopy(outputs)	
		for t in outputs['children']:
			t['checked']=False
			if t['id'] in isExistOutputs:
				t['checked']=True
				
		for t in outputs_in['children']:
			t['checked']=False
			if t['id'] in isExistOutputs_in:
				t['checked']=True
				
		for t in outputs_reader['children']:
			t['checked']=False
			if t['id'] in isExistOutputs_reader:
				t['checked']=True
				
		re['outputs']=outputs
		re['in_outputs']=outputs_in
		re['reader_outputs']=outputs_reader
		
		
		
		
		
		
		re['action_time']=action_time
		return getJSResponse(re)
	elif funid=='zonetree':
		#d={}
		rt=[]
		code=request.GET.get('code','')
		child=[]
		if code:
			AllChildrenZone(code,child)
		if request.user.is_superuser:
			objs=zone.objects.all().order_by('parent','code').exclude(DelTag=1).exclude(code=code)
		else:
			zonelist=userZoneList(request.user)
			objs=zone.objects.filter(id__in=zonelist).order_by('parent','code').exclude(DelTag=1).exclude(code=code)
		ll={}
		zones={}
		for o in objs:
			if o in child:continue
			zones['%s_code'%o.id]=o.code
			zones['%s_id'%o.id]=o.id
			zones['%s_name'%o.id]=o.name
			zones['%s_parent'%o.id]=o.parent
			try:
				ll[int(o.parent)].append(o.id)
			except:
				ll[int(o.parent)]=[]
				ll[int(o.parent)].append(o.id)
		usedzone=[]
		for z in objs:
			d={}
			if z.id in usedzone or z in child:
				continue
			usedzone.append(z.id)
			d["id"]=z.id
			d["name"]=z.name
			d["pid"]=z.parent
			d["value"]=0
			d["open"]=True
			d["isParent"]=False
			#if d['pid']==0:
			#	d['icon']="/media/img/icons/home.png"
			try:
				d["children"]=get_zone_list(z.id,ll,zones,usedzone)
			except:
				d["children"]=[]
			rt.append(d.copy())
		return getJSResponse(rt)
	elif funid=='combopen':
		d={}
		re=[]
		objs=combopen.objects.all().order_by('id')
		for t in objs:
			dd={}
			dd['id']=t.id
			dd['name']=t.name
			dd['count']=combopen_emp.objects.filter(combopen=t).count()
			re.append(dd.copy())
		
		d['combopen']=re
		rt=[]
		key=int(request.GET.get('key','-1'))
		objs=combopen_comb.objects.filter(combopen_door=key).order_by('sort')
		for t in objs:
			dd={}
			dd['combid']=t.combopen_id
			dd['opennumber']=t.opener_number
			rt.append(dd.copy())
		d['comb']=rt
		return getJSResponse(d)
	elif funid=='emp_door':
		UserID=request.GET.get('id')
		sord=request.POST.get('sord')
		objs=level_emp.objects.filter(UserID=UserID).values('level')
		if sord=='desc':
			doors=level_door.objects.filter(level__in=objs).distinct().order_by('-door_id')
		else:
			doors=level_door.objects.filter(level__in=objs).distinct().order_by('door_id')
		rt=[]
		for t in doors:
			dd={}
			dd['id']=t.door_id
			dd['door_name']=t.door.door_name
			dd['door_no']=t.door.door_no
			dd['device']=u'%s'%t.door.device
			rt.append(dd.copy())
		return getJSResponse(rt)
	elif funid=='door_emp':
		doorID=request.GET.get('id')
		sord=request.POST.get('sord')
		objs=level_door.objects.filter(door=doorID).values('level')
		if sord=='desc':
			emps=level_emp.objects.filter(level__in=objs).exclude(UserID__OffDuty=1).exclude(UserID__DelTag=1).distinct().order_by('-UserID__PIN')
		else:
			emps=level_emp.objects.filter(level__in=objs).exclude(UserID__OffDuty=1).exclude(UserID__DelTag=1).distinct().order_by('UserID__PIN')
		rt=[]
		ids=set()
		for t in emps:
			ids.add(t.UserID_id)
		for id in ids:
			dd={}
			emp=employee.objByID(id)
			dd['id']=emp.id
			dd['PIN']=emp.PIN
			dd['EName']=emp.EName or ''
			dd['Gender']=u'%s'%(emp.get_Gender_display() or '')
			dd['DeptName']=u'%s'%emp.Dept().DeptName
			dd['Card']=u'%s'%(emp.Card or '')
			rt.append(dd.copy())
		return getJSResponse(rt)
		
def userZoneList(user):
	Result=[]
	if (user.is_superuser):
		return Result
	else:
		rs_zone = ZoneAdmin.objects.filter(user=user).order_by("code")
		for t in rs_zone:
			Result.append(int(t.code_id))
	return Result

def get_zone_list(key,ll,zones,usedzone):
	d=[]
	dd={}
	for o in ll[key]:
		if zones['%s_id'%o] in usedzone:
			continue
		usedzone.append(zones['%s_id'%o])
		dd["id"]=zones['%s_id'%o]
		dd["name"]=zones['%s_name'%o]
		dd["pid"]=zones['%s_parent'%o]
		dd["value"]=zones['%s_code'%o]
		dd["open"]=False
		dd["isParent"]=False
		try:
			dd["children"]=get_zone_list(o,ll,zones,usedzone)
		except:
			dd["children"]=[]
		d.append(dd.copy())
	return d



def get_devices_of_tcp(request):
	"""获取非PUSH设备，iclock中ProductType=15为非PUSH设备,TCP/IP和RS485的区分方法是iclock中的IPAddress为IP地址时是TCP/IP,为2:COM1的格式时为RS485"""
	from mysite.iclock.iutils import getoptionsAttParam
	ret=[]
	d={}
	ll=getoptionsAttParam()

	objs=iclock.objects.filter(ProductType=15).exclude(DelTag=1)
	for t in objs:
		if not t.IPAddress:continue
		d['SN']=t.SN
		d['IPAddress']=t.IPAddress
		d['Password']=ll['compwd']
		d['CommType']='TCP'
		if ':' in t.IPAddress:
			d['CommType']='RS485'
			ls=t.IPAddress.split(':')
			d['DEVID']=ls[0]
			d['PORT']=ls[1]
			
		ret.append(d.copy())
	return getJSResponse(ret)
	
def ChildrenZone(code):
	return zone.objects.filter(parent=code)

def AllChildrenZone(code, start=[]):
	for d in ChildrenZone(code):
		if d not in start:
			start.append(d)
			AllChildrenZone(d.code,start)