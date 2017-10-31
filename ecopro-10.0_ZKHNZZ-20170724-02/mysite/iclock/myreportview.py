#coding=utf-8
from mysite.iclock.models import department,employee,attShifts,AttException,employee_borrow
from django.db.models import Q,Count,Sum
from django.core.paginator import Paginator
from django.conf import settings
import datetime
from mysite.iclock.iutils import userDeptList,getAllAuthChildDept
from mysite.iclock.datas import GetLeaveClasses
from mysite.iclock.templatetags.iclock_tags import getWorkAge

def getcalcallreportcol():
    return [
        {'name':'id','hidden':True},
        {'name':'dept','label':unicode(u'单位'),'width':140,'sortable':False},
        {'name':'rel','label':unicode(u'实有人数'),'sortable':False,'width':60},
        {'name':'onposition','label':unicode(u'在岗人数'),'sortable':False,'width':60},
        {'name':'offposition','label':unicode(u'经组织批准离岗人数'),'sortable':False,'width':120},
        {'name':'incount','label':unicode(u'借调人数'),'sortable':False,'width':60},
        {'name':'outcount','label':unicode(u'借调出人数'),'sortable':False,'width':80},
        {'name':'total','label':unicode(u'小计'),'sortable':False,'width':60},
        {'name':'btime','label':unicode(u'病假人次'),'sortable':False,'width':60},
        {'name':'stime','label':unicode(u'事假人次'),'sortable':False,'width':60},
        {'name':'abstime','label':unicode(u'旷工人次'),'sortable':False,'width':60},
        {'name':'otime','label':unicode(u'其他'),'sortable':False,'width':60},
        #{'name':'remark','label':unicode(u'备注'),'sortable':False,'width':200}
    ]

def getcalcallreportheader():
    return [
            {'startColumnName': 'total', 'numberOfColumns': 5, 'titleText': '<em>病事假等情况</em>'}
    ]

def calcallreport(request,isContainedChild,deptIDs,st,et):
    lclass = GetLeaveClasses(1)
    l_dict={}
    bl_dict={}
    for l in lclass:
        l_dict[l['LeaveName']] = l['LeaveID']
        bl_dict[l['LeaveID']] = l['LeaveName']

    if len(deptIDs)>0:
        deptidlist=deptIDs.split(',')
        deptids=[]
        if isContainedChild=="1": #是否包含下级部门
            for d in deptidlist:#支持选择多部门
                if int(d) not in deptids :
                    deptids+=getAllAuthChildDept(d,request)
        else:
            deptids = [int(d) for d in deptidlist]
    else:
        deptids=userDeptList(request.user)
        deptids.sort()
    Result = paging(request,deptids)
    deptids = Result['datas']
    deptids.sort()
    empstate = employee.objects.filter(DelTag=0,DeptID__in=deptids).values('DeptID_id','OffPosition').annotate(empCount=Count('OffPosition')).order_by('DeptID_id','OffPosition')
    fdata = employee_borrow.objects.filter(state=0,fromDate__range=[st,et]).filter(Q(fromDept__in=deptids)).values('fromDept').annotate(fromCount=Count('fromDept')).order_by('fromDept')
    tdata = employee_borrow.objects.filter(state=0,fromDate__range=[st,et]).filter(Q(toDept__in=deptids)).values('toDept').annotate(toCount=Count('toDept')).order_by('toDept')
    es_dict = {}#[在岗，离岗]
    id = None
    for i in range(len(empstate)):
        if id==empstate[i]['DeptID_id']:
            count[1] += empstate[i]['empCount']
        else:
            count = []
            id = empstate[i]['DeptID_id']
            if empstate[i]['OffPosition']==0:
                count.extend([empstate[i]['empCount'],0])
            else:
                count.extend([empstate[i]['empCount'],empstate[i]['empCount']])
        es_dict[id] = count

    b_dict = {}
    for f in fdata:
        count = []
        count.append(f['fromCount'])
        count.append(0)
        b_dict[f['fromDept']] = count
    for t in tdata:
        if b_dict.has_key(t['toDept']):
            b_dict[t['toDept']][1] = t['toCount']
        else:
            count = []
            count.append(0)
            count.append(t['toCount'])
            b_dict[t['toDept']] = count

    atts = attShifts.objects.filter(AttDate__range=[st,et],UserID__DelTag=0,deptid__in=deptids).values('deptid').annotate(empCount=Count('deptid'))
    abstime = atts.filter(Absent=1).order_by('deptid')
    ldata = atts.values('deptid','ExceptionID','empCount').filter(ExceptionID__in=l_dict.values()).order_by('deptid','ExceptionID')

    lc_dict = {}
    for ld in ldata:
        if lc_dict.has_key(ld['deptid']):
            lc_dict[ld['deptid']][ld['ExceptionID']] = ld['empCount']
        else:
            tmp = {}
            for key in l_dict.values():
                if key == ld['ExceptionID']:
                    tmp[key] = ld['empCount']
                else:
                    tmp[key] = 0
            lc_dict[ld['deptid']] = tmp
    ab_dict={}
    for ab in abstime:
        ab_dict[ab['deptid']] = ab['empCount']
    datas=[]

    relcount = 0
    oncount = 0
    offcount = 0
    incount = 0
    outcount = 0
    total = 0
    btime = 0
    stime = 0
    abstime = 0
    otime = 0
    for dept in deptids:
        r={}
        r['id'] = dept
        r['dept'] = department.objByID(dept).DeptName
        if es_dict.has_key(dept):
            r['rel'] = (es_dict[dept][0]+es_dict[dept][1]) or ''
            r['onposition'] = es_dict[dept][0] or ''
            r['offposition'] = es_dict[dept][1] or ''
        else:
            r['onposition'] = 0 or ''
            r['offposition'] = 0 or ''
            r['rel'] = 0 or ''
        if b_dict.has_key(dept):
            r['incount'] = b_dict[dept][1] or ''
            r['outcount'] = b_dict[dept][0] or ''
        else:
            r['incount'] = 0 or ''
            r['outcount'] = 0 or ''
        if ab_dict.has_key(dept):
            r['abstime'] = ab_dict[dept]
        else:
            r['abstime'] = 0 or ''
        sum = 0
        if lc_dict.has_key(dept):
            r['remark'] = ''
            remark = ''
            try:
                for k,v in lc_dict[dept].items():
                    sum += v
                    if k<>l_dict[u'病假'] and k<>l_dict[u'事假'] and v<>0:
                        remark += (bl_dict[k]+str(v)+u'人次,')
                r['remark'] = remark and remark[:-1] or ''
                r['btime'] = lc_dict[dept][l_dict[u'病假']] or ''
                r['stime'] = lc_dict[dept][l_dict[u'事假']] or ''
            except Exception,e:
                print e
                r['remark'] = ''
                r['btime'] = 0 or ''
                r['stime'] = 0 or ''
            r['otime'] = (sum-(r['btime'] or 0)-(r['stime'] or 0)) or ''
        else:
            r['btime'] = 0 or ''
            r['stime'] = 0 or ''
            r['otime'] = 0 or ''
            r['remark'] = ''
        r['total'] = (sum+(r['abstime'] or 0)) or ''

        relcount += (r['rel'] or 0)
        oncount += (r['onposition'] or 0)
        offcount += (r['offposition'] or 0)
        incount += (r['incount'] or 0)
        outcount += (r['outcount'] or 0)
        total += (r['total'] or 0)
        btime += (r['btime'] or 0)
        stime += (r['stime'] or 0)
        abstime += (r['abstime'] or 0)
        otime += (r['otime'] or 0)
        datas.append(r)
    userData = {'id':'','dept':u'合计','rel':relcount,'onposition':oncount,'offposition':offcount,'incount':incount,'outcount':outcount,
            'total':total,'btime':btime,'stime':stime,'abstime':abstime,'otime':otime,'remark':''}
    Result['datas'] = datas
    Result['userData'] = userData
    return Result

