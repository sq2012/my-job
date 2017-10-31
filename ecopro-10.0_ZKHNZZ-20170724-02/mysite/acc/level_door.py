#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import string
from django.contrib import auth
#from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context, RequestContext
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
#from mysite.iclock.models import *
from mysite.acc.models import *
#from mysite.iclock.datasproc import *
from django.core.paginator import Paginator
#from mysite.iclock.datas import *
#from mysite.core.menu import *
from mysite.utils import *
from mysite.core.cmdproc import *
@login_required
def savelevel(request,key):
 #   if key=='_new_':
       # print request.POST
        timseg=request.POST.get('timeseg','1')
        name=request.POST.get('name')
        authedDoor=request.POST.get('AuthedDoor','')
        authedList=[]
        is_timeSeg_Flag=False
        is_send=True
        last_level_doors=[]
        new_level_doors=[]
        del_level_doors=[]
        new_devs=[]
        del_devs=[]
        if authedDoor:
                authedList=authedDoor.split(',')
        try:
                rg=0
                #if '-1' in authedList:
                #        authedList.remove('-1')
                #    
                #        rg=0
                        #authedList=[]
                authedList=list(AccDoor.objects.filter(id__in=authedList).distinct().values_list('id',flat=True))
                if key=='_new_':
                        lvl=level(name=name,timeseg_id=timseg,irange=rg)
                        lvl.save(force_insert=True)
                        new_level_doors=authedList
                        adminLog(time=datetime.datetime.now(),User=request.user, model=level._meta.verbose_name, object = name,action=_(u"新增")).save(force_insert=True)#
                        is_send=False
                else:
                        obj=level.objects.get(id=key)
                        if obj.timeseg_id!=int(timseg):
                                is_timeSeg_Flag=True
            
                        if obj.irange==-1:
                                is_send=False
            
                        #if rg==-1:
                        #        if obj.irange==-1:
                        #               is_send=False #此次全选，上次也全选不发送
                        #if obj.irange!=-1:#上次没有选择所有
                        l_door=level_door.objects.filter(level=int(key))
                        for t in l_door:
                                last_level_doors.append(t.door_id)
                        #else:
                         #       l_door=AccDoor.objects.filter(device__DelTag=0).order_by('id')
                        #        for t in l_door:
                         #               last_level_doors.append(t.id)
                 
                        for t in authedList:
                               if (int(t) not in last_level_doors):
                                       new_level_doors.append(int(t))
                        for t in last_level_doors:
                               if t not in authedList:
                                       del_level_doors.append(t)
                                      
                        lvl=level(id=key,name=name,timeseg_id=timseg,irange=rg)
                        lvl.save(force_update=True)
                        adminLog(time=datetime.datetime.now(),User=request.user,object=name, model=level._meta.verbose_name, action=_(u"修改")).save(force_insert=True)#
                        level_door.objects.filter(door__in=del_level_doors,level=int(key)).delete()
                #if key!='_new_':
                    
                    #if not authedList and rg == 0:
                    #        lvl=level.objects.get(id=key)
                    #        emp_s=level_emp.objects.filter(level=lvl).values('UserID')
                    #        empobjs=employee.objects.filter(id__in=emp_s)
                    #        deleteEmpfromAcc([key],empobjs)
                        #level_door.objects.filter(level=int(key)).delete()

                if new_level_doors:    
                        new_devs=list(AccDoor.objects.filter(id__in=new_level_doors).distinct().values_list('device',flat=True))
                if del_level_doors:        
                        del_devs=list(AccDoor.objects.filter(id__in=del_level_doors).exclude(device__in=new_devs).distinct().values_list('device',flat=True))


                    
                
                                   
                    
 #               if rg!=-1:
                for t in new_level_doors:
                    level_door(level=lvl,door_id=t).save()
                if new_devs:
                        tzobj=timezones.objects.filter(id=int(timseg))
                        if tzobj:
                                sendTimeZonesToAcc(tzobj,new_devs)

                if key!='_new_' and is_send:
                        if new_devs or del_devs:
                                sendLevelToAccEx([],[key],new_devs,del_devs,1)
        except Exception,e:
            print "savelevel========",e
            return getJSResponse({"ret":1,"message":u'%s'%_("Save Failed")})

        return getJSResponse({"ret":0,"message":u'%s'%_("Save Success")})
    

