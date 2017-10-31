#coding=utf-8
"""
本文件为其他系统提供信息
"""
import os,platform
from mysite.utils import *
from mysite.core.mimi import getLicenseInfo
def index(request):
    #print request.META
    response=head_response()
    

    lic=getLicenseInfo()
        
    q=request.GET.get('q')
    if q=='system_info':
        d={'processor':platform.processor(),
           'sysname':platform.platform(),
           'registered':lic['registerTime'],
           'license':lic['closeDay'],
           'productName':lic['version'],
            'clientNo':lic['custom']
            }
        
        result='\n'.join('%s=%s'%(k,v) for k,v in d.items())
        #result=u"processor=%s\r\n%s\r\n"%(platform.processor(),platform.platform())
        #result=dumps2(result)
        result=result.encode("gb18030")
        response.write(result)
  
  
  
    return response
   
   
