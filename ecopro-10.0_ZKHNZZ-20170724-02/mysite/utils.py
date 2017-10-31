# -*- coding: utf-8 -*-
import traceback
import string
import datetime
import os
import shutil 
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings
from django.utils.encoding import smart_str
#from django.utils import simplejson as json
#from iclock.iutils import *
#from django.utils import simplejson
import json
import re

def safe_unicode(obj, encoding=None):
    """Return a unicode value from the argument"""
    if isinstance(obj, unicode):
        return obj
    elif isinstance(obj, str):
        if encoding is None:
            return unicode(obj)
        else:
            return unicode(obj, encoding)
    else:
        # it may be an int or a float
        return unicode(obj)

def set_cookie(response, key, value, expire=None):
    if expire is None:
        max_age = 365*24*60*60  #one year
    else:
        max_age = expire
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE or None)
    
def tmpDir():
    ret=settings.ADDITION_FILE_ROOT+"/tmp"
    try:
        os.makedirs(ret)
    except: pass
    return ret
def logDir():
    ret=settings.ADDITION_FILE_ROOT+"/logs"
    try:
        if not os.path.isdir(ret):
            os.makedirs(ret)
    except: pass
    return ret

#def tmpDir():
    #ret=settings.LOG_DIR
    #try:
        #os.makedirs(ret)
    #except: pass
    #return ret

def createDir(dirname):
    try:
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
    except: pass


def outBoxDir():
    ret=settings.ADDITION_FILE_ROOT+"/outbox"
    return ret
def inBoxDir():
    ret=settings.ADDITION_FILE_ROOT+"/inbox"
    return ret
def badoutBoxDir():
    ret=settings.ADDITION_FILE_ROOT+"/badoutbox"
    return ret
def senderoutBoxDir():
    ret=settings.ADDITION_FILE_ROOT+"/senderoutbox"
    return ret
