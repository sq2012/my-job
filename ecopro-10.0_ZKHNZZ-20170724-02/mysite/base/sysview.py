#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response,render
from django.core.exceptions import ObjectDoesNotExist
from exceptions import AttributeError
from django.core.cache import cache
import string,os
import datetime
import time
from mysite.utils import *
from django.contrib.auth.decorators import login_required,permission_required
from django import forms
from mysite.iclock.dataproc import *
from django.utils.encoding import force_unicode, smart_str
#from django.contrib.auth.models import User, Permission
from mysite.iclock.iutils import *
#from iclock.reb	import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
#from django.contrib.auth.models import User

from mysite.iclock.datautils import *
import operator
#from django.template import add_to_builtins
from mysite.auth_code import *
from django.contrib.auth import get_user_model
from mysite.core.menu import *
from mysite.base.models import *
from mysite.iclock.sendmail import SendMail
#add_to_builtins('mysite.iclock.templatetags.iclock_tags')

from mysite.iclock.taskview import upload_data

databases=[{'ENGINE':'mysql','NAME':'zkeco_db','USER':'','PASSWORD':'','HOST':'127.0.0.1','PORT':'83306'},
            {'ENGINE':'sql_server','NAME':'zkeco','USER':'sa','PASSWORD':'',	'HOST':'127.0.0.1','PORT':'1433'},
            {'ENGINE':'oracle','NAME':'zkeco_db','USER':'system','PASSWORD':'ROOT','HOST':'127.0.0.1',	'PORT':'1521'}
            ]
backup_dir="%s/backup/"%settings.APP_HOME
backup_dir.replace("\\\\","/")

opt_save_fields={'users':[{'name':'start_page','mod':'','default':'1'},
                        {'name':'mul_page','mod':'','default':'1'},
                        {'name':'emp_pic','mod':'','default':''},
                        {'name':'rec_pic','mod':'','default':''},{'name':'vis_pic','mod':'','default':''},
                        {'name':'page_limit','mod':'','default':'50'}
            ],

            'basic':[{'name':'sitetitle','mod':'','default':u'%s'%(_(u'武陟县人民政府云考勤平台'))},
                        {'name':'homeurl','mod':'','default':'0'},{'name':'enroll','mod':'uru','default':'0'},
                        {'name':'algversion','mod':'uru','default':'1'},{'name':'udisk','mod':'udisk','default':''},
                        {'name':'sms','mod':'sms','default':'0'},{'name':'dev_auto','mod':'','default':'1'},
                        {'name':'emp_pic','mod':'','default':'0'},
                        {'name':'self_login','mod':'','default':'0'},
                        {'name':'new_record','mod':'','default':'0'},
            {'name':'expanddept','mod':'','default':'1'},
            {'name':'Auto_audit','mod':'','default':'0'},
            #{'name':'backup_dir','mod':'','default':backup_dir},
            {'name':'lock_date','mod':'','default':'0'},{'name':'check_mins','mod':'','default':'10'},
            {'name':'show_login','mod':'','default':'0'},
            {'name':'Auto_iclock','mod':'','default':'0'},
            {'name':'Auto_logs','mod':'','default':'0'},
            {'name':'Auto_del_iclock','mod':'','default':'0'},
            {'name':'noverifypwd','mod':'','default':'0'},
            {'name':'noeditcard','mod':'','default':'0'},
            {'name':'sendempphoto','mod':'','default':'0'},
            {'name':'onlyshow_salemod','mod':'','default':'0'},
            {'name':'checkinouttype','mod':'','default':'0'}],
        'email':[{'name':'smtpserver','mod':'','default':''},{'name':'authorized','mod':'','default':''},{'name':'smtp_user','mod':'','default':''},{'name':'smtp_pass','mod':'','default':''},{'name':'forgot','mod':'','default':''},{'name':'exceptionemail','mod':'','default':''},
            {'name':'l_mail','mod':'','default':''},{'name':'rec_mail','mod':'','default':''},{'name':'usessl','mod':'','default':'1'}],
        'delolddata':[{'name':'devcmds','mod':'','default':'5'},{'name':'devlog','mod':'','default':'10'},{'name':'oplog','mod':'','default':'10'},{'name':'checkinout','mod':'','default':'0'}],
        'datasync':[{'name':'issync','mod':'','default':'0'},{'name':'authtype','mod':'','default':'0'},{'name':'authip','mod':'','default':''},
            {'name':'authuser','mod':'','default':''},{'name':'authpass','mod':'','default':''},{'name':'authtime','mod':'','default':'00:00-23:59'},
            {'name':'authkey','mod':'','default':'DESCRYPT'},{'name':'token','mod':'','default':''},],
        'app':[{'name':'distance','default':200,'mod':'att'},{'name':'checkin','default':'1','mod':'att'},
            {'name':'wifi','default':'0','mod':'att'},{'name':'face','default':'0','mod':'att'},
            {'name':'speday','default':'1','mod':'att'},{'name':'review','default':'1','mod':'att'},

            ]



    }