def exportcalcallreport(ws,datas):
    from mysite.iclock.export import Fields_date_css,Fields_css,Title_css,title_col_css,footer_css2
    style = Fields_date_css()
    field_style=Fields_css()
    title_col_style=title_col_css()
    footer_style=footer_css2()
    
    fields = ['id','dept','rel','onposition','offposition','incount','outcount','total','btime','stime','abstime','otime','remark']
    ws.write_merge(0,0,0,1,u'填报单位:（盖章）')
    ws.write_merge(0,0,2,6,u'填表人:（签名）')
    ws.write_merge(0,0,7,10,u'分管领导:（签名）')
    ws.write_merge(0,0,12,12,u'主要领导:（签名）')
    
    ws.write_merge(1,2,0,0,u'序号',title_col_style)
    ws.write_merge(1,2,1,1,u'单位',title_col_style)
    ws.write_merge(1,2,2,2,u'实有人数',title_col_style)
    ws.write_merge(1,2,3,3,u'在岗人数',title_col_style)
    ws.write_merge(1,2,4,4,u'经组织批准离岗人数',title_col_style)
    ws.write_merge(1,2,5,5,u'借调人数',title_col_style)
    ws.write_merge(1,2,6,6,u'借调出人数',title_col_style)
    ws.write(2,7,u'小计',title_col_style)
    ws.write(2,8,u'病假人次',title_col_style)
    ws.write(2,9,u'事假人次',title_col_style)
    ws.write(2,10,u'旷工人次',title_col_style)
    ws.write(2,11,u'其他',title_col_style)
    ws.write_merge(1,2,12,12,u'备注',title_col_style)
    ws.write_merge(1,1,7,11,u'病事假等情况',title_col_style)
    
    ws.col(0).width = 0x500
    ws.col(1).width = 0x1400
    ws.col(2).width = 0x500
    ws.col(3).width = 0x500
    ws.col(4).width = 0xC00
    ws.col(5).width = 0x500
    ws.col(6).width = 0x800
    ws.col(7).width = 0x500
    ws.col(8).width = 0x500
    ws.col(9).width = 0x500
    ws.col(10).width = 0x500
    ws.col(11).width = 0x500
    ws.col(12).width = 0x1900
    i = 1
    line = 3
    for data in datas:
        column = 0
        for k in fields:
            try:
                if i<>len(datas):
                    if (type(data[k])==int) or (type(data[k])==datetime.date):
                        data[k]=str(data[k])
                    if type(data[k])==datetime.datetime:
                        ws.write(line, column, data[k], style)
                    else:
                        if data[k]==None or data[k]=='None' or data[k]==0 or data[k]=='0':
                            data[k]=''
                        try:
                            data[k] = data[k].decode('utf-8')
                        except:
                            data[k]=data[k]
                        if k=='id' and column==0:
                            ws.write(line, column, i,field_style)
                        else:
                            ws.write(line, column, data[k],field_style)
                else:
                    if k=='id' and column==0:
                        pass
                    elif column==1:
                        ws.write_merge(line,line,0,column, data[k],field_style)
                    else:
                        ws.write(line, column, data[k],field_style)
            except:
                ws.write(line, column,'',field_style)
            column+=1
        line+=1
        i+=1
    footer = u'备注:  1、“实有人数”栏填写本单位人事台账人数。\n          2、此表由主管单位填写,所属二级机构分栏填写；每月5日前报人社局,财政局\n          3、此表一式三份,主管单位、人社局、财政局各一份'
    ws.write_merge(line,line+3,0,12,u'%s'%footer,footer_style)

def getexceptionreportcol():
    return [
        {'name':'id','hidden':True},
        {'name':'dept','label':unicode(u'单位'),'width':140,'sortable':False},
        {'name':'workcode','label':unicode(u'考勤编号'),'sortable':False,'width':100},
        {'name':'ename','label':unicode(u'姓名'),'sortable':False,'width':60},
        {'name':'hireday','label':unicode(u'参加工作时间'),'sortable':False,'width':90},
        {'name':'workage','label':unicode(u'工作年限'),'sortable':False,'width':60},
        {'name':'speday','label':unicode(u'病/事/旷工/其他'),'sortable':False,'width':120},
        {'name':'starttime','label':unicode(u'开始时间'),'sortable':False,'width':80},
        {'name':'endtime','label':unicode(u'截止时间'),'sortable':False,'width':80},
        {'name':'month','label':unicode(u'当月天数'),'sortable':False,'width':60},
        {'name':'year','label':unicode(u'当年累计天数'),'sortable':False,'width':90},
        {'name':'remark','label':unicode(u'备注'),'sortable':False,'width':200}
    ]

