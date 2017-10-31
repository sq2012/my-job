#!/usr/bin/env python
#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.cache import cache
from mysite.iclock.models import *
import string
import datetime
import time
from mysite.utils import *
from django.conf import settings
#from django.contrib.auth.models import User
from django.utils.encoding import smart_str
import sys,os
from django.db import connection as conn
from reb import *
from django.utils.translation import ugettext_lazy as _
#from django.utils.translation import gettext 
from datas import InitData
from mysite.iclock.iutils import *
from mysite.iclock.datasproc import *
import re
#import PIL.Image as Image
from PIL import Image
import base64
from django.contrib.auth import get_user_model
from mysite.meeting.models import *
from mysite.acc.models import *
from mysite.ipos.models import *
from mysite.core.cmdproc import *
def batchOp(request, dataModel, func):
	if request.method == 'POST':
		keys=request.POST.getlist("K")
	else: 
		keys=request.GET.getlist("K")
	info=[]
	ret=None
	t1=datetime.datetime.now()
	try:
		for i in keys:
			if dataModel==USER_SPEDAY:
				u=USER_SPEDAY.objects.filter(id=int(i))[0]
				deleteCalcLog(UserID=int(u.UserID_id),StartDate=u.StartSpecDay,EndDate=u.EndSpecDay)
			d=dataModel.objects.in_bulk([i])
			dev=d[d.keys()[0]]
			ret=func(dev)
		if ("%s"%ret)==ret:
			info.append(ret)
	except:
		pass
	if len(keys)<3 and dataModel==iclock:
		for i in keys:
			dev=getDevice(i)
			sendRecCMD(dev)
	
	t1=datetime.datetime.now()-t1
#	print "batchOp waste time===============",t1
	if len(info)>0:
		return u',\n'.join([u"%s"%f for f in info])
	return ret

dict_del_table = { # 要删除的 fk 表 记录
    str(employee) : ['fptemp'],
	str(iclock): [],
}

def delData(request, dataModel):
	if request.method == 'POST':
		keys=request.POST.getlist("K")
	else: 
		keys=request.GET.getlist("K")
	User=get_user_model()
	if dataModel==InterLock:
		objs=InterLock.objects.filter(id__in=keys)
		for t in objs:
			clear_interlock([t.device_id])
			#sendInterLockToAcc([],[t.device_id])
	if dataModel==FirstOpen_emp:
		objs=FirstOpen_emp.objects.filter(pk__in=keys)#.values_list('level',flat=True))
		emps=FirstOpen_emp.objects.filter(pk__in=keys)#.values_list('UserID',flat=True))
		try:
			deleteFirstCardEmpfromAcc(objs,emps)
		except Exception,e:
			print "4444444444",e
	if dataModel==combopen_emp:
		emps=combopen_emp.objects.filter(id__in=keys).values('UserID')
		acc_employee.objects.filter(UserID__in=emps).update(morecard_group=None)				
	
	if dataModel==forgetcause:
		if keys:
			keys = keys[0].split(',')
			dataModel.objects.filter(id__in=keys).delete()
	if dataModel==User:
		
		dataModel.objects.filter(id__in=keys).exclude(id=request.user.id).exclude(username='employee').update(DelTag=1)
		DeptAdmin.objects.filter(user__in=keys).exclude(user=request.user).delete()
		UserAdmin.objects.filter(owned__in=keys).delete()
		sql = 'delete from auth_user_groups where myuser_id in (%s)'%(','.join(keys))
		try:
			customSql(sql)
		except Exception,e:
			raise e
	elif dataModel== Group:
		for i in keys:
			sql='select count(*) from auth_user_groups where group_id=%s'%i
#			cs=customSql(sql,False)
			cs=customSql(sql,action=False)
			c=cs.fetchone()[0]
			if c==0:#如果没使用允许删除
				dataModel.objects.all().filter(pk=i).delete()
			else:
				raise Exception(u"%s"%_(u'正在使用的管理组不允许删除'))
		#adminLog(time=datetime.datetime.now(),User=request.user, model='groups', action=u'%s'%_("del"), object="del").save()
				

