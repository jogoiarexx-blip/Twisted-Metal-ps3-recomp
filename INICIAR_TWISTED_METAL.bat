@echo off
title Twisted Metal (2012) - Recompilacao Nativa PC
cd /d "%~dp0"

echo ========================================================
echo    Twisted Metal (2012) - Port Nativo PC (D3D12/x64)
echo ========================================================
echo.
echo [1/3] Configurando variaveis de ambiente e controles...
set TM_TRACE=0
set GCM_SUBCH1_3D=1
set TM_GAMELOG=1
set RSX_LIVE_DRAW=1
rem Controles: PAD_AUTOPRESS=0 permite jogar direto no teclado (WASD, Espaco, Enter, Esc) e Gamepad.
rem Defina PAD_AUTOPRESS=1 se quiser que o jogo pule telas e cinemáticas automaticamente.
set PAD_AUTOPRESS=0
set PAD_FORCE_FOCUS=1
set TM_SKIP_BANKUNLOAD=1
set TM_BRB_SILENT=1
set TM_BRB_PARK=1
set TM_BRB_ACK=1
set TM_JQ_WORKERS=4
rem TM_LOADDONE intentionally not set: the 5 s load-complete probe makes ~1/3 of boots diverge.
set TM_VIDEO_MODES=2,1
set TM_FORCEWORLD=15,direct
set TM_RSX_W=1280
set TM_RSX_H=720

echo [2/3] Verificando executavel e arquivos do jogo...
if not exist "twistedmetal.exe" (
    echo ERRO: twistedmetal.exe nao encontrado no diretorio!
    pause
    exit /b 1
)

set "ELF_PATH=E:\01 jogos\Emulador ps3\01 roms\twisted\PS3_GAME\USRDIR\EBOOT.elf"
if not exist "%ELF_PATH%" (
    echo AVISO: EBOOT.elf nao encontrado no caminho padrao E:\...
    echo Tentando carregar executavel direto...
    twistedmetal.exe
) else (
    echo [3/3] Iniciando Twisted Metal com EBOOT.elf...
    twistedmetal.exe "%ELF_PATH%"
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro durante a execucao. Codigo: %ERRORLEVEL%
    pause
)