def smsFile(text, append=True):
    fn="%s/%s.txt"%(outBoxDir(),datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    f=file(fn, append and "a+" or "w+")
    try:
#		text=u"一二"
        text=text.encode("gb18030")
        f.write(text)
        #file.write(unicode.encode(content, 'utf-8'))
    except Exception,e:
        print "-------",e
    #f.write("\n")
    f.close()
    return fn



def CleanDir( Dir ): 
    if os.path.isdir( Dir ): 
        paths = os.listdir( Dir ) 
        for path in paths: 
            filePath = os.path.join( Dir, path ) 
            if os.path.isfile( filePath ): 
                try: 
                    os.remove( filePath ) 
                except os.error: 
                    autoRun.exception( "remove %s error." %filePath )#引入logging 
            elif os.path.isdir( filePath ): 
                if filePath[-4:].lower() == ".svn".lower(): 
                    continue 
                shutil.rmtree(filePath,True) 
    return True 


 


def reportDir():
    ret=settings.ADDITION_FILE_ROOT+"/reports"
    return ret
def photoDir():
    ret=settings.ADDITION_FILE_ROOT+"/photo"
    return ret



def unquote(s):
    """unquote('abc%20def%u4E66') -> 'abc def'."""
    res = s.split('%')
    for i in xrange(1, len(res)):
        item = res[i]
        try:
            if item[0]=='u':
                res[i]=unichr(string.atoi(item[1:5],16))+item[5:]
            else:
                res[i] = chr(string.atoi(item[:2],16)) + item[2:]
        except KeyError:
            res[i] = '%' + item
        #except UnicodeDecodeError:
            #res[i] = unichr(int(item[:2], 16)) + item[2:]
    return "".join(res)


def saveToFile(fn,text,append=True,ctlsize=False):
    #if ctlsize:
    #	if os.path.getsize(fn)>30*1024:
    #		os.remove(fn)

    f=file(fn, "w+")
    try:
        f.write(text)
    except:
        try:
            f.write(text.encode("utf-8"))
        except: pass
    f.write("\n")
    f.close()
    return fn
   


def appendFile(s,sn=1):
    f=file("%s/info_%s.txt"%(tmpDir(),sn), "a+")
    try:
        f.write(s)
    except:
        try:
            f.write(s.encode("utf-8"))
        except: pass
    f.write("\n")

def tmpFile(name, text, append=True):
    fn="%s/%s"%(tmpDir(),name)
    f=file(fn, append and "a+" or "w+")
    try:
        f.write(text)
    except:
        try:
            f.write(text.encode("utf-8"))
        except: pass
    f.write("\n")
    f.close()
    return fn
def logFile(text, append=True):
    fn="%s/logs_%s.txt"%(logDir(),datetime.datetime.now().strftime("%Y%m%d"))
    f=file(fn, append and "a+" or "w+")
    try:
        f.write(text)
    except:
        pass
    f.write("\n")
    f.close()
    return fn
def logsFile(fn,text, append=True):
    fn="%s/%s.log"%(logDir(),fn)
    f=file(fn, append and "a+" or "w+")
    try:
        f.write(text)
    except:
        pass
#	f.write("\n")
    f.close()
    return fn


def savePosLogToFile(LogFlag,text,append=True,sn=None):#LogFlag=issuecard
    fn=''
    ret=settings.ADDITION_FILE_ROOT+"/ipos/%s"%(LogFlag)
    createDir(ret)
    fn="%s/%s.txt"%(ret,datetime.datetime.now().strftime("%Y%m%d"))
    if sn:
        fn="%s/%s_%s.txt"%(ret,sn,datetime.datetime.now().strftime("%Y%m%d"))


    if fn:
        f=file(fn, append and "a+" or "w+")
        try:
            f.write(text)
        except:
            try:
                f.write(text.encode("utf-8"))
            except: pass
        f.write("\n")
        f.close()
        return fn
def saveScheduleLogToFile(LogFlag,text,user='admin',append=True):#LogFlag=issuecard
    fn=''
    ret=settings.ADDITION_FILE_ROOT+"/schedule/%s"%(LogFlag)
    createDir(ret)
    fn="%s/%s_%s.txt"%(ret,datetime.datetime.now().strftime("%Y%m%d%H%M%S"),user)


    if fn:
        f=file(fn, append and "a+" or "w+")
        try:
            f.write(text)
        except:
            try:
                f.write(text.encode("utf-8"))
            except: pass
        f.write("\n")
        f.close()
        return fn


def saveEmpScheduleLogToFile(LogFlag,text,pin='admin',append=True):#LogFlag=issuecard
    fn=''
    ret=settings.ADDITION_FILE_ROOT+"/schedule/%s"%(LogFlag)
    createDir(ret)
    fn="%s/%s.txt"%(ret,pin)


    if fn:
        f=file(fn, append and "a+" or "w+")
        try:
            f.write(text)
        except:
            try:
                f.write(text.encode("utf-8"))
            except: pass
        f.write("\r\n")
        f.close()
        return fn


def errorLog(request=None):
    f=file("%s/error_%s.txt"%(tmpDir(),datetime.datetime.now().strftime("%Y%m%d%H%M%S")), "a+")
    f.write("---%s: "%datetime.datetime.now())
    if request:
        f.write("-- %s%s --\n"%(request.META["REMOTE_ADDR"],request.META["PATH_INFO"]))
#	for v in request.REQUEST: f.write("\t%s=%s\n", v, request.REQUEST[v])
        f.write(request.body)
    f.write("\n")
    traceback.print_exc(file=f)
    f.write("---------------------------------\n")
    try:
        traceback.print_exc()
    except: pass


def saveImage(fn,image):
    imgsave = open(fn,'wb')
    imgsave.write(buffer(image))
    imgsave.close()


def trim0(s):
    while(s[-1]=="\x00"): s=s[:-1]
    return s

def trimTemp(tmp):
    tmp=tmp.replace("\n","").replace("\r","")
    return tmp
    #try:
    #	tmp=tmp.decode("base64")
    #except:
    #	appendFile(tmp)
    #	errorLog()
    #tmp=trim0(tmp)
    #return tmp.encode("base64")

def fwVerStd(ver): # Ver 6.18 Oct 29 2007 ---> Ver 6.18 20071029
    ml=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov','Dec']
    if len(ver)>=20:
        tl=ver[9:].split(" ")
        try:
            tl.remove("")
        except: pass
        try:
            return ver[:9]+"%s%02d%02d"%(tl[2], 1+ml.index(tl[0]), int(tl[1]))
        except:
            return ""
    else:
        return ""

def head_response(mtype='text/plain'): #生成标准的通信响应头
    response = HttpResponse(content_type=mtype)  #文本格式
    response["Pragma"]="no-cache"                   #不要缓存，避免任何缓存，包括http proxy的缓存
    response["Cache-Control"]="no-store"            #不要缓存
    return response



def getJSResponse(content=None,mtype="text/plain",callback=''):
    if callback:mtype="text/html"
    response = head_response(mtype)
    if (type(content)==type({})) or (type(content)==type([])):
        content=dumps1(content)
    content=smart_str(content)
    if callback:
        content="""%s(%s)""" %(callback,content)
    response["Access-Control-Allow-Origin"]="*"
    #response["Content-Length"]=len(content)
    response.write(content)
    return response

    
    
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        return json.JSONEncoder.default(self, obj)

def dumps(data):
    #return dumps1(data)
    return JSONEncoder().encode(data)

#以后用下面的函数2010.11.14
def dumps1(content):
    return json.dumps(content)
def dumps2(content):
    return json.dumps(content,ensure_ascii=False)

def loads(str,encoding=settings.DEFAULT_CHARSET):
    return json.loads(str, encoding)


def escape(html):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    return html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;').replace('\'','&#x27;').replace(' ','&nbsp;').replace('\r','').replace('\n','').replace('\\','').replace('\t','&#9')


