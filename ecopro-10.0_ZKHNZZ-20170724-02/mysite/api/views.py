#coding=utf-8
from mysite.iclock.models import *
from django.utils.encoding import smart_str
from mysite.utils import *
from mysite.iclock.iutils import *
from mysite.auth_code import *
from mysite.base.models import *
from mysite.core.tools import *
import datetime


def IsValidRequest(request):
        try:
                token=request.GET.get('token','')
                if not token:
                        print "000"
                        return False
                params=GetParamValue('api_sycndata',{},'tasks')
                if not params:
                        return False
                params=loads(params)
                token=token.encode("gb18030")
                token=auth_code(token).split('\t')
                nt=OldEncodeTime(datetime.datetime.now())
                if nt-int(token[2])>36000:
                        return False
                if not (params['user']==token[0] and params['pass']==token[1]):
                        print "2222222222"
                        return False
                return True
        except Exception,e:
                print "--------",e
        

def auth_login(request):
	username=''
	password=''
	ret=0
	msg=''
	params=GetParamValue('api_sycndata','{}','tasks')
	nt=datetime.datetime.now()
	params=loads(params)
	if not params:
		ret=2
		msg=u'没有设置数据对接功能'
	else:
		if params['is_']==0:
			ret=4
			msg=u'没有设置启用数据对接功能'
		else:
			st=params['st'].split('-')
			snt=nt.strftime('%H:%M')
			if snt>=st[0] and snt<=st[1]:
				pass
			else:
				ret=5
				msg=u'未在规定时间'
	if ret==0:                
		if request.method=='GET':
			username=request.GET.get('username','')
			password=request.GET.get('password','')
			
		else:
			rawData=request.body
			users=string.split(rawData,"\n")
			if users:
				userDict=lineToDict(users[0])
				username=userDict['username']
				password=userDict['password']		
		if not username or not password:
			ret=1
			msg=u'账户或密码不能为空'
	
	
	if ret==0:
		if username==params['user'] and password==params['pass']:
			stamp=OldEncodeTime(nt)
			msg=auth_code('%s\t%s\t%s'%(username,password,stamp),'ENCODE')
		else:
			ret=3
			msg=u'账户或密码不正确'
	result={'ret':ret,'msg':msg}
	return getJSResponse(result)


def updateDeptData(rawData,tableName):
	"""客户端采用gbk编码"""
	i_insert=0
	i_update=0
	ret=0        
	for line in string.split(rawData,"\n"):
		#line=unicode(line.decode("utf-8"))
		dDict=lineToDict(line)
		if dDict!={}:
			supdt=department.objByNumber(dDict['parent'])
			dt=department.objByNumber(dDict['deptnumber'])
			if supdt:
				dDict['supdeptid']=supdt.DeptID
			elif dDict['parent']=='0':
				dDict['supdeptid']=0
			elif not dDict['parent']:
				msg=u"部门编号为 %s 的上级部门不能为空" %(dDict['deptnumber'])
				ret=1
				return (ret,msg)
			else:
				msg=u"部门编号为 %s 的上级部门不存在" %(dDict['deptnumber'])
				ret=1
				return (ret,msg)
			del dDict['parent']
			if dt:
				dDict['whereDeptID']=dt.DeptID
				sql,params=getSQL_update_new('departments',dDict)
				if customSqlEx(sql,params):
					i_update+=1
			else:
				sql,params=getSQL_insert_new('departments',dDict)
				if customSqlEx(sql,params):
					i_insert+=1
	UpdateDeptCache()
	msg=u"新增部门%s 个, 更新部门%s个！" %(i_insert,i_update)
	return (ret,msg)

 
