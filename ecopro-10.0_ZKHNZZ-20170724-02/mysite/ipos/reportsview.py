#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.base.models import *
from django.template import  RequestContext 
from django.shortcuts import render_to_response,render
from django.db import models
from django.contrib.auth.models import  Permission
from mysite.iclock.iutils import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.sessions.models import Session
from mysite.iclock.datas import *
import datetime
from django.core.paginator import Paginator
#from mysite.iclock.dataview import *
#from pyExcelerator import *
from mysite.iclock.templatetags.iclock_tags import *
import copy
#from mysite.iclock.datasproc import *
from django.core.cache import cache
from django.contrib.auth.decorators import login_required,permission_required
from mysite.iclock.datautils import GetModel,hasPerm,QueryData
from mysite.iclock.datasproc import *
from mysite.core.menu import *
from mysite.iclock.jqgrid import *
from mysite.iclock.nomodelview import *
from mysite.meeting.datamisc import *
from mysite.ipos.models import *
from math import ceil
from django.db.models import Sum

PAGE_LIMIT_VAR = 'l'


def getMealCaption():
    mealobj = Meal.objects.filter(available=1).exclude(DelTag=1)
    ll=[]
    for t in mealobj:
        ll.append({'name':'meal_%s'%t.id,'sortable':False,'width':80,'label':t.name})
    return ll

