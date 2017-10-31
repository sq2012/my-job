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
from mysite.iclock.iutils import *
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
#from django.utils.encoding import smart_unicode, iri_to_uri
import platform
import math
from mysite.iclock.datasproc import trunc,getLocalText
from mysite.authurls import dongleHID
from django.contrib.auth import get_user_model
from mysite.base.models import *
import uuid
from mysite.meeting.models import MeetLocation,Meet
from mysite.acc.models import records



@login_required
def showMsgPage(request):

    using_m=request.GET.get('mod_name','')#GetParamValue('IsUsingModule_%s'%request.user.id,'')
    if request.method=='GET':
        if using_m=='meeting':
            rt=showMeetingPage(request)
        elif using_m=='ipos':
            rt=showPosPage(request)
        elif using_m=='acc':
            rt=showAccPage(request)

        else:
            rt=showAttPage(request)
        return rt


def showMeetingPage(request):
    ret={}
    ret['devices'] = iclock.objects.filter(ProductType__in=[1]).exclude(DelTag=1).count()
    isReal = 0
    if employee.objects.all()[:1] or ret['devices'] > 0:
        isReal = 1
    plots=get_device_states(request,isReal)
    ret['sysset']=get_sysset_info(request,isReal)
    ret['meetings']=get_meetings_room(request,isReal)
    cc={'user':request.user,
        'iclocks':plots,
        'ret':ret,
        'engine':settings.DATABASE_ENGINE,
        'date':datetime.datetime.now().strftime('%Y-%m-%d  ')+u'%s'%_(datetime.datetime.now().strftime('%A'))
        }


    return render(request,'meeting\home_content.html',cc)#render_to_response('meeting\home_content.html',cc,
                                #RequestContext(request, {
                                #}))




def get_meetings_room(request,isReal):
    dDict={}
    dDict['title']=unicode(_(u'虚拟会议数据'))
    dDict['categories']=dumps1([unicode(_(u'01会议室')),unicode(_(u'02会议室')),unicode(_(u'03会议室')),unicode(_(u'04会议室')),unicode(_(u'05会议室'))])
    colors=['#54585d','#90ed7d','#000000','#7ac143']
    dDict['data']=[{'color':colors[0],'y':3},{'y':2},{'color':colors[1],'y':5},{'color':colors[2],'y':4},{'color':colors[3],'y':1}]
    if isReal:
        rooms=MeetLocation.objects.all().exclude(DelTag=1).order_by('roomNo')
        rooms_name=[]
        rooms_data=[]
        dDict['title']=unicode(_(u'今日会议室安排'))
        now=datetime.datetime.now()
        d1=datetime.datetime(now.year,now.month,now.day,0,0,0)
        d2=datetime.datetime(now.year,now.month,now.day,23,59,59)
        x=0
        for t in rooms:
            roomNo=t.id
            meet_count=Meet.objects.filter(LocationID=roomNo,Starttime__gte=d1,Starttime__lte=d2).exclude(DelTag=1).count()
            rooms_name.append(t.roomName)
            rooms_data.append({'color':colors[x],'y':meet_count})
            x=x+1
            if x>3:x=0
        dDict['categories']=dumps1(rooms_name)
        dDict['data']=rooms_data

    return dDict

def get_User_Speday_Data(request,isReal=0):
    dDict=cache.get("%s-%s"%(settings.UNIT,'home_user_speadays'))
    if dDict:return dDict
    from mysite.iclock.datas import GetExceptionText,GetLeaveClasses
    html2=""
    #html=u"""<table style="width:%s;">%s</table>"""
    #html_more=u"<a id='iclock_USER_SPEDAY' onclick=menuClick('/iclock/data/USER_SPEDAY/',this); style='float:right;color:#7ac143;'>%s </a>"%(_(u"请假"))
    roid=0
    LClasses1=GetLeaveClasses(1)
    LeaveNames=[]
    LeaveIDS=[]
    Leave_IDS=[]
    for t in LClasses1:
        #if t['IsLeave']:
        LeaveNames.append(t['LeaveName'])
        Leave_IDS.append(t['LeaveID'])
    LeaveIDS=Leave_IDS[:4]
    LeaveNames=LeaveNames[:4]
    leaveName=GetExceptionText(2)
    dDict={'title':unicode(_(u'暂无请假信息')),
        'categories':dumps1(LeaveNames),
        # 'pie_data':
        # 	dumps1([{
        # 	    "name": unicode(_(u'事假')),
        # 	    "y": 43,
        # 	}, {
        # 	    "name": unicode(_(u'病假')),
        # 	    "y": 23,
        # 	}, {
        # 	    "name": unicode(_(u'产假')),
        # 	    "y": 19,
        # 	}, {
        # 	    "name": unicode(_(u'其他')),
        # 	    "y": 10,
        #
        # 	}]),
        'yipi':[20,12,10,4],
        'weipi':[3,12,1,2],
        'jujue':[1,1,2,1]

        }


    #暂时没有和用户联系，打开以下代码即可，注意缓存用法要改
    # if not (request.user.is_superuser or request.user.is_alldept):
    # 	d=userDeptList(request.user)
    # 	spedays=speadays.filter(UserID__DeptID__in=d)
    #
    # if GetParamValue('opt_basic_approval','1')=='1':
    # 	rd=userRole.objects.filter(userid=request.user)
    # 	if rd:
    # 		roleid=rd[0].roleid.roleid
    # 		spedays=spedays.filter(roleid=roid)
    pie_list=[]
    pie_dict={}
    yipi=[0]
    weipi=[0]
    jujue=[0]
    for t in LeaveIDS:
        yipi.append(0)
        weipi.append(0)
        jujue.append(0)
    if isReal:
        now=datetime.datetime.now()
        d1=datetime.datetime(now.year,now.month,1,0,0)
        et=d1+datetime.timedelta(days=32)
        d2=datetime.datetime(et.year,et.month,1,0,0,0)
        speadays=[]
        speadays=USER_SPEDAY.objects.filter(Q(StartSpecDay__gte=d1,StartSpecDay__lt=d2)|Q(StartSpecDay__lt=d1,EndSpecDay__gt=d1))

