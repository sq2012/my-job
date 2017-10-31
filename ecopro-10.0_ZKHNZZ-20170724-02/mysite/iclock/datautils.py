#coding=utf-8
from mysite.iclock.models import *
from django.utils.encoding import smart_str
import operator
from mysite.iclock.filterspecs import FilterSpec
from mysite.iclock.iutils import *
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context, RequestContext
from django.conf import settings
#from mysite.iclock.datas import *
from django import forms
from django.contrib.auth import get_user_model
from mysite.base.models import *
#from mysite.acc.models import *
from mysite.meeting.models import *
from mysite.ipos.models import *
from mysite.visitors.models import *
from mysite.acc.getBaseData import userZoneList
from django.apps import apps

ALL_VAR = 'all'
ORDER_VAR = 'o'
ORDER_TYPE_VAR = 'ot'
PAGE_VAR = 'page'
SEARCH_VAR = 'q'
IS_POPUP_VAR = 'pop'
ERROR_FLAG = 'e'
STATE_VAR = 's'
EXPORT_VAR = 'f'
PAGE_LIMIT_VAR = 'l'
TMP_VAR = 't'
STAMP_VAR='stamp'
YEAR_VAR='y'
Contained='isContainChild'
sidx="sidx"
lookupDic={}


# class ZReadOnlyWidget(forms.widgets.TextInput):
#     def __init__(self, attrs={}):
#     super(ZReadOnlyWidget, self).__init__(attrs=attrs)
#     def value_from_datadict(self, data, files, name):
#         value=data.getlist(name)
#         if not value: return None
#         multiple=False
#         if hasattr(self, "choices") and isinstance(self.choices, forms.models.ModelChoiceIterator):
#             #value=[self.choices.queryset.get(pk=item) for item in value]
#             if isinstance(self.choices.field, forms.models.ModelMultipleChoiceField):
#                 multiple=True
#         if not multiple:
#             value=value[0]
#         #print "value_from_datadict", value, name
#         return value
#     def render(self, name, data, attrs=None):
#         try:
#             self.attrs.update(attrs)
#         #print "===========================",name,self.attrs
# #            print hasattr(self.choices, "queryset")
#         display=''
#             if hasattr(self, "choices"):
#                 if hasattr(self.choices, "queryset"):
#                     #print "000111111111111",data,type(data)
#                     if type(data)==list:
#                         display="<br>".join([u"%s"%self.choices.queryset.get(pk=item) for item in data])
#             #print "2222222==",display
#                         display2="\n".join([u"<input value=\"%s\", name=\"%s\" type=\"hidden\" />"%(item, name) for item in data])
#                         return u"""<div  style=\"height:60px;overflow-x:auto; overflow-y:scroll; border:1px solid #CAE2F9\"><ul><li>%s</li></ul></div>%s"""%(display, display2)
#                     if data:
#             display=self.choices.queryset.get(pk=data)
# #		    print "11111111111",display
#                 else:
#                     display=u"%s"%(dict(self.choices)[data])
#             #print "-----------",display
#             self.attrs['readonly']='readonly'
#                 return super(ZReadOnlyWidget, self).render('', display, attrs=self.attrs)+\
#                     (u'<input name="%s" value="%s" type="hidden">'%(name, data or ''))
#         except:
#                 import traceback; traceback.print_exc()
#         return u'<input name="%s" value="%s" readonly="readonly" >'%(name, data or "")

# def form_field_readonly(f, **kwargs):
#     kwargs.update({'widget': ZReadOnlyWidget})
# #    print "form_field_readonly", f
#     ret = f.formfield(**kwargs)
# #    print "form_field_readonly: w=", ret.widget
#     #print "form_field_readonly: ret=", ret
#  #   print "form_field_readonly: kwargs=", kwargs
#
#     return ret




def creatOracleParam(userList):
    if len(userList)>=1000 :
        mul=len(userList)/999
        ls="(userid IN (%s)"%(','.join(['%s' % int(i) for i in userList[:999]]))
        for k in range(1,mul+1):
            st=999*k
            ed=999*(k+1)
            ss=','.join(['%s' % int(i) for i in userList[st:ed]])
            s=" or userid IN (%s)"%ss
            ls=ls+s
        ls=ls+')'
    else:
        ls="userid IN (%s) " %(','.join(['%s' % int(i) for i in userList]))
    return ls


def createNewOrdUrl(ordUrl, fieldName, remove):
    ordFields=(ordUrl or "").split(',')
    if "" in ordFields: ordFields.remove("")
    desc=False
    sorted=False
    if fieldName in ordFields:
        sorted=True
        if remove:
            ordFields.remove(fieldName)
        else:
            index=ordFields.index(fieldName)
            ordFields[index]="-"+fieldName
    elif ("-"+fieldName) in ordFields:
        desc=True
        sorted=True
        if remove:
            ordFields.remove("-"+fieldName)
        else:
            index=ordFields.index("-"+fieldName)
            ordFields[index]=fieldName
    elif not remove:
        desc=True
        ordFields.append(fieldName)
    else:
        return ""
    return ",".join(ordFields), sorted, desc

class FieldNameMulti(object): #支持多字段排序
    def __init__(self, cl, orderUrl=True):
        self.cl=cl
        self.desc=1
        self.orderUrl=orderUrl

    def __getitem__(self, fieldName):
        for f in self.cl.model._meta.fields:
            if f.name==fieldName:
                orderStr, sorted, desc=createNewOrdUrl(self.cl.orderStr, fieldName, False)
                orderStr=self.cl.get_query_string({ORDER_VAR:orderStr},[ORDER_VAR]).replace("'","\\'").replace('"','\\"')
                if self.orderUrl:
                    if sorted:
                        if desc:
                            ret="<th class='sorted descending'>%s<div class='order_hd'><a href='"+orderStr+"'>^</a>"
                        else:
                            ret="<th class='sorted ascending'>%s<div class='order_hd'><a href='"+orderStr+"'>v</a>"
                        removeOrderStr, sorted, desc=createNewOrdUrl(self.cl.orderStr, fieldName, True)
#						print "ORDER_: ", removeOrderStr
                        if removeOrderStr:
                            removeOrderStr=self.cl.get_query_string({ORDER_VAR:removeOrderStr},[ORDER_VAR]).replace("'","\\'").replace('"','\\"')
                        else:
                            removeOrderStr=self.cl.get_query_string({},[ORDER_VAR])
                        ret+="<a href='"+removeOrderStr+"'>X</a></div></th>"
                    else:
                        ret="<th>%s<div class='order_hd'><a href='"+orderStr+"'>^</a></div></th>"
                    ret=ret%((u"%s"%f.verbose_name).capitalize())
                else:
                    ret="<th abbr='"+fieldName+"'>%s</th>"%(u"%s"%f.verbose_name).capitalize()
                return ret
        return ""

class FieldName(object):
    def __init__(self, cl, orderUrl=True):
        self.cl=cl
        self.desc=1
        self.orderUrl=orderUrl
        if cl.orderStr:
            if cl.orderStr[0:1]=="-":
                self.desc=0
                self.orderField=cl.orderStr[1:]
            else:
                self.orderField=cl.orderStr
        else:
            self.orderField=""
    def __getitem__(self, fieldName):
        for f in self.cl.model._meta.fields:
            if f.name==fieldName:
                orderStr=fieldName
                if self.orderUrl:
                    if fieldName==self.orderField:
                        if self.desc:
                            orderStr="-%s"%fieldName
                            ret="<th class='sorted descending'><a href='%s'>%s</a></th>"
                        else:
                            ret="<th class='sorted ascending'><a href='%s'>%s</a></th>"
                    else:
                        ret="<th><a href='%s'>%s</a></th>"
                    orderStr=self.cl.get_query_string({ORDER_VAR:orderStr},[ORDER_VAR])
                    orderStr=string.join(orderStr.split('"'),'\\"')
                    orderStr=string.join(orderStr.split("'"),"\\'")
                    ret=ret%(orderStr, (u"%s"%f.verbose_name).capitalize())
                else:
                    ret=f.verbose_name.capitalize()
                    #ret="<th abbr='"+fieldName+"'>%s</th>"%(u"%s"%f.verbose_name).capitalize()
                return ret
        return ""


def openExportFmt(request):
    try:
        formats=file(settings.TEMPLATE_DIRS[0]+"/export_formats_"+request.LANGUAGE_CODE+".txt","r").readlines();
    except:
        formats=file(settings.TEMPLATE_DIRS[0]+"/export_formats.txt","r").readlines();
    return formats

def xlist2str(list1 = []):
    str1 = ""
    if list1:
        for li in list1:
            str1 += li + ","
    if str1:
        str1 = str1[:-1]
    return str1

def getVerboseName(model, name):
    for field in model._meta.fields:
        if field.name == name:
            return u"%s"%field.verbose_name
    return ""

class ChangeList(object):
    def __init__(self, request, model):
        self.model = model
        self.opts = model._meta
        if not hasattr(self.opts, "admin"):
            try:
                self.opts.admin=model.Admin
            except Exception, e:
                #print "11111111111%s"%e
                pass

        self.params = dict(request.GET.items())
        self.filter_specs, self.has_filters = get_filters(self.opts, request, self.params, model)
        self.request=request
        self.orderStr=""
        self.lng=request.LANGUAGE_CODE
        if ORDER_VAR in self.params:
            self.orderStr=self.params[smart_str(ORDER_VAR)]
        elif model==iclock:
            self.orderStr="Alias"
        elif model==department:
            self.orderStr="DeptID"
        elif model==employee:
            self.orderStr="DeptID,PIN"
        elif model==USER_SPEDAY:
            self.orderStr="UserID__DeptID,UserID__PIN,-ApplyDate"
        elif model in[BioData,USER_OF_RUN]:
            self.orderStr="UserID__DeptID,UserID__PIN"
        elif  model==transactions:
            self.orderStr="UserID__DeptID,UserID__PIN,TTime"
        elif  model==checkexact:
            self.orderStr="UserID__DeptID,UserID__PIN,-CHECKTIME"
        elif  model in [attShifts,AttException,attpriReport]:
            self.orderStr="UserID__DeptID,UserID__PIN,AttDate"
        elif model==attRecAbnormite:
            self.orderStr="UserID__DeptID,UserID__PIN,checktime"
        elif model==devcmds:
            self.orderStr="-id"
        elif model._meta.pk.name=="id":
            self.orderStr="-id"
        self.FieldName=FieldName(self, request.GET.get(ORDER_TYPE_VAR, '0')=='1')
        searchHint=[]

        if hasattr(self.opts, "admin"):
            for f in self.opts.fields:
                try:
                    for field in self.opts.admin.search_fields:
                        if f.name in field or f.name+"__" in field:
                            searchHint.append((u"%s"%f.verbose_name).capitalize())
                except: pass
        if len(searchHint)>0:
            self.searchHint=string.join(searchHint, ",")
        else:
            self.searchHint=None
    def GetCopyFields(self):
        self._initCopyFields(self, self.model)

    def _initCopyFields(self, model):
        objs = model.objects.all()
        if objs:
            obj = objs[0]
            if model == employee or model == iclock:
                return xlist2str([field + ":" + u"%s"%getVerboseName(model, field)for field in obj.GetCopyFields()])
            else:
                return ""

    def get_query_string(self, new_params=None, remove=None):
        if new_params is None: new_params = {}
        if remove is None: remove = []
        p = self.params.copy()
        for r in remove:
            for k in p.keys():
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if k in p and v is None:
                del p[k]
            elif v is not None:
                p[k] = v
        return '?' + '&amp;'.join([u'%s=%s' % (k, v) for k, v in p.items()]).replace(' ', '%20')

    def getDataExportsFormats(self):
        fl=[]
        formats=openExportFmt(self.request)
        index=0
        for f in formats:
            fds =(f+"_").split("_")
            index+=1
            if fds[0]==self.model.__name__ and fds[1]:
                fds=(fds[1]+":").split(":")
                if fds[0] and fds[1]:
                    fl.append((index, unicode(fds[0].split('.')[0].decode("utf-8")),))
        return fl

def construct_search(field_name):
        if field_name.startswith('^'):
            return "%s__istartswith" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            return "%s__search" % field_name[1:]
        else:
            return "%s__icontains" % field_name

def get_filters(opts, request, params, dataModel):
    filter_specs = []
    try:
        if hasattr(opts, "admin") and opts.admin and opts.admin.list_filter:#  and not opts.one_to_one_field):
            filter_fields = [opts.get_field(field_name) \
                for field_name in opts.admin.list_filter]
            for f in filter_fields:
                spec = FilterSpec.create(f, request, params, dataModel)
                if spec and spec.has_output():
                    filter_specs.append(spec)
    except Exception, e:
