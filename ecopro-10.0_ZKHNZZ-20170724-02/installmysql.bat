echo installing mysql database server ...
cd /d %~dp0
cd mysql
"%CD%\bin\mysqld.exe" --install ZKEco-mysql --defaults-file="%CD%\my.ini"
net start ZKEco-mysql
cd ../
pause