def today():
    d=datetime.datetime.now()
    return datetime.datetime(d.year,d.month,d.day)

def nextDay():
    d=datetime.datetime.now()
    d=d+datetime.timedelta(1,0)
    return datetime.datetime(d.year,d.month,d.day)

def endOfDay(d):
    d=d+datetime.timedelta(1,0)
    return datetime.datetime(d.year,d.month,d.day)-datetime.timedelta(0,1)

def startOfDay(d):
    return datetime.datetime(d.year,d.month,d.day)

def decodeTimeInt(t):
    tm_sec=t % 60;
    t/=60;
    tm_min=t % 60;
    t/=60;
    tm_hour=t % 24;
    t/=24;
    tm_mday=t % 31+1;
    t/=31;
    tm_mon=t % 12
    t/=12;
    tm_year=t+2000;
    return "%04d-%02d-%02d %02d:%02d:%02d"%(tm_year,tm_mon+1,tm_mday,tm_hour,tm_min,tm_sec)

def decodeTime(data):
    t=ord(data[0])+(ord(data[1])+(ord(data[2])+ord(data[3])*256)*256)*256
    return decodeTimeInt(t)

def encodeTime(y,m,d,hour,min,sec):
    tt=((y-2000)*12*31+((m-1)*31)+d-1)*(24*60*60)+(hour*60+min)*60+sec;
    return tt



def decodeTimeInt(t):
    tm_sec=t % 60;
    t/=60;
    tm_min=t % 60;
    t/=60;
    tm_hour=t % 24;
    t/=24;
    tm_mday=t % 31+1;
    t/=31;
    tm_mon=t % 12
    t/=12;
    tm_year=t+2000;
    return "%04d-%02d-%02d %02d:%02d:%02d"%(tm_year,tm_mon+1,tm_mday,tm_hour,tm_min,tm_sec)

def decodeTime(data):
    t=ord(data[0])+(ord(data[1])+(ord(data[2])+ord(data[3])*256)*256)*256
    return decodeTimeInt(t)

#def encodeTime(y,m,d,hour,min,sec):
#	tt=((y-2000)*12*31+((m-1)*31)+d-1)*(24*60*60)+(hour*60+min)*60+sec;
#	return tt

def getAvialibleDB():
    import django
    dbs=[f for f in os.listdir(django.db.backends.__path__[0]) if not f.startswith('_') and not f.startswith('.') and not f.endswith('.py') and not f.endswith('.pyc')]
    dbs.remove('dummy')
    try:
        dbs.remove('mysql_old')
    except: pass
    try:
        import ado_mssql
        dbs.append('ado_mssql')
    except:	pass
    return dbs

def packList(l):
    r=[]
    for i in l:
        if i: r.append(i)
    return r

#设置操作系统的自动化任务			
def scheduleTask(cmd, time="00:00", weeks=('Su', 'M', 'T', 'W', 'Th', 'F', 'Sa')):
    l=os.popen("at").read()
    for s in l.split("\n"):
        r=packList(s.split(" "))
        if len(r)>=4:
            try:
                int(r[0])
            except:
                r.pop(0)
            atcmd=" ".join(r[3:])
            if cmd.lower()==atcmd.lower() or cmd[1:-1].lower()==atcmd.lower():
                print "Delete old schedule"
                os.system("at %s /DELETE"%r[0])
    if weeks:
        dur=" /EVERY:"+(",".join(weeks))
    else:
        dur=""
    cmd="at %s%s %s"%(time, dur, cmd)
#	print cmd
    os.system(cmd)



#临时目录用于保存未保存到数据库中的数据
def tempDir(childwithday=True):
    ret=settings.ADDITION_FILE_ROOT+"/temp"
    try:
        os.makedirs(ret)
    except: pass
    return ret
def tempFile(name, text, append=True):
    fn="%s/%s"%(tempDir(),name)
    f=file(fn, append and "a+" or "w+")
    try:
        f.write(text)
    except:
        try:
            f.write(text.encode("utf-8"))
        except: pass
    f.write("\n")
    f.close()
    return fn