home_url=[{'url':'/iclock/homepage/showHomepage/','title':u"%s"%_("Comprehensive information page")},
{'url':'/iclock/data/iclock/','title':u"%s"%_("Device Maintenance")},
{'url':'/iclock/data/_checkoplog_','title':u"%s"%_("Transaction Monitor")},{'url':'/iclock/data/employee/','title':u"%s"%_('Employee Maintenance')},
{'url':'/iclock/data/transactions/','title':u"%s"%_("transaction")},
{'url':'/iclock/data/department/','title':u"%s"%_("Department Maintenance")},
{'url':'/iclock/data/USER_SPEDAY/','title':u"%s"%_("Employee's Leave")},
{'url':'/iclock/att/reports/','title':u"%s"%_('Reports')}
]

auth_type=[{'authtype':0,'title':u"%s"%_(u"不需要验证")},{'authtype':1,'title':u"%s"%_(u"仅验证IP")},{'authtype':2,'title':u"%s"%_(u"DES算法验证用户名和密码")}]

def getDefaultValue_opt_save_fields(title,subtitle):
    global opt_save_fields
    l=opt_save_fields[title]
    for d in l:
        if d['name']==subtitle:
            return d['default']
    return ""


def restartTimer():
    svrName='AttServer'
    #try:
    #	os.system("cmd /C %s/%s"%(settings.FILEPATH,'iclockserver.exe -b 1'))
    #except:
    #	pass
    # try:
    # 	os.system("cmd /C net stop %s & net start %s"%(svrName, svrName))
    # except:
    # 	pass
    cache.set(settings.UNIT+'_job',1,timeout=600)


