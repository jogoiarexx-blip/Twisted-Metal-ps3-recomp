@echo off
setlocal
cd /d "%~dp0"
set PATH=C:\msys64\mingw64\bin;%PATH%

echo ============================================================
echo   Twisted Metal PS3 Recomp - Native Windows Boot Probe
echo ============================================================
echo.

if not exist "recomp\boot_probe.exe" (
    echo [INFO] Compilando boot_probe.exe com g++...
    cd recomp
    g++ -std=c++17 -O2 -Wall -Wextra entry.cpp startup2.cpp startup3.cpp startup4.cpp heap_init.cpp boot_probe.cpp -o boot_probe.exe
    if errorlevel 1 (
        echo [ERRO] Falha ao compilar boot_probe.exe.
        pause
        exit /b 1
    )
    cd ..
)

echo [OK] Executando boot_probe.exe com o EBOOT.elf real:
echo.
recomp\boot_probe.exe "BCUS98106\USRDIR\EBOOT.elf"
echo.
echo ============================================================
pause
