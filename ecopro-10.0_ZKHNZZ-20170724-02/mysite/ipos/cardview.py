#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import string
from django.contrib import auth
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context, RequestContext
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from mysite.iclock.models import *
#from mysite.iclock.datasproc import *
from django.core.paginator import Paginator
#from mysite.iclock.datas import *
#from mysite.core.menu import *
from mysite.core.tools import *
from mysite.core.cmdproc import *
from mysite.iclock.models import *
from django.shortcuts import render
from mysite.base.models import *
from mysite.utils import *
from mysite.core.menu import *
from mysite.ipos.models import *
from  decimal import Decimal
from django.db import transaction as tran

def trunc(DTime):
    return datetime.datetime(DTime.year,DTime.month,DTime.day,0,0,0)


@login_required
def index(request, ModelName):
    if request.method=='GET':
        tmpFile='ipos/'+'icard_sys.html'
        tmpFile=request.GET.get('t', tmpFile)
        sub_menu='"%s"'%createmenu(request,ModelName)
        cc={}

        cc['sub_menu']=sub_menu
        #print sub_menu
        #return render_to_response(tmpFile,cc,RequestContext(request, {}))
        return render(request,tmpFile,cc)





@login_required
def issuecard_index(request, ModelName):
    if request.method=='GET':
        try:
            tmpFile='ipos/%s.html'%(ModelName)
            tmpFile=request.GET.get('t', tmpFile)
            cc={}

            data=GetParamValue('ipos_params',{},'ipos')
            if data:
                from mysite.auth_code import auth_code
                _data=auth_code(data.encode("gb18030"))
                data=loads(_data)
            else:
                data={'pwd':'','main':1,'itype':0,'max_money':'999','pass_key':''}


            #if ModelName=='IssueCard_InitCard':
            #       cc['params']=dumps1(data)
            if ModelName in ['IssueCard_IssueCard','IssueCard_UpdateCard','IssueCard_ReissueCard']:
                from mysite.ipos.dataview import form_for_instance
                dataModel=IssueCard
                dataForm=form_for_instance(dataModel())

                cc['form']=dataForm()

            cc['params']=dumps1(data)
            #return render_to_response(tmpFile,cc,RequestContext(request, {}))
            response=render(request,tmpFile,cc)
            if response:
                return response
            else:
                return  HttpResponse("click too fast", content_type="text/html")

        except:
            return HttpResponse("click too fast", content_type="text/html")
#IC卡根据卡类验证卡余额
def blance_valid(itype,newblance,user):
    try:
        iccardobj= ICcard.objects.filter(pk=itype)
        lessmoney = iccardobj[0].less_money#卡类最小余额
        maxmoney = iccardobj[0].max_money#卡类最大余额
        if lessmoney>newblance and lessmoney>0:
            return getJSResponse({"ret":"OUT_LESSMONEY"})
        elif newblance>maxmoney and maxmoney>0:
            return getJSResponse({"ret":"OUT_MAXMONEY"})
        else:
            return "OK"
    except:
        import traceback;traceback.print_exc()

def Get_Sys_Card_no(request):
    sys_card_no=get_sys_card_no()
    return getJSResponse({"ret":"OK",'message':sys_card_no})

