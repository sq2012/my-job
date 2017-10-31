@echo off
call init.bat
@for /L %%i IN (0,1,2000) DO @python manage.py runserver 0.0.0.0:81