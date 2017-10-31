#!/usr/bin/env python
#coding=utf-8
from __future__ import division
from mysite.iclock.models import *
from django.template import loader, Context
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import string
import datetime
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import User
from mysite.cab import *
from mysite.iclock import reb
import os, time
from mysite.iclock.dataproc import *
from django.conf import settings
from mysite.iclock.iutils import *
from django.utils.translation import ugettext_lazy as _
#from django.utils.translation import gettext
from mysite.core.tools import *
from django.core.cache import cache
from mysite.utils import *
from mysite.core.cmdproc import set_pos_device_info
from decimal import Decimal

lineFmt=u"&nbsp;&nbsp;&nbsp;&nbsp;%s<br />"
def InfoErrorRec(title, errorRecs):
	if not errorRecs: return ""
#	fname="import_%s.txt"%(datetime.datetime.now().isoformat().replace(":",""))
#	tmpFile(fname, "\n".join(errorRecs))
	return lineFmt%(_("%(num)d record(s) is duplicated or invalid.") % {'num':len(errorRecs)}) #u"<a href='/iclock/tmp/%s'> %d 条数据</a>为重复或无效记录。<br />"

def reportError(title, i, i_insert, i_update, i_rep, errorRecs):
	info=[]
	if i_insert: info.append(u"%s"%_("Inserted %(object_num)d successfully") % {'object_num':i_insert})
	if i_update: info.append(u"%s"%_("Updated %(object_num)d successfully") % {'object_num':i_update})
	if i_rep: info.append(u"%s"%_(" %(object_num)d already exists in the database")% {'object_num':i_rep})
	result = u"<h2>%s:</h2> <p />%s%s%s<br />" % (title,
		lineFmt%(u"%s"%_("In the data files %(object_num)d  %(object_name)s ")%{'object_num':i,'object_name': u"%s"%_('records')}),
		info and lineFmt%(u", ".join(info)) or "",
		InfoErrorRec(title, errorRecs))
	return result

@login_required
def import_Allowance(request):
	try:
		imFields=[]
		imFieldsInfo={}
		imDatalist=[]
		sUserids=[]
		i_insert=0
		i_update=0
		i_rep=0

		imFields=request.POST["fields"].split(',')
		for t in imFields:
			try:
				imFieldsInfo[t]=int(request.POST.get(t+"2file","-1"))
			except:
				cc=_(u"导入补贴数据失败")+"</p><pre>"
				cc+=request.POST.get(t+"2file","-1")
				return render_to_response("info.html", {"title": _(u"批量上传补贴数据"), "content": cc})
		f=request.FILES["fileUpload"]
		data=""
		fName=f.name
		whatrow=request.POST["whatrowid2file"]
		ext=fName[fName.find('.')+1:].upper()
		for chunk in f.chunks():
			data+=chunk
		lines = []
		if ext=='TXT' or ext=='CSV':
			lines=data.splitlines()
		elif ext=='XLS' or ext=='XLSX':
			import xlrd
#			fn="%s/%s"%(tmpDir(),fName)
			fName=fName.encode("gb2312")
			fn="%s/%s"%(tmpDir(),fName)
			f=file(fn, "wb")
			try:
				f.write(data)
			except:
				pass
			f.close()
			bk = xlrd.open_workbook(fn)
			sheetNames=bk.sheet_names()
			if not sheetNames:
				cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
				return getJSResponse({"ret":1,"message": cc},mtype="text/plain")

			shxrange = range(bk.nsheets)
			try:
				sh = bk.sheet_by_index(0)
			except:
				s="no sheet in %s named %s" %(fn,sheetNames[0])
				cc=u"%s,%s"%(_('imported failed'),s)
				return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
			nrows = sh.nrows
			ncols = sh.ncols
			for i in range(0,nrows):
				sv=[]
				for sr in sh.row_values(i):
					if type(sr)==type(1.0):
						sr=str(long(sr))
						if sr.find(".0")!='-1':
							sr=sr.split(".")[0]
						else:
							sr=sr
					sv.append(sr)
				row_data = sv
				lines.append(row_data)
		jjj=0
		iCount=0
		sqlList=[]
		r=0
		for t in lines:
			r+=1
			if int(whatrow)>r:
				continue
			dDict={}
			if ext=="TXT":
				ls=t.split('\t')
			elif ext=='CSV':
				ls=t.split(',')
			elif ext=='XLS' or ext=='XLSX':
				ls=t
			for k,v in imFieldsInfo.items():
				try:
					if v<1 or v>10:
						continue
				except:
					continue
				if k.lower()=='pin':
					if ext!='XLS' and ext!='XLSX':
						if ls[v-1]==''  or (not ls[v-1].isdigit()):
							dDict={}
							break
					else:
						if ls[v-1]=='' or isinstance(type(ls[v-1]),type(u'1')) or isinstance(type(ls[v-1]),type(1))or isinstance(type(ls[v-1]),type(1.0)):
							dDict={}
							break
						else:
							try:
								ls[v-1]=int(ls[int(v)-1])
							except:
								dDict={}
								break
				if v<=len(ls):
					if ext!='XLS' and ext!='XLSX':
						dDict[k]=getStr_c_decode(ls[int(v)-1])
					else:
						if k.lower()=='valid_date':
							if str(type(ls[int(v)-1]))=="<type 'unicode'>":
								try:
									dDict['valid_date']=datetime.datetime.now().strptime(ls[int(v)-1],"%Y-%m-%d")
								except:
									dDict['valid_date']=datetime.datetime.now().strptime(ls[int(v)-1],"%Y/%m/%d")
							else:
								try:
									iDate = int(ls[int(v)-1])
									lDate=xlrd.xldate_as_tuple(iDate,bk.datemode)
									dDict[k]=datetime.datetime(lDate[0],lDate[1],lDate[2])
								except:
									dDict[k]=''
						else:
							dDict[k]=ls[int(v)-1]
			if dDict!={}:
				jjj+=1
				emp=employee.objects.filter(PIN=dDict['PIN']).exclude(DelTag=1)
				dDict['is_ok']=0
				dDict['is_pass']=1
				dDict['pass_name']=request.user
				dDict['allow_date']=datetime.datetime.now()
				if emp:
					t=IssueCard.objects.filter(UserID=emp[0],cardstatus__in = [CARD_OVERDUE,CARD_VALID])
					if t:
						dDict['batch'] = datetime.datetime.now().strftime("%Y%m")[2:]
						c=Allowance.objects.filter(UserID=emp[0],batch=dDict['batch'])
						if c:
							s=u"人员工号为 %s 的人员本月已经补贴" %(dDict['PIN'])
							cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
							return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
						else:
							dDict['sys_card_no']=t[0].sys_card_no
							dDict['UserID_id']=emp[0].id
							del dDict['PIN']
					else:
						s=u"人员工号为 %s 的人员没有发卡" %(dDict['PIN'])
						cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
						return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
				else:
					s=u"人员工号为 %s 的人员不存在" %(dDict['PIN'])
					cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
					return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
				if dDict['money']:
					dDict['money']=Decimal(dDict['money'])
				sqlList.append(dDict)
		settings.CARDTYPE=int(GetParamValue('ipos_cardtype',2,'ipos'))
		for dDict_n in sqlList:
			sql,params=getSQL_insert_new(Allowance._meta.db_table,dDict_n)
			if customSqlEx(sql,params):
				i_insert+=1
				if settings.CARDTYPE==1:
					u=Allowance.objects.get(UserID=dDict_n['UserID_id'],batch=dDict_n['batch'])
					issuecard = IssueCard.objByCardno(u.UserID.Card,cardstatus=CARD_VALID)
					newblan = issuecard.blance+u.money
					CardCashSZ(UserID=u.UserID,
						card=issuecard.cardno,
						dept_id=u.UserID.DeptID_id,
						checktime=datetime.datetime.now(),
						CashType=CardCashType.objects.get(id=2),#消费类型
						money=u.money,
						hide_column=2,
						allow_type=0,
						blance =newblan,
						).save(force_insert=True)
					issuecard.blance=newblan
					issuecard.save(force_update=True)
					#u.receive_date=datetime.datetime.now()
					#u.receive_money=u.money
					#u.is_ok=1
					#u.save(force_update=True)
				elif settings.CARDTYPE==2:
					devlist=iclock.objects.filter(ProductType__in=[11,12,13]).exclude(DelTag=1)
					datalist=Allowance.objects.filter(UserID=dDict_n['UserID_id'],allow_date=dDict_n['allow_date'],batch=dDict_n['batch'],money=dDict_n['money'])
					set_pos_device_info(devlist,datalist,'',"SUBSIDYLOG")
		result=reportError(u"%s"%_(u"导入补贴数据"), jjj, i_insert, i_update, i_rep, [])
		adminLog(time=datetime.datetime.now(),User=request.user, action=u"%s"%_(u"导入补贴数据"),model = Allowance._meta.verbose_name,object = request.META["REMOTE_ADDR"],count = jjj).save(force_insert = True)
		return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")
	except Exception,e:
		print "import Allowance====%s"%e
		cc=u"<h2>%s</h2>"%_(u"导入补贴数据失败")
		return getJSResponse({"ret":1,"message": cc},mtype="text/plain")


