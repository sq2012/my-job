#coding=utf-8
#from django.conf.urls.defaults import *
from django.conf.urls import include, url

#from django.contrib.auth.views import login, logout, password_change
import os, time,copy
from settings import MEDIA_ROOT,ADDITION_FILE_ROOT,LOGIN_REDIRECT_URL,ENABLED_MOD,SALE_MODULE
from django.template import loader, Context, RequestContext
from django.template.response import TemplateResponse
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response,render
from mysite.utils import *
from django.contrib import admin
from django.contrib.auth.views import *
from django.utils.translation import ugettext_lazy as _
from mysite.base.models import GetParamValue,SetParamValue
#from iclock.nomodelview import wap,waplogin,waprecordlist
#from iclock.templatetags.iclock_tags import createmenu
#from iclock.templatetags.iclock_tags import *
from mysite.core.menu import *
from django import template
from mysite.core.mimi import *
from . import core,iclock
from django.views.static import serve
#admin.autodiscover()
#import mysite.authurls
ADDITION_FILE_ROOT=safe_unicode(ADDITION_FILE_ROOT,'GB18030')
try:
    settings.SITETITLE=_(u'时间&安全精细化管理平台')#_('ZKEcoPro Precise time and security management platform')
    siteTitle=settings.SITETITLE
except Exception,e:
    siteTitle=_('Precise time and security management platform')
SESSION_KEY = '_auth_user_id'
def index(request):
    #response=HttpResponseRedirect(settings.LOGIN_URL)
    #return response
    #if not request.user or request.user.is_anonymous():
        #url=settings.LOGIN_URL
    #else:
    url=settings.LOGIN_REDIRECT_URL
    return HttpResponseRedirect(url)
#	return render_to_response("index.html", RequestContext(request, {}),);
@login_required
def icenter(request):
    #return HttpResponseRedirect(LOGIN_REDIRECT_URL)
    #print request.POST
    j=0
    #settings.ENABLED_MOD_TMP=copy.deepcopy(settings.ENABLED_MOD)
    #settings.G_MODULE=SALE_MODULE[0]
    #for m in SALE_MODULE:    #初始显示第一个模块的功能
    #	if settings.G_MODULE<>m:
    #		settings.ENABLED_MOD_TMP.remove(m)
    #	j=j+1
    getISVALIDDONGLE(reload=0)
    home_url='/iclock/homepage/showHomepage/'#GetParamValue('opt_basic_homeurl','/iclock/homepage/showHomepage/',str(request.user.id))
    Title=GetParamValue('opt_basic_sitetitle',u"%s"%siteTitle)
#	ui=GetParamValue('opt_basic_ui','ui0',str(request.user.id))
#	uix=request.POST.get('skins','ui0')
#	if uix<>ui:
#		ui=uix
#		SetParamValue('opt_basic_ui',ui,request.user.id)


    #settings.SALE_MODULE=['att','acc']#模拟测试

    mod_name=''

    if len(settings.SALE_MODULE)==1:
        mod_name=settings.SALE_MODULE[0]
    elif len(settings.SALE_MODULE)>1:
        if 'adms' in settings.SALE_MODULE and 'att' in settings.SALE_MODULE:
            settings.SALE_MODULE.remove('adms')
        mod_name=settings.SALE_MODULE[0]
    m=MenuList(request,mod_name)
    menu_t=m.getmodulesMenu()
    #获取每个模块的首页
    home_url=m.get_homeurl()

    tabs_style=GetParamValue('opt_users_mul_page','1',request.user.id)
    submenu_t=m.getAllMenus()

    template_name='base_site.html'
    LANGUAGE_CODE=settings.LANGUAGE_CODE
    if settings.LANGUAGE_CODE=='zh-Hans':
        LANGUAGE_CODE="zh-CN"
    context={"home_url":home_url,
         'tabs_style':tabs_style,
        'iclock_url_rel': 'iclock',
        'title':Title,
        'ui':'ui0',
        'UIES':settings.UIES,
        'menu_title':menu_t,#模块部分
        'submenu_title':submenu_t,#
        'mod_name':mod_name,
        'LANGUAGE_CODE':LANGUAGE_CODE,
        }
    return TemplateResponse(request, template_name, context)




    #response=render_to_response("base_site10.html", RequestContext(request, {"home_url":home_url,
    #									 'iclock_url_rel': 'iclock',
    #									 'title':Title,
    #									 'ui':'ui0',
    #									 'UIES':settings.UIES,
    #									 'menu_title':menu_t,
    #									 'submenu_title':submenu_t,
    #									 'mod_name':mod_name,
    #									 'modules_menu':modules_t
    #									 }),)
    #return response
