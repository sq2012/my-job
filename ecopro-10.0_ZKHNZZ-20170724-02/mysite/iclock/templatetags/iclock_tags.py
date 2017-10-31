#!/usr/bin/env python
#coding=utf-8
import datetime
from django.db import models, connection
from django import template
from mysite.settings import VERSION, ENABLED_MOD, STD_DATETIME_FORMAT,SALE_MODULE
from cgi import escape
from django.utils.translation import ugettext_lazy as _
#from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from mysite.iclock.datautils import GetModel, hasPerm
#from django.db import models
from django.utils.encoding import force_unicode, smart_str
from mysite.iclock.datas import GetLeaveClassesEx,FindSchClassByID,GetExceptionText
from mysite.iclock.models import transAttState,transAbnormiteName
from mysite.iclock.datasproc import *
from mysite.utils import *
from mysite.iclock.iutils import *
from mysite.accounts.models import *
from mysite.core.mimi import *
from mysite.base.models import GetParamValue
from mysite.acc.models import *
from mysite.ipos.models import IclockDininghall
import re

register = template.Library()
LClass=[]
COLOR_DEV_STATUS=['gray','blue','skyblue','#ff8888','#13EC30','#13EC30','#FE0103','#FF830F','#FF830F','#13EC30']

@register.inclusion_tag('filters.html')
def filters(cl):
    return {'cl': cl}

def filter(cl, spec):
    return {'title': spec.title(), 'choices' : list(spec.choices(cl))}
filter = register.inclusion_tag('admin/filter.html')(filter)


@register.simple_tag
def current_time(format_string):
    return str(datetime.datetime.now())

@register.filter
def HasPerm(user, operation): #判断一个登录用户是否有某个权限
    return user.has_perm(operation)



#@register.filter
#def menuItem(user, operation): #根据一项数据模型表操作产生菜单项
    #if not isinstance(user, models.Model): user=user.user
    #op, dm=operation.split('_')
    #model=GetModel(dm)
    #if model:
        #try:
            #iclock_url_rel=user.iclock_url_rel
        #except:
            #iclock_url_rel='..'
        #if user.has_perm(operation):
            #return u'<li><a href="%s/data/%s/">%s</a></li>'%(iclock_url_rel, model.__name__, model._meta.verbose_name.capitalize())
        #else:
            #return u'<li class="disablemenu">&nbsp;&nbsp;%s</li>'%model._meta.verbose_name.capitalize()
    #return ""

#@register.filter
#def opMenuItem(user, operation): #根据一项操作产生操作菜单项!!!
    #if user.has_perm(operation):
        #return u'<li><a href="%s/data/%s/">%s</a></li>'%(iclock_url_rel, model.__name__, model._meta.verbose_name.capitalize())
    #else:
        #return u'<li class="disablemenu">&nbsp;&nbsp;'+model._meta.verbose_name+'</li>'

@register.filter
def reqHasPerm(request, operation): #判断一个当前请求的数据模型表是否有某个权限operation=browse,add,changde,delete
    return hasPerm(request.user, request.model, operation)




@register.filter
def buttonItem(request, operation): #根据一项操作产生操作菜单项!!!
    if hasPerm(request.user, request.model, operation):
        return u'<li><a href="%s/data/%s/">%s</a></li>'%(iclock_url_rel, model.__name__, model._meta.verbose_name)
    else:
        return u'<li>'+model._meta.verbose_name+'</li>'
def enable_mod(mod_name):
    if mod_name=='':
        return True
    l_mod=mod_name.split(';')
    for m in l_mod:
        if m in settings.ENABLED_MOD_TMP:
            return True

    return False



@register.simple_tag
def version():
    return VERSION+' by <a href="http://www.zksoftware.com">ZKSoftware Inc.</a>'

@register.filter
def cap(s):
    return (u"%s"%s).capitalize()

