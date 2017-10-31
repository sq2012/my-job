#!/usr/bin/python
# -*- coding: utf-8 -*-
from mysite.iclock.models import *
from django.core.cache import cache
import string
import datetime
import time,os
from django.conf import settings
from mysite.utils import *
from django.utils.translation import ugettext_lazy as _
from mysite.core.tools import *
import base64


def line_to_log_ex(recordDict,line_raw,emp=None,device=None):
    RecordDict = {}


    #sql, params = getSQL_insert_new(KqRecords._meta.db_table, RecordDict)
    #customSql(sql, params)

def saveAttPhoto(request,device):
#	print "=================================================================",request.body
    #print "-----------------------",request.GET
    d=request.body
    dList=[]
    if "CMD=uploadphoto" in d: dList=d.split("CMD=uploadphoto")
    if "CMD=realupload" in d: dList=d.split("CMD=realupload")
    if not dList:return
    hlist=dList[0]
    pd=setValueDic(hlist)
    try:
        pin=pd['PIN']
    except:
        try:
            pin=request.POST.get("PIN","")#改变照片PIN的获取方式
            if not pin:
                pin=request.GET.get("PIN","")
        except:
            pin=request.GET.get("PIN","")
    #pin=pin.split(".")[0]
    fname=getUploadFileName("%s/%s"%(device.SN,pin[:6]), '',pin)
    try:
        os.makedirs(os.path.split(fname)[0])
    except:
        pass #errorLog(request)
    if dList and 'size' in pd.keys() and int(pd['size'])>1000:
        f=file(fname,"wb")
        #if "CMD=uploadphoto" in d: d=d[1][1:]
        #if "CMD=realupload" in d: d=d.split("CMD=realupload")[1][1:]
        d=dList[1][1:]
        f.write(d)
        f.close()
        #saveDeviceStamp(conn.cursor(), device, 'photostamp', device.PhotoStamp)
        #cache.set("iclock_"+device.SN, device)
    return pin[:14]


def savePhoto(device,flds):
    content = flds["FileName"].split('.')
    name = content[0]+'_SN.'+content[1]
    fname="%s/%s"%(photoDir(),name)
#   try:
#       os.makedirs(os.path.split(fname)[0])
#   except:
#       pass
    ls_f=base64.b64decode(flds["Content"]) #解码
    f=file(fname,"wb")
    f.write(ls_f)
    f.close()
    try:
        fname="%s/thumbnail/%s"%(photoDir(),name)
        os.remove(fname)
    except:pass
    return (u"USERPICDATA_%s"%flds["FileName"])[:30]
