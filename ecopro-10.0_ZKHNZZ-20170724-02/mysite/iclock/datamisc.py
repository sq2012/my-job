#coding=utf-8
from mysite.iclock.models import *
from django.utils.encoding import smart_str
from mysite.iclock.datautils import *
from django.shortcuts import render_to_response,render
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from mysite.iclock.datasproc import trunc
from mysite.cab import *
import json
def getCopyInfo(request, ModelName):
    copyInfo = request.GET.get("key", "")
    model=models.get_model("iclock", ModelName)
    toResponse = "{"
    objs = model.objects.all()
    if objs:
        copyFields = objs[0].GetCopyFields()
        if model == employee:
            info = model.objects.filter(PIN=copyInfo).values(*copyFields)[0]
        elif model == iclock:
            info = model.objects.filter(SN=copyInfo).values(*copyFields)[0]
        else:
            info = model.objects.values(*copyFields)[0]	# For Exception
        for field in copyFields:
            if field == "Gender":
                toResponse += field + ":'" + ((info[field] == u'M') and _("male") or _("female")) + "',"
            else:
                f_value = info[field]
                toResponse += field + ":'" + unicode(f_value) + "',"
        toResponse = toResponse[:-1]
    toResponse += "}"
    return getJSResponse(toResponse)

def sendnew(request, ModelName):
    # �����Ŀ�������MS-SQL
    #from data2mssql import copyTransation
    from data2txt import copyTransation
    copyTransation()
    return getJSResponse("""'OK'""")

def DataExport(request, dataModel, qs, format):
    template=""
    format, compress=(format+'_').split("_")
    formats=openExportFmt(request);
    f=formats[int(format)-1] #employee_������ձ�xt:"{{ item.PIN.PIN }}", ...
    fds =f.split("_",1)+[""]
    if fds[0]==dataModel.__name__ and fds[1]:
        fds=fds[1].split(":",1)+[""]
        if fds[0] and fds[1]: # ������ձ�xt:"{{ item.PIN.PIN }}", ...
                template=fds[1]
    if not template:  return render_to_response("info.html", {"title": _("Export data"), "content": _("Specified data format does not exist or do not support!")});
    if template[-1]=="\n": template=template[:-1]
#	print "template", template
    template=Template(template)
    content=[]
    c=len(qs)
    for item in qs[:c>settings.MAX_EXPORT_COUNT and settings.MAX_EXPORT_COUNT or c]:
        content.append(template.render(Context({'item': item})))
    content=u"\r\n".join(content)
    response=HttpResponse(content_type="text/plain")
    response["Content-Type"]="text/plain; charset="+settings.NATIVE_ENCODE
    response["Pragma"]="no-cache"
    response['Content-Disposition'] = u'attachment; filename='+(".".join(fds[0].split(".")[-2:]))
    response["Cache-Control"]="no-store"
    content=content.encode(settings.NATIVE_ENCODE)
    response["Content-Length"]=len(content);
    response.write(content);
    return response