def deviceHasCmd(deviceSN):
    nocmd_device_cname = "%s_nocmd_device_%s"

    try:
        cache.delete(nocmd_device_cname%(settings.UNIT,deviceSN))
    except: pass

def getNewColModel(colModel,keepName):
    """对原colModel根据要保留的name生成新的列表，keepName为需要的列表如['PIN','ENAME']"""
    for d in colModel:
        if d['name'] not in keepName:
            colModel.remove(d)
    return colModel



def getStoredFileName(sn, id, fname):
    fname="%s%s/%s"%(settings.ADDITION_FILE_ROOT, sn, fname)
    if id:
        fname, ext=os.path.splitext(fname)
        fname="%s_%s%s"%(fname,id,ext)
    fname.replace("\\\\","/").replace('//','/')
    return fname
def getStoredFileURL(sn, id, fname):
    fname="/iclock/file/%s/%s"%(sn, fname)
    if id:
        fname, ext=os.path.splitext(fname)
        fname="%s_%s%s"%(fname,id,ext)
    return fname

def getUploadFileName(sn, id, fname):
    if sn=='':
        return getStoredFileName('upload', id, fname)
    return getStoredFileName('upload/'+sn, id, fname)
def getUploadFileURL(sn, id, fname):
    if sn=='':
        return getStoredFileURL('upload', id, fname)
    return getStoredFileURL('upload/'+sn, id, fname)


import configparser
class myconf(configparser.ConfigParser):  
    def __init__(self,defaults=None):  
        configparser.ConfigParser.__init__(self,defaults=None)  
    def optionxform(self, optionstr):  
        return optionstr  

def SaveToIni(section,key,value):
    cfFileName=settings.FILEPATH+'/options.dat'
    cf = myconf()
    cf.read(cfFileName)
    cf.set(section, key, value)
    cf.write(open(cfFileName, "w"))

def card8To10Num(card):
    card=str(card)
    c=int('%s%s'%(hex(int(card[:-5])),'{:04x}'.format(int(card[-5:]))),16)
    return c
def card10To8Num(card):
    """用于将十进制10位卡号转换成8位区位码卡号"""
    hc=hex(int(card))
    c4=hc[-4:]
    c2=hc[:-4]
    c="%s%s"%('{:0>3}'.format(int(c2,16)),'{:0>5}'.format(int('0x'+c4,16)))
    return c

def cardHTOL(card):
    card="%s"%('{:0>8}'.format(str(hex(int(card)))[2:]))
    h="0x%s%s%s%s"%(card[6:8],card[4:6],card[2:4],card[0:2])
    l=int(h,16)
    return l

def circlePic(img):
    try:
        import PIL.Image as Image
    except:
        return None

    ima=img.convert("RGBA")
    size = ima.size
    r2 = min(size[0], size[1])
    #r2=200
    #if size[0] != size[1]:
    ima = ima.resize((r2, r2), Image.ANTIALIAS)
    imb = Image.new('RGBA', (r2, r2),(255,255,255,0))
    pima = ima.load()
    pimb = imb.load()
    r = float(r2/2)
    for i in range(r2):
        for j in range(r2):
            lx = abs(i-r+0.5)
            ly = abs(j-r+0.5)
            l  = pow(lx,2) + pow(ly,2)
            if l <= pow(r, 2):
                pimb[i,j] = pima[i,j]
    #imb.save("test_circle.jpg")
    return imb

def isDBDuplicate(estr):
    if ('SQL0803N' in estr) or ('IntegrityError' in estr) or ("UNIQUE KEY" in estr) or ("are not unique" in estr) or ("Duplicate entry" in estr) or ("unique constraint" in estr) or ("duplicate key" in estr):    
        return True
    return False

def restartSvr(svrName):
    try:
        os.system("cmd /C net stop %s & net start %s"%(svrName, svrName))
    except:
        pass
def setValueDic(data):
    d={}
    for line in data.split("\n"):
        if line:
            v=line.split("\r")[0]
        else:
            v=line
        nv=v.split("=", 1)
        if len(nv)>1:
            try:
                v=str(nv[1])
                d[nv[0]]=v
            except:
#print nv
                pass
    return d
def lineToDict(rawData,splitfmt='\t'):
    """将以\t或指定的分隔符号分隔的行变成字典"""
    d={}
    if rawData:
            rawData=rawData.replace('\r','').replace('\n','')
            #rawData=rawData.split("\r")[0]
            line=rawData.split(splitfmt)
            for t in line:
                    if t:
                            ll=t.split('=')
                            #if ll[1]=='0':ll[1]=None
                            d[ll[0]]=t[len(ll[0])+1:]
    return d