def updateUserData(rawData,tableName):
	i_insert=0
	i_update=0
	ret=0
	for line in string.split(rawData,"\n"):
		#line=unicode(line.decode("utf-8"))
		dDict=lineToDict(line)
		if dDict!={}:
			if not dDict.has_key('pin'):
				msg=u"工号为不能为空"
				ret=1
				return (ret,msg)                               
			if dDict.has_key('deptnumber'):
				dept=department.objByNumber(dDict['deptnumber'])
			else:
				dept=None
			if dept:
				dDict['defaultdeptid']=dept.DeptID
			elif dDict['deptnumber']=='0':
				dDict['defaultdeptid']=0
			elif not dDict['deptnumber']:
				msg=u"工号为 %s 的上级部门不能为空" %(dDict['pin'])
				ret=1
				return (ret,msg) 
			else:
				msg=u"工号为 %s 的部门不存在" %(dDict['pin'])
				ret=1
				return (ret,msg)
			del dDict['deptnumber']
			try:
				emp=employee.objects.get(PIN=dDict['pin'])
			except:
				emp=None
			if not dDict.has_key('offduty'):
				dDict['offduty']=0
			if not dDict.has_key('deltag'):
				dDict['deltag']=0
			dDict['offduty']=int(dDict['offduty'])
			dDict['deltag']=int(dDict['deltag'])
			if emp:
				IsUpdateStamp=False
				#if dDict.has_key('name') and dDict['name']!=emp.EName:
				#	IsUpdateStamp=True
				if dDict.has_key('defaultdeptid') and dDict['defaultdeptid']!=emp.DeptID_id:
					IsUpdateStamp=True
				elif dDict.has_key('deltag') and dDict['deltag']!=emp.DelTag:
					IsUpdateStamp=True
				elif dDict.has_key('offduty') and dDict['offduty']!=emp.OffDuty:
					IsUpdateStamp=True
				elif dDict.has_key('card') and dDict['card']!=emp.Card:
					IsUpdateStamp=True
				
				
				
				dDict['wherebadgenumber']=dDict['pin']
				if IsUpdateStamp:
					dDict['OpStamp']=datetime.datetime.now()
				del dDict['pin']
				sql,params=getSQL_update_new('userinfo',dDict)
				if customSqlEx(sql,params):
					i_update+=1
					cache.delete("%s_iclock_emp_%s"%(settings.UNIT,emp.id))					
					cache.delete("%s_iclock_emp_PIN_%s"%(settings.UNIT,emp.PIN))
			else:
				dDict['badgenumber']=dDict['pin']
				del dDict['pin']
				dDict['OpStamp']=datetime.datetime.now()
				dDict['ATT']=1
				dDict['OverTime']=1
				dDict['Holiday']=1
				dDict['INLATE']=0
				dDict['OutEarly']=0
				sql,params=getSQL_insert_new('userinfo',dDict)
				if customSqlEx(sql,params):
					i_insert+=1
	msg=u"新增人员%s 个, 更新人员%s个！" %(i_insert,i_update)
	return (ret,msg)


def updateCheckinoutData(rawData,tableName):
        ret=1
        msg=u"暂不开放此功能！"
        return (ret,msg)
        
 
def updateDeviceData(rawData,tableName):
        i_insert=0
        i_update=0
        ret=0
        for line in string.split(rawData,"\n"):
                dDict=lineToDict(line)
                if dDict!={}:
                        if not dDict.has_key('sn'):
                                msg=u"SN不能为空"
                                ret=1
                                return (ret,msg)                           
                        if not dDict.has_key('deptnumber'):
                                msg=u"部门编号不能为空"
                                ret=1
                                return (ret,msg)
                        else:
                                dept=department.objByNumber(dDict['deptnumber'])
                                dDict['DeptID']=dept.DeptID
                        if not dept:
                                msg=u"SN为 %s 的部门编号不存在" %(dDict['sn'])
                                ret=1
                                return (ret,msg)                     
                        devs=iclock.objects.filter(SN=dDict['sn'])
                        if devs:
                                dev = devs[0]
                        else:
                                dev = None
                                
                        del dDict['deptnumber']        
                        if dev:
                                dDict['whereSN']=dev.SN
                                sql,params=getSQL_update_new('iclock',dDict)
                                if customSqlEx(sql,params):
                                        i_update+=1
                        else:
                                dDict['TransInterval']=1
                                dDict['AlgVer']='10'
                                dDict['TZAdj']=8
                                dDict['State']=1
                                dDict['UpdateDB']='1111100000'
                                dDict['AccFun']=0
                                dDict['DelTag']=0
                                dDict['LogStamp']=0
                                dDict['OpLogStamp']=0
                                dDict['PhotoStamp']=0
                                dDict['Authentication']=1
                                dDict['ProductType']=9
                                dDict['isUSERPIC']=0
                                dDict['isFptemp']=1
                                dDict['isFace']=0
                                dDict['CreateTime']=datetime.datetime.now()
                                sql,params=getSQL_insert_new('iclock',dDict)
                                if customSqlEx(sql,params):
                                        i_insert+=1
                        if dDict['sn'] and dept:
                                iclockDeptDict={}                
                                iclockDeptDict['SN_id']=dDict['sn']
                                iclockDeptDict['dept_id']=dept.DeptID
                                iclockDeptDict['iscascadecheck']=0
                                sql,params=getSQL_insert_new('iclock_iclockdept',iclockDeptDict)
                                try:
                                        customSqlEx(sql,params)
                                except Exception,e:
                                        pass
        msg=u"新增设备%s 台, 更新设备%s台！" %(i_insert,i_update)
        return (ret,msg)