#         speadays=[]
        for t in speadays:
            if t.DateID not in Leave_IDS:continue
            lid=t.DateID
            txt=GetExceptionText(lid)

            if lid not in LeaveIDS:
                lid=10000
                txt=unicode(_(u'其他'))


            if t.State==2:
                try:
                    idx=LeaveIDS.index(lid)
                    yipi[idx]=yipi[idx]+1
                except:
                    yipi[-1]=yipi[-1]+1
            elif t.State==0:
                try:
                    idx=LeaveIDS.index(lid)
                    weipi[idx]=weipi[idx]+1
                except:
                    weipi[-1]=weipi[-1]+1
            elif t.State==3:
                try:
                    idx=LeaveIDS.index(lid)
                    jujue[idx]=jujue[idx]+1
                except:
                    jujue[-1]=jujue[-1]+1



            if lid in pie_dict.keys():
                pie_dict[lid]['y']=pie_dict[lid]['y']+1
            else:
                pie_dict[t.DateID]={'y':1,'name':txt}

        for k,v in pie_dict.items():
            pie_list.append(v)
        LeaveNames.append(unicode(_(u'其他')))
        dDict['categories']=dumps1(LeaveNames)
        dDict['title']=u'%s %s'%(now.strftime("%Y-%m"), unicode(_(u'请假数据')))
        dDict['pie_data']=dumps1(pie_list)
        dDict['yipi']=yipi
        dDict['weipi']=weipi
        dDict['jujue']=jujue

        cache.set("%s-%s"%(settings.UNIT,'home_user_speadays'),dDict,timeout=60*60)
    return dDict


def get_Employee_Duty_Info(request,isReal):
    dDict=cache.get("%s-%s"%(settings.UNIT,'home_user_dutys'))
    if dDict:return dDict
    dDict={}
    dDict['title']=unicode(_(u'在岗信息'))
    dDict['data']=dumps1([{'name':unicode(_(u'实到')),'y':518,'sliced':True,'selected':True},[unicode(_(u'请假')),50],[unicode(_(u'出差')),15],[unicode(_(u'旷工')),100]])
    if isReal:
        nt=trunc(datetime.datetime.now())
        dDict['title'] =u'%s%s'%(nt.strftime("%Y-%m-%d"), unicode(_(u'在岗信息')))
        attshifts=attShifts.objects.filter(AttDate=nt)
        sd,qj,cc,kg=0,0,0,0
        for t in attshifts:
            if t.RealWorkDay>0:sd+=1
            if t.ExceptionID and t.ExceptionID!=1:
                qj+=1
            if t.ExceptionID==1:
                cc+=1
            if t.Absent>0:
                kg+=1
        if sd+qj+cc+kg==0:
            sd,qj,cc,kg=1,1,1,1
            dDict['title'] =u'%s%s'%(nt.strftime("%Y-%m-%d"), unicode(_(u'暂无在岗信息')))
        dDict['data']=dumps1([{'name':unicode(_(u'实到')),'y':sd,'sliced':True,'selected':True},[unicode(_(u'请假')),qj],[unicode(_(u'出差')),cc],[unicode(_(u'旷工')),kg]])
        cache.set("%s-%s"%(settings.UNIT,'home_user_dutys'),dDict,timeout=60*10)
    return dDict

