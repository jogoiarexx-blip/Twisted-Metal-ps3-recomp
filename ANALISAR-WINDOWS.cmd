@echo off
setlocal
cd /d "%~dp0"
echo Twisted Metal - mapa do EBOOT.elf
set /p "ELF_PATH=Arraste o EBOOT.elf para esta janela e pressione Enter: "
if not defined ELF_PATH exit /b 1
set "ELF_PATH=%ELF_PATH:"=%"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\map_elf.ps1" -ElfPath "%ELF_PATH%" -OutputPath "%~dp0elf-map-local.json"
if errorlevel 1 (
  echo Falha na analise. Confira o caminho e a mensagem acima.
) else (
  echo Relatorio salvo em elf-map-local.json.
)
pause
