#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.core.tools import *
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
#from django.http import HttpResponse
from django.shortcuts import render_to_response,render
import datetime
from mysite.utils import *
from django.contrib.auth.decorators import permission_required, login_required
from mysite.iclock.dataproc import *
#from django.contrib.auth.models import User, Permission
from mysite.iclock.iutils import *
from mysite.iclock.reb  import *
#REBOOT_CHECKTIME, PAGE_LIMIT, ENABLED_MOD, TIME_FORMAT, DATETIME_FORMAT, DATE_FORMAT
from mysite.cab import *
from mysite.iclock.datv import *
from django.utils.translation import ugettext_lazy as _
#from django.contrib.auth.models import User
#from django.contrib.sessions.models import Session
from mysite.iclock.datas import *
from mysite.iclock.attcalc import *
from mysite.iclock.datasproc import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
#from mysite.iclock.datasproc import *
from mysite.iclock.templatetags.iclock_tags import getSex
from django.utils.encoding import smart_unicode, iri_to_uri
from mysite.iclock.jqgrid import *
from mysite.iclock.clearphotosdata import clearPhotos
from mysite.iclock.sendmail import *
from mysite.iclock.models import *
from django.contrib.auth import get_user_model
from mysite.base.models import *
from mysite.iclock.process import getprocess_EX
import base64
from django.db import connection

def wap(request):
    return render_to_response('loginwap.html')

def picturesave(request):

    image=request.POST.get('image','')
    photoname=request.POST.get('pname','')
    image=image.replace("data:image/jpeg;base64,","")
    #img64='/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAB+AGYDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD36iiigAo6UyWVIImlkYKiDLE9hXlPjP4i+Xuhs32IMgMrctQB6Hf+JNK08SiS8iMsY5iVgWrkLn4pWMU2FYbCpOMdDXhN7r1zdSF/MOeg5rIllnYbm5/GgD3Y/GOPzdu1QN2D8vbFdTpXxH0e+VFml2OwUA46k/y5r5UaZweas2+pSRMu1jxQDPs2zvra/gWe2lWSNuhBqxXzT4S8f3mkXkZMmUP3gxyMemK9/wBA8RWPiCySa2mQyFcvHnlaANeiiigAooooAKOlFUdYvo9O0q5uZTwqHA7k46CgDzH4lfEP7GJtLsnVkIKSMp5J789sV4hI11fyZUl1rU1mZ9V1o7fm8xq7vw54Vt4oVZ057jFROXKa04czPOLPRr2eZVNu+D3wa2n8OvGhV4WwO+2vYINMiiXbGuBVptLjlhKuuQe2Kx9q2dXsIo+eb/Ric+QuT0rNXRr2NsNHXvM/hO1jkYxxgDOelZl7oaYJK8/Sn7Ql0Ezxlra5iOdvArrvBXiO50bVoJVZgoYbgGxkelat5ose0gjj6Vyl1Z/YrvMeVweCK1hLmOedNxPrbT72LUbGK6hbckigirNeafCLXpb/AEuWxuHZjFgoXJJPqBXpdWzIKKKKACuH+KLOPDaKoyrSYb6YruK5nx5aLdeGZiULNGwYY7etAHgGiacravEcc5r2G1twkYArzzwzAJvECp2VWzXojTNG4VQa562rsdtDRXNKGPj3qRiUODUEF9DGAsu8N67eKkluIpiNjZ5rJRsbt3CRSyk1iX0RINbU1xHFEcnFc9fai0jmOGFnJ/iANDVx3sYN5ECSp61xev22x9xHGa7S9S4DlypB75rA162abR5JyPnQhj9Bya2pqxjU1R1XwdWUXshbHl7Djn6V7LXmXwftQulS3JGWYABs16bW9zhas7BRRRQIKztdcLo1wCM712Djua0ao6uCdPbAzhgf1pN2RUFeSR5RoelGy8Sygrj5SfwPH9DXU3EiW4J8suR2xR5I/tR7juUCfgCT/WryRiVuelc7d3c71FRVjj9W8S31tc2lmulKRcAFW5OASRyRwOhrd0pTOodohHjqBWw9lCV2n+VMKJAoVe3SpaKVjJ1RQbgRg/KTisbXr/UtH06U6VZ+YyOEBKsc57gDqPereuTGKQOelWtOnW9swzcgdKRTRx39pazdPEt1bx4Zcuy5HNXJbFbiwkt2H+sjZfoSMV009rEEJ71kqubkx9j0q0yGibwQZdMvdLtbfiGZMSoR0OP/AK1eq15n4SjefxOUY4WBmKj1A4r0yt47HLiLKSt2CiiiqOcKhu4/NtJUBwWU81NQRkYoGnZ3OKAIzmrNu20CtXUNLjWFpYvl28sKxuV6VzNOO53qamrosTOeSvWqF1erFs3hi5IGAM1Z3gJljg1kX2owRTAbyWxztGcVDdzSEDK8V30MeImgckkAlEJHX1pfCMxc3UThlhRh5WRjIxVfUdVdgU+cx5zlhim6dqqtkxtllODS2NZQaN2/kEYbHasW2kMt7n2OKsXt0ZY92etVtHga41GKPJUMcEjrWkNTJ7HU+EdNuV1q4vZYisYBVWP8WcdK7imRRrFEsa9FGBT66ErHnTnzO4UUUUyAooooARlDKVPQjFcjdA2108Lfwnj3FdTc3VvZQNPczJDEgyzu2ABXmF/4vtNa8T3MFhJuSKIFG6B8HDY/MfrWVVaXOjDv3rG/MPNTbng1Qk0uOLdJBAjSE5JPGaba6jG3ys2G96v/ANowwD944/CuZWO5NrY5u+tdQnVkkt4kQ/7dU7LTIrKNvkG9zkmt271K2uAzb846Vz9/q1vbqRvw3amy3NvcW/nSECMGr/h3VrGw1bTxeybDcS7Iyem4g9f89SK4iTUXvZwc554rD8dak9sdKRJHSSJ/MBQ4PXFbU1Y56rsmfV1Fcj4B8X2/ibQIGaVBeRqFkj6H2OPeuurc84KKKKAILu9trGB5rqeOGNAWLOwHFeaa78X7aOdrbR4g5XOZ5Rx+C15HrvivUNXmeS6naQsxPJ4GfQdqwYpnDtnoatRJudVq/i/U9evZJry4eREyFXdhR9F6Viadq50/xJY3Rbau7a5z/CeD/PP4VVBVE2r0PJrI1IF3Hsc0qivGxdN2lc+h57BJoxcwZ+cZBFYN/DqAUjczAdqu/DXX49f8ORwSvi6tQI3H97rg/liuquLPIJArz5Kx6EJ3R5ZNc30UZiCOreuDWZJBeXUg87LH1Nem3VgzgjbVOPRVDAsv6VKkzS6OTsdNECeYy4CjNed+Lbx7/wARNg5ii+VPpnNez6rCILaRE7j9K8W1aONNTm2diRW1Ntu5hWa5bGnoetz2AAhleNgMqyMQQceor1Pwh8W7yHy7bWGF1FkBpMYdP8e3/wBevC4pNjA1Ob028yyKeG5b612pp7nnI+zdL1rT9ZgE1hdJMuOQDyv1HbqKK+ULbX5UiAVuPrRRyruVcxWl5Xn3pyzljxVHeS4/3TUb3LRQfKACe9K5BqNdRxAmRsYrMur+GckKWyfas15GlO52JPrVq2tUkkjB7jNJu5S3Ow+GuuvoviVI3OIJxg5PfoP519Ho6yJwwIr5OuF+yPHNEcOnKn0Ne3eBvE1zrOmRvKMSKAGbPU1yVVbU9LCJVbxW530kXOaqzhgCFphupR1YmoJrtlRmIyAM1y+0i9jseHktWYHiZ1sdLuLudgo2kLzySeBXg08rySySSH5nOTXS+O9duNW1qSFmZYICwjXNcNJcybutdtFe6eViG1KxcLYpj/PGV/GqyTMx5q2gytb2Oaw+ByYVC9QOaKqpM0LyKvTNFAH/2Q=='

    base64ToImg(image,photoname)
    return getJSResponse({"ret":0,'message':''})

def base64ToImg(imgStr,photoname):
    if imgStr == '':
        return False
    import base64
    imgData = base64.decodestring(imgStr)
    pdir=settings.ADDITION_FILE_ROOT+'photo\\'+photoname+'.jpg'
    pudir=settings.ADDITION_FILE_ROOT+'photo\\thumbnail\\'+photoname+'.jpg'
    imgsave = open(pdir,'wb')
    imgsave.write(buffer(imgData))
    imgsave.close()
    try:
        import PIL.Image as Image
        im = Image.open(pdir)
        (x,y) = im.size
        x_s = 100
        y_s = y * x_s / x
        out = im.resize((x_s,y_s),Image.ANTIALIAS)
        out.save(pudir)
    except:
        pass

def waplogin(request):
    pin = request.POST.get('userpin', '')
    phone = request.POST.get('userphone', '')
    try:
        emp=employee.objects.get(PIN=pin,Mobile=phone)

    except:
        emp=None
    if emp==None:
        return render_to_response('loginwap.html',{'error':u"没有该用户"})
        #return HttpResponseRedirect('/someurl/')
        #return getJSResponse({"ret":1,"message":u"%s"%_(u'考勤号码不存在')},mtype="text/plain")
    else:
        request.session['user'] = emp.PIN
        return HttpResponseRedirect('/waprecordlist/')
        #return getJSResponse({"ret":0,"message":u"%s"%_(u'No User data file')},mtype="text/plain")
    #return HttpResponse("Hello world")


def waprecordlist(request):
    try:
        uid=request.session['user']
        emp=employee.objects.get(PIN=uid)
    except:
        return render_to_response('loginwap.html')
    pin = request.POST.get('userpin', '')
    pagecurrent=request.GET.get('page', '1')
    p=request.GET.get('p', None)
    if p:
        if p=="p":
            pagecurrent=int(pagecurrent)-1
        else:
            pagecurrent=int(pagecurrent)+1

    if int(pagecurrent)<1:
        pagecurrent='1'
    if emp==None:
        return HttpResponse("exception")

    records=transactions.objects.filter(UserID=emp).order_by('-TTime')
    pageobject = Paginator(records, 20)
    totalpages=pageobject.num_pages
    if totalpages<=int(pagecurrent):
        pagecurrent=totalpages

    try:
        page = pageobject.page(int(pagecurrent))
    except:
        page = pageobject.page(1)

    records = page.object_list
    result=[]
    for re in records:
        r={}
        r['TTime']=re.TTime
        result.append(r.copy())
    records=result

    count=pageobject.count
    return render(request,'waprecordslist.html', {'latest_item_list':records,'pagecurrent':pagecurrent,'emp':emp,'count':count,'totalpages':totalpages})

@login_required
def report_annual(request):
    request.user.iclock_url_rel='../..'
    request.model = transactions

    settings.PAGE_LIMIT=GetParamValue('opt_users_page_limit','50',request.user.id)
    limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
    cc={
            'limit':limit
    }

    return render(request,'annual_leave_report.html',cc)
    #return render_to_response('annual_leave_report.html',
    #                                               RequestContext(request, {
    #                                               'from': 1,
    #                                               'page': 1,
    #                                               'limit': 10,
    #                                               'item_count': 4,
    #                                               'page_count': 1,
    #                                               'iclock_url_rel': request.user.iclock_url_rel,
    #                                               }))

@login_required
def shift_detail(request):
    if request.method=="POST":
        id=int(request.POST.get("Shift_id","0"))
        unit=int(request.POST.get("unit","1"))
        #weekStart=int(request.POST.get("weekStartDay","0"))
        attrule=LoadAttRule()
        weekStart=attrule['WorkWeekStartDay']
        objNRD=NUM_RUN_DEIL.objects.filter(Num_runID=id).order_by('Num_runID', 'Sdays', 'StartTime')
        l=[]
        dic={}
        li=[]
        n=0
        d={}
        if objNRD.count()==0:
            d['StartTime']=0
            d['EndTime']=0
            d['Color']=16715535
            d['SchName']=''
            d['SchClassID']=''
            l.append(d.copy())
            qs=l
        else:
            #sch=GetSchClasses()
            for t in objNRD:
                st=(float(t.StartTime.hour)+float(t.StartTime.minute)/60)/24
                et=(float(t.EndTime.hour)+float(t.EndTime.minute)/60)/24
                sd=t.Sdays
                ed=t.Edays
                sclass=FindSchClassByID(t.SchclassID_id)
                if not sclass:continue
                clr=sclass['Color']
                st=(float(sclass['TimeZone']['StartTime'].hour)+float(sclass['TimeZone']['StartTime'].minute)/60)/24
                et=(float(sclass['TimeZone']['EndTime'].hour)+float(sclass['TimeZone']['EndTime'].minute)/60)/24
                if unit==1:
                    sd=sd-weekStart
                    ed=ed-weekStart
                    if ed<0:
                        sd=sd+7
                        ed=ed+7
                d['StartTime']=st+sd
                d['EndTime']=et+ed
                if clr==None:
                    d['Color']=16715535
                else:
                    d['Color']=clr
                d['SchName']=sclass['SchName']
                d['SchClassID']=t.id
                l.append(d.copy())
    return getJSResponse(dumps(l))

#此函数已作废
@login_required
def assignedShifts(request):
    if request.method=="POST":
        id=request.POST.get("emp","")
        deptids=request.POST.get("deptIDs","")
        deptIDs=[]
        if id=="":
            deptIDs=getAllAuthChildDept(int(deptids),request)
            UserIDs = employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
            #len(UserIDs)
            id=UserIDs[0]
        schPlan=LoadSchPlan(int(id),True,True,True)
        return getJSResponse(dumps(schPlan))

@login_required
def worktimezone(request):
    tzs=[]
    if request.method=="POST":
        id=request.POST.get("UserID",0)
        d1=request.POST.get("ComeTime"," ")
        d2=request.POST.get("EndDate"," ")
        flag=request.GET.get("flag","0")

        d1=datetime.datetime.strptime(d1,'%Y-%m-%d')
        d2=datetime.datetime.strptime(d2,'%Y-%m-%d')
        if int(flag)==1:
            msg={'message':'no data'}
            id=request.GET.get("userid","0")
            emp=employee.objByID(int(id))
            fn='%s/%s.txt'%(settings.ADDITION_FILE_ROOT+"/schedule/emp_schedule/",emp.pin())
            if os.path.exists(fn):
                f=open(fn,'r')
                lines=f.readlines()
                f.close()
                line="<br>".join(lines)
                msg['message']=line
            return getJSResponse(dumps(msg))


        emp=employee.objByID(int(id))
        AttRule=LoadAttRule()
        day_off_count=days_off.objects.filter(Q(FromDate__gte=d1,FromDate__lte=d2)|Q(ToDate__lte=d2,ToDate__gte=d1)).count()
        holidays=loadHoliday()
        initParams={'AttRule':AttRule,'day_off_count':day_off_count,'Holiday':holidays}
        userplan=LoadSchPlan(emp,True,True)
        l=GetUserScheduler(emp, d1, d2, userplan['HasHoliday'],initParams)
        for t in l:
            if t['TimeZone']['StartTime']>=d1 and t['TimeZone']['EndTime']<d2+datetime.timedelta(days=2):
                li=[]
                k={}
                if t['TimeZone']['EndTime']>d2+datetime.timedelta(days=1):
                    k['dis']=t['TimeZone']['StartTime']-d1
                    k['die']=d2+datetime.timedelta(days=1)-d1
                    li.append(k.copy())
                    k['dis']=d2+datetime.timedelta(days=1)-d1
                    k['die']=t['TimeZone']['EndTime']-d1

                    li.append(k.copy())
                else:
                    k['dis']=t['TimeZone']['StartTime']-d1
                    k['die']=t['TimeZone']['EndTime']-d1
                    li.append(k.copy())
                for v in li:
                    d={}
                    dd1=v['dis'].days
                    dd2=v['die'].days
                    dt1=float(v['dis'].seconds)/60/60/24
                    dt2=float(v['die'].seconds)/60/60/24
                    ds=dd1+dt1
                    de=dd2+dt2
                    d['StartTime']=ds
                    d['EndTime']=de
                    d['alt2']=t['TimeZone']['StartTime']
                    d['SchClassID']=t['schClassID']
                    d['SchName']=t['SchName']
                    if 'Color' in t:
                        d['Color']=t['Color']
                    else:
                        d['Color']=16715535
                    tzs.append(d.copy())
    return getJSResponse(dumps(tzs))

#人事信息提醒详情
@login_required
def ihrreminddetail(request):
    if request.method=="GET":
        r=[]
        item=request.GET.get("uid","1")
        fields,heads=ConstructhrremindFields(int(item))
        index=0
        for field in fields:
            r.append({"name":""+field,'sortable':False,"index":""+field,'label':heads[index],'width':100})
            index=index+1

        rs="{"+""""colModel":"""+dumps(r)+"""}"""
        return getJSResponse(rs)

    else:
        tzs=[]
        r={}
        if request.method=="POST":
            item=request.GET.get("uid","1")
            cometime=request.GET.get("cometime","")

            try:
                tzs=calchrreminddata(request,item,cometime)
            except Exception,ee:
                print ee


        limit = int(request.POST.get('rows', 30))
        offset = int(request.POST.get('page', 1))

        r['item_count']=len(tzs)
        r['page']=offset
        r['limit']=limit
        page_count =int(ceil(len(tzs)/float(limit)))
        tzs=tzs[(offset-1)*limit:offset*limit]
        r['page_count']=page_count
        r['page']=offset
        r['limit']=limit
        r['datas']=tzs
        rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
        return getJSResponse(rs)

#年假字段生成及显示数据
@login_required
def annualstatic(request):
    if request.method=="GET":
        r=[]
        heads,fields=getannualstaticFiled(request)
        index=0
        for field in fields:
            if field in ['pin','Workcode','name','dept','days','Hiredday','weiyong']:
                r.append({"name":""+field,'sortable':False,"index":""+field,'label':heads[index],'width':110})
            else:
                r.append({"name":""+field,'sortable':False,"index":""+field,'label':heads[index],'width':85})
            index=index+1
        rs="{"+""""colModel":"""+dumps(r)+"""}"""
        return getJSResponse(rs)

    else:
        tzs=[]
        r={}
        limit = int(request.POST.get('rows', 30))
        offset = int(request.POST.get('page', 1))
        deptid=request.GET.get("deptIDs",1)
        isContainChild=request.GET.get("isContainChild","0")
        deptids=[]
        if isContainChild=="1":
            deptids=getAllAuthChildDept(deptid,request)
        else:
            deptids.append(deptid)
        q=request.GET.get('q',"")
        q=unquote(q)
        if q!='':
            emp=employee.objects.filter(OffDuty=0).filter(Q(PIN__contains='%s'%(q))|Q(EName__contains='%s'%(q))|Q(Workcode__contains='%s'%(q))).exclude(DelTag=1)
        else:
            deptids=getAllAuthChildDept(deptid,request)
            emp=employee.objects.filter(DeptID__in=deptids,OffDuty=0).exclude(DelTag=1)
        r['item_count']=len(emp)
        r['page']=offset
        r['limit']=limit
        page_count =int(ceil(len(emp)/float(limit)))
        tzs=emp[(offset-1)*limit:offset*limit]
        tzs=getannual(request,tzs)
        r['page_count']=page_count
        r['page']=offset
        r['limit']=limit
        r['datas']=tzs
        rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
        return getJSResponse(rs)

def getannualstaticFiled(request):
    y=request.GET.get('y')
    ys=datetime.datetime.strptime(y,"%Y-%m")
    months=1
    days=1
    ann=annual_settings.objects.filter(Name="month_s")
    if ann.count()>0:
        months=int(ann[0].Value)
    ann=annual_settings.objects.filter(Name="day_s")
    if ann.count()>0:
        days=int(ann[0].Value)
    biao=datetime.datetime(ys.year,months,days,0,0).strftime("%Y%m")
    biao1=(datetime.datetime(ys.year+1,months,days,0,0)-datetime.timedelta(days=1)).strftime("%Y%m")
    fields=['pin','Workcode','name','dept','sex','Hiredday','bennianyuefen','gongling','days']
    le=LeaveClass.objects.filter(LeaveType=5)
    unit=3
    if le.count()>0:
        unit=le[0].Unit
    if unit==1:
        heads=[u'%s'%_('PIN'),u'%s'%_('NewPin'),u'%s'%_('name'),u'%s'%_('department name'),u'%s'%_("sex"),u'%s'%_(u"聘用日期"),u'%s'%_(u"年份"),u'%s'%_(u"工龄"),u'%s'%_(u"年假小时数")]
    else:
        heads=[u'%s'%_('PIN'),u'%s'%_('NewPin'),u'%s'%_('name'),u'%s'%_('department name'),u'%s'%_("sex"),u'%s'%_(u"聘用日期"),u'%s'%_(u"年份"),u'%s'%_(u"工龄"),u'%s'%_(u"年假天数")]
    ann=annual_settings.objects.filter(Name="month_s")
    nian=int(biao[:4])
    yue=int(biao[4:])
    while True:
        if int(biao)<=int(biao1):
            fields.append(biao)
            heads.append(u"%s年%s月"%(nian,yue))
        else:
            break
        yue=yue+1
        if yue>12:
            yue=1
            nian+=1
        biao="%s%s"%(nian,("00%s"%yue)[-2:])
    fields.append('weiyong')
    if unit==1:
        heads.append(u'%s'%_(u'未用年假小时数'))
    else:
        heads.append(u'%s'%_(u'未用年假天数'))
    return heads,fields

def getSingleAnnual(request,uid):
    y=datetime.datetime.now().year
    months=1
    days=1
    ann=annual_settings.objects.filter(Name="month_s")
    if ann.count()>0:
        months=int(ann[0].Value)
    ann=annual_settings.objects.filter(Name="day_s")
    if ann.count()>0:
        days=int(ann[0].Value)
    Ann_restart=datetime.datetime(y,months,days,0,0)
    if datetime.datetime.now()<Ann_restart:
        y=y-1
        biao=datetime.datetime(y,months,days,0,0)
    else:
        biao=Ann_restart
        Ann_restart=datetime.datetime(y+1,months,days,0,0)
    le=LeaveClass.objects.filter(LeaveType=5)
    unit=3
    minunit=1
    remaindproc=1
    if le.count()>0:
        unit=le[0].Unit
        minunit=le[0].MinUnit
        minunit=le[0].MinUnit
        remaindproc=le[0].RemaindProc
    yy= getUserAnn(uid,biao,minunit,unit,remaindproc)
    cc=0
    for x in yy.keys():
        cc+=yy[x]
    try:
        dd=float(days)
    except :
        dd=0
    e=employee.objByID(uid)
    ll={}
    ll['Ayear']=str(y)+'年'
    ll['unit']=unit
    if e.Hiredday:
        ll['Hiredday']=e.Hiredday.strftime("%Y-%m-%d")
    else:
        ll['Hiredday']=''
    ll['gongling']=getWorkAge_(e.Hiredday,biao)
    ll['Ann_restart']=Ann_restart.strftime("%Y-%m-%d")
    ll['days']=getuserannual(uid,biao.strftime("%Y-%m-%d"))
    if ll['days']:
        ll['days']=getzhuang(ll['days'],unit)
    else:
        ll['days']=''
    yy= getUserAnn(uid,biao,minunit,unit,remaindproc)
    cc=0
    for x in yy.keys():
        ll[x]=yy[x]
        cc+=ll[x]
    try:
        dd=float(ll['days'])
    except :
        dd=0
    ll['canused']=dd-cc
    ll['Hasused']=cc
    return ll