MAX_REALTIME_COUNT=50
"""实时考勤记录 """
@login_required
def newTransLog(request): #��
#	device=getDevice(request.REQUEST.get('SN', ""))
    Flag=False
    result={}
    lasttid=int(request.GET.get("lasttid","-1"))
    lastdid=int(request.GET.get("lastdid","-1"))

    if request.method=='GET':
        attColModel=[
        {'name':'id','hidden':False,'sortable':False,'align':'center','width':50,'label':unicode(_(u'ID'))},
        {'name':'TTime','sortable':False,'width':100,'align':'center','label':unicode(_(u'时间'))},
        {'name':'PIN','sortable':False,'width':120,'label':unicode(_(u'人员'))},
        #{'name':'EName','sortable':False,'width':140,'label':unicode(_(u'姓名'))},
        {'name':'DeptName','sortable':False,'width':160,'label':unicode(_(u'单位名称'))},
        {'name':'Device','sortable':False,'width':160,'label':unicode(_(u'设备名称'))},
        {'name':'urls1','sortable':False,'width':160,'label':unicode(_(u'登记照片'))},
        {'name':'urls','sortable':False,'width':160,'label':unicode(_(u'现场照片'))},


        ]
        HeaderModels=[
#			{'startColumnName': 'PIN', 'numberOfColumns': 2, 'titleText': '<em>人员</em>'},
#			{'startColumnName': 'LateMinutes', 'numberOfColumns': 1, 'titleText': '<em>'+unicode(SchClass._meta.get_field('LateMinutes').verbose_name)+'</em>'},

               ]

        cc={}
        cc['attModel']=dumps(attColModel)
        cc['HeaderModels']=dumps(HeaderModels)

        return render(request,"dlogcheck.html",cc)#render_to_response("dlogcheck.html",cc,RequestContext(request, {}))
    logs=[]
    items=[]
    photo_logs=[]
    SN=request.POST.get('SN', "")
    devices=SN.split(',')
    nt=trunc(datetime.datetime.now())

    lines=[]
    photo_lines=[]
    try:
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            ip =  request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
    except:
        ip=''
    _logstamp_=cache.get("%s_logstamp_"%(settings.UNIT))
    if (cache.get("%s_haslogs_%s_%s"%(settings.UNIT,request.user.pk,ip))!=_logstamp_) or lasttid==-1:
        cache.set("%s_haslogs_%s_%s"%(settings.UNIT,request.user.pk,ip),_logstamp_,timeout=10*60)

        items = transactions.objects.filter(TTime__gte=nt).filter( Q(SN__ProductType=9) | Q(SN__ProductType__isnull=True))
        if not request.user.is_superuser and (not request.user.is_alldept):
            dept_list = userDeptList(request.user)
            items = items.filter(UserID__DeptID__in=dept_list)
        if devices != [u'']:
            items = items.filter(SN__in=devices)

        logs=items.filter(id__gt=lasttid).order_by("-id")
        if lasttid==-1:
            logs=logs[:4]
        else:
            logs=logs[:MAX_REALTIME_COUNT]
        lasttid=0
        for l in logs:
            lasttid=max(l.id,lasttid)
            line={}
            line['id']=l.id
    #		line['PIN']="%s"%l.employee()
            line['PIN']="%s"%l.employee().PIN+'<br><br>%s'%(l.employee().EName or '')
            #line['EName']="%s"%l.employee().EName
            t=l.employee().Dept()
            if t:
                line['DeptName']="%s<br><br>%s"%(t.DeptNumber,t.DeptName)
            else:
                line['DeptName']=""


            line['TTime']=l.TTime.strftime("%H:%M:%S")
            #line['State']=getRecordName(l.State)#l.get_State_display()
            #line['Verify']=l.getComVerifys()#tranAttVerify(l.Verify)#l.get_Verify_display()
            #line['SC']=l.State
            #line['VC']=l.Verify
            devPIN=devicePIN(l.employee().PIN)
            if l.Device():
                line['Device']=l.SN_id+'<br><br>'+ safe_unicode(l.Device().Alias)
                cmapfile="%s/upload/%s/%s/%s-%s.jpg" %(settings.ADDITION_FILE_ROOT,l.Device().SN,l.TTime.strftime('%Y%m'),l.StrTime(),devPIN)
                if os.path.exists(cmapfile):
                    line['urls']="<img src=/iclock/file/upload/%s/%s/%s-%s.jpg  style='height:120px;'/>" %(l.Device().SN,l.TTime.strftime("%Y%m"),l.TTime.strftime("%Y%m%d%H%M%S"),devPIN)
                else:
                    line['urls']="<img src=/media/img/transaction/noimg.jpg style='width:160px;height:120px;'/>"
            else:
                line['Device']=""
                line['urls']="<img src=/media/img/transaction/noimg.jpg style='width:160px;height:120px;'/>"
            photourl=l.employee().getThumbnailUrl(None,False)
            if photourl:
                line['urls1']="<img src=%s style='height:120px;'/>"%photourl
            else:
                line['urls1']="<img src=/media/img/noimg.jpg style='height:120px;'/>"
            #cmapfile1="%sphoto/%s.jpg"%(settings.ADDITION_FILE_ROOT,l.employee().PIN)
            #if os.path.isfile(cmapfile1):
            #	line['urls1']="<img src=/iclock/file/photo/%s.jpg  style='height:120px;'/>"%l.employee().PIN
            #else :
            #	line['urls1']="<img src=/media/img/noimg.jpg style='height:120px;'/>"
            #line['WorkCode']=l.WorkCode=="0" and " " or l.WorkCode or ""
            #line['Reserved']=l.Reserved=="0" and " " or l.Reserved or ""
            #line['T']=1
            lines.insert(0,line.copy())
        photo_logs=items.order_by("-id")[:5]#因为照片与记录传送不同步，重新传送最新5条记录的图片url

        for l  in photo_logs:
            ls={}
            ls['id']=l.id
            devPIN=devicePIN(l.employee().PIN)
            if l.Device():
                cmapfile="%s/upload/%s/%s/%s-%s.jpg" %(settings.ADDITION_FILE_ROOT,l.Device().SN,l.TTime.strftime("%Y%m"),l.StrTime(),devPIN)
                if os.path.exists(cmapfile):
                    ls['urls']="<img src=/iclock/file/upload/%s/%s/%s-%s.jpg  style='width:160px;height:120px;'/>" %(l.Device().SN,l.TTime.strftime("%Y%m"),l.TTime.strftime("%Y%m%d%H%M%S"),devPIN)
                    photo_lines.append(ls.copy())


    result['msg']='OK'
    result['data']=lines
    result['lasttId']=lasttid
    #result['lastDId']=lastdid
    result['ret']=len(lines)
    result['photo_lines']=photo_lines
    result['tm']=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#	cache.set("%s_haslogs_%s"%(settings.UNIT,request.user.pk),0)
    return getJSResponse(result)

