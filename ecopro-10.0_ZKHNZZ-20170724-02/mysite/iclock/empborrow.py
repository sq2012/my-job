#coding=utf-8

from mysite.iclock.models import employee_borrow,employee,department,adminLog
import datetime
from mysite.utils import getJSResponse
from django.utils.translation import ugettext_lazy as _

def save_empborrow(request,keys):
    if request.method=="POST":
        userID = request.POST.get('userID','')
        toDept = request.POST.get('toDept','')
        fromTitle = request.POST.get('fromTitle','')
        toTitle = request.POST.get('toTitle','')
        fromDate = request.POST.get('fromDate','')
        toDate = request.POST.get('toDate','')
        reason = request.POST.get('reason','')
        remark = request.POST.get('remark','')
        OpTime = request.POST.get('OpTime','')
        try:
            if employee_borrow.objects.filter(userID=int(userID),state=0).count()>0:
                return getJSResponse({'ret':1,'message':u"%s"%_(u'保存失败，该人员已经在借调中，请先恢复借调')})
            fromDate = datetime.datetime.strptime(fromDate,'%Y-%m-%d %H:%M:%S')
            toDate = datetime.datetime.strptime(toDate,'%Y-%m-%d %H:%M:%S')
            OpTime = datetime.datetime.strptime(OpTime,'%Y-%m-%d %H:%M:%S')
            
            emp = employee.objByID(int(userID))
            if emp.DeptID_id==int(toDept):
                return getJSResponse({'ret':1,'message':u"%s"%_(u'保存失败，不允许借调到本单位')})
            employee_borrow(userID=int(userID),
                fromDept=emp.DeptID_id,
                toDept=int(toDept),
                fromTitle=fromTitle,
                toTitle=toTitle,
                fromDate=fromDate,
                toDate=toDate,
                reason=reason,
                remark=remark,
                OpTime=OpTime
            ).save()

            dept = department.objByID(int(toDept))
            emp.DeptID = dept
            emp.Title = toTitle
            emp.bstate = 0
            emp.save()
            adminLog(time = datetime.datetime.now(),User = request.user,model = employee_borrow._meta.verbose_name,action = _('Create'),object = request.META["REMOTE_ADDR"]).save(force_insert = True)
            return getJSResponse({'ret':0,'message':u"%s"%_(u'保存成功')})
        except Exception,e:
            print e
            return getJSResponse({'ret':0,'message':u"%s"%_(u'保存失败')})