#以后采用如下函数
@register.filter
def enabled_module(mod_name):
    if mod_name=='':
        return True
    if not settings.SALE_MODULE:
        getISVALIDDONGLE(reload=1)
    
    return (mod_name in settings.ENABLED_MOD) and (mod_name in settings.SALE_MODULE)



@register.filter
def enabled_udisk_mod(mod_name):
    return ("udisk" in settings.ENABLED_MOD)
@register.filter
def enabled_weather_mod(mod_name):
    return ("weather" in settings.ENABLED_MOD)
@register.filter
def enabled_msg_mod(mod_name):
    return ("msg" in settings.ENABLED_MOD)
@register.filter
def enabled_att_mod(mod_name):
    return ("att" in settings.ENABLED_MOD)
@register.filter
def enabled_iaccess_mod(mod_name):
    return ("acc" in settings.ENABLED_MOD)

@register.filter
def enabled_fptemp_mod(mod_name):
    return ("fptemp" in settings.ENABLED_MOD)
@register.filter
def enabled_uru_mod(mod_name):
    return ("uru" in settings.ENABLED_MOD)

#@register.filter
#def enabled_mod(mod_name):
#	return (mod_name in settings.ENABLED_MOD)

@register.filter
def lescape(s):
    if not s: return ""
    #s=escape(s)
    return escape(s).replace("\n","\\n").replace("\r","\\r").replace("'","&#39;").replace('"','&quot;')

@register.filter
def LeaveList(values, field):
    l=[]
    try:
        #connection.close()
        for s in values:
            l.append(s[field])
        return ','.join(l)
    except:
        #connection.close()
        for s in values:
            l.append(s[field])
        return ','.join(l)

@register.filter
def isoTime(value):
    if value:
        return str(value)[:19]
    if value==0:
        return "0"
    return ""

@register.filter
def transLogStamp(value):
    if value and value!='0':
        return OldDecodeTime(value)[5:]
    return ""

@register.filter
def stdTime(value):
    if value:
        return value.strftime(STD_DATETIME_FORMAT)
    return ""
@register.filter
def schName(value):
    if value:
        if int(value)!=-1:
            schClass=FindSchClassByID(int(value))
            if schClass:
                return schClass['SchName']
        else:
            return _('NoSchClass')
    return ""

@register.filter
def hourAndMinute(value):
    if value:
        h=str(int(value)/60)
        m=str(int(value)%60)
        if int(m)<10:
            m='0'+str(m)
        return h+':'+m
    return ""

@register.filter
def objj(value):
    if value:
        try:
            return value.decode('gb2312').encode('utf-8')
        except:
            return value
    return ""

@register.filter
def dept_related(value):
    r=""
    j=0
    u=value
    if u:
        deptids=userDeptList(u)
        for t in deptids:
            if j>1:
                r+="..."
                break
            r+=u'%s'%department.objByID(t).DeptName+","
            j+=1
        return r[:-1]
    return r


@register.filter
def role_related(value):
    r=""
    j=0
    if value:
        for t in value:
            if j>2:
                r+="...,"
                break
            r+=t.roleid.roleName+","
            j+=1
        return r[:-1]
    return r
@register.filter
def shortTime0(value):
    if value:
        return value.strftime('%y-%m-%d %H:%M')
    return ""
@register.filter
def shortTime(value):
    if value:
        return value.strftime('%y-%m-%d %H:%M:%S')
    return ""

@register.filter
def vshortTime(value):
    if value:
        return value.strftime('%y%m%d%H%M')
    return ""

@register.filter
def shortDTime(value):
    if value:
        return value.strftime('%m-%d %H:%M')
    else:
        return ''
@register.filter
def onlyTime(value):
    if value:
        try:
            return value.strftime('%H:%M')
        except:
            return (value+datetime.timedelta(100)).strftime('%H:%M:%S')
    elif str(value)=='00:00:00':
        return '00:00'
    else:
        return ""