def getexceptionreportheader():
    return [
            {'startColumnName': 'starttime', 'numberOfColumns': 2, 'titleText': '<em>时间期限</em>'}
    ]

def calcexceptionreport(request,isContainedChild,deptIDs,st,et,q):
    deptids = []
    if not deptIDs and (request.user.is_superuser or request.user.is_alldept):
        emps = employee.objects.filter(DelTag=0).filter(Q(PIN__icontains=q)|Q(Workcode__icontains=q)).values('id','Workcode','EName','DeptID_id','Hiredday').order_by('DeptID_id','Workcode')
        tmpids = []
        for t_emp in emps:
            tmpids.append(t_emp['id'])
        deptids = list(set(tmpids))
    else:
        if len(deptIDs)>0:
            deptidlist=deptIDs.split(',')
            if isContainedChild=="1": #是否包含下级部门
                for d in deptidlist:#支持选择多部门
                    if int(d) not in deptids :
                        deptids+=getAllAuthChildDept(d,request)
            else:
                deptids = [int(d) for d in deptidlist]
        else:
            deptids=userDeptList(request.user)
        emps = employee.objects.filter(DelTag=0,DeptID_id__in=deptids).filter(Q(PIN__icontains=q)|Q(Workcode__icontains=q)).values('id','Workcode','EName','DeptID_id','Hiredday').order_by('DeptID_id','Workcode')

    lclass = GetLeaveClasses(1)
    l_dict={}
    bl_dict={}
    for l in lclass:
        l_dict[l['LeaveName']] = l['LeaveID']
        bl_dict[l['LeaveID']] = l['LeaveName']
    # if deptids:
    atts = attShifts.objects.filter(AttDate__range=[st,et],UserID_id__in=deptids,UserID__DelTag=0).values('UserID_id').annotate(empCount=Count('UserID_id'))
    # else:
        # atts = attShifts.objects.filter(AttDate__range=[st,et],UserID__DelTag=0).values('UserID_id').annotate(empCount=Count('UserID_id'))
    abstime = atts.filter(Absent=1).order_by('UserID_id')
    ldata = atts.values('UserID_id','ExceptionID','empCount').filter(ExceptionID__in=l_dict.values()).order_by('UserID_id','ExceptionID')

    mt = datetime.datetime(et.year,et.month,1,0,0,0)
    yt = datetime.datetime(et.year,1,1,0,0,0)
    # if deptids:
    atts = attShifts.objects.filter(AttDate__range=[mt,et],UserID_id__in=deptids,UserID__DelTag=0).values('UserID_id').annotate(empCount=Count('UserID_id'))
    atts2 = attShifts.objects.filter(AttDate__range=[yt,et],UserID_id__in=deptids,UserID__DelTag=0).values('UserID_id').annotate(empCount=Count('UserID_id'))
    # else:
        # atts = attShifts.objects.filter(AttDate__range=[mt,et],UserID__DelTag=0).values('UserID_id').annotate(empCount=Count('UserID_id'))
        # atts2 = attShifts.objects.filter(AttDate__range=[yt,et],UserID__DelTag=0).values('UserID_id').annotate(empCount=Count('UserID_id'))
    month_dict = {}
    year_dict = {}
    for att in atts:
        month_dict[att['UserID_id']] = att['empCount']
    for att in atts2:
        year_dict[att['UserID_id']] = att['empCount']

    lc_dict = {}
    for ld in ldata:
        if lc_dict.has_key(ld['UserID_id']):
            lc_dict[ld['UserID_id']][ld['ExceptionID']] = ld['empCount']
        else:
            tmp = {}
            for key in l_dict.values():
                if key == ld['ExceptionID']:
                    tmp[key] = ld['empCount']
                else:
                    tmp[key] = 0
            lc_dict[ld['UserID_id']] = tmp
    ab_dict={}
    for ab in abstime:
        ab_dict[ab['UserID_id']] = ab['empCount']

    datas=[]
    for emp in emps:
        data = {}
        data['id'] = emp['id']
        data['dept'] = department.objByID(emp['DeptID_id']).DeptName or ''
        data['workcode'] = emp['Workcode'] or ''
        data['ename'] = emp['EName'] or ''
        data['hireday'] = emp['Hiredday'] or ''
        data['workage'] = getWorkAge(emp['id'],request) or ''
        sum = 0
        abtime = 0
        data['starttime'] = st.strftime('%Y-%m-%d')
        data['endtime'] = et.strftime('%Y-%m-%d')
        if month_dict.has_key(emp['id']):
            data['month'] = month_dict[emp['id']]
        else:
            data['month'] = ''
        if year_dict.has_key(emp['id']):
            data['year'] = year_dict[emp['id']]
        else:
            data['year'] = ''
        data['remark'] = ''
        remark = ''
        if lc_dict.has_key(emp['id']):
            for k,v in lc_dict[emp['id']].items():
                if k==l_dict[u'病假'] or k==l_dict[u'事假']:
                    if v:
                        tmdata = data.copy()
                        tmdata['speday'] = (bl_dict[k]+str(v))
                        datas.append(tmdata)
                else:
                    if v:
                        remark += (bl_dict[k]+str(v)+',')
                    sum += v
        if ab_dict.has_key(emp['id']):
            abtime = ab_dict[emp['id']]
            if abtime:
                tmdata = data.copy()
                tmdata['speday'] = u'旷'+str(abtime)
                datas.append(tmdata)
        if sum:
            tmdata = data.copy()
            tmdata['speday'] = u'其他'+str(sum)
            tmdata['remark'] = remark
            datas.append(tmdata)
        if (not lc_dict.has_key(emp['id'])) and (not ab_dict.has_key(emp['id'])):
            tmdata = data.copy()
            tmdata['speday'] = ''
            datas.append(tmdata)
    Result = paging(request,datas)
    return Result