@login_required
def sysList(request, ModelName):
    if request.method=='POST':
        if ModelName=='upload':
            u=GetParamValue('opt_basic_udisk','0')
            if u=='0':
                return getJSResponse({"ret":0,"message": u"%s"%_("The server is not installed U-disk data import module!")},mtype="text/html")
            return upload_data(request)
        elif ModelName=='test_send_email':
            toaddr = []
            to_addr = request.POST.get('toaddr')
            toaddr.append(to_addr)
            try:
                time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                mail = SendMail(unicode(_(u'时间&安全精细化管理平台')), 'email/testEmailMessage.html',
                                {'time': time, 'sitetitle': unicode(_(u'时间&安全精细化管理平台')),'username':request.user.username}, toaddr,
                                from_addr_name=GetParamValue('opt_email_smtp_user', ''))
                mail.send_mail()
                return getJSResponse({"ret": 0, "message": u"发送测试邮件成功，请进入收件邮箱查看"})
            except Exception, e:
                import traceback;traceback.print_exc()
                return getJSResponse({"ret": 1, "message": u"邮件服务器或邮箱身份验证不正确或收件箱不正确，发送失败"})

        elif ModelName=='saveHome':
            s_url=request.POST.get('url','')
            mod_name=request.GET.get('mod_name','')
            tab_name=request.GET.get('tab','')[4:]
            caption=unquote(request.GET.get('caption',''))
            s_url=u"%s|||%s|||%s"%(tab_name,caption,s_url)
            SetParamValue('opt_users_homeurl',s_url,"%s-%d"%(mod_name, request.user.id))
            #cache.set("%s_%s_%d_%s"%(settings.UNIT, mod_name,request.user.id,'opt_user_homeurl'),s_url)
            return getJSResponse({"ret":0,"message":u"%s" % _('Save Success')})


        elif ModelName=='database':   #save database settings
            return SaveDatabaseCFG(request)
        elif ModelName=='options':
            action=request.GET.get('action')
            if action=='get_status_rec':
                return get_status_record(request)
            if action=='delete':
                keys=request.POST.getlist("K")
                if keys:
                    for k in keys:
                        pName='opt_check_'+k
                        attparam = AttParam.objects.filter(ParaName=pName,ParaType='1')
                        if attparam:
                            DelParamValue(pName,'1')
                            return getJSResponse({"ret":0,"message":u"删除成功！"})
                        else:
                            return getJSResponse({"ret":0,"message":u"系统初始化数据，不能删除！"})
                else:
                    return getJSResponse({"ret":0,"message":u"请选择要删除的对象！"})
                #return getJSResponse({"ret":0,"message":u"%s"%(_('Save Successful!'))})
            return SaveOptions(request,action)
        elif ModelName=='option_deldata':
            auto_deldata=loads(request.POST.get('ItemData'))
            trans_day=int(request.POST.get('trans_day','0'))
            photo_day=int(request.POST.get('photo_day','0'))
            if trans_day>31 or photo_day>31:
                return getJSResponse({"ret":1,"message":u"%s"%(_(u'请输入1-31'))})
            _data={
                'trans_day':trans_day,
                'photo_day':photo_day
            }
            SetParamValue('day_deldata',dumps1(_data),'tasks')
            for t in auto_deldata['items']:
                del t['name']
            SetParamValue('auto_deldata',dumps1(auto_deldata),'tasks')
            restartTimer()
            return getJSResponse({"ret":0,"message":u"%s"%(_('Save Successful!'))})
        elif ModelName=='option_calcdata':
            is_=request.POST.get('auto_',0)
            st=request.POST.get('start_date','')
            stt=request.POST.get('start_time','')
            if is_=='on':is_=1
            auto_calcdata={
                'is_':is_,#是否启用
                'st':st,#开始启用日期
                'stt':stt,#统计开始时间
            }



            SetParamValue('auto_calcdata',dumps1(auto_calcdata),'tasks')
            restartTimer()

            return getJSResponse({"ret":0,"message":u"%s"%(_('Save Successful!'))})
        elif ModelName=='option_api':
            is_=request.POST.get('auto_',0)
            st=request.POST.get('start_date','')
            user=request.POST.get('user','')
            password=request.POST.get('pass','')
            if is_=='on':is_=1
            auto_calcdata={
                'is_':is_,#是否启用
                'st':st,#开始启用日期
                'user':user,
                'pass':password,
            }



            SetParamValue('api_sycndata',dumps1(auto_calcdata),'tasks')
            restartTimer()

            return getJSResponse({"ret":0,"message":u"%s"%(_('Save Successful!'))})

        elif ModelName=='option_key':#不走此处
            pass_key=request.POST.get('key','')
            if pass_key:
                data=GetParamValue('ipos_params','','ipos')
                data_key=''
                if data:
                    from mysite.auth_code import auth_code
                    data=loads(auth_code(data.encode("gb18030")))
                    data_key=data['pass_key']
                if not data_key:
                    return getJSResponse({"ret":1,"message":u"%s"%(_(u'请先保存证书key'))})

                if data_key!=pass_key:
                    return getJSResponse({"ret":1,"message":u"%s"%(_(u'提交key与保存的key不一样'))})

            else:
                    return getJSResponse({"ret":1,"message":u"%s"%(_(u'证书key不能为空'))})
            from mysite.auth_code import zk_encrypt

            fn=u"%stemp/%s"%(settings.ADDITION_FILE_ROOT,'issonline.zk')
            url=u"/iclock/file/temp/%s"%'issonline.zk'
            buf=zk_encrypt(pass_key,'zkteco')
            out_buf=str(binascii.b2a_hex(buf)).upper()
            f=file(fn,'wb')
            f.write(out_buf)
            f.close()


            return getJSResponse({"ret":0,"message":url})



        elif ModelName=='option_acc':
            is_=request.POST.get('open_pass',0)
            if is_=='on':is_=1
            auto_calcdata={
                'is_':is_,#是否启用
            }
            SetParamValue('acc_param',dumps1(auto_calcdata),'acc')

            return getJSResponse({"ret":0,"message":u"%s"%(_('Save Successful!'))})
        elif ModelName=='option_ipos':
            itype=request.POST.get('cardtype',2)
            max_money=request.POST.get('max_money','0')
            main_area=int(request.POST.get('main_area','1'))
            minor_area=main_area+1
            sys_pwd=request.POST.get('pass','1')
            card_cost=request.POST.get('card_cost',0)
            mng_cost=request.POST.get('mng_cost',0)
            pass_key=request.POST.get('pass_key','')
            from mysite.ipos.models import IssueCard
            #if IssueCard.objects.filter(sys_card_no__isnull=False).count() > 0:
            #	return getJSResponse({"ret":0,"message":u"%s"%(_(u'保存失败!因为卡密码已被使用，不允许修改'))})


            _data={
                'itype':itype,#卡类型
                'max_money':max_money,#卡最大余额
                'main':main_area,#主扇区
                #'minor':minor_area,#次扇区
                'pwd':sys_pwd,#系统密码
                'card_cost':card_cost,#卡成本费
                'mng_cost':mng_cost,#卡管理费
                'pass_key':pass_key
            }
            from mysite.auth_code import auth_code
            data=auth_code(dumps1(_data),'ENCODE')
            SetParamValue('ipos_params',data,'ipos')
            SetParamValue('ipos_cardtype',itype,'ipos')#此句的作用为了访问时方便
            settings.CARDTYPE=int(itype)
            from mysite.core.cmdproc import set_pos_param
            if settings.CARDTYPE==2:
                set_pos_param()
            return getJSResponse({"ret":0,"message":u"%s"%(_('Save Successful!'))})
        elif 	ModelName=='option_sap_ftp':
            _data={
                'SAPhost':request.POST.get('SAPhost',''),
                'SAPuser':request.POST.get('SAPuser',''),
                'SAPpassword':request.POST.get('SAPpassword',''),
                'SAPemp_path':request.POST.get('SAPemp_path',''),
                'SAPsch_path':request.POST.get('SAPsch_path',''),
                'SAPtrans_path':request.POST.get('SAPtrans_path',''),
                'hour':request.POST.get('hour',''),
                'week_hour':request.POST.get('week_hour','')

            }
            SetParamValue('sap_ftp',dumps1(_data),'sap')
            _data={
                'interval':request.POST.get('interval',0),
                'emails':request.POST.get('emails','')

            }
            SetParamValue('sap_email',dumps1(_data),'sap')


            restartTimer()

            return getJSResponse({"ret":0,"message":u"%s"%(_('Save Successful!'))})
    elif request.method=='GET':
        cc={}
        if ModelName=='database':
            return render_database(request,ModelName)

        elif ModelName=='option_key':
            from mysite.auth_code import zk_encrypt
            data=GetParamValue('ipos_params','','ipos')
            data_key=''
            response = HttpResponse()
            response['mimetype'] ='application/octet-stream'
            response['Content-Disposition'] = 'attachment; filename=%s'%("issonline.zk")
            if data:
                from mysite.auth_code import auth_code
                data=loads(auth_code(data.encode("gb18030")))
                data_key=data['pass_key']

                fn=u"%stemp/%s"%(settings.ADDITION_FILE_ROOT,'issonline.zk')
                url=u"/iclock/file/temp/%s"%'issonline.zk'
                buf=zk_encrypt(data_key,'zkteco')
                out_buf=str(binascii.b2a_hex(buf)).upper()
                #f=file(fn,'wb')
                #f.write(out_buf)
                #f.close()

                response.write(out_buf)
            return response


        elif ModelName=='options':
            return render_options(request,ModelName)
        elif ModelName=='option_deldata':
            tmpFile='base/'+ModelName+'.html'
            tmpFile=request.GET.get('t', tmpFile)
            dDict={1:u"%s"%(_(u'服务器下发命令日志')),2:u"%s"%(_(u'设备上传数据日志')),3:u"%s"%(_(u'管理员操作日志')),4:u"%s"%(_(u'设备操作日志')),5:u"%s"%(_(u'考勤记录')),6:u"%s"%(_(u'考勤照片'))}
            auto_deldata=loads(GetParamValue('auto_deldata','{}','tasks'))
            if not auto_deldata:
                auto_deldata={
                    'is_':1,#是否启用
                    'st':datetime.datetime.now().strftime('%Y-%m-%d'),#开始启用日期
                    'items':[
                        {'id':1,'days':10},
                        {'id':2,'days':30},
                        {'id':3,'days':0},
                        {'id':4,'days':0},
                        {'id':5,'days':0},
                        {'id':6,'days':0}
                    ]
                }
            for t in auto_deldata['items']:
                t['name']=dDict[t['id']]

            cc={}
            cc['params']=dumps1(auto_deldata)
            _data=loads(GetParamValue('day_deldata','{}','tasks'))
            if not _data:
                cc['trans_day']=0
                cc['photo_day']=0
            else:
                cc['trans_day']=_data['trans_day']
                cc['photo_day']=_data['photo_day']


            #return render(request,tmpFile,cc)#render_to_response(tmpFile, cc,RequestContext(request, {}))

        elif ModelName=='option_calc':#统计任务
            tmpFile='base/'+ModelName+'.html'
            tmpFile=request.GET.get('t', tmpFile)
            auto_calcdata=loads(GetParamValue('auto_calcdata','{}','tasks'))
            if not auto_calcdata:
                auto_calcdata={
                    'is_':0,#是否启用
                    'st':datetime.datetime.now().strftime('%Y-%m-%d'),#开始启用日期
                    'stt':'02:00',#统计开始时间
                }
            cc={}
            cc['params']=dumps1(auto_calcdata)



            #return render(request,tmpFile,cc)#render_to_response(tmpFile, cc,RequestContext(request, {}))

        elif ModelName=='option_api':#数据对接
            tmpFile='base/'+ModelName+'.html'
            tmpFile=request.GET.get('t', tmpFile)
            data=loads(GetParamValue('api_sycndata','{}','tasks'))
            if not data:
                data={
                    'is_':0,#是否启用
                    'st':'00:00-23:59',
                    'user':'admin',
                    'pass':'12345678',
                }
            cc={}
            cc['params']=dumps1(data)
            #return render(request,tmpFile,cc)#render_to_response(tmpFile, cc,RequestContext(request, {}))
        elif ModelName=='option_acc_open':#数据对接
            tmpFile='base/'+ModelName+'.html'
            tmpFile=request.GET.get('t', tmpFile)
            data=loads(GetParamValue('acc_param','{}','acc'))
            if not data:
                data={
                    'is_':0,#是否启用
                }
            cc={}
            cc['params']=dumps1(data)
            #return render(request,tmpFile,cc)#render_to_response(tmpFile, cc,RequestContext(request, {}))
        elif ModelName=='option_sap_ftp':
            tmpFile='base/'+ModelName+'.html'
            tmpFile=request.GET.get('t', tmpFile)
            data=loads(GetParamValue('sap_ftp','{}','sap'))
            if not data:
                _data={
                    'SAPemp_path':'/emp',
                    'SAPsch_path':'/sch',
                    'SAPtrans_path':'/trans',
                    'hour':'04:30',
                    'week_hour':'10:00'
                }
            else:
                _data=data
            cc=_data.copy()
            _data=loads(GetParamValue('sap_email','{}','sap'))
            if not _data:
                cc['interval']=0
                cc['emails']=''
            else:
                cc['interval']=_data['interval']
                cc['emails']=_data['emails']


            #return render(request,tmpFile,cc)#render_to_response(tmpFile, cc,RequestContext(request, {}))

        elif ModelName=='option_ipos':#消费参数,对保存的数据加密处理
            tmpFile='base/'+ModelName+'.html'
            tmpFile=request.GET.get('t', tmpFile)
            data=GetParamValue('ipos_params','','ipos')
            settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
            from mysite.ipos.models import IssueCard
            rec = IssueCard.objects.all().count()
            if not data:
                data={
                    'itype':settings.CARDTYPE,#0=未知  1=ID  2=IC
                    'max_money':'999',#卡最大余额
                    'main':1,#主扇区
                    'minor':u'%s'%(_(u'第2扇区')),#次扇区
                    'pwd':'',#系统密码
                    'pass_key':''
                }
            else:
                from mysite.auth_code import auth_code
                data=loads(auth_code(data.encode("gb18030")))
                data['minor']=_(u'第%s扇区')%(int(data['main'])+1)
                data['itype']=settings.CARDTYPE
            cc={}
            cc['params']=dumps1(data)
            if rec:
                cc['has_card'] = 1
            else:
                cc['has_card'] = 0
            #return render(request,tmpFile,cc)#render_to_response(tmpFile, cc,RequestContext(request, {}))

        elif ModelName in ['option_users','option_basic','option_email','option_state','option_app','option_devices']:
            tmpFile='base/'+ModelName+'.html'
            tmpFile=request.GET.get('t', tmpFile)
            #from mysite.acc.models import  records
            try:
                    cc={}
                    for k in opt_save_fields.keys():
                        cc[k]={}

                        for kk in opt_save_fields[k]:
                            pName='opt_'+k+'_'+kk['name']
                            if kk['mod'] and (not (kk['mod'] in settings.ENABLED_MOD)):
                                kkk='-1'#不在定义的模块里返回-1,前端不显示
                            else:
                                if pName in ['opt_users_vis_pic','opt_users_start_page','opt_users_mul_page','opt_users_rec_pic','opt_users_page_limit']:
                                    kkk=GetParamValue(pName,kk['default'],str(request.user.id))
                                else:
                                    kkk=GetParamValue(pName,kk['default'])
                                    #print pName,kkk,kk['default']
                                if kkk=='on':
                                    kkk='1'
                            cc[k][kk['name']]=kkk
                        cc[k]=dumps1(cc[k])

                #cc['HOME_URL']=dumps1(home_url)
                #cc['AUTH_TYPE']=dumps1(auth_type)
                #return render(request,tmpFile,cc)#render_to_response(tmpFile, cc,RequestContext(request, {}))

            except Exception,e:
                #import traceback;traceback.print_exc()
                return render(request,"info.html", {"title":  u"%s"%_("Error"), "content": u"%s"%_("render to response error %s")%(e)})
        else:
            tmpFile='base/'+ModelName+'.html'
            tmpFile=request.GET.get('t', tmpFile)
            cc={}
        return render(request,tmpFile, cc)#render_to_response(tmpFile, cc,RequestContext(request, {}))