def get_acc_records_Info(request,isReal):
    dDict={}
    dDict['title']=unicode(_(u'门禁异常事件'))
    now=datetime.datetime.now()
    d1=datetime.datetime(now.year,now.month,now.day,0,0)
    d2=d1+datetime.timedelta(days=1)

    no_registered=31
    Illegal_access=30
    overtime=15
    Tamper=100

    plots=cache.get("%s_acc_records"%settings.UNIT)
    if not plots:

        if isReal==0:#虚拟数据
            no_registered=31
            Illegal_access=30
            overtime=15
            Tamper=100
        else:
            no_registered = 0
            Illegal_access = 0
            overtime = 0
            Tamper = 0

            rst=records.objects.values('event_no').annotate(count=Count('event_no')).filter(event_no__in=[27,23,28,100]).filter(TTime__range=[d1,d2])
            for t in rst:
                if t['event_no']==27:
                    no_registered=t['count']
                elif t['event_no']==23:
                    Illegal_access=t['count']
                elif t['event_no']==28:
                    overtime=t['count']
                elif t['event_no']==100:
                    Tamper=t['count']
            # no_registered=records.objects.filter(event_no__in=[27]).count()#未登记人员
            # Illegal_access=records.objects.filter(event_no__in=[23]).count()#非法访问
            # overtime=records.objects.filter(event_no__in=[28]).count()#门开超时
            # Tamper=records.objects.filter(event_no__in=[100]).count()#防拆报警
            if no_registered + Illegal_access +overtime +Tamper == 0:
                    dDict['title'] = unicode(_(u'暂无异常事件'))
                    no_registered , Illegal_access , overtime , Tamper=1,1,1,1
        plots=dumps1([{'name':unicode(_(u'人未登记')),'y':no_registered,'sliced':True,'selected':True},[unicode(_(u'非法访问')),Illegal_access],[unicode(_(u'防拆报警')),overtime],[unicode(_(u'门开超时')),Tamper]])
        cache.set('%s_acc_records'%settings.UNIT,plots,timeout=600)

    dDict['data']=plots
    return dDict

def get_pos_card_info(request,isReal):
    dDict=cache.get("%s-%s"%(settings.UNIT,'home_user_cards'))
    if dDict:return dDict
    now=datetime.datetime.now()
    d1=datetime.datetime(now.year,now.month,now.day,0,0)
    d2=d1+datetime.timedelta(days=1)


    dDict={}
    dDict['title']=unicode(_(u'卡变动信息'))
    if isReal==0:
        dDict['data']=dumps1([{'name':unicode(_(u'发卡')),'y':58,'sliced':True,'selected':True},[unicode(_(u'挂失')),50],[unicode(_(u'退卡')),15],[unicode(_(u'补卡')),100]])
    else:
        fk,gs,tk,bk=0,0,0,0
        fk=IssueCard.objects.filter(issuedate__range=(d1,d2),cardstatus=CARD_VALID).count()
        gs=IssueCard.objects.filter(issuedate__range=(d1,d2),cardstatus=CARD_LOST).count()
        tk=CardCashSZ.objects.filter(checktime__range=(d1,d2),hide_column__in=[14,15]).count()
        bk=ReplenishCard.objects.filter(time__range=(d1,d2)).count()

        if fk+gs+tk+bk==0:
            dDict['title'] = unicode(_(u'暂无卡变动信息'))
            fk, gs, tk, bk = 1, 1, 1, 1
        dDict['data']=dumps1([{'name':unicode(_(u'发卡')),'y':fk,'sliced':True,'selected':True},[unicode(_(u'挂失')),gs],[unicode(_(u'退卡')),tk],[unicode(_(u'补卡')),bk]])


        cache.set("%s-%s" % (settings.UNIT, 'home_user_cards'), dDict, timeout=60 * 10)

    return dDict


