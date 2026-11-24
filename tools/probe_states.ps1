$env:TM_GAMELOG = "1"
$env:TM_FORCESTATE = "list"
$env:TM_SKIP_BANKUNLOAD = "1"
$env:TM_BRB_SILENT = "1"
$env:TM_BRB_PARK = "1"
$env:TM_BRB_ACK = "1"
$env:TM_JQ_WORKERS = "4"
$env:TM_LOADDONE = "5"

$elf = "E:\01 jogos\Emulador ps3\01 roms\twisted\PS3_GAME\USRDIR\EBOOT.elf"
$exe = "D:\Twisted metal\twistedmetal.exe"

$p = Start-Process -FilePath $exe -ArgumentList "`"$elf`"" -WorkingDirectory "D:\Twisted metal" -PassThru -RedirectStandardOutput "D:\Twisted metal\test_states_out.log" -RedirectStandardError "D:\Twisted metal\test_states_err.log"
Start-Sleep -Seconds 12
if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force }
Select-String -Path "D:\Twisted metal\test_states_err.log" -Pattern "\[states\]"