#制卡
def funIssueAddCardBakSave(request):
    try:
        robj = request.POST
        savePosLogToFile('issuecardbak',request.body)
        if robj.has_key("UserID"):
            user_id = robj['UserID']
            emp = employee.objByID(user_id)
        else:
            user_pin = robj['user_pin']
            emp = employee.objByPIN(user_pin)
        card = int(robj['cardno'])
        money = Decimal(robj['blance'])
        card_serial_no = robj['card_serial_no']
        operate_type = robj['operate_type']
        sys_card_no = robj['sys_card_no']
        itype = robj['itype']
    except:
        import traceback;traceback.print_exc()
        pass
    try:
        obj = IssueCard.objects.filter(UserID = emp,cardstatus__in = [CARD_OVERDUE,CARD_VALID],card_privage = POS_CARD,sys_card_no__isnull=False)
        if obj:
            return getJSResponse({'ret':'HAVECARD'})#该人员已有有效卡在使用
    except:
        pass
    try:
        if IssueCard.objects.get(cardno=card,cardstatus__in = [CARD_OVERDUE,CARD_VALID],sys_card_no__isnull=False):
            return getJSResponse({"ret":"ISUSE"})#卡号已经使用
    except:
        pass
    try:
        emp_card = IssueCard.objects.get(cardno=card,sys_card_no__isnull=True)
        if emp_card.cardstatus == CARD_LOST:
            return getJSResponse({"ret":"CARD_LOST"})#登记的卡号，已经挂失
        if emp_card.cardstatus == CARD_STOP:
            #print "ddddddddddd"
            return getJSResponse({"ret":"CARD_STOP"})#登记的卡号，已经停用

        if emp_card.UserID <> emp:
            return getJSResponse({"ret":"EMPNOTCARD"})#卡号登记的人员跟时间发卡的人员不一致
    except:
        pass
    if operate_type == '6':#发卡
        sys_card_no=get_sys_card_no()

    try:
        if IssueCard.objects.get(sys_card_no=sys_card_no):
            return getJSResponse({"ret":"SYS_ISUSE"})#卡账号号已经使用
    except:
        pass

    if operate_type == '12':#换卡
        sys_card_no=get_sys_card_no()
        newblance = Decimal(robj.get('blance1',0))
        money = 0
    else:
        newblance = money
    try:
        re_valid = blance_valid(itype,newblance,emp)
        if re_valid == "OK":
            CardCashSZBak(user_pin = emp.PIN,
                      user_name = emp.EName,
                      user_dept_name = '',
                      physical_card_no = card,
                      sys_card_no = sys_card_no,
                      checktime = datetime.datetime.now(),
                      money = money,
                      blance = money,
                      cardserial = card_serial_no,
                      hide_column = operate_type).save()
            return getJSResponse({"ret":"OK",'message':sys_card_no})
        else:
            message=blance_valid(itype,newblance,emp)#验证余额
            return message
    except:
        import traceback;traceback.print_exc()
        return getJSResponse({"ret":"FAIL"})



#发卡
def funIssueAddCardSave(request):
    try:
        obj = request.POST
        savePosLogToFile('issuecard',request.body)
        if obj.has_key("UserID"):
            user_id = obj['UserID']
            emp = employee.objByID(user_id)
        else:
            user_pin = obj['user_pin']
            emp = employee.objByPIN(user_pin)
        card = int(obj['cardno'])
        money = Decimal(obj['blance'])
        card_serial_no = obj['card_serial_no']
        operate_type = obj['operate_type']
        sys_card_no = obj['sys_card_no']
        itype = obj['itype']
        card_cost = obj['card_cost']
        mng_cost = obj['mng_cost']
        card_privage = obj['card_privage']
        pwd = obj['Password']
        newblance = money
        if sys_card_no=='':
            return getJSResponse({"ret":"FAIL"})

        if operate_type == '12':#补卡换卡
            #newblance = 0
            old_sys_card_no = obj['old_sys_card_no']
            card_cost1 = obj['card_cost1']

            ReplenishCard(UserID=emp,
                       oldcardno=old_sys_card_no,
                       newcardno=sys_card_no,
                       blance=newblance,create_operator=request.user.username).save()
            objcard = IssueCard.objects.get(sys_card_no=old_sys_card_no)
            newblance1=objcard.blance
            objcard.cardstatus = CARD_INVALID
            objcard.blance = 0
            objcard.save()
            CardCashSZ(UserID=objcard.UserID,
                      card=objcard.cardno,
                      sys_card_no = sys_card_no,
                      dept_id=objcard.UserID.DeptID_id,
                      checktime = datetime.datetime.now(),
                      CashType_id=5,#charge type
                      money=newblance1,
                      create_operator=request.user,
                      cardserial = card_serial_no,
                      hide_column=15,blance=0,log_flag = 2).save(force_insert=True)

            if card_cost1>0:
                CardCashSZ(UserID=objcard.UserID,
                              card=objcard.cardno,
                              sys_card_no = sys_card_no,
                              dept_id=objcard.UserID.DeptID_id,
                              checktime = datetime.datetime.now(),
                              CashType_id=4,#charge type
                              money=card_cost1,
                              cardserial = card_serial_no,
                              create_operator=request.user,
                              hide_column=15,blance=0,log_flag = 2).save(force_insert=True)
            IssueCard(UserID = emp,
               cardno = card,
               sys_card_no = sys_card_no,
               cardstatus = CARD_VALID,
               card_privage = POS_CARD,
               card_cost = card_cost,
               mng_cost = mng_cost,
               issuedate=trunc(datetime.datetime.now()),
               itype_id = itype,blance = newblance,Password = pwd,card_serial_num=card_serial_no ).save()

            updateCardToEmp(emp,card)
            logName=datetime.datetime.now().strftime("replenishcard_%Y%m%d.txt")#日志名字
            nt=datetime.datetime.now()
            tempFile(logName,u"oldcardno=%s,newcardno=%s,blance=%s, 时间：%s 操作员：%s"%(old_sys_card_no,sys_card_no,newblance,nt.strftime('%Y-%m-%d %H:%M:%S'),request.user.username))
            #iclocks = iclock.objects.filter(ProductType__in = [11,12,13]).exclude(DelTag=1)
            #update_pos_device_info(iclocks,[objcard],"USERINFO")#下发原卡为黑名单
            #new_objcard = IssueCard.objects.get(sys_card_no = sys_card_no)
            #update_pos_device_info(dev,[new_objcard],"USERINFO")#下发白名单卡
        else:#发卡
            obj = IssueCard.objects.filter(UserID = emp,cardstatus__in = [CARD_OVERDUE,CARD_VALID],card_privage = POS_CARD,sys_card_no__isnull=True)
            if obj:
                obj[0].itype_id = itype
                obj[0].blance = money
                obj[0].Password = pwd
                obj[0].sys_card_no = sys_card_no
                obj[0].cardno = card
                obj[0].card_cost = card_cost
                obj[0].mng_cost = mng_cost
                obj[0].card_serial_num = card_serial_no
                obj[0].issuedate=trunc(datetime.datetime.now())
                obj[0].create_operator=request.user
                obj[0].save(force_update=True)