#查询数据
def getModelsData(request,table):
	ret=0
	msg=''
	items=[]
	data={}
	if table=='checkinout':
		startdate=request.GET.get('startdate')
		enddate=request.GET.get('enddate')
		sn=request.GET.get('sn')
		pin=request.GET.get('pin')
		
		startdate=datetime.datetime.strptime(startdate,"%Y%m%d")
		enddate=datetime.datetime.strptime(enddate,"%Y%m%d")      
		data={}
		items=[]
		trans=transactions.objects.filter(TTime__gte=startdate,TTime__lt=enddate).order_by('TTime')
		if sn:
			trans=trans.filter(SN=sn)
		if pin:
			trans=trans.filter(UserID__PIN=pin)
		for t in trans:
			d={}
			#emp=employee.objByID(t.UserID)
			d['pin']=t.UserID.PIN
			d['checktime']=t.TTime.strftime("%Y-%m-%d %H:%M:%S")
			if t.SN:
				d['sn']=t.SN.SN
			else:
				d['sn']=''
			d['verify']=t.Verify
			d['reserved']=t.Reserved
			items.append(d.copy())
		data['count']=len(items)
		data['items']=items
		msg=u"获取原始记录 %s 条。" %(len(items))
	elif table=='records':
		startdate=request.GET.get('startdate')
		enddate=request.GET.get('enddate')
		sn=request.GET.get('sn')
		pin=request.GET.get('pin')

		startdate=datetime.datetime.strptime(startdate,"%Y%m%d")
		enddate=datetime.datetime.strptime(enddate,"%Y%m%d")
		data={}
		items=[]
		trans=records.objects.filter(TTime__gte=startdate,TTime__lt=enddate).order_by('TTime')
		if sn:
			trans=trans.filter(SN=sn)
		if pin:
			trans=trans.filter(pin=pin)			
		for t in trans:
			d={}
			#emp=employee.objByID(t.UserID)
			d['pin']=t.pin
			d['TTime']=t.TTime.strftime("%Y-%m-%d %H:%M:%S")
			if t.SN:
				d['sn']=t.SN.SN
			else:
				d['sn']=''
			d['verify']=t.verify
			d['inorout']=t.inorout
			d['event_no']=t.event_no
			d['card_no']=t.card_no
			items.append(d.copy())
		data['count']=len(items)
		data['items']=items
		ret=0
		msg=u"获取原始门禁记录 %s 条。" %(len(items))
	elif  table=='department':
		deptnumber=request.GET.get('deptnumber')
		iscontainchild=request.GET.get('iscontainchild')
		deptids=[]
		if not deptnumber:
			deptids=department.objects.all().values_list('DeptID', flat=True).order_by('DeptNumber',"DeptID")
		else:
			dept=department.objByNumber(deptnumber)
			if dept:
				if iscontainchild == 1:
					depts=dept.AllChildren()
					for d in depts:
						deptids.append(d.DeptID)
				else:
					deptids.append(dept.DeptID)
			else:
				ret=1
				msg=u"部门编号为 %s 的部门不存在" %(deptnumber)
				return (ret,msg,data)
		for id in deptids:
			dept=department.objByID(id)
			d={}
			d['deptnumber']=dept.DeptNumber
			d['deptname']=dept.DeptName
			if dept.Parent():
				d['parent']=dept.Parent().DeptNumber
			else:
				d['parent']=''
			items.append(d.copy())
		data['count']=len(items)
		data['items']=items
		ret=0
		msg=u"获取部门 %s 个。" %(len(items))
			
	elif table=='userinfo':
		deptnumber=request.GET.get('deptnumber')
		pin=request.GET.get('pin')
		userids=[]
		if pin:
			emp = employee.objByPIN(pin)
			if emp:
				userids.append(emp.id)
			else:
				ret=1
				msg=u"工号为 %s 的人员不存在" %(deptnumber)
				return (ret,msg,data)                           
		else:
			if not deptnumber:
				userids = employee.objects.all().values_list('id', flat=True).order_by('PIN')
			else:
				dept = department.objByNumber(deptnumber)
				
				if dept:
					userids = employee.objects.filter(DeptID=dept).values_list('id',flat=True)
				else:
					ret=1
					msg=u"部门编号为 %s 的部门不存在" %(deptnumber)
					return (ret,msg,data)
		for id in userids:
			user=employee.objByID(id)
			d={}
			d['pin']=user.PIN
			d['name']=user.EName
			d['pager']=user.Mobile
			d['sysPass']=user.Password
			d['deptnumber']=user.DeptID.DeptNumber
			items.append(d.copy())
		data['count']=len(items)
		data['items']=items
		ret=0
		msg=u"获取人员 %s 个。" %(len(items))
	elif table=='device':
		deptnumber=request.GET.get('deptnumber')
		sn=request.GET.get('sn')
		snlist=[]
		if sn:
			device = iclock.objects.filter(SN=sn).exclude(DelTag=1)
			if device:
				snlist.append(device[0].SN)
			else:
				ret=1
				msg=u"设备序列号为 %s 的设备不存在" %(sn)
				return (ret,msg,data)                           
		else:
			snlist=iclock.objects.all().exclude(DelTag=1).values_list('SN', flat=True).order_by('SN')
		for s in snlist:
			device = iclock.objects.filter(SN=s)[0]
			d={}
			d['sn']=device.SN
			d['ipddress']=device.IPAddress
			d['alias']=device.Alias
			#d['deptnumber']=device.DeptID.DeptNumber
			d['devicename']=device.DeviceName
			items.append(d.copy())
		data['count']=len(items)
		data['items']=items
		ret=0
		msg=u"获取设备 %s 个。" %(len(items))
	else:
		ret=2
		msg=u'table不正确'                
	return (ret,msg,data)


