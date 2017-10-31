cls
@echo off
call init.bat

if EXIST mysql call installmysql.bat


echo "Install memcached ..."
sc create memcached binPath= "%CD%\memcached\memcached.exe -p 11211 -l 127.0.0.1 -m 128 -d runservice" DisplayName= "memcached server" start= auto depend= TCPIP
net start memcached

