@echo off
setlocal
cd /d "%~dp0"
where cl >nul 2>nul
if not errorlevel 1 goto msvc
where g++ >nul 2>nul
if not errorlevel 1 goto mingw
echo ERRO: compilador C++ nao encontrado. Abra o Developer Command Prompt do Visual Studio ou instale g++.
goto error
:msvc
cl /nologo /std:c++17 /EHsc /O2 /Fe:boot_probe.exe entry.cpp startup2.cpp startup3.cpp startup4.cpp boot_probe.cpp
if errorlevel 1 goto error
goto run
:mingw
g++ -std=c++17 -O2 -Wall -Wextra entry.cpp startup2.cpp startup3.cpp startup4.cpp boot_probe.cpp -o boot_probe.exe
if errorlevel 1 goto error
:run
if "%~1"=="" (
  echo Compilado boot_probe.exe. Arraste o EBOOT.elf da atualizacao 1.06 para este CMD.
) else (
  boot_probe.exe "%~1"
)
pause
exit /b 0
:error
echo Falha. Copie o erro desta janela.
pause
exit /b 1