#                cache.set("IC_Card_Count",sys_card_no,TIMEOUT)
            else:
                IssueCard(UserID = emp,
                cardno = card,
                    sys_card_no = sys_card_no,
                    cardstatus = CARD_VALID,
                    card_privage = card_privage,
                    card_cost = card_cost,
                    mng_cost = mng_cost,
                    create_operator=request.user,
                    issuedate=trunc(datetime.datetime.now()),
                itype_id = itype,blance = money,Password = pwd,card_serial_num=card_serial_no ).save(force_insert=True)
#                cache.set("IC_Card_Count",sys_card_no,TIMEOUT)
            updateCardToEmp(emp,card)
            objcard = IssueCard.objects.get(sys_card_no = sys_card_no)
            if settings.CARDTYPE==2:
                iclocks = iclock.objects.filter(ProductType__in = [11,12,13]).exclude(DelTag=1)
                update_pos_device_info(iclocks,[objcard],"USERINFO")#下发白名单卡
        if card_privage == POS_CARD:
#            blance_valid(type,newblance,emp)#验证余额
            CardCashSZ(UserID=emp,
                 card = card,
                 dept = emp.DeptID,
                 checktime = datetime.datetime.now(),
                 CashType_id = 7,#cost type 发卡
                 cardserial = card_serial_no,
                 money = card_cost,
                 sys_card_no = sys_card_no,
                 create_operator=request.user,

                 hide_column = 7,blance = newblance,log_flag = 2 ).save()
            if  money>0:#换卡,发卡的时候充值operate_type <> '12' and
                CardCashSZ(UserID = emp,
                     card = card,
                     dept = emp.DeptID,
                     sys_card_no = sys_card_no,
                     checktime = datetime.datetime.now(),
                     cardserial = card_serial_no,
                     CashType_id =1,#cost type发卡的时候充值
                     money = money,
                    create_operator=request.user,
                     hide_column = 1,blance = newblance,log_flag = 2).save()
            CardCashSZ(UserID = emp,
                 card = card,
                 dept = emp.DeptID,
                 sys_card_no = sys_card_no,
                 checktime = datetime.datetime.now(),
                 CashType_id =11,#cost type 管理费
                 cardserial = card_serial_no,
                 money=mng_cost,
                 create_operator=request.user,

                 hide_column=11,blance=newblance,log_flag = 2).save()
            return getJSResponse({"ret":"OK"})
    except:
        import traceback;traceback.print_exc()
        cache.delete("IC_Card_Count");
        return getJSResponse({"ret":"FAIL"})