def GetGridCaption(rName,request):
    #if request.method=="GET":
    disabledCols=FetchDisabledFields(request.user,rName)
    HeaderNames=[]
    colModel=[]
    if rName=='IssueCard':
        colModel=IssueCard.colModels()

    elif rName=='Supplement':
        colModel=[
            {'name':'user_pin','sortable':False,'width':80,'label':unicode(_(u'工号'))},
            {'name':'user_name','sortable':False,'width':80,'label':unicode(_(u'姓名'))},
            {'name':'DeptName','sortable':False,'width':80,'label':unicode(_(u'部门'))},
            {'name':'card','sortable':False,'width':80,'label':unicode(_(u'卡号'))},
            {'name':'sys_card_no','sortable':False,'width':80,'label':unicode(_(u'卡账号'))},
            {'name':'card_serial_num','sortable':False,'width':80,'label':unicode(_(u'卡流水号'))},
            {'name':'money','sortable':False,'width':80,'label':unicode(_(u'充值金额'))},
            {'name':'hide_column','sortable':False,'width':80,'label':unicode(_(u'充值类型'))},
            {'name':'blance','sortable':False,'width':80,'label':unicode(_(u'卡余额'))},
            {'name':'checktime','sortable':False,'width':120,'label':unicode(_(u'充值时间'))},
            {'name':'convey_time','sortable':False,'width':120,'label':unicode(_(u'上传时间'))},
            {'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))},
            {'name':'serialnum','sortable':False,'width':80,'label':unicode(_(u'设备流水号'))},
            {'name':'sn','sortable':False,'width':80,'label':unicode(_(u'设备序列号'))},
            {'name':'log_flag','sortable':False,'width':80,'label':unicode(_(u'记录类型'))}
        ]
    elif rName=='Refund':
        colModel=[
            {'name':'user_pin','sortable':False,'width':80,'label':unicode(_(u'工号'))},
            {'name':'user_name','sortable':False,'width':80,'label':unicode(_(u'姓名'))},
            {'name':'DeptName','sortable':False,'width':80,'label':unicode(_(u'部门'))},
            {'name':'card','sortable':False,'width':80,'label':unicode(_(u'卡号'))},
            {'name':'sys_card_no','sortable':False,'width':80,'label':unicode(_(u'卡账号'))},
            {'name':'card_serial_num','sortable':False,'width':80,'label':unicode(_(u'卡流水号'))},
            {'name':'money','sortable':False,'width':80,'label':unicode(_(u'退款金额'))},
            {'name':'blance','sortable':False,'width':80,'label':unicode(_(u'卡余额'))},
            {'name':'checktime','sortable':False,'width':120,'label':unicode(_(u'退款时间'))},
            {'name':'convey_time','sortable':False,'width':120,'label':unicode(_(u'上传时间'))},
            {'name':'create_operator','sortable':False,'width':60,'label':unicode(_(u'操作员'))},
            {'name':'serialnum','sortable':False,'width':80,'label':unicode(_(u'设备流水号'))},
            {'name':'sn','sortable':False,'width':80,'label':unicode(_(u'设备序列号'))},
            {'name':'log_flag','sortable':False,'width':80,'label':unicode(_(u'记录类型'))}
        ]
    elif rName=='Backcard':
        colModel = BackCard.colModels()
        # colModel=[
        # 	{'name':'user_pin','sortable':False,'width':80,'label':unicode(_(u'工号'))},
        # 	{'name':'user_name','sortable':False,'width':80,'label':unicode(_(u'姓名'))},
        # 	{'name':'DeptName','sortable':False,'width':80,'label':unicode(_(u'部门'))},
        # 	{'name':'card','sortable':False,'width':80,'label':unicode(_(u'卡号'))},
        # 	{'name':'sys_card_no','sortable':False,'width':80,'label':unicode(_(u'卡账号'))},
        # 	{'name':'card_serial_num','sortable':False,'width':80,'label':unicode(_(u'卡流水号'))},
        # 	{'name':'money','sortable':False,'width':80,'label':unicode(_(u'支出卡成本'))},
        # 	{'name':'back_money','sortable':False,'width':80,'label':unicode(_(u'退款金额'))},
        #
        # 	{'name':'checktime','sortable':False,'width':120,'label':unicode(_(u'退卡时间'))},
        # 	{'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
        # ]
    elif rName=='Cardcost':
        colModel=[
            {'name':'user_pin','sortable':False,'width':80,'label':unicode(_(u'工号'))},
            {'name':'user_name','sortable':False,'width':80,'label':unicode(_(u'姓名'))},
            {'name':'DeptName','sortable':False,'width':80,'label':unicode(_(u'部门'))},
            {'name':'card','sortable':False,'width':80,'label':unicode(_(u'卡号'))},
            {'name':'sys_card_no','sortable':False,'width':80,'label':unicode(_(u'卡账号'))},
            {'name':'money','sortable':False,'width':80,'label':unicode(_(u'成本金额'))},
            {'name':'checktime','sortable':False,'width':120,'label':unicode(_(u'操作时间'))},
            {'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
        ]
    elif rName=='CardBlance':
        colModel=[
            {'name':'user_pin','sortable':False,'width':80,'label':unicode(_(u'工号'))},
            {'name':'user_name','sortable':False,'width':80,'label':unicode(_(u'姓名'))},
            {'name':'DeptName','sortable':False,'width':80,'label':unicode(_(u'部门'))},
            {'name':'card','sortable':False,'width':80,'label':unicode(_(u'卡号'))},
            {'name':'sys_card_no','sortable':False,'width':80,'label':unicode(_(u'卡账号'))},
            {'name':'itype','sortable':False,'width':80,'label':unicode(_(u'卡类名称'))},
            {'name':'blance','sortable':False,'width':80,'label':unicode(_(u'卡余额'))}
            #{'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
        ]
    elif rName=='NoCardBack':
        colModel=[
            {'name':'user_pin','sortable':False,'width':80,'label':unicode(_(u'工号'))},
            {'name':'user_name','sortable':False,'width':80,'label':unicode(_(u'姓名'))},
            {'name':'DeptName','sortable':False,'width':80,'label':unicode(_(u'部门'))},
            {'name':'card','sortable':False,'width':80,'label':unicode(_(u'卡号'))},
            {'name':'sys_card_no','sortable':False,'width':80,'label':unicode(_(u'卡账号'))},
            {'name':'itype','sortable':False,'width':80,'label':unicode(_(u'卡类名称'))},
            {'name':'checktime','sortable':False,'width':120,'label':unicode(_(u'退卡时间'))},
            {'name':'money','sortable':False,'width':80,'label':unicode(_(u'退卡金额'))},
            {'name':'blance','sortable':False,'width':80,'label':unicode(_(u'卡余额'))}
            #{'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
        ]
    elif rName=='IDPosListReport':
        colModel=[
        {'name':'id','hidden':True},
        {'name':'user_pin','width':80,'label':unicode(_(u'工号'))},
        {'name':'user_name','width':80,'label':unicode(_(u'姓名'))},
        {'name':'DeptName','width':80,'label':unicode(_('department name'))},
        {'name':'card','width':80,'label':unicode(_(u"卡号"))},
        {'name':'money','width':80,'label':unicode(_(u"消费金额"))},
        {'name':'blance','width':80,'label':unicode(_(u"余额"))},
        {'name':'pos_model','width':90,'label':unicode(_(u'消费模式'))},
        {'name':'dining','width':80,'label':unicode(_(u"餐厅"))},
        {'name':'meal','width':80,'label':unicode(_(u"餐别"))},
        {'name':'dev_sn','width':120,'label':unicode(_(u"设备序列号"))},
        {'name':'checktime','width':120,'label':unicode(_(u"消费时间"))},
        ]
    elif rName=='ICConsumerList':
        colModel=ICConsumerList.colModels()
    elif rName=='Allowance':
        colModel=Allowance.colModels()
        colModel.insert(8,{'name':'clear_money','sortable':False,'width':80,'label':unicode(_(u"清零金额"))})
    elif rName=='LoseUniteCard':
        colModel=LoseUniteCard.colModels()
    elif rName=='CardManage':
        colModel=CardManage.colModels()
    elif rName=='EmpSumPos':#个人消费汇总表
        colModel=[
            {'name':'pin','sortable':False,'width':80,'label':unicode(_(u'工号'))},
            {'name':'name','sortable':False,'width':80,'label':unicode(_(u'姓名'))},
            {'name':'dept_name','sortable':False,'width':100,'label':unicode(_(u'部门'))},
            {'name':'pos_count','sortable':False,'width':100,'label':unicode(_(u'消费次数合计'))},
            {'name':'add_single_money','sortable':False,'width':80,'label':unicode(_(u'手工补单'))},
            {'name':'meal_money','sortable':False,'width':100,'label':unicode(_(u'消费金额合计'))},
            {'name':'back_count','sortable':False,'width':80,'label':unicode(_(u'纠错次数'))},
            {'name':'back_money','sortable':False,'width':80,'label':unicode(_(u'纠错合计'))},
            {'name':'summary_total_time','sortable':False,'width':80,'label':unicode(_(u'计次次数'))},
            {'name':'summary_count','sortable':False,'width':80,'label':unicode(_(u'结算次数'))},
            {'name':'summary_dev_money','sortable':False,'width':80,'label':unicode(_(u'结算金额'))},
            {'name':'summary_money','sortable':False,'width':120,'label':unicode(_(u'结算金额(含补单)'))},
            {'name':'pos_date','sortable':False,'width':200,'label':unicode(_(u'消费日期'))}
            #{'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
        ]
        mealModel=getMealCaption()
        j=0
        for t in mealModel:
            colModel.insert(6+j,t)
            j+=1

    elif rName=='DeptSumPos':#部门消费汇总表
        colModel=[
            {'name':'dept_name','sortable':False,'width':110,'label':unicode(_(u'部门'))},
            {'name':'pos_count','sortable':False,'width':100,'label':unicode(_(u'消费次数合计'))},
            {'name':'meal_money','sortable':False,'width':100,'label':unicode(_(u'消费金额合计'))},
            {'name':'back_count','sortable':False,'width':80,'label':unicode(_(u'纠错次数'))},
            {'name':'back_money','sortable':False,'width':80,'label':unicode(_(u'纠错合计'))},
            {'name':'summary_total_time','sortable':False,'width':80,'label':unicode(_(u'计次次数'))},
            {'name':'summary_count','sortable':False,'width':80,'label':unicode(_(u'结算次数'))},
            {'name':'summary_money','sortable':False,'width':80,'label':unicode(_(u'结算金额'))},
            {'name':'pos_date','sortable':False,'width':200,'label':unicode(_(u'消费日期'))}
            #{'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
        ]
        mealModel=getMealCaption()
        j=0
        for t in mealModel:
            colModel.insert(6+j,t)
            j+=1



    elif rName=='DiningSumPos':# 餐厅汇总
        colModel=[
            {'name':'dining_name','sortable':False,'width':80,'label':unicode(_(u'餐厅'))},
            {'name':'pos_count','sortable':False,'width':100,'label':unicode(_(u'消费次数合计'))},
            {'name':'meal_money','sortable':False,'width':100,'label':unicode(_(u'消费金额合计'))},
            {'name':'back_count','sortable':False,'width':80,'label':unicode(_(u'纠错次数'))},
            {'name':'back_money','sortable':False,'width':80,'label':unicode(_(u'纠错合计'))},
            {'name':'summary_total_time','sortable':False,'width':80,'label':unicode(_(u'计次次数'))},
            {'name':'add_single_money','sortable':False,'width':80,'label':unicode(_(u'手工补单'))},
            {'name':'summary_count','sortable':False,'width':80,'label':unicode(_(u'结算次数'))},
            {'name':'summary_dev_money','sortable':False,'width':80,'label':unicode(_(u'结算金额'))},
            {'name':'summary_money','sortable':False,'width':120,'label':unicode(_(u'结算金额(含补单)'))},
            {'name':'pos_date','sortable':False,'width':200,'label':unicode(_(u'消费日期'))}
            #{'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
        ]
        mealModel=getMealCaption()
        j=0
        for t in mealModel:
            colModel.insert(6+j,t)
            j+=1


    elif rName=='DeviceSumPos':# 设备汇总
        colModel=[
            {'name':'device_name','sortable':False,'width':80,'label':unicode(_(u'设备'))},
            {'name':'device_sn','sortable':False,'width':80,'label':unicode(_(u'设备序列号'))},
            {'name':'pos_count','sortable':False,'width':100,'label':unicode(_(u'消费次数合计'))},
            {'name':'meal_money','sortable':False,'width':100,'label':unicode(_(u'消费金额合计'))},
            {'name':'back_count','sortable':False,'width':80,'label':unicode(_(u'纠错次数'))},
            {'name':'back_money','sortable':False,'width':80,'label':unicode(_(u'纠错合计'))},
            {'name':'summary_total_time','sortable':False,'width':80,'label':unicode(_(u'计次次数'))},
            {'name':'add_single_money','sortable':False,'width':80,'label':unicode(_(u'手工补单'))},
            {'name':'summary_count','sortable':False,'width':80,'label':unicode(_(u'结算次数'))},
            {'name':'summary_dev_money','sortable':False,'width':80,'label':unicode(_(u'结算金额'))},
            {'name':'summary_money','sortable':False,'width':120,'label':unicode(_(u'结算金额(含补单)'))},
            {'name':'pos_date','sortable':False,'width':200,'label':unicode(_(u'消费日期'))}
            #{'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
        ]

        mealModel=getMealCaption()
        j=0
        for t in mealModel:
            colModel.insert(6+j,t)
            j+=1

    elif rName=='SzSumPos':# 收支汇总
        colModel=[
            {'name':'operate','sortable':False,'width':70,'label':unicode(_(u'统计对象'))},
            {'name':'recharge_count','sortable':False,'width':70,'label':unicode(_(u'充值次数'))},
            {'name':'refund_count','sortable':False,'width':70,'label':unicode(_(u'退款次数'))},
            {'name':'hairpin_count','sortable':False,'width':70,'label':unicode(_(u'发卡次数'))},
            {'name':'back_card_count','sortable':False,'width':70,'label':unicode(_(u'退卡次数'))},

            {'name':'no_card_back','sortable':False,'width':70,'label':unicode(_(u'无卡退卡'))},
            {'name':'card_back','sortable':False,'width':70,'label':unicode(_(u'有卡退卡'))},
            {'name':'clear_card','sortable':False,'width':70,'label':unicode(_(u'清零金额'))},
            {'name':'allow_card','sortable':False,'width':70,'label':unicode(_(u'补贴金额'))},

            {'name':'recharge_money','sortable':False,'width':80,'label':unicode(_(u'充值合计'))},
            {'name':'refund_money','sortable':False,'width':80,'label':unicode(_(u'退款合计'))},
            {'name':'cost_money','sortable':False,'width':80,'label':unicode(_(u'卡成本合计'))},
            {'name':'manage_money','sortable':False,'width':80,'label':unicode(_(u'管理费合计'))},
            {'name':'back_card_money','sortable':False,'width':90,'label':unicode(_(u'退卡成本合计'))},
            {'name':'sz_money','sortable':False,'width':80,'label':unicode(_(u'收支合计'))},
            {'name':'summary_date','sortable':False,'width':200,'label':unicode(_(u'汇总时间'))}
            #{'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
        ]
    elif rName=='MealSumPos':# 餐别汇总
        colModel=[
            {'name':'dining_name','sortable':False,'width':80,'label':unicode(_(u'餐别名称'))},
            {'name':'pos_count','sortable':False,'width':100,'label':unicode(_(u'消费次数合计'))},
            {'name':'meal_money','sortable':False,'width':100,'label':unicode(_(u'消费金额合计'))},
            {'name':'back_count','sortable':False,'width':80,'label':unicode(_(u'纠错次数'))},
            {'name':'back_money','sortable':False,'width':80,'label':unicode(_(u'纠错合计'))},
            {'name':'summary_total_time','sortable':False,'width':80,'label':unicode(_(u'计次次数'))},
            {'name':'add_single_money','sortable':False,'width':80,'label':unicode(_(u'手工补单'))},
            {'name':'summary_count','sortable':False,'width':80,'label':unicode(_(u'结算次数'))},
            {'name':'summary_dev_money','sortable':False,'width':80,'label':unicode(_(u'结算金额'))},
            {'name':'summary_money','sortable':False,'width':120,'label':unicode(_(u'结算金额(含补单)'))},
            {'name':'pos_date','sortable':False,'width':200,'label':unicode(_(u'消费日期'))}
            #{'name':'create_operator','sortable':False,'width':80,'label':unicode(_(u'操作员'))}
        ]


    d={}
    rs="{"+""""disabledcols":"""+dumps(disabledCols)+","+""""colModel":"""+dumps(colModel)+","+""""groupHeaders":"""+dumps(HeaderNames)+"""}"""
    return getJSResponse(rs)

#卡成本报表
def getCardcost(request,userids,q):
    iCount=0
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset=1
    settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
    limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
    sidx=""
    ot=[]
    if request.GET.has_key('sidx'):
        sidx = request.GET.get('sidx','')
    else:
        sidx = request.POST.get('sidx','')
    if sidx:
        ot=sidx.split(',')
    objs=None
    if q!='':
        objs=employee.objects.filter(Q(PIN=q)|Q(EName=q))
    else:
        if userids:
            userids=userids.split(',')
            objs=employee.objects.filter(id__in=userids)

    st=request.GET.get('StartDate','')
    et=request.GET.get('EndDate','')
    st=datetime.datetime.strptime(st,"%Y-%m-%d")
    et=datetime.datetime.strptime(et,"%Y-%m-%d")
    et=et+datetime.timedelta(days=1)
    if objs:
        ts=CardCashSZ.objects.filter(UserID__in=objs,checktime__gte=st,checktime__lt=et,hide_column=7).order_by(*ot)
    else:
        ts=CardCashSZ.objects.filter(checktime__gte=st,checktime__lt=et,hide_column=7).order_by(*ot)

    d_sum=ts.aggregate(Sum('money'))
    sum_money=str(d_sum['money__sum'] or 0)


    p=Paginator(ts, limit,allow_empty_first_page=True)
    iCount=p.count
    if iCount<(offset-1)*limit:
        offset=1
    page_count=p.num_pages
    pp=p.page(offset)
    Result={}
    re=[]
    for t in pp.object_list:
        ll={}

        ll['user_pin']=''
        ll['user_name']=''
        ll['DeptName']=''
        if t.UserID:
            ll['user_pin']=t.UserID.PIN
            ll['user_name']=t.UserID.EName
            if t.UserID.Dept():
                ll['DeptName']=t.UserID.Dept().DeptName
        ll['card']=t.card
        ll['sys_card_no']=t.sys_card_no or ''
        ll['money']=str(t.money)
        ll['checktime']=t.checktime
        ll['create_operator']=t.create_operator or ''
        re.append(ll.copy())
    if 'exporttype' in request.GET:
        d={}
        d['user_pin']=u'总计'
        d['money']=sum_money
        re.append(d.copy())
    userData={'user_pin':u'总计','money':sum_money}

    if offset>page_count:offset=page_count
    item_count =iCount
    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit+1
    Result['page_count']=page_count
    Result['datas']=re
    Result['userData']=userData
    return Result

#退卡报表
def getRetreatCard(request,userids,q):
    iCount = 0
    settings.CARDTYPE = int(GetParamValue('ipos_cardtype', 2, 'ipos'))
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset = 1
    settings.PAGE_LIMIT = GetParamValue('opt_basic_page_limit', '30')
    limit = int(request.POST.get('rows', settings.PAGE_LIMIT))
    sidx = ""
    ot = []
    if request.GET.has_key('sidx'):
        sidx = request.GET.get('sidx', '')
    else:
        sidx = request.POST.get('sidx', '')
    if sidx:
        ot = sidx.split(',')
    objs = None
    if q != '':
        objs = employee.objects.filter(Q(PIN = q) | Q(EName = q))
    else:
        if userids:
            userids = userids.split(',')
            objs = employee.objects.filter(id__in = userids, OffDuty__lt = 1).exclude(DelTag = 1)
    st = request.GET.get('StartDate', '')
    et = request.GET.get('EndDate', '')
    st = datetime.datetime.strptime(st, "%Y-%m-%d")
    et = datetime.datetime.strptime(et, "%Y-%m-%d")
    et = et + datetime.timedelta(days = 1)
    if objs:
        ts = BackCard.objects.filter(UserID__in = objs,checktime__gte=st,checktime__lt=et).order_by(*ot)
    else:
        ts = BackCard.objects.filter(checktime__gte = st, checktime__lt = et).order_by(*ot)
    sum_card_money = ts.aggregate(Sum('card_money'))##退卡成本合计
    sum_card_money = str(sum_card_money['card_money__sum'] or 0)
    sum_back_money = ts.aggregate(Sum('back_money'))##退卡金额合计
    sum_back_money = str(sum_back_money['back_money__sum'] or 0)

    p = Paginator(ts, limit, allow_empty_first_page = True)
    iCount = p.count
    if iCount < (offset - 1) * limit:
        offset = 1
    page_count = p.num_pages
    pp = p.page(offset)
    Result = {}
    re = []
    for t in pp.object_list:
        ll = {}

        ll['user_pin'] = ''
        ll['user_name'] = ''
        ll['DeptName'] = ''
        ll['back_money'] = '0.00'
        ll['money'] = '0.00'

        if t.UserID:
            ll['user_pin'] = t.UserID.PIN
            ll['user_name'] = t.UserID.EName
            if t.UserID.Dept():
                ll['DeptName'] = t.UserID.Dept().DeptName
            ll['cardno'] = t.cardno
            ll['sys_card_no'] = t.sys_card_no
            ll['card_serial_num'] = t.card_serial_num
            ll['back_money'] = str(t.back_money)
            ll['card_money'] = str(t.card_money)
            ll['checktime'] = t.checktime
            ll['create_operator'] = t.create_operator
        re.append(ll.copy())
    if 'exporttype' in request.GET:
        d = {}
        d['user_pin'] = u'总计'
        d['card_money'] = sum_card_money
        d['back_money'] = sum_back_money
        re.append(d.copy())
    userData = {'user_pin':u'总计', 'card_money':(sum_card_money != '0' and sum_card_money or '0.00'),
                'back_money':(sum_back_money != '0' and sum_back_money or '0.00')}
    if offset > page_count:
        offset = page_count
    item_count = iCount
    Result['item_count'] = item_count
    Result['page'] = offset
    Result['limit'] = limit
    Result['from'] = (offset - 1) * limit + 1
    Result['page_count'] = page_count
    Result['datas'] = re
    Result['userData'] = userData
    return Result


# #退卡报表(该函数未使用)
# def getBackcard(request,userids,q):
# 	iCount=0
# 	settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
#
# 	try:
# 		offset = int(request.POST.get('page', 1))
# 	except:
# 		offset=1
# 	settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
# 	limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
# 	sidx=""
# 	ot=[]
# 	if request.GET.has_key('sidx'):
# 		sidx = request.GET.get('sidx','')
# 	else:
# 		sidx = request.POST.get('sidx','')
# 	if sidx:
# 		ot=sidx.split(',')
# 	objs=None
# 	if q!='':
# 		objs=employee.objects.filter(Q(PIN=q)|Q(EName=q))
# 	else:
# 		if userids:
# 			userids=userids.split(',')
# 			objs=employee.objects.filter(id__in=userids,OffDuty__lt=1).exclude(DelTag=1)
#
# 	st=request.GET.get('StartDate','')
# 	et=request.GET.get('EndDate','')
# 	st=datetime.datetime.strptime(st,"%Y-%m-%d")
# 	et=datetime.datetime.strptime(et,"%Y-%m-%d")
# 	et=et+datetime.timedelta(days=1)
# 	if objs:
# 		ts=CardCashSZ.objects.filter(UserID__in=objs,checktime__gte=st,checktime__lt=et,hide_column=15)#,CashType=4)
# 	else:
# 		ts=CardCashSZ.objects.filter(checktime__gte=st,checktime__lt=et,hide_column=15)#CashType=4)
#
# 	#退卡成本合计
# 	money_sum=ts.filter(CashType=4).aggregate(Sum('money'))
# 	sum_money=str(money_sum['money__sum'] or 0)
# 	#退卡金额合计
# 	money_sum=ts.filter(CashType=5).aggregate(Sum('money'))
# 	sum_back_money=str(money_sum['money__sum'] or 0)
#
#
#
#
# 	ts=ts.filter(CashType=5).order_by(*ot)
# 	p=Paginator(ts, limit,allow_empty_first_page=True)
# 	iCount=p.count
# 	if iCount<(offset-1)*limit:
# 		offset=1
# 	page_count=p.num_pages
# 	pp=p.page(offset)
# 	Result={}
# 	re=[]
# 	for t in pp.object_list:
# 		ll={}
#
# 		ll['user_pin']=''
# 		ll['user_name']=''
# 		ll['DeptName']=''
# 		ll['back_money']='0.00'
# 		ll['money']='0.00'
#
# 		if t.UserID:
# 			ll['user_pin']=t.UserID.PIN
# 			ll['user_name']=t.UserID.EName
# 			if t.UserID.Dept():
# 				ll['DeptName']=t.UserID.Dept().DeptName
# 		ll['card']=t.card
# 		ll['sys_card_no']=t.sys_card_no
# 		ll['card_serial_num']=t.cardserial
# 		ll['back_money']=str(t.money)
# 		ll['checktime']=t.checktime
# 		ll['create_operator']=t.create_operator
# 		if settings.CARDTYPE==2:
# 			t_obj=CardCashSZ.objects.filter(UserID=t.UserID,sys_card_no=t.sys_card_no,cardserial=t.cardserial,checktime__gte=st,checktime__lt=et,hide_column=15,CashType=4)
# 		elif settings.CARDTYPE==1:
# 			t_obj=CardCashSZ.objects.filter(UserID=t.UserID,card=t.card,checktime__gte=st,checktime__lt=et,hide_column=15,CashType=4)
# 		if t_obj:
# 			ll['money']=str(t_obj[0].money)
#
#
# 		re.append(ll.copy())
# 	if 'exporttype' in request.GET:
# 		d={}
# 		d['user_pin']=u'总计'
# 		d['money']=sum_money
# 		d['back_money']=sum_back_money
# 		re.append(d.copy())
# 	userData={'user_pin':u'总计','money':(sum_money!='0' and sum_money or '0.00'),'back_money':(sum_back_money!='0' and sum_back_money or '0.00')}
#
# 	if offset>page_count:offset=page_count
# 	item_count =iCount
# 	Result['item_count']=item_count
# 	Result['page']=offset
# 	Result['limit']=limit
# 	Result['from']=(offset-1)*limit+1
# 	Result['page_count']=page_count
# 	Result['datas']=re
# 	Result['userData']=userData
# 	return Result

#退款报表
def getRefund(request,userids,q):
    iCount=0
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset=1
    settings.PAGE_LIMIT=GetParamValue('opt_users_page_limit','50',request.user.id)
    limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
    sidx=""
    ot=[]
    if request.GET.has_key('sidx'):
        sidx = request.GET.get('sidx','')
    else:
        sidx = request.POST.get('sidx','')
    if sidx:
        ot=sidx.split(',')
    objs=None
    if q!='':
        objs=employee.objects.filter(Q(PIN=q)|Q(EName=q))
    else:
        if userids:
            userids=userids.split(',')
            objs=employee.objects.filter(id__in=userids)
    st=request.GET.get('StartDate','')
    et=request.GET.get('EndDate','')
    st=datetime.datetime.strptime(st,"%Y-%m-%d")
    et=datetime.datetime.strptime(et,"%Y-%m-%d")
    et=et+datetime.timedelta(days=1)
    if objs:
        ts=CardCashSZ.objects.filter(UserID__in=objs,checktime__gte=st,checktime__lt=et,CashType=5).order_by(*ot)
    else:
        ts=CardCashSZ.objects.filter(checktime__gte=st,checktime__lt=et,CashType=5).order_by(*ot)
    d_sum=ts.aggregate(Sum('money'))
    sum_money=str(d_sum['money__sum'] or 0)
    p=Paginator(ts, limit,allow_empty_first_page=True)
    iCount=p.count
    if iCount<(offset-1)*limit:
        offset=1
    page_count=p.num_pages
    pp=p.page(offset)
    Result={}
    re=[]
    for t in pp.object_list:
        ll={}
        ll['user_pin']=t.UserID.PIN
        ll['user_name']=t.UserID.EName
        ll['DeptName']=""
        if t.UserID.Dept():
            ll['DeptName']=t.UserID.Dept().DeptName
        ll['card']=t.card
        ll['sys_card_no']=t.sys_card_no
        ll['card_serial_num']=t.cardserial
        ll['money']=str(t.money)
        ll['blance']=str(t.blance)
        ll['checktime']=t.checktime
        ll['convey_time']=t.convey_time or ''
        ll['create_operator']=t.create_operator
        ll['serialnum']=t.serialnum or ''
        ll['sn']=t.sn
        ll['log_flag']=t.get_log_flag_display()
        re.append(ll)
    if 'exporttype' in request.GET:
        d={}
        d['user_pin']=u'总计'
        d['money']=str(sum_money)
        re.append(d.copy())
    userData={'user_pin':u'总计','money':str(sum_money)}

    if offset>page_count:offset=page_count
    item_count =iCount
    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit+1
    Result['page_count']=page_count
    Result['datas']=re
    Result['userData']=userData
    return Result

#ID消费明细报表
def getIDPosListReport(request,userids,q):
    iCount=0
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset=1
    settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
    limit= int(request.POST.get('rows', settings.PAGE_LIMIT))-1
    sidx=""
    ot=[]
    if request.GET.has_key('sidx'):
        sidx = request.GET.get('sidx','')
    else:
        sidx = request.POST.get('sidx','')
    if sidx:
        ot=sidx.split(',')
    objs=None
    if q!='':
        objs=employee.objects.filter(OffDuty__lt=1).filter(Q(PIN=q)|Q(EName=q))
    else:
        if userids:
            userids=userids.split(',')
            objs=employee.objects.filter(id__in=userids,OffDuty__lt=1).exclude(DelTag=1)


    st=request.GET.get('StartDate','')
    et=request.GET.get('EndDate','')
    st=datetime.datetime.strptime(st,"%Y-%m-%d")
    et=datetime.datetime.strptime(et,"%Y-%m-%d")
    et=et+datetime.timedelta(days=1)
    if objs:
        ts=CardCashSZ.objects.filter(UserID__in=objs,checktime__gte=st,checktime__lt=et,pos_model__in=[1,2,3,4,5,6,7,8,9]).order_by(*ot)
    else:
        ts=CardCashSZ.objects.filter(checktime__gte=st,checktime__lt=et,pos_model__in=[1,2,3,4,5,6,7,8,9]).order_by(*ot)
    d_sum=ts.aggregate(Sum('money'))
    sum_money=str(d_sum['money__sum'] or '0.00')
    p=Paginator(ts, limit,allow_empty_first_page=True)
    iCount=p.count
    if iCount<(offset-1)*limit:
        offset=1
    page_count=p.num_pages
    pp=p.page(offset)
    Result={}
    re=[]
    for t in pp.object_list:
        ll={}
        ll['user_pin']=t.UserID.PIN
        ll['user_name']=t.UserID.EName
        ll['DeptName']=""
        if t.UserID.Dept():
            ll['DeptName']=t.UserID.Dept().DeptName
        ll['card']=t.card
        ll['money']=str(t.money)
        ll['blance']=str(t.blance)
        ll['pos_model']=t.get_pos_model_display()
        ll['dining']=str(t.dining or '')
        ll['meal']=(t.meal and str(t.meal)) or ''
        ll['dev_sn']=t.sn
        ll['checktime']=t.checktime
        re.append(ll)
    if 'exporttype' in request.GET:
        d={}
        d['user_pin']=u'总计'
        d['money']=str(sum_money)
        re.append(d.copy())
    userData={'user_pin':u'总计','money':str(sum_money)}
    if offset>page_count:offset=page_count
    item_count =iCount
    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit+1
    Result['page_count']=page_count
    Result['datas']=re
    Result['userData'] = userData
    return Result

#充值报表
def getSupplement(request,userids,q):
    iCount=0
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset=1
    settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','50')
    limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
    sidx=""
    ot=[]
    if request.GET.has_key('sidx'):
        sidx = request.GET.get('sidx','')
    else:
        sidx = request.POST.get('sidx','')
    if sidx:
        ot=sidx.split(',')
    objs=None
    if q!='':
        objs=employee.objects.filter(Q(PIN=q)|Q(EName=q))
    else:
        if userids:
            userids=userids.split(',')
            objs=employee.objects.filter(id__in=userids)


    st=request.GET.get('StartDate','')
    et=request.GET.get('EndDate','')
    st=datetime.datetime.strptime(st,"%Y-%m-%d")
    et=datetime.datetime.strptime(et,"%Y-%m-%d")
    et=et+datetime.timedelta(days=1)
    if objs:
        ts=CardCashSZ.objects.filter(UserID__in=objs,checktime__gte=st,checktime__lt=et,hide_column__in=[1,21,22]).order_by(*ot)
    else:
        ts=CardCashSZ.objects.filter(checktime__gte=st,checktime__lt=et,hide_column__in=[1,21,22]).order_by(*ot)

    d_sum=ts.aggregate(Sum('money'))
    sum_money=str(d_sum['money__sum'] or 0)

    p=Paginator(ts, limit,allow_empty_first_page=True)
    iCount=p.count
    if iCount<(offset-1)*limit:
        offset=1
    page_count=p.num_pages
    pp=p.page(offset)
    Result={}
    re=[]
    for t in pp.object_list:
        ll={}
        ll['user_pin']=t.UserID.PIN
        ll['user_name']=t.UserID.EName
        ll['DeptName']=""
        if t.UserID.Dept():
            ll['DeptName']=t.UserID.Dept().DeptName
        ll['card']=t.card
        ll['sys_card_no']=t.sys_card_no
        ll['card_serial_num']=t.cardserial
        ll['money']=str(t.money)
        ll['hide_column']=t.get_hide_column_display()
        ll['blance']=str(t.blance)
        ll['checktime']=t.checktime
        ll['convey_time']=t.convey_time or ''
        ll['create_operator']=t.create_operator
        ll['serialnum']=t.serialnum or ''
        ll['sn']=t.sn
        ll['log_flag']=t.get_log_flag_display()
        re.append(ll.copy())
    if 'exporttype' in request.GET:
        d={}
        d['user_pin']=u'总计'
        d['money']=str(sum_money)
        re.append(d.copy())
    userData={'user_pin':u'总计','money':str(sum_money)}

    if offset>page_count:offset=page_count
    item_count =iCount
    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit+1
    Result['page_count']=page_count
    Result['datas']=re
    Result['userData']=userData
    return Result

#卡余额报表
def getCardBlance(request,userids,q):
    iCount=0
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset=1
    settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
    limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
    sidx=""
    ot=[]
    if request.GET.has_key('sidx'):
        sidx = request.GET.get('sidx','')
    else:
        sidx = request.POST.get('sidx','')
    if sidx:
        ot=sidx.split(',')
    objs=None
    if q!='':
        objs=employee.objects.filter(Q(PIN=q)|Q(EName=q))

    else:
        if userids:
            userids=userids.split(',')
            objs=employee.objects.filter(id__in=userids)

    if objs:
        ts=IssueCard.objects.filter(UserID__in=objs).order_by(*ot)
    else:
        ts=IssueCard.objects.all().order_by(*ot)
    d_blance=ts.aggregate(Sum('blance'))
    sum_blance=str(d_blance['blance__sum'] or 0)
    p=Paginator(ts, limit,allow_empty_first_page=True)
    iCount=p.count
    if iCount<(offset-1)*limit:
        offset=1
    page_count=p.num_pages
    pp=p.page(offset)
    Result={}
    re=[]
    for t in pp.object_list:
        d={}
        d['user_pin']=''
        d['user_name']=''
        d['DeptName']=''
        if t.UserID:
            d['user_pin']=t.UserID.PIN
            d['user_name']=t.UserID.EName
            if t.UserID.Dept():
                d['DeptName']=t.UserID.Dept().DeptName
        d['card']=t.cardno
        d['sys_card_no']=t.sys_card_no or ''
        d['itype']=t.itype is not None and str(t.itype) or ''
        d['blance']=str(t.blance)
        #ll['create_operator']=''
        re.append(d.copy())
    if 'exporttype' in request.GET:
        d={}
        d['user_pin']=u'总计'
        d['blance']=sum_blance
        re.append(d.copy())
    userData={'user_pin':u'总计','blance':sum_blance}

    if offset>page_count:offset=page_count
    item_count =iCount
    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit+1
    Result['page_count']=page_count
    Result['datas']=re
    Result['userData']=userData
    return Result

#无卡退卡报表
def getNoCardBack(request,userids,q):
    iCount=0
    try:
        offset = int(request.POST.get('page', 1))
    except:
        offset=1
    settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
    limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
    sidx=""
    ot=[]
    if request.GET.has_key('sidx'):
        sidx = request.GET.get('sidx','')
    else:
        sidx = request.POST.get('sidx','')
    if sidx:
        ot=sidx.split(',')
    objs=None
    if q!='':
        objs=employee.objects.filter(Q(PIN=q)|Q(EName=q))
    else:
        if userids:
            userids=userids.split(',')
            objs=employee.objects.filter(id__in=userids)

    st=request.GET.get('StartDate','')
    et=request.GET.get('EndDate','')
    st=datetime.datetime.strptime(st,"%Y-%m-%d")
    et=datetime.datetime.strptime(et,"%Y-%m-%d")
    et=et+datetime.timedelta(days=1)
    if objs:
        ts=CardCashSZ.objects.filter(UserID__in=objs,checktime__gte=st,checktime__lt=et,CashType__in=[4,5],hide_column=14).order_by(*ot)
    else:
        ts=CardCashSZ.objects.filter(checktime__gte=st,checktime__lt=et,CashType__in=[4,5],hide_column=14).order_by(*ot)

    d_sum=ts.aggregate(Sum('money'))
    sum_money=str(d_sum['money__sum'] or 0)



    p=Paginator(ts, limit,allow_empty_first_page=True)
    iCount=p.count
    if iCount<(offset-1)*limit:
        offset=1
    page_count=p.num_pages
    pp=p.page(offset)
    Result={}
    re=[]
    for t in pp.object_list:
        ll={}
        ll['user_pin']=t.UserID.PIN
        ll['user_name']=t.UserID.EName
        ll['DeptName']=""
        if t.UserID.Dept():
            ll['DeptName']=t.UserID.Dept().DeptName
        ll['card']=t.card
        ll['sys_card_no']=t.sys_card_no or ''
        cc=IssueCard.objects.filter(sys_card_no=t.sys_card_no)
        if cc:
            ll['itype']=cc[0].itype.name
        else:
            ll['itype']=''
        ll['blance']=str(t.blance)
        ll['money']=str(t.money)
        ll['checktime']=t.checktime.strftime("%Y-%m-%d %H:%M:%S")
        #ll['create_operator']=''
        re.append(ll.copy())
    if 'exporttype' in request.GET:
        d={}
        d['user_pin']=u'总计'
        d['money']=sum_money
        re.append(d.copy())
    userData={'user_pin':u'总计','money':sum_money}

    if offset>page_count:offset=page_count
    item_count =iCount
    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit+1
    Result['page_count']=page_count
    Result['datas']=re
    Result['userData']=userData
    return Result


#个人消费汇总表 废弃
def getEmpSumPos(request,UserIDs,q):
    offset = int(request.GET.get('page', 1))
    settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
    limit= int(request.GET.get('rows', settings.PAGE_LIMIT))
    sum_back_money = 0
    sum_summary_money = 0
    sum_meal_money = 0
    sum_back_count = 0
    sum_pos_count = 0
    sum_summary_count = 0
    summary_total_time = 0
    summary_total_money = 0
    sum_single_money = 0
    sum_dev_money = 0
    datas=[]
    Result={}
    re=[]
    if q!='':
        if request.user.is_superuser or request.user.is_alldept:
            empids=employee.objects.filter(PIN__startswith='%s'%(q),OffDuty__lt=1).exclude(DelTag=1).values_list('id', flat=True).order_by('id')
        else:
            auth_depts=userDeptList(request.user)
            empids=employee.objects.filter(DeptID__in=auth_depts,PIN__startswith='%s'%(q),OffDuty__lt=1).exclude(DelTag=1).values_list('id', flat=True).order_by('id')
    else:
        if UserIDs:
            userids=UserIDs.split(',')
            empids=employee.objects.filter(id__in=userids).exclude(DelTag=1).values_list('id', flat=True).order_by('id')
        else:
            if request.user.is_superuser or request.user.is_alldept:
                empids=employee.objects.all().exclude(DelTag=1).values_list('id', flat=True).order_by('id')
            else:
                auth_depts=userDeptList(request.user)
                empids=employee.objects.filter(DeptID__in=auth_depts).exclude(DelTag=1).values_list('id', flat=True).order_by('id')

    p=Paginator(empids, limit,allow_empty_first_page=True)
    item_count=p.count
    if item_count<(offset-1)*limit:
        offset=1
    page_count=p.num_pages
    pp=p.page(offset)

    st=request.GET.get('StartDate','')
    et=request.GET.get('EndDate','')
    st=datetime.datetime.strptime(st,"%Y-%m-%d")
    et=datetime.datetime.strptime(et,"%Y-%m-%d")
    et=et+datetime.timedelta(days=0,hours=23,minutes=59,seconds=59)


    if settings.CARDTYPE==2:
        sql = '''
            select
               sum(case when  pos_model=9 then money else 0 end) as back_money,
               sum(case when  pos_model=9 then 1 else 0 end) as back_count,
               sum(case when  type_name=6 then 1 else 0 end) as pos_count,
               sum(case when  type_name in (6,8) then money else 0 end) as summary_money,
               sum(case when  pos_model=4 then 1 else 0 end) as total_count,
               sum(case when  type_name=8 then money else 0 end) as add_single_money %(where)s
            '''
    elif settings.CARDTYPE==1:
        sql = '''
            select
               sum(case when  pos_model=9 then money else 0 end) as back_money,
               sum(case when  pos_model=9 then 1 else 0 end) as back_count,
               sum(case when  hide_column=6 then 1 else 0 end) as pos_count,
               sum(case when  hide_column in (6,8) then money else 0 end) as summary_money,
               sum(case when  pos_model=4 then 1 else 0 end) as total_count,
               sum(case when  hide_column=8 then money else 0 end) as add_single_money %(where)s
            '''
    for t in pp.object_list:
        if settings.CARDTYPE==2:
            sqlstr = sql%({'where':" from ipos_icconsumerlist where  user_id = %s  and pos_time>=%s and pos_time <=%s  group by user_id "})
        elif settings.CARDTYPE==1:
            sqlstr = sql%({'where':" from ipos_cardcashsz where  UserID_id = %s  and checktime>=%s and checktime <=%s  group by UserID_id "})
        params=(t,st,et)
        cs=customSqlEx(sqlstr,params,False)
        row=cs.fetchall()
        d={}
        empss=employee.objects.filter(id=t)
        if empss:
            d['pin'] = empss[0].PIN
            d['name'] = empss[0].EName
            d['dept_name'] =""
            if empss[0].Dept():
                d['dept_name'] =empss[0].Dept().DeptName
        if row:
            back_money = row[0][0] or 0
            back_count = row[0][1] or 0
            pos_count = row[0][2] or 0
            all_money = row[0][3] or 0
            total_count = row[0][4] or 0
            summary_count = pos_count-back_count
            summary_money = all_money - back_money #包含补单金额结算

            d['summary_total_time']=str(total_count)
            single_money = row[0][5] or 0 #手工补消费
            summary_total_time +=total_count
            summary_dev_money = all_money - back_money  - single_money#不包含补单金额结算
            d['pos_date']=st.strftime("%Y-%m-%d")+"---"+et.strftime("%Y-%m-%d")
            d['meal_money']='￥'+ str(all_money)
            d['back_money']='￥'+ str(back_money)
            d['summary_money']='￥'+ str(summary_money)
            d['back_count']=str(back_count)
            d['pos_count']=str(pos_count+total_count)
            d['summary_count']=str(summary_count)
            d['summary_dev_money']='￥'+ str(summary_dev_money)
            d['add_single_money']='￥'+ str(single_money)
            sum_meal_money +=all_money
            sum_back_money +=back_money
            sum_back_count +=back_count
            sum_pos_count +=pos_count+total_count
            sum_summary_count +=summary_count
            sum_summary_money +=summary_money
            sum_single_money +=single_money
            sum_dev_money +=summary_dev_money
        else:
            d['summary_total_time']='0'
            d['pos_date']=st.strftime("%Y-%m-%d")+"---"+et.strftime("%Y-%m-%d")
            d['meal_money']='￥0'
            d['back_money']='￥0'
            d['summary_money']='￥0'
            d['back_count']='0'
            d['pos_count']='0'
            d['summary_count']='0'
            d['summary_dev_money']='￥0'
            d['add_single_money']='￥0'
        re.append(d.copy())

    if 'exporttype' in request.GET:
        d={}
        d['pin']=u'汇总:'
        d['pos_count']=str(sum_pos_count)
        d['meal_money']='￥'+ str(sum_meal_money)
        d['back_count']=str(sum_back_count)
        d['summary_total_time']=str(summary_total_time)
        d['back_money']='￥'+ str(sum_back_money)
        d['summary_money']='￥'+ str(sum_summary_money)
        d['summary_count']=str(sum_summary_count)
        d['summary_dev_money']='￥'+ str(sum_dev_money)
        d['add_single_money']='￥'+ str(sum_single_money)
        d['pos_date']=st.strftime("%Y-%m-%d")+"---"+et.strftime("%Y-%m-%d")
        re.append(d.copy())
    userData={'pin':u'总计','pos_count':str(sum_pos_count),'meal_money':'￥'+ str(sum_meal_money),'back_count':str(sum_back_count),
          'summary_total_time':str(summary_total_time),'back_money':'￥'+ str(sum_back_money),'summary_money':'￥'+ str(sum_summary_money),
          'summary_count':str(sum_summary_count),'summary_dev_money':'￥'+ str(sum_dev_money),
          'add_single_money':'￥'+ str(sum_single_money)}

    #print len(re),"================="
    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit
    Result['page_count']=page_count
    Result['datas']=re
    Result['userData']=userData
    return Result


#部门\餐厅、设备餐别消费汇总表 废弃
def getDept_Ding_Device_SumPos(request,dbname):
    offset = int(request.GET.get('page', 1))
    settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
    limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
    st=request.GET.get('StartDate','')
    et=request.GET.get('EndDate','')
    st=datetime.datetime.strptime(st,"%Y-%m-%d")
    et=datetime.datetime.strptime(et,"%Y-%m-%d")
    et=et+datetime.timedelta(days=0,hours=23,minutes=59,seconds=59)

    sum_back_money = 0
    sum_summary_money = 0
    sum_meal_money = 0
    sum_back_count = 0
    sum_pos_count = 0
    sum_summary_count = 0
    summary_total_time = 0
    summary_total_money = 0
    sum_single_money = 0
    sum_dev_money = 0

    if dbname == 'Dininghall':
        ids=Dininghall.objects.all().exclude(DelTag=1).order_by('id').values_list('id','name')
    elif dbname == 'Device':
        ids = iclock.objects.all().filter(ProductType__in = [11]).exclude(DelTag=1).order_by('SN').values_list('Alias','SN')
    elif dbname == 'dept':
        if request.user.is_superuser or request.user.is_alldept:
            ids=department.objects.all().exclude(DelTag=1).order_by('DeptID').values_list('DeptNumber','DeptName','DeptID')
        else:
            auth_depts=userDeptList(request.user)
            ids=department.objects.filter(DeptID__in=auth_depts).exclude(DelTag=1).order_by('DeptID').values_list('DeptNumber','DeptName','DeptID')
    elif dbname=='Meal':
        ids=list(Meal.objects.all().exclude(DelTag=1).order_by('id').values_list('id','name'))
        ids.append((None,u'其他'))

    p=Paginator(ids, limit,allow_empty_first_page=True)
    item_count=p.count
    if item_count<(offset-1)*limit:
        offset=1
    page_count=p.num_pages
    pp=p.page(offset)
    Result={}
    re=[]
    if settings.CARDTYPE==2:
        sql = '''
            select
            sum(case when  pos_model=9 then money else 0 end) as back_money,
            sum(case when  pos_model=9 then 1 else 0 end) as back_count,
            sum(case when  type_name=6 then 1 else 0 end) as pos_count,
            sum(case when  type_name in (6,8) then money else 0 end) as summary_money,
            sum(case when  pos_model=4 then 1 else 0 end) as total_count,
            sum(case when  type_name=8 then money else 0 end) as add_single_money %(where)s
        '''
    elif settings.CARDTYPE==1:
        sql = '''
            select
            sum(case when  pos_model=9 then money else 0 end) as back_money,
            sum(case when  pos_model=9 then 1 else 0 end) as back_count,
            sum(case when  hide_column=6 then 1 else 0 end) as pos_count,
            sum(case when  hide_column in (6,8) then money else 0 end) as summary_money,
            sum(case when  pos_model=4 then 1 else 0 end) as total_count,
            sum(case when  hide_column=8 then money else 0 end) as add_single_money %(where)s
        '''
    for t in pp.object_list:
        d={}
        if settings.CARDTYPE==2:
            if dbname == 'Dininghall':
                sqlstr = sql%({'where':" from ipos_icconsumerlist where  dining_id = %s and pos_time>=%s and pos_time <%s"})
                params=[t[0],st,et]
            elif dbname == 'Device':
                sqlstr = sql%({'where':" from ipos_icconsumerlist where  dev_sn = %s and pos_time>=%s and pos_time <%s"})
                params=[t[1],st,et]
            elif dbname == 'dept':
                sqlstr = sql%({'where':" from ipos_icconsumerlist where  dept_id = %s and pos_time>=%s and pos_time <%s"})
                params=[t[2],st,et]
            elif dbname == 'Meal':
                if t[0]:
                    sqlstr = sql%({'where':" from ipos_icconsumerlist where  meal_id = %s and pos_time>=%s and pos_time <%s"})
                    params=[t[0],st,et]
                else:
                    sqlstr = sql%({'where':" from ipos_icconsumerlist where  meal_id is Null and pos_time>=%s and pos_time <%s"})
                    params=[st,et]
        elif settings.CARDTYPE==1:
            if dbname == 'Dininghall':
                sqlstr = sql%({'where':" from ipos_cardcashsz where  dining_id = %s and checktime>=%s and checktime <%s"})
                params=[t[0],st,et]
            elif dbname == 'Device':
                sqlstr = sql%({'where':" from ipos_cardcashsz where  sn = %s and checktime>=%s and checktime <%s"})
                params=[t[1],st,et]
            elif dbname == 'dept':
                sqlstr = sql%({'where':" from ipos_cardcashsz where  dept_id = %s and checktime>=%s and checktime <%s"})
                params=[t[2],st,et]
            elif dbname == 'Meal':
                if t[0]:
                    sqlstr = sql%({'where':" from ipos_cardcashsz where  meal_id = %s and checktime>=%s and checktime <%s"})
                    params=[t[0],st,et]
                else:
                    sqlstr = sql%({'where':" from ipos_cardcashsz where  meal_id is Null and checktime>=%s and checktime <%s"})
                    params=[st,et]

        cs=customSqlEx(sqlstr,params,False)
        row=cs.fetchall()
        if row:
            back_money = row[0][0] or 0
            back_count = row[0][1] or 0
            pos_count = row[0][2] or 0
            all_money = row[0][3] or 0
            total_count = row[0][4] or 0
            single_money = row[0][5] or 0 #手工补单
            summary_count = pos_count-back_count
            summary_money = all_money - back_money #设备消费结算金额
            summary_dev_money = all_money - back_money  - single_money#不包含补单金额结算
            d['summary_total_time']=str(total_count)
            summary_total_time +=total_count
            d['pos_date']=st.strftime("%Y-%m-%d")+"---"+et.strftime("%Y-%m-%d")
            if dbname == 'Dininghall':
                d['dining_name']=t[1]
            elif dbname == 'Device':
                d['device_name']=t[0]
                d['device_sn']=t[1]
            elif dbname=='dept':
                d['dept_name']=t[1]
            elif dbname=='Meal':
                d['dining_name']=t[1]
        #            r['breakfast_money']=str(breakfast_money)
        #            r['lunch_money']=str(lunch_money)
        #            r['dinner_money']=str(dinner_money)
        #            r['supper_money']=str(supper_money)
            d['meal_money']='￥'+ str(all_money)
            d['back_money']='￥'+ str(back_money)
            d['summary_money']='￥'+ str(summary_money)
            d['back_count']=str(back_count)
            d['pos_count']=str(pos_count+total_count)
            d['summary_count']=str(summary_count)
            if dbname in ['Dininghall','Device']:
                d['summary_dev_money']='￥'+ str(summary_dev_money)
                d['add_single_money']='￥'+ str(single_money)
        #            sum_breakfast_money +=breakfast_money
        #            sum_lunch_money +=lunch_money
        #            sum_dinner_money +=dinner_money
        #            sum_supper_money +=supper_money
            sum_meal_money +=all_money
            sum_back_money +=back_money
            sum_back_count +=back_count
            sum_pos_count +=pos_count+total_count
            sum_summary_count +=summary_count
            sum_summary_money +=summary_money
            sum_single_money +=single_money
            sum_dev_money +=summary_dev_money
            re.append(d.copy())


    d={}
    if dbname == 'Dininghall':
        d['dining_name']=u'汇总:'
    elif dbname == 'Device':
        d['device_name']=u'汇总:'
    elif dbname=='dept':
        d['dept_name']=u'汇总:'
    elif dbname=='Meal':
        d['dining_name']=u'汇总:'

    d['pos_date']=st.strftime("%Y-%m-%d")+"---"+et.strftime("%Y-%m-%d")

    d['meal_money']='￥'+ str(sum_meal_money)
    d['back_money']='￥'+ str(sum_back_money)
    d['summary_money']='￥'+ str(sum_summary_money)
    d['back_count']=str(sum_back_count)
    d['pos_count']=str(sum_pos_count)
    d['summary_count']=str(sum_summary_count)
    re.append(d.copy())

    #userdata={'dept_name':'aaaa'}
    Result['item_count']=item_count+1
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit+1
    Result['page_count']=page_count
    Result['datas']=re
    #Result['userdata']=userdata
    return Result



#个人消费汇总表   不再处理授权部门，不管离职，不含未消费的人员
def getEmpSumPos_Ex(request,UserIDs,q):
    offset = int(request.GET.get('page', 1))
    settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
    limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
    sum_back_money = 0
    sum_summary_money = 0
    sum_meal_money = 0
    sum_back_count = 0
    sum_pos_count = 0
    sum_summary_count = 0
    summary_total_time = 0
    summary_total_money = 0
    sum_single_money = 0
    sum_dev_money = 0
    datas=[]
    Result={}
    re=[]
    item_count=0
    userids=UserIDs
    if q!='':
        empids=employee.objects.filter(PIN__startswith='%s'%(q)).exclude(DelTag=1).values_list('id', flat=True).order_by('id')

        userids=','.join([str(i) for i in empids])



    #p=Paginator(empids, limit,allow_empty_first_page=True)
    #item_count=p.count
    #if item_count<(offset-1)*limit:
    #	offset=1
    #page_count=p.num_pages
    #pp=p.page(offset)

    st=request.GET.get('StartDate','')
    et=request.GET.get('EndDate','')
    st=datetime.datetime.strptime(st,"%Y-%m-%d")
    et=datetime.datetime.strptime(et,"%Y-%m-%d")
    et=et+datetime.timedelta(days=1)
    mealobj = Meal.objects.filter(available=1).exclude(DelTag=1)


    if settings.CARDTYPE==2:
        sql = '''
            select user_id as id,
               sum(case when  pos_model=9 then money else 0 end) as back_money,
               sum(case when  pos_model=9 then 1 else 0 end) as back_count,
               sum(case when  type_name=6 then 1 else 0 end) as pos_count,
               sum(case when  type_name in (6,8) then money else 0 end) as summary_money,
               sum(case when  pos_model=4 then 1 else 0 end) as total_count,
               sum(case when  type_name=8 then money else 0 end) as add_single_money
               '''
    elif settings.CARDTYPE==1:
        sql = '''
            select userid_id as id,
               sum(case when  pos_model=9 then money else 0 end) as back_money,
               sum(case when  pos_model=9 then 1 else 0 end) as back_count,
               sum(case when  hide_column=6 then 1 else 0 end) as pos_count,
               sum(case when  hide_column in (6,8) then money else 0 end) as summary_money,
               sum(case when  pos_model=4 then 1 else 0 end) as total_count,
               sum(case when  hide_column=8 then money else 0 end) as add_single_money
            '''
    meal_sum={}
    if mealobj:
        meal_sql=''' ,sum(case when  meal_id=%s then money else 0 end) as meal_%s,sum(case when  pos_model=9 and meal_id=%s then money else 0 end) as back_meal_%s'''#扣除纠错金额
        for t in mealobj:
            sql=sql+meal_sql%(t.id,t.id,t.id,t.id)
            meal_sum['meal_%s'%t.id]=0
    sql=sql+''' %(where)s'''
    if settings.CARDTYPE==2:
        sqlstr = sql%({'where':" from ipos_icconsumerlist where   pos_time>=%s and pos_time <%s  "})
        if userids:
            sqlstr=sqlstr+' and user_id in (%s)'%(userids)
        sqlstr=sqlstr+' group by user_id'

    elif settings.CARDTYPE==1:
        sqlstr = sql%({'where':" from ipos_cardcashsz where   checktime>=%s and checktime <%s   "})
        if userids:
            sqlstr=sqlstr+' and UserID_id in (%s)'%(userids)

        sqlstr=sqlstr+' group by userid_id'
    params=(st,et)
    cs=customSqlEx(sqlstr,params,False)
    desc=cs.description
    fldNames={}
    i=0
    for c in desc:
        fldNames[c[0].lower()]=i
        i=i+1

    rows=cs.fetchall()
    for t in rows:
        d={}
        item_count+=1
        back_money = t[fldNames['back_money']] or 0
        back_count = t[fldNames['back_count']] or 0
        pos_count = t[fldNames['pos_count']] or 0
        all_money = t[fldNames['summary_money']] or 0
        total_count = t[fldNames['total_count']] or 0
        summary_count = pos_count-back_count
        summary_money = all_money - back_money #包含补单金额结算

        d['summary_total_time']=str(total_count)
        single_money = t[fldNames['add_single_money']] or 0 #手工补消费
        summary_total_time +=total_count
        summary_dev_money = all_money - back_money  - single_money#不包含补单金额结算
        for tt in meal_sum.keys():
            back_x=t[fldNames['back_'+tt]] or 0
            x=(t[fldNames[tt]] or 0)-back_x
            d[tt]= '￥'+(x and str(x) or '0.00')
            meal_sum[tt]+=x

        d['pos_date']=st.strftime("%Y-%m-%d")+"---"+(et+datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
        d['meal_money']='￥'+ (all_money and str(all_money) or '0.00')
        d['back_money']='￥'+ (back_money and str(back_money) or '0.00')
        d['summary_money']='￥'+ (summary_money and str(summary_money) or '0.00')
        d['back_count']=str(back_count)
        d['pos_count']=str(pos_count+total_count)
        d['summary_count']=str(summary_count)
        d['summary_dev_money']='￥'+ (summary_dev_money and str(summary_dev_money) or '0.00')
        d['add_single_money']='￥'+ (single_money and str(single_money) or '0.00')
        sum_meal_money +=all_money
        sum_back_money +=back_money
        sum_back_count +=back_count
        sum_pos_count +=pos_count+total_count
        sum_summary_count +=summary_count
        sum_summary_money +=summary_money
        sum_single_money +=single_money
        sum_dev_money +=summary_dev_money

        if item_count>(offset-1)*limit and item_count<=offset*limit:
            id=t[fldNames['id']]
            emp=employee.objByID(id)
            if emp:
                d['pin'] = emp.PIN
                d['name'] = emp.EName
                d['dept_name'] =""
                if emp.Dept():
                    d['dept_name'] =emp.Dept().DeptName
            re.append(d.copy())

    if 'exporttype' in request.GET:
        d={}
        d['pin']=u'总计'
        d['pos_count']=str(sum_pos_count)
        d['meal_money']='￥'+ (sum_meal_money and str(sum_meal_money) or '0.00')
        d['back_count']=str(sum_back_count)
        d['summary_total_time']=str(summary_total_time)
        d['back_money']='￥'+ (sum_back_money and str(sum_back_money) or '0.00')
        d['summary_money']='￥'+ (sum_summary_money and str(sum_summary_money) or '0.00')
        d['summary_count']=str(sum_summary_count)
        d['summary_dev_money']='￥'+ (sum_dev_money and str(sum_dev_money) or '0.00')
        d['add_single_money']='￥'+ (sum_single_money and str(sum_single_money) or '0.00')
        d['pos_date']=st.strftime("%Y-%m-%d")+"---"+(et+datetime.timedelta(days=-1)).strftime("%Y-%m-%d")


        for tt in meal_sum.keys():
            x=meal_sum[tt]
            d[tt]= '￥'+(x and str(x) or '0.00')


        re.append(d.copy())


    userData={'pin':u'总计','pos_count':str(sum_pos_count),'meal_money':'￥'+ (sum_meal_money and str(sum_meal_money) or '0.00'),'back_count':str(sum_back_count),
          'summary_total_time':str(summary_total_time),'back_money':'￥'+ (sum_back_money and str(sum_back_money) or '0.00'),'summary_money':'￥'+ (sum_summary_money and str(sum_summary_money) or '0.00'),
          'summary_count':str(sum_summary_count),'summary_dev_money':'￥'+ (sum_dev_money and str(sum_dev_money) or '0.00'),
          'add_single_money':'￥'+ (sum_single_money and str(sum_single_money) or '0.00'),'pos_date':st.strftime("%Y-%m-%d")+"---"+(et+datetime.timedelta(days=-1)).strftime("%Y-%m-%d")}
    for tt in meal_sum.keys():
        x=meal_sum[tt]
        userData[tt]= '￥'+(x and str(x) or '0.00')

    page_count =int(ceil(item_count/float(limit)))
    if page_count and offset>page_count:offset=page_count


    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit
    Result['page_count']=page_count
    Result['datas']=re
    Result['userData']=userData
    return Result


#部门\餐厅、设备餐别消费汇总表 增加餐别的汇总
def getDept_Ding_Device_SumPos_Ex(request,dbname):
    offset = int(request.GET.get('page', 1))
    settings.PAGE_LIMIT=GetParamValue('opt_basic_page_limit','30')
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
    limit= int(request.POST.get('rows', settings.PAGE_LIMIT))
    st=request.GET.get('StartDate','')
    et=request.GET.get('EndDate','')
    st=datetime.datetime.strptime(st,"%Y-%m-%d")
    et=datetime.datetime.strptime(et,"%Y-%m-%d")
    et=et+datetime.timedelta(days=1)

    sum_back_money = 0
    sum_summary_money = 0
    sum_meal_money = 0
    sum_back_count = 0
    sum_pos_count = 0
    sum_summary_count = 0
    summary_total_time = 0
    summary_total_money = 0
    sum_single_money = 0
    sum_dev_money = 0
    mealobj = Meal.objects.filter(available=1).exclude(DelTag=1)

    if dbname == 'Dininghall':
        ids=Dininghall.objects.all().exclude(DelTag=1).order_by('id').values_list('id','name')
    elif dbname == 'Device':
        ids = iclock.objects.all().filter(ProductType__in = [11]).exclude(DelTag=1).order_by('SN').values_list('Alias','SN')
    elif dbname == 'dept':
        if request.user.is_superuser or request.user.is_alldept:
            ids=department.objects.all().exclude(DelTag=1).order_by('DeptID').values_list('DeptNumber','DeptName','DeptID')
        else:
            auth_depts=userDeptList(request.user)
            ids=department.objects.filter(DeptID__in=auth_depts).exclude(DelTag=1).order_by('DeptID').values_list('DeptNumber','DeptName','DeptID')
    elif dbname=='Meal':
        ids=list(Meal.objects.all().exclude(DelTag=1).order_by('id').values_list('id','name'))
        ids.append((None,u'其他'))

    Result={}
    re=[]
    item_count=0
    if settings.CARDTYPE==2:
        sql = '''
            select
            sum(case when  pos_model=9 then money else 0 end) as back_money,
            sum(case when  pos_model=9 then 1 else 0 end) as back_count,
            sum(case when  type_name=6 then 1 else 0 end) as pos_count,
            sum(case when  type_name in (6,8) then money else 0 end) as summary_money,
            sum(case when  pos_model=4 then 1 else 0 end) as total_count,
            sum(case when  type_name=8 then money else 0 end) as add_single_money
        '''
    elif settings.CARDTYPE==1:
        sql = '''
            select
            sum(case when  pos_model=9 then money else 0 end) as back_money,
            sum(case when  pos_model=9 then 1 else 0 end) as back_count,
            sum(case when  hide_column=6 then 1 else 0 end) as pos_count,
            sum(case when  hide_column in (6,8) then money else 0 end) as summary_money,
            sum(case when  pos_model=4 then 1 else 0 end) as total_count,
            sum(case when  hide_column=8 then money else 0 end) as add_single_money
        '''


    meal_sum={}
    if mealobj:
        meal_sql=''' ,sum(case when  meal_id=%s then money else 0 end) as meal_%s'''
        for t in mealobj:
            sql=sql+meal_sql%(t.id,t.id)
            meal_sum['meal_%s'%t.id]=0
    sql=sql+''' %(where)s'''



    for t in ids:
        d={}
        if settings.CARDTYPE==2:
            if dbname == 'Dininghall':
                sqlstr = sql%({'where':" from ipos_icconsumerlist where  dining_id = %s and pos_time>=%s and pos_time <%s"})
                params=[t[0],st,et]
            elif dbname == 'Device':
                sqlstr = sql%({'where':" from ipos_icconsumerlist where  dev_sn = %s and pos_time>=%s and pos_time <%s"})
                params=[t[1],st,et]
            elif dbname == 'dept':
                sqlstr = sql%({'where':" from ipos_icconsumerlist where  dept_id = %s and pos_time>=%s and pos_time <%s"})
                params=[t[2],st,et]
            elif dbname == 'Meal':
                if t[0]:
                    sqlstr = sql%({'where':" from ipos_icconsumerlist where  meal_id = %s and pos_time>=%s and pos_time <%s"})
                    params=[t[0],st,et]
                else:
                    sqlstr = sql%({'where':" from ipos_icconsumerlist where  meal_id is Null and pos_time>=%s and pos_time <%s"})
                    params=[st,et]
        elif settings.CARDTYPE==1:
            if dbname == 'Dininghall':
                sqlstr = sql%({'where':" from ipos_cardcashsz where  dining_id = %s and checktime>=%s and checktime <%s"})
                params=[t[0],st,et]
            elif dbname == 'Device':
                sqlstr = sql%({'where':" from ipos_cardcashsz where  sn = %s and checktime>=%s and checktime <%s"})
                params=[t[1],st,et]
            elif dbname == 'dept':
                sqlstr = sql%({'where':" from ipos_cardcashsz where  dept_id = %s and checktime>=%s and checktime <%s"})
                params=[t[2],st,et]
            elif dbname == 'Meal':
                if t[0]:
                    sqlstr = sql%({'where':" from ipos_cardcashsz where  meal_id = %s and checktime>=%s and checktime <%s"})
                    params=[t[0],st,et]
                else:
                    sqlstr = sql%({'where':" from ipos_cardcashsz where  meal_id is Null and checktime>=%s and checktime <%s"})
                    params=[st,et]

        cs=customSqlEx(sqlstr,params,False)
        desc=cs.description
        fldNames={}
        i=0
        for c in desc:
            fldNames[c[0].lower()]=i
            i=i+1



        row=cs.fetchall()
        if row:
            item_count+=1
            back_money = row[0][fldNames['back_money']] or 0
            back_count = row[0][fldNames['back_count']] or 0
            pos_count = row[0][fldNames['pos_count']] or 0
            all_money = row[0][fldNames['summary_money']] or 0
            total_count = row[0][fldNames['total_count']] or 0
            single_money = row[0][fldNames['add_single_money']] or 0 #手工补单
            summary_count = pos_count-back_count
            summary_money = all_money - back_money #设备消费结算金额
            summary_dev_money = all_money - back_money  - single_money#不包含补单金额结算
            d['summary_total_time']=str(total_count)
            summary_total_time +=total_count
            d['pos_date']=st.strftime("%Y-%m-%d")+"---"+(et+datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
            if dbname == 'Dininghall':
                d['dining_name']=t[1]
            elif dbname == 'Device':
                d['device_name']=t[0]
                d['device_sn']=t[1]
            elif dbname=='dept':
                d['dept_name']=t[1]
            elif dbname=='Meal':
                d['dining_name']=t[1]
        #            r['breakfast_money']=str(breakfast_money)
        #            r['lunch_money']=str(lunch_money)
        #            r['dinner_money']=str(dinner_money)
        #            r['supper_money']=str(supper_money)
            d['meal_money']='￥'+ (all_money and str(all_money) or '0.00')
            d['back_money']='￥'+ (back_money and str(back_money) or '0.00')
            d['summary_money']='￥'+ (summary_money and str(summary_money) or '0.00')
            d['back_count']=str(back_count)
            d['pos_count']=str(pos_count+total_count)
            d['summary_count']=str(summary_count)
            if dbname in ['Dininghall','Device','Meal']:
                d['summary_dev_money']='￥'+ (summary_dev_money and str(summary_dev_money) or '0.00')
                d['add_single_money']='￥'+ (single_money and str(single_money) or '0.00')
        #            sum_breakfast_money +=breakfast_money
        #            sum_lunch_money +=lunch_money
        #            sum_dinner_money +=dinner_money
        #            sum_supper_money +=supper_money
            sum_meal_money +=all_money
            sum_back_money +=back_money
            sum_back_count +=back_count
            sum_pos_count +=pos_count+total_count
            sum_summary_count +=summary_count
            sum_summary_money +=summary_money
            sum_single_money +=single_money
            sum_dev_money +=summary_dev_money
            for tt in meal_sum.keys():
                x=row[0][fldNames[tt]] or 0
                d[tt]= '￥'+(x and str(x) or '0.00')
                meal_sum[tt]+=x

            if item_count>(offset-1)*limit and item_count<=offset*limit:
                re.append(d.copy())


    d={}
    if dbname == 'Dininghall':
        d['dining_name']=u'总计'
        d['summary_dev_money']='￥'+ (sum_dev_money and str(sum_dev_money) or '0.00')
        d['add_single_money']='￥'+(sum_single_money and str(sum_single_money) or '0.00')
    elif dbname == 'Device':
        d['device_name']=u'总计'
        d['summary_dev_money']='￥'+ (sum_dev_money and str(sum_dev_money) or '0.00')
        d['add_single_money']='￥'+(sum_single_money and str(sum_single_money) or '0.00')
    elif dbname=='dept':
        d['dept_name']=u'总计'
    elif dbname=='Meal':
        d['dining_name']=u'总计'
        d['summary_dev_money']='￥'+ (sum_dev_money and str(sum_dev_money) or '0.00')
        d['add_single_money']='￥'+(sum_single_money and str(sum_single_money) or '0.00')

    d['pos_date']=st.strftime("%Y-%m-%d")+"---"+(et+datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    d['summary_total_time']=str(summary_total_time)
    d['meal_money']='￥'+ (sum_meal_money and str(sum_meal_money) or '0.00')
    d['back_money']='￥'+ (sum_back_money and str(sum_back_money) or '0.00')
    d['summary_money']='￥'+ (sum_summary_money and str(sum_summary_money) or '0.00')
    d['back_count']=str(sum_back_count)
    d['pos_count']=str(sum_pos_count)
    d['summary_count']=str(sum_summary_count)
    for tt in meal_sum.keys():
        x=meal_sum[tt]
        d[tt]= '￥'+(x and str(x) or '0.00')

    if 'exporttype'  in request.GET:
        re.append(d.copy())

    page_count =int(ceil(item_count/float(limit)))
    if page_count and offset>page_count:offset=page_count
    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit
    Result['page_count']=page_count
    Result['datas']=re
    Result['userData']=d
    #Result['userdata']=userdata
    return Result





#收支汇总表
def SZ_sum_report(request):
    offset = int(request.GET.get('page', 1))
    limit= int(request.GET.get('rows', 30))
    st=request.GET.get('StartDate','')
    et=request.GET.get('EndDate','')
    st=datetime.datetime.strptime(st,"%Y-%m-%d")
    et=datetime.datetime.strptime(et,"%Y-%m-%d")
    et=et+datetime.timedelta(days=0,hours=23,minutes=59,seconds=59)
    check_opreate= request.GET.get('check_opreate', '')
    dev = iclock.objects.filter(ProductType__in=[11,12,13])
    sum_recharge_money = 0
    sum_recharge_count = 0
    sum_refund_money = 0
    sum_refund_count = 0
    sum_cost_money = 0
    sum_manage_money = 0
    sum_hairpin_count = 0
    sum_back_card_count = 0
    sum_back_card_money = 0
    sum_sz_money = 0

    sum_no_card_back=0
    sum_card_back=0
    sum_clear_card=0
    sum_allow_card=0

    operate_list = []

    Result={}
    re=[]

    sql = '''
        select
        sum(case when  cashtype_id=1 then money else 0 end) as recharge_money,
        sum(case when  cashtype_id=1 then 1 else 0 end) as recharge_count,
        sum(case when  cashtype_id=5 then money else 0 end) as refund_money,
        sum(case when  cashtype_id=5 then 1 else 0 end) as refund_count,
        sum(case when  cashtype_id=7 then money else 0 end) as cost_money,
        sum(case when  cashtype_id=11 then money else 0 end) as manage_money,
        sum(case when  cashtype_id=7 then 1 else 0 end) as hairpin_count,
        sum(case when  cashtype_id=4 then 1 else 0 end) as back_card_count,
        sum(case when  cashtype_id=4 then money else 0 end) as back_card_money,
    sum(case when  cashtype_id=5 and hide_column=14  then money else 0 end) as no_card_back,
    sum(case when  cashtype_id=5 and hide_column=15  then money else 0 end) as card_back,
    sum(case when  cashtype_id=2 and allow_type=1  then money else 0 end) as clear_back,
    sum(case when  cashtype_id=2 and allow_type=0  then money else 0 end) as allow_card
        
        %(where)s   
    '''

    if check_opreate == 'checked':
        sql_db = sql%({'where':" ,create_operator from ipos_CardCashSZ where  checktime>=%s and checktime <%s and  create_operator !='0' group by create_operator"})
        union_sql='''
        union all 
        select 
                sum(case when  cashtype_id=1 then money else 0 end) as recharge_money,
                sum(case when  cashtype_id=1 then 1 else 0 end) as recharge_count,
                sum(case when  cashtype_id=5 then money else 0 end) as refund_money,
                sum(case when  cashtype_id=5 then 1 else 0 end) as refund_count,
                sum(case when  cashtype_id=7 then money else 0 end) as cost_money,
                sum(case when  cashtype_id=11 then money else 0 end) as manage_money,
                sum(case when  cashtype_id=7 then 1 else 0 end) as hairpin_count,
                sum(case when  cashtype_id=4 then 1 else 0 end) as back_card_count,
                sum(case when  cashtype_id=4 then money else 0 end) as back_card_money,
    sum(case when  cashtype_id=5 and hide_column=14  then money else 0 end) as no_card_back,
    sum(case when  cashtype_id=5 and hide_column=15  then money else 0 end) as card_back,
    sum(case when  cashtype_id=2 and allow_type=1  then money else 0 end) as clear_back,
    sum(case when  cashtype_id=2 and allow_type=0  then money else 0 end) as allow_card,

                sn
        from ipos_cardcashsz where  checktime>=%s and checktime <%s and create_operator='0' group by sn
        '''
        sqlstr = sql_db + union_sql
        params=[st,et,st,et]
    else:
        sqlstr = sql%({'where':" from ipos_cardcashsz where  checktime>=%s and checktime <%s"})
        params=[st,et]
    try:
        cs=customSqlEx(sqlstr,params,False)
    except Exception,e:
        print "------------------",e
        pass
        #{'name':'no_card_back','sortable':False,'width':70,'label':unicode(_(u'无卡退卡'))},
            #{'name':'back_card','sortable':False,'width':70,'label':unicode(_(u'有卡退卡'))},
            #{'name':'clear_card','sortable':False,'width':70,'label':unicode(_(u'清零金额'))},
            #{'name':'allow_card','sortable':False,'width':70,'label':unicode(_(u'补贴金额'))},
            #

    rows=cs.fetchall()
    for row in rows:
        d={}
        recharge_money = row[0] or 0
        recharge_count = row[1] or 0
        refund_money = row[2] or 0
        refund_count = row[3] or 0
        cost_money = row[4] or 0
        manage_money = row[5] or 0
        hairpin_count = row[6] or 0
        back_card_count = row[7] or 0
        back_card_money = row[8] or 0
        no_card_back=row[9] or 0
        card_back=row[10] or 0
        clear_card=row[11] or 0
        allow_card=row[12] or 0



        sz_money = recharge_money - refund_money + cost_money + manage_money - back_card_money
        d['summary_date']=st.strftime("%Y-%m-%d")+"---"+et.strftime("%Y-%m-%d")
        d['recharge_money']='￥'+ (recharge_money and str(recharge_money) or '0.00')
        d['recharge_count']=str(recharge_count)
        d['refund_money']='￥'+ (refund_money and str(refund_money) or '0.00')
        d['refund_count']=str(refund_count)
        d['cost_money']='￥'+ (cost_money and str(cost_money) or '0.00')
        d['manage_money']='￥'+ (manage_money and str(manage_money) or '0.00')
        d['hairpin_count']=str(hairpin_count)
        d['back_card_count']=str(back_card_count)
        d['back_card_money']='￥'+ (back_card_money and str(back_card_money) or '0.00')
        d['no_card_back']='￥'+ (no_card_back and str(no_card_back) or '0.00')
        d['card_back']='￥'+ (card_back and str(card_back) or '0.00')
        d['clear_card']='￥'+ (clear_card and str(clear_card) or '0.00')
        d['allow_card']='￥'+ (allow_card and str(allow_card) or '0.00')




        d['sz_money']='￥'+ (sz_money and str(sz_money) or '0.00')
        if check_opreate == 'checked':
            d['operate']=str(row[13] or '')
        else:
            d['operate']=_(u'全部')
        sum_recharge_money +=recharge_money
        sum_recharge_count +=recharge_count
        sum_refund_money +=refund_money
        sum_refund_count +=refund_count
        sum_cost_money +=cost_money
        sum_manage_money +=manage_money
        sum_hairpin_count +=hairpin_count
        sum_back_card_count +=back_card_count
        sum_back_card_money +=back_card_money

        sum_no_card_back+=no_card_back
        sum_card_back+=card_back
        sum_clear_card+=clear_card
        sum_allow_card+=allow_card

        sum_sz_money +=sz_money
        if check_opreate == 'checked':
            if row[13]:
                d['operate']=str(row[13])
        else:
               d['operate']=u'%s'%_(u'全部')

        re.append(d.copy())
    d={}
    d['operate']=u'汇总:'
    d['recharge_money']='￥'+ (sum_recharge_money and str(sum_recharge_money) or '0.00')
    d['recharge_count']=str(sum_recharge_count)
    d['refund_money']='￥'+ (sum_refund_money and str(sum_refund_money) or '0.00')
    d['refund_count']=str(sum_refund_count)
    d['cost_money']='￥'+ (sum_cost_money and str(sum_cost_money) or '0.00')
    d['manage_money']='￥'+ (sum_manage_money and str(sum_manage_money) or '0.00')
    d['hairpin_count']=str(sum_hairpin_count)
    d['back_card_count']=str(sum_back_card_count)
    d['back_card_money']='￥'+ (sum_back_card_money and str(sum_back_card_money) or '0.00')
    d['no_card_back']='￥'+ (sum_no_card_back and str(sum_no_card_back) or '0.00')
    d['card_back']='￥'+ (sum_card_back and str(sum_card_back) or '0.00')
    d['clear_card']='￥'+ (sum_clear_card and str(sum_clear_card) or '0.00')
    d['allow_card']='￥'+ (sum_allow_card and str(sum_allow_card) or '0.00')




    d['sz_money']='￥'+ (sum_sz_money and str(sum_sz_money) or '0.00')
    d['summary_date']=st.strftime("%Y-%m-%d")+"---"+et.strftime("%Y-%m-%d")
    if 'exporttype' in request.GET:
        re.append(d.copy())
    item_count=len(re)#不分页
    page_count=1
    limit=item_count
    Result['item_count']=item_count
    Result['page']=offset
    Result['limit']=limit
    Result['from']=(offset-1)*limit+1
    Result['page_count']=page_count
    Result['datas']=re
    Result['userData']=d
    return Result




#报表入口
def getsearchRecordsr(request,ReportName):
    #isContainedChild=request.GET.get("isContainChild","0")
    #deptIDs=request.GET.get('deptIDs',"")
    userIDs=request.GET.get('UserIDs',"")
    q=request.GET.get('q','')
    #if st=='':
    #	st=datetime.datetime(now.year,now.month,1,0,0)
    #else:
    #	st=datetime.datetime.strptime(st,"%Y-%m-%d")
    #if et=='':
    #	et=now
    #else:
    #	et=datetime.datetime.strptime(et,"%Y-%m-%d 23:59:59")
        #et=et+datetime.timedelta(days=0,hours=23,minutes=59,seconds=59)
    q=unquote(q)
    ReportName=ReportName.lower()
    if ReportName=='icconsumerlist':
        r=getModelRecords(request,ICConsumerList)
    elif ReportName=='issuecard':
        r=getModelRecords(request,IssueCard)
    elif ReportName=='allowance':
        r=getModelRecords(request,Allowance)
    elif ReportName=='loseunitecard':
        r=getModelRecords(request,LoseUniteCard)
    elif ReportName=='cardmanage':
        r=getModelRecords(request,CardManage)
    elif ReportName=='cardcost':
        r=getCardcost(request,userIDs,q)
    elif ReportName=='backcard':
        r=getRetreatCard(request,userIDs,q)
        #r=getBackcard(request,userIDs,q)
    elif ReportName=='refund':
        r=getRefund(request,userIDs,q)
    elif ReportName=='idposlistreport':
        r=getIDPosListReport(request,userIDs,q)
    elif ReportName=='supplement':
        r=getSupplement(request,userIDs,q)
    elif ReportName=='cardblance':
        r=getCardBlance(request,userIDs,q)
    elif ReportName=='nocardback':
        r=getNoCardBack(request,userIDs,q)
    elif ReportName=='empsumpos':
        r=getEmpSumPos_Ex(request,userIDs,q)
    elif ReportName=='deptsumpos':
        r=getDept_Ding_Device_SumPos_Ex(request,'dept')
    elif ReportName=='diningsumpos':
        r=getDept_Ding_Device_SumPos_Ex(request,'Dininghall')
    elif ReportName=='devicesumpos':
        r=getDept_Ding_Device_SumPos_Ex(request,'Device')
    elif ReportName=='szsumpos':
        r=SZ_sum_report(request)
    elif ReportName=='mealsumpos':
        r=getDept_Ding_Device_SumPos_Ex(request,'Meal')


    return r




#获取Model类型报表 
def getModelRecords(request,dataModel):
    appName=request.path.split('/')[1]
    jqGrid=JqGrid(request,datamodel=dataModel)
    items=jqGrid.get_items()   #not Paged
    userData={}

    d_sum={'money__sum':0,'receive_money__sum':0,'clear_money__sum':0}
    I_sum={'money__sum':0}
    if dataModel==Allowance:
        d_sum=items.aggregate(Sum('money'),Sum('receive_money'))
    if dataModel==ICConsumerList:
        I_sum=items.exclude(pos_model=9).aggregate(Sum('money'))
        t_money=items.filter(pos_model=9).aggregate(Sum('money'))

        userData={'user_pin':u'总计','money':(((I_sum['money__sum'] or 0)-(t_money['money__sum'] or 0)) and str((I_sum['money__sum'] or 0)-(t_money['money__sum'] or 0)) or '0.00')}

    cc=jqGrid.get_json(items)
    tmpFile=dataModel.__name__+'_list.js'
    if appName!='iclock':
        tmpFile=appName+'/'+tmpFile


    t=loader.get_template(tmpFile)
    cc['can_change']=False
    try:
        rows=t.render(cc)#t.render(RequestContext(request, cc))
        if dataModel==Allowance:
            #计算清零补贴合计
            q=request.GET.get('q','')
            userids=request.GET.get('UserID__id__in',"")
            objs=None
            if q!='':
                objs=employee.objects.filter(Q(PIN=q)|Q(EName=q))
            else:
                if userids:
                    userids=userids.split(',')
                    objs=employee.objects.filter(id__in=userids)


            st=request.GET.get('receive_date__gte','')
            et=request.GET.get('receive_date__lte','')
            st=datetime.datetime.strptime(st,"%Y-%m-%d")
            et=datetime.datetime.strptime(et,"%Y-%m-%d %H:%M:%S")
            #et=et+datetime.timedelta(days=1)
            if objs:
                ts=CardCashSZ.objects.filter(UserID__in=objs,checktime__gte=st,checktime__lte=et,allow_type=1,CashType=2)
            else:
                ts=CardCashSZ.objects.filter(checktime__gte=st,checktime__lte=et,allow_type=1,CashType=2)

            a_sum=ts.aggregate(Sum('money'))
            sum_money=str(a_sum['money__sum'] or 0)

            #
            #ll=loads(rows)
            #d={}
            #d['PIN']=u'总计'
            #d['money']=str(d_sum['money__sum'] or 0)
            #d['receive_money']=str(d_sum['receive_money__sum'] or 0)
            #d['clear_money']=sum_money
            #ll.append(d.copy())
            #rows=dumps(ll)
            userData={'PIN':u'总计','money':(d_sum['money__sum']>0 and str(d_sum['money__sum']) or '0.00'),'receive_money':(d_sum['receive_money__sum']>0 and str(d_sum['receive_money__sum']) or '0.00'),'clear_money':(sum_money!='0' and sum_money or '0.00')}




    except Exception,e:
        import traceback;traceback.print_exc()
        rows='[]'
        print "==============",e
    Result={}
    Result['item_count']=cc['records']
    Result['page']=cc['page']
    Result['page_count']=cc['total']
    Result['datas']=loads(rows)
    Result['userData']=userData
    return Result



@permission_required("ipos.iclockdininghall_reports")
def index(request):
    request.user.iclock_url_rel='../..'
    sub_menu='"%s"'%createmenu(request,'report')
    appName=request.path.split('/')[1]
    #print "===============================",sub_menu
    if not request.user.has_perm("ipos.iclockdininghall_reports"):
        return getJSResponse(_("You do not have the browse %s permission!")%(u"报表"))
    settings.PAGE_LIMIT=GetParamValue('opt_users_page_limit','50')
    limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
    tmpFile="reports_list.html"
    if appName!='iclock':
        tmpFile=appName+'/'+tmpFile
    else:
        tmpFile='att'+'/'+tmpFile
    return render(request,tmpFile,{'sub_menu':sub_menu,'limit':limit})
    # return render_to_response(tmpFile,
    # 						 {
    # 						  'sub_menu':sub_menu,
    # 						  'limit':limit
    # 						},RequestContext(request, {}))



@login_required
def gridIndex(request,ReportName):
    if request.method=='GET':
        r=GetGridCaption(ReportName,request)
        return r
    else:
        Result=getsearchRecordsr(request,ReportName)
        rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
        return getJSResponse(rs)


#未来样式，每一个报表一个html
@login_required
def reportIndex(request,ReportName):
    appName=request.path.split('/')[1]
    tmpFile="%s.html"%ReportName
    settings.PAGE_LIMIT=GetParamValue('opt_users_page_limit','50',request.user.id)
    limit= int(request.GET.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
    if appName!='iclock':
        tmpFile=appName+'/report_'+tmpFile
    else:
        tmpFile='att'+'/report_'+tmpFile
    if request.method=='GET':
        if 'title' in request.GET.keys():
            r=GetGridCaption(ReportName,request)
            return r
        cc={}
        cc['limit']=limit
        cc['reportName']=ReportName
        return render(request,tmpFile,cc)#render_to_response(tmpFile,cc,RequestContext(request, {}))
    else:
        Result=getsearchRecordsr(request,ReportName)
        if not 'userData' in Result:Result['userData']={}
        rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+","+""""userdata":"""+dumps(Result['userData'])+"""}"""
        #rs="{"+""""page":"""+str(Result['page'])+","+""""total":"""+str(Result['page_count'])+","+""""records":"""+str(Result['item_count'])+","+""""rows":"""+dumps(Result['datas'])+"""}"""
        return getJSResponse(rs)