#	elif dataModel==facetemp:
#		facetemp.objects.filter(id__in=keys).delete()
	elif dataModel==department:
		if '1' in keys:
			raise Exception(u"%s"%_(u'根部门不允许删除，可以修改编号和名称'))
		
		if dataModel.objects.filter(parent__in=keys).exclude(DelTag=1).count()>0:
			raise Exception(u"%s"%_(u'选择的部门存在下级部门不允许删除'))
		if employee.objects.filter(DeptID__in=keys).exclude(DelTag=1).count()>0:
			raise Exception(u"%s"%_(u'选择的部门存在人员不允许删除'))
		dataModel.objects.filter(pk__in=keys).exclude(pk=1).update(DelTag=1)
		UpdateDeptCache()
	elif dataModel==Dininghall:
		if '1' in keys:
			raise Exception(u"%s"%_(u'根餐厅不允许删除，可以修改名称'))
		if IclockDininghall.objects.filter(dining__in=keys).exclude(SN__DelTag=1).count()>0:
			raise Exception(u"%s"%_(u'选择的餐厅存在设备不允许删除'))
		dataModel.objects.filter(pk__in=keys).exclude(pk=1).delete()
	elif dataModel==ICcard:
		if '1' in keys:
			raise Exception(u"%s"%_(u'系统卡类不允许删除，可修改信息'))
		dataModel.objects.filter(pk__in=keys).exclude(pk=1).update(DelTag=1)
	elif dataModel==Merchandise:
		code_list=dataModel.objects.filter(id__in=keys).values_list('code',flat=True)
		for c in code_list:
			if StoreDetail.objects.filter(store_code=c):
				dataModel.objects.filter(code=c).update(DelTag=1)
			else:
				dataModel.objects.filter(code=c).delete()
	elif dataModel==Allowance:
		ts=dataModel.objects.filter(pk__in=keys)
		if ts:
			for t in ts:
				if t.is_pass==1:
					raise Exception(u"%s"%_(u'该补贴已通过审核，不允许删除'))
		dataModel.objects.filter(pk__in=keys).delete()
	elif dataModel==Merchandise:
		from mysite.core.cmdproc import delete_pos_device_info
		devset=iclock.objects.filter(ProductType__in=[11,12,13]).exclude(DelTag=1)
		datalist=dataModel.objects.filter(pk__in=keys)
		op=''
		tablename="STOREINFO"
		delete_pos_device_info(devset,datalist,op,tablename)
		dataModel.objects.filter(pk__in=keys).update(DelTag=1)
	elif dataModel==KeyValue:
		from mysite.core.cmdproc import delete_pos_device_info
		ts=KeyValuemechine.objects.filter(keyvalue__in=keys)
		if ts:
			devset=[]
			for t in ts:
				devset.append(t.SN)
		else:
			devset=iclock.objects.filter(ProductType__in=[11,12,13]).exclude(DelTag=1)
		datalist=dataModel.objects.filter(pk__in=keys)
		op=''
		tablename="PRESSKEY"
		delete_pos_device_info(devset,datalist,op,tablename)
		dataModel.objects.filter(pk__in=keys).update(DelTag=1)
		KeyValuemechine.objects.filter(keyvalue__in=keys).delete()
	elif dataModel==zone:
		if '1' in keys:
			raise Exception(u"%s"%_(u'根区域不允许删除，可以修改编号和名称'))
		if dataModel.objects.filter(parent__in=keys).exclude(DelTag=1).count()>0:
			raise Exception(u"%s"%_(u'选择的区域存在下级区域不允许删除'))
		dataModel.objects.filter(id__in=keys).update(DelTag=1)
	elif dataModel==timezones:
		if '1' in keys:
			raise Exception(u"%s"%_(u'初始时间段不允许删除，可以修改'))
		dataModel.objects.filter(pk__in=keys).exclude(pk=1).update(DelTag=1)
	elif dataModel==level_emp:
		Levels=list(level_emp.objects.filter(pk__in=keys).distinct().values_list('level',flat=True))
		level_emps=level_emp.objects.filter(pk__in=keys)#.values_list('UserID',flat=True))
		empss=list(level_emps.values_list('UserID',flat=True))
		emps=employee.objects.filter(id__in=empss)
		try:
			deleteEmpfromAcc(Levels,emps,keys,1)
		except Exception,e:
			print "level_emp4444444444",e
		#level_emps.delete()
	elif dataModel==AntiPassBack:
		
		objs=AntiPassBack.objects.filter(pk__in=keys)
		for obj in objs:
			clear_antipassback(obj.device.SN)
		objs.delete()
	elif dataModel==FirstOpen:
		FirstOpen_emp.objects.filter(firstopen__in=keys).delete()
		sendFirstCardToAcc(keys)
		FirstOpen.objects.filter(id__in=keys).delete()
	elif dataModel==linkage:
		objs=linkage.objects.filter(pk__in=keys)
		for link in objs:
			SN=link.device_id
			trig_objs=linkage_trigger.objects.filter(linkage=link)
			del_linkage_trig(SN,trig_objs)
			trig_objs.delete()
			linkage_inout.objects.filter(linkage=link).delete()
		objs.delete()
			
	elif dataModel==level:
		Levels=keys
		emps=level_emp.objects.filter(level__in=keys).values('UserID')#.values_list('UserID',flat=True))
		emps=employee.objects.filter(id__in=emps)
		try:
			deleteEmpfromAcc(Levels,emps,[],-1)
		except Exception,e:
			print "4444444444",e
		level_door.objects.filter(level__in=keys).delete()
		level_emp.objects.filter(level__in=keys).delete()
		level.objects.filter(pk__in=keys).delete()
		#userids=list(emps.values_list('UserID',flat=True))
		levels=list(level_emp.objects.filter(UserID__in=emps).values_list('level',flat=True))
		
		#sendLevelToAcc(emps,levels)
	elif dataModel==combopen_door:
		objs=combopen_door.objects.filter(id__in=keys)
		clear_multimcard(objs)
		combopen_comb.objects.filter(combopen_door__in=keys).delete()
		objs.delete()
	#elif dataModel==facetemp:
	#	for k in keys:
	#		uid=facetemp.objects.get(id=k).UserID_id
	#		facetemp.objects.filter(UserID_id=uid).delete()
	elif  fieldVerboseName(dataModel, "DelTag"):
		if dataModel==MeetLocation:
			now=datetime.datetime((datetime.datetime.today()).year, (datetime.datetime.today()).month, (datetime.datetime.today()).day, 0, 0, 0)#修改会议开完后还是无法删除会议室bug
			# if Meet.objects.filter(LocationID__pk__in=keys).count()>0:
			if Meet.objects.filter(LocationID__pk__in=keys).exclude(Endtime__lt=now).count()>0:
				raise Exception(u'会议室处于占用状态，无法删除')
		dataModel.objects.filter(pk__in=keys).update(DelTag=1)
		if dataModel==iclock:
			for sn in keys:
				cache.delete("iclock_"+sn)
				IclockDininghall.objects.filter(SN__exact=sn).delete()
				IclockDept.objects.filter(SN=sn).delete()
				IclockZone.objects.filter(SN=sn).delete()
				doorids=AccDoor.objects.filter(device=sn).values_list('pk',flat=True)
				level_door.objects.filter(door__pk__in=doorids).delete()
				empofdevice.objects.filter(SN=sn).delete()
