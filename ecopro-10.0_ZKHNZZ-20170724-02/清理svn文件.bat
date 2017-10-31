@echo off
set SrcDir=d:\zksoftware\zknet902
for /f "tokens=1* delims=" %%a in ('dir /s /b /ad "%SrcDir%" ^| findstr /i ".svn$"') do (
  rd /s /q "%%a"
)
pause