#删除数据
def delData(request,table):
	i_delete=0
	ret=0
	msg=''
	if table=='device':
		sn=request.GET.get('sn')
		if not sn:
			devs=iclock.objects.exclude(DelTag=1)
			msg=u"删除设备 %s 个！" %(len(devs))
			devs.update(DelTag=1)
		else:
			devs=iclock.objects.filter(SN=sn)
			if not devs:
				msg=u"序列号为 %s 的设备不存在" %(sn)
				ret=1
				return (ret,msg)
			else:
				dev=devs[0]
				dev.DelTag=1
				dev.save()
				msg=u"序列号为 %s 的设备已删除！" %(sn)

	elif table=='userinfo':
		pin=request.GET.get('pin')
		if not pin:
			emps=employee.objects.exclude(DelTag=1)
			msg=u"删除人员 %s 个！" %(len(emps))
			emps.update(DelTag=1)
		else:
			#emp=employee.objByPIN(pin)
			emp=employee.objects.filter(PIN=pin).exclude(DelTag=1)
			if not emp:
				msg=u"工号为 %s 的人员不存在" %(pin)
				ret=1
				return (ret,msg)
			else:
				#emp.DelTag=1
				#emp.save()
				emp.update(DelTag=1)
				msg=u"工号为 %s 的人员已删除！" %(pin)
		
	elif table=='department':
		deptnumber=request.GET.get('deptnumber')
		if not deptnumber:
			depts=department.objects.exclude(DelTag=1)
			msg=u"删除删除部门 %s 个！" %(len(depts))
			depts.update(DelTag=1)
		else:
			#dept=department.objByNumber(deptnumber)
			dept=department.objects.filter(DeptNumber=deptnumber).exclude(DelTag=1)
			if not dept:
				msg=u"部门编号为 %s 的部门不存在" %(deptnumber)
				ret=1
				return (ret,msg)
			else:
				#dept.DelTag=1
				#dept.save()
				dept.update(DelTag=1)
				msg=u"编号为 %s 的部门已删除！" %(deptnumber)
		UpdateDeptCache()
	else:
		ret=2
		msg=u'table不正确' 
		
	return (ret,msg)
		
