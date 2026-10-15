@echo off
setlocal
cd /d "%~dp0"
where cl >nul 2>nul
if not errorlevel 1 goto msvc
where g++ >nul 2>nul
if not errorlevel 1 goto mingw
echo ERRO: nenhum compilador C++ encontrado. Use Developer Command Prompt ou MinGW g++.
goto error
:msvc
cl /nologo /std:c++17 /EHsc /O2 /Fe:lv2_memory_test.exe lv2_memory_test.cpp
if errorlevel 1 goto error
goto run
:mingw
g++ -std=c++17 -O2 -Wall -Wextra -Werror lv2_memory_test.cpp -o lv2_memory_test.exe
if errorlevel 1 goto error
:run
lv2_memory_test.exe
if errorlevel 1 goto error
echo Testes LV2 concluidos. Para testar com ELF real use COMPILAR-WINDOWS.cmd
pause
exit /b 0
:error
echo Teste LV2 falhou. Leia as mensagens acima.
pause
exit /b 1