def funSaveCardmanage(request):
    """发管理卡"""
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
    obj = request.POST
    try:
        card_privage = obj['card_privage']
        card = int(obj['cardno'])
        sys_card_no = obj['sys_card_no']
        pwd ='' #obj['Password']
        dining_id = obj['dining']
        if dining_id=='0':
            dining_id=None
        try:
            if IssueCard.objects.get(cardno=card):
                return getJSResponse({"ret":"ISUSE"})#卡号已经使用
        except:
            pass
        try:
            if IssueCard.objects.get(sys_card_no = sys_card_no):
                return getJSResponse({"ret":"SYS_ISUSE"})#卡账号重复
        except:
            pass
        CardManage(card_no = card,
        pass_word = pwd,
        dining_id = dining_id,
        cardstatus = CARD_VALID,
        sys_card_no = sys_card_no,card_privage = card_privage).save()
        IssueCard(
                        cardno = card,
                        sys_card_no = sys_card_no,
                        cardstatus = CARD_VALID,
                        card_privage = card_privage,
                        create_operator=request.user.username,
                        issuedate=datetime.datetime.now(),
                        Password = pwd,itype = None ).save()
        #dev = Device.objects.filter(device_type = DEVICE_POS_SERVER,dining = Dininghall.objects.get(pk=dining_id))
        if settings.CARDTYPE==2:
            if dining_id:
                sns=IclockDininghall.objects.filter(dining__in=dining_id).values_list('SN',flat=True)
                iclocks = iclock.objects.filter(ProductType__in = [11,12,13],SN__in=sns).exclude(DelTag=1)
            else:
                iclocks = iclock.objects.filter(ProductType__in = [11,12,13]).exclude(DelTag=1)
            objcard = IssueCard.objects.get(sys_card_no = sys_card_no)
            update_pos_device_info(iclocks,[objcard],"USERINFO")

        adminLog(time=datetime.datetime.now(),User=request.user,object=u'%s'%card, model=CardManage._meta.verbose_name, action=u'%s'%_(u"发管理卡")).save(force_insert=True)

        return getJSResponse({"ret":"OK"})
    except:
        cache.delete("IC_Card_Count")
        import traceback;traceback.print_exc()
        return getJSResponse({"ret":"FAIL"})

