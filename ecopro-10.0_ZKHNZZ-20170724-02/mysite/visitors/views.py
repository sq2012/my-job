#!/usr/bin/python
# -*- coding: utf-8 -*-

from mysite.base.models import *
from mysite.visitors.models import *
from mysite.iclock.models import adminLog
from mysite.core.cmdproc import delete_pos_device_info,update_pos_device_info
from mysite.utils import *
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render_to_response,render,render
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from mysite.iclock.datasproc import FetchDisabledFields
from mysite.acc.models import *
from mysite.core.cmdproc import saveCmd
def hasReasons(request):
    ll=[]
    reasons=reason.objects.filter(DelTag=0)
    for i in reasons:
        ll.append(i.reasonName)
    return getJSResponse(dumps(ll))


def sendVisitorsToAcc(obj):
    if obj.levels and obj.Card:
        Levels=obj.levels.split(',')
        emppin='vis%d'%obj.id
        #emppin='%d'%obj.id
        starttime=0
        endtime=0
        if obj.EnterTime and obj.ExitTime:
            starttime=OldEncodeTime(obj.EnterTime)
            endtime=OldEncodeTime(obj.ExitTime)
        for lv in Levels:
            lv=int(lv)
            obj_level=level.objects.get(id=lv)
            doors=level_door.objects.filter(level=lv).values('door')
            devs=AccDoor.objects.filter(id__in=doors).distinct().values('device')

            iclocks=iclock.objects.filter(SN__in=devs)

            for dev in iclocks:
                if dev.ProductType in [5,15,25]:
                    doorofdev=AccDoor.objects.filter(id__in=doors,device=dev)
                    AuthorizeDoorId=0
                    for t in doorofdev:
                        doorno=t.door_no
                        m=pow(2,doorno-1)
                        AuthorizeDoorId=AuthorizeDoorId+m

                    #set_data(dev.SN,'user',emps)
                    #zk_set_data(dev,'userinfo',emps,cmdTime=None)

                    cmdStr="DATA UPDATE user CardNo=%s\tPin=%s\tPassword=%s\tGroup=%s\tStartTime=%s\tEndTime=%s"%(obj.Card or '',emppin,'',0,starttime,endtime)
                    saveCmd(dev.SN,cmdStr)
                    line_tuple = []
                    filters = ""


                        #if len(emppin)>9:
                        #	continue

                    cmdStr="\r\nPin=%s\tAuthorizeTimezoneId=%s\tAuthorizeDoorId=%s"%(emppin,obj_level.timeseg_id,AuthorizeDoorId)




                    line_tuple.append(cmdStr)
                    line = ''.join(line_tuple).replace("\r\n","",1)
                    if len(line)>0:
                        CMDs="DATA UPDATE userauthorize %s"%(line)
                        saveCmd(dev.SN,CMDs)




@permission_required("visitors.browse_visitionlogs")
def visitionlogs_his(request):
    request.user.iclock_url_rel='../..'
    request.model = visitionlogs
    disabledCols=FetchDisabledFields(request.user, 'visitionlogs')
    #disabledOrderCols=FetchDisabledOrderFields(request.user, 'visitionlogs')
    colModel=visitionlogs.colModels()
    # return render_to_response('visitors/visitionlogsHis_list.html',
    return render(request,'visitors/visitionlogsHis_list.html',
                            {#'transaction_list': dumps(d),
                            'from': 1,
                            'page': 1,
                            'limit': 10,
                            'item_count': 4,
                            'page_count': 1,
                            'disabledcols':dumps(disabledCols),
                            #'disabledOrderCols':dumps(disabledOrderCols),
                            'colModel':dumps(colModel),
                            'iclock_url_rel': request.user.iclock_url_rel,
                            })