@login_required	
def newDevLog(request): #�
#	device=getDevice(request.REQUEST.get('SN', ""))
    SN=request.GET.get('SN', "")
    if SN=="all":
        if (request.user.is_superuser) or (request.user.is_alldept):
            device=iclock.objects.filter(Q(DelTag__isnull=True)|Q(DelTag=0))
        else:
            sns=userIClockList(request.user)
            device=iclock.objects.filter(SN__in=sns).filter(Q(DelTag__isnull=True)|Q(DelTag=0))
    else:
        device=iclock.objects.filter(SN__in=request.GET.get('SN', "").split(",")).filter(Q(DelTag__isnull=True)|Q(DelTag=0))
    result={}
    lasttid=int(request.GET.get("lasttid","-1"))
    lastdid=int(request.GET.get("lastdid","-1"))
    if lasttid==-1:
        t= render(request,"dlogcheck.html",{})
        return t
    if (not request.user.is_superuser) and (not request.user.is_alldept):
        dept_list=userDeptList(request.user)
        if device:
            logs=oplog.objects.filter(id__gt=lastdid,SN__in=device).order_by("-id")
        else:
            logs=oplog.objects.filter(id__gt=lastdid,SN__DeptID__in=dept_list).order_by("-id")
    else:
        if device:
            logs=oplog.objects.filter(id__gt=lastdid,SN__in=device).order_by("-id")
        else:
            logs=oplog.objects.filter(id__gt=lastdid).order_by("-id")
    logs=logs[:MAX_REALTIME_COUNT]
    if logs: lastdid=logs[0].id
    lines=[]
    for l in logs:
        line={}
        line['id']=l.id
        line['PIN']=l.admin or ""
        line['EName']=""
        line['DeptName']=""
        line['TTime']=l.OPTime.strftime("%m-%d %H:%M:%S")
        line['State']=u"%s"%l.ObjName() or ""
        line['Verify']=u"%s"%l.OpName()
        line['SC']=u"%s"%l.Object
        line['VC']=u"%s"%l.OP
        line['Device']=smart_str(l.Device().Alias)
        line['WorkCode']=l.Param1 or ""
        line['Reserved']=l.Param2 or ""
        lines.append(line.copy())
#	lines.sort(lambda x,y: x['TTime']<y['TTime'] and 1 or -1)
#	lines=lines[:MAX_REALTIME_COUNT]
    result['msg']='OK'
    result['data']=lines
    result['lasttId']=lasttid
    result['lastDId']=lastdid
    result['ret']=len(lines)
    return getJSResponse(json.dumps(result))

#@login_required	
#def uploadFile(request, path): 
#	if request.method=='GET':
#		return render_to_response("uploadfile.html",{"title": "Only for upload file test"})
#	if "EMP_PIN" not in request.REQUEST:
#		return getJSResponse("result=-1; message='Not specified a target';")
#	f=devicePIN(request.REQUEST["EMP_PIN"])+".jpg"
#	size=saveUploadImage(request, "fileUpload", fname=getStoredFileName("photo", None, f))
#	return getJSResponse("result=%s; message='%s';"%(size,getStoredFileURL("photo",None,f)))


MAX_PHOTO_WIDTH=400