#IC保存充值，退款，退卡纠错检查数据
def funIssueCardBakSave(request):
    from mysite.ipos.models import CardCashSZBak,IssueCard,PRIVAGE_CARD,CARD_LOST,CARD_STOP,CARD_OVERDUE
    obj = request.POST
    #print "99999=",obj
    try:
        card = int(obj['card'])
        money = obj['money']
        operate_type = obj['operate_type']
        if operate_type=='8':
            card_serial_no = int(obj['card_serial_no'])
        else:
            card_serial_no = int(obj['card_serial_num'])
        sys_card_no = obj['sys_card_no']
        if operate_type in ['1','5']:
            card_new_blance = obj['op_card_blance']
        if operate_type == '4':#退卡
            card_blance = Decimal(obj['card_blances'])
        objcard=IssueCard.objects.get(sys_card_no = sys_card_no)
        if objcard:
            if objcard.card_privage == PRIVAGE_CARD and operate_type == '1':
                return getJSResponse({"ret":"PRIVAGE_CARD"})
            elif objcard.cardstatus == CARD_LOST and operate_type == '1':
                return getJSResponse({"ret":"CARD_LOST"})
            elif objcard.cardstatus ==CARD_STOP and operate_type == '1':
                return getJSResponse({"ret":"CARD_STOP"})
            elif objcard.cardstatus ==CARD_OVERDUE and operate_type == '1':
                return getJSResponse({"ret":"CARD_OVERDUE"})
            elif operate_type == '9':#纠错
                if card!=int(objcard.cardno):
                    return getJSResponse({"ret":1,"message":u'卡号不符！'})
                if objcard.cardstatus in [CARD_LOST,CARD_STOP,CARD_OVERDUE]:
                    return getJSResponse({"ret":1,"message":u'卡状态异常！'})
                if objcard.card_privage in [PRIVAGE_CARD]:
                    return getJSResponse({"ret":1,"message":u'卡为管理卡！'})
                id=request.POST.get('pos_id')
                card_blance = Decimal(obj['card_blances'])
                ic_obj=ICConsumerList.objects.get(id=id)
                if ic_obj.pos_model!=2:
                    return getJSResponse({"ret":1,"message":u'仅限对于金额模式的消费进行纠错！'})

                if card_blance!=objcard.blance:
                    return getJSResponse({"ret":1,"message":u'卡余额与账上余额不符！'})

                ic_money=ic_obj.money
                c_money=ic_money-Decimal(money)
                if c_money+objcard.blance<0:
                    return getJSResponse({"ret":1,"message":u'卡内余额不足！'})
                return getJSResponse({"ret":0,"data":{"c":int(c_money*100),"b":int((c_money+objcard.blance)*100)/100}})


            else:
                newblance = 0
                if operate_type == '5':#退款
                    newblance = Decimal(card_new_blance)
                    card_serial_no+=1
                    re_valid = blance_valid(objcard.itype_id,newblance,objcard.UserID)#验证余额
                    if  not re_valid == "OK":
                        return re_valid
                if operate_type == '1':#充值
                    newblance = Decimal(card_new_blance)
                    re_valid = blance_valid(objcard.itype_id,newblance,objcard.UserID)
                    if not re_valid == "OK":
                        return re_valid
                if operate_type == '8':#手工补消费
                    card_serial_no+=1
                    c_blance = Decimal(obj['blance'])
                    newblance = c_blance - Decimal(money)
                    re_valid = blance_valid(objcard.itype_id,newblance,objcard.UserID)
                    if not re_valid == "OK":
                        return re_valid
                if operate_type == '4' and card_blance > 0:#退卡
                    card_serial_no+=1
                    CardCashSZBak(user_pin = objcard.employee().PIN,
                          user_name = objcard.employee().EName,
                          user_dept_name = '',
                          physical_card_no = card,
                          sys_card_no = sys_card_no,
                          checktime = datetime.datetime.now(),
                          money = card_blance,
                          blance = 0,
                          cardserial = card_serial_no,
                          hide_column = 5).save()

                CardCashSZBak(user_pin = objcard.employee().PIN,
                          user_name = objcard.employee().EName,
                          user_dept_name = '',
                          physical_card_no = card,
                          sys_card_no = sys_card_no,
                          checktime = datetime.datetime.now(),
                          money = money,
                          blance = newblance,
                          cardserial = card_serial_no,
                          hide_column = operate_type).save()
            return getJSResponse({"ret":"OK"})
    except:
        import traceback;traceback.print_exc()
        return getJSResponse({"ret":"FAIL"})