def exportcalcexceptionreport(ws,datas):
    from mysite.iclock.export import Fields_date_css,Fields_css,Title_css,title_col_css,footer_css2
    style = Fields_date_css()
    field_style=Fields_css()
    title_col_style=title_col_css()
    footer_style=footer_css2()
    fields = ['id','dept','ename','hireday','workage','speday','starttime','endtime','month','year','remark']
    ws.write_merge(0,0,0,1,u'填报单位:（盖章）')
    ws.write_merge(0,0,2,4,u'填表人:（签名）')
    ws.write_merge(0,0,5,7,u'分管领导:（签名）')
    ws.write_merge(0,0,8,10,u'主要领导:（签名）')
    
    ws.write_merge(1,2,0,0,u'序号',title_col_style)
    ws.write_merge(1,2,1,1,u'单位',title_col_style)
    ws.write_merge(1,2,2,2,u'姓名',title_col_style)
    ws.write_merge(1,2,3,3,u'参加工作时间',title_col_style)
    ws.write_merge(1,2,4,4,u'工作年限',title_col_style)
    ws.write_merge(1,2,5,5,u'病/事/旷工/其他',title_col_style)
    ws.write_merge(1,1,6,7,u'时间期限',title_col_style)
    ws.write(2,6,u'开始时间',title_col_style)
    ws.write(2,7,u'截止时间',title_col_style)
    ws.write_merge(1,2,8,8,u'当月天数',title_col_style)
    ws.write_merge(1,2,9,9,u'当年累计天数',title_col_style)
    ws.write_merge(1,2,10,10,u'备注',title_col_style)
    
    ws.col(0).width = 0x500
    ws.col(1).width = 0x1400
    ws.col(2).width = 0xA00
    ws.col(3).width = 0xF00
    ws.col(4).width = 0x700
    ws.col(5).width = 0xC00
    ws.col(6).width = 0xF00
    ws.col(7).width = 0xF00
    ws.col(8).width = 0x500
    ws.col(9).width = 0x800
    ws.col(10).width = 0x1400
    
    i = 1
    line = 3
    for data in datas:
        column = 0
        for k in fields:
            try:
                if (type(data[k])==int) or (type(data[k])==datetime.date):
                    data[k]=str(data[k])
                if type(data[k])==datetime.datetime:
                    ws.write(line, column, data[k], style)
                else:
                    if data[k]==None or data[k]=='None' or data[k]==0 or data[k]=='0':
                        data[k]=''
                    try:
                        data[k] = data[k].decode('utf-8')
                    except:
                        data[k]=data[k]
                    if k=='id' and column==0:
                        ws.write(line, column, i,field_style)
                    else:
                        ws.write(line, column, data[k],field_style)
            except:
                ws.write(line, column,'',field_style)
            column+=1
        line+=1
        i+=1
    footer = u'备注:  1、此表由主管单位填写,每月5日前报人社、财政部门;“单位”栏填写病/事/旷工人员所在具体单位。2、上月病事假人数为“0”的，不填此表；\n          3、病假、事假和旷工分类单独填表；4、其他包括带薪年休假、婚丧假、生育假等；5、此表一式三份,主管单位、人社局、财政局各一份'
    ws.write_merge(line,line+2,0,10,u'%s'%footer,footer_style)

def getbackreportcol():
    return [
        {'name':'id','hidden':True},
        {'name':'workcode','label':unicode(u'考勤编号'),'sortable':False,'width':100},
        {'name':'ename','label':unicode(u'姓名'),'sortable':False,'width':60},
        {'name':'dept','label':unicode(u'单位'),'width':140,'sortable':False},
        {'name':'hireday','label':unicode(u'参加工作时间'),'sortable':False,'width':90},
        {'name':'month','label':unicode(u'上月天数'),'sortable':False,'width':60},
        {'name':'year','label':unicode(u'当年累计天数'),'sortable':False,'width':90},
        {'name':'total1','label':unicode(u'小计'),'sortable':False,'width':40},
        {'name':'title','label':unicode(u'职务(岗位)'),'sortable':False,'width':90},
        {'name':'level','label':unicode(u'级别(薪级)'),'sortable':False,'width':90},
        {'name':'jichu1','label':unicode(u'生活性津贴(基础绩效)'),'sortable':False,'width':130},
        {'name':'jiangli1','label':unicode(u'工作性津贴(奖励绩效)'),'sortable':False,'width':130},
        {'name':'rever','label':unicode(u'保留福利津贴'),'sortable':False,'width':90},
        {'name':'other1','label':unicode(u'岗位津贴及其他'),'sortable':False,'width':100},
        {'name':'total2','label':unicode(u'小计'),'sortable':False,'width':40},
        {'name':'base','label':unicode(u'基本工资'),'sortable':False,'width':60},
        {'name':'jichu2','label':unicode(u'生活性津贴(基础绩效)'),'sortable':False,'width':130},
        {'name':'jiangli2','label':unicode(u'工作性津贴(奖励绩效)'),'sortable':False,'width':130},
        {'name':'other2','label':unicode(u'岗位津贴及其他'),'sortable':False,'width':100},
        {'name':'real','label':unicode(u'月应发工资'),'sortable':False,'width':90}
    ]

def getbackreportheader():
    return [
            {'startColumnName': 'month', 'numberOfColumns': 2, 'titleText': '<em>事假病假旷工天数</em>'},
            {'startColumnName': 'title', 'numberOfColumns': 2, 'titleText': '<em>基本工资</em>'}
    ]

