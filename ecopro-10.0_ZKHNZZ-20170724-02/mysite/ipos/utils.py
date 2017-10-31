# -*- coding: utf-8 -*-
#import traceback
import string
import datetime
import os
import shutil 
#from django.http import HttpResponse
#from django.conf import settings
#from django.utils.encoding import smart_str
import json

def enc(s):
    ser="zksoft"
    ret=""
    for k in range(6):
          ret += chr(ord(s[k])^ord(ser[k]))
    return ret
