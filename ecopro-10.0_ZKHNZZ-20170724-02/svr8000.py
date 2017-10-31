#import site
import wsgiserver
import os
import sys
#import django.core.handlers.wsgi


import threading
import time
from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

class server():
	server_type='Simple'
	def __init__(self, configFile='attsite.ini'):
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
		#os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
		p=settings.FILEPATH
		self.p=p
		os.environ['PATH']="%(p)s\\apache\\bin;%(p)s\\Python27;"%{"p":p}+os.environ['PATH']
		newpath="%INSTALL_PATH%\\mssql;%INSTALL_PATH%\\ibm_db_django;%INSTALL_PATH%\\Python27;%INSTALL_PATH%\\Python27\\Lib\\site-packages;%INSTALL_PATH%".replace('%INSTALL_PATH%',p).split(";")
		for p in newpath:
			if p not in sys.path:
				sys.path.append(p)
#		print "sys.path:", sys.path

		#gprint "---------",settings.SERVER_PORT		
		self.address='0.0.0.0:80'
		self.numthreads=50
		self.queue_size=400
			
		self.address="%s:%s"%('0.0.0.0', settings.SERVER_PORT)
		self.server_type=(settings.SERVER_TYPE).lower()
		#self.numthreads=cfg.Options.NumThreads or self.numthreads
		#self.queue_size=cfg.Options.QueueSize or self.queue_size

		print "Start Automatic Data Master Server ... ...\nOpen your web browser and go http://%s"%(self.address.replace("0.0.0.0","127.0.0.1"))+"/"

	def runWSGIServer(self):	
#		print "runWSGIServer"
		if self.server_type!='wsgi':return
		address=tuple(self.address.split(":"))
		wserver = wsgiserver.CherryPyWSGIServer(
			(address[0], int(address[1])),
			application,
			server_name='www.bio-iclock.com',
			numthreads = self.numthreads,
			request_queue_size=self.queue_size,
		)
		try:
			wserver.start()
		except KeyboardInterrupt:
			wserver.stop()

	def runSimpleServer(self):
#		print "runSimpleServer"
		from django.core.management import execute_manager
		execute_manager(settings, [self.p+'/manage.py', 'runserver', self.address])
	

	def run(self):
		self.runWSGIServer()
		if self.server_type=='simple': self.runSimpleServer()
if __name__ == "__main__":
	config="attsite.ini"
	server(config).run()
	
