import uuid
import os
import django
django.setup()
from django.db import  connection
from django.conf import settings
fn=settings.ADDITION_FILE_ROOT+'\conn_logs.zk'
try:
	os.remove(fn)
except:pass

LMAC=uuid.uuid1().hex[-12:].lower()
print "mac=%s"%LMAC
s=''
try:
	cursor=connection.cursor()
	print "connect successfully"
	s="connect successfully"
except Exception as e:
	s='%s'%e
	print "connect failed:",s
	
	s="connect failed:"+s
from mysite.utils import saveToFile
saveToFile(fn,s)