def getannual(request,tzs):
    y=request.GET.get('y')
    ys=datetime.datetime.strptime(y,"%Y-%m")
    yearstr=ys.year
    months=1
    days=1
    ann=annual_settings.objects.filter(Name="month_s")
    if ann.count()>0:
        months=int(ann[0].Value)
    ann=annual_settings.objects.filter(Name="day_s")
    if ann.count()>0:
        days=int(ann[0].Value)
    biao=datetime.datetime(ys.year,months,days,0,0)
    re=[]
    le=LeaveClass.objects.filter(LeaveType=5)
    unit=3
    minunit=1
    remaindproc=1
    if le.count()>0:
        unit=le[0].Unit
        minunit=le[0].MinUnit
        minunit=le[0].MinUnit
        remaindproc=le[0].RemaindProc
    for e in tzs:
        ll={}
        ll['pin']=e.PIN
        ll['name']=e.EName
        ll['Workcode'] = e.Workcode
        ll['dept']=e.Dept().DeptName
        ll['sex']=getSex(e.Gender)
        ll['Hiredday']=e.Hiredday
        ll['bennianyuefen']=yearstr
        ll['gongling']=getWorkAge_(e.Hiredday,biao)
        ll['days']=getuserannual(e.id,biao.strftime("%Y-%m-%d"))
        if ll['days']:
            ll['days']=getzhuang(ll['days'],unit)
        else:
            ll['days']=''
        yy= getUserAnn(e.id,biao,minunit,unit,remaindproc)
        cc=0
        for x in yy.keys():
            ll[x]=yy[x]
            cc+=ll[x]
        try:
            dd=float(ll['days'])
        except :
            dd=0
        ll['weiyong']=dd-cc
        re.append(ll)
    return re

def getzhuang(val,unit):
    if unit==1:
        attP=AttParam.objects.filter(ParaName="MinsWorkDay")
        hours=8
        if attP:
            hours=float(attP[0].ParaValue)/60
        val=float(val)*hours
    return val
def getUserAnn(id,y,minunit,unit,remaindproc):
    LClass=GetLeaveClassesEx(1)
    LeaveID=[]
    for t in LClass:
        if t['LeaveType']==5:
            LeaveID.append(t['LeaveID'])
    y1=datetime.datetime(year=y.year+1,month=y.month,day=y.day)
    AttExcep=AttException.objects.filter(UserID=int(id),ExceptionID__in=LeaveID,InScopeTime__gt=0,AttDate__lte=y1,AttDate__gt=y)
    ll={}
    biao=y.strftime("%Y%m")
    biao1=y1.strftime("%Y%m")
    nian=int(biao[:4])
    yue=int(biao[4:])
    while True:
        if int(biao)<=int(biao1):
            ll[biao]=0
        else:
            break
        yue=yue+1
        if yue>12:
            yue=1
            nian+=1
        biao="%s%s"%(nian,("00%s"%yue)[-2:])
    for a in AttExcep:
        ll["%s%s"%(a.AttDate.year,("00%s"%a.AttDate.month)[-2:])]+=NormalAttValue(a.InScopeTime,minunit,unit,remaindproc)
    return ll

def getWorkAge_(value,ys):
    d_y_m=ys
    d_h=value
    if d_h:
        y1=d_y_m.year
        m1=d_y_m.month
        y2=d_h.year
        m2=d_h.month
        if (y1>y2) or ((y1==y2) and (m1>m2)):
            if m1>=m2:
                m=m1-m2
                y=y1-y2
            else:
                m=m1+12-m2
                y=y1-y2-1
        elif (y1==y2) and (m1<=m2):
            y=y1-y2
        return "%s年"%y

    return ""

@login_required
def ihrreversedetail(request):
    item=request.GET.get("uid","1")
    if item=="1":
        if (request.user.is_superuser) or (request.user.is_alldept):
            qs=employee.objects.all().extra(where=['UserID NOT IN (%s)'%('select userid from template')])
        else:
            deptid=userDeptList(request.user)
            qs=employee.objects.filter(DeptID__in=deptid).extra(where=['UserID NOT IN (%s)'%('select userid from template')])

    elif item=="2":
        if (request.user.is_superuser) or (request.user.is_alldept):
            qs=employee.objects.all().extra(where=['UserID NOT IN (%s)'%('select userid from facetemplate')])
        else:
            deptid=userDeptList(request.user)
            qs=employee.objects.filter(DeptID__in=deptid).extra(where=['UserID NOT IN (%s)'%('select userid from facetemplate')])
    elif item=='3':
        now=datetime.datetime.now()
        if (request.user.is_superuser) or (request.user.is_alldept):
            trans=transactions.objects.filter(TTime__year=now.year,TTime__month=now.month,TTime__day=now.day).values_list("UserID")
            qs=employee.objects.all().exclude(id__in=trans)
        else:
            deptid=userDeptList(request.user)
            trans=transactions.objects.filter(UserID__DeptID__in=deptid,TTime__year=now.year,TTime__month=now.month,TTime__day=now.day).values_list("UserID")
            qs=employee.objects.filter(DeptID__in=deptid).exclude(id__in=trans)

    elif item=='4':
        yestoday=datetime.datetime.now()-datetime.timedelta(days=1)
        if (request.user.is_superuser) or (request.user.is_alldept):
            trans=transactions.objects.filter(TTime__year=yestoday.year,TTime__month=yestoday.month,TTime__day=yestoday.day).values_list("UserID")
            qs=employee.objects.all().exclude(id__in=trans)
        else:
            deptid=userDeptList(request.user)
            trans=transactions.objects.filter(UserID__DeptID__in=deptid,TTime__year=yestoday.year,TTime__month=yestoday.month,TTime__day=yestoday.day).values_list("UserID")
            qs=employee.objects.filter(DeptID__in=deptid).exclude(id__in=trans)

    elif item=='5':
        now=datetime.datetime.now()
        now=datetime.datetime(now.year,now.month,now.day,0,0,0)
        start=now-datetime.timedelta(days=now.weekday())
        end=now+datetime.timedelta(days=7-now.weekday())
        if (request.user.is_superuser) or (request.user.is_alldept):
            trans=transactions.objects.filter(TTime__gte=start,TTime__lt=end).values_list("UserID")
            qs=employee.objects.all().exclude(id__in=trans)
        else:
            deptid=userDeptList(request.user)
            trans=transactions.objects.filter(UserID__DeptID__in=deptid,TTime__gte=start,TTime__lt=end).values_list("UserID")
            qs=employee.objects.filter(DeptID__in=deptid).exclude(id__in=trans)
    elif item=='6':
        now=datetime.datetime.now()
        if (request.user.is_superuser) or (request.user.is_alldept):
            trans=transactions.objects.filter(TTime__year=now.year,TTime__month=now.month).values_list("UserID")
            qs=employee.objects.all().exclude(id__in=trans)
        else:
            deptid=userDeptList(request.user)
            trans=transactions.objects.filter(UserID__DeptID__in=deptid,TTime__year=now.year,TTime__month=now.month).values_list("UserID")
            qs=employee.objects.filter(DeptID__in=deptid).exclude(id__in=trans)
    else:
        qs=None
    if qs:

        qs=qs.filter(OffDuty=0)

        limit = int(request.POST.get('rows', 30))
        offset = int(request.POST.get('page', 1))
        r={}
        paginator = Paginator(qs, limit)
        item_count = paginator.count
        if offset>paginator.num_pages: offset=paginator.num_pages
        if offset<1: offset=1
        pgList = paginator.page(offset)
        ll=[]
        for p in pgList.object_list:
            uu={}
            uu['id']=p.id
            uu['pin']=p.PIN
            uu['name']=p.EName
            if p.Dept():
                uu['dept']=p.Dept().DeptName
            else:
                uu['dept']=''
            uu['sex']=p.get_Gender_display()
            ll.append(uu)
        r['item_count']=item_count
        r['page_count']=paginator.num_pages
        r['page']=offset
        r['limit']=limit
        r['datas']=ll
        rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
        return getJSResponse(rs)
    else:
        rs="{"+""""page":"""+str(0)+","+""""total":"""+str(0)+","+""""records":"""+str(0)+","+""""rows":"""+dumps([])+"""}"""
        return getJSResponse(rs)



@login_required
def hasRoles(request):
    ll=[]
    role=userRoles.objects.all()
    for i in role:
        ll.append(i.roleName)
    return getJSResponse(dumps(ll))

@login_required
def attrule(request):
    l=[]
    attrule=LoadAttRule()
    l.append(attrule)
    return getJSResponse(dumps(l))


@permission_required("iclock.browse_employee")  #指纹采集器登记指纹渲染页面
def registerFinger(request):
    request.user.iclock_url_rel='../..'
    request.model = employee
    return render(request,'RegisterFP_list.html',
                                                     {
                                                    'from': 1,
                                                    'page': 1,
                                                    'limit': 10,
                                                    'item_count': 4,
                                                    'page_count': 1,
                                                    'iclock_url_rel': request.user.iclock_url_rel,
                                                    })

@permission_required("visitors.browse_visitionlogs")
def saveSSNPhoto(request):    #上传人员照片
    #request.user.iclock_url_rel='../..'
    #request.model = employee
    #from base64 import decodestring
    if request.method == 'POST':

        SSN=request.POST.get('SSN','')
        img64=request.POST.get('img','')
        img64=img64.replace("\n","").replace("\r","").replace(" ","")
        try:
            imgData = base64.decodestring(img64)
        except Exception,e:
            print e

        pdir=settings.ADDITION_FILE_ROOT+'photo\\'+SSN+'.jpg'
        if not os.path.exists(pdir):
            #print pdir,'==='
            imgsave = open(pdir,'wb')
            imgsave.write(buffer(imgData))
            imgsave.close()
        return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')},mtype="text/plain")


@permission_required("iclock.browse_employee")
def savePhoto(request):    #上传人员照片
    request.user.iclock_url_rel='../..'
    request.model = employee
    if request.method == 'POST':
        f=request.FILES["fileToUpload"]
        pin= request.GET.get("PIN")
        pin=employee.objByID(pin).PIN
        pin='%s.%s'%(pin,f.name.split(".")[1])
        #try:
        #       os.makedirs("%sphoto/"%settings.ADDITION_FILE_ROOT)
        #except:
        #       pass
        from mysite.iclock.datamisc import saveUploadImage
        fname="%s%s/%s"%(settings.ADDITION_FILE_ROOT,'photo',pin)
        saveUploadImage(request, "fileToUpload", fname)
        tbName=getStoredFileName("photo/thumbnail", None, pin)
        if os.path.exists(tbName):
            fullName=getStoredFileName("photo", None, pin)
            if os.path.exists(fullName):
                createThumbnail(fullName, tbName)
        return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')},mtype="text/plain")
#               return HttpResponse("result=0")
#
#def handle_upfile(files):
#       print 'file name is', files['name']
#       storefile = open(files.name, 'w')
#       for chunk in files.chunks():
#               storefile.write(chunk)
#       storefile.close()
#def upload(request):
#       if request.method == 'POST':
#               # form = upfileform.UploadForm(request.POST, request.FILES)
#               #print 'check if is_valid'
#               print request
#               f=request.FILES["fileToUpload"]
#               print f.name,'oooooooooooooo'
#               handle_upfile(f)
#               return HttpResponseRedirect(reverse('fage.views.detail'))
#       else:
#               form = upfileform.UploadForm()
#       return render(request, 'fage/upload.html', {'form': form})


@login_required
def saveFingerprint(request):    #保存指纹采集器登记的指纹模板
    userid=int(request.POST['UserIDs'])
    fid=request.POST.get('fingerid',0)
    tmp=request.POST.get('templates','')
    tmps=tmp.split(',')
    fids=fid.split(',')
    AlgVer=GetParamValue('opt_basic_algversion','1')
    if AlgVer=='on':
        AlgVer='1'
    if AlgVer=='1':
        AlgVer=10
    else:
        AlgVer=9
    if (not fids) or (not tmps):
        return getJSResponse({"ret":0,"message": u"%s"%_('Save Failed')},mtype="text/plain")

    for i in range(len(fids)):
        try:

            f=BioData.objects.filter(UserID=userid, bio_no=int(fids[i])-1,bio_type=bioFinger,majorver=AlgVer)
            if f.count():
                dDict={'whereuserid':userid,'wherebio_no':int(fids[i])-1,'wheremajorver':AlgVer,'wherebio_type':bioFinger,'bio_tmp':tmps[i],'UTime':datetime.datetime.now()}
                sql,params=getSQL_update_new(BioData._meta.db_table,dDict)




                #sql="update template set template = '%s', utime='%s',AlgVer=%s where userid=%s and fingerid=%s" % (tmps[i], str(datetime.datetime.now())[:19], AlgVer,userid, int(fids[i])-1)
            else:
                dDict={'userid':userid,'bio_no':int(fids[i])-1,'bio_index':0,'bio_format':0,'minorver':'0','duress':0,'majorver':AlgVer,'bio_tmp':tmps[i],'bio_type':bioFinger,'valid':1,'UTime':datetime.datetime.now()}
                sql,params=getSQL_insert_new(BioData._meta.db_table,dDict)


#                               sql="insert into template(template, userid, fingerid,  utime, valid,AlgVer) values('%s', %s, %s, '%s', 1,%s)" % (tmps[i], userid, int(fids[i])-1, str(datetime.datetime.now())[:19],AlgVer)
            if sql:
                customSqlEx(sql,params)
        except:
#                       return  getJSResponse("result=1; message='%s'%_('Save Failed');")
            return getJSResponse({"ret":1,"message": u"%s"%_('Save Failed')})
#                       return getJSResponse(content="result=1",mimetype='text/plain')
    return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')})
#       return getJSResponse(content="result=0",mimetype='text/plain')




@permission_required("iclock.Forget_transaction")
def forget(request):
    request.user.iclock_url_rel='../..'
    request.model = transactions
    #d=checkForget()
    ll=GetRecordStatus()
    d={'states':ll}
    return render(request,'ForgetAtt_list.html',
                                                    {'ForgetAtt_list': dumps(d),
                                                    'from': 1,
                                                    'page': 1,
                                                    'limit': 10,
                                                    'item_count': 4,
                                                    'page_count': 1,
                                                    'iclock_url_rel': request.user.iclock_url_rel,
                                                    })

@permission_required("iclock.browse_user_of_run")
def searchShifts(request):
    request.user.iclock_url_rel='../..'
    request.model = transactions
    return render(request,'search_shifts.html',
                                                    {
                                                    'from': 1,
                                                    'page': 1,
                                                    'limit': 10,
                                                    'item_count': 4,
                                                    'page_count': 1,
                                                    'iclock_url_rel': request.user.iclock_url_rel,
                                                    })

@permission_required("iclock.browse_fptemp")
def fpfaceManage(request):
    request.user.iclock_url_rel='../..'
    request.model = transactions
    return render(request,'fpfacetemp.html',
                                                     {
                                                    'from': 1,
                                                    'page': 1,
                                                    'limit': 10,
                                                    'item_count': 4,
                                                    'page_count': 1,
                                                    'iclock_url_rel': request.user.iclock_url_rel,
                                                    })



@permission_required("iclock.add_user_of_run")
def deleteTmpShifts(request):
    request.user.iclock_url_rel='../..'
    request.model = transactions
    return render(request,'delete_tmpshifts.html',
                                                    {
                                                    'from': 1,
                                                    'page': 1,
                                                    'limit': 10,
                                                    'item_count': 4,
                                                    'page_count': 1,
                                                    'iclock_url_rel': request.user.iclock_url_rel,
                                                    })


@login_required
def     clearUserDefinedRep():                  #清除所有自定义报表
    pass

@login_required
def deleteAddTrans(request):    #删除补的考勤记录
    ids=request.POST.get("ids").split(',')
    for i in ids:
        sql="delete from %s where id=%s"%(transactions._meta.db_table,int(i))
        ret=customSql(sql)
    adminLog(time=datetime.datetime.now(),User=request.user, model=u"%s"%transactions._meta.verbose_name,action=_(u"Delete add transaction"),object=request.META["REMOTE_ADDR"],count=len(ids)).save(force_insert = True)#
    if ret!=None:
        return getJSResponse({"ret":0,"message":""})
    else:
        return getJSResponse({"ret":1,"message":u"%s" % _('Delete fail!')})
@login_required
def checkUsrName(request):
    User=get_user_model()

    usrname=request.POST.get("usrname")
    isexist=User.objects.all().filter(username=usrname)
    if isexist:
        return getJSResponse({"ret":1,"message":""})
    else:
        return getJSResponse({"ret":0,"message":""})


def forgotpassword(request):
    if request.method=="POST":
        User=get_user_model()

        username=request.POST.get("username")
        email=request.POST.get("email")
        try:
            u=User.objects.get(username=username)
        except:
            return getJSResponse({"ret":2,"message":u"%s"%_("The user name does not exist")})
        if email==u.email:
            try:
                url=request.META['HTTP_REFERER']
                index=url.find('?')
                if index>0:
                    url=url[:index+1]

                url='%s?sessionid=%s&username=%s'%(url,u.password,u.username)
                mail = SendMail(u"%s"%_('Reset Password'),'email/forgotpwd.html',{'url':url,'sitetitle':GetParamValue('opt_basic_sitetitle',u"%s"%_('ZKNet Attendance Data Manage System'))},[email],from_addr_name=u"%s"%_(u'时间&安全精细化管理平台'))
                mail.send_mail()
                adminLog(time=datetime.datetime.now(),User=request.user, model=_(u"SendEmail"),action=_(u"SendEmail"),object=u"%s"%u).save(force_insert = True)#

                mes=u"%s"%_("We've e-mailed you instructions for setting your password to the e-mail address you submitted. You should be receiving it shortly.")
                return getJSResponse({"ret":0,"message":mes})
            except Exception,e:
                return getJSResponse({"ret":1,"message":u"%s--%s"%(_("Send Failed"),e)})

            #发送email
        else:
            return getJSResponse({"ret":1,"message":"The user name does not exist"})
    else:
        pass

def get_Parameters(request):
    field_names = ['userids','deptids','isContainedChild','isAudit','reson','checktype','checktime','checkdate_a','checkdate_bs','checkdate_b']
    dicts = {}.fromkeys(field_names, 'null')
    dicts["userids"] = request.POST.get('UserIDs','')
    dicts["deptids"] = request.POST.get('deptIDs','')
    dicts["isContainedChild"] = request.POST.get('isContainChild',"0")
    dicts["isAudit"] = 1
    dicts["reson"] = request.POST.get('reson','')
    dicts["checktype"] = request.POST.get('checktype','')
    dicts["checkdate_bs"] = request.POST.get('id_checkdate_bs','')#是否勾选结束日期

    checkdate_a = request.POST.get('checkdate_a','')#开始日期
    checkdate_b = request.POST.get('checkdate_b','')#结束日期
    checktime = request.POST.get('checktime','')

    dicts["checkdate_a"] = datetime.datetime.strptime(checkdate_a,'%Y-%m-%d')
    if checkdate_b:
        dicts["checkdate_b"] = datetime.datetime.strptime(checkdate_b,'%Y-%m-%d')

    if checktime and len(checktime.split(':')) < 3:
        checktime += ":00"
        #checktime =checktime
    checktimes = datetime.datetime.strptime(checktime,'%H:%M:%S')
    dicts["checktime"] = checktimes
    return dicts


@login_required
def saveCheckForget(request,key):
    id=key
    s=''
    c=0
    j=0
    cache.set("%s_logstamp_" % (settings.UNIT), str(datetime.datetime.now()),timeout=10*60)
    if id=='_new_':
        try:
            parameters = get_Parameters(request)#参数字典
        except:
            return getJSResponse({"ret":1,"message":u"%s" % _(u'时间格式不支持！')})

        first_name=u'%s %s'%(request.user.username,request.user.first_name)
        if parameters['checkdate_bs'] == '1':
            if not allowAction(parameters['checkdate_b'],3):
                return getJSResponse({"ret":1,"message":u"%s" % _('Save Fail,account has been locked!')})
        if not allowAction(parameters['checkdate_a'],3):
            return getJSResponse({"ret":1,"message":u"%s" % _('Save Fail,account has been locked!')})
        if parameters['userids']=='':
            deptidlist=[int(i) for i in parameters['deptids'].split(',')]
            deptids=deptidlist
            if parameters['isContainedChild']=="1":   #是否包含下级部门
                deptids=[]
                if 1 not in deptidlist:
                    for d in deptidlist:#支持选择多部门
                        if int(d) not in deptids :
                            deptids+=getAllAuthChildDept(d,request)
                    uids=employee.objects.filter(DeptID__in=deptids).exclude(OffDuty=1).exclude(DelTag=1).values_list('id', flat=True).order_by('id')
                else:
                    uids=employee.objects.all().exclude(OffDuty=1).exclude(DelTag=1).values_list('id', flat=True).order_by('id')
            else:
                uids=employee.objects.filter(DeptID__in=deptids).exclude(OffDuty=1).exclude(DelTag=1).values_list('id', flat=True).order_by('id')
        else:
            uids=map(int,parameters['userids'].split(','))
        state=2
        if parameters['isAudit']==1:
            state=0
        c=len(uids)
        for i in uids:
            uid=int(i)
            did=employee.objByID(uid).DeptID_id
            print did
            proc,pid=getprocess_EX(uid,10001,1)
            if len(proc)==0:
                roleid=0
                process=''
            else:
                roleid=proc[0]
                process=','.join(str(x) for x in proc)
                process=','+process+','
            try:
                checkdate_a=parameters['checkdate_a']
                checkdate_b=parameters['checkdate_b']
                checktimes = parameters['checktime']

                checktypes = parameters['checktype']
                resons = parameters['reson']
                SN=request.POST.get('SN')
                pp=9
                if SN:
                    SN=SN
                    device=getDevice(SN)
                    pp=device.ProductType
                else:
                    SN=None
                    pp=9
                time_check=datetime.datetime.now()
                time_check=datetime.datetime(time_check.year,time_check.month,time_check.day,time_check.hour,time_check.minute,time_check.second)
                if parameters['checkdate_bs'] == '1':#批量
                    if checkdate_a >time_check or (checkdate_b!='null' and checkdate_b >time_check):
                        return getJSResponse({"ret":0,"message":u'保存失败!补签时间大于当前时间'})
                    if checkdate_b!='null' and checkdate_a > checkdate_b:
                        return getJSResponse({"ret":0,"message":u'保存失败!结束日期大于开始日期.'})
                    while (checkdate_b!='null' and checkdate_a <= checkdate_b):
                        checktime_a = datetime.datetime(checkdate_a.year,checkdate_a.month,checkdate_a.day,checktimes.hour,checktimes.minute,checktimes.second)
                        checktimes = datetime.datetime(checkdate_a.year,checkdate_a.month,checkdate_a.day,checktimes.hour,checktimes.minute,checktimes.second)
                        #sql_a,params_a=getSQL_insert_new(checkexact._meta.db_table,UserID=uid, CHECKTIME=checktime_a, CHECKTYPE=checktypes, YUYIN=resons,MODIFYBY=first_name,APPLYDATE=datetime.datetime.now(),SaveStamp=datetime.datetime.now(),STATE=state,SN=SN,)
                        #customSqlEx(sql_a,params_a)