@register.filter
def shortDate(value):
    if value:
        return value.strftime('%y-%m-%d')
    return ""
@register.filter
def shortDate4(value):
    if value:
        return value.strftime('%Y-%m-%d')
    return ""
@register.filter
def shortDate41(value):
    if value:
        if value.strftime('%Y-%m-%d')=='1900-01-01':
            return ''
        else:
            return value.strftime('%Y-%m-%d')
    return ""

Absent={
    "0":_("No"),
    "1":_("Yes"),
    }
@register.filter
def isYesNo(value):
    if value:
        return Absent['1']
    return Absent['0']

@register.filter
def isTrueOrFalse(value):
    if value:
        return Absent['0']
    return Absent['1']


GENDER_CHOICES = {
    'M': _('Male'),
    'F': _('Female'),
}
@register.filter
def getSex(value):
    try:
        return GENDER_CHOICES[value].title()
    except:
        return ''
#
#@register.filter
#def getRoles(value):
#	if value:
#		userRole={}
#		role=userRoles.objects.all()
#		for i in role:
#			userRole[i.roleid]=i.roleName
#		try:
#			return userRole[value]
#		except:
#			return ''
#	else:
#		return ''
#
@register.filter
def getother(value):
    return getother_process(value)

@register.filter
def isOdd(value):
    if int(value)%2!=0:
        return 1
    else:
        return 0

def getAttStateStr(s):
    if s:
        return transAttState(s)
    return "" 

@register.filter
def StateName(value):
    if value:
        return getAttStateStr(value)
    return ""

@register.filter
def left(value, size):
    s=(u"%s"%value)
    if len(s)>size:
        return s[:size]+" ..."
    return s

#@register.filter
#def HasPerm(user, operation):
#	return user.has_perm(operation)

@register.filter
def Leave(value):
    LClass=GetLeaveClassesEx(1)
    for s in  LClass:
        if value==s["LeaveID"]:
            return s["LeaveName"]
    return ""
@register.filter
def ExceptionStr(value):
    if value:
        return GetExceptionText(value)
    return ""
@register.filter
def AbnormiteName(value):
    if value:
        return transAbnormiteName(value)
    return ""

@register.filter
def PackList(values, field):
    l=[]
    try:
        for s in values:
            l.append(s[field])
        return ','.join(l)
    except Exception,e:
        print "PackList==",e
        for s in values:
            l.append(s[field])
        return ','.join(l)


#def _(s): return s


@register.filter
def cmdName(value):
    return getContStr(value)

DataContentNames={
    'TRANSACT':u'%s'%(_('Transaction')),
    'USERDATA':u'%s'%(_('employee info/fingerprint '))}

@register.filter
def dataShowStr(value):
    if value in DataContentNames:
        return value+" <span style='color:#1C94C4;'>"+DataContentNames[value]+"</span>"
    return value

@register.filter
def colorShowStr(value):
    shex=str(hex(int(value)))
    shex=shex[2:]
    shex="000000"+shex
    shex=shex[len(shex)-6:]
    apage="<P style='background-color:#"+shex+"'>"+str(value)+"</P>"
    return apage


@register.filter
def cmdShowStr(value):
    value=re.sub("[\t\r\n]"," ",value)
    return left(value, 50)+" <span style='color:#1C94C4;'>"+getContStr(value)+"</span>"

@register.filter
def deptShowStr(value):
    #value=re.sub(","," ",value)
    SN=value.SN
    depts=''
    if value.ProductType in [3,4,5,15,25]:
        deptlist=getZoneBySN(SN)
        for d in deptlist:
            try:
                obj=zone.objects.get(id=d)
                if obj.DelTag==1:
                    depts+=obj.name+u'(已删除),'
                else:
                    depts+=obj.name+','
            except:
                pass
    elif value.ProductType in [11,12,13]:
        deptlist=getDiningBySN(SN)
        for d in deptlist:
            try:
                obj=Dininghall.objects.get(id=d)
                depts+=obj.name+','
            except:
                pass
    else:
        deptlist=getDepartmentBySN(SN)
        # if deptlist==[]:
        #     depts += u'%s,' % _(u'所有部门')
        #     return depts[:-1]
        if -1 in deptlist:
            depts+=u'%s,'%_(u'所有部门')
        else:
            j=0
            for d in deptlist:
                if j>1:
                    depts+='...,'
                    break
                obj=department.objByID(d)
                if obj:
                    depts+=obj.DeptName+','
                    j+=1

    return depts[:-1]

