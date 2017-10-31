#coding=utf-8
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.models import employee_borrow,attShifts,employee,department,DeptAdmin,AttException
import datetime
from django.db.models import Q,Count
from django.core.cache import cache
from django.conf import settings
from django.core.paginator import Paginator
from mysite.utils import getJSResponse,dumps

def colModel():
    return [
        {'name':'id','hidden':True},
        {'name':'PIN','label':unicode(_('PIN')),'sortable':False,'width':120,'frozen':True,'hidden':True},
        {'name':'workcode','label':unicode(_('NewPin')),'sortable':False,'width':90,'frozen':True},
        {'name':'EName','label':unicode(_('EName')),'sortable':False,'width':80},
        {'name':'DeptID','label':unicode(_(u'单位编号')),'sortable':False,'width':120},
        {'name':'DeptName','label':unicode(_(u'单位名称')),'sortable':False,'width':120},
        {'name':'toDeptID','label':unicode(_(u'借调单位编号')),'sortable':False,'width':120},
        {'name':'toDept','label':unicode(_(u'借调单位')),'sortable':False,'width':120},
        {'name':'absday','label':unicode(_(u'旷工天数')),'sortable':False,'width':60},
        {'name':'attention','label':unicode(_(u'提醒内容')),'sortable':False,'width':270}
    ]


def getdata(request):
    Result = cache.get('att_home_attention')
    if not Result:
        from mysite.iclock.datas import GetLeaveClasses
        lclass = GetLeaveClasses(1)
        l_dict={}
        for l in lclass:
            l_dict[l['LeaveName']] = l['LeaveID']

        if not request.user.is_superuser and not request.user.is_alldept:
            depts = DeptAdmin.objects.filter(user=request.user)
        else:
            depts = department.objects.filter(DelTag=0)
        emps = employee.objects.filter(DelTag=0,DeptID__in=depts)
        empids = emps.values_list('id',flat=True)
        emp_dict={}
        for emp in emps:
            emp_dict[emp.id] = emp

        eb_dict = {}
        ebs = employee_borrow.objects.filter(state=0,userID__in=empids)
        for eb in ebs:
            eb_dict[eb.userID] = eb

        et = datetime.datetime.now()
        st = datetime.datetime(et.year,1,1,0,0,0)
        et = datetime.datetime(et.year,et.month,et.day,0,0,0)
        atts = attShifts.objects.filter(AttDate__gte=st,AttDate__lte=et,Absent=1,UserID_id__in=emps).values('UserID','Absent').annotate(abstime=Count('Absent')).values('UserID','abstime').order_by('UserID__DeptID_id','abstime')
        exps = AttException.objects.filter(AttDate__gte=st,AttDate__lte=et,UserID_id__in=emps,InScopeTime__gt=0).values('UserID','ExceptionID').annotate(time=Count('ExceptionID')).filter(ExceptionID__in=[l_dict[_(u'病假')],l_dict[_(u'事假')]]).order_by('UserID')
        datas = []
        index = {}
        Result = {}
        i = 0
        try:
            if request.method=='GET':
                offset = int(request.GET.get('page', 1))
            else:
                offset = int(request.POST.get('page', 1))
        except:
            offset=1
        if request.method=='GET':
            limit= int(request.GET.get('rows', settings.PAGE_LIMIT))
        else:
            limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
        paginator = Paginator(atts, limit)
        item_count = paginator.count
        try:
            pgList = paginator.page(offset)
        except ValueError:
            offset=1
            pgList = paginator.page(1)
        page_count=paginator.num_pages
        Result['item_count']=item_count
        Result['page']=offset
        Result['limit']=limit
        Result['from']=(offset-1)*limit+1
        Result['page_count']=page_count
        
        for att in pgList.object_list:
            data={}
            data['id'] = att['UserID']
            data['PIN'] = emp_dict[att['UserID']].PIN
            data['workcode'] = emp_dict[att['UserID']].Workcode
            data['EName'] = emp_dict[att['UserID']].EName
            data['absday'] = att['abstime']
            data['attention'] = ''
            if eb_dict.has_key(att['UserID']):
                tmp_dept = department.objByID(eb_dict[att['UserID']].toDept)
                data['toDeptID'] = tmp_dept.DeptNumber
                data['toDept'] = tmp_dept.DeptName
                tmp_dept = department.objByID(eb_dict[att['UserID']].fromDept)
            else:
                tmp_dept = department.objByID(emp_dict[att['UserID']].DeptID_id)
            data['DeptID'] = tmp_dept.DeptNumber
            data['DeptName'] = tmp_dept.DeptName
            datas.append(data)
            index[att['UserID']] = i
            i += 1

        for exp in exps:
            if exp['ExceptionID'] == l_dict[_(u'病假')]:
                count = exp['time']
                from mysite.iclock.templatetags.iclock_tags import getWorkAge
                workage = getWorkAge(exp['UserID'],request).replace('年','')
                if workage:
                    workage = int(workage)
                else:
                    workage = 0
                if count>10 and workage<=10 and count<=60:
                    datas[index[exp['UserID']]]['attention'] += u'病假超10天需提供诊断证明  '
                elif workage<=10 and count>60:
                    datas[index[exp['UserID']]]['attention'] += u'病假超60天扣发工资  '
                elif workage>10 and count>180:
                    datas[index[exp['UserID']]]['attention'] += u'病假超60天扣发工资  '
            if exp['ExceptionID'] == l_dict[_(u'事假')]:
                count = exp['time']
                if count>20 and count<=30:
                    datas[index[exp['UserID']]]['attention'] += u'事假超20天扣发工资  '
                elif count>30:
                    datas[index[exp['UserID']]]['attention'] += u'事假超30天停发工资  '
        Result['datas'] = datas
        cache.set('att_home_attention',Result,8*3600)
    rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
    return getJSResponse(rs)