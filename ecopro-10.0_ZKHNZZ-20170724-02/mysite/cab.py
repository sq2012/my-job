import os
import zipfile
import time
import fnmatch
import threading
# def decryption( s, key = 101):
#     if not s:
#         return ''
#     s = s.strip()
#     c = bytearray( str(s).encode("utf-8") )
#     n = len(c)
#     if n % 2 != 0 :
#         return None
#     n = n // 2
#     b = bytearray( n )
#     j = 0
#     for i in range( 0, n ):
#         c1 = c[j]
#         c2 = c[j+1]
#         j = j+2
#         c1 = c1 - 65
#         c2 = c2 - 65
#         b2 = c2*16 + c1
#         b1 = b2^ key
#         b[i]= b1
#     try:
#       return b.decode("utf-8")
#     except:
#       return None	

def tmpDir():
	ret=os.path.split(__file__)[0]
	if ret: 
		ret=ret+"/Release"
	else:
		ret=os.getcwd()+"/Release"
	try:
		os.makedirs(ret)
	except: pass
	return ret


def famatch(fn, matches):
	for m in matches:
		if fnmatch.fnmatch(fn, m):
			return True
	return False

def zipDir(source_dir, target_file, match=['*'], exclude_dirs=[], exclude_files=[]):
	myZipFile = zipfile.ZipFile(target_file, 'w' )
	for root,dirs,files in os.walk(source_dir):
		for xdir in exclude_dirs:
			if xdir in dirs:
				dirs.remove(xdir)
		if files:
			files=filter(lambda f: famatch(f, match), files)
			files=filter(lambda f: not famatch(f, exclude_files), files)
			for vfileName in files:
				vf=vfileName
				if vf=='manage.pyc':vf='manage.py'
				fileName = os.path.join(root,vf)
				myZipFile.write( fileName, fileName, zipfile.ZIP_DEFLATED )
	myZipFile.close()

def listFile(source_dir, match=['*'], exclude_dirs=[], exclude_files=[]):	
	fl=[]
	for root,dirs,files in os.walk(source_dir):
		for xdir in exclude_dirs:
			if xdir in dirs:
				dirs.remove(xdir)
		if files:
			files=filter(lambda f: famatch(f, match), files)
			files=filter(lambda f: not famatch(f, exclude_files), files)
			for vfileName in files:
				fl.append(os.path.join(root,vfileName))
	return fl

def unzipFile(source_file, target_dir):
	fl={}
	if not os.path.exists(target_dir):
		os.mkdir(target_dir)
	if target_dir[-1] not in ["/","\\"]:
		target_dir+="/"									
	z=zipfile.ZipFile(source_file, 'r')
	for fn in z.namelist():
		bytes=z.read(fn)
		filename=target_dir+fn
#		print filename
		if (len(bytes)==0) and (fn[-1] in ["/","\\"]):					 
			try:
				os.makedirs(filename)
			except: pass
		else:
			try:
				os.makedirs("/".join(filename.split('/')[:-1]))
			except: pass
			file(filename,"wb+").write(bytes)
			fl[filename]=len(bytes)
	return fl

def restartSvr(svrName):
	os.system("cmd /C net stop %s & net start %s"%(svrName, svrName))

class restartThread(threading.Thread):
	def __init__(self, svrName):
		threading.Thread.__init__(self)
		self.svrName=svrName
	def run(self):
		time.sleep(2)
		restartSvr(self.svrName)

def exportMysite():
	import compileall
	old=os.getcwd()
	compileall.compile_dir(old)
	zipDir(old, tmpDir()+'/mysite.zip', ['*'], ['data', '.hg','_svn','.svn','photologue','photos','lzo','upload','tmp','Release'], ['.*','icdat.db','*.swp','*.py','*.orig','*.zip','options.txt','l.txt','*.log','*.sql', '*.7z', '*.doc', 'tftpgui.cfg', 'oracle9'])
	try:
		os.removedirs(tmpDir()+"/mysite")
	except: pass
	unzipFile(tmpDir()+'/mysite.zip', tmpDir()+"/mysite/")
	#file(tmpDir()+"/mysite/manage.py","w+").write(file("manage.py","r").read())
	os.chdir(tmpDir()+"/")										
	#zipDir('mysite/', tmpDir()+'/mysite.zip')
	os.remove('mysite.zip')
	os.chdir(old)

if __name__=="__main__":
#	os.chdir("../")
	exportMysite()

