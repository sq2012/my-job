cls
@echo off
cd /d %~dp0

echo "Install memcached ..."
sc create memcached binPath= "%CD%\memcached\memcached.exe -p 11211 -l 127.0.0.1 -m 256 -d runservice" DisplayName= "ZKEco-cached" start= auto depend= TCPIP
net start memcached
pause

