#!/usr/bin/env python
#coding=utf-8

from mysite.base.models import *
from mysite.ipos.models import *
from mysite.iclock.models import adminLog,employee
from mysite.core.cmdproc import delete_pos_device_info,update_pos_device_info,set_pos_device_info,saveCmd
from mysite.utils import *
from mysite.iclock.iutils import *
from django.utils.translation import ugettext_lazy as _
from  decimal import Decimal
from django.db import transaction as tran
import datetime

def save_Meal_Machine(request,*args):
    use_machine = request.POST.get('use_machine', '')
    if use_machine:
        use_machine=request.POST.get('use_machine','').split(",")
        code=request.POST.get('code','')
        Mealmachine.objects.filter(meal__code=code).delete()
        meal=Meal.objects.get(code=code)
        for t in use_machine:
            dev=getDevice(t)
            Mealmachine(meal=meal,SN=dev).save()
            update_pos_device_info([dev],[meal],"MEALTYPE")
    else:
        code=request.POST.get('code','')
        Mealmachine.objects.filter(meal__code=code).delete()

def saveICcard(request,*args):
    from  decimal import Decimal
    code=request.POST.get('code','')
    name=request.POST.get('name')
    discount=request.POST.get('discount',0)
    pos_time=request.POST.get('pos_time',1)
    date_max_money=request.POST.get('date_max_money',0)
    date_max_count=request.POST.get('date_max_count',0)
    per_max_money=request.POST.get('per_max_money',0)
    meal_max_money=request.POST.get('meal_max_money',0)
    meal_max_count=request.POST.get('meal_max_count',0)
    less_money=request.POST.get('less_money',0)
    max_money=request.POST.get('max_money',9999)
    remark=request.POST.get('remark','')
    posmeal=request.POST.get('posmeal','').split(",")
    use_mechine=request.POST.get('use_mechine','').split(",")
    use_date=request.POST.get('use_date',0)
    date_max_money=Decimal(date_max_money)
    per_max_money=Decimal(per_max_money)
    meal_max_money=Decimal(meal_max_money)
    less_money=Decimal(less_money)
    max_money=Decimal(max_money)
    discount=long(discount)
    date_max_count=long(date_max_count)

    ic=ICcard.objects.filter(id__in=args)
    if ic:
        u=ic[0]
        u.code=code
        u.name=name
        u.discount=discount
        u.pos_time=pos_time
        u.date_max_money=date_max_money
        u.date_max_count=date_max_count
        u.per_max_money=per_max_money
        u.meal_max_money=meal_max_money
        u.meal_max_count=meal_max_count
        u.less_money=less_money
        u.max_money=max_money
        u.use_date=use_date
        u.remark=remark
        u.save()
        adminLog(time=datetime.datetime.now(),User=request.user, model=ICcard._meta.verbose_name,object=u"编号:%s;名称:%s"%(u.code,u.name), action=_(u"修改")).save(force_insert=True)

    else:
        if ICcard.objects.filter(code=code,DelTag=0):
            return getJSResponse({"ret":1,"message": u"%s"%_(u'卡类编号重复')})
        u=ICcard(code=code,name=name,discount=discount,pos_time=pos_time,date_max_money=date_max_money,date_max_count=date_max_count,
                   per_max_money=per_max_money,meal_max_money=meal_max_money,meal_max_count=meal_max_count,less_money=less_money,max_money=max_money,use_date=use_date,remark=remark)
        u.save()
        adminLog(time=datetime.datetime.now(),User=request.user, model=ICcard._meta.verbose_name,object=u"编号:%s;名称:%s"%(u.code,u.name), action=_(u"新增")).save(force_insert=True)
    newObj=u
    ICcardposmeal.objects.filter(iccard=u).delete()
    for t in posmeal:
        try:
            m=Meal.objects.get(code=t)
            ICcardposmeal(iccard=u, meal=m).save()
        except:
            pass
    old_ICcardmechine=ICcardmechine.objects.filter(iccard=u).values_list('SN',flat=True)
    del_ICcardmechine=[]
    for del_sn in old_ICcardmechine:
        if del_sn in use_mechine:
            continue
        else:
            del_ICcardmechine.append(del_sn)
    ICcardmechine.objects.filter(iccard=u).delete()
    for t in use_mechine:
        try:
            i=iclock.objects.get(SN=t)
            ICcardmechine(iccard=u, SN=i).save()
        except:
            pass
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))

    if settings.CARDTYPE==2:
        del_devs=iclock.objects.filter(SN__in=del_ICcardmechine,ProductType__in=[11,12,13]).exclude(DelTag=1)
        if del_devs:
            delete_pos_device_info(del_devs,[newObj],"","CARDTYPE")
        devlist=iclock.objects.filter(ProductType__in=[11,12,13]).exclude(DelTag=1)
        #objs=ICcardmechine.objects.filter(iccard=newObj)
        #devlist=[]
        ##      devlist.append(t.SN)

        if devlist:
            update_pos_device_info(devlist,[newObj],"CARDTYPE")
    return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')})



