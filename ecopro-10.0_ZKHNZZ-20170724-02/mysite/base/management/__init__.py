#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models, connection,router
from django.db.models import signals
#from django.contrib.auth.models import create_superuser
from django.contrib.auth import (models as auth_app, get_permission_codename,
    get_user_model)
from mysite.base.models import *
from mysite.iclock.models import *
from mysite.meeting.models import *
from mysite.acc.models import *
from django.db.models.fields import NOT_PROVIDED
from django.core.cache import cache

from mysite.ipos.models import *
from django.utils.translation import ugettext_lazy as _
from datetime import time
from django.conf import settings
from django.apps import apps



#初次建立数据库时需要实现的通过如下函数实现
def upgradeDB():
    dbVer=int(GetParamValue('ADMSDBVersion',100))
    if dbVer==-10000:return

    sqls=(
    "ALTER TABLE userinfo ADD AutoSchPlan int NULL",
    "ALTER TABLE userinfo ADD MinAutoSchInterval int NULL",
    "ALTER TABLE userinfo ADD RegisterOT int NULL",
    "ALTER TABLE userinfo ADD Image_id int NULL",
    "ALTER TABLE SchClass ADD WorkDay int NULL",
    "ALTER TABLE iclock ADD PhotoStamp varchar(20) NULL",
    "ALTER TABLE iclock ADD FWVersion varchar(30) NULL",
    "ALTER TABLE iclock ADD FPCount varchar(10) NULL",
    "ALTER TABLE iclock ADD TransactionCount varchar(10) NULL",
    "ALTER TABLE iclock ADD UserCount varchar(10) NULL",
    "ALTER TABLE iclock ADD MainTime varchar(20) NULL",
    "ALTER TABLE iclock ADD MaxFingerCount int NULL",
    "ALTER TABLE iclock ADD MaxAttLogCount int NULL",
    "ALTER TABLE iclock ADD DeviceName varchar(30) NULL",
    "ALTER TABLE iclock ADD AlgVer varchar(30) NULL",
    "ALTER TABLE iclock ADD FlashSize varchar(10) NULL",
    "ALTER TABLE iclock ADD FreeFlashSize varchar(10) NULL",
    "ALTER TABLE iclock ADD Language varchar(30) NULL",
    "ALTER TABLE iclock ADD VOLUME varchar(10) NULL",
    "ALTER TABLE iclock ADD DtFmt varchar(10) NULL",
    "ALTER TABLE iclock ADD IPAddress varchar(20) NULL",
    "ALTER TABLE iclock ADD IsTFT varchar(5) NULL",
    "ALTER TABLE iclock ADD Platform varchar(20) NULL",
    "ALTER TABLE iclock ADD Brightness varchar(5) NULL",
    "ALTER TABLE iclock ADD BackupDev varchar(30) NULL",
    "ALTER TABLE iclock ADD OEMVendor varchar(30) NULL",
    "ALTER TABLE iclock ADD AccFun int NOT NULL DEFAULT 0",
    "ALTER TABLE iclock ADD TZAdj int NOT NULL DEFAULT 8",
    "ALTER TABLE checkinout ADD WorkCode VARCHAR(20) NULL",
    "ALTER TABLE checkinout ADD Reserved VARCHAR(20) NULL",
    "ALTER TABLE iclock DROP COLUMN CheckInterval")
    #batchSql(sqls)
    #from mysite.iclock.modpin import checkPINWidth
    #checkPINWidth()

    if dbVer<105 and dbVer>0:
        ct=ContentType.objects.get_for_model(USER_SPEDAY)
        cname='user-defined report'
        cn='definedReport_'+USER_SPEDAY.__name__.lower()
        tryAddPermission(ct, cn, cname)

    if dbVer<205 and dbVer>0:
        sqls=("delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('import_employee'),
            "delete from auth_permission where codename='%s'"%('import_employee'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('optionsDatabase_employee'),
            "delete from auth_permission where codename='%s'"%('optionsDatabase_employee'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('clearObsoleteData_transaction'),
            "delete from auth_permission where codename='%s'"%('clearObsoleteData_transaction'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('init_database'),
            "delete from auth_permission where codename='%s'"%('init_database'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_user_temp_sch'),
            "delete from auth_permission where codename='%s'"%('add_user_temp_sch'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_useracprivilege'),
            "delete from auth_permission where codename='%s'"%('change_useracprivilege'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('AuditedTrans_transaction'),
            "delete from auth_permission where codename='%s'"%('AuditedTrans_transaction'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('definedReport_itemdefine'),
            "delete from auth_permission where codename='%s'"%('definedReport_itemdefine'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('upgradefw_iclock'),
            "delete from auth_permission where codename='%s'"%('upgradefw_iclock'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('copyudata_iclock'),
            "delete from auth_permission where codename='%s'"%('copyudata_iclock'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('resetPwd_iclock'),
            "delete from auth_permission where codename='%s'"%('resetPwd_iclock'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('restoreData_iclock'),
            "delete from auth_permission where codename='%s'"%('restoreData_iclock'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_itemdefine'),
            "delete from auth_permission where codename='%s'"%('add_itemdefine'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_itemdefine'),
            "delete from auth_permission where codename='%s'"%('delete_itemdefine'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_itemdefine'),
            "delete from auth_permission where codename='%s'"%('change_itemdefine'),

            )
        batchSql(sqls)
        #checkAndCreateModelPermissions(iclock._meta.app_label)

    if dbVer<505 and dbVer>0:
        sqls=(
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_iaccdevitemdefine'),
            "delete from auth_permission where codename='%s'"%('add_iaccdevitemdefine'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_iaccdevitemdefine'),
            "delete from auth_permission where codename='%s'"%('delete_iaccdevitemdefine'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_iaccdevitemdefine'),
            "delete from auth_permission where codename='%s'"%('change_iaccdevitemdefine'),

            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_iaccempitemdefine'),
            "delete from auth_permission where codename='%s'"%('add_iaccempitemdefine'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_iaccempitemdefine'),
            "delete from auth_permission where codename='%s'"%('delete_iaccempitemdefine'),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_iaccempitemdefine'),
            "delete from auth_permission where codename='%s'"%('change_iaccempitemdefine'),

            )
        batchSql(sqls)

    if dbVer<527 and dbVer>0:
        User=get_user_model()

        sqls=("ALTER TABLE %s ADD emp_pin varchar(30) null"%(User._meta.db_table),
              )
        batchSql(sqls)

        if "mysql" in settings.DATABASE_ENGINE or "oracle" in settings.DATABASE_ENGINE:
            sqls=( "ALTER TABLE %s modify column reserved varchar(40)  NULL"%(transactions._meta.db_table),

                )
        else:
            sqls=(
                "ALTER TABLE %s alter column  reserved varchar(40)  NULL"%(transactions._meta.db_table),
            )
        #batchSql(sqls)





    if dbVer<530:           #更新成最新版本号
        SetParamValue('ADMSDBVersion','530')

def search_object(model, data, append=True):
    for field in data:
        try:
            f = model._meta.get_field(field)
        except:
            continue
        value = data[field]
        if isinstance(f, models.fields.related.ForeignKey):
            if type(value) == type({}): #
                objs = search_object(f.rel.to, value, append)
                value = objs[0]
                data[field] = value
    udata = dict([(k.replace("_id", ""), unicode(v)) for k, v in data.items()])#value需要unicode
    objs = model.objects.filter(**udata)
    if append and len(objs) == 0:
        obj = model(**udata)
        obj.save()
        objs = [obj, ]
    return objs


def check_and_create_model_initial_data(model):
    if not hasattr(model, "Admin"): return
    if not hasattr(model.Admin, "initial_data"): return
    datas = getattr(model.Admin, "initial_data")
    if type(datas) in (list, tuple):
        for data in datas:
            try:
                obj = search_object(model, data, True)
            except:
                print '-----error-----'
                #print_exc()
    elif callable(datas):
        model.Admin().initial_data()

def tryAddPermission(ct, cn, cname):
    try:
        Permission.objects.get(content_type=ct, codename=cn)
    except:
        try:
            Permission(content_type=ct, codename=cn, name=cname).save()
            print "Add permission %s OK"%cn
        except Exception, e:
            print "Add permission %s failed:"%cn, e


def checkAndCreateModelPermission(model):
    ct=ContentType.objects.get_for_model(model)

    cn='browse_'+model.__name__.lower()
    cname='Can browse %s'%model.__name__
    tryAddPermission(ct, cn, cname)
    for perm in model._meta.permissions:
        tryAddPermission(ct, perm[0], perm[1])


def check_and_create_model_default(model):
    return
    #if 'sql_server' in settings.DATABASE_ENGINE.lower():
        #db_table = model._meta.db_table
        #for f in model._meta.fields:
        #    if not (f.default == NOT_PROVIDED):
        #	db_column = f.db_column or f.column
        #	value = "'%s'" % f.get_default()
        #	sql = "ALTER TABLE %s ADD CONSTRAINT default_value_%s_%s DEFAULT %s FOR %s" % (db_table, db_table, db_column, value, db_column)
        #	try:
        #	    customSql(sql)
        #	except:
        #	    pass
        #




def checkAndCreateModelPermissions(app):
    #from django.db.models.loading import get_app
    from django.db import models
    #app=get_app(appName)
        #创建一个超级用户
    User=get_user_model()
    if not User.objects.filter(username="admin"):
        User.objects.create_superuser("admin", "admin")
    for app_config in apps.get_app_configs():
        if app.label!=app_config.label:continue
        #print "====",app.label
        models_list= router.get_migratable_models(app_config, connection.alias, include_auto_created=False)
        for model in models_list:
#			if callable(model) and type(model) not in [type(issubclass), type(checkAndCreateModelPermissions)]:
            try:
                if issubclass(model, models.Model) and not model._meta.abstract:
                    checkAndCreateModelPermission(model)
                    check_and_create_model_default(model)
                    check_and_create_model_initial_data(model)


            except:
                pass
    userDefinePermissions=[
#			       {'ModelName':Group,'codename':'browse_'+Group.__name__.lower(),'name':'Can browse Group'},
#			       {'ModelName':User,'codename':'browse_'+User.__name__.lower(),'name':'Can browse User'},

#			       {'ModelName':accounts,'codename':'browse_'+accounts.__name__.lower(),'name':'Can browse accounts'},
#			       {'ModelName':accounts,'codename':'delete_'+accounts.__name__.lower(),'name':'Can delete accounts'},
#				   {'ModelName':accounts,'codename':'change_'+accounts.__name__.lower(),'name':'Can change accounts'},
#				   {'ModelName':accounts,'codename':'add_'+accounts.__name__.lower(),'name':'Can add accounts'},
                   #{'ModelName':attpriReport,'codename':'browse_'+attpriReport.__name__.lower(),'name':'Can browse attpriReport'},
                   #{'ModelName':attpriReport,'codename':'delete_'+attpriReport.__name__.lower(),'name':'Can delete attpriReport'},
                   #{'ModelName':attpriReport,'codename':'change_'+attpriReport.__name__.lower(),'name':'Can change attpriReport'},
                   #{'ModelName':attpriReport,'codename':'add_'+attpriReport.__name__.lower(),'name':'Can add attpriReport'},

#				   {'ModelName':employee,'codename':'restoreEmpLeave_employee','name':'restore Employee leave'},人员恢复离职
            #           {'ModelName':iclock,'codename':'deptEmptoDev_iclock','name':'Transfer employee of department to the device'},
            #	   {'ModelName':iclock,'codename':'deptEmptoDelete_iclock','name':'Delete employee from the device'},#按部门人员从设备中删除人员
            #	   #{'ModelName':iclock,'codename':'deptEmptmptoDelete_iclock','name':'Delete fingers of employee the device'},#按部门人员从设备中删除人员指纹
            #	   {'ModelName':iclock,'codename':'toDevPic_iclock','name':'toDevPic employee'},#传送人员照片到设备
            #	   {'ModelName':iclock,'codename':'delFingerFromDev_iclock','name':'Delete fingers from the device'},
            #	   {'ModelName':iclock,'codename':'delFaceFromDev_iclock','name':'Delete face from the device'},
            #	   {'ModelName':iclock,'codename':'clearpic_iclock','name':'Clear pictures in device'},

                   #{'ModelName':iclock,'codename':'deptEmpfacetoDelete_iclock','name':'Delete face of employee the device'},#按部门人员从设备中删除人员面部
#			       {'ModelName':employee,'codename':'import_employee','name':'import employee'},人员导入
#			       {'ModelName':transaction,'codename':'AuditedTrans_transaction','name':'Audited Transaction'},考勤记录审核
#			       {'ModelName':ItemDefine,'codename':'definedReport_itemdefine','name':'user-defined report'},自定义报表
                   #{'ModelName':ItemDefine,'codename':'attrecReport_itemdefine','name':'attrecabnormite report'},
                   #{'ModelName':ItemDefine,'codename':'attshiftsReport_itemdefine','name':'attshifts report'},
                   #{'ModelName':ItemDefine,'codename':'attexceptReport_itemdefine','name':'attexception report'},
                   #{'ModelName':ItemDefine,'codename':'attTotalReport_itemdefine','name':'attTotal report'},
                   #{'ModelName':ItemDefine,'codename':'attDailyTotalReport_itemdefine','name':'attDailyTotal report'},
                   #{'ModelName':ItemDefine,'codename':'exceptReport_itemdefine','name':'exception report'},
                   #{'ModelName':ItemDefine,'codename':'leaveReport_itemdefine','name':'Leaves report'},
                   #{'ModelName':ItemDefine,'codename':'OriginalReport_itemdefine','name':'Original report'},
                   #{'ModelName':ItemDefine,'codename':'department_report','name':'department report'},
                   #{'ModelName':transactions,'codename':'Forget_transaction','name':'Forget to clock in and out'},
                   #{'ModelName':ItemDefine,'codename':'reCalcaluteReport_itemdefine','name':'ReCalculate Reports'},
                   #{'ModelName':USER_TEMP_SCH,'codename':'Data_Management','name':'Data Management'},#数据管理
                   #{'ModelName':USER_TEMP_SCH,'codename':'Init_database','name':'Init database'},#初始化系统
                   #{'ModelName':USER_TEMP_SCH,'codename':'Clear_Obsolete_Data','name':'Clear Obsolete Data'},#清除过期数据
                   #{'ModelName':USER_TEMP_SCH,'codename':'Backup_Database','name':'Backup Database'},#备份数据库
                   #{'ModelName':USER_TEMP_SCH,'codename':'import_department_data','name':'import department data'},#导入部门数据
                   #{'ModelName':USER_TEMP_SCH,'codename':'import_employee_data','name':'import employee data'},#导入人员数据
                   #{'ModelName':USER_TEMP_SCH,'codename':'Import_Finger_data','name':'Import Finger data'},#导入指纹数据
                   #{'ModelName':USER_TEMP_SCH,'codename':'U_Disk_Data_Manager','name':'U_Disk Data Manager'},#U盘数据管理
                   #{'ModelName':USER_TEMP_SCH,'codename':'Database_Options','name':'Database Options'},#数据库设置
                   #{'ModelName':USER_TEMP_SCH,'codename':'System_Options','name':'System Options'},#系统设置
                   #{'ModelName':USER_TEMP_SCH,'codename':'preferences_user','name':'user-Preferences'},#自定义显示字段
                   #{'ModelName':USER_TEMP_SCH,'codename':'setprocess','name':'set process'},
                   #{'ModelName':USER_TEMP_SCH,'codename':'user_temp_sch_add','name':'add user_temp_sch'},#系统选项的增加
                   ##{'ModelName':USER_TEMP_SCH,'codename':'user_temp_sch_browse','name':'browse user_temp_sch'},#系统选项的浏览
                   #{'ModelName':USER_TEMP_SCH,'codename':'user_temp_sch_modify','name':'modify user_temp_sch'},#系统选项的修改
                   #{'ModelName':USER_TEMP_SCH,'codename':'user_temp_sch_delete','name':'delete user_temp_sch'},#系统选项删除



                   #{'ModelName':USER_OF_RUN,'codename':'Employee_shift_details','name':'Employee shift details'},
                  # {'ModelName':UserACPrivilege,'codename':'setdevice','name':'Distribution Device'},
                   #{'ModelName':UserACPrivilege,'codename':'Employee_to_device','name':'Employee to device'},
                  # {'ModelName':iclock,'codename':'Upload_Iclock_Photo','name':'Upload Iclock Photo'},
                  # {'ModelName':iclock,'codename':'delDevPic_iclock','name':'delDevPic employee'}#删除设备上的人员照片
                   ]
    #for t in userDefinePermissions:
    #	try:
    #		dataModal=t['ModelName']
    #		ct=ContentType.objects.get_for_model(dataModal)
    #		Permission(content_type=ct, codename=t['codename'], name=t['name']).save()
    #	except:
    #		pass





    #try:
        #ct=ContentType.objects.get_for_model(transaction)
        #Permission(content_type=ct, codename='init_database', name='Init database').save()
    #except: pass
    #try:
        #ct=ContentType.objects.get_for_model(Group)
        #Permission(content_type=ct, codename='browse_'+Group.__name__.lower(), name='Can browse %s'%Group.__name__).save()
    #except: pass
    #try:
        #ct=ContentType.objects.get_for_model(iclock)
        #Permission(content_type=ct, codename='deptEmptoDev_iclock', name='Transfer employee of department to the device').save()
    #except: pass

    #try:
        #ct=ContentType.objects.get_for_model(employee)
        #Permission(content_type=ct, codename='import_employee', name='import employee').save()
    #except: pass
    #try:
        #ct=ContentType.objects.get_for_model(transaction)
        #Permission(content_type=ct, codename='AuditedTrans_transaction', name='Audited Transaction').save()
    #except: pass


#db创建数据库时删除无用的权限
def Delete_unused_permissions():
    sqls=("ALTER TABLE %s ADD verifycode integer "%(attRecAbnormite._meta.db_table),
            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('definedReport_user_speday'),
            "delete from auth_permission where codename='%s'"%('definedReport_user_speday'),

            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('reCalcaluteReport_transaction'),
            "delete from auth_permission where codename='%s'"%('reCalcaluteReport_transaction'),

            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('report_transaction'),
            "delete from auth_permission where codename='%s'"%('report_transaction'),

            "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where name='%s')"%('operate Forget to clock in and out'),
            "delete from auth_permission where name='%s'"%('operate Forget to clock in and out'),
#				"ALTER TABLE %s ADD CmdContentExt varchar(200) NULL"%(devcmds._meta.db_table),
#				"ALTER TABLE %s ADD flag integer "%(devcmds._meta.db_table),
              )
    batchSql(sqls)

    sqls=("delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('import_employee'),
        "delete from auth_permission where codename='%s'"%('import_employee'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('optionsDatabase_employee'),
        "delete from auth_permission where codename='%s'"%('optionsDatabase_employee'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('clearObsoleteData_transaction'),
        "delete from auth_permission where codename='%s'"%('clearObsoleteData_transaction'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('init_database'),
        "delete from auth_permission where codename='%s'"%('init_database'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_user_temp_sch'),
        "delete from auth_permission where codename='%s'"%('add_user_temp_sch'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_user_temp_sch'),
        "delete from auth_permission where codename='%s'"%('delete_user_temp_sch'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_user_temp_sch'),
        "delete from auth_permission where codename='%s'"%('change_user_temp_sch'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_useracprivilege'),
        "delete from auth_permission where codename='%s'"%('change_useracprivilege'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('AuditedTrans_transaction'),
        "delete from auth_permission where codename='%s'"%('AuditedTrans_transaction'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('definedReport_itemdefine'),
        "delete from auth_permission where codename='%s'"%('definedReport_itemdefine'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('upgradefw_iclock'),
        "delete from auth_permission where codename='%s'"%('upgradefw_iclock'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('copyudata_iclock'),
        "delete from auth_permission where codename='%s'"%('copyudata_iclock'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('resetPwd_iclock'),
        "delete from auth_permission where codename='%s'"%('resetPwd_iclock'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('restoreData_iclock'),
        "delete from auth_permission where codename='%s'"%('restoreData_iclock'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_itemdefine'),
        "delete from auth_permission where codename='%s'"%('add_itemdefine'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_itemdefine'),
        "delete from auth_permission where codename='%s'"%('delete_itemdefine'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_itemdefine'),
        "delete from auth_permission where codename='%s'"%('change_itemdefine'),

        )
    batchSql(sqls)


    sqls=(
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_iaccdevitemdefine'),
        "delete from auth_permission where codename='%s'"%('add_iaccdevitemdefine'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_iaccdevitemdefine'),
        "delete from auth_permission where codename='%s'"%('delete_iaccdevitemdefine'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_iaccdevitemdefine'),
        "delete from auth_permission where codename='%s'"%('change_iaccdevitemdefine'),

        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_iaccempitemdefine'),
        "delete from auth_permission where codename='%s'"%('add_iaccempitemdefine'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_iaccempitemdefine'),
        "delete from auth_permission where codename='%s'"%('delete_iaccempitemdefine'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_iaccempitemdefine'),
        "delete from auth_permission where codename='%s'"%('change_iaccempitemdefine'),

        )
    batchSql(sqls)

    sqls=(
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_attparam'),
        "delete from auth_permission where codename='%s'"%('add_attparam'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_attparam'),
        "delete from auth_permission where codename='%s'"%('delete_attparam'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_annual_settings'),
        "delete from auth_permission where codename='%s'"%('add_annual_settings'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_annual_settings'),
        "delete from auth_permission where codename='%s'"%('delete_annual_settings'),
        #"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_annual_settings'),
        #"delete from auth_permission where codename='%s'"%('add_attparam'),
        #"delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('annual_settings'),
        #"delete from auth_permission where codename='%s'"%('delete_attparam'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_employeelog'),
        "delete from auth_permission where codename='%s'"%('change_employeelog'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_employeelog'),
        "delete from auth_permission where codename='%s'"%('add_employeelog'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_adminlog'),
        "delete from auth_permission where codename='%s'"%('add_adminlog'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_adminlog'),
        "delete from auth_permission where codename='%s'"%('change_adminlog'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('browse_user_temp_sch'),
        "delete from auth_permission where codename='%s'"%('browse_user_temp_sch'),

        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('browse_iclockdininghall'),
        "delete from auth_permission where codename='%s'"%('browse_iclockdininghall'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('change_iclockdininghall'),
        "delete from auth_permission where codename='%s'"%('change_iclockdininghall'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('add_iclockdininghall'),
        "delete from auth_permission where codename='%s'"%('add_iclockdininghall'),
        "delete from auth_group_permissions where PERMISSION_ID=(select id from auth_permission where codename='%s')"%('delete_iclockdininghall'),
        "delete from auth_permission where codename='%s'"%('delete_iclockdininghall'),
        )

    batchSql(sqls)
    disable_permisstioins=['add_transactions','change_transactions','add_devcmds','change_devcmds','add_devlog','change_devlog','add_oplog',
                           'change_oplog','change_fptemp','change_facetemp','change_biodata','add_attshifts','change_attshifts','delete_attshifts',
                           'add_itemdefine','change_itemdefine','delete_itemdefine','add_splittime','delete_splittime',
                           'add_batchtime','delete_batchtime','add_meal','delete_meal','add_issuecard','delete_issuecard','change_issuecard',
                           'browse_attcalclog','add_attcalclog','delete_attcalclog','change_attcalclog','browse_iclockdept','delete_iclockdept','change_iclockdept','add_iclockdept','add_records','change_records','delete_records','browse_records','add_empofdevice','change_empofdevice','delete_empofdevice','delete_icconsumerlist']
    sql="delete from auth_permission where codename='%s'"
    sqls=[]
    for t in disable_permisstioins:
        sqls.append(sql%t)

    batchSql(sqls)


def post_syncdb_initdb(sender, **kwargs):
    dbVer=int(GetParamValue('ADMSDBVersion',100))
    if dbVer==-10000:
        print "Create Table Failed!!!"
        return
    #upgradeDB()
    app=sender
    checkAndCreateModelPermissions(app)


    ##db删除无用的权限
    #try:
    #    Delete_unused_permissions()
    #except:
    #    pass



#signals.post_syncdb.disconnect(create_superuser,
#    sender=auth_app, dispatch_uid="django.contrib.auth.management.create_superuser")
signals.post_migrate.connect(post_syncdb_initdb)

