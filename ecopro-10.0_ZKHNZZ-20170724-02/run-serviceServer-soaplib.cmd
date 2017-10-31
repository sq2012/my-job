if {%1}=={} GOTO noparms
set p=%1\
goto param1

:noparms
set p=%CD%\

:param1
call %p%init.bat %p%


IF EXIST %p%mysite\api\soaplib_server.py GOTO py
 
python.exe %p%mysite\api\soaplib_server.pyc
GOTO end

:py
python.exe %p%mysite\api\soaplib_server.py

:end
pause
