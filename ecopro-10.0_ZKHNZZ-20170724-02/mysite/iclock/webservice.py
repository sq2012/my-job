#coding=utf-8
from mysite.iclock.models import *
from django.utils.encoding import smart_str
from mysite.utils import *
from mysite.iclock.iutils import *

def IsValidRequest(request):
	issync=int(GetParamValue('opt_datasync_issync','0'))
	if issync==0: return False
	
	authtype=int(GetParamValue('opt_dataissync_authtype','0'))
	if authtype==1:
		print request
	if authtype==2:
		token=request.GET.get('token')
		if not token:return False
		token_=GetParamValue('opt_dataissync_token','')
		if token<>token_:return False
	return True
	
	
def index(request, function):
	if not IsValidRequest(request):
		return getJSResponse("")
		
	if request.method=='GET':
		res=ProcessGet(request,function)
	else:
		res=ProcessPost(request,function)
	fmt=request.GET.get('format','json')
	if fmt=='json':
		return getJSResponse(res)
	elif fmt=='text':
		return getJSResponse(res,mtype='text/plain')
	else:
		return getJSResponse("")
	
		
def ProcessGet(request,function):
	result={}
	fmt=request.GET.get('format','json')
	if function=='devices':
		sns=iclock.objects.all().exclude(DelTag=1)
		if fmt=='json':
			l=[]
			for k in sns:
				l.append(k.SN)
			result={'ret':len(l),'data':l}
		elif fmt=='text':
			s='\n'.join('%s'%k.SN for k in sns)
			result=s
	elif function=='device':
		sn=request.GET.get('sn','')
		dev=getDevice(sn)
		if dev:
			d={'sn':dev.SN,'state':dev.State,'lastactivity':'%s'%dev.LastActivity,'transinterval':dev.TransInterval,
			   'realtime':1,'logstamp':dev.LogStamp,'oplogstamp':dev.OpLogStamp,
			   'isface':dev.isFace,'isfingerprint':dev.isFptemp,'ip':dev.IPAddress}

			if fmt=='json':
				result=d
			elif fmt=='text':
				s='\n'.join("%s=%s"%(k,v) for k,v in d.items())
				result=s
	elif function=='deldevice':
		sn=request.GET.get('sn','')
		if sn:
			devs=iclock.objects.filter(SN=sn)
			for dev in devs:
				dev.delete()
			if fmt=='json':
				result={'error_code':0}
			elif fmt=='text':
				result='message='+sn+' deleted'
	elif function=='logs':
		st=request.GET.get('starttime','')
		et=request.GET.get('endtime','')
		sn=request.GET.get('sn','')
		pin=request.GET.get('pin','')
		if st and et:
			st=datetime.datetime.strptime(st,'%Y%m%d%H%M%S')
			et=datetime.datetime.strptime(et,'%Y%m%d%H%M%S')
			logs=transactions.objects.filter(TTime__gte=st,TTime__lte=et)
			if sn:
				logs=logs.filter(SN=sn)
			if pin:
				logs=logs.filter(UserID__PIN=pin)
		l=[]
		s=""
		if logs:
			
			for t in logs:
				d={}
				d['pin']=t.employee().PIN
				d['name']=u"%s"%t.employee().EName or ""
				d['checktime']=t.TTime.strftime('%Y-%m-%d %H:%M:%S')
				d['card']=u"%s"%t.employee().Card or ""
				d['sn']=t.SN_id or ""
				if fmt=="json":
					l.append(d.copy())
				elif fmt=="text":
					s+=','.join("%s=%s"%(k,v) for k,v in d.items())+'\n'
		if fmt=="json":
			result=l
		elif fmt=="text":
			result=s
	elif function=="params":
		d={'approval':GetParamValue('opt_basic_approval',0),'new_record':GetParamValue('opt_basic_new_record',0),
		   'self_login':GetParamValue('opt_basic_self_login',0),'device_auto':GetParamValue('opt_basic_dev_auto',0)}
		d['records']=transactions.objects.all().count()
		d['devices']=iclock.objects.all().count()
		d['departments']=department.objects.all().count()
		d['employees']=employee.objects.all().count()
		if fmt=="json":
			result=d
		elif fmt=="text":
			s='\n'.join("%s=%s"%(k,v) for k,v in d.items())
			result=s
			
	return result

def ProcessPost(request,function):
	fmt=request.GET.get('format','json')
	result={}
#	print request
	if function=='departments':
		raw_data=request.body
		
		#raw_data=raw_data.decode("gb2312")
		try:
			if fmt=='json':
				#print raw_data
				l=loads(raw_data)
				for t in l:
					d=department.objByNumber(t['deptid'])
					if d:
						d.DeptNumber=t['deptid'];d.DeptName=t['deptname'];d.parent=t['parent'];d.save()
					else:
						department(DeptNumber=t['deptid'],DeptName=t['deptname'],parent=t['parent']).save()
					if t['flag']==2:
						pass
				result={'ret':len(l),'message':'successed'}
			elif fmt=='text':
				c=0
				for line in string.split(raw_data,"\n"):
					t={}
					c+=1
					items=line.split(',')
#					print items
					for item in items:
						index=item.find("=")
						if index>0: t[item[:index]]=item[index+1:]
					d=department.objByNumber(t['deptid'])
					if d:
						d.DeptNumber=t['deptid'];d.DeptName=t['deptname'];d.parent=t['parent'];
						d.save()
					else:
						department(DeptNumber=t['deptid'],DeptName=t['deptname'],parent=t['parent']).save()
				result="message=successed:%s"%c
		except Exception,e:
			print "==============",e
			return "%s"%e
		return result
	if function=='employees':
		raw_data=request.body
		
		#raw_data=raw_data.decode("gb2312")
		print raw_data
		try:
			if fmt=='json':
				l=loads(raw_data)
				for t in l:
					t['pin']=str(t['pin'])
					try:
						u=employee.objByPIN(t['pin'])
					except:
						u=None
					d=department.objByNumber(t['deptid'])
					if u:
						u.DeptID=d;u.EName=t['name'];u.Card=t['card'];u.SSN=t['sn']
						if t['gender']==0:
							u.Gender='M'
						if t['gender']==1:
							u.Gender='F'
							
						u.save()
					else:
						employee(PIN=t['pin'],DeptID=d,EName=t['name'],Card=t['card'],SSN=t['sn']).save()
					if t['flag']==2:
						pass
				result={'ret':len(l),'message':'successed'}
			elif fmt=='text':
				c=0
				for line in string.split(raw_data,"\n"):
					t={}
					c+=1
					items=line.split(',')
#					print items
					for item in items:
						index=item.find("=")
						if index>0: t[item[:index]]=item[index+1:]
					t['pin']=str(t['pin'])
					try:
						u=employee.objByPIN(t['pin'])
					except:
						u=None
					d=department.objByNumber(t['deptid'])
					if u:
						u.DeptID=d;u.EName=t['name'];u.Card=t['card'];u.SSN=t['sn']
						if t['gender']==0:
							u.Gender='M'
						if t['gender']==1:
							u.Gender='F'
							
						u.save()
					else:
						employee(PIN=t['pin'],DeptID=d,EName=t['name'],Card=t['card'],SSN=t['sn']).save()
					if t['flag']==2:
						pass
				result="message=successed:%s"%c
		except Exception,e:
			print "==============",e
			return "%s"%e
		return result
				