#                         st = trunc(checktimes)
#                         et=trunc(checktimes+datetime.timedelta(days=1))
#                         print '33333333333333',st
#                         print '444444444444444444',et
#                         emp=employee.objByID(uid)
#                         schedules=GetUserScheduler(emp, st, et,False)
#                         print '22222222222',schedules
#                         for sch in schedules:
#                             dt=sch['TimeZone']['StartTime']
#                             dt1=sch['TimeZone']['EndTime']
#                             print '777777777777888888888',dt
#                             print '99999999900000000',dt1
                        if  trunc(checktimes)==trunc(datetime.datetime.now()):
                            sql_as,params_as=getSQL_insert_new(transactions._meta.db_table,userid=uid, checktime=checktime_a, checktype=checktypes, verifycode='5',purpose =pp,SN=SN)
                            try:
                                customSql(sql_as,params_as)
                            except:pass
                            if not settings.PIRELLI:
                                sql_a,params_a=getSQL_insert_new(checkexact._meta.db_table,UserID=uid, CHECKTIME=checktimes, CHECKTYPE=checktypes, YUYIN=resons,MODIFYBY=first_name,ApplyDate=datetime.datetime.now(),State=2,SN=SN,roleid=roleid,process=process,processid=pid,procSN=0,deptid=did)
                                try:
                                    customSql(sql_a,params_a)
                                except:pass
                        else:
                            sql_a,params_a=getSQL_insert_new(checkexact._meta.db_table,UserID=uid, CHECKTIME=checktime_a, CHECKTYPE=checktypes, YUYIN=resons,MODIFYBY=first_name,ApplyDate=datetime.datetime.now(),State=0,SN=SN,roleid=roleid,process=process,processid=pid,procSN=0,deptid=did)
                            try:
                                customSql(sql_a,params_a)
                            except:pass
                        checkdate_a += datetime.timedelta(days=1)
                    deleteCalcLog(UserID=uid,StartDate=parameters['checkdate_a'],EndDate=parameters['checkdate_b'])
                else:#单天
                    if checkdate_a >time_check or (checkdate_b!='null' and checkdate_b >time_check):
                        return getJSResponse({"ret":0,"message":u'保存失败!补签时间大于当前时间'})
                    checktimes = datetime.datetime(checkdate_a.year,checkdate_a.month,checkdate_a.day,checktimes.hour,checktimes.minute,checktimes.second)
                    if trunc(checktimes)==trunc(datetime.datetime.now()):
                        sql_b,params_b=getSQL_insert_new(transactions._meta.db_table,userid=uid, checktime=checktimes, checktype=checktypes, verifycode='5',purpose = pp,SN=SN)
                        customSqlEx(sql_b,params_b)
                        if not settings.PIRELLI:
                            sql_a,params_a=getSQL_insert_new(checkexact._meta.db_table,UserID=uid, CHECKTIME=checktimes, CHECKTYPE=checktypes, YUYIN=resons,MODIFYBY=first_name,ApplyDate=datetime.datetime.now(),State=2,SN=SN,roleid=roleid,process=process,processid=pid,procSN=0,deptid=did)
                            customSqlEx(sql_a,params_a)
                    else:
                        sql_a,params_a=getSQL_insert_new(checkexact._meta.db_table,UserID=uid, CHECKTIME=checktimes, CHECKTYPE=checktypes, YUYIN=resons,MODIFYBY=first_name,ApplyDate=datetime.datetime.now(),State=0,SN=SN,roleid=roleid,process=process,processid=pid,procSN=0,deptid=did)
                        customSqlEx(sql_a,params_a)
                    deleteCalcLog(UserID=uid,StartDate=parameters['checkdate_a'],EndDate=parameters['checkdate_a'])
                j += 1
            except Exception,e:
                connection.commit()
                print e
                pass
        if c-j == 0:
            s=u"成功保存:%s人" % j
        else:
            s=u"成功保存:%s人,失败:%s人"%(j,c-j)
    else:
        try:
            user_id = request.POST.get('UserID')
            proc,pid=getprocess_EX(user_id,10001,1)
            if len(proc)==0:
                roleid=0
                process=''
            else:
                roleid=proc[0]
                process=','.join(str(x) for x in proc)
                process=','+process+','
            checktime=request.POST.get('CHECKTIME')
            nt=datetime.datetime.strptime(checktime,'%Y-%m-%d %H:%M:%S')
            ct=request.POST.get('CHECKTYPE','I')#ATTSTATES[int(request.POST.get('checktype'))][0]
            reason=request.POST.get('YUYIN')
            ll = {'whereid': id, 'CHECKTIME': nt, 'CHECKTYPE': ct, 'ApplyDate': datetime.datetime.now(),'YUYIN': reason, 'roleid': roleid, 'process': process, 'processid': pid, 'procSN': 0}
            sql,params=getSQL_update_new(checkexact._meta.db_table,ll)
            customSqlEx(sql,params)
            #lls={'whereuserid':user_id,'wherechecktime':nt,'checktype':ct}
            #sql,params=getSQL_update_new(transactions._meta.db_table,lls)
            #customSqlEx(sql,params)
            deleteCalcLog(UserID=user_id,StartDate=nt,EndDate=nt)
        except Exception,e:
            connection.commit()
            s=u"保存失败:可能因为数据重复!"
            #print "------",e
            #pass
    cache.set("%s_logstamp_"%(settings.UNIT),datetime.datetime.now())
    adminLog(time=datetime.datetime.now(),User=request.user, model=u"%s"%checkexact._meta.verbose_name,action=_(u"Add"),object=_(u"Transaction Modify Records"),count=c).save(force_insert = True)
    return getJSResponse({"ret":0,"message":u'%s' % s})

@login_required
def saveFields(request):
    u=request.user
    f=request.POST.get('Fields','')
    tblName=request.POST.get('tblName','')
    item=None
    try:
        item=ItemDefine.objects.get(Author=u,ItemName=tblName,ItemType='report_fields_define')
    except:
        if f!="":
            item=ItemDefine(Author=u,ItemName=tblName,ItemType='report_fields_define')
    if f!="":
        #item=ItemDefine(Author=u,ItemName=tblName,ItemType='report_fields_define',ItemValue=f)
        item.ItemValue=f
        item.save()
    else:
        if item:
            item.delete()
    return getJSResponse({"ret":0,"message":""})

