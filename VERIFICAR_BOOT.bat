@echo off
title Twisted Metal - Verificacao de Boot PPU
cd /d "%~dp0"

echo ========================================================
echo       Twisted Metal - Teste de Boot Probe
echo ========================================================
echo.

set "ELF_PATH=E:\01 jogos\Emulador ps3\01 roms\twisted\PS3_GAME\USRDIR\EBOOT.elf"
if not exist "%ELF_PATH%" (
    echo Informe o caminho do EBOOT.elf:
    set /p ELF_PATH="Caminho: "
)

echo Executando recomp\boot_probe.exe com %ELF_PATH%...
recomp\boot_probe.exe "%ELF_PATH%"
echo.
pause