def backreport(request,isContainedChild,deptIDs,st,et,q):
    lclass = GetLeaveClasses(1)
    l_dict={}
    bl_dict={}
    for l in lclass:
        l_dict[l['LeaveName']] = l['LeaveID']
        bl_dict[l['LeaveID']] = l['LeaveName']

    if len(deptIDs)>0:
        deptidlist=deptIDs.split(',')
        deptids=[]
        if isContainedChild=="1": #是否包含下级部门
            for d in deptidlist:#支持选择多部门
                if int(d) not in deptids :
                    deptids+=getAllAuthChildDept(d,request)
        else:
            deptids = [int(d) for d in deptidlist]
    else:
        deptids=userDeptList(request.user)
        deptids.sort()

    this_month_start = datetime.datetime(et.year, et.month, 1)
    last_month_end = this_month_start - datetime.timedelta(days=1)
    last_month_end = datetime.datetime(last_month_end.year, last_month_end.month, last_month_end.day,23,59,59)
    last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
    ys = datetime.datetime(et.year, 1, 1)
    
    emps = employee.objects.filter(DelTag=0,DeptID_id__in=deptids).values('id','Workcode','EName','DeptID_id','Hiredday').order_by('DeptID_id','Workcode')
    Result = paging(request,emps)
    emps = Result['datas']
    tmpids = []
    for emp in emps:
        tmpids.append(emp['id'])
    deptids = list(set(tmpids))

    attsm = attShifts.objects.filter(AttDate__range=[last_month_start,last_month_end],UserID__DelTag=0,UserID_id__in=deptids).values('UserID_id').annotate(empCount=Count('UserID_id'))
    attsy = attShifts.objects.filter(AttDate__range=[ys,et],UserID__DelTag=0,UserID_id__in=deptids).values('UserID_id').annotate(empCount=Count('UserID_id'))
    abstimem = attsm.filter(Absent=1).order_by('UserID_id')
    abstimey = attsy.filter(Absent=1).order_by('UserID_id')
    ldatam = attsm.values('UserID_id','ExceptionID','empCount').filter(ExceptionID__in=l_dict.values()).order_by('UserID_id','ExceptionID')
    ldatay = attsy.values('UserID_id','ExceptionID','empCount').filter(ExceptionID__in=l_dict.values()).order_by('UserID_id','ExceptionID')
    
    ab_dictm={}
    for abm in abstimem:
        ab_dictm[abm['UserID_id']] = abm['empCount']
    ab_dicty={}
    for aby in abstimey:
        ab_dicty[aby['UserID_id']] = aby['empCount']
    lc_dictm = {}
    for ldm in ldatam:
        if lc_dictm.has_key(ldm['UserID_id']):
            lc_dictm[ldm['UserID_id']][ldm['ExceptionID']] = ldm['empCount']
        else:
            tmp = {}
            for key in l_dict.values():
                if key == ldm['ExceptionID']:
                    tmp[key] = ldm['empCount']
                else:
                    tmp[key] = 0
            lc_dictm[ldm['UserID_id']] = tmp
    lc_dicty = {}
    for ldy in ldatay:
        if lc_dicty.has_key(ldy['UserID_id']):
            lc_dicty[ldy['UserID_id']][ldy['ExceptionID']] = ldy['empCount']
        else:
            tmp = {}
            for key in l_dict.values():
                if key == ldy['ExceptionID']:
                    tmp[key] = ldy['empCount']
                else:
                    tmp[key] = 0
            lc_dicty[ldy['UserID_id']] = tmp
    datas=[]
    colname=[]
    col = getbackreportcol()

    for c in col:
        if c['name'] not in ['id','workcode','dept','ename','hireday','year','month']:
            colname.append(c['name'])
    for emp in emps:
        data = {}
        data['id'] = emp['id']
        data['workcode'] = emp['Workcode'] or ''
        data['dept'] = department.objByID(emp['DeptID_id']).DeptName or ''
        data['ename'] = emp['EName'] or ''
        data['hireday'] = emp['Hiredday'] or ''
        lclsm = 0
        lclsy = 0
        abtimem = 0
        abtimey = 0
        try:
            if lc_dictm.has_key(emp['id']):
                for k,v in lc_dictm[emp['id']].items():
                    if k==l_dict[u'病假'] or k==l_dict[u'事假']:
                        lclsm += v
        except Exception,e:
            print e
            lclsm = 0
        try:
            if lc_dicty.has_key(emp['id']):
                for ky,vy in lc_dicty[emp['id']].items():
                    if ky==l_dict[u'病假'] or ky==l_dict[u'事假']:
                        lclsy += vy
        except Exception,e:
            print e
            lclsy = 0
        if ab_dictm.has_key(emp['id']):
            abtimem = ab_dictm[emp['id']]
        if ab_dicty.has_key(emp['id']):
            abtimey = ab_dicty[emp['id']]
        data['month'] = (lclsm+abtimem) or ''
        data['year'] = (lclsy+abtimey) or ''
        for c in colname:
            data[c] = ''
        datas.append(data)
    Result['datas'] = datas
    return Result