def Connection_DB(db):
    try:
        from django.db.utils import ConnectionHandler, ConnectionRouter, load_backend, DEFAULT_DB_ALIAS, DatabaseError, IntegrityError
        backend = load_backend(db['ENGINE'])
        conn = backend.DatabaseWrapper(db, 'test')
        cursor = conn.cursor()
        cursor.execute('select count(*) from attparam')
    except Exception,e:
        str="%s"%e
        if 'attparam' in str:
            return 1,u"%s"%_("table doesn't exist")
        else:
            return 0,u"%s"%_("Connection Failed")
    return 2,u"%s"%_("Connection Success")


def SaveDatabaseCFG(request):
    global databases
    action=request.POST['action']
    db={'ENGINE':databases[int(request.POST.get('Database_Engine'))]['ENGINE'],
        'NAME':str(request.POST['NAME']),
        'USER':str(request.POST['USER']),
        'PASSWORD':str(request.POST['PASS']),
        'HOST':str(request.POST['HOST']),
        'PORT':str(request.POST['PORT']),
        'OPTIONS':{}
        }
    re,info=Connection_DB(db)
    if action=='save':
        if re==1:
            info=u"%s"%_('Save Successful!')+" "+info+u"%s"%_('please run db.bat for creating table manually')+", "+u"%s"%_('Take effect after system reboot')
        elif re==2:
            info=u"%s %s"%(_('Save Successful!'),_('Take effect after system reboot'))
        elif re==0:
            info=u"%s %s"%(_('Save Failed!'),info)
        if re>0:
            settings.CFG.DATABASE.ENGINE=db['ENGINE']
            settings.CFG.DATABASE.NAME=db['NAME']
            settings.CFG.DATABASE.USER=db['USER']
            settings.CFG.DATABASE.PASSWORD=db['PASSWORD']
            settings.CFG.DATABASE.HOST=db['HOST']
            settings.CFG.DATABASE.PORT=db['PORT']
            settings.CFG.save()
            return getJSResponse({"ret":0,"message":info})
        else:
            return getJSResponse({"ret":1,"message":info})
    elif action=="connect":
        if re==1:
            info=u"%s"%(_('Connection Successful!'))+" "+info
        if re>0:
            return getJSResponse({"ret":0,"message":info})
        else:
            return getJSResponse({"ret":1,"message":info})