def saveSplitTime(request,key):
    code=request.POST.get('code','')
    name=request.POST.get('name')
    starttime=request.POST.get('starttime',time(0,0))
    endtime=request.POST.get('endtime',time(0,0))
    isvalid=request.POST.get('isvalid',0)
    fixedmonery=request.POST.get('fixedmonery',0)
    remarks=request.POST.get('remarks','')
    use_mechine=request.POST.get('use_mechine','').split(",")
    u=SplitTime.objects.get(id=key)

    u.code=code
    u.name=name
    u.starttime=datetime.datetime.strptime(starttime,'%H:%M').time()
    u.endtime=datetime.datetime.strptime(endtime,'%H:%M').time()
    if isvalid==u'2':
        u.isvalid=1
    else:
        u.isvalid=0
    from  decimal import Decimal

    u.fixedmonery=Decimal(fixedmonery)
    u.remarks=remarks
    try:
        u.data_check()
        u.save()
    except Exception,e:
        return getJSResponse({"ret":1,"message": u"%s"%e})

    adminLog(time=datetime.datetime.now(),User=request.user, model=SplitTime._meta.verbose_name,object=u"编号:%s;名称:%s"%(u.code,u.name), action=_(u"修改")).save(force_insert=True)
    newObj=u
    SplitTimemechine.objects.filter(splittime=u).delete()
    for t in use_mechine:
        try:
            i=iclock.objects.get(SN=t)
            SplitTimemechine(splittime=u, SN=i).save()
        except:
            pass
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))

    if settings.CARDTYPE==2:
        objs=SplitTimemechine.objects.filter(splittime=newObj)
        devlist=iclock.objects.filter(ProductType__in=[11,12,13]).exclude(DelTag=1)
        if devlist:
            if objs:
                devs=[]
                for t in objs:
                    devs.append(t.SN)
                if newObj.isvalid == 1:
                    delete_pos_device_info(devlist,[newObj],'',"FIXED")
                    update_pos_device_info(devs,[newObj],"FIXED")
                else:
                    delete_pos_device_info(devs,[newObj],'',"FIXED")

            else:#没有选择设备默认所有设备
                if newObj.isvalid == 1:
                    update_pos_device_info(devlist,[newObj],"FIXED")
                else:
                    delete_pos_device_info(devlist,[newObj],'',"FIXED")
    return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')})


def saveKeyValue(request,*args):
    from decimal import Decimal
    code=request.POST.get('code','')
    money=request.POST.get('money',0)
    try:
        money=Decimal(money)
    except:
        money=Decimal(0)
    use_mechine=request.POST.get('use_mechine','').split(",")
    ic=KeyValue.objects.filter(id__in=args)
    if ic.count()>0:
        u=ic[0]
        u.code=code
        u.money=money
        u.save()
        adminLog(time=datetime.datetime.now(),User=request.user, model=KeyValue._meta.verbose_name,object=u"编号:%s;名称:%s"%(u.code,u.money), action=_(u"修改")).save(force_insert=True)
    else:
        t=KeyValue.objects.filter(code=code)
        if t:
            u=t[0]
            if u.DelTag==1:
                u.money=money
                u.DelTag=0
                u.save()
                adminLog(time=datetime.datetime.now(),User=request.user, model=KeyValue._meta.verbose_name,object=u"编号:%s;名称:%s"%(u.code,u.money), action=_(u"新增")).save(force_insert=True)
            else:
                return getJSResponse({"ret":1,"message": u"%s"%_(u'键值编号重复')})
        else:
            u=KeyValue(code=code,money=money)
            u.save()
            adminLog(time=datetime.datetime.now(),User=request.user, model=KeyValue._meta.verbose_name, action=_(u"新增"),object=u"编号:%s;名称:%s"%(u.code,u.money)).save(force_insert=True)
    newObj=u
    KeyValuemechine.objects.filter(keyvalue=u).delete()
    for t in use_mechine:
        try:
            i=iclock.objects.get(SN=t)
            KeyValuemechine(keyvalue=u, SN=i).save()
        except:
            pass
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))

    if settings.CARDTYPE==2:

        devlist=iclock.objects.filter(ProductType__in=[11]).exclude(DelTag=1)

        if devlist:
            update_pos_device_info(devlist,[newObj],"PRESSKEY")
    return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')})

@tran.atomic
def saveAllowance(request,key):
    if request.method=="POST":
        #print "saveAllowance",request.POST
        deptIDs=request.POST.get('deptIDs',"")
        UserIDs=request.POST.get('UserIDs',"")
        isContainedChild=request.POST.get('isContainChild',"")
        if UserIDs=='':
            deptidlist=[int(i) for i in deptIDs.split(',')]
            deptids=deptidlist
            if isContainedChild=="1":   #是否包含下级部门
                deptids=[]
                for d in deptidlist:#支持选择多部门
                    if int(d) not in deptids :
                        deptids+=getAllAuthChildDept(d,request)
            cardObj=IssueCard.objects.filter(cardstatus__in = ['1','4']).values('UserID')#, flat=True)#判断人员有效消费卡
            UserIDs=employee.objects.filter(id__in=cardObj,DeptID__in=deptids,OffDuty=0).exclude(DelTag=1)

        else:
            emplist=UserIDs.split(',')
            UserIDs=employee.objects.filter(id__in=emplist)

        valid_date=request.POST.get('valid_date',"")
        if valid_date=="":
            return getJSResponse({"ret":1,"message": u"%s"%_(u'保存失败!日期不正确')})
        try:
            valid_date=datetime.datetime.strptime(valid_date,"%Y-%m-%d")
        except:
            return getJSResponse({"ret":1,"message": u"%s"%_(u'保存失败!日期不正确')})


        money=Decimal(request.POST.get('money',0))
        if money<0.1:
            return getJSResponse({"ret":1,"message": u"%s"%_(u'保存失败!补贴金额过小')})

        #from django.db.models import Max
        #d=Allowance.objects.filter(UserID__in=UserIDs).aggregate(Max('valid_date'))
        #db_valid_date=d['valid_date__max']
        nt=datetime.datetime.now()
        if nt>valid_date :
            return getJSResponse({"ret":1,"message": u"%s"%_(u'保存失败!有效日期应大于当前日期')})
        #batch_id = int(GetParamValue('allow_%s'%(nt.strftime("%Y%m%d")),0,'ipos'))
        #if batch_id==0:
        #       batch_count = int(GetParamValue('allow_batch',0,'ipos'))
        #       batch_id=batch_count+1
        #       SetParamValue('allow_batch',batch_id,'ipos')
        #       SetParamValue('allow_%s'%(nt.strftime("%Y%m%d")),batch_id,'ipos')

        remark= request.POST.get('remark',"")
        if key=='_new_':
            for u in UserIDs:
                objcard = IssueCard.objects.filter(UserID=u,cardstatus__in = [CARD_OVERDUE,CARD_VALID])