def exportbackreport(ws,datas):
    from mysite.iclock.export import Fields_date_css,Fields_css,Title_css,title_col_css,footer_css4,footer_css3
    style = Fields_date_css()
    field_style=Fields_css()
    title_col_style=title_col_css()
    footer_style=footer_css4()
    footer_style3=footer_css3()
    fields = ['id','ename','dept','hireday','month','year','total1','title','level','jichu1','jiangli1','rever','other','total2','base','jichu2','jiangli2','other2','real']

    ws.write_merge(0,2,0,0,u'序号',title_col_style)
    ws.write_merge(0,2,1,1,u'姓名',title_col_style)
    ws.write_merge(0,2,2,2,u'单位',title_col_style)
    ws.write_merge(0,2,3,3,u'参加工作时间',title_col_style)
    ws.write(2,4,u'上月\n天数',title_col_style)
    ws.write(2,5,u'当年累计天数',title_col_style)
    ws.write_merge(0,1,4,5,u'事假病假\n旷工天数',title_col_style)
    
    ws.write_merge(1,2,6,6,u'小计',title_col_style)
    ws.write(2,7,u'职务\n(岗位)',title_col_style)
    ws.write(2,8,u'级别\n(薪级)',title_col_style)
    ws.write_merge(1,1,7,8,u'基本工资',title_col_style)
    ws.write_merge(1,2,9,9,u'生活性津贴(基础绩效)',title_col_style)
    ws.write_merge(1,2,10,10,u'工作性津贴(奖励绩效)',title_col_style)
    ws.write_merge(1,2,11,11,u'保留福利津贴',title_col_style)
    ws.write_merge(1,2,12,12,u'岗位津贴及其他',title_col_style)
    ws.write_merge(0,0,6,12,u'原应发月工资',title_col_style)
    
    ws.write_merge(1,2,13,13,u'小计',title_col_style)
    ws.write_merge(1,2,14,14,u'基本工资',title_col_style)
    ws.write_merge(1,2,15,15,u'生活性津贴(基础绩效)',title_col_style)
    ws.write_merge(1,2,16,16,u'工作性津贴(奖励绩效)',title_col_style)
    ws.write_merge(1,2,17,17,u'岗位津贴及其他',title_col_style)
    ws.write_merge(0,0,13,17,u'月扣发金额',title_col_style)
    ws.write_merge(0,2,18,18,u'月应发\n工资',title_col_style)
    
    ws.col(0).width = 0x500
    ws.col(1).width = 0xA00
    ws.col(2).width = 0x1300
    ws.col(3).width = 0xE00
    
    ws.col(4).width = 0x700
    ws.col(5).width = 0x900
    ws.col(6).width = 0x700
    ws.col(7).width = 0x700
    ws.col(8).width = 0x700
    ws.col(9).width = 0xC00
    ws.col(10).width = 0xC00
    ws.col(11).width = 0x900
    ws.col(12).width = 0xA00
    ws.col(13).width = 0x700
    ws.col(14).width = 0xA00
    ws.col(15).width = 0xC00
    ws.col(16).width = 0xC00
    ws.col(17).width = 0xA00
    ws.col(18).width = 0x900
    
    i = 1
    line = 3
    for data in datas:
        column = 0
        for k in fields:
            try:
                if (type(data[k])==int) or (type(data[k])==datetime.date):
                    data[k]=str(data[k])
                if type(data[k])==datetime.datetime:
                    ws.write(line, column, data[k], style)
                else:
                    if data[k]==None or data[k]=='None' or data[k]==0 or data[k]=='0':
                        data[k]=''
                    try:
                        data[k] = data[k].decode('utf-8')
                    except:
                        data[k]=data[k]
                    if k=='id' and column==0:
                        ws.write(line, column, i,field_style)
                    else:
                        ws.write(line, column, data[k],field_style)
            except:
                ws.write(line, column,'',field_style)
            column+=1
        line+=1
        i+=1
    ws.write_merge(line,line+7,0,0,u'单\n位\n意\n见',footer_style)
    ws.write_merge(line,line+6,1,5,u'年       月       日      ',footer_style3)
    ws.write_merge(line+7,line+7,1,5,'',footer_style)
    ws.write_merge(line,line+7,6,6,u'主\n管\n部\n门\n意\n见',footer_style)
    ws.write_merge(line,line+6,7,11,u'年       月       日      ',footer_style3)
    ws.write_merge(line+7,line+7,7,11,'',footer_style)
    ws.write_merge(line,line+7,12,12,u'审\n批\n部\n门\n意\n见',footer_style)
    ws.write_merge(line,line+6,13,18,u'年       月       日      ',footer_style3)
    ws.write_merge(line+7,line+7,13,18,'',footer_style)

def getallexceptionreportcol():
    return [
        {'name':'id','hidden':True},
        {'name':'dept','label':unicode(u'单位名称'),'width':140,'sortable':False},
        {'name':'lcount','label':unicode(u'迟到人次'),'sortable':False,'width':60},
        {'name':'lrate','label':unicode(u'迟到率'),'sortable':False,'width':60},
        {'name':'ecount','label':unicode(u'早退人次'),'sortable':False,'width':60},
        {'name':'erate','label':unicode(u'早退率'),'sortable':False,'width':60},
        {'name':'bcheck','label':unicode(u'补签到(退)'),'sortable':False,'width':80},
        {'name':'rcheck','label':unicode(u'补签率'),'sortable':False,'width':60},
        #{'name':'btime','label':unicode(u'补请假人次'),'sortable':False,'width':70},
        {'name':'lecount','label':unicode(u'请假人次'),'sortable':False,'width':60},
        {'name':'lerate','label':unicode(u'请假率'),'sortable':False,'width':60},
        {'name':'scount','label':unicode(u'事假人次'),'sortable':False,'width':60},
        {'name':'srate','label':unicode(u'事假率'),'sortable':False,'width':60},
        {'name':'bcount','label':unicode(u'病假人次'),'sortable':False,'width':60},
        {'name':'brate','label':unicode(u'病假率'),'sortable':False,'width':60},
        {'name':'ocount','label':unicode(u'其他假类人次'),'sortable':False,'width':90},
        {'name':'orate','label':unicode(u'其他假类率'),'sortable':False,'width':60}
    ]

