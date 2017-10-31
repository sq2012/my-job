#coding=utf-8
import os
from mysite.iclock.models import USER_SPEDAY,USER_SPEDAY_DETAILS
from django.conf import settings
from mysite.utils import getJSResponse
from django.utils.translation import ugettext_lazy as _

def fileDelete(request,ModelName):
    if ModelName=='USER_SPEDAY':
        keys = request.POST.getlist("K")
        return del_spedy_file(keys)
        
def del_spedy_file(keys):
    path = '%s%s/'%(settings.ADDITION_FILE_ROOT,'userSpredyFile')
    files = USER_SPEDAY_DETAILS.objects.filter(USER_SPEDAY_ID__pk__in=keys).values_list('file',flat=True)
    try:
        for file in files:
            tmp_path = path + file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        USER_SPEDAY_DETAILS.objects.filter(USER_SPEDAY_ID__pk__in=keys).update(file='')
    except:
        return getJSResponse({"ret":1,"message":u'%s'%_(u'删除失败')})
    return getJSResponse({"ret":0,"message":u'%s'%_(u'删除成功')})