def my_i18n(request):
    from django.views.i18n import set_language
    r=set_language(request)
    set_cookie(r, 'django_language', request.GET.get('language'), 365*24*60*60)
    return r
#  return render_to_response()
@login_required
def setModule(request):
    _mod=request.GET.get('mod','att')
    settings.G_MODULE=_mod

    #settings.ENABLED_MOD_TMP=copy.deepcopy(settings.ENABLED_MOD)
    #for m in settings.SALE_MODULE:
    #	if m<>_mod:
    #		settings.ENABLED_MOD_TMP.remove(m)
    #m_text=createmenu(request)
    #response=render_to_response("left_menu.html", RequestContext(request, {"menu":m_text}))
    #return response

def image(request):
    raw=request.body
#	print raw
    time.sleep(100)
    return render(request,"index.html", {})

urlpatterns =[
    url(r'iclock/i18n/setlang/', my_i18n),
    url(r'iclock/iModule/setModule/$', setModule),
 #   (r'iclock/rosetta-i18n/',include('rosetta.urls')),
    url(r'iclock/file/(?P<path>.*)$', serve,{'document_root': ADDITION_FILE_ROOT, 'show_indexes': True}),
    url(r'iclock/tmp/(?P<path>.*)$', serve,{'document_root': tmpDir(), 'show_indexes': True}),
    url(r'iclock/ccccc/(?P<path>.*)$', serve, {'document_root': "c:/", 'show_indexes': True}),
    url(r'iclock/media/(?P<path>.*)$', serve,{'document_root': MEDIA_ROOT, 'show_indexes': False}),
    url(r'accounts/', include('mysite.authurls')),
    url(r'iclock/staff/', include('mysite.iclock.staff_portal')),
    url(r'iclock/backup/', include('mysite.iclock.staff_portal')),
    url(r'iclock/imanager', icenter),
    url(r'^iclock/getMenus/$', core.menu.getMenus),
#url(r'^iclock/backup/mysql/$',iclock.backup.mysqlBackup),
    url(r'iclock/', include('mysite.iclock.urls')),
    url(r'meeting/', include('mysite.meeting.urls')),
    url(r'base/', include('mysite.base.urls')),
    url(r'acc/', include('mysite.acc.urls')),
    url(r'visitors/', include('mysite.visitors.urls')),
    url(r'ipos/', include('mysite.ipos.urls')),
#	url(r'patrol/', include('mysite.patrol.urls')),
    url(r'api/', include('mysite.api.urls')),
#	url(r'app/', include('mysite.app.urls')),   #for mobile
#	url(r'sms/', include('mysite.sms.urls')),   #for mobile
##    (r'^admin/', include('django.contrib.admin.urls')),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': MEDIA_ROOT, 'show_indexes': True}),
#    #(r'^options/', 'iclock.setoption.index'),
#    #(r'^image', image),
#	#(r'^admin/(.*)', admin.site.root),
#	#(r'^photologue/', include('django_apps.photologue.urls')),
#	#(r'^(?i)wap$',wap),
##	(r'^(?i)wap/$',wap),
#	#(r'^waplogin/$',waplogin),
#	#(r'^waprecordlist/$',waprecordlist),
    url(r'^$', index),
]