@register.filter
def thumbnailUrl(obj):
    try:
        url=obj.getThumbnailUrl()
        if url:
            try:
                fullUrl=obj.getImgUrl()
            except: #only have thumbnail, no real picture
                return "<img src='%s' />"%url
            else:
                if not fullUrl:
                    return "<img src='%s' />"%url
            return "<a href='#' onmouseover=showphotodiv(this,'%s') onmouseout='dropphotodiv()'><img src='%s' /></a>"%(fullUrl, url)
    except Exception,e:
        import traceback;print traceback.print_exc()
        print "thumbnailUrl ",e
        pass

    return ""

@register.filter
def thumbnailUrlz(obj):
    try:
        url=obj.getThumbnailUrlz()
        if url:
            try:
                fullUrl=obj.getImgUrlz()
            except: #only have thumbnail, no real picture
                return "<img src='%s' />"%url
            else:
                if not fullUrl:
                    return "<img src='%s' />"%url
            return "<a href='#' onmouseover=showphotozdiv(this,'%s') onmouseout='dropphotozdiv()'><img src='%s' /></a>"%(fullUrl, url)
    except Exception,e:
        print ""
        pass

    return ""

@register.filter
def trans_thumbnailUrl(obj,user):
    try:
        fullUrl=obj.getImgUrl(user)
    except: #only have thumbnail, no real picture
        return ""
    if fullUrl:
        return "<a href='#' onmouseover=showphotodiv(this,'%s') onmouseout='dropphotodiv()'><img src='%s' style='width:80px;height:100px;' /></a>"%(fullUrl, fullUrl)
    return ""

@register.filter
def GetAnnualleaves(value):
    return GetAnnualleave(value)


@register.filter
def GetUsedAnnualleaves(value,dateid):
    from mysite.iclock.datas import NormalAttValue
    LClass=GetLeaveClassesEx(1)
    LeaveID=0
    Unit=3
    MinUnit=1
    remaindproc=1
    for t in LClass:
        if t['LeaveID']==int(dateid) and t['LeaveType']==5:
            MinUnit=t['MinUnit']
            Unit=t['Unit']
            LeaveID=t['LeaveID']
            remaindproc=t['RemaindProc']
            break
    if LeaveID==0:
        return 0
    InScopeTime=0
    ys=datetime.datetime.now()
    months=1
    days=1
    ann=annual_settings.objects.filter(Name="month_s")
    if ann.count()>0:
        months=int(ann[0].Value)
    ann=annual_settings.objects.filter(Name="day_s")
    if ann.count()>0:
        days=int(ann[0].Value)
    y1=datetime.datetime(ys.year,months,days,0,0)
    if ys>y1:
        y2=datetime.datetime(year=y1.year+1,month=y1.month,day=y1.day)
    else:
        y2=y1
        y1=datetime.datetime(year=y1.year-1,month=y1.month,day=y1.day)
    AttExcep=AttException.objects.filter(UserID=int(value),ExceptionID=LeaveID,InScopeTime__gt=0,AttDate__lte=y2,AttDate__gt=y1)
    for Exc in AttExcep:
        InScopeTime+=NormalAttValue(Exc.InScopeTime,MinUnit,Unit,remaindproc)
    return InScopeTime