@login_required
def import_Merchandise(request):
	try:
		imFields=[]
		imFieldsInfo={}
		imDatalist=[]
		sUserids=[]
		i_insert=0
		i_update=0
		i_rep=0

		imFields=request.POST.get("fields").split(',')
		for t in imFields:
			try:
				imFieldsInfo[t]=int(request.POST.get(t+"2file","-1"))
			except:
				cc=_(u"导入商品资料失败")+"</p><pre>"
				cc+=request.POST.get(t+"2file","-1")
				return render_to_response("info.html", {"title": _(u"批量上传商品资料"), "content": cc})
		f=request.FILES["fileUpload"]
		data=""
		fName=f.name
		whatrow=request.POST["whatrowid2file"]
		ext=fName[fName.find('.')+1:].upper()
		for chunk in f.chunks():
			data+=chunk
		lines = []
		if ext=='TXT' or ext=='CSV':
			lines=data.splitlines()
		elif ext=='XLS' or ext=='XLSX':
			import xlrd
#			fn="%s/%s"%(tmpDir(),fName)
			fName=fName.encode("gb2312")
			fn="%s/%s"%(tmpDir(),fName)
			f=file(fn, "wb")
			try:
				f.write(data)
			except:
				pass
			f.close()
			bk = xlrd.open_workbook(fn)
			sheetNames=bk.sheet_names()
			if not sheetNames:
				cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
				return getJSResponse({"ret":1,"message": cc},mtype="text/plain")

			shxrange = range(bk.nsheets)
			try:
				sh = bk.sheet_by_index(0)
			except:
				s="no sheet in %s named %s" %(fn,sheetNames[0])
				cc=u"%s,%s"%(_('imported failed'),s)
				return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
			nrows = sh.nrows
			ncols = sh.ncols
			for i in range(0,nrows):
				sv=[]
				for sr in sh.row_values(i):
					if type(sr)==type(1.0):
						sr=str(long(sr))
						if sr.find(".0")!='-1':
							sr=sr.split(".")[0]
						else:
							sr=sr
					sv.append(sr)
				row_data = sv
				lines.append(row_data)
		jjj=0
		iCount=0
		sqlList=[]
		r=0
		
		for t in lines:
			r+=1
			if int(whatrow)>r:
				continue
			dDict={}
			if ext=="TXT":
				ls=t.split('\t')
			elif ext=='CSV':
				ls=t.split(',')
			elif ext=='XLS' or ext=='XLSX':
				ls=t
			for k,v in imFieldsInfo.items():
				try:
					if v<1 or v>10:
						continue
				except:
					continue
				if v<=len(ls):
					if ext!='XLS' and ext!='XLSX':
						dDict[k]=getStr_c_decode(ls[int(v)-1])
					else:
						dDict[k]=ls[int(v)-1]
			if dDict!={}:
				jjj+=1
				dDict['DelTag']=0
				if Merchandise.objects.filter(code=dDict['code']):
					s=u"商品编号为 %s 的商品已使用" %(dDict['code'])
					cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
					return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
				if dDict['money']:
					dDict['money']=Decimal(dDict['money'])
				else:
					dDict['money']=Decimal(0)
				if not dDict['rebate']:
					dDict['rebate']=0
				sql,params=getSQL_insert_new(Merchandise._meta.db_table,dDict)
				if customSqlEx(sql,params):
					i_insert+=1

		result=reportError(u"%s"%_(u"导入商品资料"), jjj, i_insert, i_update, i_rep, [])
		adminLog(time=datetime.datetime.now(),User=request.user, action=u"%s"%_(u"导入商品资料"),model = Merchandise._meta.verbose_name,object = request.META["REMOTE_ADDR"],count = jjj).save(force_insert = True)
		return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")
	except Exception,e:
		print "import Allowance====%s"%e
		cc=u"<h2>%s</h2>"%_(u"导入商品资料失败")
		return getJSResponse({"ret":1,"message": cc},mtype="text/plain")