def allexceptionreport(request,isContainedChild,deptIDs,st,et):
    from mysite.iclock.models import checkexact,ATTSTATES
    from mysite.base.models import GetParamValue
    RealWorkNoLate = GetParamValue('RealWorkNoLate','','rule_0')
    lclass = GetLeaveClasses(1)
    l_dict={}
    bl_dict={}
    lids = []
    for l in lclass:
        l_dict[l['LeaveName']] = l['LeaveID']
        bl_dict[l['LeaveID']] = l['LeaveName']
        if not l['Classify']:
            lids.append(l['LeaveID'])

    if len(deptIDs)>0:
        deptidlist=deptIDs.split(',')
        deptids=[]
        if isContainedChild=="1": #是否包含下级部门
            for d in deptidlist:#支持选择多部门
                if int(d) not in deptids :
                    deptids+=getAllAuthChildDept(d,request)
        else:
            deptids = [int(d) for d in deptidlist]
    else:
        deptids=userDeptList(request.user)
    deptids.sort()

    Result = paging(request,deptids)
    deptids = Result['datas']
    atts = attShifts.objects.filter(deptid__in=deptids,AttDate__range=[st,et])
    odata = atts.values('deptid').order_by('deptid').annotate(incount=Count('MustIn'),outcount=Count('MustOut'),worktime=Sum('WorkMins')).values('deptid','incount','outcount','worktime')
    eldata = atts.filter(Q(Early__gt=0)|Q(Late__gt=0)).values('deptid').annotate(ecount=Count('Early'),lcount=Count('Late')).values('deptid','ecount','lcount')
    lcdata = atts.filter(ExceptionID__gt=0,ExceptionID__in=lids).values('deptid','ExceptionID').annotate(esum=Sum('Early'),lsum=Sum('Late'),worktime=Sum('WorkTime'),workmin=Sum('WorkMins')).values('deptid','ExceptionID','esum','lsum','worktime','workmin')
    lemp = atts.filter(ExceptionID__gt=0,ExceptionID__in=lids).values('deptid','ExceptionID').annotate(empcount=Count('deptid'))
    
    ckdata = checkexact.objects.filter(deptid__in=deptids,CHECKTIME__range=[st,et]).values('deptid')
    incheck = ckdata.filter(CHECKTYPE=ATTSTATES[0][0]).annotate(bin=Count('CHECKTYPE'))
    outcheck = ckdata.filter(CHECKTYPE=ATTSTATES[1][0]).annotate(bout=Count('CHECKTYPE'))

    check_dict = {}
    for inc in incheck:
        tmp = {}
        tmp['in'] = inc['bin']
        tmp['out'] = 0
        check_dict[inc['deptid']] = tmp
    for outc in outcheck:
        if check_dict.has_key(outc['deptid']):
            tmp = check_dict[outc['deptid']]
            tmp['out'] = outc['bout']
        else:
            tmp = {}
            tmp['in'] = 0
            tmp['out'] = outc['bout']
            check_dict[outc['deptid']] = tmp
    lcount_dict = {}
    for le in lemp:
        if lcount_dict.has_key(le['deptid']):
            tmp = lcount_dict[le['deptid']]
            tmp[le['ExceptionID']] = le['empcount']
        else:
            tmp = {}
            tmp[le['ExceptionID']] = le['empcount']
            lcount_dict[le['deptid']] = tmp

    odata_dict = {}
    for od in odata:
        tmp = {}
        tmp['incount'] = od['incount']
        tmp['outcount'] = od['outcount']
        tmp['worktim'] = od['worktime']
        odata_dict[od['deptid']] = tmp

    eldata_dict = {}
    for eld in eldata:
        tmp = {}
        tmp['ecount'] = eld['ecount']
        tmp['lcount'] = eld['lcount']
        eldata_dict[eld['deptid']] = tmp

    lcdata_dict = {}
    for lcd in lcdata:
        if lcdata_dict.has_key(lcd['deptid']):
            tmp = lcdata_dict[lcd['deptid']]
            if RealWorkNoLate:
                sum = (lcd['workmin'] or 0)-(lcd['worktime'] or 0)-(lcd['esum'] or 0)-(lcd['lsum'] or 0)
            else:
                sum = (lcd['workmin'] or 0)-(lcd['worktime'] or 0)
            tmp[lcd['ExceptionID']] = sum
        else:
            tmp = {}
            if RealWorkNoLate:
                sum = (lcd['workmin'] or 0)-(lcd['worktime'] or 0)-(lcd['esum'] or 0)-(lcd['lsum'] or 0)
            else:
                sum = (lcd['workmin'] or 0)-(lcd['worktime'] or 0)
            tmp[lcd['ExceptionID']] = sum
            lcdata_dict[lcd['deptid']] = tmp

    datas = []
    for id in deptids:
        data = {}
        lcount = 0
        ecount = 0
        incount = 0
        outcount = 0
        lccount = 0
        lcminute = 0
        scount = 0
        sminute = 0
        bcount = 0
        bminute = 0
        ocount = 0
        ominute = 0
        ckincount = 0
        ckoutcount = 0
        workminute = 0
        
        data['id'] = id
        data['dept'] = department.objByID(id).DeptName
        if eldata_dict.has_key(id):
            lcount = eldata_dict[id]['lcount'] or 0
            ecount = eldata_dict[id]['ecount'] or 0
        if odata_dict.has_key(id):
            incount = odata_dict[id]['incount'] or 0
            outcount = odata_dict[id]['outcount'] or 0
            workminute = odata_dict[id]['worktim'] or 0
        if lcount_dict.has_key(id):
            for k,v in lcount_dict[id].items():
                lccount += v
                if k==l_dict[u'事假']:
                    scount = v
                elif k==l_dict[u'病假']:
                    bcount = v
                else:
                    ocount += v
        if lcdata_dict.has_key(id):
            for k,v in lcdata_dict[id].items():
                lcminute += v
                if k==l_dict[u'事假']:
                    sminute = v
                elif k==l_dict[u'病假']:
                    bminute = v
                else:
                    ominute += v
        if check_dict.has_key(id):
            ckincount = check_dict[id]['in'] or 0
            ckoutcount = check_dict[id]['out'] or 0

        data['lcount'] = lcount or ''
        if incount and lcount:
            data['lrate'] = '%.2f'%(float(lcount)/float(incount)*100)+'%'
        else:
            data['lrate'] = ''
        data['ecount'] = ecount or ''
        if outcount and ecount:
            data['erate'] = '%.2f'%(float(ecount)/float(outcount)*100)+'%'
        else:
            data['erate'] = ''
        data['lecount'] = lccount or ''
        if lcminute and workminute:
            data['lerate'] = '%.2f'%(float(lcminute)/float(workminute)*100)+'%'
        else:
            data['lerate'] = ''
        data['scount'] = scount or ''
        if sminute and workminute:
            data['srate'] = '%.2f'%(float(sminute)/float(workminute)*100)+'%'
        else:
            data['srate'] = ''
        data['bcount'] = bcount or ''
        if bminute and workminute:
            data['brate'] = '%.2f'%(float(bminute)/float(workminute)*100)+'%'
        else:
            data['brate'] = ''
        data['ocount'] = ocount or ''
        if ominute and workminute:
            data['orate'] = '%.2f'%(float(ominute)/float(workminute)*100)+'%'
        else:
            data['orate'] = ''
        data['bcheck'] = (ckincount+ckoutcount) or ''
        if (ckincount and incount) or (ckoutcount and outcount):
            data['rcheck'] ='%.2f'%((float(ckincount)/float(incount)*100)+(float(ckoutcount)/float(outcount)*100))+'%'
        else:
            data['rcheck'] = ''
        datas.append(data)
    Result['datas'] = datas
    return Result