#                               if not objcard:
#                                       return getJSResponse({"ret":1,"message": u"%s"%_(u'保存失败!编号%s人员没有发卡')%(u.PIN)})
                sys_card_no = objcard[0].sys_card_no
                batch = datetime.datetime.now().strftime("%Y%m")[2:]
                #batch = 1
                #from django.db.models import Max
                #d=Allowance.objects.filter(sys_card_no=sys_card_no).aggregate(Max('batch'))
                #if d['batch__max']:
                #       batch = int(d['batch__max'])+1
                if (not sys_card_no) and settings.CARDTYPE==2:
                    return getJSResponse({"ret":1,"message": u"%s"%(_(u'保存失败!%s没有卡账号')%objcard[0].cardno)})
                try:
                    Allowance(UserID=u,money=money,valid_date=valid_date,allow_date=nt,remark=remark,batch=batch,sys_card_no=sys_card_no).save(force_insert=True)
                except Exception,e:
                    estr="%s"%e
                    if ('SQL0803N' in estr) or ('IntegrityError' in estr) or ("UNIQUE KEY" in estr) or ("are not unique" in estr) or ("Duplicate" in estr) or ("unique constraint" in estr) or ("duplicate" in estr):
                        return getJSResponse({"ret":1,"message": u"%s"%(_(u'保存失败，补贴重复！'))})
                    #print "saveAllowance",e
                    return getJSResponse({"ret":1,"message": u"%s:%s"%(_(u'保存失败!数据可能出现错误'),e)})

                #else:
                    #return getJSResponse({"ret":1,"message": u"%s"%_(u'保存失败!编号%s人员没有发卡')%(u.PIN)})
        return getJSResponse({"ret":0,"message": u"%s"%_('Save Success')})


def staDataAllowance(request,dataModel,val):
    keys=request.POST.getlist("K")
    devlist=iclock.objects.filter(ProductType__in=[13]).exclude(DelTag=1)
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
    for i in keys:
        try:

            u=Allowance.objects.get(id=int(i))
            if settings.CARDTYPE==1:
                issuecard=IssueCard.objects.get(UserID = u.UserID,cardstatus = CARD_VALID)
            else:
                issuecard=IssueCard.objects.get(sys_card_no = u.sys_card_no)
            #issuecard=IssueCard.objByCardno(u.UserID.Card)
            if issuecard:
                #valid_date = self.object.valid_date
                #if get_option("POS_IC") and now > valid_date:
                #    raise Exception(_(u"编号%s人员补贴记录已超过补贴有效期")%self.object.user)
                #if  iscarobj.cardstatus != CARD_VALID:
                #    raise Exception(_(u"编号%s卡已挂失或过期，无法补贴") % self.object.user)
                #if get_option("POS_IC"):
                #    dev=Device.objects.filter(device_type=DEVICE_POS_SERVER,device_use_type = 2)#查找补贴机
                #    if not dev:
                #        raise Exception(_(u"当前系统，没有补贴设备,操作失败"))
                #newblan = iscarobj.blance+self.object.money
                #if iscarobj.type is not None:
                #   from mysite.personnel.models.model_iccard import ICcard
                #   iccardobj= ICcard.objects.get(pk=iscarobj.type_id)
                #   lessmoney = iccardobj.less_money#卡类最小余额
                #   maxmoney = iccardobj.max_money#卡类最大余额
                #   if lessmoney>newblan and lessmoney>0:
                #        raise Exception(_(u"人员编号%s超出卡类最小余额")%self.object.user)
                #   if newblan>maxmoney and maxmoney>0:
                #        raise Exception(_(u"人员编号%s超出卡类最大余额")%self.object.user)
                #   if maxmoney==0 and newblan > 10000 :
                #        raise Exception(_(u"人员编号%s超出系统允许最大余额")%self.object.user)
                current_time =  datetime.datetime.now()
                u.is_pass=val
                u.pass_name=u'%s'%request.user
                if settings.CARDTYPE==1:
                    u.is_ok = val
                    u.receive_date = (current_time + datetime.timedelta(seconds=1))
                u.save()
                if val==1:

                    if settings.CARDTYPE==1:
                        newblan = issuecard.blance+u.money
                        CardCashSZ(UserID=u.UserID,
                                                  card=issuecard.cardno,
                                                  dept_id=u.UserID.DeptID_id,
                                                  checktime=current_time,
                                                  CashType=CardCashType.objects.get(id=2),#消费类型
                                                  money=u.money,
                                                  hide_column=2,
                                                  blance =newblan,
                                        ).save(force_insert=True)
                        issuecard.blance=newblan
                        issuecard.save(force_update=True)

                    else:
                        set_pos_device_info(devlist,[u],'',"SUBSIDYLOG")
        except Exception,e:
            #print "staDataAllowance-----",e
            return u'%s-%s'%(_(u'审核出现错误'),e)
            #ass


    return _(u'审核完成')


