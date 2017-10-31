@echo off
cd /d %~dp0
cd ../
call init.bat
python ConnDb.py

