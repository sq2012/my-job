#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.iclock.sendmail import *
from mysite import settings 
import datetime
from django.utils.translation import ugettext_lazy as _
from mysite.base.models import *


def transactionsend():
    timing=settings.timing
    try:
        times=timing.split(":")
        now=datetime.datetime.now()
        h=int(times[0])
        m=int(times[1])
        s=int(times[2])      
    except:
        pass

    paramvalue= GetParamValue("opt_email_rec_mail")
    if paramvalue=="on":
        if now.hour==h and now.second==s and now.minute==m:
            url=""
            mail = SendMail(u"%s"%(_(u'考勤记录预览')),'email/usertransaction.html',{'url':url,"welcome":"",
                    'sitetitle':GetParamValue('opt_basic_sitetitle',u"%s"%_(u'时间&安全精细化管理平台'))},
                    [],from_addr_name=u"%s"%_(u'时间&安全精细化管理平台'))
            mail.loginmail()
            emps=employee.objects.all()
            for emp in emps:
                if emp.email:
                    trans=transactions.objects.filter(UserID=emp,TTime__year=now.year,TTime__month=now.month,TTime__day=now.day)
                    email=[]
                    email.append(emp.email)
                    mail.to_addr=email
                    
                    url=trans
                    mail.context={'url':url,"welcome":u"%s您好：" % emp.EName,
                    'sitetitle':GetParamValue('opt_basic_sitetitle',u"%s"%_(u'时间&安全精细化管理平台'))}
                    try:
                        mail.send_mail_handlogin()
                    except:
                        mail.loginmail()
                        mail.send_mail_handlogin()
            mail.quitmail()

