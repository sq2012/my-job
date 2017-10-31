#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import smtplib, base64
from django.template import loader, Context
from mysite.iclock.iutils import *
from mysite.base.models import GetParamValue

CHARSET = 'utf-8'
#FROM_ADD = GetParamValue('opt_email_smtp_user','')#'xxxxxxxxx@163.com'
#SMTP_SERVER = GetParamValue('opt_email_smtpserver','')#'smtp.163.com'
#SMTP_USER = GetParamValue('opt_email_smtp_user','')
#SMTP_PASS = GetParamValue('opt_email_smtp_pass','')
#print "=====",SMTP_SERVER,SMTP_USER,SMTP_USER
class SendMail:        
    """邮件发送模块,此模块运行使用django模块来发送邮件
    参数介绍(*必填):        subject *邮件主题        template *邮件模板位置        context *邮件模板上下文
    to_addr *目的地址,允许发给多人,格式为['test@examp.com','test2@example',......]        smtp_server 发件服务器地址
    smtp_server_port 发件服务器端口号        from_addr 发信地址        from_addr_name 发信人名称        user 发件箱登录用户名
    pass 发件箱登录密码
    e.g:         from ureg.helper import SendMail
    mail = SendMail('test','email/register.html',{'tmp_code':'123'},['ad@fengsage.cn'])
    mail.send_mail()            """
    def __init__(self,subject,template,context,to_addr,from_addr_name=u'xxxxx'):
        self.subject = subject
        self.template = template
        self.context = context
        self.to_addr  = to_addr
        self.from_addr = GetParamValue('opt_email_smtp_user','')
        self.from_addr_name = from_addr_name
        self.username = GetParamValue('opt_email_smtp_user','')
        self.password = GetParamValue('opt_email_smtp_pass','')
        #self.smtp_server_port = smtp_server_port
        self.mailserver = GetParamValue('opt_email_smtpserver','')
        #self.smtp=smtplib.SMTP(self.mailserver,self.smtp_server_port)
    def loginmail(self):
        #self.smtp = smtplib.SMTP(self.mailserver,self.smtp_server_port)
        self.smtp.login(self.username, self.password)

    def quitmail(self):
        self.smtp.quit()


    def send_mail(self):
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email import Utils
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = self.subject
        msgRoot['From'] =  self.named(self.from_addr, self.from_addr_name)
        if len(self.to_addr) == 1:
            msgRoot['To'] = self.to_addr[0]
        else:
            msgRoot['To'] = Utils.COMMASPACE.join(self.to_addr)
         #msgRoot['Date'] = Utils.formatdate()                # Encapsulate the plain and HTML versions of the message body in an        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        #根据模板生成html
        html = self.render(self.template, self.context).encode('utf-8')#
        #print "sendmail==",html
        msgText = MIMEText(html,'html',_charset='utf-8')
        msgAlternative.attach(msgText)
        ssl = GetParamValue('opt_email_usessl','0')
        if ssl=='0':
            smtp = smtplib.SMTP(self.mailserver,25)
        else:
            smtp = smtplib.SMTP_SSL(self.mailserver,465)
        smtp.login(self.username, self.password)
        result = smtp.sendmail(self.from_addr, self.to_addr, msgRoot.as_string())
        smtp.quit()
    def send_mail_handlogin(self):
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email import Utils
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = self.subject
        msgRoot['From'] =  self.named(self.from_addr, self.from_addr_name)
        if len(self.to_addr) == 1:
            msgRoot['To'] = self.to_addr[0]
        else:
            msgRoot['To'] = Utils.COMMASPACE.join(self.to_addr)
            pass
        #msgRoot['Date'] = Utils.formatdate()                # Encapsulate the plain and HTML versions of the message body in an        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        #根据模板生成html
        html = self.render(self.template, self.context).encode('utf-8')#
#		print "sendmail==",html
        msgText = MIMEText(html,'html',_charset='utf-8')
        msgAlternative.attach(msgText)
        #smtp = smtplib.SMTP(self.mailserver,self.smtp_server_port)
        #smtp.login(self.username, self.password)
        result = self.smtp.sendmail(self.from_addr, self.to_addr, msgRoot.as_string())
        #smtp.quit()

    def render(self,template,context):
        """        读取模板内容,并赋值        """
        if template:
            t = loader.get_template(template)
            return t.render(context)
        return context
    def named(self,mail,name):
        """        格式化右键发信/收信格式            e.g fredzhu <me@zksoftware.com>        """
        if name:
            return '%s <%s>' % (name,mail)
        return mail


if __name__=='__main__':
    mail = SendMail("USER_REGISTER",'email/register.html',{'tmp_code':'tmp_code','tmp_user':'username'},['support@zkteco.com'])
    mail.send_mail()