@echo off
cd /d %~dp0
cd ../
call init.bat
python manage.py migrate --run-syncdb