def get_sysset_info(request,isReal=0):
    dDict={}
    if GetParamValue('opt_basic_dev_auto','1')=='1':
        dDict['dev_auto']="<i class='icon-zkgreen icon iconfont icon-dui'></i>"
    else:
        dDict['dev_auto']="<img src='../media/img/cancel.png'/>"
    if GetParamValue('opt_basic_new_record','0')=='1':
        dDict['new_record']="<i class='icon-zkgreen icon iconfont icon-dui'></i>"
    else:
        dDict['new_record']="<i class='icon-red icon iconfont icon-cuo'></i>"

    if GetParamValue('opt_basic_Auto_iclock','0')=='1':
        if IclockDept.objects.all().count()==0:
            dDict['Auto_iclock']=u"%s"%_(u'启用无效，需要对设备进行设置归属部门')
        else:
            dDict['Auto_iclock']="<i class='icon-zkgreen icon iconfont icon-dui'></i>"
    else:
        dDict['Auto_iclock']="<i class='icon-red icon iconfont icon-cuo'></i>"
    if GetParamValue('opt_basic_self_login','0')=='1':
        dDict['self_login']="<i class='icon-zkgreen icon iconfont icon-dui'></i>"
    else:
        dDict['self_login']="<i class='icon-red icon iconfont icon-cuo'></i>"
    dDict['page_limit']=GetParamValue('opt_basic_page_limit','50')
    dDict['photo_show']=''

    if GetParamValue('opt_basic_emp_pic','0')=='1':
        dDict['photo_show']="<i class='icon-zkgreen icon iconfont icon-dui'></i>"
    if GetParamValue('opt_basic_rec_pic','')=='1':
        dDict['photo_show']="<i class='icon-zkgreen icon iconfont icon-dui'></i>"
    if dDict['photo_show']=='':
        dDict['photo_show']="<i class='icon-red icon iconfont icon-cuo'></i>"
    if GetParamValue('opt_basic_lock_date','0')=='0':
        dDict['lock_date']="<i class='icon-red icon iconfont icon-cuo'></i>"
    else:
        dDict['lock_date']=u'%s'%_(u'每月%s日后不允许修改上月的数据')%GetParamValue('opt_basic_lock_date','0')
    if GetParamValue('opt_basic_enroll','0')=='1':
        dDict['enroll']="<i class='icon-zkgreen icon iconfont icon-dui'></i>"
    else:
        dDict['enroll']="<i class='icon-red icon iconfont icon-cuo'></i>"

    dDict['options']=u"<a class='icon iconfont icon-xiugai' id='%s' onclick=menuClick('%s',this); style='float:left;color:#7ac143;'>%s </a>"%('base_options','/base/isys/options/',(_(u"系统选项")))

    if request.user.has_perm('iclock.browse_announcement'):
        dDict['Announcement']=u"<a id='iclock_Announcement' onclick=menuClick('/iclock/data/Announcement/',this); style='float:right;color:#7ac143;'>%s </a>"%(_(u"公告"))

    if (request.user.is_superuser) or (request.user.is_alldept):
        dDict['Auth_dept']=_('All deptartments')
        dDict['Auth_device']=_('All devices')
        dDict['Auth_timezone']=_(u'所有时段和班次')
    else:
        html=""
        title=""
        d=userDeptList(request.user)
        j=0
        for i in d:
            s=department.objByID(i).DeptName
            if j<1:
                html+=s+','
            title+=s+','
            j+=1
        html=html[:-1]
        if j>1:
            html+="..."
        title=title[:-1]
        dDict['Auth_dept']="<a href='#' title='%s'>%s</a>"%(title,html)
        html=""
        iclocks=AuthedIClockList(request.user)
        html=','.join(iclocks[:1])
        if len(iclocks)>1:
            html+='...'
        title=','.join(iclocks)
        dDict['Auth_device']="<a href='#' title='%s'>%s</a>"%(title,html)

        User=get_user_model()
        u=User.objects.get(pk=request.user.pk)
        if u.AutheTimeDept:
            dName=department.objByID(u.AutheTimeDept).DeptName
            title=''
            html=u'授权使用%s的时段'%dName
            dDict['Auth_timezone']="<a href='#' title='%s'>%s</a>"%(title,html)





    return dDict.copy()

def get_device_states(request,isReal):
    using_m=request.GET.get('mod_name','')#GetParamValue('IsUsingModule_%s'%request.user.id,'')
    plots=[]
    if using_m in ['adms','att','acc','meeting','visitors']:
            devs={'online':0,'pause':0,'offline':0,'trans':0,'uid':request.user.id}
            plots=[]

            devs_cache=cache.get('%s_home_devices_state_%s_%s'%(settings.UNIT,using_m,request.user.id))
            if not devs_cache:
                items=iclock.objects.all().exclude(DelTag=1).exclude(ProductType__in=[11,12,13])
                if using_m in ['adms','att']:
                    items=items.filter(Q(ProductType__isnull=True)|Q(ProductType=9))
                elif using_m in ['acc','visitors']:#访客暂时用门禁设备
                    items=items.filter(ProductType__in=[5,15,25])
                elif using_m in ['meeting']:
                    items=items.filter(ProductType__in=[1])
                if request.user.is_superuser or request.user.is_alldept:
                    #t=iclock.objects.all().exclude(DelTag=1).count()
                    #t1=datetime.datetime.now()-datetime.timedelta(seconds=settings.MAX_DEVICES_STATE)
                    #c=iclock.objects.filter(LastActivity__gte=t1).exclude(DelTag=1).count()
                    ##devs['online']=c
                    #
                    #p=iclock.objects.filter(State=0).exclude(DelTag=1).count()
                    #devs['pause']=p
                    #
                    #off=t-c-p#iclock.objects.filter(LastActivity__lt=t1).filter(Q(DelTag__isnull=True)|Q(DelTag=0)).count()#
                    #devs['offline']=off
                    #
                    #trans=devcmds.objects.values('SN').annotate().filter(SN__LastActivity__gte=t1, CmdTransTime__isnull=True,CmdCommitTime__lte=datetime.datetime.now()).exclude(SN__DelTag=1).count()
                    #devs['trans']=trans
                    #devs['online']=c-trans


                    c=0
                    y1=0
                    y2=0
                    y3=0
                    y4=0
                    c=items.count()
                    if c<500:
                        for i in items:
                            #c+=1
                            t=i.getDynState()
                            if t==0:
                                y1+=1
                            elif t==1:
                                y2+=1
                            elif t==2:
                                y3+=1
                            elif t==3:
                                y4+=1
                            else:
                                pass
                    else:

                        d=datetime.datetime.now()-datetime.timedelta(seconds=settings.MAX_DEVICES_STATE+100)


                        y1=items.filter(State=0).count()
                        y2=items.filter(State=1,LastActivity__gte=d).count()
                        y3=items.filter(State=2).count()
                        y4=c-y1-y2-y3#items.filter(State=3).count()
                    devs['pause']=y1
                    devs['online']=y2
                    devs['trans']=y3
                    devs['offline']=y4
                else:
                    iclocks=AuthedIClockList(request.user)
                    rows=items.filter(SN__in=iclocks)#filter(Q(DelTag__isnull=True)|Q(DelTag=0))
                    c=0
                    y1=0
                    y2=0
                    y3=0
                    y4=0
                    for i in rows:
                        c+=1
                        t=i.getDynState()
                        if t==0:
                            y1+=1
                        elif t==1:
                            y2+=1
                        elif t==2:
                            y3+=1
                        elif t==3:
                            y4+=1
                        else:
                            pass
                    devs['pause']=y1
                    devs['online']=y2
                    devs['trans']=y3
                    devs['offline']=y4

                if c>100:
                    cache.set('%s_home_devices_state_%s_%s'%(settings.UNIT,using_m,request.user.id),devs,timeout=300)
            else:
                devs=devs_cache
            if isReal==0:
                plots=[{'color':'#50B432','y':100},{'color':'#058DC7','y':100},{'color':'#ED561B','y':100},{'color':'#B5CA92','y':100}]
            else:
                plots=[{'color':'#50B432','y':devs['online']},{'color':'#058DC7','y':devs['trans']},{'color':'#000000','y':devs['offline']},{'color':'#B5CA92','y':devs['pause']}]

    elif using_m in ['ipos']:
            devs={'online':0,'pause':0,'offline':0,'trans':0,'uid':request.user.id}
            sns=iclock.objects.filter(ProductType__in=[11,12,13]).exclude(DelTag=1).values_list('SN')
            for sn in sns:
                dev=getDevice(sn[0])
                if dev.getDynState()==0:
                    devs['pause']=devs['pause']+1
                elif dev.getDynState()==1:
                    devs['online']=devs['online']+1
                elif dev.getDynState()==3:
                    devs['offline']=devs['offline']+1
                elif dev.getDynState()==2:
                    devs['trans']=devs['trans']+1

            if isReal==0:
                plots=[{'color':'#50B432','y':12},{'color':'#058DC7','y':1},{'color':'#ED561B','y':5},{'color':'#B5CA92','y':2}]
            else:
                plots=[{'color':'#50B432','y':devs['online']},{'color':'#058DC7','y':devs['trans']},{'color':'#ED561B','y':devs['offline']},{'color':'#B5CA92','y':devs['pause']}]





    return plots
def get_acc_data_charts(request,isReal):
    u"""门禁首页数据信息"""
    now=datetime.datetime.now()
    d1=datetime.datetime(now.year,now.month,now.day,0,0)
    d2=d1+datetime.timedelta(days=1)
    Names=[unicode(_(u'部门')),unicode(_(u'人员')),unicode(_(u'今日门禁记录'))]
    dDict={}
    plots=[]
    dDict['categories']=dumps1(Names)
    colors=['#90ed7d','#54585d','#7ac143']
    x=0

    plots= cache.get("%s_acc_data"%(settings.UNIT))
    if not plots:


        dDict['title']=unicode(_(u'系统数据信息'))
        if isReal==0:
            dDict['title']=unicode(_(u'暂无门禁数据'))
            plots=[{'color':colors[0],'y':500},{'color':colors[1],'y':3000},{'color':colors[2],'y':5800}]
        else:
            c=employee.objects.exclude(DelTag=1).exclude(OffDuty=1).count()
            d_y=department.objects.exclude(DelTag=1).count()
            r1=records.objects.filter(TTime__gte=d1,TTime__lt=d2).count()
            plots=[{'color':colors[0],'y':d_y},{'color':colors[1],'y':c},{'color':colors[2],'y':r1}]
            cache.set("%s_acc_data"%(settings.UNIT),plots,timeout=600)


    dDict['plots']=plots

    return dDict

