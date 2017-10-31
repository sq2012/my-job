cls
@echo off
call init.bat


sc stop memcached
@ping -n 3 127.1 >nul 2>nul
sc start memcached
n: