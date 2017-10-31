#coding=utf-8
from mysite.iclock.models import *
from django.utils.encoding import smart_str
from mysite.iclock.datautils import *
from django.shortcuts import render_to_response,render
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from mysite.iclock.datasproc import trunc
from mysite.acc.models import *
from mysite.utils import *
#import json
MAX_REALTIME_COUNT=50
g_rtstate={}
g_doorstate={}
def get_recordColModel():
    Result=[{'name':'id','hidden':True}]
    for i in range(10):
        Result.append({'name':'door%s'%(i),'sortable':False,'width':90,'title':False,'resizable':False,'align':'center','label':''})
    return Result

def get_door_state(val, doorno):
    if doorno==1:
        return (val & 0x00000000000000000000FF)
    elif doorno == 2:
        return (val & 0x000000000000000000FF00) >> 8
    elif doorno == 3:
        return (val & 0x0000000000000000FF0000) >> 16
    elif doorno == 4:
        return (val & 0x00000000000000FF000000) >> 24
    elif doorno == 5:
        return (val & 0x000000000000FF00000000) >> 32
    elif doorno == 6:
        return (val & 0x0000000000FF0000000000) >> 40
    elif doorno == 7:
        return (val & 0x00000000FF000000000000) >> 48
    elif doorno == 8:
        return (val & 0x000000FF00000000000000) >> 56
    elif doorno == 9:
        return (val & 0x0000FF0000000000000000) >> 64
    elif doorno == 10:
        return (val & 0x00FF000000000000000000) >> 72
    elif doorno == 11:
        return (val & 0xFF00000000000000000000) >> 80



def get_rtLog(request):
    SN=request.GET.get('SN', "")
    nt=trunc(datetime.datetime.now()-datetime.timedelta(days=1))
    lasttid=int(request.GET.get("lasttid","-1"))
    items=records.objects.all()#filter(SN__ProductType__in=[4,5])
    devices=SN.split(',')
    if devices!=[u'']:
        items=items.filter(SN__in=devices)

    #items=items

#	if (cache.get("%s_haslogs_%s"%(settings.UNIT,request.user.pk))<>cache.get("%s_logstamp_"%(settings.UNIT))) or lasttid==0:
#		cache.set("%s_haslogs_%s"%(settings.UNIT,request.user.pk),cache.get("%s_logstamp_"%(settings.UNIT)))





    if lasttid==0:
        logs=items.filter(TTime__gt=nt).order_by("-id")
        logs=logs[:10]
    else:
        logs=items.filter(id__gt=lasttid).order_by("-id")
        logs=logs[:MAX_REALTIME_COUNT]
    lines=[]
    photo_lines=[]
    result={}
    for l in logs:
        lasttid=max(l.id,lasttid)
        line={}
        line['id']=l.id
#		line['PIN']="%s"%l.employee()
        line['TTime']=l.TTime.strftime("%m-%d %H:%M:%S")

        if l.SN:
            line['Device']=u"%s(%s)"%(l.Device().SN,l.Device().Alias or '')
        else:
            line['Device']=""

        line['event_point']=get_event_point_name(l)

        line['event_no']=l.get_event_no_display()
        if l.event_no==6:
            line['card_no']=''
        else:
            line['card_no']=l.card_no or ''
        line['pin']=''
        emp=None
        if l.pin:
            try:
                emp=employee.objByPIN(l.pin)
            except:
                emp=None
        if emp:
            line['pin']=u"%s %s"%(emp.PIN,emp.EName or '')

        line['inorout']=unicode(dict(STATE_CHOICES)[l.inorout])
        if l.event_no==6:
            line['verify']= get_EVENT_CHOICES_name(l.verify)
        else:
            line['verify']= l.get_verify_display() or ''
        line['dev_serial_num']=l.dev_serial_num or ''
        lines.insert(0,line.copy())
    result['data']=lines
    result['lasttId']=lasttid
    result['ret']=len(lines)
    result['tm']=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return result

def getDoorState(SN,door_no,stamp):
    rtstate=cache.get('_device_%s'%SN)
    if rtstate:
        d=lineToDict(rtstate)
        tm=d['time']
        sensor=d['sensor']
        relay=int(d['relay'],16)
        alarm=d['alarm']
        rela=relay>>(door_no-1)&0x01
        if door_no<5:
            sens=sensor[0:2]
        else:
            sens=sensor[2:4]
        sens=int(sens,16)
        sens=sens>>((door_no-1)*2)&0x03
        alm = alarm[door_no*2-2:door_no*2]
        alm=int(alm,16)
        alms = bin(alm)[2:].zfill(5)
        alm0 = alms[0]
        alm1 = alms[1]
        alm2 = alms[2]
        alm3 = alms[3]
        alm4 = alms[4]
        #print "ssss-----",rtstate,door_no,sens,rela,alm
        if sens==0:
            if rela==1:
                return ('nosensor_unlocked',sens,rela,alm)
            else:
                return ('nosensor',sens,rela,alm)
            return ('nosensor',sens,rela,alm)
        if sens==1:
            if alm == 0:

                if rela==0:
                    return ('closed',sens,rela,alm)
                elif rela==1:
                    return ('closed_unlocked',sens,rela,alm)
            else:

                if rela==0:
                    return ('alarm_closed',sens,rela,alm)
                elif rela==1:
                    return ('alarm_closed_unlocked',sens,rela,alm)
            return ('closed',sens,rela,alm)
        if sens==2:
            if alm == 0:
                if rela==0:
                    return ('opened',sens,rela,alm)
                elif rela==1:
                    return ('opened_unlocked',sens,rela,alm)
            else:
                if alm4 == 1:
                    if rela==0:
                        return ('alarm_timeout',sens,rela,alm)
                    elif rela==1:
                        return ('alarm_timeout_unlocked',sens,rela,alm)
                else:
                    if rela==0:
                        return ('alarm_opened',sens,rela,alm)
                    elif rela==1:
                        return ('alarm_opened_unlocked',sens,rela,alm)

            return ('opened',sens,rela,alm)

        return ('closed',sens,rela,alm)
    else:


        device=getDevice(SN)
        state=device.getDynState()
        if state==DEV_STATUS_PAUSE:
            return ('disabled',0,0,0)
        elif state==DEV_STATUS_OFFLINE:
            return ('offline',0,0,0)
        else:
            return ('default',0,0,0)



    return ('offline',0,0,0)

def getDoorStateForTCP(SN,door_no,stamp):
    rtstate=cache.get('_device_tcp_%s'%SN)
    if rtstate:
        l=rtstate.split(',')
        tm=l[0]
        rela=0
        sens=get_door_state(int(l[1]),door_no)#（0无门磁，1门关, 2门开）

        alm = get_door_state(int(l[2]),door_no) #（1报警，2门开超时)

        if sens==0:
            return ('nosensor',sens,rela,alm)
        if sens==1:
            if alm == 0:
                return ('closed',sens,rela,alm)
            elif alm==1:
                return ('alarm_closed',sens,rela,alm)
            elif alm==2:
                return ('alarm_closed',sens,rela,alm)
#			else:
#				print "-=====alarm===",alm


            return ('closed',sens,rela,alm)
        if sens==2:
            if alm == 0:
                return ('opened',sens,rela,alm)
            elif alm == 1:
                return ('alarm_opened',sens,rela,alm)
            elif alm == 2:
                return ('alarm_timeout',sens,rela,alm)

            return ('opened',sens,rela,alm)

        return ('closed',sens,rela,alm)
    else:
        device=getDevice(SN)
        state=device.getDynState()
        if state==DEV_STATUS_PAUSE:
            return ('disabled',0,0,0)
        elif state==DEV_STATUS_OFFLINE:
            return ('offline',0,0,0)
        else:
            return ('default',0,0,0)



    return ('offline',0,0,0)



def get_rtstate(request):
    global g_doorstate
    stamp=request.GET.get('stamp',0)
    SN=request.GET.get('SN','')
    devices=SN.split(',')

    if not g_doorstate or stamp==0:
        logs=AccDoor.objects.filter(device__DelTag=0).order_by('id')
        if devices!=[u'']:
            logs=logs.filter(device__in=devices)
        else:
            if request.user.is_superuser or request.user.is_alldept:
                logs=logs
            else:
                zonelist=userZoneList(request.user)
                sn_list=IclockZone.objects.filter(zone__in =zonelist).values_list("SN",flat=True)
                iclocks=iclock.objects.filter(SN__in=sn_list).values_list("SN",flat=True)
                logs=logs.filter(device__in=iclocks)
        for l in logs:
            line={}
            line['id']=l.id
            line['SN']=l.device_id
            line['door_name']=l.door_name
            line['door_no']=l.door_no
            line['ptype']=l.device.ProductType
            if line['ptype']==15:#非PUSH设备如C3
                try:
                    state=getDoorStateForTCP(l.device_id,l.door_no,stamp)
                except:
                    #import traceback;traceback.print_exc()
                    pass

            else:
                state=getDoorState(l.device_id,l.door_no,stamp)
            #doorstate=state[0]
            #if state[1]==1:
            #	doorstate='closed'
            #elif state[1]==2:
            #	doorstate='opened'
            #elif state[1]==2:
            #	doorstate='opened'


            #line['url']=doorstate#'door_offline.jpg'
            line['stamp']=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            line['state']=state
            g_doorstate[l.id]=line.copy()
    else:
        for k,v in g_doorstate.items():
            if devices!=[u'']:
                if v['SN'] not in devices:continue
            if v['ptype']==15:#非PUSH设备如C3
                state=getDoorStateForTCP(v['SN'],v['door_no'],stamp)
            else:
                state=getDoorState(v['SN'],v['door_no'],stamp)
            if state and v['state']!=state: #对于状态未改变的不更新
                v['state']=state
                v['stamp']=datetime.datetime.now().strftime('%Y%m%d%H%M%S')



    result={}
    state={}
    c=0
    laststamp=stamp
    for k,v in g_doorstate.items():
        if stamp>=v['stamp']:continue
        if devices!=[u'']:
            if v['SN'] not in devices:continue
        state[k]=v
        c+=1
        laststamp=max(laststamp,v['stamp'])
    #laststamp=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    result['data']=state
    result['ret']=c
    result['stamp']=laststamp
    result['tm']=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return result







"""实时 """
@login_required
def newTransLog(request):

    global g_doorstate
    result={}
    lasttid=int(request.GET.get("lasttid","-1"))
    lastdid=int(request.GET.get("lastdid","-1"))
    mapid=int(request.GET.get("mapid","-1"))
    if request.method=='GET':
        attColModel=records.colModels()
        HeaderModels=[]
        cc={}
        cc['recordColModel']=dumps(get_recordColModel())
        cc['accModel']=dumps(attColModel)
        cc['HeaderModels']=dumps(HeaderModels)
        g_doorstate={}
        data=GetParamValue('acc_param',{},'acc')
        if not data:
                data={
                    'is_':0,#是否启用
                }
        else:
                data=loads(data)
        cc['acc_params']=dumps1(data)



        return render(request,"acc/dlogcheck.html",cc)#render_to_response("acc/dlogcheck.html",cc,RequestContext(request, {}))
    logs=[]
    items=[]
    photo_logs=[]
    datas=[]
    if mapid==-1:
        datas=get_rtLog(request)
    try:
        rtstate=get_rtstate(request)
    except Exception,e:
        print "-----",e

    cc={}
    cc['data']=datas
    cc['state']=rtstate
    return getJSResponse(cc)


def newInoutLog(request): 
    if request.method=='GET':
        cc={}
        Title=GetParamValue('opt_basic_sitetitle')
        cc['title']=Title
        return render(request,"acc/dlogcheck_blue.html",cc)
    else:
        result={}
        lasttid=int(request.GET.get("lasttid","-1"))
        result['lastId']=lasttid
        now=datetime.date.today()
        logs=records.objects.filter(id__gt=lasttid,TTime__gte=now).exclude(pin=0).order_by("-id")
        result['emp_date']={}
        result['depts_date']={}
        if logs:
            ll={}
            ll['pin']=logs[0].pin
            ll['name']=logs[0].name
            if logs[0].employee()!='':
                ll['deptname']=logs[0].employee().Dept().DeptName
            else:
                ll['deptname']=''
            ll['ttime']=logs[0].TTime.strftime("%Y-%m-%d %H:%M:%S")
            if logs[0].Device():
                ll['sn']=logs[0].Device().Alias or logs[0].Device().SN
            if logs[0].Device( ):
                cmapfile="%s/photo/%s.jpg" %(settings.ADDITION_FILE_ROOT,logs[0].pin)
                if os.path.exists(cmapfile):
                    ll['urls']=logs[0].pin
                else:
                    ll['urls']=""

            if logs[0].employee()!='':
                ll['ssn']=logs[0].employee().SSN
            else:
                ll['ssn']=""
            ll['event_no']=logs[0].event_no
            inorout=logs[0].inorout
            ll['feifa']=""
            if inorout==0:
                ll['inorout']=u'进入'
            elif inorout==1:
                ll['inorout']=u'外出'
            else:
                ll['inorout']=''
            res=records.objects.filter(pin=ll['pin'],TTime__lt=logs[0].TTime).order_by("-TTime")
            if res:
                if inorout==res[0].inorout:
                    ll['feifa']="F"
            result['emp_date']=ll
            res=records.objects.filter(TTime__gte=now).order_by("-TTime")
            emps=[]
            depts_date=[]
            dlist={}
            for r in res:
                if r.inorout==0 and r.pin not in emps:
                    try:
                        deptid=str(r.employee().Dept().DeptID)
                    except:
                        continue
                    try:
                        dlist[deptid]+=1
                    except:
                        dlist[deptid]=1
                emps.append(r.pin)
            for k in dlist.keys():
                deptname=department.objByID(k).DeptName
                plan=u"<div>%s在场：   %s人</div>"%(deptname,dlist[k])
                depts_date.append(plan)
            result['depts_date']=depts_date
            result['lastId']=logs[0].id
        return getJSResponse(result)
#@login_required	
#def DeviceState(request): 
#	logs=AccDoor.objects.all().order_by('id')
#
#	result={}
#	lines=[]
#	door_state={'disabled':"door_disabled.png",
#        'default':"door_default.jpg",
#        'nosensor':"door_nosensor.png",
#        'offline': "door_offline.png",
#        'opened': "door_opened.png",
#        'closed': "door_closed.png",
#        'alarm': "door_alarm.png",
#        'open_timeout': "door_open_timeout.png"
#	}
#
#	lines.append(line.copy())
#	result['msg']='OK'
#	result['data']=lines
#	result['ret']=len(lines)
#	return getJSResponse(result)
#
#	
#
#MAX_PHOTO_WIDTH=400
#
