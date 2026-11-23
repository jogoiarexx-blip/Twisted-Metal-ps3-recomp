# Twisted Metal (2012) PS3 Native Recompilation Launcher
# BCUS98106 - Base Disc 1.00

$discPaths = @(
    "E:\01 jogos\Emulador ps3\01 roms\twisted\PS3_GAME\USRDIR\EBOOT.elf",
    ".\PS3_GAME\USRDIR\EBOOT.elf",
    ".\input\EBOOT.elf",
    ".\EBOOT.elf"
)

$targetElf = $null
foreach ($path in $discPaths) {
    if (Test-Path $path) {
        $targetElf = (Resolve-Path $path).Path
        break
    }
}

if (-not $targetElf) {
    Write-Host "ERRO: EBOOT.elf do Twisted Metal 1.00 nao encontrado." -ForegroundColor Red
    Write-Host "Certifique-se de que o dump do disco PS3_GAME esteja disponivel." -ForegroundColor Yellow
    exit 1
}

Write-Host "Iniciando Twisted Metal Nativo com EBOOT: $targetElf" -ForegroundColor Green

# Parametros de runtime para estabilidade de audio, SPURS e RSX
$env:TM_GAMELOG = "1"
$env:RSX_LIVE_DRAW = "1"
$env:GCM_SUBCH1_3D = "1"
$env:PAD_AUTOPRESS = "1"
$env:TM_SKIP_BANKUNLOAD = "1"
$env:TM_BRB_SILENT = "1"
$env:TM_BRB_PARK = "1"
$env:TM_BRB_ACK = "1"
$env:TM_JQ_WORKERS = "4"
$env:TM_LOADDONE = "5"
$env:TM_VIDEO_MODES = "2,1"

& ".\twistedmetal.exe" "$targetElf"