def staDataLoseCard(request,dataModel,val):
    keys=request.POST.getlist("K")
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))

    cardtype=settings.CARDTYPE
    for k in keys:
        if val==3:#挂失
            objcard=dataModel.objects.get(id=k)
            if cardtype==2 and objcard.card_privage ==  PRIVAGE_CARD:
                return _(u'该卡为管理卡，操作失败')
            elif cardtype==2 and objcard.card_privage ==  OPERATE_CARD:
                return _(u'该卡为操作卡，操作失败')
            elif objcard.cardstatus==CARD_LOST:
                return _(u'该卡已挂失，操作失败')
            elif objcard.cardstatus==CARD_STOP:
                return _(u'该卡已停用，操作失败')
            elif objcard.cardstatus ==CARD_INVALID:
                return _(u'该卡已失效，操作失败')
            objcard.cardstatus=CARD_LOST
            objcard.save(force_update=True)
            updateCardToEmp(objcard.UserID,'')
            if cardtype==1:#ID
                if objcard.card_privage == PRIVAGE_CARD:
                    LoseUniteCard(
                             cardno = objcard.cardno,
                             itype = objcard.itype,
                             cardstatus=CARD_LOST,
                             create_operator=request.user.username,
                             Losetime = datetime.datetime.now()).save()
                    obj_card_manage = CardManage.objects.get(card_no = objcard.cardno)
                    obj_card_manage.cardstatus = CARD_LOST
                    obj_card_manage.save()
                else:
                    LoseUniteCard(UserID = objcard.UserID,
                     cardno = objcard.cardno,
                     itype = objcard.itype,
                     cardstatus=CARD_LOST,
                     create_operator=request.user.username,
                     Losetime = datetime.datetime.now()).save()
            if cardtype==2 and objcard.sys_card_no:#挂失名单下发
                LoseUniteCard(UserID = objcard.UserID,
                                 cardno = objcard.cardno,
                                 itype = objcard.itype,
                                 cardstatus=CARD_LOST,
                                create_operator=request.user.username,
                                sys_card_no=objcard.sys_card_no,
                                 Password=objcard.Password,
                                 Losetime = datetime.datetime.now()).save()
                if cardtype==2:

                    devlist=iclock.objects.filter(ProductType__in=[11,12,13]).exclude(DelTag=1)
                    update_pos_device_info(devlist,[objcard],"USERINFO")
        elif val==1:#解挂
            objcard=dataModel.objects.get(id=k)
            if cardtype==2 and objcard.card_privage ==  PRIVAGE_CARD:
                return _(u'该卡为管理卡，操作失败')
            elif cardtype==2 and objcard.card_privage ==  OPERATE_CARD:
                return _(u'该卡为操作卡，操作失败')
            elif objcard.cardstatus==CARD_VALID:
                return _(u'请先挂失，操作失败')
            elif objcard.cardstatus==CARD_STOP:
                return _(u'该卡已停用，操作失败')
            elif objcard.cardstatus ==CARD_INVALID:
                return _(u'该卡已失效，操作失败')
            elif objcard.cardstatus==CARD_OVERDUE:
                return _(u'该卡已过期，操作失败')
            elif objcard.card_privage<> PRIVAGE_CARD and objcard.UserID.OffDuty==1:

                return _(u'该人员已经离职，操作失败')
            obj = IssueCard.objects.filter(UserID = objcard.UserID,cardstatus = CARD_VALID)
            if obj:
                return _(u'该人员已有正在使用的卡,操作失败')


            objcard.cardstatus=CARD_VALID
            objcard.save(force_update=True)
            updateCardToEmp(objcard.UserID,objcard.cardno)

            if cardtype==1:#ID
                if objcard.card_privage == PRIVAGE_CARD:
                    LoseUniteCard(
                             cardno = objcard.cardno,
                             itype = objcard.itype,
                             cardstatus=CARD_VALID,
                             create_operator=request.user.username,
                             Losetime = datetime.datetime.now()).save()
                    obj_card_manage = CardManage.objects.get(card_no = objcard.cardno)
                    obj_card_manage.cardstatus = CARD_VALID
                    obj_card_manage.save()
                else:
                    LoseUniteCard(UserID = objcard.UserID,
                     cardno = objcard.cardno,
                     itype = objcard.itype,
                     cardstatus=CARD_VALID,
                     create_operator = request.user.username,
                     Losetime = datetime.datetime.now()).save()
            if cardtype==2 and objcard.sys_card_no:#解挂名单下发
                LoseUniteCard(UserID = objcard.UserID,
                                 cardno = objcard.cardno,
                                 itype = objcard.itype,
                                 cardstatus=CARD_VALID,
                                 sys_card_no=objcard.sys_card_no,
                                 Password=objcard.Password,
                                 create_operator=request.user.username,
                                 Losetime = datetime.datetime.now()).save()
                if settings.CARDTYPE==2:
                    devlist=iclock.objects.filter(ProductType__in=[11,12,13]).exclude(DelTag=1)
                    delete_pos_device_info(devlist,[objcard],'',"USERINFO")

    return u''

