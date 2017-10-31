#coding=utf-8
from mysite.iclock.models import *
from django.utils.encoding import smart_str
from mysite.utils import *
#from django.utils import simplejson
from mysite.iclock.iutils import *
def getMiniData(request, ModelName):
	# dialog 获取数据
	miniData=request.GET.get("key", "")
	toResponse = "'"
	pk, pk_note, pk_note2, objs = (None, None, None, None)
	if miniData == "UserID":
		pk, pk_note, pk_note2 = ("id", "PIN", "EName")
		objs = employee.objects.all()
		objs=objs.order_by("PIN").values("id", "PIN", "EName")
	if miniData in ["SN","Device"]:
		if not request.user.is_superuser:
			depts=userDeptList(request.user)
			sns=IclockDept.objects.filter(dept__in=depts).values_list('SN')
			snlist=[]
			for sn in sns:
				snlist.append(sn[0])
			objs = iclock.objects.filter(SN__in=snlist).exclude(DelTag=1)
		else:
			objs = iclock.objects.filter(Q(DelTag__isnull=True)|Q(DelTag=0))
		pk, pk_note = ("SN", "Alias")
		objs=objs.order_by("Alias").values("SN", "Alias")
	elif miniData in ["DeptID", "depart"]:
		pk, pk_note = ("DeptNumber", "DeptName")
		if (not request.user.is_superuser) and (not request.user.is_alldept ):			
			dept_list=userDeptList(request.user)
#			dd=[]
#			for i in dept_list:
#				dd.append(int(i.DeptID))
			objs=department.objects.filter(DeptID__in=dept_list).values("DeptNumber", "DeptName")
		else:
			objs = department.objects.all().values("DeptNumber", "DeptName")
	elif miniData in ["User", "Administrator"]:
		pk, pk_note = ("id", "username")
		objs = User.objects.all().values("id", "username")
	res={}
	if len(objs)>0:
		for row in objs:
			res[row[pk]]=("%s"%row[pk_note])+(pk_note2 and
                (" %s"%row[pk_note2]) or "")
#		print res
	toResponse = dumps1(res)
	return getJSResponse(toResponse)