#		print "get_filters", e.message
        pass
    return filter_specs, bool(filter_specs)

def preProcessParams(params):
    if 'x' in params.keys():
        q=params['x']
        objs=employee.objects.filter(Q(PIN__contains = q)|Q(Workcode__contains = q))
        ulist=[t.id for t in objs]
        params['UserID__in']=ulist
        del params['x']
    if 'ApplyDate__lte' in params.keys():
        q=params['ApplyDate__lte']
        q = q+' 23:59:59'
        params['ApplyDate__lte'] = q

def getAllcodes(c,request,zoneids):
    zone_parents=zone.objects.filter(parent=c)
    if zone_parents:
        for zone_parent in zone_parents:
            if int(zone_parent.id) not in zoneids:
                zoneids.append(int(zone_parent.id))
                getAllcodes(zone_parent.id,request,zoneids)
    return zoneids
def QueryData(request, dataModel):
    opts = dataModel._meta
    params = dict(request.GET.items())
    User=get_user_model()
    if not hasattr(opts, "admin"):
        try:
            opts.admin=dataModel.Admin
        except: pass
    #查询
    if fieldVerboseName(dataModel, "DelTag"):
        qs=dataModel.objects.exclude(DelTag=1)#filter(Q(DelTag__isnull=True)|Q(DelTag=0))
    else:
        try:
            qs=dataModel.objects.all()
        except Exception,e:
            print "QueryData",e
    search=request.GET.get(SEARCH_VAR,"")
    isContainedChild=request.GET.get(Contained,"")
    search=unquote(search)
    if search and hasattr(opts, "admin") and opts.admin and opts.admin.search_fields:
        for bit in search.split():
            if dataModel==employee_borrow:
                break
            or_queries = [models.Q(**{construct_search(field_name): bit}) for field_name in opts.admin.search_fields]
            other_qs = dataModel.objects.all()
            try:
                other_qs.dup_select_related(qs)
            except:
                if qs.select_related:
                    other_qs = other_qs.select_related()
            other_qs = other_qs.filter(reduce(operator.or_, or_queries))
            qs = qs & other_qs
    lookup_params={}
    lookup_params=GetLookup_params(params)
    # Apply lookup parameters from the query string.
    if lookup_params:
        lookup={}
        tflag=0
        for l in lookup_params:
#			bb = dict((k,v) for k, v in bb.iteritems() if (v and len(v[0])!=0) )
            if len(lookup_params[l])>0:
                lookup[l]=lookup_params[l]
                if isinstance(lookup[l],list):
                    if len(lookup[l])==1:        #判断该俩表是否只有一个项
                        if len(lookup[l][0])==0:    #判断这个项目是否为空
                            del lookup[l]
                if l=='processState':
                    del lookup[l]
                try:
                    tt=datetime.datetime.strptime(lookup[l],'%Y-%m-%d')
                    tflag=1
                except:
                    pass
        lookup_params=lookup.copy()
        #Process not foreign key model
        if (dataModel in [days_off]):
            preProcessParams(lookup_params)

        if(dataModel in [User]):
            if 'username__icontains' in lookup_params:
                lookup_params['username__icontains']= unquote(lookup_params['username__icontains'])#print 'come on baby',lookup_params
        if(dataModel in [Group]):
            if 'name__icontains' in lookup_params:
                lookup_params['name__icontains']= unquote(lookup_params['name__icontains'])#print 'come on baby',lookup_params

        if (dataModel in [USER_SPEDAY,USER_OVERTIME]):
            if (GetParamValue('opt_basic_approval','1')=='1' or GetParamValue('opt_basic_approval','1')==1) and 'filtertag' in lookup_params:
                roles=userRole.objects.filter(userid=request.user)
                if roles.count()>0:
                    roleid=roles[0].roleid.roleid
                    if lookup_params['filtertag']==0 or lookup_params['filtertag']=='0':
                        lookup_params['process__contains']=',%s,'%str(roleid)
                    elif lookup_params['filtertag']==1 or lookup_params['filtertag']=='1':
                        lookup_params['roleid']=roleid
                        qs = qs.exclude(State=2)
                    elif lookup_params['filtertag']==3 or lookup_params['filtertag']=='3':
                        lookup_params['oldprocess__contains']=',%s,'%str(roleid)
                    else:
                        lookup_params['process__contains']=',%s,'%str(roleid)
                        qs = qs.exclude(State=2)
                else:
                    qs=qs.filter(State=-1)#不能查询任何数据，State没有-1参数。
            if 'filtertag' in lookup_params:
                del lookup_params['filtertag']
        if (dataModel in [USER_SPEDAY,USER_OVERTIME,USER_OF_RUN,USER_TEMP_SCH,attRecAbnormite,attShifts,AttException,transactions,records,checkexact,attpriReport,adminLog,employeeLog,visitionlogs]): #and tflag: 应该是时间标识，可能会有影响其他模块 2011-01-26 cg
            st=0
            et=0
            if dataModel==transactions or dataModel==records:


                try:
                    st=datetime.datetime.strptime(lookup_params['TTime__gte'],'%Y-%m-%d')
                    et=datetime.datetime.strptime(lookup_params['TTime__lt'],'%Y-%m-%d')
                    lookup_params['TTime__lt']=lookup_params['TTime__lt']+" 23:59:59"
                except :
                    pass
            if dataModel==adminLog:
                try:
                    st=datetime.datetime.strptime(lookup_params['time__gte'],'%Y-%m-%d')
                    et=datetime.datetime.strptime(lookup_params['time__lt'],'%Y-%m-%d')
                    lookup_params['time__lt']=lookup_params['time__lt']+" 23:59:59"
                except :
                    pass
            if dataModel==employeeLog:
                try:
                    st=datetime.datetime.strptime(lookup_params['LTime__gte'],'%Y-%m-%d')
                    et=datetime.datetime.strptime(lookup_params['LTime__lt'],'%Y-%m-%d')
                    lookup_params['LTime__lt']=lookup_params['LTime__lt']+" 23:59:59"
                except :
                    pass
            if dataModel==USER_SPEDAY:
                #if 'StartSpecDay__gte' in lookup_params and 'StartSpecDay__lt' in lookup_params:
                #	st=datetime.datetime.strptime(lookup_params['StartSpecDay__gte'],'%Y-%m-%d')
                #	et=datetime.datetime.strptime(lookup_params['StartSpecDay__lt'],'%Y-%m-%d')
                #	lookup_params['StartSpecDay__lt']=lookup_params['StartSpecDay__lt']+" 23:59:59"
                #elif 'EndSpecDay__gte' in lookup_params and 'EndSpecDay__lt' in lookup_params:
                #	st=datetime.datetime.strptime(lookup_params['EndSpecDay__gte'],'%Y-%m-%d')
                #	et=datetime.datetime.strptime(lookup_params['EndSpecDay__lt'],'%Y-%m-%d')
                #	lookup_params['EndSpecDay__lt']=lookup_params['EndSpecDay__lt']+" 23:59:59"
                #elif 'ApplyDate__gte' in lookup_params and 'ApplyDate__lt' in lookup_params:
                #	st=datetime.datetime.strptime(lookup_params['ApplyDate__gte'],'%Y-%m-%d')
                #	et=datetime.datetime.strptime(lookup_params['ApplyDate__lt'],'%Y-%m-%d')
                #	lookup_params['ApplyDate__lt']=lookup_params['ApplyDate__lt']+" 23:59:59"
                if 'startdate' in lookup_params and 'enddate' in lookup_params:

                    st=datetime.datetime.strptime(lookup_params['startdate'],'%Y-%m-%d')
                    et=datetime.datetime.strptime(lookup_params['enddate'],'%Y-%m-%d')+datetime.timedelta(days=1)
                    qs=qs.filter(Q(StartSpecDay__gte=st,StartSpecDay__lt=et)|Q(StartSpecDay__lt=st,EndSpecDay__gt=st))
                    del lookup_params['startdate']
                    del lookup_params['enddate']

            if dataModel==USER_OVERTIME:
                #if 'StartOTDay__gte' in lookup_params and 'StartOTDay__lt' in lookup_params:
                #	st=datetime.datetime.strptime(lookup_params['StartOTDay__gte'],'%Y-%m-%d')
                #	et=datetime.datetime.strptime(lookup_params['StartOTDay__lt'],'%Y-%m-%d')
                #	lookup_params['StartOTDay__lt']=lookup_params['StartOTDay__lt']+" 23:59:59"
                #elif 'EndOTDay__gte' in lookup_params and 'EndOTDay__lt' in lookup_params:
                #	st=datetime.datetime.strptime(lookup_params['EndOTDay__gte'],'%Y-%m-%d')
                #	et=datetime.datetime.strptime(lookup_params['EndOTDay__lt'],'%Y-%m-%d')
                #	lookup_params['EndOTDay__lt']=lookup_params['EndOTDay__lt']+" 23:59:59"
                #elif 'ApplyDate__gte' in lookup_params and 'ApplyDate__lt' in lookup_params:
                #	st=datetime.datetime.strptime(lookup_params['ApplyDate__gte'],'%Y-%m-%d')
                #	et=datetime.datetime.strptime(lookup_params['ApplyDate__lt'],'%Y-%m-%d')
                #	lookup_params['ApplyDate__lt']=lookup_params['ApplyDate__lt']+" 23:59:59"

                if 'startdate' in lookup_params and 'enddate' in lookup_params:
                    st=datetime.datetime.strptime(lookup_params['startdate'],'%Y-%m-%d')
                    et=datetime.datetime.strptime(lookup_params['enddate'],'%Y-%m-%d')+datetime.timedelta(days=1)
                    qs=qs.filter(Q(StartOTDay__gte=st,StartOTDay__lt=et)|Q(StartOTDay__lt=st,EndOTDay__gt=st))
                    del lookup_params['startdate']
                    del lookup_params['enddate']
            if dataModel==visitionlogs:
                if 'EnterTime__gte' in lookup_params and 'EnterTime__lt' in lookup_params:
                    st=datetime.datetime.strptime(lookup_params['EnterTime__gte'],'%Y-%m-%d')
                    et=datetime.datetime.strptime(lookup_params['EnterTime__lt'],'%Y-%m-%d')
                    lookup_params['EnterTime__lt']=lookup_params['EnterTime__lt']+" 23:59:59"
                elif 'ExitTime__gte' in lookup_params and 'ExitTime__lt' in lookup_params:
                    st=datetime.datetime.strptime(lookup_params['ExitTime__gte'],'%Y-%m-%d')
                    et=datetime.datetime.strptime(lookup_params['ExitTime__lt'],'%Y-%m-%d')
                    lookup_params['ExitTime__lt']=lookup_params['ExitTime__lt']+" 23:59:59"
            if dataModel==USER_TEMP_SCH:
                st=datetime.datetime.strptime(lookup_params['ComeTime__gte'],'%Y-%m-%d')
                et=datetime.datetime.strptime(lookup_params['LeaveTime__lt'],'%Y-%m-%d')
                lookup_params['LeaveTime__lt']=lookup_params['LeaveTime__lt']+" 23:59:59"
            if dataModel==checkexact:
                if 'CHECKTIME__gte' in lookup_params.keys():
                    st=datetime.datetime.strptime(lookup_params['CHECKTIME__gte'],'%Y-%m-%d')
                    et=datetime.datetime.strptime(lookup_params['CHECKTIME__lte'],'%Y-%m-%d')
                    filtertag = request.GET.get('filtertag', '')
                    if filtertag == '4':
                        lookup_params['CHECKTIME__gte'] = st-datetime.timedelta(days=4)
                        lookup_params['CHECKTIME__lte'] = et+datetime.timedelta(days=4)
                    else:
                        lookup_params['CHECKTIME__lte']=lookup_params['CHECKTIME__lte']+" 23:59:59"
                if 'ApplyDate__gte' in lookup_params.keys():
                    #st=datetime.datetime.strptime(lookup_params['DATE__gte'],'%Y-%m-%d')
                    et=datetime.datetime.strptime(lookup_params['ApplyDate__lte'],'%Y-%m-%d')
                    lookup_params['ApplyDate__lte']=lookup_params['ApplyDate__lte']+" 23:59:59"
                if 'filtertag' in lookup_params:
                    del lookup_params['filtertag']


            if dataModel==attRecAbnormite:
                st=datetime.datetime.strptime(lookup_params['checktime__gte'],'%Y-%m-%d')
                et=datetime.datetime.strptime(lookup_params['checktime__lt'],'%Y-%m-%d')
                lookup_params['checktime__lt']=lookup_params['checktime__lt']+" 23:59:59"
            if dataModel==attShifts or dataModel== AttException or dataModel== attpriReport:
                st=datetime.datetime.strptime(lookup_params['AttDate__gte'],'%Y-%m-%d')
                et=datetime.datetime.strptime(lookup_params['AttDate__lt'],'%Y-%m-%d')
                lookup_params['AttDate__lt']=lookup_params['AttDate__lt']+" 23:59:59"
            try:
                useridstr=','.join(lookup_params['UserID__id__in'])
            except:
                useridstr=''
            userids=[]
            deptids=[]
            #if useridstr!="":
            #	userids=useridstr.split(',')
            #else:
            #	try:
            #	    if lookup_params['deptIDs']!="":
            #		deptidlist=[int(i) for i in lookup_params['deptIDs'].split(",")]
            #		deptids=deptidlist
            #		if isContainedChild=="1": #是否包含下级部门
            #			deptids=[]
            #			for d in deptidlist:#支持选择多部门
            #				if int(d) not in deptids :
            #					deptids+=getAllAuthChildDept(d,request)
            #		lookup_params['UserID__DeptID__in']=deptids
            #	except:
            #		pass
            #	try:
            #		del lookup_params['UserID__id__in']
            #	except:
            #		pass
            t=datetime.datetime.now()