#				for item in dev_halls:
#				    item.delete()
		if dataModel==employee:
			emps = dataModel.objects.filter(pk__in=keys)
			iclocks=iclock.objects.filter(ProductType__in=[5,15,25])
			dataModel.objects.filter(pk__in=keys).update(OpStamp=datetime.datetime.now())
			for t in emps:
				delEmpInDevice(t.PIN,-1)
				for dev in iclocks:
					delete_data(dev.SN,'user','Pin=%s'%t.pin())
				cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,t.PIN))
				cache.delete("%s_iclock_emp_%s"%(settings.UNIT,t.id))
			combopen_emp.objects.filter(UserID__in=emps).delete()
		if dataModel==SchClass:
			sch = dataModel.objects.filter(pk__in=keys)
			for s in sch:
				cache.delete("%s_iclock_schclass_%s"%(settings.UNIT,s.SchclassID))
			cache.delete("%s_schclasses"%(settings.UNIT))
			
			
	else:
		rows=dataModel.objects.filter(pk__in=keys)
		if dataModel==USER_SPEDAY:
			for row in rows: 
				#u=USER_SPEDAY.objects.filter(id=int(row.id))[0]
				deleteCalcLog(UserID=row.UserID_id,StartDate=row.StartSpecDay,EndDate=row.EndSpecDay)
			from mysite.iclock.fileprocess import del_spedy_file
			del_spedy_file(keys)
				#attCalcLog.objects.filter(UserID=int(u.UserID.id)).delete()
		elif dataModel==days_off:
			for row in rows: 
				#u=days_off.objects.filter(id=int(row.id))[0]
				#if u.UserID:
					
				deleteCalcLog(UserID=row.UserID,StartDate=row.FromDate,EndDate=row.ToDate)
		elif dataModel==checkexact:
			for row in rows:
				transactions.objects.filter(UserID=row.UserID,TTime=row.CHECKTIME,Verify=5).delete()
		elif dataModel==userRoles:
			ids=[]
			for row in rows:
				if userRole.objects.filter(roleid__roleid=row.roleid).count()>0 or employee.objects.filter(Title=row.roleName).count()>0:
					ids.append(row.roleid)
				else:
					row.delete()
			if ids:
				names=userRoles.objects.filter(roleid__in=ids).values_list('roleName',flat=True)
				raise Exception(u'职务 %s 正在使用无法删除,其余职务已删除'%(u','.join(names)))
			#adminLog(time=datetime.datetime.now(),User=request.user, model=transactions.__name__, action=u'%s'%_("del"), object="del "+str(len(rows))).save()
