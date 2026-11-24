Add-Type -AssemblyName System.Drawing

function Convert-BmpToPng($bmp, $png) {
    if (Test-Path $bmp) {
        $img = [System.Drawing.Image]::FromFile($bmp)
        $img.Save($png, [System.Drawing.Imaging.ImageFormat]::Png)
        $img.Dispose()
        Write-Host "Converted $bmp -> $png"
    }
}

$dir = "C:\Users\luis\.gemini\antigravity\brain\e0d02404-d211-4bb2-807a-b2befe488b48"
Convert-BmpToPng "$dir\frame_latest_190.bmp" "$dir\frame_latest_190.png"