#			if dataModel==attShifts:
#				MainCalc(userids,deptids,st,et)
            t1=datetime.datetime.now()-t
        try:
            if lookup_params['deptIDs']!="":
                try:
                    deptidlist=[int(i) for i in lookup_params['deptIDs'].split(",")]
                except:
                    deptidlist=[1]
                deptids=deptidlist
                alldept_flag=False
                if isContainedChild=="1": #是否包含下级部门
                    deptids=[]
                    if 1 in deptidlist: #如果选择的是总公司，理解为是全部部门
                            if(request.user.is_superuser) or ( request.user.is_alldept):
                                alldept_flag=True
                    if not alldept_flag:
                        for d in deptidlist:#支持选择多部门
                            if int(d) not in deptids :
                                deptids+=getAllAuthChildDept(d,request)
#					t2=datetime.datetime.now()
#					print "=========tttt===",t2-t1
                #当部门数过多时理解成为不限制部门，一般情况下，只有超级管理员选根部门时才能出现，普通管理员不应该授权过多部门
                #if len(deptids)<1000:
                if not alldept_flag:
                    if dataModel==employee or dataModel==department:
                        lookup_params['DeptID__in']=deptids
                    else:
                        lookup_params['UserID__DeptID__in']=deptids
#				lookup_params['UserID__DeptID__in']=deptids
            del lookup_params['deptIDs']
        except:
            pass

        if dataModel in [zone,]:
            try:
                if lookup_params['zone_code']!="":
                    try:
                        zoneidlist=[i for i in lookup_params['zone_code'].split(",")]
                    except:
                        zoneidlist=[1]
                    zoneids=zoneidlist
                    if isContainedChild=="1": #是否包含下级部门
                        zoneids=[]
                        for d in zoneidlist:#支持选择多部门
                            if int(d) not in zoneids:
                                zoneids.append(int(d))
                                zoneids=getAllcodes(d,request,zoneids)
                    lookup_params['id__in']=zoneids
                del lookup_params['zone_code']
            except:
                pass
        if dataModel in [empofdevice,]:
            pinlist=[]
            if 'User_in_Dev' in lookup_params.keys():
                emps=employee.objects.filter(id__in=lookup_params['User_in_Dev'].split(','))
                for emp in emps:
                    pinlist.append(emp.PIN)
                lookup_params['PIN__in']=pinlist
                del lookup_params['User_in_Dev']
        if dataModel==days_off:
            if 'UserID__id__exact' in lookup_params:
                lookup_params['UserID__in']=lookup_params['UserID__id__exact']
                del lookup_params['UserID__id__exact']
            if 'UserID__id__in' in lookup_params:
                lookup_params['UserID__in']=lookup_params['UserID__id__in']
                del lookup_params['UserID__id__in']
            if 'UserID__DeptID__in' in lookup_params:
                lookup_params['DeptID__in']=lookup_params['UserID__DeptID__in']
                del lookup_params['UserID__DeptID__in']
        if dataModel==attShifts and 'Late__gt' in lookup_params and 'Early__gt' in lookup_params:
            del lookup_params['Early__gt']
            del lookup_params['Late__gt']
            #qs = qs.filter(**lookup_params)
            qs = qs.filter(Q(Late__gt=0)|Q(Early__gt=0)|Q(StartTime__isnull=True)|Q(EndTime__isnull=True)|Q(Absent__exact=1))
            qs = qs.exclude(ExceptionID__gt=0)
        elif dataModel==iclock and  ('DeptID__DeptID__in' in lookup_params.keys() or 'DeptID__DeptID__exact' in lookup_params.keys() or 'ZoneID__Iclock__in' in lookup_params.keys() or 'Dining__Iclock__exact' in lookup_params.keys()):
            if 'ZoneID__Iclock__in' in lookup_params.keys():
                zoneidlist=lookup_params['ZoneID__Iclock__in']
                zoneids=zoneidlist
                if isContainedChild=="1": #是否包含下级部门
                    zoneids=[]
                    for d in zoneidlist:#支持选择多部门
                        if d not in zoneids :
                            zoneids.append(d)
                            zoneids+=getAllcodes(d,request,zoneids)
                zoneids=list(set(zoneids))
                rs_SN = IclockZone.objects.filter(zone__in=zoneids).values_list('SN', flat=True)
                del lookup_params['ZoneID__Iclock__in']
                lookup_params['SN__in']=rs_SN
            if 'Dining__Iclock__exact' in lookup_params.keys():
                diningiclock=lookup_params['Dining__Iclock__exact']
                rs_SN = IclockDininghall.objects.filter(dining=diningiclock).values_list('SN', flat=True)
                del lookup_params['Dining__Iclock__exact']
                lookup_params['SN__in']=rs_SN
            elif 'DeptID__DeptID__in' in lookup_params.keys():
                deptidlist=lookup_params['DeptID__DeptID__in']
                dept_list=deptidlist
                if isContainedChild=="1": #是否包含下级部门
                    dept_list=[]
                    for d in deptidlist:#支持选择多部门
                        if int(d) not in dept_list :
                            dept_list+=getAllAuthChildDept(d,request)
                rs_SN = IclockDept.objects.filter(dept__in=dept_list).values_list('SN', flat=True)
                del lookup_params['DeptID__DeptID__in']
                lookup_params['SN__in']=rs_SN
            elif 'DeptID__DeptID__exact' in lookup_params.keys():
                rs_SN=[]
                alldept_flag=False
                dept_list=lookup_params['DeptID__DeptID__exact']
                if isContainedChild=="1": #是否包含下级部门
                    if dept_list=="1":
                        if(request.user.is_superuser) or ( request.user.is_alldept):
                            alldept_flag=True
                    if not alldept_flag:
                        deptids=getAllAuthChildDept(dept_list,request)
                        pids=AllParents(dept_list)
                        objs=IclockDept.objects.filter(dept__in=deptids).exclude(SN__DelTag=1)
                        for l in objs:
                            if l.SN_id not in rs_SN:
                                rs_SN.append(l.SN_id)
                        objs=IclockDept.objects.filter(dept__in=pids).exclude(SN__DelTag=1)
                        for l in objs:
                            if (l.iscascadecheck==1) and l.SN_id not in rs_SN:
                                rs_SN.append(l.SN_id)
                else:
                    rs_SN=getDeviceListByDept(dept_list)
                del lookup_params['DeptID__DeptID__exact']
                if not alldept_flag:
                    lookup_params['SN__in']=rs_SN
            #qs = qs.filter(**lookup_params)
        elif dataModel==employee and ('Finger' in lookup_params.keys()):#判断人员有无指纹
                finObj=BioData.objects.filter(bio_type=bioFinger).values('UserID')
                #finObj=list(set(finObj))
                if lookup_params['Finger']=='1':
                    qs = qs.filter(id__in=finObj)
                else:
                    qs = qs.exclude(id__in=finObj)
                del lookup_params['Finger']
        elif dataModel==employee and ('Face' in lookup_params.keys()):#判断人员有无面部
                finObj=BioData.objects.filter(bio_type=bioFace).values('UserID')
                #finObj=list(set(finObj))
                if lookup_params['Face']=='1':
                    qs = qs.filter(id__in=finObj)
                else:
                    qs = qs.exclude(id__in=finObj)
                del lookup_params['Face']
        elif dataModel==employee and  ('issuecard' in lookup_params.keys()):
                if lookup_params['issuecard']=='0':
                    qs = qs.filter(Q(Card__isnull=True)|Q(Card=''))
                else:
                    qs = qs.exclude(Q(Card__isnull=True)|Q(Card=''))
                if ('cardstatus' in lookup_params.keys()):
                    cardObj=IssueCard.objects.filter(cardstatus = lookup_params['cardstatus']).values('UserID')
                    qs = qs.filter(id__in=cardObj)
                    del lookup_params['cardstatus']
                del lookup_params['issuecard']
                #qs = qs.filter(**lookup_params)
        elif dataModel==employee and ('isvalidcard' in lookup_params.keys()):	#判断人员有效消费卡
                cardObj=IssueCard.objects.filter(cardstatus__in = ['1','4']).values('UserID')#, flat=True)#判断人员有效消费卡
                if lookup_params['isvalidcard']=='1':
                    qs = qs.filter(id__in=cardObj)
                else:
                    qs = qs.exclude(id__in=cardObj)
                del lookup_params['isvalidcard']
                #qs = qs.filter(**lookup_params)





        #elif dataModel==employee and ('Face' in lookup_params.keys()):
        #	faceObj=facetemp.objects.all().values_list('UserID', flat=True)#判断人员有无面部
        #	faceObj=list(set(faceObj))
        #	if lookup_params['Face']=='1':
        #		qs = qs.filter(id__in=faceObj)
        #	else:
        #		qs = qs.exclude(id__in=faceObj)
        #elif dataModel==employee and ('issuecard' in lookup_params.keys()):
        #	if lookup_params['issuecard']=='0':
        #		qs = qs.filter(Q(Card__isnull=True)|Q(Card=''))
        #	else:
        #		qs = qs.exclude(Q(Card__isnull=True)|Q(Card=''))
        #	if ('cardstatus' in lookup_params.keys()):
        #		cardObj=IssueCard.objects.filter(cardstatus = lookup_params['cardstatus']).values('UserID')
        #		qs = qs.filter(id__in=cardObj)
        #		del lookup_params['cardstatus']
        #	del lookup_params['issuecard']
        #	qs = qs.filter(**lookup_params)
        #elif dataModel==employee and ('isvalidcard' in lookup_params.keys()):
        #	cardObj=IssueCard.objects.filter(cardstatus__in = ['1','4']).values('UserID')#, flat=True)#判断人员有效消费卡
        #	if lookup_params['isvalidcard']=='1':
        #		qs = qs.filter(id__in=cardObj)
        #	else:
        #		qs = qs.exclude(id__in=cardObj)
        #	del lookup_params['isvalidcard']
        #	qs = qs.filter(**lookup_params)

        #此处在排班中根据所选的部门和是否包含子部门查出相关的人员信息 2011-01-26 cg
