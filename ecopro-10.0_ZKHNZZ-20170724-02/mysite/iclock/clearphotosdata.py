#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
import os
import shutil

def clearPhotos(strdate,date,photodir):
	try:
		l=str(date).split("-")
	except:
		return False
	try:
		ll=str(strdate).split("-")
	except:
		return False
	day=int('%s%s%s'%(l[0],l[1],l[2]))
	day1=int('%s%s%s'%(ll[0],ll[1],ll[2]))
	devs=iclock.objects.all().order_by("SN")
	try:
		for dev in devs:
			dir=photodir+dev.SN
			if os.path.exists(dir):
				dirs=os.listdir(dir)
				if len(dirs)==0:
					continue
				for w in dirs:
					if(int(w[:8])>=day1 and int(w[:8])<=day):
						os.remove(dir+"\\"+w)
	except:
		return False
	return True