@login_required
def import_IssueCard(request):
	try:
		imFields=[]
		imFieldsInfo={}
		imDatalist=[]
		sUserids=[]
		i_insert=0
		i_update=0
		i_rep=0
		from mysite.auth_code import auth_code
		try:
			data=GetParamValue('ipos_params','','ipos')
			data=loads(auth_code(data.encode("gb18030")))
			mng_cost=data['mng_cost']
			card_cost=data['card_cost']
		except:
			mng_cost=0
			card_cost=0
		imFields=request.POST["fields"].split(',')
		for t in imFields:
			try:
				imFieldsInfo[t]=int(request.POST.get(t+"2file","-1"))
			except:
				cc=_(u"导入普通卡失败")+"</p><pre>"
				cc+=request.POST.get(t+"2file","-1")
				return render_to_response("info.html", {"title": _(u"批量上传普通卡"), "content": cc})
		f=request.FILES["fileUpload"]
		data=""
		fName=f.name
		whatrow=request.POST["whatrowid2file"]
		ext=fName[fName.find('.')+1:].upper()
		for chunk in f.chunks():
			data+=chunk
		lines = []
		if ext=='TXT' or ext=='CSV':
			lines=data.splitlines()
		elif ext=='XLS' or ext=='XLSX':
			import xlrd