def update_data(request):
        if not IsValidRequest(request):
                ret=1
                msg=u'token不正确'
                result={'ret':ret,'msg':msg}
                return getJSResponse(result)
        ret=0
        msg=''
        if request.method=='POST':
                table=request.GET.get('table')
                if not table:
                        ret=2
                        msg=u'table不正确'
                        result={'ret':ret,'msg':msg}
                        return getJSResponse(result)
                rawData=request.body
                if table=='department':
                        ret,msg=updateDeptData(rawData,table)
                elif table=='userinfo':
                        ret,msg=updateUserData(rawData,table)
                elif table=='checkinout':
                        ret,msg=updateCheckinoutData(rawData,table) 
                elif table=='device':
                        ret,msg=updateDeviceData(rawData,table)
                else:
                        ret=2
                        msg=u'table不正确'                        
        if request.method=='GET':
                table=request.GET.get('table')
                if not table:
                        ret=2
                        msg=u'table不正确'
                        result={'ret':ret,'msg':msg}
                        return getJSResponse(result)
                if table=='checkinout':
                        ret,msg,data=getCheckinoutData(request)
                        result={'ret':ret,'msg':msg,'data':data}
                        return getJSResponse(result)                                                
                else:
                        ret=2
                        msg=u'table不正确' 
        result={'ret':ret,'msg':msg}
        return getJSResponse(result)
                        
                        
                
def query_data(request):
        if not IsValidRequest(request):
                ret=1
                msg=u'token不正确'
                result={'ret':ret,'msg':msg}
                return getJSResponse(result)
        ret=0
        msg=''
        data={}
        if request.method=='POST':
                table=request.GET.get('table')
                if not table:
                        ret=2
                        msg=u'table不正确'
                        result={'ret':ret,'msg':msg}
                        return getJSResponse(result)

        if request.method=='GET':
                table=request.GET.get('table')
                if not table:
                        ret=2
                        msg=u'table不正确'
                        result={'ret':ret,'msg':msg}
                        return getJSResponse(result)
                else:
                        ret,msg,data=getModelsData(request,table)
                        result={'ret':ret,'msg':msg,'data':data}
                        return getJSResponse(result)                                                

        result={'ret':ret,'msg':msg}
        return getJSResponse(result)

                
def delete_data(request):
        if not IsValidRequest(request):
                ret=1
                msg=u'token不正确'
                result={'ret':ret,'msg':msg}
                return getJSResponse(result)
        ret=0
        msg=''
        if request.method=='POST':
                table=request.GET.get('table')
                if not table:
                        ret=2
                        msg=u'table不正确'
                        result={'ret':ret,'msg':msg}
                        return getJSResponse(result)

        if request.method=='GET':
                table=request.GET.get('table')
                if not table:
                        ret=2
                        msg=u'table不正确'
                        result={'ret':ret,'msg':msg}
                        return getJSResponse(result)
                else:
                        ret,msg=delData(request,table)

        result={'ret':ret,'msg':msg}
        return getJSResponse(result)

def weiang_data(request):
	#if not IsValidRequest(request):
	#        ret=1
	#        msg=u'token不正确'
	#        result={'ret':ret,'msg':msg}
	#        return getJSResponse(result)
	ret=0
	msg=u'你好'
	rawData=request.body
	s=unicode(rawData.decode("gb18030"))
	print "22222",s,type(s)
	#if request.method=='POST':
	#	table=request.GET.get('table')
	#	if not table:
	#		ret=2
	#		msg=u'table不正确'
	#		result={'ret':ret,'msg':msg}
	#		return getJSResponse(result)
	#	rawData=request.body
	result={'ret':ret,'msg':msg}
	response=head_response()
	msg=dumps2(result)
	#print "333333",res,type(msg)
	msg=msg.encode("gb18030")
	#msg=msg.encode("gb18030")
	print "44444",msg,type(msg)
	print "55555",msg,type(msg)
	response.write(msg)
	return response