#		for row in rows: 
#			try:
#				row.delete()
#			except:
#				raise Exception(_("%s has been used")%row)
#	return
#		return batchOp(request, dataModel, lambda d: d.delete())
	
#		for i in keys:  # 清理 表记录
#			del_by_fk(dataModel, i)
		#else:
		dataModel.objects.filter(pk__in=keys).delete()
	#if dataModel==InterLock:
	#	objs=InterLock.objects.filter(id__in=keys)
	#	for t in objs:
	#		sendInterLockToAcc([],[t.device_id])

def moveEmpToDev(devs, emp, cursor=None):#转移人员数据到新设备上
#	pin=emp.pin()
#	device=emp.SN
#	if devs:
#		if dev.SN==device.SN: #人员的登记设备保持不变
#			return None
#		appendDevCmdNew(devs, "DATA DEL_USER PIN=%s"%pin, cursor) #从原登记设备中删除
#		device=emp.SN.BackupDevice()
#		if device:
#			appendDevCmd(device, "DATA DEL_USER PIN=%s"%pin, cursor) #从备份设备中删除
#	emp.SN=dev #更改人员的登记设备
#	emp.save()
	appendEmpToDevNew(devs, emp, cursor) #把人员的信息传送到新设备中	


# #此函数已不合适，建议不要使用 2017.7.19
# def delEmpFromDev(superuser, emp, dev): #从机器中删除员工，如果没有指定机器的话，删除数据库中的员工同时在登记机和备份机中删除
# 	pin=emp.pin()
# 	if dev:
# 		return appendDevCmd(dev, "DATA DEL_USER PIN=%s"%pin)
# 	#if emp.SN:
# 	#	bk=emp.SN.BackupDevice()
# 	#	if bk:	
# 	#		appendDevCmd(bk, "DATA DEL_USER PIN=%s"%pin)
# 	#	appendDevCmd(emp.SN, "DATA DEL_USER PIN=%s"%pin)
# 	if superuser:
# 		emp.OffDuty=1
# 		emp.save()

def del_by_fk(dataModel, pk, app_label = "iclock"):
	table_fk = []	# 以外键方式 关联 主表 的 表
	datas = dataModel.objects.all()
	if datas:
		for row in dir(datas[0]):
			r = str(row)		
			if r.endswith('_set'):
				table_fk.append(r[:-4])	
#	print table_fk
	# 去掉要删除记录的表(不把他的外键值设置为None)
	if dict_del_table.has_key(str(dataModel)):		
		for row in dict_del_table[str(dataModel)]:
			if row in table_fk:
				table_fk.remove(row)