def get_consume_data(request,isReal):
    dDict=cache.get("%s-%s"%(settings.UNIT,'home_user_consumes'))
    if dDict:return dDict
    now=datetime.datetime.now()
    d1=datetime.datetime(now.year,now.month,1,0,0)
    et=d1+datetime.timedelta(days=32)
    d2=datetime.datetime(et.year,et.month,1,0,0,0)
    data=GetParamValue('ipos_params','','ipos')
    if data:
        from mysite.auth_code import auth_code
        data=loads(auth_code(data.encode("gb18030")))
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
    Names=[]
    Names_Dict={}
    Names_id=[]
    dDict={}
    plots=[]
    objs=Meal.objects.filter(available=True).exclude(DelTag=1)
    for t in objs:
        Names.append(t.name)
        Names_id.append(t.id)
        Names_Dict[t.id]=0
    dDict['categories']=dumps1(Names)
    colors=['#54585d','#90ed7d','#000000','#7ac143']
    x=0
    if isReal>0:
        if (data and data['itype']=='2') or (not data and settings.CARDTYPE=='2'):
            objs=ICConsumerList.objects.filter(pos_time__gte=d1,pos_time__lte=d2).values('meal').annotate(mCount=Count('meal')).order_by()
            for t in objs:
                Names_Dict[t['meal']]=t['mCount']
        elif (data and data['itype']=='1') or (not data and settings.CARDTYPE=='1'):
            for obj in objs:
                Names_Dict[obj.id]=CardCashSZ.objects.filter(checktime__gte=d1,checktime__lte=d2,meal=obj).count()
    dDict['title']=unicode(_(u'本月各餐别消费人次信息'))
    if isReal==0:
        dDict['title']=unicode(_(u'虚拟消费数据'))
        plots=[{'color':colors[0],'y':500},{'color':colors[1],'y':1000},{'color':colors[2],'y':1800},{'color':colors[3],'y':100}]
    else:
        for t in Names_id:
            plots.append({'color':colors[x],'y':Names_Dict[t]})     #[{'color':'#50B432','y':Names_Dict[]},{'color':'#058DC7','y':devs['trans']},{'color':'#ED561B','y':devs['offline']},{'color':'#B5CA92','y':devs['pause']}]
            x=x+1
            if x>3:
                x=0
    dDict['plots']=plots
    cache.set("%s-%s" % (settings.UNIT, 'home_user_consumes'), dDict, timeout=60 * 10)

    return dDict



def get_records(using_m):
    _records={}
    dt=datetime.datetime.now()
    s=''
    for t in range(30):
        d=dt-datetime.timedelta(days=t)
        if t%2==0:
            s="'%s'"%d.strftime('%d')+','+s
        else:
            s="'%s'"%('')+','+s
    _records['categories']=s
    s=''
    key='%s_record_29_%s_%s'
    datas29=cache.get(key%(settings.UNIT,using_m,dt.strftime("%Y-%m-%d%H")))
    rg=0
    is_cache=0
    record_list=[]
    if datas29:
        is_cache=1
        #record_list=datas_29
    else:
        fn=settings.APP_HOME+'/files/records.dat'
        lines=[]
        if os.path.exists(fn):
            f=open(fn,'r')
            lines=f.readlines()
            f.close()
            datas_=lines[0]
            #print lines,"0000"
            datas_29=loads(datas_)
        else:
            datas_29={}
        try:
            datas29=datas_29[using_m]
        except:
            datas29={}



    r_flag=False
    if not is_cache:
        for t in range(30):
            d=dt-datetime.timedelta(days=t)
            try:
                c=datas29[d.strftime("%Y-%m-%d")]
                record_list.append(c)
            except:
                if t>0:
                    rg=30
                d1=trunc(d)
                d2=d1+datetime.timedelta(days=1)
                if using_m=='acc':
                    c=records.objects.filter(TTime__range=(d1,d2)).count()
                elif using_m in ['att','adms']:
                    c=transactions.objects.filter(TTime__range=(d1,d2)).exclude(purpose=1).count()
                elif using_m=='ipos':
                    c=ICConsumerList.objects.filter(pos_time__range=(d1,d2)).count()
                else:
                    c=transactions.objects.filter(TTime__range=(d1,d2)).filter(purpose=1).count()
                record_list.insert(0,c)
                datas29[d.strftime("%Y-%m-%d")]=c
            if c>0:r_flag=True
    else:
        for t in range(30):
            d=dt-datetime.timedelta(days=t)
            c=datas29[d.strftime("%Y-%m-%d")]
            record_list.insert(0,c)

    cache.set(key%(settings.UNIT,using_m,dt.strftime("%Y-%m-%d%H")),datas29,timeout=86400)
    if rg==30:
        try:
            del datas29[dt.strftime("%Y-%m-%d")]
        except:
            pass
        datas_29[using_m]=datas29
        fn=settings.APP_HOME+'/files/records.dat'
        f=file(fn, "w")
        f.write(dumps(datas_29))
        f.close()

    for t in record_list:
        s+=str(t)+','

    _records['datas']=s
    return _records