#保存充值.退款.手工补消费纠错数据zkecopro
#@tran.commit_on_success
def funIssueCardSave(request):
    obj = request.POST
    #print obj
    card = int(obj['card'])
    #operate_type = obj['operate_type']
    money = Decimal(obj['money'])
    sys_card_no = obj['sys_card_no']
    operate_type = obj['operate_type']
    if operate_type=='8':
        card_serial_no = int(obj['card_serial_no'])
    else:
        card_serial_no = int(obj['card_serial_num'])
    if operate_type == '8':#手工补消费
        name = obj['name']
        pin = obj['pin']
        meal = obj['meal']
        try:
            pos_device = obj['posdevice']
        except:
            return getJSResponse({"ret":"FAIL"})
        hand_date = obj['hand_date']
        c_blance = Decimal(obj['blance'])
    if operate_type == '15':#退卡
        card_serial_no+=1
        card_blance = Decimal(obj['card_blances'])
    if operate_type == '9':#
        c_blance = Decimal(obj['card_blances'])

    if operate_type in ['1','5']:#充值、退款
        card_new_blance = obj['op_card_blance']
    objcard=IssueCard.objects.get(sys_card_no = sys_card_no)
    if objcard:
        try:
            objcard.create_operator=request.user.username
            action = ''
            if operate_type == '15':#有卡退卡操作，改变状态为无效
                action = u'%s'%_(u"有卡退卡")
                objcard.cardstatus =CARD_INVALID
                objcard.blance = 0
                pin=objcard.UserID.PIN
                if card_blance >0 :
                    CardCashSZ(UserID = objcard.UserID,
                         card = card,
                         dept = objcard.UserID.DeptID,
                         checktime = datetime.datetime.now(),
                         CashType_id = 5,#charge type
                         money = card_blance,
                         blance = 0,
                         sys_card_no = sys_card_no,
                         cardserial = card_serial_no,
                         create_operator=request.user,
                         hide_column = operate_type,log_flag = 2).save()
                BackCard(UserID = objcard.UserID,
                            cardno = card,
                            sys_card_no = sys_card_no,
                            card_serial_num = card_serial_no,
                            card_money = money or 0,
                            back_money = card_blance or 0,
                            checktime = datetime.datetime.now(),
                            create_operator = request.user).save(force_insert = True)
                objcard.save()
                emp=employee.objByPIN(pin)
                updateCardToEmp(emp,'')
                devlist = iclock.objects.filter(ProductType__in =[11,12,13]).exclude(DelTag=1)
                delete_pos_device_info(devlist,[objcard],'',"USERINFO")#删除黑白名单
                LoseUniteCard.objects.all().filter(UserID = objcard.UserID_id).delete()#删除挂失解挂记录
            else:
                if operate_type == '5' or operate_type == '1':#退款,充值
                    action =  u'%s'%_(u"充值") if operate_type == '1' else u'%s'%_(u"退款")
                    card_serial_no+=1
                    newblance = card_new_blance
                elif operate_type=='8':#手工补消费
                    action = u'%s'%_(u"手工补消费")
                    card_serial_no+=1
                    newblance = c_blance - money
                elif operate_type=='9':
                    action = u'%s'%_(u"纠错")
                    card_serial_no+=1
                    id = int(obj['pos_id'])

                    ic_obj=ICConsumerList.objects.get(id=id)


                    ic_money=ic_obj.money
                    c_money=ic_money-Decimal(money)

                    newblance = c_blance + c_money

                objcard.blance = newblance
                objcard.card_serial_num = card_serial_no
                objcard.save()
            if operate_type == '8':#手工补消费
                HandConsume(
                card = card,
                sys_card_no = sys_card_no,
                blance = objcard.blance,
                name = name,
                pin = pin,
                meal_id = meal,
                posdevice_id = pos_device,
                create_operator=request.user,
                money = money,hand_date=hand_date,
                card_serial_no = card_serial_no
                ).save()
            if operate_type == '9':#纠错
                postime=obj['apply_datetime']
                #ic_obj.pos_model=9
                #ic_obj.blance=c_blance+ic_obj.money
                #ic_obj.type_name=9
                #ic_obj.create_operator=request.user
                #ic_obj.pos_time=postime
                #ic_obj.id=None
                #ic_obj.money=ic_obj.money
                #ic_obj.save(force_insert=True)
                ICConsumerList(user_id=ic_obj.user_id,
                               user_pin=ic_obj.user_pin,
                               user_name=ic_obj.user_name,
                               dept=ic_obj.dept,
                               card=ic_obj.card,
                               sys_card_no=ic_obj.sys_card_no,
                               dev_sn=ic_obj.dev_sn,
                               card_serial_num=card_serial_no+1,
                               dev_serial_num=ic_obj.dev_serial_num,
                               pos_time=postime,
                               convey_time=None,#postime,
                               type_name=9,
                               money=ic_obj.money,
                               balance=c_blance+ic_obj.money,
                               pos_model=9,
                               dining =ic_obj.dining,
                               meal=ic_obj.meal,
                               meal_data=ic_obj.meal_data,
                               create_operator=request.user,
                               log_flag=ic_obj.log_flag,
                               discount=ic_obj.discount

                               ).save(force_insert=True)



                #
                #ic_obj.id=None
                #ic_obj.type_name=6
                #ic_obj.create_operator=request.user
                #ic_obj.pos_time=postime
                #ic_obj.card_serial_num=card_serial_num
                #ic_obj.pos_model=2
                #ic_obj.blance=newblance
                #ic_obj.money=money
                #ic_obj.save(force_insert=True)


                ICConsumerList(user_id=ic_obj.user_id,
                               user_pin=ic_obj.user_pin,
                               user_name=ic_obj.user_name,
                               dept=ic_obj.dept,
                               card=ic_obj.card,
                               sys_card_no=ic_obj.sys_card_no,
                               dev_sn=ic_obj.dev_sn,
                               card_serial_num=card_serial_no+1,
                               dev_serial_num=ic_obj.dev_serial_num,
                               pos_time=postime,
                               convey_time=None,#postime,
                               type_name=6,
                               money=money,
                               balance=newblance,
                               pos_model=2,
                               dining =ic_obj.dining,
                               meal=ic_obj.meal,
                               meal_data=ic_obj.meal_data,
                               create_operator=request.user,
                               log_flag=ic_obj.log_flag,
                               discount=ic_obj.discount

                               ).save(force_insert=True)
                logName=datetime.datetime.now().strftime("correct_%Y%m%d.txt")#日志名字
                nt=datetime.datetime.now()
                tempFile(logName,u"id=%d,card=%s,sys_card_no=%s,money=%s,old_money=%s 时间：%s       操作员：%s"%(ic_obj.id,ic_obj.card,sys_card_no,money,ic_obj.money,nt.strftime('%Y-%m-%d %H:%M:%S'),request.user.username))




            if operate_type not in ['8','9']:
                if operate_type=='1':
                    cashtypeid=1
                elif operate_type=='15':
                    cashtypeid=4
                else:
                    cashtypeid=5
                CardCashSZ(UserID = objcard.UserID,
                            card = card,
                            dept = objcard.UserID.DeptID,
                            checktime = (datetime.datetime.now()+datetime.timedelta(seconds=1)),
                            CashType_id = cashtypeid,#charge type
                            money = money,
                            blance = objcard.blance,
                            sys_card_no = sys_card_no,
                            cardserial = card_serial_no,
                            create_operator=request.user,
                            hide_column = operate_type,log_flag = 2).save()
            #adminLog(time=datetime.datetime.now(),User=request.user,object=request.META["REMOTE_ADDR"], model='CardCashSZ', action=u'%s-%s-%s-%s-%s'%(_(u"卡操作"),card,operate_type,money,sys_card_no)).save(force_insert=True)
            adminLog(time = datetime.datetime.now(), User = request.user, object = u'%s-%s-%s'%(card,money,sys_card_no),
                     model = CardCashSZ._meta.verbose_name,
                     action = u'%s-%s' % (_(u"卡操作"), action)).save(force_insert = True)

            return getJSResponse({"ret":"OK"})
        except:
            import traceback;traceback.print_exc()
            return getJSResponse({"ret":"FAIL"})