@register.filter
def GetempAnnualleaves(Annualleave,Hiredday):
    if Hiredday==None:
        return Annualleave
    elif str(type(Hiredday))!="<type 'datetime.date'>" and str(type(Hiredday))!="<type 'datetime.datetime'>":
        return 0
    else:
        nowyear=datetime.datetime.now().year
        hireyear=checkTime(Hiredday).year
        if hireyear<1960:
            return 0
        diff=nowyear-hireyear
        re=0
        if diff>=1 and diff<10:
            re=5
        elif diff>=10 and diff<20:
            re=10
        elif diff>=20:
            re=15
        if Annualleave!=None:
            if Annualleave<re:
                re=Annualleave
        return re
@register.filter
def trim(value):
    if not value and value!=0:return ""
    if value==" ":
        value=value.strip(" ")
    if str(type(value))=="<type 'unicode'>" or type(value)==type(" "):
        value=value.replace("\n"," ")
    return value
@register.filter
def killnone(value):
    if not value or value==u'None':
        value=""
    return value

@register.filter    
def field_as_td_h(field,cols):
    lbl=field.label_tag()
    c=1
    try:
        c=cols
    except:
        pass
    if c!=1:
        helptext=field.help_text and ("<p>%s</p>"%unicode(field.help_text)) or ""
    else:
        helptext=field.help_text and ("<span>%s</span>"%unicode(field.help_text)) or ""


    if field.name != 'id':
        if field.field.required:
            lbl="<font color='red'>*</font>"+field.label_tag()

    f_html=u"<th>%s</th><td style='vertical-align:top;'>%s%s%s</td>"%(
        lbl,
        field.as_widget(),
        field.errors and "<ul class='errorlist'>%s</ul>"%("".join(["<li>%s</li>"%e for e in field.errors])) or "",helptext)
    #        field.help_text and ("<p>%s</p>"%unicode(field.help_text)) or "")
    #        helptext)
    return f_html


@register.filter    
def getStateStr(state):
    if(state>=0):# and  state<len(DEV_STATUS)):
        str=u"<span style='color:%s ';>%s</span>"%(COLOR_DEV_STATUS[state],get_DEV_STATUS()[int(state)])
        return str
    return state

@register.filter    
def getRecordState(state):
    if state==None:
        state=''
    return getRecordName(state)

@register.filter    
def getMeetRecordState(state):
    gStatus=GetRecordStatus()
    ret=state
    if state=='I':
        ret=u'%s'%(_(u"参会签到"))
    elif state=='O':
        ret=u'%s'%(_(u"参会签退"))
    return ret

@register.filter    
def get_params(pName,request=None):
    from mysite.base.sysview import getDefaultValue_opt_save_fields
    default_value="0"
    if pName=="opt_basic_enroll":
        if not 'uru' in settings.ENABLED_MOD:
            return '0'
        default_value=getDefaultValue_opt_save_fields('basic','enroll')
        isEnroll=GetParamValue("opt_basic_enroll",default_value)
        if isEnroll=='1':
            if request:
                if request.user.has_perm('iclock.enroll_employee'):
                    return '1'
        return '0'


    elif pName=='opt_email_forgot':
        default_value=getDefaultValue_opt_save_fields('email','forgot')
    elif pName=="opt_ac_options":
        if not 'acc' in settings.ENABLED_MOD:
            return '0'
        else:
            return '1'
    elif pName=="opt_basic_algversion":
        default_value=getDefaultValue_opt_save_fields('basic','algversion')
    elif pName in ['opt_users_rec_pic','opt_basic_emp_pic','opt_users_vis_pic','opt_users_start_page']:
        if pName in ['opt_users_start_page']:
            default_value='1'
        if pName in ['opt_users_rec_pic']:
            default_value='0'
        default_value=GetParamValue(pName,default_value,request.user.id)
    else:
        p=GetParamValue(pName,default_value)
        if p=='on':
            p='1'
        return p
    #print default_value,pName
    return default_value

@register.filter
def get_State_State(value):
    return get_State_States(value)
