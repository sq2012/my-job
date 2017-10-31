#!/usr/bin/python
# -*- coding: utf-8 -*-

"this is the locale selecting middleware that will look at accept headers"

from django.utils.cache import patch_vary_headers
from django.utils import translation
#from mysite.settings import MEDIA_URL, ADMIN_MEDIA_PREFIX
from django.conf import settings
from django.core.urlresolvers import (is_valid_path, get_resolver,
                                      LocaleRegexURLResolver)
from django.core.cache import cache
#from django.core.context_processors import PermWrapper
from django.contrib.auth.context_processors import PermWrapper
#from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _

#from django.utils.datastructures import SortedDict
from django.utils.deprecation import MiddlewareMixin

noLocalePath=(settings.MEDIA_URL, settings.ADMIN_MEDIA_PREFIX,
	'/iclock/tmp/',
	'/iclock/files/',
	'/iclock/ccccc/',
	'/iclock/media/',
	'/media',
	'/iclock/getrequest',
	'/iclock/cdata',
	'/iclock/devicecmd',
	)

def IEVersion(request):
	bVer=request.META['HTTP_USER_AGENT'] #'OpenWare (compatible; MSIE 7.0; Windows NT 5.1; WPS; (R1 1.3); .NET CLR 1.1.4322)'
	p=bVer.find("MSIE ")
#	print bVer, p
	if p<0: return 100
	return int(bVer[p+5:].split(".")[0])

class LocaleMiddleware(MiddlewareMixin):
	"""
	This is a very simple middleware that parses a request
	and decides what translation object to install in the current
	thread context. This allows pages to be dynamically
	translated to the language the user desires (if the language
	is available, of course).
	"""
	#def __init__(self):
	#    #self._supported_languages = SortedDict(settings.LANGUAGES)
	#    self._is_language_prefix_patterns_used = False
	#    for url_pattern in get_resolver(None).url_patterns:
	#	if isinstance(url_pattern, LocaleRegexURLResolver):
	#	    self._is_language_prefix_patterns_used = True
	#	    break

	def process_request(self, request):
		path=request.META["PATH_INFO"]
		for nol in noLocalePath:
			if path.find(nol)==0:
				request.isLocaled=False
				return

		language = translation.get_language_from_request(request)
		translation.activate(language)
		request.LANGUAGE_CODE = translation.get_language()
		request.isLocaled=True
		if "employee" in request.session: request.employee=request.session["employee"]
#		settings.SupportNewCSS=IEVersion(request)>=7
#print "LANGUAGE_CODE=%s"%request.LANGUAGE_CODE

	def process_response(self, request, response):
		if hasattr(request, "isLocaled") and request.isLocaled:
			patch_vary_headers(response, ('Accept-Language',))
			response["Pragma"]="no-cache"
			response["Cache-Control"]="no-store"
			response['Content-Language'] = translation.get_language()
			translation.deactivate()
		return response

def employee(request):
#{% if user.first_name %}{{ user.first_name|escape }}{% else %}{{ user.username }}{% endif %}
	user=request.user
	if user.is_anonymous(): return ''
	if user.username=='employee' and "employee" in request.session:
		return _(u"Staff %s")%request.session["employee"]['name']
	else:
		return user.first_name or user.username

def myContextProc(request):
	emp=None
	user=request.user
	userName=''
	if not user.is_anonymous():
		if user.username=='employee' and "employee" in request.session:
			emp=request.session["employee"]
			userName=_(u"Staff %s")%(emp['name'] or emp['pin'])
		else:
			userName=user.first_name or user.username
	return {#'SupportNewCSS': settings.SupportNewCSS,
		'IS_ADMIN': emp==None and not user.is_anonymous(),
		'login_username': userName,
		'employee': emp,
		'request': request,
		}


#��ontextProc�����django.core.context_processors.auth��
#�Ӷ��������uth_messages

def auth(request):
    """
    Returns context variables required by apps that use Django's authentication
    system.

    If there is no 'user' attribute in the request, uses AnonymousUser (from
    django.contrib.auth).
    """
    if hasattr(request, 'user'):
        user = request.user
    else:
        from django.contrib.auth.models import AnonymousUser
        user = AnonymousUser()

    return {
        'user': user,
        'perms': PermWrapper(user),
    }

#����iddleware�����django.contrib.auth.middleware.AuthenticationMiddleware
#ʹ������������û�������ζ�����ݿ�
SESSION_KEY = '_auth_user_id'

class LazyUser(object):
	def __get__(self, request, obj_type=None):
		if not hasattr(request, '_cached_user'):
			u=None
			try:
				user_id = request.session[SESSION_KEY]
				k="user_id_%s"%user_id	
				u=cache.get(k)
			except:
				from django.contrib.auth.models import AnonymousUser
				u=AnonymousUser()
			if u==None:
				from django.contrib.auth import get_user
				u = get_user(request)
				cache.set(k, u, 60*60)
			request._cached_user=u
		return request._cached_user

class AuthenticationMiddleware(MiddlewareMixin):
	def process_request(self, request):
		assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
		request.__class__.user = LazyUser()
		return None

