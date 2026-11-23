$env:TM_TRACE = "1"
$env:GCM_SUBCH1_3D = "1"
$env:TM_GAMELOG = "1"
$env:RSX_LIVE_DRAW = "1"
$env:PAD_AUTOPRESS = "1"
$env:TM_SKIP_BANKUNLOAD = "1"
$env:TM_BRB_SILENT = "1"
$env:TM_BRB_PARK = "1"
$env:TM_BRB_ACK = "1"
$env:TM_JQ_WORKERS = "4"
$env:TM_LOADDONE = "5"

$elf = "E:\01 jogos\Emulador ps3\01 roms\twisted\PS3_GAME\USRDIR\EBOOT.elf"
$exe = "D:\Twisted metal\twistedmetal.exe"

$p = Start-Process -FilePath $exe -ArgumentList "`"$elf`"" -WorkingDirectory "D:\Twisted metal" -PassThru -RedirectStandardOutput "D:\Twisted metal\test_advance_out.log" -RedirectStandardError "D:\Twisted metal\test_advance_err.log"

Start-Sleep -Seconds 20

if (-not $p.HasExited) {
    Stop-Process -Id $p.Id -Force
}

$outSize = (Get-Item "D:\Twisted metal\test_advance_out.log").Length
$errSize = (Get-Item "D:\Twisted metal\test_advance_err.log").Length
Write-Host "Test finished. outSize=$outSize, errSize=$errSize"