#		elif dataModel==employee and ('DeptID__DeptID__in' in lookup_params.keys()):
#			deptlist=lookup_params['DeptID__DeptID__in']
#			qs=employee.objects.filter(DeptID__in=deptlist)
        elif dataModel==devcmds and ('CmdReturn__exclude' in lookup_params.keys()):
            qs = qs.exclude(CmdReturn=lookup_params['CmdReturn__exclude']).exclude(CmdReturn=None)
            if 'SN' in lookup_params.keys():
                qs=qs.filter(SN=lookup_params['SN'])
        elif dataModel==devcmds and ('CmdReturn__None' in lookup_params.keys()):
            qs = qs.filter(CmdReturn=None)
            if 'SN' in lookup_params.keys():
                qs=qs.filter(SN=lookup_params['SN'])
        elif dataModel==checkexact and ('log' in lookup_params.keys()):
            if 'UserID__DeptID__in' in lookup_params.keys():
                del lookup_params['UserID__DeptID__in']
            if 'log' in lookup_params.keys():
                del lookup_params['log']
            #qs = qs.filter(**lookup_params)
        elif dataModel==USER_OF_RUN:
            if 'startDate' in lookup_params.keys():
                stX=datetime.datetime.strptime(lookup_params['startDate'],'%Y-%m-%d')
                del lookup_params['startDate']
            if 'endDate'  in lookup_params.keys():
                etX=datetime.datetime.strptime(lookup_params['endDate'],'%Y-%m-%d')
                del lookup_params['endDate']
            lookup_params['UserID__OffDuty']=0
            #qs = qs.filter(**lookup_params)
            try:
                qs=qs.exclude(StartDate__gt=etX).exclude(EndDate__lt=stX).exclude(UserID__DelTag=1)
            except:
                pass
        elif dataModel==USER_TEMP_SCH:
            lookup_params['UserID__OffDuty']=0
            qs = qs.exclude(UserID__DelTag=1)
        #else:
            #qs = qs.filter(**lookup_params)
            #print 'params:',lookup_params,' QS:',qs
    #if dataModel==facetemp:
    #	qs = qs.extra(where=['id IN ( SELECT MAX(id) FROM facetemplate GROUP BY userid,AlgVer)'])
    using_m=request.GET.get('mod_name','att')
    if not request.user.is_superuser and using_m in ['acc'] :
        ll={}
        if dataModel in [zone,]:
            zonelist=userZoneList(request.user)
            ll['id__in']=zonelist
        if dataModel in [iclock]:
            zonelist=userZoneList(request.user)
            sn_list=IclockZone.objects.filter(zone__in =zonelist).values_list("SN",flat=True)
            ll['SN__in']=sn_list
        if dataModel in [records]:
            depts=userDeptList(request.user)
            try:
                ll['pin__in']=employee.objects.filter(DeptID__in=depts).exclude(DelTag=1).exclude(OffDuty=1).values_list('PIN',flat=True)
            except:pass
        if dataModel in [employee]:
            depts=userDeptList(request.user)
            ll["DeptID__in"]=depts
        if ll:
            qs=qs.filter(**ll)
    if (not (request.user.is_superuser or request.user.is_alldept)) and using_m in ['att','adms','meeting']:
        if dataModel in [SchClass,]:
            qs=qs.filter(Q(TimeZoneOfDept=0)|Q(TimeZoneOfDept__isnull=True)|Q(TimeZoneOfDept=request.user.AutheTimeDept))
        elif dataModel in [NUM_RUN,]:
            qs=qs.filter(Q(Num_RunOfDept=0)|Q(Num_RunOfDept__isnull=True)|Q(Num_RunOfDept=request.user.AutheTimeDept))
        elif (not request.user.is_alldept):
            ll={}
            if dataModel in [iclock,]:
                if 'DeptID' not in str(request.GET.keys()):
                    sn_list=AuthedIClockList(request.user)
                #if using_m=='acc':
                #	sn_list=IclockZone.objects.filter(zone__in=zoneids).values_list('SN',flat=True)
                    ll['SN__in']=sn_list
            else:
                if request.user.username=='employee':
                    ll['UserID']=request.employee
                elif 'DeptID__in' not in str(lookup_params.keys()):
                    if 'UserID' in dir(dataModel):
                        dept_list=userDeptList(request.user)
                        ll['UserID__DeptID__in']=dept_list
                    elif 'DeptID' in dir(dataModel):
                        dept_list=userDeptList(request.user)
                        ll['DeptID__in']=dept_list
                    elif 'Children' in dir(dataModel):
                        dept_list=userDeptList(request.user)
                        ll['DeptID__in']=dept_list
                    elif dataModel==days_off:
                        dept_list=userDeptList(request.user)
                if  'UserID' not in dir(dataModel) and 'DeptID' not in dir(dataModel) and 'SN' in dir(dataModel):
                    sn_list=AuthedIClockList(request.user)
                    ll['SN__in']=sn_list
                if dataModel in [records]:
                    zcode = ZoneAdmin.objects.filter(user=request.user).values_list('code',flat=True)
                    iz = IclockZone.objects.filter(zone__in=zcode).values_list('SN__SN',flat=True)
                    if ll.has_key('SN__in'):
                        slist = ll['SN__in']
                        slist.extend(iz)
                    else:
                        ll['SN__in'] = iz
            if ll:
                qs = qs.filter(**ll)
    if (not (request.user.is_superuser or request.user.is_alldept)):
        if dataModel in [Group,User]:
            owned=[]
            getOwnedUsers(request.user.id,str(User._meta),owned)
            if dataModel in [Group]:
                grs=UserAdmin.objects.filter(user__in=owned,dataname=str(dataModel._meta))
                owned=set([int(t.owned) for t in grs])
            lll={}
            lll['id__in']=owned
            qs = qs.filter(**lll)
    if dataModel in [User]:
        qs=qs.exclude(username='employee')
    if dataModel in [IssueCard,Allowance,CardCashSZ]:
        if not (request.user.is_superuser or request.user.is_alldept):
            dept_list=userDeptList(request.user)
            qs=qs.filter(UserID__DeptID__in=dept_list)
        #if dataModel==IssueCard:
    #	qs=qs.exclude(cardstatus__in= ['999'])
    if dataModel==ICConsumerList:
        if not (request.user.is_superuser or request.user.is_alldept):
            dept_list=userDeptList(request.user)
            qs=qs.filter(dept__in=dept_list)
    if dataModel in [transactions,iclock]:
        if dataModel==transactions:
            if using_m=='meeting':
                meetid=request.GET.get("transmeetid",0)
                if meetid:
                    userid= Meet_details.objects.filter(MeetID=meetid).values('UserID')
                    qs=qs.filter(UserID__in=userid)
            pType=settings.MOD_DICT[using_m]
            qs=qs.filter(Q(purpose=None)|Q(purpose=pType)|Q(purpose=0))
        elif dataModel==iclock:
            sale=len(settings.SALE_MODULE)
            if 'visitors' in settings.SALE_MODULE:
                sale=sale-1
            if sale>1:
                pType=settings.MOD_DICT[using_m]
                if pType==5:#门禁
                #qs=qs.filter(Q(ProductType=None)|Q(ProductType__in=[pType,pType+1]))
                    qs=qs.filter(ProductType__in=[pType-1,pType,15,25])
                elif pType==3:#消费
                    qs=qs.filter(ProductType__in=[11,12,13,14])#11,12,13为消费机三个子类,14为ID卡消费机
                elif pType==9:
                    qs=qs.filter(Q(ProductType=None)|Q(ProductType=pType)|Q(ProductType=0))
                elif pType==1:#会议
                    qs = qs.filter(Q(ProductType=None) | Q(ProductType__in=[pType,25]))
                else:
                    qs=qs.filter(Q(ProductType=None)|Q(ProductType=pType))
        qs=qs.order_by('SN')
    if dataModel in [level_emp]:
        qs=qs.exclude(UserID__OffDuty=1).exclude(UserID__DelTag=1)
    if dataModel == participants_details:
        qs=qs.order_by('UserID__PIN')
    if dataModel==AntiPassBack:#反潜，通过设备序列号查询
        q=request.GET.get('q')
        if q:
            qs=qs.filter(device__SN=q)
            return qs
    if dataModel==employee_borrow:
        if lookup_params.has_key('UserID__DeptID__in'):
            tmpValue = lookup_params['UserID__DeptID__in']
            del lookup_params['UserID__DeptID__in']
            lookup_params['fromDept__in']=tmpValue
        if lookup_params.has_key('fromDate__lte'):
            tmpValue = lookup_params['fromDate__lte']
            tmpValue += ' 23:59:59'
            lookup_params['fromDate__lte']=tmpValue
    qs = qs.filter(**lookup_params)
    if dataModel==employee_borrow and search:
        ids = employee.objects.filter(Q(Workcode__icontains=search)|Q(EName__icontains=search)|Q(PIN__icontains=search)).values_list('id',flat=True)
        qs = qs.filter(userID__in=ids)
    if dataModel==checkexact:
        filtertag=request.GET.get('filtertag','')
        if filtertag=='4':
            qs=filtercheckexact(request,qs)




    return qs