#注销管理卡
def staCancelManageCard(request,dataModel):
    keys=request.POST.getlist("K")
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))

    cardtype=settings.CARDTYPE
    for k in keys:
        objcard=dataModel.objects.get(id=k)
        if objcard.card_privage not in [PRIVAGE_CARD,OPERATE_CARD]:
            return _(u'当前操作只对管理卡或者操作卡有效，操作失败')
        try:
            if settings.CARDTYPE==2 and objcard.sys_card_no:
                obj_manage = CardManage.objects.get(sys_card_no = objcard.sys_card_no)
            else:
                obj_manage = CardManage.objects.get(card_no = objcard.cardno,cardstatus=CARD_VALID)

            obj_manage.cardstatus = CARD_CANCEL
            obj_manage.save()
            objcard.cardstatus = STATUS_INVALID
            objcard.save(force_update=True)
            if settings.CARDTYPE==2:
                devlist=iclock.objects.filter(ProductType__in=[11,12,13]).exclude(DelTag=1)
                delete_pos_device_info(devlist,[objcard],'',"USERINFO")
        except:
            #import traceback;traceback.print_exc()
            pass
    return ''

#@tran.commit_on_success
#@tran.atomic
def staNoCardRetireCard(request,dataModel):
    """退卡，ID卡退卡后清除IssueCard中的信息同时清空userinfo中的Card"""
    keys=request.POST.getlist("K")
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
    cardtype=settings.CARDTYPE

    is_retire_money=1#无卡退款
    for k in keys:
        objcard=dataModel.objects.get(id=k)
        if objcard.card_privage ==  PRIVAGE_CARD:
            return _(u'该卡为管理卡，操作失败')
        if objcard.card_privage ==  OPERATE_CARD:
            return _(u'该卡为操作卡，操作失败')
        if objcard.cardstatus in [CARD_VALID,CARD_OVERDUE]:
            return _(u'请先挂失，操作失败')
        if objcard.cardstatus in [CARD_INVALID]:
            return _(u'无效卡，操作失败')
        try:
            card_blance = objcard.blance
            #objcard.status = STATUS_INVALID
            if settings.CARDTYPE==2:
                objcard.cardstatus = CARD_INVALID
                objcard.failuredate = datetime.datetime.now()
                if is_retire_money:
                    objcard.blance = 0
                objcard.save(force_update=True)
            else:
                if card_blance > 0:
                    return _(u'卡号%s请先退款')%objcard.cardno




            if settings.CARDTYPE==2:#IC
                if objcard.sys_card_no:

                    devlist=iclock.objects.filter(ProductType__in=[11,12,13]).exclude(DelTag=1)
                    #delete_pos_device_info(devlist,[objcard],'',"USERINFO")#删除白名单
                    LoseUniteCard.objects.all().filter(UserID = objcard.UserID).delete()#删除挂失解挂记录
    #                    if self.object.cardstatus==CARD_VALID and  get_option("ATT"):
    #                        oldObj=self.object.UserID
    #                        devs=oldObj.search_device_byuser()
    #                        sync_report_user(devs, [oldObj])
    #                    if self.object.cardstatus==CARD_VALID and get_option("IACCESS"):
    #                        oldObj=self.object.UserID
    #                        if oldObj.check_accprivilege():
    #                           devs=oldObj.search_accdev_byuser()
    #                           sync_report_user(devs,[oldObj])
    #                           #sync_delete_user_privilege(devs,[oldObj])

            if  objcard.card_privage <> PRIVAGE_CARD:

                if is_retire_money and card_blance > 0:
                    CardCashSZ(UserID = objcard.UserID,
                             card = objcard.cardno,
                             dept_id=objcard.UserID.DeptID_id,
                             checktime = datetime.datetime.now(),
                             CashType_id = 5,#退款
                             money = card_blance,
                             blance = 0,
                             sys_card_no = objcard.sys_card_no,
                             log_flag = 2,
                             create_operator=request.user.username,
                             hide_column = 14).save()
                CardCashSZ(UserID = objcard.UserID,
                                card = objcard.cardno,
                                checktime = datetime.datetime.now(),
                                dept_id=objcard.UserID.DeptID_id,
                                CashType_id = 4,#退卡成本
                                money = 0,
                                blance = objcard.blance,
                                sys_card_no = objcard.sys_card_no,
                                log_flag = 2,
                                create_operator=request.user.username,
                                hide_column = 14).save()
                BackCard(UserID = objcard.UserID,
                            cardno = objcard.cardno,
                            card_money = 0,
                            back_money = card_blance,
                            checktime = datetime.datetime.now(),
                            operate_type = 14,
                            create_operator = request.user).save(force_insert = True)
            else:
                try:
                    CardManage.objects.get(card_no = objcard.cardno).delete()
                except:
                    pass

            if settings.CARDTYPE==1:
                updateCardToEmp(objcard.UserID,'')
                objcard.delete()


        except:
            import traceback;traceback.print_exc()



    return ''

def SaveOpSupplement(request,dataModel):
    ss=''
    keys=request.POST.getlist("K")
    money=Decimal(request.GET.get('money',0))
    objcards=dataModel.objects.filter(pk__in = keys)
    for objcard in objcards:
        ss=save_Supplement([objcard],money,request)
    return ss

def SaveSupplement(request,dataModel):
    ss=''
    card=request.POST.get('card',0)
    money=Decimal(request.POST.get('money',0))
    objcards=dataModel.objects.filter(cardno = int(card)).order_by('-id')
    ss=save_Supplement(objcards,money,request)
    return ss