@register.filter
def getEmpShift(value,flag):
    r=""
    if flag==0:
        ru=USER_OF_RUN.objects.filter(UserID=value).order_by("-id")[:1]
        for u in ru:
            r=datetime.datetime.strftime(u.StartDate,'%Y-%m-%d')+' '+datetime.datetime.strftime(u.EndDate,'%Y-%m-%d')+' '+u.NUM_OF_RUN_ID.Name
    elif flag==1:
    
        ru=USER_TEMP_SCH.objects.filter(UserID=value).order_by("-id").exclude(SchclassID__lt=1)[:1]
        for u in ru:
            r=datetime.datetime.strftime(u.ComeTime,'%Y-%m-%d %H:%M')+' '+datetime.datetime.strftime(u.LeaveTime,'%Y-%m-%d %H:%M')+' '+schName(u.SchclassID)
    return r
@register.filter
def getFlag(id):
    return getFlagValue(id)
@register.filter
def getTimeDept(value):
    u=value
    if u.is_superuser:
        return u'%s'%_(u"所有部门时段")
    s=department.objByID(u.AutheTimeDept)
    if not s:
        s=u'%s'%_(u"所有公共时段")
    return s

@register.filter
def getUserCreator(value):
    s=''
    try:
        users=UserAdmin.objects.filter(owned=value.id,dataname=str(MyUser._meta)).values('user')
        myuser=MyUser.objects.filter(id__in=users)
        if myuser:
            s=myuser[0].username
    except Exception,e:
        print 'getCreator =======',e
    return s

@register.filter
def getGroupCreator(value):
    s=''
    try:
        users=UserAdmin.objects.filter(owned=value.id,dataname=str(Group._meta)).values('user')
        myuser=MyUser.objects.filter(id__in=users)
        if myuser:
            s=myuser[0].username
    except Exception,e:
        print 'getGroupCreator =======',e
    return s


@register.filter
def defaultEx(value):
    if value:
        return value
    elif (value is None) or (value==""):
        return ""
    return 0




@register.filter
def filteryuanyin(value):
    try:
        value=escape(value)
    except:
        value=''
    return value

@register.filter
def getWorkAge(value,flag):
    id=int(value)
    d=datetime.datetime.now()
    ym=flag.GET.get('y',"%s-%s"%(d.year,d.month))
    y_m=ym.split('-')
    months=1
    days=1
    ann=annual_settings.objects.filter(Name="month_s")
    if ann.count()>0:
        months=int(ann[0].Value)
    ann=annual_settings.objects.filter(Name="day_s")
    if ann.count()>0:
        days=int(ann[0].Value)
    d_y_m=datetime.date(int(y_m[0]),months,days)
    e=employee.objByID(id)
    d_h=e.Hiredday
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
            return "%s年"%y

    return ""

@register.filter
def getannual_fading(value,request):
    from mysite.iclock.nomodelview import getannual_f
    day=request.GET.get('y')+'-01'
    return getannual_f(value,day)

@register.filter
def getannual_gongsi(value,request):
    from mysite.iclock.nomodelview import getuserannual
    day=request.GET.get('y')+'-01'
    return getuserannual(value,day)


@register.filter
def GetAnnualleaves_ex(value,day):
    from mysite.iclock.nomodelview import getuserannual
    day=day.strftime("%Y-%m-%d")
    return getuserannual(value,day)
    
@register.filter
def IsSuper(user): #判断一个登录用户是否有某个权限
    return user.is_superuser
    
@register.filter
def showTitle(value):
    try:
        r=userRoles.getallrole()
        return r[value]
    except:
        return value