def render_database(request,ModelName):
    global databases
    tmpFile=ModelName+'_sys.html'
    tmpFile=request.GET.get('t', tmpFile)
    try:
        cc={
        'Database':{
        'ENGINE':settings.DATABASE_ENGINE,
        'NAME':settings.DATABASE_NAME,
        'USER':settings.DATABASE_USER,
        'PASSWORD':settings.DATABASE_PASSWORD,
        'HOST':settings.DATABASE_HOST,
        'PORT':settings.DATABASE_PORT
        },
        'DATABASES':databases
    }
        return render(request,tmpFile, cc)
    except Exception,e:
        return render_to_response("info.html", {"title":  _("Error"), "content": _("render to response error %s")%(e)})

def render_options(request,ModelName):
    global opt_save_fields
    global home_url
    tmpFile='base/'+ModelName+'_sys.html'
    tmpFile=request.GET.get('t', tmpFile)
    try:
        sub_menu='"%s"'%createmenu(request,'options')
        cc={}
        cc['sub_menu']=sub_menu

        #print sub_menu
        return render(request,tmpFile,cc)#render_to_response(tmpFile,cc,RequestContext(request, {}))
    except Exception,e:
        return render_to_response("info.html", {"title":  _("Error"), "content": _("render to response error %s")%(e)})




