#!/usr/bin/env python
#coding=utf-8
import os,sys
#import dict4ini
import django
django.setup()
from mysite.iclock.models import *
from mysite.core.tools import getSQL_update_new,getSQL_insert_new
from django.conf import settings
from django.core.cache import cache
import datetime
from django.db import connection,connections
from mysite.iclock.dataproc import deptEmptoDev
from mysite.iclock.dataproc import trunc
from mysite.utils import *
#from mysite.iclock.datas import MainCalc,GetLeaveClassesEx1,FindSchClassByID
from mysite.iclock.iutils import getAllAuthChildDept
from django.db import transaction as tran
def savelogFile(text,filename='departments'):
	"""保存错误日志，保存路径为安装目录\files\logs"""
	ret="%s/logs/%s"%(settings.ADDITION_FILE_ROOT,filename)
	try:
		os.makedirs(ret)
	except: pass
	fn="%s/logs_%s.txt"%(ret,datetime.datetime.now().strftime("%Y%m%d"))
	f=file(fn,"a+")
	try:
		f.write(text)
	except:
		pass
	f.write("\n")
	f.close()			 
	return fn

@tran.atomic
def batchSqls(sqls):
	for s in sqls:
		customSql(s,False)
#		    name="sql"+datetime.datetime.now().strftime("%Y%m%d")
#		    tmpFile(name,s)
	tran.rollback()
def getSQL_inser(table, Dict={},**kwargs):
	""" 生成 insert SQL 语句
		"""
	ks = ""
	vs = ""
	kvs=[]
	if not Dict:Dict=kwargs
	#print "-----",Dict
	for k, v in Dict.items():
		ks += k + ","
		vs+="%s"+','
		#if v==None:
		#	v='null'
		#if str(type(v))=="<type 'datetime.datetime'>":
		#	print "111111111111111"
		#	kvs.append(v)
		#elif str(type(v))=="<type 'datetime.time'>":
		#	if settings.DATABASE_ENGINE == 'oracle':
		#		v1+="TIMESTAMP'1899-12-30 "+v.strftime('%H:%M:%S')+"',"
		#	else:
		#		v1+="'"+v.strftime('%H:%M:%S')+"',"
		#	kvs.append(v1)
		#elif isNumber(v) or v == "null":
		#	kvs.append(v)
		#else:
		kvs.append(v)
#	print "33333333333333333"
	ret_sql="""INSERT INTO %s (%s) VALUES (%s)""" % (table, ks[:-1],vs[:-1])
	return ret_sql,tuple(kvs)

def c_table():
	ww=""
	de=datetime.datetime.now()
	print "begin time111111==",de
	ww+='creat table:%s'%de
	if settings.DATABASE_ENGINE=='oracle':
		sql='''CREATE TABLE c_test (RESERVED NVARCHAR2(100) NULL,id int,ATTDATE TIMESTAMP NOT NULL)'''
	else:
		sql='''CREATE TABLE c_test (RESERVED VARCHAR(100) NULL,id int)'''
		
	customSql(sql)
	#d={'reserved':None,'id':5,'attdate':datetime.datetime.now()}
	#sql,params=getSQL_inser('c_test',d,reserved=None,id=4,attdate=datetime.datetime.now())
	#print "====",sql,params
	#customSqlEx(sql,params)
	de=datetime.datetime.now()
	ww+='insert start:%s'%de
	sqls=[]
	for i in range(10000):
		sql="insert into c_test(RESERVED,id) values('%s',%s)"%(datetime.datetime.now(),i)
		sqls.append(sql)
		customSql(sql,True)
		#print "9999999",i
	#batchSqls(sqls)
	sqls=[]
	#for i in range(10000):
		#sql="update c_test set reserved=%s where id=%s"%(10000-i,i)
		#print sql
	#	sqls.append(sql)
		#customSql(sql,True)
	#batchSqls(sqls)
		

	sql='''drop TABLE c_test'''
	#customSql(sql)
	de=datetime.datetime.now()-de
	print "waste time==%s sec"%(de.total_seconds())
	ww+='end:%s'%de
	d1=datetime.datetime.now()
	sql="select * from c_test"
	#cs=customSql(sql)
	#d2=datetime.datetime.now()-d1
	#print d2,len(cs.fetchall()),"4444444444444444"
	#print "-------",ww
	#savelogFile(ww,'c_table')
	#close_connection()
if __name__=='__main__':
	try:
		c_table()
		#pass
	except Exception,e:
		savelogFile(str(e),'c_table')
	#objs=transactions.objects.filter(id__gt=0)
	#print objs,"===="