def get_records(using_m):
    _records={}
    _records['categories']=[]
    dt=datetime.datetime.now()
    s=''
    for t in range(30):
        d=dt-datetime.timedelta(days=t)
        if t%2!=0:
            s="%s"%d.strftime('%d')
        else:
            s="%s"%('')
        _records['categories'].insert(0,s)
    #_records['categories']=s
    s=''
    key='%s_record_29_%s_%s'
    datas29=cache.get(key%(settings.UNIT,using_m,dt.strftime("%Y-%m-%d")))
    rg=0
    is_cache=0
    record_list=[]
    if datas29:
        is_cache=1
        #record_list=datas_29
    else:
        fn=settings.ADDITION_FILE_ROOT+'/records_%s.dat'%using_m
        lines=[]
        if os.path.exists(fn):
            f=open(fn,'r')
            lines=f.readlines()
            f.close()
            datas_=lines[0]
            #print lines,"0000"
            datas_29=loads(datas_)
        else:
            datas_29={}
        try:
            datas29=datas_29[using_m]
        except:
            datas29={}



    r_flag=False
    if not is_cache:
        for t in range(30):
            d=dt-datetime.timedelta(days=t)
            try:
                c=datas29[d.strftime("%Y-%m-%d")]
                record_list.append(c)
            except:
                if t>0:
                    rg=30
                d1=trunc(d)
                d2=d1+datetime.timedelta(days=1)
                if using_m=='acc':
                    c=records.objects.filter(TTime__range=(d1,d2)).count()
                elif using_m in ['att','adms']:
                    c=transactions.objects.filter(TTime__range=(d1,d2)).exclude(purpose=1).count()
                elif using_m=='ipos':
                    c=ICConsumerList.objects.filter(pos_time__range=(d1,d2)).count()
                else:
                    c=transactions.objects.filter(TTime__range=(d1,d2)).filter(purpose=1).count()
                record_list.insert(0,c)
                datas29[d.strftime("%Y-%m-%d")]=c
            if c>0:r_flag=True
    else:
        for t in range(30):
            d=dt-datetime.timedelta(days=t)
            c=datas29[d.strftime("%Y-%m-%d")]
            record_list.insert(0,c)
    cache.set(key%(settings.UNIT,using_m,dt.strftime("%Y-%m-%d")),datas29)
    if rg==30:
        try:
            del datas29[dt.strftime("%Y-%m-%d")]
        except:
            pass
        datas_29[using_m]=datas29
        fn=settings.ADDITION_FILE_ROOT+'/records_%s.dat'%using_m
        f=file(fn, "w")
        f.write(dumps(datas_29))
        f.close()

    for t in record_list:
        s+=str(t)+','

    _records['datas']=s
    return _records


def showAttPage(request):
        from mysite.iclock.home_attention import colModel
        clm = colModel()
        ret={}
        ret['records']=0
        ret['t_records']=0  #attendance records
        ret['reccount']=0
        ret['online']=0
        ret['processor']=platform.processor()
        ret['os']=platform.platform()
        ret['mac']=uuid.uuid1().hex[-12:]
        ret['version']=settings.VERSION
        ret['serialno']=dongleHID
        trialversion=u'%s'%_(u'永久')
        if settings.CLOSE_DATE!='' or settings.MAX_DAYS<999:
            trialversion=getLocalText('Trial')+';'
            if settings.CLOSE_DATE!='':
                trialversion+='&nbsp;&nbsp;'+getLocalText('TrialDays')+str(settings.CLOSE_DATE)
            else:
                trialversion+='&nbsp;&nbsp;'+getLocalText('TrialDays')+str(settings.MAX_DAYS)
        ret['authed']=trialversion
        ret['devicelimit']=settings.MAX_DEVICES
        ret['devices']=iclock.objects.exclude(DelTag=1).count()
        isReal=0
        if employee.objects.all()[:1] or ret['devices']>0:
            isReal=1
        plots=get_device_states(request,isReal)
        #ret['leave']=u"<span style='color:#32598A;'>%s</span>"%(_('No Leave Data'))#暂无请假信息



        #请假信息
        ret['leaves']=get_User_Speday_Data(request,isReal)

        ret['employee_info']=get_Employee_Duty_Info(request,isReal)

        #系统设置



        ret['sysset']=get_sysset_info(request)
        # #公告信息
        # ret['announce']=u"<span style='color:#32598A;'>%s</span>"%(_('No Information Data'))#暂无公告信息
        # announcement=Announcement.objects.all().order_by('-IsTop','-Pubdate')[:9]
        # html=''
        # for t in announcement:
        # 	#url='/iclock/data/Announcement/?q='+str(t.id)
        # 	Title=t.Title+'&nbsp;&nbsp;['+ t.Pubdate.strftime('%Y-%m-%d')+']'
        # 	#html+="<div class='contentbr'>&nbsp;<img src='../media/img/icon_setIndex.gif'/>&nbsp;"+"<a href='#' onclick='createAnnouncementDetail("+content+titl+")'>"+Title+"</a></div>"
        # 	html+="<div class='contentbr'>&nbsp;<img src='../media/img/icon_setIndex.gif'/>&nbsp;"+"<a href='#' onclick='ShowAnnouncement("+str(t.id)+")'>"+Title+"</a></div>"
        # if html:
        # 	ret['announce']=html
        #最新30天记录信息
        records=get_records('att')



        cc={'user':request.user,
            'iclocks':plots,
            'records':records,
            'ret':ret,
            'engine':settings.DATABASE_ENGINE,
            'date':datetime.datetime.now().strftime('%Y-%m-%d  ')+u'%s'%_(datetime.datetime.now().strftime('%A')),
            'colModel':dumps1(clm)
            }
        result=[]
        #t1=datetime.datetime.now()
        #AllChildrens(101,result)
        #t2=datetime.datetime.now()-t1
        #print "======",t2,result

        return render(request,'att\home_content.html',cc)
        #render_to_response('home_content.html',cc,RequestContext(request, {}))