def exportallexceptionreport(ws,datas):
    from mysite.iclock.export import Fields_date_css,Fields_css,Title_css,title_col_css,footer_css2
    style = Fields_date_css()
    field_style=Fields_css()
    title_col_style=title_col_css()
    footer_style=footer_css2()
    fields = ['id','dept','lcount','lrate','ecount','erate','bcheck','rcheck','lecount','lerate','scount','srate','bcount','brate','ocount','orate']

    ws.write(0,0,u'序号',title_col_style)
    ws.write(0,1,u'单位名称',title_col_style)
    ws.write(0,2,u'迟到人次',title_col_style)
    ws.write(0,3,u'迟到率',title_col_style)
    ws.write(0,4,u'早退人次',title_col_style)
    ws.write(0,5,u'早退率',title_col_style)
    ws.write(0,6,u'补签到(退)',title_col_style)
    ws.write(0,7,u'补签率',title_col_style)
    ws.write(0,8,u'请假人次',title_col_style)
    ws.write(0,9,u'请假率',title_col_style)
    ws.write(0,10,u'事假人次',title_col_style)
    ws.write(0,11,u'事假率',title_col_style)
    ws.write(0,12,u'病假人次',title_col_style)
    ws.write(0,13,u'病假率',title_col_style)
    ws.write(0,14,u'其他假类人次',title_col_style)
    ws.write(0,15,u'其他假类率',title_col_style)
    
    ws.col(0).width = 0x500
    ws.col(1).width = 0x1400
    ws.col(2).width = 0xA00
    ws.col(3).width = 0xA00
    ws.col(4).width = 0xA00
    ws.col(5).width = 0xA00
    ws.col(6).width = 0xB00
    ws.col(7).width = 0xA00
    ws.col(8).width = 0xA00
    ws.col(9).width = 0xA00
    ws.col(10).width = 0xA00
    ws.col(11).width = 0xA00
    ws.col(12).width = 0xA00
    ws.col(13).width = 0xA00
    ws.col(14).width = 0xE00
    ws.col(15).width = 0xC00
    
    i = 1
    line = 1
    for data in datas:
        column = 0
        for k in fields:
            try:
                if (type(data[k])==int) or (type(data[k])==datetime.date):
                    data[k]=str(data[k])
                if type(data[k])==datetime.datetime:
                    ws.write(line, column, data[k], style)
                else:
                    if data[k]==None or data[k]=='None' or data[k]==0 or data[k]=='0':
                        data[k]=''
                    try:
                        data[k] = data[k].decode('utf-8')
                    except:
                        data[k]=data[k]
                    if k=='id' and column==0:
                        ws.write(line, column, i,field_style)
                    else:
                        ws.write(line, column, data[k],field_style)
            except:
                ws.write(line, column,'',field_style)
            column+=1
        line+=1
        i+=1

def getjiezhuancol(request):
    year = request.GET.get('y')
    return [
        {'name':'id','hidden':True},
        {'name':'PIN','label':unicode(u'身份证号'),'sortable':False,'width':110},
        {'name':'workcode','label':unicode(u'考勤编号'),'sortable':False,'width':100},
        {'name':'ename','label':unicode(u'姓名'),'width':100,'sortable':False},
        {'name':'dept','label':unicode(u'单位名称'),'sortable':False,'width':140},
        {'name':'qall','label':unicode(str(int(year)-1)+u'年假期结转值'),'sortable':False,'width':110},
        {'name':'now','label':unicode(year+u'年结转'),'sortable':False,'width':80},
        {'name':'all','label':unicode(year+u'年假期结转值'),'sortable':False,'width':110}
    ]

def jiezhuanreport(request,isContainedChild,deptIDs,q):
    from mysite.iclock.models import USER_SPEDAY
    year = request.GET.get('y')
    if not deptIDs and (request.user.is_superuser or request.user.is_alldept):
        emps = employee.objects.filter(DelTag=0).filter(Q(PIN__icontains=q)|Q(Workcode__icontains=q)|Q(EName__icontains=q)).values('id','EName','DeptID_id','Workcode','PIN').order_by('DeptID_id','Workcode')
    else:
        if len(deptIDs)>0:
            deptidlist=deptIDs.split(',')
            deptids=[]
            if isContainedChild=="1": #是否包含下级部门
                for d in deptidlist:#支持选择多部门
                    if int(d) not in deptids :
                        deptids+=getAllAuthChildDept(d,request)
            else:
                deptids = [int(d) for d in deptidlist]
        else:
            deptids=userDeptList(request.user)
            deptids.sort()
        emps = employee.objects.filter(DelTag=0,DeptID_id__in=deptids).filter(Q(PIN__icontains=q)|Q(Workcode__icontains=q)).values('id','EName','DeptID_id','Workcode','PIN').order_by('DeptID_id','PIN')
    Result = paging(request,emps)
    emps = Result['datas']
    tmpids = []
    for t_emp in emps:
        tmpids.append(t_emp['id'])
    deptids = list(set(tmpids))
    et = datetime.datetime(int(year),12,31,23,59,59)
    mt = datetime.datetime(int(year)-1,12,31,23,59,59)
    us = USER_SPEDAY.objects.filter(EndSpecDay__lte=et,State=2,tianshu__gt=0,UserID_id__in=deptids).values('UserID').order_by('UserID')
    nus = us.annotate(days=Sum('tianshu'))
    qus = us.filter(EndSpecDay__lte=mt).annotate(days=Sum('tianshu'))
    nus_dict = {}
    for n in nus:
        nus_dict[n['UserID']] = n['days']
    qus_dict = {}
    for q in qus:
        qus_dict[q['UserID']] = q['days']
    datas = []
    for emp in emps:
        data = {}
        data['id'] = emp['id']
        data['PIN'] = emp['PIN']
        data['workcode'] = emp['Workcode'] or ''
        data['ename'] = emp['EName'] or ''
        data['dept'] = department.objByID(emp['DeptID_id']).DeptName or ''
        data['qall'] = ''
        data['all'] = ''
        if qus_dict.has_key(emp['id']):
            data['qall'] = str(qus_dict[emp['id']])+u'天'
        if nus_dict.has_key(emp['id']):
            data['all'] = str(nus_dict[emp['id']])+u'天'
        ty= (int((data['all'][:-1] or 0)) - int((data['qall'][:-1] or 0))) or ''
        data['now'] = ty and str(ty)+u'天' or ''
        datas.append(data)
    Result['datas'] = datas
    return Result

def paging(request,datas):
    Result={}
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
    paginator = Paginator(datas, limit)
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
    Result['datas'] = pgList.object_list
    return Result