#	print table_fk
	# 查询 外键关联的表 的pk关联记录，并设置其关联外键值为 None		
	for row_table in table_fk:	# 表		
		to_field = dataModel._meta.pk.name
		model_fk = models.get_model(app_label, row_table)
		fields = model_fk._meta.fields
#		print "row_table",row_table,fields
		for row_field in fields:		# 字段						
			try:
				if "ForeignKey" in str(type(row_field)):	# 外键				
#					print to_field, row_field.name
					if to_field == row_field.name:
						rs = eval("model_fk.objects.all().filter(" + to_field + "=pk)")	# 关联的记录
						rs=len(rs)
						for row_rs in rs:				
							setattr(row_rs, to_field, None)
							row_rs.save()
			except:
				pass
def staAData(dObj, state):
	dObj.State=state
	dObj.save()

def staData(request, dataModel, state):
	batchOp(request, dataModel, lambda d: staAData(d, state))


def saveEmpComverify(request):
	isContainedChild=request.POST.get("isContainChild","0")
	deptIDs=request.POST.get('deptIDs',"")
	userIDs=request.POST.get('UserIDs',"")
	comverify=request.POST.get('comverify',"")
	ids=[]
	if len(userIDs)>0 and userIDs!='null':
		empids=userIDs.split(',')
	elif len(deptIDs)>0:
		deptidlist=deptIDs.split(',')
		deptids=deptidlist
		if isContainedChild=="1": #是否包含下级部门
			deptids=[]
			for d in deptidlist:#支持选择多部门
				if int(d) not in deptids :
					deptids+=getAllAuthChildDept(d,request)
		empids=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).exclude(DelTag=1).values_list('id', flat=True)
	for empid in empids:
		emp=employee.objects.get(id=empid)
		emp.VERIFICATIONMETHOD=comverify
		emp.OpStamp=datetime.datetime.now()
		emp.save()
	return getJSResponse({"ret":0,"message":u"%s"%_('Save Success')})

def saveFingerData(request,emp):
	#from mysite.iclock.models import BioData, employee
	if not emp:return
	fingers =request.POST.get("finnger10","").split(",")
	templates =request.POST.get("template10","").split(",")
	fptype =request.POST.get("fptype","")
	#==================save SSN photo 2017-8-25
	img64=request.POST.get('identity_img','')
	if img64:
		img64=img64.replace("\n","").replace("\r","").replace(" ","")
		try:
			imgData = base64.decodestring(img64)	
			pdir=settings.ADDITION_FILE_ROOT+'photo\\'+emp.PIN+'.jpg'
			if os.path.exists(pdir):
				os.remove(pdir)
			imgsave = open(pdir,'wb')
			imgsave.write(buffer(imgData))
			imgsave.close()
		except Exception,e:
			print e
	#===================save SSN photo end
	#save upload photo 2017-8-28 ------------------
	from mysite.iclock.datamisc import saveUploadImage
	f=request.FILES.get("up_img",None)
	if f:
		pin='%s_SN.%s'%(emp.PIN,f.name.split(".")[1])
		fname="%s%s/%s"%(settings.ADDITION_FILE_ROOT,'photo',pin)
		saveUploadImage(request, "up_img", fname)
		tbName=getStoredFileName("photo/thumbnail", None, pin)
		if os.path.exists(tbName):
			fullName=getStoredFileName("photo", None, pin)
			if os.path.exists(fullName):
				createThumbnail(fullName, tbName)
	#save upload photo end------------------
	fing_len = len(fingers)
	if fing_len > 1 or (fing_len==1 and fingers[0]):
		if fptype:
			fptype = fptype.split(",")
		else:
			fptype = ["1" for i in range(fing_len)]
		for i in range(fing_len):
			t = BioData.objects.filter(UserID=emp, bio_type = 1, bio_no=fingers[i], majorver='10')
			if not t:
				t = BioData()
			else:
				t = t[0]
			t.UserID = emp
			t.bio_type = 1	#指纹
			t.bio_no = fingers[i]
			t.bio_tmp = templates[i]
			t.duress = fptype[i]
			t.majorver = '10'
			t.UTime=datetime.datetime.now()
			t.save()