def showAccPage(request):
        ret={}
        ret['records']=0
        ret['t_records']=0  #attendance records
        ret['reccount']=0
        ret['online']=0
        ret['version']=settings.VERSION
        ret['serialno']=dongleHID
        trialversion=u'%s'%_(u'永久')
        t1=datetime.datetime.now()
        ret['devices']=iclock.objects.exclude(DelTag=1).count()
        isReal=0
        if employee.objects.all()[:1] or ret['devices']>0:
            isReal=1

        plots=get_device_states(request,isReal)
        ret['data']=get_acc_data_charts(request,isReal)
        ret['employee_info']=get_acc_records_Info(request,isReal)
        #系统设置



        ret['sysset']=get_sysset_info(request)
        # #公告信息
        # ret['announce']=u"<span style='color:#32598A;'>%s</span>"%(_('No Information Data'))#暂无公告信息
        # announcement=Announcement.objects.all().order_by('-IsTop','-Pubdate')[:9]
        # html=''
        # for t in announcement:
        # 	#url='/iclock/data/Announcement/?q='+str(t.id)
        # 	Title=t.Title+'&nbsp;&nbsp;['+ t.Pubdate.strftime('%Y-%m-%d')+']'
        # 	#html+="<div class='contentbr'>&nbsp;<img src='../media/img/icon_setIndex.gif'/>&nbsp;"+"<a href='#' onclick='createAnnouncementDetail("+content+titl+")'>"+Title+"</a></div>"
        # 	html+="<div class='contentbr'>&nbsp;<img src='../media/img/icon_setIndex.gif'/>&nbsp;"+"<a href='#' onclick='ShowAnnouncement("+str(t.id)+")'>"+Title+"</a></div>"
        # if html:
        # 	ret['announce']=html
        #最新30天记录信息
        records=get_records('acc')
        cc={'user':request.user,
            'iclocks':plots,
            'records':records,
            'ret':ret,
            'engine':settings.DATABASE_ENGINE,
            'date':datetime.datetime.now().strftime('%Y-%m-%d  ')+u'%s'%_(datetime.datetime.now().strftime('%A'))
            }
        result=[]
        #t1=datetime.datetime.now()
        #AllChildrens(101,result)
        #t2=datetime.datetime.now()-t1
        #print "======",t2,result

        return render(request,'acc\home_content.html',cc)




@login_required
def getAnnouncement(request,DataKey):
    if request.method=='GET':
        a=Announcement.objects.filter(id__exact=DataKey)[0]
        return getJSResponse({"Title":u"%s"%a.Title,"Content":u"%s"%a.Content,"Pubdate":"%s"%a.Pubdate})





def showPosPage(request):
        ret={}
        ret['records']=0
        ret['t_records']=0  #attendance records
        ret['reccount']=0
        ret['online']=0
        ret['processor']=platform.processor()
        ret['os']=platform.platform()
        ret['mac']=uuid.uuid1().hex[-12:]
        ret['version']=settings.VERSION
        ret['serialno']=dongleHID
        trialversion=u'%s'%_(u'永久')
        if settings.CLOSE_DATE!='' or settings.MAX_DAYS<999:
            trialversion=getLocalText('Trial')+';'
            if settings.CLOSE_DATE!='':
                trialversion+='&nbsp;&nbsp;'+getLocalText('TrialDays')+str(settings.CLOSE_DATE)
            else:
                trialversion+='&nbsp;&nbsp;'+getLocalText('TrialDays')+str(settings.MAX_DAYS)
        ret['authed']=trialversion
        ret['devicelimit']=settings.MAX_DEVICES
        ret['devices']=iclock.objects.exclude(DelTag=1).count()
        isReal=0
        if employee.objects.all()[:1] or ret['devices']>0:
            isReal=1

        plots=get_device_states(request,isReal)
        #ret['leave']=u"<span style='color:#32598A;'>%s</span>"%(_('No Leave Data'))#暂无请假信息


        ret['pos_card_info']=get_pos_card_info(request,isReal)

        ret['consumes']=get_consume_data(request,isReal)


        #系统设置



        ret['sysset']=get_sysset_info(request)


        ret['devicelimit']=settings.MAX_DEVICES






        #最新30天记录信息
        records=get_records('ipos')

        cc={'user':request.user,
            'iclocks':plots,
            'records':records,
            'ret':ret,
            'engine':settings.DATABASE_ENGINE,
            'date':datetime.datetime.now().strftime('%Y-%m-%d  ')+u'%s'%_(datetime.datetime.now().strftime('%A'))
            }
        result=[]
        #t1=datetime.datetime.now()
        #AllChildrens(101,result)
        #t2=datetime.datetime.now()-t1
        #print "======",t2,result

        return render(request,'ipos\home_content.html',cc)#render_to_response('ipos\home_content.html',cc,
                                #RequestContext(request, {
                                #}))