#zkecopro
#@tran.commit_manually
#@tran.atomic
def save_Supplement(objcard,money,request):
    ss=''
    if objcard and objcard[0].cardno:
        if objcard[0].card_privage == PRIVAGE_CARD:
            ss=u'%s'%(_(u"管理卡，操作失败"))
        if objcard[0].cardstatus == CARD_LOST:
            ss=u'%s'%(_(u"该卡已经挂失，操作失败"))
        if objcard[0].cardstatus ==CARD_STOP:
            ss=u'%s'%(_(u"该卡已停用，操作失败"))
        if objcard[0].cardstatus ==CARD_INVALID:
            ss=u'%s'%(_(u"该卡已失效，操作失败"))
        if objcard[0].cardstatus ==CARD_OVERDUE:
            ss=u'%s'%(_(u"该卡已过期，操作失败"))
        if int(money)<0:
            ss=u'%s'%(_(u"充值金额不能为负数"))
        if int(money) == 0:
            ss=u'%s'%(_(u"充值金额不能为零"))
        if ss:
            #tran.rollback()
            return ss
        newblance = objcard[0].blance + money
        try:
            blance_valid(objcard[0].itype_id,newblance,objcard[0].UserID)#验证余额
        except Exception,e:
            ss=u'%s'%e
            #tran.rollback()
            return ss

        try:
            objcard[0].blance = newblance
            objcard[0].save(force_update=True)
            CardCashSZ(UserID = objcard[0].UserID,
                    dept_id = objcard[0].UserID.DeptID_id,
                    card = objcard[0].cardno,
                    checktime = datetime.datetime.now(),
                    CashType_id = 1,#charge type
                    money = money,
                    blance = objcard[0].blance,
                    create_operator=request.user,
                    hide_column = 1,log_flag = 2).save(force_insert=True)
            #tran.commit()
        except Exception,e:
            ss=u'%s'%(_(u"充值失败"))
            #tran.rollback()
            import traceback;traceback.print_exc()
    else:
        ss=u'%s'%(_(u"卡号不存在"))
    return ss
#zkecopro
#@tran.commit_manually
# @tran.atomic
def SaveReim(request,dataModel):
    """ID卡退款"""
    ss=''
    card=request.POST.get('card',0)
    money=Decimal(request.POST.get('money',0))
    objcard=dataModel.objects.filter(cardno = int(card)).order_by('-id')
    if objcard:
        if objcard[0].card_privage == PRIVAGE_CARD:
            ss=u'%s'%(_(u"管理卡，操作失败"))
        if objcard[0].cardstatus == CARD_LOST:
            ss=u'%s'%(_(u"该卡已经挂失，操作失败"))
        if objcard[0].cardstatus ==CARD_STOP:
            ss=u'%s'%(_(u"该卡已停用，操作失败"))
        if objcard[0].cardstatus ==CARD_INVALID:
            ss=u'%s'%(_(u"该卡已失效，操作失败"))
        if int(money)<0:
            ss=u'%s'%(_(u"退款金额不能为负数"))
        if int(money) == 0:
            ss=u'%s'%(_(u"退款金额不能为零"))
            #from mysite.pos.posdevview import read_timebrush
            #objbatch = read_timebrush(card)
            #if objbatch:
            #    type=objbatch.split(':')[0]
            #    if type=='1':#计时开始
            #        raise Exception(_(u'当前用户计时消费未结账，不能退款'))
        if ss:
            # tran.rollback()
            return ss
        newblance = objcard[0].blance - money
        try:
            blance_valid(objcard[0].itype_id,newblance,objcard[0].UserID)#验证余额
        except Exception,e:
            ss=u'%s'%e
            # tran.rollback()
            return ss
        try:
            objcard[0].blance = newblance
            objcard[0].save(force_update=True)
            CardCashSZ(UserID=objcard[0].UserID,
                      card=card,
                      dept_id=objcard[0].UserID.DeptID_id,
                      checktime = datetime.datetime.now(),
                      CashType_id=5,#charge type
                      money=money,
                      create_operator=request.user,
                      hide_column=5,blance=objcard[0].blance,log_flag = 2).save(force_insert=True)
            # tran.commit()
        except:
            ss=u'%s'%(_(u"退款失败"))
            # tran.rollback()
            import traceback;traceback.print_exc()

    else:
        ss=u'%s'%(_(u"卡号不存在"))
    return ss


#zkecopro
#@tran.commit_manually
# @tran.atomic
def SaveRetreat(request,dataModel):
    """ID卡退卡"""
    ss=''
    card=request.POST.get('card',0)
    money=Decimal(request.POST.get('money',0))
    card_serial_num = request.POST.get('card_serial_num',0)
    objcard=dataModel.objects.filter(cardno = int(card)).order_by('-id')
    if objcard:
        if objcard[0].card_privage == PRIVAGE_CARD:
            ss=u'%s'%(_(u"管理卡，操作失败"))
        if objcard[0].cardstatus == CARD_LOST:
            ss=u'%s'%(_(u"该卡已经挂失，操作失败"))
        if objcard[0].cardstatus ==CARD_STOP:
            ss=u'%s'%(_(u"该卡已停用，操作失败"))
        if objcard[0].cardstatus ==CARD_INVALID:
            ss=u'%s'%(_(u"该卡已失效，操作失败"))
        if int(money)<0:
            ss=u'%s'%(_(u"退还成本不能为负数"))
        if ss:
            # tran.rollback()
            return ss
        try:
            newblance=objcard[0].blance
            objcard[0].blance = 0
            objcard[0].cardstatus=CARD_INVALID
            objcard[0].save(force_update=True)
            CardCashSZ(UserID=objcard[0].UserID,
                      card=card,
                      dept_id=objcard[0].UserID.DeptID_id,
                      checktime = datetime.datetime.now(),
                      CashType_id=5,#charge type
                      money=newblance,
                      create_operator=request.user,
                      hide_column=15,blance=0,log_flag = 2).save(force_insert=True)
            if money >0 :
                CardCashSZ(UserID=objcard[0].UserID,
                          card=card,
                          dept_id=objcard[0].UserID.DeptID_id,
                          checktime = datetime.datetime.now(),
                          CashType_id=4,#charge type
                          money=money,
                          create_operator=request.user,
                          hide_column=15,blance=0,log_flag = 2).save(force_insert=True)
            BackCard(UserID = objcard[0].UserID,
                        cardno = card,
                        card_money = money,
                        back_money = newblance,
                        checktime = datetime.datetime.now(),
                        create_operator = request.user).save(force_insert = True)
            pin = request.POST.get('PIN','')
            emp=employee.objects.filter(PIN=pin,DelTag=0)
            if emp:
                emp[0].Card = ''
                emp[0].save()

            # tran.commit()
        except:
            ss=u'%s'%(_(u"退卡失败"))
            # tran.rollback()
            #import traceback;traceback.print_exc()

    else:
        ss=u'%s'%(_(u"卡号不存在"))
    return ss