#验证卡的有效性
def funValidCard(request):
    obj = request.POST
    operate_type = obj['operate_type']
    if operate_type == '9':#换卡
        sys_card_no = obj['old_sys_card_no']
    elif operate_type in ['8','1']: #修改卡资料
        sys_card_no = obj['sys_card_no']
    try:
        objcard=IssueCard.objects.get(sys_card_no = sys_card_no)
    except:
        return getJSResponse({"ret":"Not_REGISTER_CARD"})
    try:
        if objcard:
            if objcard.card_privage == PRIVAGE_CARD:
                return getJSResponse({"ret":"PRIVAGE_CARD"})
            elif operate_type == '9' and objcard.cardstatus in [CARD_OVERDUE,CARD_VALID]:
                return getJSResponse({"ret":"CARD_OVERDUE_VALID"})
            elif objcard.UserID.OffDuty == 1:
                return getJSResponse({"ret":"STATUS_LEAVE"})
            elif objcard.cardstatus ==CARD_STOP:
                return getJSResponse({"ret":"CARD_STOP"})
            elif operate_type <> '9' and objcard.cardstatus ==CARD_LOST:
                return getJSResponse({"ret":"CARD_LOST"})
            else:
                return getJSResponse({"ret":"OK"})
    except Exception,e:
        print "-----",e

#修改卡资料
def funChangeCardInfo(request):
    obj = request.POST
    #    print "99999",obj
    sys_card_no = obj['sys_card_no']
    card_type = obj['itype']
    pwd = obj['Password']
    issue_date = obj['issue_date']
    objcard=IssueCard.objects.get(sys_card_no = sys_card_no)
    try:
        objIccard = ICcard.objects.get(pk=card_type)
    except:
        import traceback;traceback.print_exc()
        pass
    try:
        iscardate = datetime.datetime.strptime(issue_date,'%Y-%m-%d')
        nowtime = datetime.datetime.now()
        daycount = (nowtime-iscardate).days
        maxday = objIccard.use_date
        if maxday==None or maxday>=daycount  or maxday==0:
            objcard.cardstatus=CARD_VALID
        elif daycount>maxday and maxday >0:
            objcard.cardstatus=CARD_OVERDUE
        objcard.itype_id = card_type
        objcard.Password = pwd
        objcard.issuedate = iscardate
        objcard.create_operator=request.user.username
        objcard.save()
        return getJSResponse({"ret":"OK"})
    except:
        import traceback;traceback.print_exc()
        return getJSResponse({"ret":"FAIL"})