def filtercheckexact(request,qs):
    from mysite.iclock.datas import GetUserScheduler
    dDict = {}
    for t in qs:
        try:
            dDict[int(t.UserID_id)].append((t.CHECKTIME, t.id))
        except:
            dDict[int(t.UserID_id)] = []
            dDict[int(t.UserID_id)].append((t.CHECKTIME, t.id))
    ids = []
    ab = []
    st = datetime.datetime.strptime(request.GET.get('CHECKTIME__gte'), '%Y-%m-%d') - datetime.timedelta(days=4)
    et = datetime.datetime.strptime(request.GET.get('CHECKTIME__lte'), '%Y-%m-%d') + datetime.timedelta(days=4)
    for k, v in dDict.items():

        tmList = []

        for t in v:
            tmList.append(t[0])
        if len(v) < 5:
            continue
        if (max(tmList) - min(tmList)).days < 4:
            continue
        j = 0
        emp = employee.objByID(k)

        schedules = GetUserScheduler(emp, st, et, False)
        abcd = []
        for sch in schedules:
            dt = sch['TimeZone']['StartTime'].date()
            i = 0
            for tm in v:

                if tm[0].date() == dt:
                    i = 1
                    abcd.append(tm[1])
            if i == 1: j += 1

            if i == 0:
                j = 0
                abcd=[]
            if j > 4:
                ids.append(k)
                ab.extend(abcd)
        j = 0
    qs = qs.filter(id__in=ab)

    return qs