#zkecopro
#@tran.commit_manually
# @tran.atomic
def SaveOpReim(request,dataModel):

    ss=''
    money=Decimal(request.GET.get('money',0))
    keys=request.POST.getlist("K")
    objcards=dataModel.objects.filter(pk__in = keys)
    for obj in objcards:
        objcard=[obj]
        if objcard[0].card_privage == PRIVAGE_CARD:
            ss=u'%s'%(_(u"管理卡，操作失败"))
        if objcard[0].cardstatus == CARD_LOST:
            ss=u'%s'%(_(u"该卡已经挂失，操作失败"))
        if objcard[0].cardstatus ==CARD_STOP:
            ss=u'%s'%(_(u"该卡已停用，操作失败"))
        if objcard[0].cardstatus ==CARD_INVALID:
            ss=u'%s'%(_(u"该卡已失效，操作失败"))
        if int(money)<0:
            ss=u'%s'%(_(u"退款金额不能为负数"))
        if int(money) == 0:
            ss=u'%s'%(_(u"退款金额不能为零"))
        #from mysite.pos.posdevview import read_timebrush
        #objbatch = read_timebrush(card)
        #if objbatch:
        #    type=objbatch.split(':')[0]
        #    if type=='1':#计时开始
        #        raise Exception(_(u'当前用户计时消费未结账，不能退款'))
        if ss:
            return ss
        newblance = objcard[0].blance - money
        try:
            blance_valid(objcard[0].itype_id,newblance,objcard[0].UserID)#验证余额
        except Exception,e:
            ss=u'%s'%e
            # tran.rollback()
            return ss
        try:
            objcard[0].blance = newblance
            objcard[0].save(force_update=True)
            CardCashSZ(UserID=objcard[0].UserID,
                    dept_id=objcard[0].UserID.DeptID_id,
                    card=objcard[0].cardno,
                    checktime = datetime.datetime.now(),
                    CashType_id=5,#charge type
                    money=money,
                    create_operator=request.user,
                    hide_column=5,blance=objcard[0].blance,log_flag = 2).save(force_insert=True)
            #tran.commit()
        except:
            ss=u'%s'%(_(u"退款失败"))
            # tran.rollback()
            #import traceback;traceback.print_exc()
    # try:
    #       # tran.commit()
    # except:
    #       ss=u'%s'%(_(u"退款失败"))
    #       tran.rollback()
    #       import traceback;traceback.print_exc()
    return ss
#zkecopro
#@tran.commit_manually
#@tran.atomic
def SaveOpUpdateCard(request,dataModel):
    ss=''
    cardtype=request.GET.get('cardtype',1)
    keys=request.POST.getlist("K")
    objcards=dataModel.objects.filter(pk__in = keys)
    for obj in objcards:
        objcard=[obj]
        if objcard[0].card_privage == PRIVAGE_CARD:
            ss=u'%s'%(_(u"管理卡，操作失败"))
        try:
            objcard[0].itype_id = cardtype
            objcard[0].save(force_update=True)
            #tran.commit()
        except:
            ss=u'%s'%(_(u"退款失败"))
            #tran.rollback()
            #import traceback;traceback.print_exc()
    #else:
    #       ss=u'%s'%(_(u"卡号不存在"))
    return ss
def trunc(DTime):
    return datetime.datetime(DTime.year,DTime.month,DTime.day,0,0,0)
