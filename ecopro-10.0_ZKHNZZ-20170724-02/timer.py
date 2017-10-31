#!/usr/bin/env python
#coding=utf-8
import os,sys
p=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
os.environ['PATH']="%(p)s\\Python27;"%{"p":p}+os.environ['PATH']
newpath="%INSTALL_PATH%\\Python27;%INSTALL_PATH%\\Python27\\Lib\\site-packages;%INSTALL_PATH%".replace('%INSTALL_PATH%',p).split(";")
for t in newpath:
	if t not in sys.path:
		sys.path.append(t)
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
import django
django.setup()

import datetime
from mysite.schedulers import *
#import logging
#logging.basicConfig()
            

if __name__ == '__main__':
	Run_Tasks()