@register.filter
def device_memo(value):
    dev=value
    s=''
    if dev.ProductType not in [11,12,13]:
        if dev.isFptemp and dev.AlgVer and dev.AlgVer!='0':
            s+=u'%s'%_(u'指纹版本:')+dev.AlgVer+' '
        if dev.isFace and dev.FaceAlgVer and dev.FaceAlgVer!='-1' and dev.FaceAlgVer!='0':
            s+=u'%s'%_(u'面部版本:')+dev.FaceAlgVer+' '
        if dev.Authentication==2:
            s+=u'%s'%_(u'组合验证')+' '
        if hasattr(dev,'FvFunOn') and dev.FvFunOn==1:
            if hasattr(dev,'FvVersion'):
                s+=u'%s'%_(u'静脉版本:')+dev.FvVersion+' '

        if hasattr(dev,'PvFunOn') and dev.PvFunOn==1:
            if hasattr(dev,'PvVersion'):
                s+=u'%s'%_(u'掌纹版本:')+dev.PvVersion+' '


    if dev.pushver:
        s+='PushVer:'+dev.pushver+' '
    if dev.TransTime and dev.TransTime.year!=2000:
        s+=u'%s:%s'%(u'同步人员',shortDTime(dev.TransTime))
    #    if not dev.ProductType:
    #	s+=u'%s'%(u'未设定设备用途')
    return s

@register.filter
def devdn(value):
    id = value.id
    c=IclockDininghall.objects.filter(dining=id).exclude(SN__DelTag=1).count()
    return c

@register.filter
def showprocess(val):
    value=val.process
    if value:
        role=cache.get("%s_userRoles"%(GetParamValue('ROLEVERSION')))

        if role:
            for r in role:
                if val.roleid==r['roleid']:
                    dd=",<font color='red'>"+r['roleName']+"</font>,"
                else:
                    dd=","+r['roleName']+","
                cc=","+str(r['roleid'])+","
                value=value.replace(cc,dd)
        else:
            role=userRoles.objects.all()
            ll=[]
            for r in role:
                l={}
                l['roleid']=str(r.roleid)
                l['roleName']=r.roleName
                ll.append(l)
                if val.roleid==r.roleid:
                    dd=",<font color='red'>"+r.roleName+"</font>,"
                else:
                    dd=","+r.roleName+","
                cc=","+str(r.roleid)+","
                value=value.replace(cc,dd)
            dt=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            cache.set("ROLEVERSION",dt)
            cache.set("%s_userRoles"%(dt),ll)
        value=value[1:-1]
        value=value.replace(',','--> ')
    else:
        value=''
    return value


@register.filter
def isModule(value,mod_name):
    return value in mod_name
 
@register.filter
def show_ProductType(value):
    if not value:return ''
    if value==11:
        return u'消费机'
    elif value==12:
        return u'出纳机'
    elif value==13:
        return u'补贴机'
    elif value==9:
        return u'考勤机'
    elif value==4:
        return u'门禁一体机'
    elif value==5:
        return u'控制器'

    return ''
@register.filter
def show_LastLogStamp(value):
    if not value:return ''

    dev=value
    v=dev.ProductType
    if not v:return ''
    ret=''
    if v==11:
        ret=OldDecodeTime(dev.PosLogStamp)[5:]
    elif v==12:
        ret=OldDecodeTime(dev.FullLogStamp)[5:]
    elif v==13:
        ret=OldDecodeTime(dev.AllowLogStamp)[5:]
    return ret
@register.filter
def show_LastLogId(value):
    if not value:return ''
    dev=value
    v=dev.ProductType
    if not v:return ''
    ret=''
    if v==11:
        ret=dev.PosLogStampId
    elif v==12:
        ret=dev.FullLogStampId
    elif v==13:
        ret=dev.AllowLogStampId
    return ret
@register.filter
def get_apb_rule_name(item):
    s=item.get_details()
    return s

@register.filter
def get_interlock_rule_name(item):
    s=item.get_details()
    return s

@register.filter
def filter_config_option(key):
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))

    if key=='POS_ID':
        if settings.CARDTYPE==1:
            return True
    elif key=='POS_IC':
        if settings.CARDTYPE==2:
            return True
    return False