def SaveOptions(request,action):
    global opt_save_fields
    try:
        is_restart = 0
        if action == 'email':
            is_restart = 1

        if action=='status':
            o_pName=request.POST.get('old_option_value','')
            id=request.POST.get('id','10')
            id=id.split('_')[0]
            if o_pName!='':
                o_pName='opt_check_'+id+'_'+o_pName
                DelParamValue(o_pName,'0')
                DelParamValue(o_pName,'1')
            v=request.POST.get('option_title')
            pName='opt_check_'+id+'_'+request.POST.get('option_value')
            if not v or not request.POST.get('option_value'):
                return getJSResponse({"ret":1,"message":u"%s"%(_(u'名称和值不能为空!'))})
            cache.delete("%s_%s"%(settings.UNIT, 'all_record_states'))
            if int(id) in range(len(ATTSTATES)+11):
                SetParamValue(pName,v,'0')
            else:
                SetParamValue(pName,v,'1')
            settings.KEY_STATES={}
            InitStatus()
        elif action=='Single':
            v=request.POST.get('opt_basic_approval',0)
            if v=='on':v='1'     #add by wjz
            SetParamValue('opt_basic_approval',v)
        else:
            for k in opt_save_fields[action]:
                pName='opt_'+action+'_'+k['name']
                if k['name'] in request.POST.keys():
                    v=request.POST.get(k['name'])
                    if v=='on':v='1'     #add by wjz

                    if k['name'] in ['vis_pic','start_page','mul_page','rec_pic','page_limit']:
                        #v=home_url[int(request.POST.get(k['name']))]['url']
                        SetParamValue(pName,v,str(request.user.id))
                    elif k['name']=='self_login':
                        try:
                            User=get_user_model()
                            if User.objects.filter(username='employee').count()==0:#重复保存支持员工自助登录由于约束造成参数存储不上
                                User.objects.create_user('employee', 'test2werer@example.com', '@!45&*%$(#^*!testpw')
                        except Exception,e:
                            print "=========",e
                        SetParamValue(pName,v,'')
                    elif k['name']=='token':
                        authuser=request.POST.get('authuser')
                        authpass=request.POST.get('authpass')
                        authkey=request.POST.get('authkey')
                        data="%s"%authuser+','+authpass
                        if  authuser and authpass:
                            kdes = auth_code(data,'ENCODE',key=authkey)
                            SetParamValue(pName,kdes,'')
                    elif k['name']=='Auto_logs':
                        v1=GetParamValue(pName,'0')
                        SetParamValue(pName,v)
                        if v1!=v:
                            is_restart=1
                    elif k['name']=='Auto_iclock':
                        v1=GetParamValue(pName,'0')
                        SetParamValue(pName,v)
                        if v1!=v:
                            is_restart=1

                    else:
                        SetParamValue(pName,v)
                else:
                    if k['name']=='self_login':
                        try:
                            User=get_user_model()
                            d=User.objects.filter(username='employee')
                            d.delete()
                        except  Exception, e:
                            print "SaveOptions==",e
                        SetParamValue(pName,'0')

                    elif k['name']=='Auto_logs':
                        v1=GetParamValue(pName,'0')
                        if v1!='0':
                            is_restart=1
                        SetParamValue(pName,'0')
                    elif k['name']=='Auto_iclock':
                        v1=GetParamValue(pName,'0')
                        if v1!='0':
                            is_restart=1
                        SetParamValue(pName,'0')

                    elif k['name'] in ['vis_pic','start_page','mul_page','rec_pic']:
                        v1=GetParamValue(pName,'0',request.user.id)


                        SetParamValue(pName,'0',request.user.id)
                    else:
                        SetParamValue(pName,'0')
            if is_restart==1:
                restartTimer()
                #cache.set(settings.UNIT+'_job',1,timeout=600)

    except Exception,e:
        return getJSResponse({"ret":1,"message":u"%s--%s"%(_('Save Failed!'),e)})
        #DelParamValue(pName)
    return getJSResponse({"ret":0,"message":u"%s"%(_('Save Successful!'))})

def get_status_record(request):
    allstat=GetRecordStatus()
    #print "============",allstat           #此句不要注释,不知为什么不用此句在IE下显示不出来
    rowl=[]
    dd={}
    for d in allstat:
        dd['ItemName']=u'%s'%d['pName']
        dd['Value']=u'%s'%d['pValue']
        if d['id']<100:
            dd['id']=u'%s'%d['id']
        else:
            dd['id']=str(d['id'])+'_'+d['pValue']

        rowl.append(dd.copy())
    cc={'page':1,'total':len(rowl),'records':len(rowl),'rows':rowl}
    #print cc
    #cc="{"+""""page":"""+str(1)+","+""""total":"""+str(1)+","+""""records":"""+str(len(rowl))+","+""""rows":"""+dumps(rowl)+"""}"""
    #print "222222222",cc
    return getJSResponse(cc)