#zkecopro
#@tran.commit_manually
# @tran.atomic
def SaveOpChangeCard(request,dataModel):
    ss=''
    obj=request.POST
    keys=obj.getlist("K")
    card = int(obj['cardno'])
    money = Decimal(obj['blance'])
    money1 = Decimal(obj['card_cost1'])
    objcard=IssueCard.objects.get(pk=keys[0])
    if objcard.cardstatus == CARD_STOP:
        ss=u'%s'%(_(u'该卡已停用，操作失败'))
    if objcard.cardstatus ==CARD_INVALID:
        ss=u'%s'%(_(u"该卡已失效，操作失败"))
    if objcard.UserID.OffDuty == 1:
        ss=u'%s'%(_(u'该人员已经离职，操作失败'))
    if objcard.card_privage == PRIVAGE_CARD:
        ss=u'%s'%(_(u'该卡为管理卡，操作失败'))
    tmpobj = IssueCard.objects.filter(UserID = objcard.UserID,cardstatus__in = [CARD_OVERDUE,CARD_VALID],card_privage = POS_CARD)
    #if tmpobj:
    #   ss=u'%s'%(_(u'该人员已有正在使用的卡,换卡前请先挂失'))
    if  IssueCard.objects.filter(cardno=card,cardstatus=CARD_VALID).count() <> 0:
        ss=u'%s'%(_(u'卡号已使用'))
    orgcard='0'
    try:
        orgcard = str(card)
    except:
        ss=u'%s'%(_(u'卡号不正确'))
    import re
    tmp = re.compile('^[0-9]+$')
    if not tmp.search(orgcard):
        ss=u'%s'%(_(u'卡号不正确'))
    if int(card) == 0:
        ss=u'%s'%(_(u'卡号不能为0'))
    #if objcard.cardstatus == CARD_VALID or objcard.cardstatus==CARD_OVERDUE:
    #    ss=u'%s'%(_(u"请先挂失"))
    if ss!='':
        # tran.rollback()

        return ss

    operate_type = 16#换卡
    itype = objcard.itype_id
    if not itype:
        try:
            tmpobj=ICcard.objects.all()[0]
            itype=tmpobj.id
        except:
            pass

    card_cost = obj['card_cost']
    mng_cost = obj['mng_cost']
    card_privage = objcard.card_privage
    pwd = obj['Password']
    UserID=objcard.UserID
    old_cardno=objcard.cardno

    try:

        newblance=objcard.blance
        objcard.blance = 0
        objcard.cardstatus=CARD_INVALID
        objcard.save(force_update=True)

        CardCashSZ(UserID=objcard.UserID,
                  card=objcard.cardno,
                  dept_id=objcard.UserID.DeptID_id,
                  checktime = datetime.datetime.now(),
                  CashType_id=5,#charge type
                  money=newblance,
                  create_operator=request.user,
                  hide_column=15,blance=0,log_flag = 2).save(force_insert=True)

        if money1 >0 :
            CardCashSZ(UserID=objcard.UserID,
                      card=objcard.cardno,
                      dept_id=objcard.UserID.DeptID_id,
                      checktime = datetime.datetime.now(),
                      CashType_id=4,#charge type
                      money=money1,
                      create_operator=request.user,
                      hide_column=15,blance=0,log_flag = 2).save(force_insert=True)

        obj=IssueCard(UserID = UserID,
                        cardno = int(card),
                        cardstatus = CARD_VALID,
                        card_privage = objcard.card_privage,
                        card_cost = card_cost,
                        mng_cost = mng_cost,
                        create_operator=request.user,                   issuedate=trunc(datetime.datetime.now()),
                        itype_id = itype,blance = money,Password = pwd ).save(force_insert=True,operate_type=operate_type)

        updateCardToEmp(UserID,card)
        ReplenishCard(UserID=UserID,
                           oldcardno=old_cardno,
                           newcardno=card,
                           blance=money).save(force_insert=True)
        # tran.commit()

    except Exception,e:
        # tran.rollback()
        ss=u'%s'%(_(u"换卡失败"))
    return ss


def staDataAllowanceReUpload(request,dataModel):
    batch=request.GET.get('batch','00')
    objs=Allowance.objects.filter(batch=batch,is_pass=1).exclude(is_ok=1)
    devlist=iclock.objects.filter(ProductType__in=[13]).exclude(DelTag=1)

    set_pos_device_info(devlist,objs,'',"SUBSIDYLOG")


def staDataAllowanceBatch(request,dataModel,val):
    keys=request.GET.get("batch")
    devlist=iclock.objects.filter(ProductType__in=[13]).exclude(DelTag=1)
    settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
    datalist=Allowance.objects.filter(batch=keys)
    if datalist:
        for u in datalist:
            if u.is_pass==1:
                ss = _(u'该补贴已经审核')
                return ss
            try:
                if settings.CARDTYPE==1:
                    issuecard=IssueCard.objects.get(UserID = u.UserID,cardstatus = CARD_VALID)
                else:
                    issuecard=IssueCard.objects.get(sys_card_no = u.sys_card_no)
                if issuecard:
                    u.is_pass=val
                    u.pass_name=u'%s'%request.user
                    u.save()
                    if val==1:
                        if settings.CARDTYPE==1:
                            newblan = issuecard.blance+u.money
                            CardCashSZ(UserID=u.UserID,
                                                              card=issuecard.cardno,
                                                              dept_id=u.UserID.DeptID_id,
                                                              checktime=datetime.datetime.now(),
                                                              CashType=CardCashType.objects.get(id=2),#消费类型
                                                              money=u.money,
                                                              hide_column=2,
                                                              blance =newblan,
                                                              create_operator=request.user,log_flag = 2
                                            ).save(force_insert=True)
                            issuecard.blance=newblan
                            issuecard.save(force_update=True)

                        else:
                            set_pos_device_info(devlist,[u],'',"SUBSIDYLOG")
            except Exception,e:
                print "staDataAllowance-----",e
                pass
    else:
        ss = _(u'补贴批次号不存在')
        return ss
    return ''

def deviceLogCheck(sn,starttime,endtime):

    st=starttime#datetime.datetime.now()-datetime.timedelta(days=100)
    et=endtime#datetime.datetime.now()
    pos_data = ICConsumerList.objects.filter(pos_time__gte=st,pos_time__lte=et,dev_sn__exact=sn).exclude(dev_serial_num__isnull=True).values('dev_serial_num').order_by('dev_serial_num')
    item = 0
    data_len = len(pos_data)
    err_log = []
    if data_len>0:
        b = pos_data[0]['dev_serial_num']
        e = pos_data[data_len-1]['dev_serial_num']
        for i in range(b,e):
            if(i!=int(pos_data[item]['dev_serial_num'])):
                item = item-1
                err_log.append(i)
            item = item + 1
        for j in  err_log:
            cmdstr="SYNC POSLOG START=%s\tEND=%s"%(j,j)#固件有BUG，START和END要相等
            saveCmd(sn,cmdstr)
    return err_log
