from django.shortcuts import render
from mysite.base.models import *
from mysite.iclock.models import adminLog
from mysite.utils import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required,permission_required

# Create your views here.
@login_required
def save_Home(request):
	s_url=request.POST.get('url','')
        mod_name=request.GET.get('mod_name','')
	SetParamValue('opt_user_homeurl',s_url,"%s-%d"%(mod_name, request.user.id))
	cache.set("%s_%s_%d_%s"%(settings.UNIT, mod_name,request.user.id,'opt_user_homeurl'),s_url)
	return getJSResponse({"ret":0,"message":u"%s" % _('Save Success')})