@register.filter
def trigcon(id):
    objs=linkage_trigger.objects.filter(linkage=id)
    c=0
    s=''
    for t in objs:
        s=s+' %s'%get_EVENT_CHOICES_name(t.trigger_cond)
        if c>2:break
        c+=1
    #if s=='':
    #	return id
    return s

@register.filter
def getclearmoney(sys_card_no,id):
    csz=CardCashSZ.objects.filter(allow_batch=id,sys_card_no=sys_card_no,hide_column=2,blance=0,money__gt=0)
    if csz:
        return csz[0].money
    else:
        return 0
@register.filter
def AccRecords(item,iflag):
    if iflag=='card':
        if item.event_no==6:
            return ''
        return item.card_no
    elif iflag=='verify':
        if item.event_no==6:
            return get_EVENT_CHOICES_name(item.verify)
        return item.get_verify_display()
    elif iflag=='point':
        return get_event_point_name(item)

@register.filter
def getEmpLostCard(id,name):
    e=employee.objByID(id)
    obj = IssueCard.objects.filter(UserID = e.id,cardstatus = 3)
    if obj:
        if name=='cardno':
            return obj[0].cardno
        elif name=='sys_card_no':
            return obj[0].sys_card_no
        elif name=='blance':
            return obj[0].blance
    return ''
@register.filter
def IsValidLog(value,flag):
    ret=3
    sPic=''
    if flag=='att':
        if value.Reserved and value.Reserved!='0':
            de_code=decryption(value.Reserved)
            if value.TTime.strftime("%H%M%S%m%d")==de_code:
                ret=1
            else:
                ret=0
        else:
            ret=2
    else:
        ret=3
    if ret==1:
        sPic="""%s"""%("<img   src='../media/img/ok.gif' style='width:20px;height:10px;'/>")
    elif ret==0:
        sPic="""%s"""%("<img   src='../media/img/error.gif' style='width:20px;height:10px;'/>")

    return sPic
@register.filter
def isDelete(name,value):
    if value==0:
        return name
    else:
        return name+u'(已删除)'
    
# @register.simple_tag
# def authorizeinfo():
#     return "客户编码:%s <br> 授权点数：%s"%('980001', '300') #此处授权获取信息
@register.filter
def isAddIclock(value):
    try:
        dev=getDevice(value.SN)
        return isYesNo(1)
    except:
        return isYesNo(0)

@register.filter
def getFileUrl(item):
    content = ''
    try:
        u = USER_SPEDAY_DETAILS.objects.get(USER_SPEDAY_ID=item)
        if u.file:
            url = '/iclock/file/userSpredyFile/%s'%u.file
            content=u"&nbsp;<a  title='查看上传文件' onclick='getFileDetail(\\\"%s\\\")'style='color:green;'>文件浏览</a>&nbsp;"%url
    except:
        return ''
    return content

@register.filter
def empborrowState(value):
    if value==0:
        return u'借调中'
    elif value==1:
        return u'已恢复'
    elif value==2:
        return u'未借调'

@register.filter
def getempworkcode(value):
    emp = employee.objByID(value)
    return emp.Workcode or ''

@register.filter
def getemppin(value):
    emp = employee.objByID(value)
    return emp.PIN or ''

@register.filter
def getempname(value):
    emp = employee.objByID(value)
    return emp.EName or ''

@register.filter
def getempdeptid(value):
    dept = department.objByID(value)
    return dept.DeptNumber or ''

@register.filter
def getempdeptname(value):
    dept = department.objByID(value)
    return dept.DeptName or ''

@register.filter
def getborrowdatas(value,key):
    try:
        if key=='title':
            return employee_borrow.objects.get(userID=value).toTitle
        elif key=='deptid':
            return employee_borrow.objects.get(userID=value).toDept
        elif key=='deptname':
            id = employee_borrow.objects.get(userID=value).toDept
            return getempdeptname(id)
    except:
        return ''