#			fn="%s/%s"%(tmpDir(),fName)
			fName=fName.encode("gb2312")
			fn="%s/%s"%(tmpDir(),fName)
			f=file(fn, "wb")
			try:
				f.write(data)
			except:
				pass
			f.close()
			bk = xlrd.open_workbook(fn)
			sheetNames=bk.sheet_names()
			if not sheetNames:
				cc=u"%s,%s"%(_('imported failed'),_("No Sheet"))
				return getJSResponse({"ret":1,"message": cc},mtype="text/plain")

			shxrange = range(bk.nsheets)
			try:
				sh = bk.sheet_by_index(0)
			except:
				s="no sheet in %s named %s" %(fn,sheetNames[0])
				cc=u"%s,%s"%(_('imported failed'),s)
				return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
			nrows = sh.nrows
			ncols = sh.ncols
			for i in range(0,nrows):
				sv=[]
				for sr in sh.row_values(i):
					if type(sr)==type(1.0):
						sr=str(long(sr))
						if sr.find(".0")!='-1':
							sr=sr.split(".")[0]
						else:
							sr=sr
					sv.append(sr)
				row_data = sv
				lines.append(row_data)
		jjj=0
		iCount=0
		sqlList=[]
		cards=[]
		r=0
		for t in lines:
			r+=1
			if int(whatrow)>r:
				continue
			dDict={}
			if ext=="TXT":
				ls=t.split('\t')
			elif ext=='CSV':
				ls=t.split(',')
			elif ext=='XLS' or ext=='XLSX':
				ls=t

			for k,v in imFieldsInfo.items():
				try:
					if v<1 or v>10:
						continue
				except:
					continue
				if k.lower()=='pin':
					if ext!='XLS' and ext!='XLSX':
						if ls[v-1]==''  or (not ls[v-1].isdigit()):
							dDict={}
							break
					else:
						if ls[v-1]=='' or isinstance(type(ls[v-1]),type(u'1')) or isinstance(type(ls[v-1]),type(1))or isinstance(type(ls[v-1]),type(1.0)):
							dDict={}
							break
						else:
							try:
								ls[v-1]=int(ls[int(v)-1])
							except:
								dDict={}
								break
				if v<=len(ls):
					if ext!='XLS' and ext!='XLSX':
						dDict[k]=getStr_c_decode(ls[int(v)-1])
					else:
						dDict[k]=ls[int(v)-1]
					if k.lower()=='card':
						cards.append(dDict[k])
			if len(cards) != len(list(set(cards))):
				s=u"导入文件中卡号%s有重复"%(cards[-1])
				cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
				return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
			if dDict!={}:
				jjj+=1
				if dDict['balance']:
					dDict['balance']=Decimal(dDict['balance'])
				else:
					dDict['balance']=Decimal(0)
				if card_cost:
					dDict['card_cost']=Decimal(card_cost)
				else:
					dDict['card_cost']=Decimal(0)
				if mng_cost:
					dDict['mng_cost']=Decimal(mng_cost)
				else:
					dDict['mng_cost']=Decimal(0)
				emp=employee.objects.filter(PIN=dDict['PIN']).exclude(DelTag=1)
				if not emp:
					s=u"人员工号为 %s 的人员不存在" %(dDict['PIN'])
					cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
					return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
				IssueCardList=IssueCard.objects.filter(UserID=emp[0],cardstatus__in = [CARD_OVERDUE,CARD_VALID])
				if IssueCardList:
					s=u"人员工号为 %s 的人员已发卡" %(dDict['PIN'])
					cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
					return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
				cardList=IssueCard.objects.filter(cardstatus__in = [CARD_OVERDUE,CARD_VALID]).values_list('cardno',flat=True)
				if dDict['card'] in cardList:
					s=u"卡号为 %s 的卡已在使用" %(dDict['card'])
					cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
					return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
				itype=ICcard.objects.filter(name=dDict['itype'])
				if not itype:
					s=u"消费卡类为 %s 的卡类资料不存在" %(dDict['itype'])
					cc=u"<h2>%s</h2><p style='color:red'>%s</p>"%(_(u'导入失败'),s)
					return getJSResponse({"ret":1,"message": cc},mtype="text/plain")
				dDict['UserID_id']=emp[0].id
				dDict['itype_id']=itype[0].id
				#del dDict['name']
				#del dDict['PIN']
				#del dDict['itype']
				sqlList.append(dDict)
		for dDict_i in sqlList:
			IssueCard(UserID_id=dDict_i['UserID_id'],cardno=dDict_i['card'],card_privage='0',blance=dDict_i['balance'],card_cost=dDict_i['card_cost'],mng_cost=dDict_i['mng_cost'],Password=dDict_i['Password'],itype_id=dDict_i['itype_id']).save(force_insert=True)
			i_insert+=1

		result=reportError(u"%s"%_(u"导入普通卡"), jjj, i_insert, i_update, i_rep, [])
		adminLog(time=datetime.datetime.now(),User=request.user, action=u"%s"%_(u"导入普通卡"),model = IssueCard._meta.verbose_name,object = request.META["REMOTE_ADDR"],count = jjj).save(force_insert = True)
		return getJSResponse({"ret":0,"message": u"%s"%(result)},mtype="text/plain")
	except Exception,e:
		print "import IssueCard====%s"%e
		cc=u"<h2>%s</h2>"%_(u"导入普通卡失败")
		return getJSResponse({"ret":1,"message": cc},mtype="text/plain")