#假类统计
@login_required
def calcLeaveReport(request):
    if request.method=="GET":
        r,FieldNames,FieldCaption=ConstructLeaveFieldsEx()
        disabledCols=FetchDisabledFields(request.user,'calcLeaveReport')
        rs=[]
        it=0
        for field in FieldNames:
            if field.upper()=='USERID':
                rs.append({"name":""+field,'hidden':True})
            elif field.upper()=='DEPTID':
                rs.append({"name":""+field,'sortable':False,'label':_('department name'),'width':120})
            else:
                rs.append({"name":""+field,'sortable':False,'label':unicode(''+FieldCaption[it]),'width':80})
            it+=1
        r="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(rs)+"""}"""
        return getJSResponse(r)
    else:
        deptIDs=request.GET.get('deptIDs',"")
        userIDs=request.GET.get('UserIDs',"")
        st=request.GET.get('startDate','')
        et=request.GET.get('endDate','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')

        r=CalcLeaveReportItem(request,deptIDs,userIDs,st,et)
        rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
        return getJSResponse(rs)

#班次详情
@login_required
def calcAttShiftsReport(request):
    if request.method=="GET":
        fieldNames,fieldCaptions,rt=ConstructAttshiftsFields1()
        disabledCols=FetchDisabledFields(request.user,'calcAttShiftsReport')
        r=[]
        it=0
        for field in fieldNames:
            if field=='userid' or field=='UserID':
                r.append({"name":"UserID",'hidden':True})
            elif field=='DeptID':
                r.append({"name":field,'sortable':False,'label':_('department name'),'width':120})
            elif field=='SSpeDayHolidayOT':
                r.append({"name":field,'sortable':False,'label':_('SSpeDayHolidayOT'),'width':150})

            else:
                r.append({"name":field,'sortable':False,'label':fieldCaptions[it],'width':60})
            it=it+1
        rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
        return getJSResponse(rs)
    else:
        deptIDs=request.GET.get('deptIDs',"")
        userIDs=request.GET.get('UserIDs',"")
        st=request.GET.get('startDate','')
        et=request.GET.get('endDate','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')

        r=CalcAttShiftsReportItem(request,deptIDs,userIDs,st,et)
        rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
        return getJSResponse(rs)

#考勤统计汇总
@login_required
def calcReport(request):
    if request.method=="GET":
        rt,fieldNames,fieldCaptions=ConstructFields()
        disabledCols=FetchDisabledFields(request.user,'calcReport')
        r=[]
        it=0
        for field in fieldNames:
            if field=='userid' or field=='UserID':
                r.append({"name":""+field,'hidden':True})
            elif field=='DeptID' or field=='deptid':
                r.append({"name":""+field,'sortable':False,'label':_('department name'),'width':120})
            elif field=='SSpeDayHolidayOT':
                r.append({"name":field,'sortable':False,'label':_('SSpeDayHolidayOT'),'width':150})
            else:
                r.append({"name":""+field,'sortable':False,'label':unicode(''+fieldCaptions[it]),'width':60})
            it+=1

        rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
        return getJSResponse(rs)
    else:
        deptIDs=request.GET.get('deptIDs',"")
        userIDs=request.GET.get('UserIDs',"")
        st=request.GET.get('startDate','')
        et=request.GET.get('endDate','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        r=CalcReportItem(request,deptIDs,userIDs,st,et)

        rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
        return getJSResponse(rs)


#部门统计汇总
@login_required
def department_report(request):
    AbnomiteRptItems=GetLeaveClasses()
    AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
    if request.method=="GET":
        fieldNames=['dept','count','duty','realduty','absent','late','early','timeout','speday','gongchu','noin','noout','yingqian']
        fieldTitle=[u'%s'%_(u'部门'),u'%s'%_(u'人数')]#,_(u'工作日'),_(u'工作日'),_(u'次'),_(u'次'),_(u'次'),_(u'小时'),_(u'次'),_(u'小时'),_(u'次'),_(u'次'),_(u'次')]
        fieldCaptions=[u'%s'%_(u'部门'),u'%s'%_(u'人数'),u'%s'%_('duty'),u'%s'%_('realduty'),u'%s'%_('absent'),u'%s'%_('late'),u'%s'%_('early'),u'%s'%_(u'加班'),u'%s'%_(u'请假'),u'%s'%_(u'公出'),u'%s'%_('noin'),u'%s'%_('noout'),u'%s'%_(u'应签次数')]
        disabledCols=FetchDisabledFields(request.user,'department_report')
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1000)+"</span>")
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1000)+"</span>")
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1004)+"</span>")
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1001)+"</span>")
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1002)+"</span>")
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1005)+"</span>")
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1003)+"</span>")
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1)+"</span>")
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1008)+"</span>")
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,1009)+"</span>")
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+_(u"次")+"</span>")
        r=[]
        it=0
        LClasses1=GetLeaveClasses(1)
        for t in LClasses1:
            if t['LeaveID']==1:
                continue
            fName='Leave_'+str(t['LeaveID'])
            fieldNames.append(fName)
            fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,t['LeaveID'])+"</span>")
            fieldCaptions.append(t['LeaveName'])
        fieldNames.append('shijian')
        fieldNames.append('chuqinlv')
        fieldTitle.append("<span style='font-size:11px;font-weight:normal'>"+_(u'小时')+"</span>")
        fieldTitle.append(u'%s'%_(u'出勤率 %'))
        fieldCaptions.append(u'%s'%_(u'工作时间'))
        fieldCaptions.append(u'%s'%_(u'出勤率\n%'))
        for field in fieldNames:
            if field=='dept' :
                r.append({"name":""+field,'sortable':False,'label':unicode(''+fieldTitle[it]),'width':120})
            else:
                r.append({"name":""+field,'sortable':False,'label':unicode(''+fieldTitle[it]),'width':60})
            it+=1
        HeaderNames=[]
        io=0
        for f in fieldNames:
            if f not in ['dept','count','chuqinlv']:
                HeaderNames.append({'startColumnName': f, 'numberOfColumns': 1, 'titleText': fieldCaptions[io]})
            io+=1
        rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+","+""""groupHeaders":"""+dumps(HeaderNames)+"""}"""
        return getJSResponse(rs)
    else:
        deptIDs=request.GET.get('deptIDs',"")
        isContainChild=request.GET.get('isContainChild',"")
        st=request.GET.get('startDate','')
        et=request.GET.get('endDate','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        r=departmentreportItem(request,deptIDs,isContainChild,st,et)
        try:
            rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
        except Exception,e:
            print e
        return getJSResponse(rs)

def getdepttitle(AbnomiteRptItems,AttAbnomiteRptIndex,exceptid):
    Unit=AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['Unit']
    if Unit==2:
        return u'%s'%_(u"分钟")
    elif Unit==1:
        return u'%s'%_(u"小时")
    elif Unit==3:
        return u'%s'%_(u"工作日")
    elif Unit==4:
        return u'%s'%_(u"次")

def departmentreportItem(request,deptIDs,isContainChild,st,et):
    q=request.GET.get('q','')
    q=unquote(q)
    if q!='':
        depts=department.objects.filter(Q(DeptNumber=q)|Q(DeptName=q)).values_list("DeptID",flat=True).order_by('DeptNumber')
        if request.user.is_superuser or request.user.is_alldept:
            deptids=depts
        else:
            deptids=userDeptList(request.user)
        deptidlist=[]
        for dept in depts:
            if dept in deptids:
                deptidlist.append(dept)
    elif type(deptIDs)==list:
        deptidlist=deptIDs
        deptIDs=','.join(deptIDs)
    elif deptIDs == '':
        if request.user.is_superuser or request.user.is_alldept:
            deptidlist=list(department.objects.all().exclude(DelTag=1).values_list('DeptID',flat=True).order_by('DeptNumber'))
        else:
            deptidlist=userDeptList(request.user)
    else:
        deptidlist=[int(i) for i in deptIDs.split(',')]
    depts=[]
    if isContainChild=="1":   #是否包含下级部门
        for d in deptidlist:#支持选择多部门
            if int(d) not in depts:
                depts+=getAllAuthChildDept(d,request)
    else:
        depts=copy.deepcopy(deptidlist)
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset=1
    limit = int(request.GET.get('rows', 30))
    r={}
    r['item_count']=len(depts)
    page_count =int(ceil(len(depts)/float(limit)))
    depts=depts[(offset-1)*limit:offset*limit]
    r['page_count']=page_count
    r['page']=offset
    r['limit']=limit
    lx=[]
    rl=CalcReportItem(request,deptIDs,'',st,et,0,100000)
    dets={}
    LClasses1=GetLeaveClasses(2)
    for t in rl['datas']:
        if not t['deptid_id']:
            continue
        if t['duty']:
            try:
                dets['%s_duty'%t['deptid_id']]+=float(t['duty'])
            except:
                dets['%s_duty'%t['deptid_id']]=float(t['duty'])
        if t['realduty']:
            try:
                dets['%s_realduty'%t['deptid_id']]+=float(t['realduty'])
            except:
                dets['%s_realduty'%t['deptid_id']]=float(t['realduty'])
        if t['absent']:
            try:
                dets['%s_Absent'%t['deptid_id']]+=float(t['absent'])
            except:
                dets['%s_Absent'%t['deptid_id']]=float(t['absent'])
        if t['late']:
            try:
                dets['%s_Late'%t['deptid_id']]+=float(t['late'])
            except:
                dets['%s_Late'%t['deptid_id']]=float(t['late'])
        if t['early']:
            try:
                dets['%s_Early'%t['deptid_id']]+=float(t['early'])
            except:
                dets['%s_Early'%t['deptid_id']]=float(t['early'])
        if t['overtime']:
            try:
                dets['%s_OverTime'%t['deptid_id']]+=float(t['overtime'])
            except:
                dets['%s_OverTime'%t['deptid_id']]=float(t['overtime'])
        if t['noin']:
            try:
                dets['%s_noin'%t['deptid_id']]+=float(t['noin'])
            except:
                dets['%s_noin'%t['deptid_id']]=float(t['noin'])
        if t['noout']:
            try:
                dets['%s_noout'%t['deptid_id']]+=float(t['noout'])
            except:
                dets['%s_noout'%t['deptid_id']]=float(t['noout'])
        if t['dutyinout']:
            try:
                dets['%s_dutyinout'%t['deptid_id']]+=float(t['dutyinout'])
            except:
                dets['%s_dutyinout'%t['deptid_id']]=float(t['dutyinout'])
        if t['worktime_de']:
            try:
                dets['%s_worktime'%t['deptid_id']]+=float(t['worktime_de'])
            except:
                dets['%s_worktime'%t['deptid_id']]=float(t['worktime_de'])
        if t['Leave']:
            try:
                dets['%s_Leave'%t['deptid_id']]+=float(t['Leave'])
            except:
                dets['%s_Leave'%t['deptid_id']]=float(t['Leave'])

        for t1 in LClasses1:
            fName='Leave_'+str(t1['LeaveID'])
            if t[fName]:
                try:
                    dets['%s_%s'%(t['deptid_id'],fName)]+=float(t[fName])
                except:
                    dets['%s_%s'%(t['deptid_id'],fName)]=float(t[fName])
    for d in depts:
        ll={}
        ll['dept']=department.objByID(d).DeptName
        ll['count']=employee.objects.filter(DeptID=d,OffDuty=0,DelTag=0).count()
        try:
            ll['duty']=dets['%s_duty'%d]
        except:
            ll['duty']=''
        try:
            ll['realduty']=dets['%s_realduty'%d]
        except:
            ll['realduty']=''
        try:
            ll['absent']=dets['%s_Absent'%d]
        except:
            ll['absent']=''
        try:
            ll['late']=dets['%s_Late'%d]
        except:
            ll['late']=''
        try:
            ll['early']=dets['%s_Early'%d]
        except:
            ll['early']=''
        try:
            ll['timeout']=dets['%s_OverTime'%d]
        except:
            ll['timeout']=''
        try:
            ll['noin']=dets['%s_noin'%d]
        except:
            ll['noin']=''
        try:
            ll['noout']=dets['%s_noout'%d]
        except:
            ll['noout']=''
        try:
            ll['yingqian']=dets['%s_dutyinout'%d]
        except:
            ll['yingqian']=''
        try:
            ll['shijian']=formatdTime(dets['%s_worktime'%d])
        except:
            ll['shijian']=''
        try:
            ll['speday']=dets['%s_Leave'%d]
        except:
            ll['speday']=''
        for t in LClasses1:
            fName='Leave_'+str(t['LeaveID'])
            try:
                ll[fName]=dets['%s_%s'%(d,str(fName))]
            except:
                ll[fName]=''
        if ll['realduty'] and ll['duty'] and ll['duty']!=0:
            ll['chuqinlv']='%.1f'%(ll['realduty']*100/ll['duty'])
        lx.append(ll)
    r['datas']=lx
    return r

def changeUnitforDay(value):
    param=GetParamValue('1005')
    min=int(GetParamValue('MinsWorkDay'))
    if param==1 or param=='1':
        return float(value)*60/min
    if param==2 or param=='2':
        return float(value)/min
    if param==3 or param=='3':
        return float(value)

@login_required
def calcPriReport(request):
    if request.method=="POST":
        deptIDs=request.POST.get('deptIDs',"")
        userIDs=request.POST.get('UserIDs',"")
        st=request.POST.get('ComeTime','')
        et=request.POST.get('EndTime','')
        isforce=request.POST.get('isForce','1')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        isContainedChild=request.POST.get('isContainChild',"")

        deptids=[]
        userids=[]
        if userIDs == "":
            if isContainedChild=="1":
                deptids=getAllAuthChildDept(int(deptIDs),request)
            else:
                deptids=deptIDs.split(',')
        else:
            userids=userIDs.split(',')


        if userids or deptids:
            t1=datetime.datetime.now()
            re=PriReportCalc(userids,deptids,st,et,int(isforce))
            t2=datetime.datetime.now()-t1
            if re==-3:
                r=getJSResponse({"ret":-3,"message":""})
            elif re==-4:
                r=getJSResponse({"ret":0,"message":u"%s" % _("account has been locked!")})
            else:
                r=getJSResponse({"ret":0,"message":u"%s" % (_('Calculate Succes'),_('Total Time'),t2.seconds,_('Seconds'))})
        else:
            r=getJSResponse({"ret":1,"message":""})
        return r

#每日考勤统计表
@login_required
def dailycalcReport(request):
    if request.method=="GET":
        st=request.GET.get('startDate','')
        et=request.GET.get('endDate','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        rt,fieldNames,fieldCaptions=ConstructFields1(st,et)
        disabledCols=FetchDisabledFields(request.user,'dailycalcReport')
        r=[]
        it=0
        for field in fieldNames:
            if field=='userid' or field=='UserID':
                r.append({"name":""+field,'hidden':True})
            elif field=='DeptID':
                r.append({"name":""+field,'sortable':False,'label':_('department name'),'width':120})
            elif field=='SSpeDayHolidayOT':
                r.append({"name":field,'sortable':False,'label':_('SSpeDayHolidayOT'),'width':150})
            else:
                r.append({"name":""+field,'sortable':False,'label':unicode(''+fieldCaptions[it]),'width':60})
            it+=1

        rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
        return getJSResponse(rs)
    else:
        deptIDs=request.GET.get('deptIDs',"")
        userIDs=request.GET.get('UserIDs',"")
        st=request.GET.get('startDate','')
        et=request.GET.get('endDate','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        r=CalcReportItem(request,deptIDs,userIDs,st,et,1)
        rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
        return getJSResponse(rs)
def getLocal(fin,k):
    i=0
    for kk in fin:
        if k ==kk:
            return i
        i+=1
def cacleExcepDaily(request,data,exp=0):
    r={}
    fd=data['datas']
    fis=data['fieldcaptions']
    fin=data['fieldnames']
#       print 1111,fis,data['fieldnames'],fd
    flist=[]
    dif={}
    lc,ec,sc,pc,exc,ac=0,0,0,0,0,0
    for f in fd:
        dd={}
        ee=[]
        flag=0
        aflag=0
        i=0

        dd['deptid']=f['deptid']
        dd['badgenumber']=f['badgenumber']
        dd['username']=f['username']
        dd['AttDate']=f['AttDate']
        dd['schid']=f['schid']
        for k,v in f.items():
            if k  in ['deptid','badgenumber','schid','AttDate','username','ssn','overtime','duty','Leave','realduty','SSpeDayHoliday','SSpeDayNormalOT','SSpeDayWeekendOT','SSpeDayHolidayOT','userid']:
                continue
            elif k  in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']:
                continue
            else:
#                               print 88899,k,v
                if v !='' and v!=None:
                    if k =='late':
                        lc+=1
                    elif k =='early':
                        ec+=1
                    elif k =='absent':
                        ac+=1
                    ex=fis[getLocal(fin,k)]
                    if ex in [_('Sick leave'),]:
                        sc+=1
                    elif ex in [_('Private affair leave'),]:
                        pc+=1
                    elif k not in ['late','early','absent']:
                        exc+=1

                    dd['exception']=ex
                    dd['times']=v
                    dd['memo']=''
                    dc={}
                    dc=copy.deepcopy(dd)
                    flist.append(dc)
    fc=[_('NO.'),_('department name'),_('PIN'),_('EName'),_('AttDate'),_('SchId'),_('Exception'),_('time'),_('Notes')]
    fn=['deptid','badgenumber', 'username', 'AttDate', 'schid','exception','times','memo']
#       print 99999,lc,ec,sc,pc,exc
    r['disableCols']=[]
    #分页
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset=1
    if exp:
        r['late']=lc
        r['early']=ec
        r['sick']=sc
        r['Private']=pc
        r['absent']=ac
        r['other']=exc
        r['datas']=flist
        r['fieldcaptions']=fc
        r['fieldnames']=fn
        return r
#       limit= int(settings.PAGE_LIMIT)  #导出时使用
    limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
#       page_count =len(flist)/limit+1
    page_count =int(ceil(len(flist)/float(limit)))
    if offset>page_count:offset=page_count
    item_count =len(flist)
    uids=flist[(offset-1)*limit:offset*limit]
    k=0
    r['item_count']=item_count
    r['page']=offset
    r['limit']=limit
    r['from']=(offset-1)*limit+1
    r['page_count']=page_count
    r['datas']=uids
    r['fieldcaptions']=fc
    r['fieldnames']=fn

#       print 999,r
    return r




#异常考勤表
@login_required
def ExcepDaily(request):
    if request.method=="GET":
        deptIDs=request.GET.get('deptIDs',"")
        userIDs=request.GET.get('UserIDs',"")
        st=request.GET.get('startDate','')
        et=request.GET.get('endDate','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
#               rt,fieldNames,fieldCaptions=ConstructFields1(st,et)
        fieldCaptions=[_('department name'),_('PIN'),_('EName'),_('AttDate'),_('SchId'),_('Exception'),_('time'),_('Notes')]
        fieldNames=['deptid','badgenumber', 'username', 'AttDate', 'schid','exception','times','memo']

        disabledCols=FetchDisabledFields(request.user,'excep_att_report')
        r=[]
        it=0
        for field in fieldNames:
            if field=='userid' or field=='UserID':
                r.append({"name":""+field,'hidden':True})
            else:
                r.append({"name":""+field,'sortable':False,'label':unicode(''+fieldCaptions[it]),'width':100})
            it+=1

        rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
        return getJSResponse(rs)

    else:
        deptIDs=request.GET.get('deptIDs',"")
        userIDs=request.GET.get('UserIDs',"")
        st=request.GET.get('startDate','')
        et=request.GET.get('endDate','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        r=CalcReportItemEx(request,deptIDs,userIDs,st,et,3)
        r=cacleExcepDaily(request,r)
        rs="{"+""""page":"""+str(r['page'])+","+""""total":"""+str(r['page_count'])+","+""""records":"""+str(r['item_count'])+","+""""rows":"""+dumps(r['datas'])+"""}"""
        return getJSResponse(rs)





@permission_required("iclock.IclockDept_calcreports")
def reCaluate(request):
    request.user.iclock_url_rel='../..'
    request.model = transactions
    settings.PAGE_LIMIT=GetParamValue('opt_users_page_limit','50',request.user.id)
    limit= settings.PAGE_LIMIT


    return render(request,'CalcReports.html',{'limit':limit})
@login_required
def reCaluateAction(request):
    if request.method=="POST":
        deptIDs=request.POST.get('deptIDs',"")
        userIDs=request.POST.get('UserIDs',"")
        st=request.POST.get('ComeTime','')
        et=request.POST.get('EndTime','')
        isContainedChild=request.POST.get('isContainChild',"")
        logst=st
        loget=et
        isforce=request.POST.get('isForce','0')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        deptids=[]
        userids=[]
        isAllDept=0
        if userIDs == "":
            deptidlist=deptIDs.split(',')
            if isContainedChild=="1":
                for d in deptidlist:#支持选择多部门
                    if(request.user.is_superuser) or ( request.user.is_alldept):
                        if department.objByID(int(d)).parent==0:
                            isAllDept=1
                            deptids=[]
                            break
                    if int(d) not in deptids:
                        deptids+=getAllAuthChildDept(d,request)
            else:
                deptids=deptidlist
        else:
            userids=userIDs.split(',')
        if userids or deptids or isAllDept:
            t1=datetime.datetime.now()

            tempFile("job_calc_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),u'%s--手动统计开始，统计时间范围：%s至%s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),st.strftime("%Y-%m-%d"),et.strftime("%Y-%m-%d")))

            re=MainCalc(userids,deptids,st,et,int(isforce),isAllDept)
            t2=datetime.datetime.now()-t1

            tempFile("job_calc_%s.txt"%(datetime.datetime.now().strftime("%Y%m")),u'%s--手动统计结束，统计共%s人用时%s'%(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),re,t2))

            if re==-3:
                r=getJSResponse({"ret":0,"message":u"%s %s"%(_('Calculate Fail,The Ending Date should not more than'),t1.strftime('%Y-%m-%d'))})
            elif re==-4:
                r=getJSResponse({"ret":0,"message":u'%s'%_("account has been locked!")})
            elif re==-5:
                r=getJSResponse({"ret":0,"message":u'%s'%_("System is busy,please waiting!")})
            else:
                r=getJSResponse({"ret":0,"message":u"%s,%s:%s%s,%s:%s"%(_('Calculate Succes'),_('Total Time'),t2.seconds,_('Seconds'),_(u'总人数'),re)})
        else:
            r=getJSResponse({"ret":0,"message":u"%s,%s:%s%s,%s:%s"%(_('Calculate Succes'),_('Total Time'),0,_('Seconds'),_(u'总人数'),0)})
        #if userIDs == "":
            #try:
                #deptIDs=deptIDs.split(',')
                #userlist = employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
            #except:
                #pass
            #userIDs=",".join(["%s" % int(i) for i in userlist])
        #t1=datetime.datetime.now()
        #if len(userIDs)>0:
            #re=MainCalc(userIDs,st,et,1)
            #t2=datetime.datetime.now()-t1
            #if re==-3:
                #r=getJSResponse("result=-3")
            #else:
                #r=getJSResponse("result=0;message=%d sec"%(t2.seconds))
        #else:
            #r=getJSResponse("result=1")
        adminLog(time=datetime.datetime.now(),User=request.user, action=_(u"CalcReport"), object=request.META["REMOTE_ADDR"], model=u"%s %s"%(logst,loget)).save(force_insert = True)#
        return r

    else:
        action=request.GET.get('action')
        if action=='query':
            msg=cache.get('_iscalcing_')
            v=1
            if not msg:
                msg=[0,0]
            else:
                msg=msg.split('-')
                if int(msg[1])>0:
                    v=int(msg[0])*100/int(msg[1])
            r=getJSResponse({'ret':0,'c':msg[1],"n":msg[0],'message':v})
        elif action=='cancelCalc':
            cache.set('__cancelCalc__',1)
            r=getJSResponse({'ret':0,'message':''})

        return r

def saveUserACPrivliege(request,key):
    emp=request.POST.get('UserIDs')
    deptids=request.POST.get('DeptIDs')
    UserID=request.POST.get('UserID','')
    if UserID:
        t=employee.objects.get(id=UserID)
        tz1=request.POST.get('TimeZone1',0)
        tz2=request.POST.get('TimeZone2',0)
        tz3=request.POST.get('TimeZone3',0)
        acGroupId=request.POST.get('ACGroupID',1)
        isusergrp=request.POST.get('IsUseGroup',0)
    #       sn=request.POST.get('SNs').split(',')
        try:
            t.AccGroup=acGroupId
            t.save()
        except:
            pass
        #if acGroupId=='':
        #       acGroupId='1'
        if tz1=='':
            tz1=0
        if tz2=='':
            tz2=0
        if tz3=='':
            tz3=0
        uac=UserACPrivilege(UserID=t,ACGroupID_id=acGroupId,IsUseGroup=isusergrp,TimeZone1=tz1,TimeZone2=tz2,TimeZone3=tz3)
        uac.save()
        adminLog(time=datetime.datetime.now(),User=request.user, action=u'%s'%_(u"Change"), object=uac, model=UserACPrivilege._meta.verbose_name).save(force_insert = True)#

    else:
        isContainedChild=request.POST.get('isContainChild',"")
        if emp=='':
            deptidlist=[int(i) for i in deptids.split(',')]
            deptids=deptidlist
            if isContainedChild=="1":   #是否包含下级部门
                deptids=[]
                for d in deptidlist:#支持选择多部门
                    if int(d) not in deptids :
                        deptids+=getAllAuthChildDept(d,request)
            emps=employee.objects.filter(DeptID__in=deptids).values_list('id', flat=True).order_by('id')
        else:
            emps=emp.split(',')
        print "emps==",emps
            #emps=employee.objects.filter(id__in=emplist)
        tz1=request.POST.get('TimeZone1')
        tz2=request.POST.get('TimeZone2')
        tz3=request.POST.get('TimeZone3')
        acGroupId=request.POST.get('ACGroupID')
    #       sn=request.POST.get('SNs').split(',')
        isusergrp=0
        if acGroupId=='':
            acGroupId='1'
        if tz1=='0' and tz2=='0' and tz3=='0':
            isusergrp=1

        for t in emps:
            uac=UserACPrivilege(UserID_id=t,ACGroupID_id=acGroupId,IsUseGroup=isusergrp,TimeZone1=tz1,TimeZone2=tz2,TimeZone3=tz3)
            uac.save()
            try:
                ee=employee.objects.get(id=t)
                ee.AccGroup=acGroupId
                ee.save()
            except:
                pass
            adminLog(time=datetime.datetime.now(),User=request.user, action=_(u"Create"), object=uac, model=UserACPrivilege._meta.verbose_name).save(force_insert = True)#
            #for s in sn:
                #try:
                    #UserACMachines(UserID_id=t,SN_id=s).save()
                #except:
                    #pass

    return getJSResponse({"ret":0,"message":u'%s'%_("Save Success")})

@login_required
def saveOvertime(request,key):
    if request.method=="POST":
        id=key
        userids=request.POST.get('UserID','')
        if id=="_new_":
            userids=userids.split(',')
        st=request.POST.get('StartOTDay','')
        if len(st.split(':'))<3:
            st=st+":00"
        et=request.POST.get('EndOTDay','')
        if len(et.split(':'))<3:
            et=et+":00"
        at=request.POST.get('ApplyDate','')
        reson=request.POST.get('YUANYING','')
        AsMinute=request.POST.get('AsMinute','')
        st=datetime.datetime.strptime(st,"%Y-%m-%d %H:%M:%S")
        et=datetime.datetime.strptime(et,"%Y-%m-%d %H:%M:%S")
        minunit=float(AsMinute)
        min=float(GetParamValue('MinsWorkDay'))
        minunit=minunit/min
        if not allowAction(st,4,et):
            return getJSResponse("result=1;message=%s"%(_('Save Fail,account has been locked!')))
        try:
            if id=="_new_":
                for i in userids:
                    proc,pid=getprocess_EX(i,10000,minunit)
                    if len(proc)==0:
                        roleid=0
                        process=''
                    else:
                        roleid=proc[0]
                        process=','.join(map(str,proc))
                        process=','+process+','
                    sql,params=getSQL_insert_new(USER_OVERTIME._meta.db_table,UserID = int(i), StartOTDay=st, EndOTDay=et, YUANYING=reson,ApplyDate=at,AsMinute=AsMinute,State=0,roleid=roleid,process=process,processid=pid,procSN=0)
                    customSqlEx(sql,params)
                    #deleteCalcLog(UserID=i)
            else:
                uu=USER_OVERTIME.objects.get(id=id)
                proc,pid=getprocess_EX(uu.UserID_id,10000,minunit)
                if len(proc)==0:
                    roleid=0
                    process=''
                else:
                    roleid=proc[0]
                    process=','.join(map(str,proc))
                    process=','+process+','
                ll={'whereid':id,'StartOTDay':st,'EndOTDay':et,'YUANYING':reson,'ApplyDate':at,'AsMinute':AsMinute,'roleid':roleid,'process':process,'processid':pid,'procSN':0}
                sql,params=getSQL_update_new(USER_OVERTIME._meta.db_table,ll)
                customSqlEx(sql,params)
                #deleteCalcLog(UserID=int(userids))#审核后才用此功能
        except Exception,rr:
            connection.commit()
            # print rr
            return getJSResponse({"ret":1,"message":u'%s'%(_(u'加班已经申请!'))})
        return getJSResponse({"ret":0,"message":u'%s'%_("Save Success")})


@login_required
def savespecialday(request,key):
    if request.method=="POST":
        cache.delete("%s-%s"%(settings.UNIT,'home_user_speadays'))
        id=key
        userids=request.POST.get('UserID','')
        if id=="_new_":
            userids=userids.split(',')
        st=request.POST.get('StartSpecDay','')
        if len(st.split(':'))<3:
            st=st+":00"
        et=request.POST.get('EndSpecDay','')
        if len(et.split(':'))<3:
            et=et+":00"
        #at=request.POST.get('ApplyDate','')
        at=datetime.datetime.now()
        at = at.strftime('%Y-%m-%d %H:%M:%S')
        Place=request.POST.get('Place','')
        Place=Place.replace("\'","").replace("\"","")

        mobile=request.POST.get('mobile','')
        mobile=mobile.replace("\'","").replace("\"","")
        successor=request.POST.get('successor','')
        successor=successor.replace("\'","").replace("\"","")
        remarks=request.POST.get('remarks','')
        remarks=remarks.replace("\'","").replace("\"","")

        reson=request.POST.get('YUANYING','')
        #reson=reson.replace("\'","")
        #reson=reson.replace("\"","")

        dateid=request.POST.get('DateID','')
        clearance=request.POST.get('clearance','')
        st=datetime.datetime.strptime(st,"%Y-%m-%d %H:%M:%S")
        et=datetime.datetime.strptime(et,"%Y-%m-%d %H:%M:%S")
        fname=[]
        if not allowAction(st,2,et):
            return getJSResponse({"ret":1,"message":u'%s'%_('Save Fail,account has been locked!')})
        try:
            if GetParamValue('opt_basic_Auto_audit','0')=='0':#是否支持自动审核，如支持自动将状态改为已接受2
                state=0
            else:
                state=2
            if id=="_new_":
                for i in userids:
                    minunit=gettimediff(et,st)
                    #minunit=gettimediff_byshift(i,et,st)
                    proc,pid=getprocess_EX(i,dateid,minunit)
                    if len(proc)==0:
                        roleid=0
                        process=''
                    else:
                        roleid=proc[0]
                        process=','.join(str(x) for x in proc)
                        process=','+process+','

                    sql,params=getSQL_insert_new(USER_SPEDAY._meta.db_table,UserID=int(i), StartSpecDay=st, EndSpecDay=et, YUANYING=reson,ApplyDate=at,DateID=dateid,clearance=clearance,State=state,roleid=roleid,process=process,processid=pid,procSN=0,jiezhuang=0,tianshu=0)


                    #if settings.DATABASE_ENGINE == 'oracle':
                    #       sql="""insert into %s (UserID, StartSpecDay, EndSpecDay, YUANYING,"DATE",DateID,clearance,State,roleid,process) values('%s',  to_date('%s','YYYY-MM-DD HH24:MI:SS'), to_date('%s','YYYY-MM-DD HH24:MI:SS'), '%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'),'%s','%s','%s','%s','%s')""" % (USER_SPEDAY._meta.db_table, int(i),st,et,reson, at,dateid,clearance,state,roleid,process)
                    #else:
                    #       sql="""insert into %s (UserID, StartSpecDay, EndSpecDay, YUANYING,Date,DateID,clearance,State,roleid,process) values('%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s')""" % (USER_SPEDAY._meta.db_table, int(i), st, et,reson, at,dateid,clearance,state,roleid,process)



                    customSqlEx(sql,params)
                    uspe=USER_SPEDAY.objects.get(UserID=int(i),StartSpecDay=st,DateID=dateid)
                    ret = save_speday_file(request,fname,uspe.pk)
                    if ret:
                        return ret
                    fname = fname and fname[0] or ''
                    USER_SPEDAY_DETAILS(USER_SPEDAY_ID=uspe,remarks=remarks,Place=Place,mobile=mobile,successor=successor,file=fname).save()
                    #deleteCalcLog(UserID=i)#审核后才用此功能
            else:
                uu=USER_SPEDAY.objects.get(id=id)
                minunit=gettimediff(et,st)
                #minunit=gettimediff_byshift(id,et,st)
                proc,pid=getprocess_EX(uu.UserID_id,dateid,minunit)
                if len(proc)==0:
                    roleid=0
                    process=''
                else:
                    roleid=proc[0]
                    process=','.join(str(x) for x in proc)
                    process=','+process+','
                if 'oracle' in settings.DATABASE_ENGINE:
                    sql="""update %s set StartSpecDay=to_date('%s','YYYY-MM-DD HH24:MI:SS'),EndSpecDay=to_date('%s','YYYY-MM-DD HH24:MI:SS'),YUANYING='%s',ApplyDate=to_date('%s','YYYY-MM-DD HH24:MI:SS'),DateID='%s',clearance='%s',State='%s',roleid='%s',process='%s',processid='%s',procSN='0' where id=%s"""%(USER_SPEDAY._meta.db_table,st,et,reson,at,dateid,clearance,state,roleid,process,pid,id)
                else:
                    sql="update %s set StartSpecDay='%s',EndSpecDay='%s',YUANYING='%s',ApplyDate='%s',DateID='%s',clearance='%s',State='%s',roleid='%s',process='%s',processid='%s',procSN='0' where id=%s"%(USER_SPEDAY._meta.db_table,st,et,reson,at,dateid,clearance,state,roleid,process,pid,id)
                customSql(sql)
                try:
                    u_details=USER_SPEDAY_DETAILS.objByID(id)
                    ret = save_speday_file(request,fname,uu.pk)
                    if ret:
                        return ret
                    fname = fname and fname[0] or ''
                    if u_details:
                        tmp_file = u_details.file
                        u_details.remarks=remarks
                        u_details.Place=Place
                        u_details.mobile=mobile
                        u_details.successor=successor
                        u_details.file=fname
                        u_details.save()
                        if tmp_file!=fname:
                            path = '%s%s/'%(settings.ADDITION_FILE_ROOT,'userSpredyFile')
                            tmp_path = path+tmp_file
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                    else:
                        USER_SPEDAY_DETAILS(USER_SPEDAY_ID=uu,remarks=remarks,Place=Place,mobile=mobile,successor=successor,file=fname).save()
                except Exception,e:
                    pass
                    #print e
                #deleteCalcLog(UserID=int(userids))#审核后才用此功能
        except Exception,e:
            #print e
            return getJSResponse({"ret":1,"message":u'%s'%_('The specail has been applied!')})
        return getJSResponse({"ret":0,"message":u'%s'%_("Save Success")})

@login_required
def saveaddcontract(request,key):
    if request.method=="POST":
        id=key
        userids=request.POST.get('UserID','')
        if id=="_new_":
            userids=userids.split(',')
        st=request.POST.get('StartContractDay','')
        et=request.POST.get('EndContractDay','')
        at=request.POST.get('ApplyDate','')
        reson=request.POST.get('Notes','')
        State=request.POST.get('State',0)
        Type=request.POST.get('Type',0)
        st=datetime.datetime.strptime(st,"%Y-%m-%d")
        et=datetime.datetime.strptime(et,"%Y-%m-%d")

        try:
            if id=="_new_":
                for i in userids:
                    if 'oracle' in settings.DATABASE_ENGINE:
                        sql="""insert into %s (UserID, StartContractDay, EndContractDay, Notes,ApplyDate,State,Type) values('%s',  to_date('%s','YYYY-MM-DD HH24:MI:SS'), to_date('%s','YYYY-MM-DD HH24:MI:SS'), '%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'),'%s','%s')""" % (USER_CONTRACT._meta.db_table, int(i),st,et,reson, at,State,Type)
                    else:
                        sql="""insert into %s (UserID, StartContractDay, EndContractDay, Notes,ApplyDate,State,Type) values('%s', '%s', '%s', '%s','%s','%s','%s')""" % (USER_CONTRACT._meta.db_table, int(i), st, et,reson, at,State,Type)

                    customSql(sql)
                    empobj=employee.objByID(i)
                    empobj.Contractendtime=et
                    empobj.save()
        except Exception,ee:
            #print ee
            return getJSResponse({"ret":1,"message":u'%s'%_(u'该合同已经添加')})
        return getJSResponse({"ret":0,"message":u'%s'%_("Save Success")})


@login_required
def savedaysoff(request,key):
    if request.method=="POST":
        id=key
        deptids=request.POST.get('DeptID','')
        isContainedChild=request.POST.get('isContainChild',"")
        userids=request.POST.get('UserID','')
        if userids=='':
            if isContainedChild=="1":
                deptids=getAllAuthChildDept(int(deptids),request)
        if id=="_new_":
            userids=userids.split(',')
        st=request.POST.get('FromDate','')
        et=request.POST.get('ToDate','')
        at=request.POST.get('ApplyDate','')
        sts=st+" 00:00:00"
        ets=et+" 23:59:59"
        sts=datetime.datetime.strptime(sts,"%Y-%m-%d %H:%M:%S")
        ets=datetime.datetime.strptime(ets,"%Y-%m-%d %H:%M:%S")
        st=datetime.datetime.strptime(st,"%Y-%m-%d")
        et=datetime.datetime.strptime(et,"%Y-%m-%d")
        if not allowAction(sts,2,ets):
            return getJSResponse({"ret":1,"message":u'%s'%_('Save Fail,account has been locked!')})

        try:
            if id=="_new_":
                if userids==['']:
                    for i in deptids:
                        if 'oracle' in settings.DATABASE_ENGINE:
                            sql="""insert into %s (DeptID, FromDate, ToDate, ApplyDate) values('%s',to_date('%s','YYYY-MM-DD HH24:MI:SS'), to_date('%s','YYYY-MM-DD HH24:MI:SS'), to_date('%s','YYYY-MM-DD HH24:MI:SS'))""" % (days_off._meta.db_table, int(i),st,et, at)
                        else:
                            sql="""insert into %s (DeptID, FromDate, ToDate, ApplyDate) values('%s', '%s', '%s','%s')""" % (days_off._meta.db_table, int(i), st, et, at)
                        customSql(sql)
                        deleteCalcLog(DeptID=int(i),StartDate=st,EndDate=et)
                else:
                    for i in userids:
                        try:
                            shifts=GetScheduleTime(i,st,st,False,None)
                        except Exception,e:
                            import traceback;traceback.print_exc()
                        if not shifts:
                            return getJSResponse({"ret":1,"message":u'%s'%_(u'保存失败，调休日期没有班次!')})
                        shifts=GetScheduleTime(i,et,et,False,{})
                        if  shifts:
                            return getJSResponse({"ret":1,"message":u'%s'%_(u'保存失败，调至日期有班次!')})

                        emp=employee.objByID(int(i))
                        if 'oracle' in settings.DATABASE_ENGINE:
                            sql="""insert into %s (DeptID,UserID, FromDate, ToDate, ApplyDate) values('%s','%s',  to_date('%s','YYYY-MM-DD HH24:MI:SS'), to_date('%s','YYYY-MM-DD HH24:MI:SS'), to_date('%s','YYYY-MM-DD HH24:MI:SS'))""" % (days_off._meta.db_table, emp.Dept().DeptID,emp.id,st,et,at)
                        else:
                            sql="""insert into %s (DeptID,UserID, FromDate, ToDate, ApplyDate) values('%s', '%s', '%s', '%s','%s')""" % (days_off._meta.db_table, emp.Dept().DeptID,emp.id, st, et, at)
                        customSql(sql)
                        deleteCalcLog(UserID=int(i),StartDate=st,EndDate=et)
            else:
                if settings.DATABASE_ENGINE == 'oracle':
                    sql="""update %s set FromDate=to_date('%s','YYYY-MM-DD HH24:MI:SS'),ToDate=to_date('%s','YYYY-MM-DD HH24:MI:SS') where id=%s"""%(days_off._meta.db_table,st,et,id)
                else:
                    sql="update %s set FromDate='%s',ToDate='%s' where id=%s"%(days_off._meta.db_table,st,et,id)
                customSql(sql)
                u=days_off.objects.get(id=id)
                if u.UserID:
                    deleteCalcLog(UserID=u.UserID,StartDate=u.FromDate,EndDate=u.ToDate)
                else:
                    deleteCalcLog(DeptID=u.DeptID,StartDate=u.FromDate,EndDate=u.ToDate)
            InitData('days_off')
        except:
            return getJSResponse({"ret":1,"message":u'%s'%_('The specail has been applied!')})
        return getJSResponse({"ret":0,"message":u"%s"%_("Save Success")})

@login_required
def auditedTrans(request):
    try:
        id=int(request.POST['id'])
        rk=request.POST['remarks']
        sql="update %s set Reserved2='%s' where id=%s "%(transactions._meta.db_table,rk,id)
        customSql(sql)
        return getJSResponse({"ret":0,"message":""})
    except:
        return getJSResponse({"ret":1,"message":""})
@login_required
def deleteLeaveClass(request):
    id=request.GET.get('LeaveID','')
    if USER_SPEDAY.objects.filter(DateID=id).count()>0:
        return getJSResponse({"ret":1,"message":u"有正在使用的假类，无法删除"})
    try:
        leaveObj = LeaveClass.objects.filter(LeaveID = id)
        if leaveObj:
            LeaveNames = leaveObj[0].LeaveName
        else:
            LeaveNames = ''
    except:
        LeaveNames = ''
    #sql="delete from %s where LeaveId=%s"%(LeaveClass._meta.db_table, id)
    sql="update %s set deltag=1 where LeaveID=%s"%(LeaveClass._meta.db_table, id)
    customSql(sql)
    cache.delete("%s_LeaveClass_0"%(settings.UNIT))
    cache.delete("%s_LeaveClass_1"%(settings.UNIT))
    cache.delete("%s_LeaveClass_2"%(settings.UNIT))
    adminLog(time=datetime.datetime.now(),User=request.user,action=u'%s'%_(u'del'), model=LeaveClass._meta.verbose_name,object = LeaveNames).save(force_insert = True)#
    return getJSResponse({"ret":0,"message":""})
@login_required
def submitLeaveClass(request):
    if request.method=="POST":
        try:
            s=request.POST.get('LeaveClass','')
            LeaveName = request.POST.get('LeaveName','')
            l=loads(s)
            SaveLeaveClass(l,1)  #保存假类表
        except Exception,e:
            return getJSResponse({"ret":0,"message":u"保存假类失败，可能因计算单位未选择"})
        adminLog(time=datetime.datetime.now(),User=request.user, model=LeaveClass._meta.verbose_name,action = u"%s"%_(u"Modify"),object = LeaveName).save(force_insert = True)#
        return getJSResponse({"ret":0,"message":u"保存假类成功"})

def submitAttParam(request):
    if request.method=="POST":
        try:
            ruleId=request.POST.get('ruleID','')
            if ruleId=='new':
                deptID=request.POST.get('DeptID_attparam','')
                if deptID=='0':
                    return getJSResponse({"ret":1,"message":u"保存失败，应用范围和默认规则重复"})
                rName=request.POST.get('ruleName','')
                try:
                    if rName==u'默认考勤规则':
                        return getJSResponse({"ret":1,"message":u"保存失败，规则名称和默认规则重复"})

                    obj=attParamDepts.objects.get(ruleName=rName)
                    return getJSResponse({"ret":1,"message":u"保存失败，规则名称和已有规则重复"})
                except:
                    obj=attParamDepts()
                    obj.ruleName=rName
                    obj.DeptID=deptID
                    obj.operator=request.user.username
                    obj.OpTime=datetime.datetime.now()
                    obj.save()
                    ruleId=obj.id

            AttRuleName = request.POST.get("ruleName",'')
            s=request.POST['LeaveClass']
            l=loads(s)
            SaveAttRule(request.POST,ruleId)
            SaveLeaveClass(l)
        except Exception,e:
            import traceback;traceback.print_exc()

            print "submitAttParam===",e
            return getJSResponse({"ret":0,"message":u"保存失败，可能是因为计算单位为空"})

        adminLog(time=datetime.datetime.now(),User=request.user, model=AttParam._meta.verbose_name,action = u"%s"%_(u"Modify"),object = AttRuleName).save(force_insert = True)#
        return getJSResponse({"ret":0,"message":u"保存考勤规则成功"})

def getLeaveClass(request):
    ls=GetLeaveClasses(2)
    return getJSResponse(dumps(ls))

#@login_required
#def deleteEmpFromDevice(request):   #从设备中删除 用户 自动包括删除指纹信息
    #userids=request.POST.get("userids","")
    #deptIDs=request.POST.get("deptIDs","")
    #sns=request.POST.getlist("K")
    #flag=int(request.POST.get("flag"))     #flag=1为从所有设备删除用户
    #isContainedChild=request.POST.get('isContainChild',"")
    #if userids=='':
        #deptidlist=[int(i) for i in deptIDs.split(',')]
        #deptids=deptidlist
        #if isContainedChild=="1":   #是否包含下级部门
            #for d in deptidlist:#支持选择多部门
                #deptids=getAllAuthChildDept(d,request)
        #userids=employee.objects.filter(DeptID__in=deptids)
    #else:
        #emplist=userids.split(',')
        #userids=employee.objects.filter(id__in=emplist)
    #len(userids)
    #if flag==1:
        #o_devs=iclock.objects.all()
    #else:
        #o_devs=iclock.objects.filter(SN__in=sns)
    #settings.DEV_STATUS_SAVE=1
    #for dev in o_devs:
        #d=getDevice(dev.SN)
        #for userPin in userids:
            #appendDevCmd(d, "DATA DEL_USER PIN=%s"%userPin.PIN)
    #settings.DEV_STATUS_SAVE=0
    #return getJSResponse({"ret":0,"message":""})

#@login_required
#def delFingerFromDev(request):     #从设备中仅删除用户的指纹
    #userids=request.POST.get("userids","")
    #deptIDs=request.POST.get("deptIDs","")
    #sns=request.POST.getlist("K")
    #flag=int(request.POST.get("flag",'0')) #flag=1为从所有设备删除用户指纹
    #isDel=int(request.POST.get("isDel",'0'))       #isDel=1为同时从数据库中将指纹删除
    #isContainedChild=request.POST.get('isContainChild',"")
    #if userids=='':
        #deptidlist=[int(i) for i in deptIDs.split(',')]
        #deptids=deptidlist
        #if isContainedChild=="1":   #是否包含下级部门
            #for d in deptidlist:#支持选择多部门
                #deptids=getAllAuthChildDept(d,request)
        #userids=employee.objects.filter(DeptID__in=deptids)
    #else:
        #emplist=userids.split(',')
        #userids=employee.objects.filter(id__in=emplist)
    #len(userids)
    #if flag==1:
        #o_devs=iclock.objects.all()
    #else:
        #o_devs=iclock.objects.filter(SN__in=sns)
    #settings.DEV_STATUS_SAVE=1
    #for dev in o_devs:
        #d=getDevice(dev.SN)
        #for userPin in userids:
            #tmp=fptemp.objects.filter(UserID=int(userPin.id)).values_list('FingerID', flat=True)
            #if len(tmp):
                #for t in tmp:
                    #appendDevCmd(d, "DATA DEL_FP PIN=%s\tFID=%s"%(userPin.PIN,t))
    #settings.DEV_STATUS_SAVE=0
    #if isDel==1:  #下发删除指纹命令后，再从数据库中删除指纹
        #for userPin in userids:
            #fptemp.objects.filter(UserID=int(userPin.id)).delete()
    #return getJSResponse({"ret":0,"message":""})

#次函数因为慢作废
#def get_dept_list(request,deptid,isall=False):
#       d_items=get_dept_items(request,deptid)
#       deptObj = []
#       d = {}
#       cdept=getChildFromCache(request)
#       for i in d_items:
#               d["id"]=str(i['DeptID'])
#               d["text"]=i['DeptName']
#               d["value"]=str(i['DeptID'])
#               d["showcheck"]=True
#               d["checkstate"]="0"
#               d["isexpand"]=False
#               d["complete"]=False   #是否已加载子节点
#
#               d["hasChildren"]=len(hasChildren(i['DeptID'],request,cdept))>0
#
#               if isall:
#                       d["isexpand"]=True
#                       d["ChildNodes"]=get_dept_list(request,i['DeptID'],isall)
#               else:
#                       d["isexpand"]=False
#                       d["ChildNodes"]=[]
#               t = d.copy()
#               deptObj.append(t)
#       return deptObj




#def get_dept_items(request,deptid):
#       dept_list=[]
#       if (not request.user.is_superuser) and (not request.user.is_alldept):
#               dept_list=userDeptList(request.user)
#               if deptid==0:
#                       objs=department.objects.filter(DeptID__in=dept_list).exclude(parent__in=dept_list).values("DeptID", "DeptName","parent").order_by("DeptNo","DeptID")
#               else:
#                       objs=department.objects.filter(parent__exact=deptid,DeptID__in=dept_list).values("DeptID", "DeptName","parent").order_by("DeptNo","DeptID")
#       else:
#               objs=department.objects.filter(parent__exact=deptid).values("DeptID", "DeptName","parent").order_by("DeptNo","DeptID")
#       return objs
#
#
#def get_dept_list_ex(request,d_item,deptid,isall=False,onlyshowsecondDept=False,sub_fun="",lDepts=[]):
#       if deptid not in d_item.keys():
#               return []
#       d_items=d_item[deptid]
#       deptObj = []
#       d = {}
#       for i in d_items:
#               if sub_fun=='department':
#                       if not i['DeptID'] in lDepts:continue
#
#               d["id"]=str(i['DeptID'])
#               d["text"]=i['DeptName']
#               d["value"]=str(i['DeptID'])
#               d["showcheck"]=True
#               d["checkstate"]="0"
#               d["isexpand"]=False
#               d["complete"]=False   #是否已加载子节点
#               tag=True
#               try:
#                       d_item[i['DeptID']]
#               except:
#                       tag=False
#               d["hasChildren"]=tag
#               if isall:
#                       d["isexpand"]=True
#                       d["ChildNodes"]=get_dept_list_ex(request,d_item,i['DeptID'],isall,onlyshowsecondDept,sub_fun,lDepts)
#               else:
#                       d["isexpand"]=False
#                       if onlyshowsecondDept:
#                               d["isexpand"]=True
#                       d["ChildNodes"]=[]
#               t = d.copy()
#               deptObj.append(t)
#       return deptObj
#
#def get_dept_items_ex(request):
#       dept_list=[]
#       if (not request.user.is_superuser) and (not request.user.is_alldept):
#               dept_list=userDeptList(request.user)
#               objs=department.objects.filter(DeptID__in=dept_list).values("DeptID", "DeptName","parent").order_by("DeptNo","DeptNumber")
#       else:
#               objs=department.objects.all().values("DeptID", "DeptName","parent").order_by("DeptNo","DeptNumber")
#       ll={}
#       for o in objs:
#               try:
#                       ll[o['parent']].append(o)
#               except:
#                       ll[o['parent']]=[]
#                       ll[o['parent']].append(o)
#       return ll
#


@login_required
def getData(request):

    funid = request.GET.get("func", "")
    if funid == 'init_database' and request.user.has_perm('Init_database'):
        ClearDataAll()
        adminLog(time=datetime.datetime.now(), User=request.user, action=_(u"InitSystem"), object=request.META["REMOTE_ADDR"]).save()#
        return getJSResponse({"ret":0,"message":u"%s"%_("Operation Successfully")})
    elif funid == 'clearObsoleteData':
        attEndTime = request.GET.get("attEndTime", "")
        attStrTime = request.GET.get("attStrTime", "1999-01-01")
        cleartype = request.GET.get("cleartype","")
        if cleartype== "0" or cleartype == 0:
            attEndTime = attEndTime + " 23:59:59"
            attStrTime = attStrTime + " 00:00:00"
            if 'oracle' in settings.DATABASE_ENGINE:
                Condition = "checktime >= to_date('%s','YYYY-MM-DD HH24:MI:SS') and checktime <= to_date('%s','YYYY-MM-DD HH24:MI:SS')" % (attStrTime,attEndTime)
            else:
                Condition = "checktime >= '%s' and checktime <= '%s'" % (attStrTime,attEndTime)
            ClearTableData("checkinout", Condition)
            adminLog(time=datetime.datetime.now(), User=request.user, action=u'%s'%_(u"Clear Obsolete transaction Data"),model = transactions._meta.verbose_name,object=request.META["REMOTE_ADDR"]).save(force_insert = True)#
        if cleartype== "1" or cleartype == 1:
            #清除照片功能,未完
            photodir=settings.ADDITION_FILE_ROOT+'upload\\'
            clearPhotos(attStrTime,attEndTime,photodir)
            adminLog(time=datetime.datetime.now(), User=request.user, action=u'%s'%_(u"Clear Obsolete transaction picture Data"), model = u'%s'%_(u"Picture file"), object=request.META["REMOTE_ADDR"]).save(force_insert = True)#
        if cleartype== "2" or cleartype == 2:
            attEndTime2 = attEndTime + " 23:59:59"
            attStrTime2 = attStrTime + " 00:00:00"
            if 'oracle' in settings.DATABASE_ENGINE:
                Condition = "checktime >= to_date('%s','YYYY-MM-DD HH24:MI:SS') and checktime <= to_date('%s','YYYY-MM-DD HH24:MI:SS')" % (attStrTime2,attEndTime2)
            else:
                Condition = "checktime >= '%s' and checktime <= '%s'" % (attStrTime2,attEndTime2)
            ClearTableData(attRecAbnormite._meta.db_table, Condition)

            if 'oracle' in settings.DATABASE_ENGINE:
                Condition = "attdate >= to_date('%s','YYYY-MM-DD HH24:MI:SS') and attdate <= to_date('%s','YYYY-MM-DD HH24:MI:SS')" % (attStrTime,attEndTime)
            else:
                Condition = "attdate >= '%s' and attdate <= '%s'" % (attStrTime,attEndTime)
            ClearTableData(attShifts._meta.db_table, Condition)

            ClearTableData(AttException._meta.db_table, Condition)
            adminLog(time=datetime.datetime.now(), User=request.user, action=u'%s'%_(u"Clear Obsolete cacluate Data"),model = u'%s'%_(u"Calculate"), object=request.META["REMOTE_ADDR"]).save(force_insert = True)#
        if cleartype== "3" or cleartype == 3:
            attEndTime = attEndTime + " 23:59:59"
            attStrTime = attStrTime + " 00:00:00"
            if 'oracle' in settings.DATABASE_ENGINE:
                Condition = "CmdCommitTime >= to_date('%s','YYYY-MM-DD HH24:MI:SS') and CmdCommitTime <= to_date('%s','YYYY-MM-DD HH24:MI:SS')" % (attStrTime,attEndTime)
            else:
                Condition = "CmdCommitTime >= '%s' and CmdCommitTime <= '%s'" % (attStrTime,attEndTime)
            ClearTableData(devcmds._meta.db_table, Condition)
            adminLog(time=datetime.datetime.now(), User=request.user, action=u'%s'%_(u"Clear Obsolete devcmds Data"),model = devcmds._meta.verbose_name, object=request.META["REMOTE_ADDR"]).save(force_insert = True)#
        if cleartype== "4" or cleartype == 4:
            attEndTime = attEndTime + " 23:59:59"
            attStrTime = attStrTime + " 00:00:00"
            if settings.DATABASE_ENGINE=="oracle":
                Condition = "OpTime >= to_date('%s','YYYY-MM-DD HH24:MI:SS') and OpTime <= to_date('%s','YYYY-MM-DD HH24:MI:SS')" % (attStrTime,attEndTime)
            else:
                Condition = "OpTime >= '%s' and OpTime <= '%s'" % (attStrTime,attEndTime)
            ClearTableData(devlog._meta.db_table, Condition)
            adminLog(time=datetime.datetime.now(), User=request.user, action=u'%s'%_(u"Clear Obsolete devlog Data"),model = devlog._meta.verbose_name, object=request.META["REMOTE_ADDR"]).save(force_insert = True)#

        return getJSResponse({"ret":0,"message":u"%s"%_("Operation Successfully")})
    elif funid=='backup_database':
        re,mes=Backup_Database()
        adminLog(time=datetime.datetime.now(), User=request.user, action=u'%s'%_(u"Back Up DataBase"),object=request.META["REMOTE_ADDR"]).save(force_insert = True)
        return getJSResponse({"ret":re,"message":mes})
    elif funid == 'verifymethod':
        verifymethod = COMVERIFYS
        re = []
        ss = {}
        for t in verifymethod:
            ss['id'] = t[0]
            ss['Name'] = unicode(t[1])
            t = ss.copy()
            re.append(t)
        return getJSResponse(dumps(re))
    elif funid == 'schClass':
        schclasses = GetSchClasses(User=request.user)
        re = []
        ss = {}
        for t in schclasses:
            #if not request.user.is_superuser:
            #       if t['TimeZoneOfDept']>0:
            #               if t['TimeZoneOfDept']<>request.user.AutheTimeDept:continue
            ss['SchclassID'] = t['schClassID']
            ss['SchName'] = t['SchName']
            ss['StartTime'] = t['TimeZone']['StartTime'].time()
            ss['EndTime'] = t['TimeZone']['EndTime'].time()
            t = ss.copy()
            re.append(t)
        return getJSResponse(dumps(re))
    elif funid == 'devs':
        q=request.POST.get("q","")
        if q=="":
            q=request.GET.get("q","")
        if request.user.is_superuser or request.user.is_alldept:
            if q!="":
                iclocks=iclock.objects.filter(Q(SN__contains=q)|Q(Alias__contains=q)).filter(Q(DelTag__isnull=True)|Q(DelTag=0))
            else:
                iclocks=iclock.objects.filter(Q(DelTag__isnull=True)|Q(DelTag=0))
        else:
            sns=userIClockList(request.user)
            if q!="":
                iclocks=iclock.objects.filter(SN__in=sns).filter(Q(SN__contains=q)|Q(Alias__contains=q)).filter(Q(DelTag__isnull=True)|Q(DelTag=0))
            else:
                iclocks=iclock.objects.filter(SN__in=sns).filter(Q(DelTag__isnull=True)|Q(DelTag=0))
        re=[]
        r={}
        for dev in iclocks:
            r['SN']=dev.SN
            r['Alias']=dev.Alias
            re.append(r.copy())
        return getJSResponse(smart_str(dumps(re)))

    elif funid=='devs_checkexact':
        dd={}
        val=request.GET.get("mod_name","att")
        pt=9
        if val=="meeting":
            pt=1
        if request.user.is_superuser or request.user.is_alldept:
            iclocks=iclock.objects.filter(ProductType=pt).exclude(DelTag=1)
        else:
            sns=AuthedIClockList(request.user)
            iclocks=iclock.objects.filter(SN__in=sns,ProductType=pt).exclude(DelTag=1)
        d=[]
        for t in iclocks:
            dd["id"]=t.SN
            if t.Alias:
                dd["name"]=t.SN+' '+t.Alias
            else:
                dd["name"]=t.SN
            dd["pid"]=0
            dd["value"]=t.SN
            dd["open"]=False
            dd["isParent"]=False
            d.append(dd.copy())
        return getJSResponse(d)

    elif funid=='devs_tree':
        d={}
        dd={}
        ptype=request.GET.get('ptype','')
        deptName=u'所有设备'

        if request.user.is_superuser or request.user.is_alldept:
            iclocks=iclock.objects.all()
        else:
            sns=AuthedIClockList(request.user)
            iclocks=iclock.objects.filter(SN__in=sns)
        if ptype=='acc':
            iclocks=iclocks.filter(ProductType__in=[4,5,15])
        elif ptype=='patrol':
            iclocks=iclocks.filter(ProductType__in=[2])

        else:
            iclocks=iclocks.exclude(ProductType__in=[1,2,4,5,11,12,13,15])
        #       iclocks=iclocks.filter(Q(ProductType__isnull=True)|Q(ProductType=0))
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


    elif funid == 'accdevs':
        q=request.POST.get("q","")
        if q=="":
            q=request.GET.get("q","")
        snlist=UserACCDevice.objects.filter(UserID=q)#.values_list('SN')
        re=[]
        r={}
        for dev in snlist:
            r['SN']=dev.SN.SN
            r['Alias']=dev.SN.Alias
            re.append(r.copy())
        return getJSResponse(smart_str(dumps(re)))
    elif funid == 'shifts':
        nrun = NUM_RUN.objects.all().exclude(DelTag=1).order_by('Num_runID')
        if not request.user.is_superuser:
            nrun = nrun.filter(Q(Num_RunOfDept=0)|Q(Num_RunOfDept__isnull=True)|Q(Num_RunOfDept=request.user.AutheTimeDept)).order_by('Num_runID')
        re = []
        ss = {}
        for t in nrun:
            ss['shift_id'] = t.Num_runID
            ss['shift_name'] = t.Name
            t = ss.copy()
            re.append(t)
        return getJSResponse(dumps(re))
    elif funid == 'employee':
        pin=request.GET.get("pin")
        t={}
        if pin:
            emp = employee.objByPIN(pin)
            e = {}
            e['id'] = emp.id
            e['PIN'] = emp.PIN
            e['EName'] = emp.EName
            e['DeptName'] = emp.Dept().DeptName
            e['Title']=emp.Title
            e['Card']=emp.Card
            e['Sex']=getSex(emp.Gender)
            t = e.copy()
        return getJSResponse(dumps(t))
    elif funid == 'NUM_RUN':
        numrunid=request.GET.get("numrunid", "")
        if numrunid:
            num=NUM_RUN.objects.filter(Num_runID=numrunid)[0]
            n={}
            n['Num_runID']=num.Num_runID
            n['Name']=num.Name
            n['StartDate']=num.StartDate
            n['EndDate']=num.Name
            n['Cycle']=num.Cycle
            n['h_unit']=num.Units
            n['Units']=''
            t = n.copy()
        return getJSResponse(dumps(t))
    elif funid == 'employees':
        deptids=[]
        deptid=[]
        isContainChild=int(request.GET.get('isContainChild',0))
        q=request.GET.get('q',"")
        q=unquote(q)
        deptid=request.GET.get('DeptID__DeptID__in')
        ot=['DeptID','PIN']
        qs=employee.objects.filter(OffDuty__lt=1).order_by(*ot)
        if deptid!='':
            dept_id=deptid.split(',')
            for d in dept_id:
                deptids.append(d)
            t1=datetime.datetime.now()
            if isContainChild:
                deptids=[]
                for d in dept_id:
                    if int(d) not in deptids :
                        deptids+=getAllAuthChildDept(d,request)
            qs=qs.filter(DeptID__in=deptids)
        t2=datetime.datetime.now()
        if q!="":
            qs=qs.filter(Q(PIN__startswith='%s'%(q))|Q(EName__startswith='%s'%(q))|Q(Title__startswith='%s'%(q))|Q(DeptID__DeptName__startswith='%s'%(q)))

        #分页
        try:
            offset = int(request.GET.get('p', 1))
        except:
            offset=1
        limit= int(request.GET.get('l', settings.PAGE_LIMIT))
        paginator = Paginator(qs, limit)
        item_count = paginator.count
        if offset>paginator.num_pages: offset=paginator.num_pages
        if offset<1: offset=1
        pgList = paginator.page(offset)
        cc={'latest_item_list': pgList.object_list,
                'from': (offset-1)*limit+1,
                'item_count': item_count,
                'page': offset,
                'limit': limit,
                'page_count': paginator.num_pages,
                'title': (u"%s"%employee._meta.verbose_name).capitalize(),
                'dataOpt': employee._meta,
                }
        tmpFile=request.GET.get('t')
        return render(request,tmpFile, cc,{})
    elif funid == 'devs':
        d=request.GET.get('d',"")
        d=unquote(d)
        qs=iclock.objects.all().order_by('SN')
        if d!="":
            qs=qs.filter(Q(SN__contains='%s'%(d))|Q(Alias__contains='%s'%(d)))
        #分页
        try:
            offset = int(request.GET.get('p', 1))
        except:
            offset=1
        limit= int(request.GET.get('l', settings.PAGE_LIMIT))
        paginator = Paginator(qs, limit)
        item_count = paginator.count
        if offset>paginator.num_pages: offset=paginator.num_pages
        if offset<1: offset=1
        pgList = paginator.page(offset)
        cc={'latest_item_list': pgList.object_list,
                'from': (offset-1)*limit+1,
                'item_count': item_count,
                'page': offset,
                'limit': limit,
                'page_count': paginator.num_pages,
                'title': (u"%s"%iclock._meta.verbose_name).capitalize(),
                'dataOpt': iclock._meta,
                }
        tmpFile=request.GET.get('t')
        return render(request,tmpFile, cc,{})

    elif funid == 'leaveClass':
        qs = GetLeaveClasses(2)
        return getJSResponse(dumps(qs))
    elif funid == 'attParam':
        ruleId=request.GET.get('ruleId')
        la = LoadAttRule()
        lc = LoadCalcItems()

        rules=[]
        if not ruleId:
            qs = la.copy()
            qs['LeaveClass'] = lc

            rules =[
                { 'id':0, 'pId':-1, 'name':u"默认考勤规则"}
            ]
            objs=attParamDepts.objects.all().order_by('id')
            for t in objs:
                dDict={
                    'id':t.id,
                    'pId':-1,
                    'name':t.ruleName
                }
                rules.append(dDict)
        else:
            if int(ruleId)==0:
                qs = la.copy()
            else:
                obj=attParamDepts.objects.get(id=ruleId)
                qs=la['customer'][obj.DeptID]
                print "99999999999",qs['ruleName']
        qs['LeaveClass'] = lc

        qs['rules']=rules


        return getJSResponse(dumps(qs))

    #人事信息提醒
    elif funid=='reverse':
        result=[{'id':1,'pid':0,'name':u'%s'%_(u'无指纹人员'),'icon':"media/img/icons/cal.gif"},{'id':1,'pid':0,'name':u'%s'%_(u'无面部人员'),'icon':"media/img/icons/cal.gif"},
        {'id':3,'pid':0,'name':u'%s'%_(u'今天未考勤人员'),'icon':"media/img/icons/cal.gif"},{'id':4,'pid':0,'name':u'%s'%_(u'昨天未考勤人员'),'icon':"media/img/icons/cal.gif"},
        {'id':5,'pid':0,'name':u'%s'%_(u'本周未考勤人员'),'icon':"media/img/icons/cal.gif"},{'id':6,'pid':0,'name':u'%s'%_(u'本月未考勤人员'),'icon':"media/img/icons/cal.gif"}]
        return getJSResponse(dumps(result))
    elif funid == 'ihrremind':
        cometime=request.GET.get("cometime","")
        if cometime=="" or len(cometime)==0:
            now=datetime.datetime.now()
        else:
            now=datetime.datetime.strptime(cometime,'%Y-%m-%d')

        deptObj=[]
        re={}
        re["pid"]=0
        re['icon']="media/img/icons/cal.gif"

        result=[]
        #当天生日
        re['id']=1
        empcount=employee.objects.filter(Birthday__month=now.month,Birthday__day=now.day).count()
        re['name']=_(u'当天生日')+(str(empcount))
        result.append(re.copy())

        #本月生日
        re['id']=2
        empmonthcount=employee.objects.filter(Birthday__month=now.month).count()
        re['name']=_(u'本月生日')+str(empmonthcount)
        result.append(re.copy())

        #下月生日
        re['id']=3
        year=now.year
        month=now.month+1
        if now.month==12:
            year=year+1
            month=1
        nextmonth=datetime.datetime(year=year,month=month,day=1)
        empmonthcount=employee.objects.filter(Birthday__month=nextmonth.month).count()
        re['name']=_(u'下月生日')+str(empmonthcount)
        result.append(re.copy())

        #当月合同到期
        re['id']=4
        empmonthcount=employee.objects.filter(Contractendtime__month=now.month).count()
        re['name']=_(u'本月合同到期')+str(empmonthcount)
        result.append(re.copy())

        #当日合同到期
        re['id']=5
        empcount=employee.objects.filter(Contractendtime__year=now.year,Contractendtime__month=now.month,Contractendtime__day=now.day).count()
        re['name']=_(u'当天合同到期')+str(empcount)
        result.append(re.copy())

        #下月合同到期
        re['id']=6
        empmonthcount=employee.objects.filter(Contractendtime__year=now.year,Contractendtime__month=nextmonth.month).count()
        re['name']=_(u'下月合同到期')+str(empmonthcount)

        result.append(re.copy())

        #当月试用期到期
        re['id']=7
        empmonthcount=employee.objects.filter(Trialendtime__year=now.year,Trialendtime__month=now.month).count()
        re['name']=_(u'本月试用期合同到期')+str(empmonthcount)
        result.append(re.copy())

        #当日试用期到期
        re['id']=8
        empcount=employee.objects.filter(Trialendtime__year=now.year,Trialendtime__month=now.month,Trialendtime__day=now.day).count()
        re['name']=_(u'当天试用期合同到期')+str(empcount)
        result.append(re.copy())

        #下月试用期到期
        re['id']=9
        empmonthcount=employee.objects.filter(Trialendtime__year=nextmonth.year,Trialendtime__month=nextmonth.month).count()
        re['name']=_(u'下月试用期合同到期')+str(empmonthcount)
        result.append(re.copy())

        #离职员工总人数
        re['id']=10
        empmonthcount=employee.objects.filter(OffDuty=1).count()
        re['name']=_(u'离职员工总人数')+str(empmonthcount)
        result.append(re.copy())

        #该年新加入员工
        re['id']=11
        empmonthcount=employee.objects.filter(Hiredday__year=now.year).count()
        re['name']=_(u'该年新入职员工')+str(empmonthcount)
        result.append(re.copy())

        #入职周年人数
        re['id']=12
        preyear=datetime.datetime(year=now.year-1,month=now.month,day=now.day)
        empmonthcount=employee.objects.filter(Hiredday__lt=preyear).count()
        re['name']=_(u'入职周年人数')+str(empmonthcount)

        result.append(re.copy())

        #7天内请假到期人数
        re['id']='13'
        #########计算七天后的日期
        try:
            sevendays=now-datetime.timedelta(days=7)
            userspe=USER_SPEDAY.objects.filter(State=2,EndSpecDay__lte=sevendays,StartSpecDay__gte=now).values('UserID').annotate()
        except Exception,ee:
            userspe=[]
            print ee

        re['name']=_(u'七天内请假到期人数')+str(len(userspe))
        result.append(re.copy())


        return getJSResponse(dumps(result))






#               deptid=int(request.POST.get("value",0))
#               objs=get_dept_items(request,deptid)
#               sub_fun=request.GET.get("m","")
#               lDepts=[]
#               if sub_fun=='department':#编辑部门时判断
#                       dataKey=request.GET.get("deptid",0)
#                       pdepts=getAvailableParentDepts(dataKey,request)
#                       for i in pdepts:
#                               lDepts.append(int(i.DeptID))
#               deptObj = []
#               d = {}
#               expand_dept=GetParamValue('opt_basic_expanddept','1')
#               isall=False
#               if expand_dept=='1' or expand_dept=='on':
#                       isall=True
#               if isall:
#                       c_deptObj=cache.get("%s_depttree_%s_%s"%(settings.UNIT, request.user.id,settings.DEPTVERSION))
#                       if c_deptObj:
#                               return getJSResponse(dumps(c_deptObj))
#               cdept=getChildFromCache(request)
#               for i in objs:
#                       if sub_fun=='department':
#                               if not i['DeptID'] in lDepts:continue
#                       d["id"]=str(i['DeptID'])
#                       d["text"]=i['DeptName']
#                       d["value"]=str(i['DeptID'])
#                       d["showcheck"]=True
#                       d["checkstate"]="0"
#                       d["complete"]=False   #是否已加载子节点
#                       d["hasChildren"]=len(hasChildren(i['DeptID'],request,cdept))>0
#                       if deptid==0:#自动取得第一级部门
#                               d["ChildNodes"]=get_dept_list(request,i['DeptID'],isall)
#                               d["isexpand"]=True
#                       else:
#                               d["isexpand"]=False
#                               d["ChildNodes"]=[]
##                      d["ChildNodes"]=[{"id":"2","text":"2332","value":2,"showcheck":True,"checkstate":"0","isexpand":False,"complete":False,"hasChildren":False,"ChildNodes":[]}]
#                       t = d.copy()
#                       deptObj.append(t)
#               if isall:
#                       cache.set("%s_depttree_%s_%s"%(settings.UNIT, request.user.id,settings.DEPTVERSION),deptObj)
#               return getJSResponse(dumps(deptObj))
    elif funid=='attTotal':
        t,rFieldNames,rCaption=ConstructFields()
        dis=FetchDisabledFields(request.user,funid)
        d={}
        d['FieldNames']=rFieldNames
        d['FieldCaptions']=rCaption
        d['disableCols']=dis
        return getJSResponse(dumps(d))
    elif funid=='attDailyTotal':
        st=request.POST.get('startDate','')
        et=request.POST.get('endDate','')
        if (st=='') or (et==''):
            st=datetime.datetime.now()
            et=datetime.datetime.now()
        d1=datetime.datetime.strptime(st,'%Y-%m-%d')
        d2=datetime.datetime.strptime(et,'%Y-%m-%d')

        t,rFieldNames,rCaption=ConstructFields1(d1,d2)
        #rCaption=ConstructFields1(st,et)[2]
        #item=ItemDefine.objects.filter(Author=request.user,ItemName=funid,ItemType='report_fields_define')
        dis=FetchDisabledFields(request.user,funid)
        d={}
        d['FieldNames']=rFieldNames
        d['FieldCaptions']=rCaption
        d['disableCols']=dis
        return getJSResponse(dumps(d))
    elif funid=='attShifts':
        """for New attshifts detail"""
        rFieldNames,rCaption,r=ConstructAttshiftsFields1()
        rFieldNames.remove('userid')
        rCaption.remove('UserID')
        dis=FetchDisabledFields(request.user,funid)
        d={}
        d['FieldNames']=rFieldNames
        d['FieldCaptions']=rCaption
        d['disableCols']=dis
        return getJSResponse(dumps(d))
    #elif funid=='ACTimeZones':
    #       timezone = ACTimeZones.objects.all().order_by('TimeZoneID')
    #       re = []
    #       ss = {}
    #       for t in timezone:
    #               ss['TimeZoneID'] = t.TimeZoneID
    #               ss['Name'] = t.Name
    #               t = ss.copy()
    #               re.append(t)
    #       return getJSResponse(dumps(re))
    elif funid=='holidays':
        holiday = holidays.objects.all().order_by('HolidayID')
        re = []
        ss = {}
        for t in holiday:
            ss['HolidayID'] = t.HolidayID
            ss['HolidayName'] = t.HolidayName
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
    elif funid=='SN':
        device=iclock.objects.all().order_by('SN')
        re = []
        ss = {}
        for d in device:
            ss['SN'] = d.SN
            ss['Alias'] = d.Alias
            d = ss.copy()
            re.append(d)
        return getJSResponse(dumps(re))
    elif funid == 'picture_canlendar':
        y=int(request.GET.get('year','2014'))
        nt=datetime.datetime.now()
        re=[]
        if int(y)==nt.year:
            mon=nt.month
        else:
            mon=12
        d={}
        dd={}
        d["id"]=0
        d["name"]='%04d'%y
        d["pid"]=-1
        d["value"]='%04d'%y
        d["open"]=True
        d["isParent"]=True
        #d['icon']="/media/img/icons/home.png"
        d["children"]=[]
        for m in range(mon,0,-1):
            s='%04d-%02d'%(y,m)
            dd={}
            dd["id"]=m
            dd["name"]=s
            dd["pid"]=0
            dd["value"]='%04d%02d'%(y,m)
            dd["open"]=False
            dd["isParent"]=False
            #d['icon']="/media/img/icons/home.png"
            dd["children"]=[]
            dt=datetime.datetime(y,m,1,0,0)
            for ds in range(32):
                s='%d-%02d-%02d'%(y,m,ds+1)
                ddd={}
                ddd["id"]=ds
                ddd["name"]=s
                ddd["pid"]=m
                ddd["value"]='%d%02d%02d'%(y,m,ds+1)
                ddd["open"]=False
                ddd["isParent"]=False
                #d['icon']="/media/img/icons/home.png"
                ddd["children"]=[]
                dd["children"].append(ddd.copy())
                dt=dt+datetime.timedelta(days=1)
                if dt.month!=m:break

            d["children"].append(dd.copy())
        return getJSResponse(d)
    elif funid == 'fingerids':
        userid=request.GET.get('userid')
        finger=['0','0','0','0','0','0','0','0','0','0']
        objs=fptemp.objects.filter(UserID=userid)
        for t in objs:
            fingerid=t.FingerID
            finger[fingerid]='1'

        fingers=''.join('%s'%f for f in finger)
        d={'ret':0,'finger':fingers}
        return getJSResponse(d)
    elif funid=='users':
        from django.contrib.auth import get_user_model
        User=get_user_model()

        #d={}
        rt=[]
        objs=User.objects.all().exclude(username='employee').order_by('id')
        for t in objs:
            d={}
            d["id"]=t.id
            d["name"]=t.username
            d["pid"]=0
            d["value"]=0
            d["open"]=True
            d["isParent"]=False
            #d['icon']="/media/img/icons/home.png"
            rt.append(d.copy())
        return getJSResponse(rt)




    return getJSResponse({"ret":0,"message":""})

def ClearDataAll():
    EXCNOTES.objects.all().delete()
    holidays.objects.all().delete()
    NUM_RUN.objects.all().delete()
    SchClass.objects.all().delete()
    SECURITYDETAILS.objects.all().delete()
    SHIFT.objects.all().delete()
#       LeaveClass.objects.all().delete()
#       LeaveClass1.objects.all().delete()
#       AttParam.objects.all().delete()
    UserUsedSClasses.objects.all().delete()
    attCalcLog.objects.all().delete()
    attRecAbnormite.objects.all().delete()
    AttException.objects.all().delete()
    ItemDefine.objects.all().delete()
#       adminLog.objects.all().delete()
#       sql='''delete from auth_user where (username<>'%s') and  (is_superuser<>1)'''%('employee')
#       customSql(sql)
#       initDB()
    clearData()
    #InitData()
#       print "Init Success"
@permission_required("iclock.browse_employee")
def NoFingerCount(request):#, qs, offset, limit, cl, state):
    request.user.iclock_url_rel='../..'
    request.model = employee
    count=0
    curCount=0
    try:
        offset = int(request.GET.get('p', 1))
        deptid=request.GET.get('DeptID__DeptID__in')
        deptid=deptid.split(',')
    except:
        offset=1
    limit= int(request.GET.get('l', settings.PAGE_LIMIT))
    state = int(request.GET.get('s', -1))

    qs=employee.objects.filter(DeptID__DeptID__in=deptid).extra(where=['UserID NOT IN (%s)'%('select userid from template')])
    paginator = Paginator(qs, limit)
    item_count = paginator.count
    if offset>paginator.num_pages: offset=paginator.num_pages
    if offset<1: offset=1
    pgList = paginator.page(offset)
    cc={'latest_item_list': pgList.object_list,
            'from': (offset-1)*limit+1,
            'item_count': item_count,
            'page': offset,
            'limit': limit,
            'page_count': paginator.num_pages,
            'dataOpt': employee._meta,
            'iclock_url_rel': request.user.iclock_url_rel,
            }

    tmpFile='empsInDept_noFP.html'
    return render(request,tmpFile, cc)
#----------------------------------------------------------------------


@login_required
def searchRecords(request):#综合记录查询
    from math import ceil
    if request.method=="GET":
        fieldNames,fieldCaptions,rt=ConstructScheduleFields2(request)
        disabledCols=FetchDisabledFields(request.user,'original_records')#FetchDisabledFields(request.user,flag)
        r=[]
        it=0
        w=100
        for field in fieldCaptions:
            if field=='userid' or field=='UserID':
                r.append({"name":"UserID",'sortable':False,'hidden':True})
            else:
                if it>=4:
                    w=100
                r.append({"name":field,'sortable':False,'label':rt[it],'width':w})
            it=it+1
        rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(r)+"""}"""
        return getJSResponse(rs)

    else:
        isContainedChild=request.GET.get("isContainChild","0")
        deptIDs=request.GET.get('deptIDs',"")
        userIDs=request.GET.get('UserIDs',"")
        st=request.GET.get('startDate','')
        et=request.GET.get('endDate','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        et=et+datetime.timedelta(1)
        Result=getsearchRecords(request,isContainedChild,deptIDs,userIDs,st,et)
        rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
        return getJSResponse(rs)


def getsearchRecords(request,isContainedChild,deptIDs,userIDs,st,et):
    iCount=0
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset=1
    limit= int(request.POST.get('rows', 30))
    sidx=""
    if request.GET.has_key('sidx'):
        sidx = request.GET.get('sidx','')
    else:
        sidx = request.POST.get('sidx','')
    ot=sidx.split(',')
    if len(userIDs)>0 and userIDs!='null':
        objs=userIDs.split(',')
        emps=employee.objects.filter(id__in=objs,OffDuty__lt=1).order_by(*ot)
        p=Paginator(emps, limit)
        page_count=p.num_pages
        iCount=p.count
        pp=p.page(offset)
        ids=pp.object_list.values_list('id', flat=True)
    elif len(deptIDs)>0:
        deptidlist=deptIDs.split(',')
        deptids=deptidlist
        if isContainedChild=="1": #是否包含下级部门
            deptids=[]
            for d in deptidlist:#支持选择多部门
                if int(d) not in deptids :
                    deptids+=getAllAuthChildDept(d,request)
#               ot=['DeptID','PIN']
        #iCount=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).count()
        objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).order_by(*ot)
        #objs=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).values_list('id', flat=True).order_by(*ot)
        p=Paginator(objs, limit)
        iCount=p.count
        page_count=p.num_pages
        pp=p.page(offset)
        ids=pp.object_list.values_list('id', flat=True)
    re=[]
    Result={}
    Result['datas']=re
#               print "icount==",iCount
#               print "page_count==",page_count
#               print "ids==",ids
#               ids=ids[(offset-1)*limit:offset*limit]
    for id in ids:
        e=employee.objByID(id)
        d={}
        d['deptid']=e.Dept().DeptName
        d['badgenumber']=e.PIN
        d['username']=e.EName
        st1=st
        while st1<=et:
            dd=str(st1.month)+'-'+str(st1.day)
            d[dd]=''
            st1=st1+datetime.timedelta(1)
        att=transactions.objects.filter(UserID=id,TTime__gte=st,TTime__lt=et).order_by('TTime')
        for t in att:
            dd=str(t.TTime.month)+'-'+str(t.TTime.day)
            sTime=t.TTime.strftime('%H:%M')
            if dd in d.keys():
                d[dd]=d[dd]+' '+sTime
            else:
                d[dd]=sTime
        re.append(d.copy())
#               page_count =int(ceil(iCount/float(limit)))
    if offset>page_count:offset=page_count
    item_count =iCount
    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit+1
    Result['page_count']=page_count
    Result['datas']=re
    return Result

ENGINE_CHOICES = (
        'mysql',
        'sqlite3',
        'oracle',
        'ado_mssql'
)
YN_CHOICES = (
        (1, _('YES')),
        (0, _('NO')),
)

#@permission_required("iclock.DataBase")
#def setOptions(request):
#       request.user.iclock_url_rel='../..'
#       request.model = transaction
#       x = dict4ini.DictIni('attsite.ini')
#       WebPort = x.Options.Port
#       info={"WebPort":WebPort,"DbEngine":settings.DATABASE_ENGINE,"DatabaseName":settings.DATABASE_NAME,"DatabaseUser":settings.DATABASE_USER,"DatabasePassword":settings.DATABASE_PASSWORD,"DatabasePort":settings.DATABASE_PORT,"DatabaseHost":settings.DATABASE_HOST,"PIN_WIDTH":settings.PIN_WIDTH,"ENCRYPT":settings.ENCRYPT,"PAGE_LIMIT":settings.PAGE_LIMIT,"REALTIME":settings.TRANS_REALTIME,"AUTO_REG":settings.ICLOCK_AUTO_REG, "DBEC": ENGINE_CHOICES,"YN":YN_CHOICES }
#       if request.method=='GET':
#               return render_to_response('setoptions.html',info,
#                                                               RequestContext(request, {
#                                                               'from': 1,
#                                                               'page': 1,
#                                                               'limit': 10,
#                                                               'item_count': 4,
#                                                               'page_count': 1,
#                                                               'iclock_url_rel': request.user.iclock_url_rel,
#                                                               }))
#       else:
#               print request.POST
def init_database(request):
    if request.method=='GET':
        html='<div>are you sure to init</div>'
        return getJSResponse(html)

@login_required
def days_planner(request):
    userid=request.GET.get("UserID","0")
    return render_to_response('daysplanner.html',{"UserID":userid},
                                                    RequestContext(request, {
                                                    }))


#
#@permission_required("iclock.addDistribution_num_run")
#def processDistribution(request):
#       userid=request.POST.get("emp","")
#       deptIDs=request.POST.get("dept","")
#       K=request.POST.get("K")
#       pro=K.split(',')
#       Userids=userid.split(",")
#       isContainChild=request.POST.get("isContainChild","0")
#       if userid=="":
#               deptidlist=[int(i) for i in deptIDs.split(',')]
#               deptids=deptidlist
#               if isContainChild=="1":#是否包含下级部门
#                       for d in deptidlist:#支持选择多部门
#                               deptids=getAllAuthChildDept(d,request)
#               for dept in deptids:
#                       for p in pro:
#                               try:
#                                       prodeptmapping(processid=int(p),DeptID=int(dept),UserID=-1).save()
#                               except:
#                                       pass
#       else:
#               for users in Userids:
#                       for p in pro:
#                               try:
#                                       prodeptmapping(processid=int(p),DeptID=-1,UserID=users).save()
#                               except:
#                                       pass
#       return getJSResponse(u"result=0,message=%s"%_('Save Success'))
#
##删除选择审核流下的部门或员工
#@login_required
#def deleteDeptorUser(request):
#       sUsers=request.POST.get("sUsers","")
#       sDepts=request.POST.get("sDepts","")
#       Userids=sUsers.split(",")
#       deptIDs=sDepts.split(",")
#       keys=request.POST.getlist("K")
#       if sDepts!="":
#               prodeptmapping.objects.filter(processid__in=keys,DeptID__in=deptIDs).delete()
#       if sUsers!="":
#               prodeptmapping.objects.filter(processid__in=keys,UserID__in=Userids).delete()
#       return getJSResponse(u"result=0,message=%s"%_('Delete Success'))
#@login_required
def getRoles(request):
    role=userRoles.objects.all()
    ll=[]
    for r in role:
        ll.append(r.id)
    return getJSResponse(smart_str(dumps(ll)))
#获得选择审核流的所有部门
#@permission_required("iclock.Backup_Database")
def Backup_Database():
    import datetime
    import os
    despath="%s/backup/"%settings.APP_HOME
    despath=GetParamValue('opt_basic_backup_dir',despath)
    despath.replace("\\\\","/")
    if not os.path.exists(despath):
        if(os.mkdir(despath)) != None:
            return 1,"Save Failed"
    despath="%s%s_%s.zip"%(despath,settings.DATABASE_NAME,datetime.datetime.now().day)
    if settings.DATABASE_ENGINE=='mysql':
        dbpath=settings.APP_HOME+'/mysql/data/'+settings.DATABASE_NAME
        try:
            #dbpath="d:/mysql/data/"+settings.DATABASE_NAME
            dbpath.replace("\\\\","/")
            zipfolder(dbpath,despath,True)
        except:
            return 1,u"%s"%_("Save Failed")
    else:
        return 0,u"%s"%_("对于非mysql数据库,建议用数据库管理工具进行备份!")

    return 0,u"%s"%_("Save Success")

#
#@login_required
#def processdeptemps(request):
#       funid = request.REQUEST.get("func", "")
#       proid=request.GET.get("id").split(',')
#       q=request.GET.get('q',"")
#       dept_list=userDeptList(request.user)
#       q=unquote(q)
#       ll=[]
#       if funid=='employee':
#               emp=employee.objects.filter(DeptID__in=dept_list)
#               qs=prodeptmapping.objects.filter(processid__in=proid,UserID__in=emp)
#               if q!='':
#                       qs_id=[]
#                       for qss in qs:
#                               de=employee.objByID(qss.UserID)
#                               if str(de.PIN).find(q)!=-1 or de.EName.find(q)!=-1:
#                                       qs_id.append(qss.id)
#                       qs=qs.filter(id__in=qs_id)
#               #分页
#               try:
#                       offset = int(request.GET.get('p', 1))
#               except:
#                       offset=1
#               limit= int(request.GET.get('l', settings.PAGE_LIMIT))
#               paginator = Paginator(qs, limit)
#               item_count = paginator.count
#               if offset>paginator.num_pages: offset=paginator.num_pages
#               if offset<1: offset=1
#               pgList = paginator.page(offset)
#               for p in pgList.object_list:
#                       uu={}
#                       u=employee.objByID(p.UserID)
#                       uu['id']=u.id
#                       uu['PIN']=u.PIN
#                       uu['EName']=u.EName
#                       ll.append(uu)
#
#
#               cc={'latest_item_list': ll,
#                       'from': (offset-1)*limit+1,
#                       'item_count': item_count,
#                       'page': offset,
#                       'limit': limit,
#                       'page_count': paginator.num_pages,
#                       'title': (u"%s"%employee._meta.verbose_name).capitalize(),
#                       'dataOpt': employee._meta,
#                       }
#               tmpFile=request.GET.get('t')
#               return render_to_response(tmpFile, cc,RequestContext(request, {}))
#       elif funid=='department':
#               qs=prodeptmapping.objects.filter(processid__in=proid,DeptID__in=dept_list)
#               if q!='':
#                       qs_id=[]
#                       for qss in qs:
#                               de=department.objByID(qss.DeptID)
#                               if str(de.DeptID).find(q)!=-1 or de.DeptName.find(q)!=-1:
#                                       qs_id.append(qss.id)
#                       qs=qs.filter(id__in=qs_id)
#               #分页
#               try:
#                       offset = int(request.GET.get('p', 1))
#               except:
#                       offset=1
#               limit= int(request.GET.get('l', settings.PAGE_LIMIT))
#               paginator = Paginator(qs, limit)
#               item_count = paginator.count
#               if offset>paginator.num_pages: offset=paginator.num_pages
#               if offset<1: offset=1
#               pgList = paginator.page(offset)
#               for p in pgList.object_list:
#                       dd={}
#                       d=department.objByID(p.DeptID)
#                       dd['DeptID']=d.DeptID
#                       dd['DeptName']=d.DeptName
#                       ll.append(dd)
#               cc={'latest_item_list': ll,
#                       'from': (offset-1)*limit+1,
#                       'item_count': item_count,
#                       'page': offset,
#                       'limit': limit,
#                       'page_count': paginator.num_pages,
#                       'title': (u"%s"%department._meta.verbose_name).capitalize(),
#                       'dataOpt': department._meta,
#                       }
#               tmpFile=request.GET.get('t')
#               return render_to_response(tmpFile, cc,RequestContext(request, {}))
#       return getJSResponse({"ret":0,"message":""})
@login_required
def USER_SEARCH_SHIFTS(request):
    request.user.iclock_url_rel='../..'
    request.model = transactions
    unit=GetCalcUnit()
#       symbol=GetCalcSymbol()
    dc={}
#       dc['unit']=unit
#       dc['symbol']=symbol
    try:
        colModel=[]#transaction.colModels()
    except:
        colModel=[]
#       print "000000000000000000000000"
    return render(request,'search_shifts.html',
                                                     {'latest_item_list': smart_str(dumps(dc)),
                                                    'from': 1,
                                                    'page': 1,
                                                    'colModel':dumps(colModel),
                                                    'limit': 10,
                                                    'item_count': 4,
                                                    'page_count': 1,
                                                    'iclock_url_rel': request.user.iclock_url_rel
                                                    })

#@login_required
#def setprocess(request):
#       request.user.iclock_url_rel='../..'
#       request.model = transactions
#       unit=GetCalcUnit()
#       dc={}
#       try:
#               colModel=[]#transaction.colModels()
#       except:
#               colModel=[]
#       return render_to_response('process_list.html',
#                                                        {'latest_item_list': smart_str(dumps(dc)),
#                                                       'from': 1,
#                                                       'page': 1,
#                                                       'colModel':dumps(colModel),
#                                                       'limit': 10,
#                                                       'item_count': 4,
#                                                       'page_count': 1,
#                                                       'iclock_url_rel': request.user.iclock_url_rel
#                                                       },RequestContext(request, {}))

@login_required
def newplannertype(request):
    name=request.POST.get("name","")
    if name!='':
        Eventtype(typename=name).save()
    eal=Eventtype.objects.all()
    ll=[]
    for l in eal:
        lx={}
        lx['id']=l.id
        lx['name']=l.typename
        lx['color']=l.color
        lx['check']=0
        ll.append(lx)
    return getJSResponse({"ret":0,"message":ll})

@login_required
def delplannertype(request):
    id=request.POST.get("id","").split(",")
    etype=Eventtype.objects.filter(id__in=id)
    etype.delete()
    eal=Eventtype.objects.all()
    ll=[]
    for l in eal:
        lx={}
        lx['id']=l.id
        lx['name']=l.typename
        lx['color']=l.color
        lx['check']=0
        ll.append(lx)
    return getJSResponse({"ret":0,"message":ll})

@login_required
def colplannertype(request):
    color=request.POST.get("color","")
    id=request.POST.get("id","").split(",")
    etype=Eventtype.objects.filter(id__in=id)
    for i in etype:
        i.color=color
        i.save()
    eal=Eventtype.objects.all()
    ll=[]
    for l in eal:
        lx={}
        lx['id']=l.id
        lx['name']=l.typename
        lx['color']=l.color
        if l.id in id or str(l.id) in id:
            lx['check']=1
        else:
            lx['check']=0
        ll.append(lx)
    return getJSResponse({"ret":0,"message":ll})

@login_required
def selplannertype(request):
    eal=Eventtype.objects.all()
    ll=[]
    for l in eal:
        lx={}
        lx['id']=l.id
        lx['name']=l.typename
        lx['color']=l.color
        lx['check']=0
        ll.append(lx)
    return getJSResponse({"ret":0,"message":ll})

@login_required
def changeplanner(request):
    planid=request.POST.get("planid",0)
    days=request.POST.get("startDate","1900-01-01")
    start=request.POST.get("start","00:00:00")
    end=request.POST.get("end","00:00:00")
    descr=request.POST.get("descr","")
    alarm=request.POST.get("alarm","")
    notify=request.POST.get("notify","0")
    if notify=="":
        notify="0"
    unit=request.POST.get("unit","")
    types=request.POST.get("types","")
    phone=request.POST.get("phone","")
    group=request.POST.get("group","")
    note=request.POST.get("note","")
    allDay=request.POST.get("allDay","")
    if group!="":
        groupid=Eventtype.objects.get(id=group)
    st=datetime.datetime.strptime(days+" "+start,'%Y-%m-%d %H:%M')
    et=datetime.datetime.strptime(days+" "+end,'%Y-%m-%d %H:%M')
    if et<st:
        et=et+datetime.timedelta(days=1)
    sts=st.strftime('%Y-%m-%d')
    ets=et.strftime('%Y-%m-%d')
    ll=[]
    if descr!="":
        plan=daysPlanner.objects.get(id=planid)
        try:

            if alarm=='true':
                start=datetime.time(st.hour,st.minute)
                end=datetime.time(et.hour,et.minute)
                if  notify!="0":
                    if unit=="1":
                        st=st-datetime.timedelta(hours=int(notify))
                    elif unit=="2":
                        st=st-datetime.timedelta(minutes=int(notify))
                    else:
                        st=st-datetime.timedelta(days=int(notify))
                now=datetime.datetime.now()
                plan.StartDate=sts
                plan.EndDate=ets
                plan.StartTime=start
                plan.EndTime=end
                plan.description=descr
                plan.note=note
                plan.isalarm=1
                plan.notify=notify
                plan.Unit=unit
                plan.AlarmType=types
                plan.phoneoremail=phone
                plan.allDay=allDay
                if group!='':
                    plan.type=groupid
                else:
                    plan.type =None
                if plan.alarmid:
                    ala=Alarmclock.objects.get(id=plan.alarmid.id)
                    ala.StartTime=st
                    ala.AlarmType=types
                    ala.photooremail=phone
                    ala.description=descr
                    ala.State=0
                    ala.save()
                else:
                    Alarmclock(StartTime=st,AlarmType=types,photooremail=phone,description=descr,title=u"工作计划提醒",State=0,ApplyDate=now).save()
                    Alarmc=Alarmclock.objects.filter(ApplyDate=now,StartTime=st,photooremail=phone,description=descr)
                    plan.alarmid=Alarmc[0]
            else:
                start=datetime.time(st.hour,st.minute)
                end=datetime.time(et.hour,et.minute)
                plan.StartDate=sts
                plan.EndDate=ets
                plan.StartTime=start
                plan.EndTime=end
                plan.description=descr
                plan.note=note
                plan.isalarm=0
                plan.notify=0
                plan.Unit=unit
                plan.AlarmType=types
                plan.phoneoremail=phone
                plan.allDay=allDay
                if group!='':
                    plan.type=groupid
                else:
                    plan.type =None
                if plan.alarmid:
                    ala=Alarmclock.objects.get(id=plan.alarmid.id)
                    ala.State=2
                    ala.save()
            plan.save()
        except Exception,e:
            print e
        star=plan.StartTime.strftime('%H:%M')
        endt=plan.EndTime.strftime('%H:%M')
        ll.append(planid)
        ll.append("%s %s"%(sts,star))
        ll.append("%s %s"%(ets,endt))
        ll.append(descr)
        ll.append(plan.allDay)
    else:
        getJSResponse({"ret":1,"message":""})
    return getJSResponse({"ret":0,"message":ll})


@login_required
def delplanner(request):
    id=request.POST.get("planid",0)
    try:
        daysPlanner.objects.get(id=id).delete()
    except:
        return getJSResponse({"ret":1,"message":""})
    return getJSResponse({"ret":0,"message":""})

@login_required
def addplanner(request):
    days=request.POST.get("startDate","1900-01-01")
    start=request.POST.get("start","00:00:00")
    end=request.POST.get("end","00:00:00")
    descr=request.POST.get("descr","")
    alarm=request.POST.get("alarm","")
    notify=request.POST.get("notify","0")
    if notify=="":
        notify="0"
    unit=request.POST.get("unit","")
    types=request.POST.get("types","")
    phone=request.POST.get("phone","")
    group=request.POST.get("group","")
    note=request.POST.get("note","")
    allDay=request.POST.get("allDay","")
    if allDay:
        allDay=1
    else:
        allDay=0
    if group!="":
        groupid=Eventtype.objects.get(id=group)
    st=datetime.datetime.strptime(days+" "+start,'%Y-%m-%d %H:%M')
    et=datetime.datetime.strptime(days+" "+end,'%Y-%m-%d %H:%M')
    if et<st:
        et=et+datetime.timedelta(days=1)
    sts=st.strftime('%Y-%m-%d')
    ets=et.strftime('%Y-%m-%d')
    username=request.user.username
    ll=[]
    if descr!="":
        if alarm=='true':
            start=datetime.time(st.hour,st.minute)
            end=datetime.time(et.hour,et.minute)
            if  notify!="0":
                if unit=="1":
                    st=st-datetime.timedelta(hours=int(notify))
                elif unit=="2":
                    st=st-datetime.timedelta(minutes=int(notify))
                else:
                    st=st-datetime.timedelta(days=int(notify))
            now=datetime.datetime.now()
            Alarmclock(StartTime=st,AlarmType=types,photooremail=phone,description=descr,title=u"工作计划提醒",State=0,ApplyDate=now).save()
            Alarmc=Alarmclock.objects.filter(ApplyDate=now,StartTime=st,photooremail=phone,description=descr)
            if group=='':
                if username=='employee':
                    emp=request.POST.get("emp")
                    daysPlanner(StartDate=sts,EndDate=ets,StartTime=start,EndTime=end,description=descr,note=note,isalarm=1,notify=notify,Unit=unit,AlarmType=types,phoneoremail=phone,alarmid=Alarmc[0],userid=request.user,employeeID=emp,allDay=allDay).save()
                else:
                    daysPlanner(StartDate=sts,EndDate=ets,StartTime=start,EndTime=end,description=descr,note=note,isalarm=1,notify=notify,Unit=unit,AlarmType=types,phoneoremail=phone,alarmid=Alarmc[0],userid=request.user,allDay=allDay).save()
            else:
                if username=='employee':
                    emp=request.POST.get("emp")
                    daysPlanner(StartDate=sts,EndDate=ets,StartTime=start,EndTime=end,description=descr,note=note,type=groupid,isalarm=1,notify=notify,Unit=unit,AlarmType=types,phoneoremail=phone,alarmid=Alarmc[0],userid=request.user,employeeID=emp,allDay=allDay).save()
                else:
                    daysPlanner(StartDate=sts,EndDate=ets,StartTime=start,EndTime=end,description=descr,note=note,type=groupid,isalarm=1,notify=notify,Unit=unit,AlarmType=types,phoneoremail=phone,alarmid=Alarmc[0],userid=request.user,allDay=allDay).save()
        else:
            start=datetime.time(st.hour,st.minute)
            end=datetime.time(et.hour,et.minute)
            if group=='':
                if username=='employee':
                    emp=request.POST.get("emp")
                    daysPlanner(StartDate=sts,EndDate=ets,StartTime=start,EndTime=end,description=descr,note=note,userid=request.user,employeeID=emp,allDay=allDay).save()
                else:
                    daysPlanner(StartDate=sts,EndDate=ets,StartTime=start,EndTime=end,description=descr,note=note,userid=request.user,allDay=allDay).save()
            else:
                if username=='employee':
                    emp=request.POST.get("emp")
                    daysPlanner(StartDate=sts,EndDate=ets,StartTime=start,EndTime=end,description=descr,note=note,type=groupid,userid=request.user,employeeID=emp,allDay=allDay).save()
                else:
                    daysPlanner(StartDate=sts,EndDate=ets,StartTime=start,EndTime=end,description=descr,note=note,type=groupid,userid=request.user,allDay=allDay).save()
        if username=='employee':
            emp=request.POST.get("emp")
            plan=daysPlanner.objects.filter(StartDate=sts,StartTime=start,description=descr,userid=request.user.id,employeeID=emp,allDay=allDay)
        else:
            plan=daysPlanner.objects.filter(StartDate=sts,StartTime=start,description=descr,userid=request.user.id,allDay=allDay)
        for p in plan:
            star=p.StartTime.strftime('%H:%M')
            endt=p.EndTime.strftime('%H:%M')
            ll.append(p.id)
            ll.append("%s %s"%(sts,star))
            ll.append("%s %s"%(ets,endt))
            ll.append(p.description)
            ll.append(p.allDay)
            break
    else:
        getJSResponse({"ret":1,"message":""})
    return getJSResponse({"ret":0,"message":ll})

@login_required
def selplanner(request):
    st=request.POST.get("st",'2012-01-01')
    st=datetime.datetime.strptime(st,'%Y-%m-%d')
    st=datetime.date(st.year,st.month,1)
    et=st+datetime.timedelta(days=31)
    emp=request.POST.get("emp")
    if emp!=0 and emp!="0":
        plan=daysPlanner.objects.filter(StartDate__gte=st,StartDate__lt=et,userid=request.user.id,employeeID=emp)
    else:
        plan=daysPlanner.objects.filter(StartDate__gte=st,StartDate__lt=et,userid=request.user.id)
    tt=[]
    for p in plan:
        sts=p.StartDate.strftime('%Y-%m-%d')
        ets=p.EndDate.strftime('%Y-%m-%d')
        star=p.StartTime.strftime('%H:%M')
        endt=p.EndTime.strftime('%H:%M')
        ll={}
        ll['id']=p.id
        ll['st']="%s %s"%(sts,star)
        ll['et']="%s %s"%(ets,endt)
        ll['desc']=p.description
        ll['allDay']=p.allDay
        tt.append(ll)
    return getJSResponse({"ret":0,"message":tt})

@login_required
def selplannerbyid(request):
    id=request.POST.get("id")
    try:
        p=daysPlanner.objects.get(id=id)
        ll={}
        ll['id']=p.id
        ll['startDay']=p.StartDate.strftime('%Y-%m-%d')
        ll['description']=p.description
        ll['StartTime']=p.StartTime.strftime("%H:%M")
        ll['EndTime']=p.EndTime.strftime("%H:%M")
        ll['alarm']=p.isalarm
        ll['notify']=p.notify
        ll['unit']=p.Unit
        ll['type']=p.AlarmType
        ll['phone']=p.phoneoremail
        ll['note']=p.note
        if p.type:
            ll['groupx']=p.type.id
        else:
            ll['groupx']=""
        eal=Eventtype.objects.all()
        tt=[]
        for l in eal:
            lx={}
            lx['id']=l.id
            lx['name']=l.typename
            lx['color']=l.color
            if l.id==ll['groupx']:
                lx['check']=1
            else:
                lx['check']=0
            tt.append(lx)
        ll['group']=tt
    except:
        return getJSResponse({"ret":1,"message":""})
    return getJSResponse({"ret":0,"message":ll})

@login_required
def moveplannerbyid(request):
    id=request.POST.get("id")
    dayDelta=request.POST.get("dayDelta",0)
    minuteDelta=request.POST.get("minuteDelta",0)
    allDay=request.POST.get("allDay",False)
    if allDay=="true" or allDay==True:
        allDay=1
    else:
        allDay=0
    try:
        p=daysPlanner.objects.get(id=id)
        if dayDelta!=0 and dayDelta!="0":
            EndDate=p.EndDate+datetime.timedelta(days=int(dayDelta))
            p.EndDate=EndDate
            StartDate=p.StartDate+datetime.timedelta(days=int(dayDelta))
            p.StartDate=StartDate
        if minuteDelta!=0 and minuteDelta!="0":
            EndTime=datetime.datetime(2012,1,1,p.EndTime.hour,p.EndTime.minute)+datetime.timedelta(minutes=int(minuteDelta))
            p.EndTime=EndTime.strftime("%H:%M")
            StartTime=datetime.datetime(2012,1,1,p.StartTime.hour,p.StartTime.minute)+datetime.timedelta(minutes=int(minuteDelta))
            p.StartTime=StartTime.strftime("%H:%M")
        p.allDay=allDay
        p.save()
    except:
        return getJSResponse({"ret":1,"message":""})
    return getJSResponse({"ret":0,"message":""})

@login_required
def resizeplannerbyid(request):
    id=request.POST.get("id")
    dayDelta=request.POST.get("dayDelta",0)
    minuteDelta=request.POST.get("minuteDelta",0)
    allDay=request.POST.get("allDay",False)
    if allDay=="true" or allDay==True:
        allDay=1
    else:
        allDay=0
    try:
        p=daysPlanner.objects.get(id=id)
        if dayDelta!=0 and dayDelta!="0":
            EndDate=p.EndDate+datetime.timedelta(days=int(dayDelta))
            p.EndDate=EndDate
        if minuteDelta!=0 and minuteDelta!="0":
            EndTime=datetime.datetime(2012,1,1,p.EndTime.hour,p.EndTime.minute)+datetime.timedelta(minutes=int(minuteDelta))
            p.EndTime=EndTime.strftime("%H:%M")
        p.allDay=allDay
        p.save()
    except:
        return getJSResponse({"ret":1,"message":""})
    return getJSResponse({"ret":0,"message":""})


@login_required
def saveannualdays(request):
    DeptID=request.POST.get("DeptID","")
    emp=request.POST.get("emp","").split(",")
    ischecked=request.POST.get("ischecked",0)
    years=request.POST.get("year",'')
    days=request.POST.get("days",'')
    if years=='' or days=='':
        return getJSResponse({"ret":1,"message":""})
    if len(emp)>0 and emp!='null' and emp!=[u'']:
        emps=employee.objects.filter(id__in=emp,OffDuty__lt=1)
    elif DeptID!="":
        deptids=[]
        deptids.append(DeptID)
        if ischecked=="1": #是否包含下级部门
            deptids=getAllAuthChildDept(int(DeptID),request)
        emps=employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1)
    ann=annual_leave.objects.filter(UserID__in=emps,inyear=years)
    for a in ann:
        a.annual_attach=days
        a.save()
    for e in emps:
        try:
            annual_leave(UserID=e,inyear=years,annual_attach=days).save()
        except:
            pass
    return getJSResponse({"ret":0,"message":""})


@login_required
def getannualsettings(request):
    setting=annual_settings.objects.all()
    ll={}
    max=0
    for s in setting:
        try:
            seq=int(s.Sequence)
            if seq>max:
                max=seq
        except:
            pass
        ll[s.Name+'_'+s.Type+'_'+s.Sequence]=s.Value
    ll['maxcount']=max
    return getJSResponse({"ret":0,"message":ll})

@login_required
def submitAnnSet(request):
    keys=request.POST.get("K")
    c=request.POST.get("counts")
    keys=eval(keys)
    for k in keys:
        ann=annual_settings.objects.filter(Name=k['Name'],Type=k['Type'],Sequence=k['Sequence'])
        if ann.count()>0:
            for a in ann:
                a.Value=k['Value']
                a.save()
        else:
            annual_settings(Name=k['Name'],Type=k['Type'],Value=k['Value'],Sequence=k['Sequence']).save()
    nu=annual_settings.objects.exclude(Sequence='')
    for n in nu:
        try:
            if int(n.Sequence)>int(c):
                n.delete()
        except:
            pass
    return getJSResponse({"ret":0,"message":""})

def getuserannual(UserID,today):
    try:
        nu=annual_settings.objects.all()
        ll={}
        for n in nu:
            ll[n.Name+'_'+n.Type+'_'+n.Sequence]=n.Value
        annuals=0
        to=datetime.datetime.strptime(today,'%Y-%m-%d')
        to=datetime.datetime(to.year,int(ll['month_s__']),int(ll['day_s__']),0,0)
        toyear=to.year
        annual=annual_leave.objects.filter(UserID=UserID,inyear=toyear)
        if annual.count()>0:
            ann=sheru(annual[0].annual_attach,ll['RemaindProc__'])
            return ann
        if  ll['type_b__']=='1' or ll['type_b__']==1:
            annuals=getannual_f(UserID,today,ll)
        elif ll['type_b__']=='2' or ll['type_b__']==2:
            annuals=getannual_g(UserID,today,ll)
    except:
        annuals=0
    return annuals

def getannual_f(UserID,today,ll=True):
    ann=0
    if ll==True:
        nu=annual_settings.objects.all()
        ll={}
        for n in nu:
            ll[n.Name+'_'+n.Type+'_'+n.Sequence]=n.Value
    emp=employee.objByID(UserID)
    times=''
    if ll['type_f__']=='Hiredday':
        times=emp.Hiredday
    elif ll['type_f__']=='Trialstarttime':
        times=emp.Trialstarttime
    elif ll['type_f__']=='Trialendtime':
        times=emp.Trialendtime
    elif ll['type_f__']=='Contractstarttime':
        times=emp.Contractstarttime

    if times:
        #print 'times',times
        to=datetime.datetime.strptime(today,'%Y-%m-%d')
        to=datetime.datetime(to.year,int(ll['month_s__']),int(ll['day_s__']),0,0)
        m=0
        y=0
        y1=to.year
        #print 'to',to
        m1=to.month
        y2=times.year
        m2=times.month
        if (y1>y2) or ((y1==y2) and (m1>m2)):
            if m1>=m2:
                m=m1-m2
                y=y1-y2
            else:
                m=m1+12-m2
                y=y1-y2-1
        st=checkTime(times)
        if (st.year%4==0 and st.year%100!=0) or (st.year%400==0):
            if st.month==2 and st.day==29:
                st1=datetime.datetime(st.year+1,st.month,st.day-1,0,0)
            else:
                st1=datetime.datetime(st.year+1,st.month,st.day,0,0)
        else:
            st1=datetime.datetime(st.year+1,st.month,st.day,0,0)
        tag=0
        if not (y==0 and m==0):
#                       y+=1
            tag=1
        if (y==0 and m!=0) or (y==1 and tag==1):
            if to>st1:
                ann='%.2f'%(5*(to-st1).days/365.0)
            else:
                ann=0
        elif y>=1 and y<10:
            ann=5
        elif y>=10 and y<20:
            ann=10
        elif y>=20:
            ann=15
        ann=sheru(ann,ll['RemaindProc__'])
    else:
        return ''
    return ann
def getannual_g(UserID,today,ll=True):
    ann=0
    if ll==True:
        nu=annual_settings.objects.all()
        ll={}
        for n in nu:
            ll[n.Name+'_'+n.Type+'_'+n.Sequence]=n.Value
    emp=employee.objByID(UserID)
    times=''
    if ll['type_g_'+ll['guize__']+'_']=='Hiredday':
        times=emp.Hiredday
    elif ll['type_g_'+ll['guize__']+'_']=='Trialstarttime':
        times=emp.Trialstarttime
    elif ll['type_g_'+ll['guize__']+'_']=='Trialendtime':
        times=emp.Trialendtime
    elif ll['type_g_'+ll['guize__']+'_']=='Contractstarttime':
        times=emp.Contractstarttime
    to=datetime.datetime.strptime(today,'%Y-%m-%d')
    to=datetime.datetime(to.year,int(ll['month_s__']),int(ll['day_s__']),0,0)
    toyear=to.year
    tag=0
    if times:
        m=0
        y=0
        y1=toyear
        m1=to.month
        y2=times.year
        m2=times.month
        if (y1>y2) or ((y1==y2) and (m1>m2)):
            if m1>=m2:
                m=m1-m2
                y=y1-y2
            else:
                m=m1+12-m2
                y=y1-y2-1
        st=checkTime(times)
        if ll['guize__']==1 or ll['guize__']=='1':
            try:
                day_g_1=float(ll['day_g_1_'])
            except:
                day_g_1=0
            try:
                month_g_1_=float(ll['month_g_1_'])
            except:
                month_g_1_=0
            if y==0 and m!=0:
                ann='%.2f'%(day_g_1*((to-st).days/30)/month_g_1_)
            elif y>=1 :
                ann='%.2f'%(day_g_1*12/month_g_1_)
        elif ll['guize__']==2 or ll['guize__']=='2':
            if  not (y==0 and m==0):
                y+=1
                tag=1
            try:
                xi_g_2_=float(ll['xi_g_2_'])
            except:
                xi_g_2_=0
            try:
                man_g_2_=float(ll['man_g_2_'])
            except:
                man_g_2_=0
            try:
                zeng_g_2_=float(ll['zeng_g_2_'])
            except:
                zeng_g_2_=0
            try:
                max_g_2_=float(ll['max_g_2_'])
            except:
                max_g_2_=0
            if (y==0 and m!=0) or (y==1 and tag==1):
                ann='%.2f'%(xi_g_2_*(to-st).days/365.0)
            elif y>=1:
                ann='%.2f'%(man_g_2_+(y-1)*zeng_g_2_)
            if float(ann)>=max_g_2_:
                ann='%.2f'%max_g_2_
        elif ll['guize__']==3 or ll['guize__']=='3':
            if  not (y==0 and m==0):
                y+=1
                tag=1
            try:
                xi_g_3_=float(ll['xi_g_3_'])
            except:
                xi_g_3_=0
            try:
                day_1_10_3_=float(ll['day_1_10_3_'])
            except:
                day_1_10_3_=0
            try:
                day_10_20_3_=float(ll['day_10_20_3_'])
            except:
                day_10_20_3_=0
            try:
                day_20_3_=float(ll['day_20_3_'])
            except:
                day_20_3_=0

            if (y==0 and m!=0) or (y==1 and tag==1):
                ann='%.2f'%(xi_g_3_*(to-st).days/365.0)
            elif y>=1 and y<10:
                ann='%.2f'%day_1_10_3_
            elif y>=10 and y<20:
                ann='%.2f'%day_10_20_3_
            elif y>=20:
                ann='%.2f'%day_20_3_
        elif ll['guize__']==4 or ll['guize__']=='4':
            if  not (y==0 and m==0):
                y+=1
                tag=1
            try:
                xi_g_4_=float(ll['xi_g_4_'])
            except:
                xi_g_4_=0

            if (y==0 and m!=0) or (y==1 and tag==1):
                ann='%.2f'%(xi_g_4_*(to-st).days/365.0)
            else:
                i=1
                while y>0:
                    try:
                        try:
                            nian_s_4_=float(ll['nian_s_4_'+str(i)])
                        except:
                            break
                        try:
                            nian_e_4_=float(ll['nian_e_4_'+str(i)])
                        except:
                            break
                        try:
                            nian_day_4_=float(ll['nian_day_4_'+str(i)])
                        except:
                            nian_day_4_=0

                        if y>=nian_s_4_ and y<nian_e_4_:
                            ann='%.2f'%nian_day_4_
                    except:
                        break
                    i+=1
            if y>=float(ll['nian_end_4_']):
                ann='%.2f'%float(ll['nian_day_end_4_'])
        ann=sheru(ann,ll['RemaindProc__'])
    else:
        return ''
    return ann

def sheru(val,tag):
    rval=float(val)
    ival=int(rval)
    if tag==0 or tag=='0':
        rval='%.f'%ival
    elif tag==1 or tag=='1':
        rval='%.f'%rval
    elif tag==2 or tag=='2':
        if rval>ival:
            rval='%.f'%(ival+1)
        else:
            rval='%.f'%ival
    return rval
#生成人事提醒数据
def calchrreminddata(request,uid,cometime):
    tzs=[]
    item=uid
    if cometime=="" or len(cometime)==0:
        now=datetime.datetime.now()
    else:
        now=datetime.datetime.strptime(cometime,'%Y-%m-%d')
    year=now.year
    month=now.month+1
    if now.month==12:
        year=year+1
        month=1
    nextmonth=datetime.datetime(year=year,month=month,day=1)
    l=[]
    #当天生日查询
    if int(item)==1:
        l=employee.objects.filter(Birthday__month=now.month,Birthday__day=now.day)

    #当月生日查询
    if int(item)==2:
        l=employee.objects.filter(Birthday__month=now.month)

    #下月生日查询
    if int(item)==3:
        l=employee.objects.filter(Birthday__month=nextmonth.month)

    #当月合同查询
    if int(item)==4:
        l=employee.objects.filter(Contractendtime__month=now.month)
    #当天合同查询
    if int(item)==5:
        l=employee.objects.filter(Contractendtime__month=now.month,Contractendtime__day=now.day)
    #下月合同查询
    if int(item)==6:
        l=employee.objects.filter(Contractendtime__month=nextmonth.month)

    #当月试用期合同查询
    if int(item)==7:
        l=employee.objects.filter(Trialendtime__month=now.month)
    #当天试用期合同查询
    if int(item)==8:
        l=employee.objects.filter(Trialendtime__month=now.month,Trialendtime__day=now.day)
    #下月试用期合同查询
    if int(item)==9:
        l=employee.objects.filter(Trialendtime__month=nextmonth.month)
    #离职员工总人数
    if int(item)==10:
        l=employee.objects.filter(OffDuty=1)
    #该年新加入员工
    if int(item)==11:
        l=employee.objects.filter(Hiredday__year=now.year)
    #入职周年人数
    if int(item)==12:
        if (now.year%4 == 0 and (now.year%100 != 0 or now.year%400 == 0) ):
            l=employee.objects.filter(Hiredday__month=now.month,Hiredday__day=now.day)
        else:
            if now.month==2 and now.day==28:
                l=employee.objects.filter(Hiredday__month=now.month).filter(Q(Hiredday__day=28)|Q(Hiredday__day=29))
            else:
                l=employee.objects.filter(Hiredday__month=now.month,Hiredday__day=now.day)

        #l=employee.objects.filter(Hiredday__month=now.month,Hiredday__day=now.day)
    if int(item)==13:
        leaveday=now.day
        leavemonth=now.month
        leaveyear=now.year
        if now.month==2:
            if (now.year%4 == 0 and (now.year%100 != 0 or now.year%400 == 0) ):
                if now.day+7>29:
                    leaveday=now.day+7-29
                    leavemonth=now.month+1
                else:
                    leaveday=now.day+7
            else:
                if now.day+7>28:
                    leaveday=now.day+7-28
                    leavemonth=now.month+1
                else:
                    leaveday=now.day+7
        elif now.month in [1,3,5,7,8,10]:
            if now.day+7>31:
                leaveday=now.day+7-31
                leavemonth=now.month+1
            else:
                leaveday=now.day+7
        elif now.month in [4,6,9,11]:
            if now.day+7>30:
                leaveday=now.day+7-30
                leavemonth=now.month+1
            else:
                leaveday=now.day+7
        else:
            if now.day+7>31:
                leaveday=now.day+7-31
                leavemonth=1
                leaveyear=leaveyear+1
            else:
                leaveday=now.day+7
        try:
            sevendays=datetime.datetime(year=leaveyear,month=leavemonth,day=leaveday)
            print sevendays,now
            l=USER_SPEDAY.objects.filter(State=2,EndSpecDay__lte=sevendays,StartSpecDay__gte=now)
        except Exception,ee:
            l=[]
            print ee

    if int(item)==1 or int(item)==2 or int(item)==3:
        for t in l:
            d={}
            d['pin']=t.PIN
            d['name']=t.EName
            d['dept']=t.DeptID.DeptName
            d['sex']=getSex(t.Gender)
            d['Birthday']=t.Birthday.strftime("%Y-%m-%d")
            tzs.append(d.copy())
    elif int(item)==4 or int(item)==5 or int(item)==6:
        for t in l:
            d={}
            d['pin']=t.PIN
            d['name']=t.EName
            d['dept']=t.DeptID.DeptName
            d['sex']=getSex(t.Gender)
            try:
                if t.Contractstarttime:
                    d['contractstart']=t.Contractstarttime.strftime("%Y-%m-%d")
                if t.Contractendtime:
                    d['contractend']=t.Contractendtime.strftime("%Y-%m-%d")
            except Exception,ee:
                print ee
            tzs.append(d.copy())
    elif int(item)==7 or int(item)==8 or int(item)==9:
        for t in l:
            d={}
            d['pin']=t.PIN
            d['name']=t.EName
            d['dept']=t.DeptID.DeptName
            d['sex']=getSex(t.Gender)
            try:
                if t.Trialstarttime:
                    d['Trialstarttime']=t.Trialstarttime.strftime("%Y-%m-%d")
                if t.Trialendtime:
                    d['Trialendtime']=t.Trialendtime.strftime("%Y-%m-%d")
            except Exception,ee:
                print ee
            tzs.append(d.copy())
    elif int(item)==10:
        for t in l:
            d={}
            d['pin']=t.PIN
            d['name']=t.EName
            d['dept']=t.DeptID.DeptName
            d['sex']=getSex(t.Gender)
            tzs.append(d.copy())
    elif int(item)==11:
        for t in l:
            d={}
            d['pin']=t.PIN
            d['name']=t.EName
            d['dept']=t.DeptID.DeptName
            d['sex']=getSex(t.Gender)
            d['Hiredday']=t.Hiredday.strftime("%Y-%m-%d")
            tzs.append(d.copy())
    elif int(item)==12:
        for t in l:
            d={}
            d['pin']=t.PIN
            d['name']=t.EName
            d['dept']=t.DeptID.DeptName
            d['sex']=getSex(t.Gender)
            d['Hiredday']=t.Hiredday.strftime("%Y-%m-%d")
            d['countyear']=now.year-t.Hiredday.year
            tzs.append(d.copy())
    elif int(item)==13:
        for t in l:
            d={}
            d['pin']=t.UserID.PIN
            d['name']=t.UserID.EName
            d['dept']=t.UserID.DeptID.DeptName
            d['sex']=getSex(t.UserID.Gender)
            d['StartSpecDay']=t.StartSpecDay.strftime("%Y-%m-%d")
            d['EndSpecDay']=t.EndSpecDay.strftime("%Y-%m-%d")
            tzs.append(d.copy())

    datas=tzs
    return datas


def setoptionAttParam(request):
    ErrorDelay=request.POST.get("ErrorDelay")
    Delay=request.POST.get("Delay")
    Realtime=request.POST.get("Realtime")
    TransTimes=request.POST.get("TransTimes")
    TransInterval=request.POST.get("TransInterval")
    compwd=request.POST.get("compwd")
    TransType=request.POST.get("TransType")
    TransType=('0000000000%s'%TransType)[-10:]
    try:
        Delay=int(Delay)
    except:
        Delay=60
    try:
        TransInterval=int(TransInterval)
    except:
        TransInterval=1
    try:
        tt=TransTimes.split(";")
        timestr=""
        for t in tt:
            if t.find(":")!=-1:
                ts=t.split(":")
                t1=int(ts[0])
                t2=int(ts[1])
                if t1>24 or t2>60:
                    continue
                t2='00%s'%t2
                t2=t2[-2:]
                timestr+='%s:%s;'%(t1,t2)
        TransTimes=timestr
    except:
        TransTimes='0:00'

    SetParamValue("ErrorDelay", ErrorDelay)
    SetParamValue("Delay", Delay)
    SetParamValue("Realtime", Realtime)
    SetParamValue("TransTimes", TransTimes)
    SetParamValue("TransInterval", TransInterval)
    SetParamValue("TransType", TransType)
    SetParamValue("compwd", compwd)
    settings.MAX_DEVICES_STATE=int(Delay)+20
    if settings.MAX_DEVICES_STATE<=300:
        settings.MAX_DEVICES_STATE=320
    objs=iclock.objects.all().exclude(DelTag=1).exclude(State=0)
    for dev in objs:
        appendDevCmd(dev, "INFO")


    return getJSResponse({"ret":0,"message":""})

def getoptionAttParam(request):
    ll=getoptionsAttParam()
    return getJSResponse({"ret":0,"message":ll})

def gettimediff(et,st):
    """修改为按天请假，暂时不在计算小时"""
    st1=datetime.datetime(st.year,st.month,st.day,0,0)
    et1=datetime.datetime(et.year,et.month,et.day,0,0)
    days=1
    while True:
        st1+=datetime.timedelta(days=1)
        if st1<=et:
            days+=1
        else:
            break
    return days
    #diff=et-st
    #min=int(GetParamValue('MinsWorkDay'))
    #minunit=0
    #if diff.seconds/60>min:
    #       minunit+=min
    #else:
    #       minunit+=diff.seconds/60
    #minunit+=diff.days*min
    #return minunit

#def gettimediff_byshift(id,et,st):
#       st1=st-datetime.timedelta(days=2)
#       et1=et+datetime.timedelta(days=2)
#       userplan=LoadSchPlanEx(id,True,True)
#       l=GetUserScheduler(int(id), st1, et1, userplan['HasHoliday'])
#       sumvalue=0
#       for s in l:
#               value=0
#               if et<s['TimeZone']['StartTime'] or st>s['TimeZone']['EndTime']:
#                       pass
#               else:
#                       if s['IsCalcRest']:
#                               value+=s['WorkMins']-s['RestTime']
#                       else:
#                               value=s['WorkMins']
#                       if s['TimeZone']['StartTime']<st:
#                               sst=st-s['TimeZone']['StartTime']
#                               value=value-sst.seconds/60-sst.days*60*24
#                       if s['TimeZone']['EndTime']>et:
#                               eet=s['TimeZone']['EndTime']-et
#                               value=value-eet.seconds/60-eet.days*60*24
#               sumvalue+=value
#       return sumvalue

@login_required
def save_empleave(request,key):
    import time
    if request.method=="POST":
        userids=request.POST.get('UserID','')
        ld=request.POST.get('leavedate','')

        ld = ld.split(' ')[0]
        t=time.strptime(ld, '%Y-%m-%d')
        y,m,d = t[0:3]
        ldate = datetime.datetime(y,m,d)

        ltype=request.POST.get('leavetype','0')
        reas=request.POST.get('reason','')
        try:
            if key=="_new_":
                userids=userids.split(',')
                emps=employee.objects.filter(id__in = userids).exclude(DelTag=1)
                for emp in emps:
                    try:
                        leavelogs=empleavelog.objects.filter(UserID=emp)
                        if leavelogs:
                            for leavelog in leavelogs:
                                leavelog.leavedate = ldate
                                leavelog.leavetype = ltype
                                leavelog.reason = reas
                                leavelog.createtime = datetime.datetime.now()
                                leavelog.deltag = 0
                                leavelog.save()
                        else:
                            empleav = empleavelog()
                            empleav.UserID = emp
                            empleav.leavedate = ldate
                            empleav.leavetype = ltype
                            empleav.reason = reas
                            empleav.createtime = datetime.datetime.now()
                            empleav.save()

                            emp.OffDuty = 1
                            emp.save()
                    except Exception,ee:
                        print ee

        except Exception,e:
            return getJSResponse({"ret":1,"message":u'%s'%_('The specail has been applied!')})
        return getJSResponse({"ret":0,"message":u'%s'%_("Save Success")})

def save_speday_file(request,fname,id):
    file = request.FILES.get("spedy_file",'')
    if file:
        fname.append(str(id)+u'_'+file.name)
        file_dir="%s%s/%s"%(settings.ADDITION_FILE_ROOT,'userSpredyFile',fname[0])
        extendName=fname[0].split('.')[-1].upper()
        if extendName=='PDF':
            try:
                f = open(file_dir,'wb')#上传文件写入
                f.write(file.read())
                f.close()
            except IOError:
                return getJSResponse({"ret":1,"message":u'%s'%_(u'保存PDF失败')})
        elif extendName in ['JPG','BMP','JPEG','PNG']:
            try:
                from mysite.iclock.datamisc import saveUploadImage2
                saveUploadImage2(request, "spedy_file", file_dir)
            except:
                return getJSResponse({"ret":1,"message":u'%s'%_(u'保存图片失败')})
        else:
            return getJSResponse({"ret":1,"message":u'%s'%_(u'文件格式错误')})