def NoPermissionResponse(title=''):
    return getJSResponse({"ret":0,"message":u"%s" % _("You do not have the permission!")})#render_to_response("info.html", {"title": title, "content": _("You do not have the permission!")});

def GetModel(ModelName,AppName='iclock'):

    if ModelName.lower()=='user':
        dataModel=get_user_model()
        return dataModel

    if ModelName.lower()=='group':
        dataModel=apps.get_model("auth",ModelName)
        return dataModel

    
    #try:
    #    dataModel=models.get_model("iclock",ModelName)
    #except:
    #    dataModel=None
    #if not dataModel:
    #	dataModel=models.get_model("auth",ModelName)
    #return dataModel
    
    try:
        dataModel=apps.get_model(AppName,ModelName)
    except:
        try:
            if not dataModel:
                dataModel=apps.get_model("auth",ModelName)
        except:
            dataModel=None
    return dataModel

def hasPerm(user, model, operation):
    if operation=="toDev" :
        model=GetModel("iclock")
        operation='deptEmptoDev'
    if operation=="delDev" :
        model=GetModel("iclock")
        operation='deptEmptoDelete'

    if operation=="toDevPic" :
        model=GetModel("iclock")
        operation="deptEmptoDelete"
    if  operation=="toDevWithin" :
        model=GetModel("iclock")
        operation="toDevWithin"
    if  operation=="delDevPic" :
        model=GetModel("iclock")
        operation="deptEmptoDelete"
    if  operation=="mvToDev":
        model=GetModel("iclock")
        operation="mvToDev"

    #if operation=='delFingerFromDev' or operation=='delFaceFromDev':
    #	operation="delEmpFromDev"
    #指纹和面部权限合并处理
#	if model.__name__=="facetemp":
##		model=GetModel(ModelName)
    #年假基本规则和年假标准权限合并处理
    if model.__name__=="annual_leave":
        ModelName="annual_settings"
        model=GetModel(ModelName)
    if model.__name__=='forgetcause':
        ModelName="checkexact"
        model=GetModel(ModelName)

    modelName=model.__name__.lower()
    perm='%s.%s_%s'%(model._meta.app_label, operation,modelName)
    if operation in ['Upload_AC_Options','Upload_User_AC_Options','Upload_pos_all_data','Upload_pos_Merchandise','Upload_pos_Meal']:
        perm='%s.%s'%(model._meta.app_label, operation)
    return user.has_perm(perm)

def NoFound404Response(request):
    return getJSResponse({"ret":0,"message":u"%s" % _("Sorry,you have no the permission or the page doesn't exist!")})#render_to_response("404.html",{"url":request.path},RequestContext(request, {}),);

def GetLookup_params(params):

        #过滤
    lookup_params={}
    lookup_params = params.copy() # a dictionary of the query string
    for i in (STAMP_VAR,ALL_VAR, ORDER_VAR, ORDER_TYPE_VAR, SEARCH_VAR, IS_POPUP_VAR, PAGE_VAR, STATE_VAR, EXPORT_VAR,PAGE_LIMIT_VAR,TMP_VAR,Contained,sidx,YEAR_VAR,'exporttblName','rows','exporttype','e','transmeetid','mod_name','show_style'):
        if i in lookup_params:
            del lookup_params[i]
    for key, value in lookup_params.items():
        if not isinstance(key, str):
        # 'key' will be used as a keyword argument later, so Python
        # requires it to be a string.
            del lookup_params[key]
            k=smart_str(key)
            lookup_params[k] = value
        else:
            k=key
        if (k.find("__in")>0) or (k.find("__exact")>0 and value.find(',')>0):
            del lookup_params[key]
            lookup_params[k.replace("__exact","__in")]=value.split(",")
    return lookup_params
