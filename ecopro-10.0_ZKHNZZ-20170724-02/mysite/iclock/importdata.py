#!/usr/bin/env python
#coding=utf-8
from __future__ import division
from mysite.iclock.models import *
from mysite.core.tools import *
from django.template import loader, Context, RequestContext, Library, Template, Context
from django.conf import settings
#from iclock.devview import checkDevice, commitLog
from mysite.iclock.iutils import getUserIclocks
from django.shortcuts import render_to_response
import time, datetime
from django.utils.translation import ugettext_lazy as _
from django.utils import *

lineFmt=u"&nbsp;&nbsp;&nbsp;&nbsp;%s<br />"

def InfoErrorRec(title, errorRecs):
	if not errorRecs: return ""
	time.sleep(0.1)
	fname="import_%s.txt"%(datetime.datetime.now().isoformat().replace(":",""))
	tmpFile(fname, "\n".join(errorRecs))
	return lineFmt%(_("<a href='/iclock/tmp/%(object_name)s'> %(num)d record(s) is duplicated or invalid.") % {'object_name':fname, 'num':len(errorRecs)}) #u"<a href='/iclock/tmp/%s'> %d 条数据</a>为重复或无效记录。<br />"

def reportError(title, i, i_insert, i_update, i_rep, errorRecs):
	info=[]
	if i_insert: info.append(u"%s"%_("Inserted %(object_num)d successfully") % {'object_num':i_insert})
	if i_update: info.append(u"%s"%_("Updated %(object_num)d successfully") % {'object_num':i_update})
	if i_rep: info.append(u"%s"%_(" %(object_num)d already exists in the database")% {'object_num':i_rep})
	result = u"<h2>%s:</h2> <br />%s%s%s<br />" % (title,
		lineFmt%(u"%s"%_("In the data files %(object_num)d  %(object_name)s ")%{'object_num':i,'object_name': u"%s"%_('records')}),
		info and lineFmt%(u", ".join(info)) or "",
		InfoErrorRec(title, errorRecs))
	return result

from iclock.validdata import checkRecData,checkALogData				 

def checkAndRunSql(cursor, sqlList, sql=None):
	error=[]
	if sql:
		sqlList.append(sql)
	if cursor and sqlList:
		if (not sql) or (len(sqlList)>=100):
			print "Post:", len(sqlList)
			try:
				commitLog(cursor, '; '.join(sqlList))
			except Exception, er:
#				print er
				for s in sqlList:
					try:
						from django.db import connection as conn
#						cursor=conn.cursor()
						cursor.execute(s)
#						conn._commit()
					except Exception, e:
						emsg="SQL '%s' Failed: %s"%(s,e)
#						print emsg
						error.append(emsg)
			for s in range(len(sqlList)): sqlList.pop()
	return error
#		typedef struct _User_{		//size:72
#			U16 PIN;				//[:2]
#			U8 Privilege;			//[2:3]		Privilege
#			char Password[8];		//[3:11]	Password
#			char Name[24];			//[11:35]	EName
#			U8 Card[4];				//[35:39]					//卡号码，用于存储对应的ID卡的号码
#			U8 Group;				//[39:40]	AccGroup		//用户所属的分组
#			U16 TimeZones[4];		//[40:48]	TimeZones		//用户可用的时间段，位标志
#			char PIN2[24];			//[48:]		PIN
#		}GCC_PACKED TUser, *PUser;			

