param(
    [Parameter(Mandatory=$true)][string]$ElfPath,
    [Parameter(Mandatory=$true)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
try {
    $ElfPath = $ElfPath.Trim('"')
    $b = [System.IO.File]::ReadAllBytes($ElfPath)
    function U32([long]$i) {
        if ($i -lt 0 -or $i + 4 -gt $b.Length) { throw 'Leitura fora do arquivo' }
        [uint64]$v = 0
        for ($j=0; $j -lt 4; $j++) { $v = ($v -shl 8) -bor [uint64]$b[$i+$j] }
        return $v
    }
    function U64([long]$i) { return ((U32 $i) -shl 32) -bor (U32 ($i+4)) }
    if ($b.Length -lt 64 -or $b[0] -ne 127 -or $b[1] -ne 69 -or $b[2] -ne 76 -or $b[3] -ne 70 -or $b[4] -ne 2 -or $b[5] -ne 2) {
        throw 'O arquivo nao e ELF64 big endian'
    }
    if ($b[18] -ne 0 -or $b[19] -ne 21) { throw 'O arquivo nao e PowerPC64' }
    $entry = U64 24
    $phoff = U64 32
    $phsize = ([int]$b[54] -shl 8) -bor $b[55]
    $phnum = ([int]$b[56] -shl 8) -bor $b[57]
    if ($phsize -lt 56 -or $phoff + $phsize*$phnum -gt $b.Length) { throw 'Cabecalhos ELF invalidos' }
    $segs = [System.Collections.Generic.List[object]]::new()
    for ($i=0; $i -lt $phnum; $i++) {
        $p = [long]($phoff + $i*$phsize)
        if ((U32 $p) -ne 1) { continue }
        $s = [pscustomobject]@{offset=(U64 ($p+8)); vaddr=(U64 ($p+16)); filesz=(U64 ($p+32)); memsz=(U64 ($p+40)); flags=(U32 ($p+4))}
        if ($s.offset + $s.filesz -gt $b.Length) { throw 'Segmento ultrapassa o arquivo' }
        $segs.Add($s)
    }
    $entryOff = $null
    foreach ($s in $segs) {
        if ($entry -ge $s.vaddr -and $entry + 8 -le $s.vaddr + $s.filesz) {
            $entryOff = [long]($s.offset + $entry - $s.vaddr); break
        }
    }
    if ($null -eq $entryOff) { throw 'Descritor de entrada nao esta no arquivo' }
    $code = U32 $entryOff
    $toc = U32 ($entryOff + 4)
    $exec = @($segs | Where-Object { ($_.flags -band 1) -ne 0 })
    if (@($exec | Where-Object { $code -ge $_.vaddr -and $code -lt $_.vaddr + $_.filesz }).Count -eq 0) { throw 'Entrada nao aponta para codigo' }
    $descriptors = [System.Collections.Generic.List[object]]::new()
    foreach ($s in $segs) {
        if (($s.flags -band 2) -eq 0) { continue }
        for ([long]$p=$s.offset; $p+8 -le $s.offset+$s.filesz; $p+=4) {
            if ((U32 ($p+4)) -ne $toc) { continue }
            $target = U32 $p
            if (($target -band 3) -ne 0) { continue }
            foreach ($xs in $exec) {
                if ($target -ge $xs.vaddr -and $target -lt $xs.vaddr+$xs.filesz) {
                    $descriptors.Add([pscustomobject]@{descriptor=('0x{0:x8}' -f ($s.vaddr+$p-$s.offset)); code=('0x{0:x8}' -f $target)})
                    break
                }
            }
        }
    }
    $sha = (Get-FileHash -LiteralPath $ElfPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $report = [ordered]@{
        input_sha256=$sha; input_size=$b.Length; machine='PowerPC64 big-endian'
        entry_descriptor=('0x{0:x8}' -f $entry); entry_code=('0x{0:x8}' -f $code); entry_toc=('0x{0:x8}' -f $toc)
        descriptor_count=$descriptors.Count; descriptors=$descriptors.ToArray()
        caveat='Candidatos a descritores; nao sao funcoes recompiladas.'
    }
    $report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Host ("Concluido: {0} candidatos; entrada 0x{1:x8}" -f $descriptors.Count,$code)
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