def saveUploadImage(request, requestName, fname):
    import StringIO
    import os
    try:
        os.makedirs(os.path.split(fname)[0])
    except: pass
    output = StringIO.StringIO()
    f=request.FILES[requestName]
    size=f.size
    for chunk in f.chunks():
        output.write(chunk)
    try:
        import PIL.Image as Image
    except:
        return None
    try:
        output.seek(0)
        im = Image.open(output)
    except IOError, e:
#		print "error to open", imgUrlOrg, e.message
        return getJSResponse("result=-1; message='Not a valid image file';")
    #print f.name
    size=f.size
    if im.size[0]>MAX_PHOTO_WIDTH:
        width=MAX_PHOTO_WIDTH
        height=int(im.size[1]*MAX_PHOTO_WIDTH/im.size[0])
        try:
            im=im.resize((width, height), Image.ANTIALIAS)
        except Exception,e:
            print "6666666666==",e
    try:
        im.save(fname);
    except IOError:
        print "saveUploadImage=="
        im.convert('RGB').save(fname)
    return size


#这个方法跟上面的唯一区别就是 不压缩上传图片的大小，图片多大上传上去就是多大	
def saveUploadImage2(request, requestName, fname):
    import StringIO
    import os
    try:
        os.makedirs(os.path.split(fname)[0])
    except: pass
    output = StringIO.StringIO()
    f=request.FILES[requestName]
    size=f.size
    for chunk in f.chunks():
        output.write(chunk)
    try:
        import PIL.Image as Image
    except:
        return None
    try:
        output.seek(0)
        im = Image.open(output)
    except IOError, e:
#		print "error to open", imgUrlOrg, e.message
        return getJSResponse("result=-1; message='Not a valid image file';")
    #print f.name
    size=f.size

    try:
        im.save(fname);
    except IOError:
        im.convert('RGB').save(fname)
    return size
MAX_PHOTO_WIDTH3=40

def saveUploadImage3(request, requestName, fname):
    import StringIO
    import os
    try:
        os.makedirs(os.path.split(fname)[0])
    except: pass
    output = StringIO.StringIO()
    f=request.FILES[requestName]
    size=f.size
    for chunk in f.chunks():
        output.write(chunk)
    try:
        import PIL.Image as Image
    except:
        return None
    try:
        output.seek(0)
        im = Image.open(output)
    except IOError, e:
#		print "error to open", imgUrlOrg, e.message
        return getJSResponse("result=-1; message='Not a valid image file';")
    #print f.name
    size=f.size
    if im.size[0]>MAX_PHOTO_WIDTH3:
        width=MAX_PHOTO_WIDTH3
        height=30#int(im.size[1]*MAX_PHOTO_WIDTH3/im.size[0])
        im=im.resize((width, height), Image.ANTIALIAS)
    try:
        im.save(fname);
    except IOError:
        im.convert('RGB').save(fname)
    return size



def saveUploadTranspic(request, requestName, fname):
    import StringIO
    import os
    import zipfile
    try:
        os.makedirs(os.path.split(fname)[0])
    except: pass
    output = StringIO.StringIO()
    sn = request.POST.get("SN", None)
    f=request.FILES[requestName]
    piczip = open(fname, 'wb+')
    for chunk in f.chunks():
        piczip.write(chunk)
    piczip.close()
    fname="%s%s%s/%s"%(settings.ADDITION_FILE_ROOT,'upload/temp_transpic/',sn, f)
    source_file = fname
    target_dir = "%s%s%s/"%(settings.ADDITION_FILE_ROOT,'upload/temp_transpic/',sn)
    unzipFile(fname, target_dir)
    pic_dir = "%s%s%s/%s"%(settings.ADDITION_FILE_ROOT,'upload/temp_transpic/',sn, 'pass')
    files = os.listdir(pic_dir)
    for pin in files:
        imgUrlOrg = pic_dir+'/'+pin
        imgname=pin
        pin=pin.split(".")[0].split("-")

        dt=pin[0]
        if len(pin)==2:
            pin=pin[1]
        else:
            pin=None
        #fname=getUploadFileName("%s/%s/%s"%(sn,dt[:4],dt[4:8]), pin, dt[8:]+".jpg")
        fname=getUploadFileName("%s/%s/"%(sn,dt[:6]), '', imgname)
        createThumbnail(imgUrlOrg, fname)

