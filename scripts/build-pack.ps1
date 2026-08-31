[CmdletBinding()]
param(
    [string] $BasePack,
    [string] $OverlayRoot,
    [string] $OutputPack
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repositoryRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($BasePack)) {
    $BasePack = Join-Path $repositoryRoot 'base/ViksStuff-Pack.base.zip'
}
if ([string]::IsNullOrWhiteSpace($OverlayRoot)) {
    $OverlayRoot = Join-Path $repositoryRoot 'overlay'
}
if ([string]::IsNullOrWhiteSpace($OutputPack)) {
    $OutputPack = Join-Path $repositoryRoot 'ViksStuff-Pack.zip'
}

$basePath = [System.IO.Path]::GetFullPath($BasePack)
$overlayPath = [System.IO.Path]::GetFullPath($OverlayRoot)
$outputPath = [System.IO.Path]::GetFullPath($OutputPack)
$temporaryPath = "$outputPath.tmp"

if (-not [System.IO.File]::Exists($basePath)) {
    throw "Base pack does not exist: $basePath"
}
if (-not [System.IO.Directory]::Exists($overlayPath)) {
    throw "Overlay directory does not exist: $overlayPath"
}
if ([System.StringComparer]::OrdinalIgnoreCase.Equals($basePath, $outputPath)) {
    throw 'BasePack and OutputPack must be different files'
}

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$entries = [System.Collections.Generic.SortedDictionary[string, byte[]]]::new(
    [System.StringComparer]::Ordinal
)
$casePaths = [System.Collections.Generic.Dictionary[string, string]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)

function Assert-SafeEntryPath {
    param([string] $EntryPath)

    if (
        [string]::IsNullOrWhiteSpace($EntryPath) -or
        $EntryPath.StartsWith('/') -or
        $EntryPath.StartsWith('../') -or
        $EntryPath.Contains('/../') -or
        $EntryPath.Contains('\')
    ) {
        throw "Unsafe ZIP entry path: $EntryPath"
    }
}

function Add-PackEntry {
    param(
        [string] $EntryPath,
        [byte[]] $Bytes,
        [bool] $AllowReplacement
    )

    Assert-SafeEntryPath $EntryPath
    if ($casePaths.ContainsKey($EntryPath) -and $casePaths[$EntryPath] -cne $EntryPath) {
        throw "Case-insensitive path collision: $EntryPath conflicts with $($casePaths[$EntryPath])"
    }
    if ($entries.ContainsKey($EntryPath) -and -not $AllowReplacement) {
        throw "Duplicate base ZIP entry: $EntryPath"
    }

    $casePaths[$EntryPath] = $EntryPath
    $entries[$EntryPath] = $Bytes
}

$baseArchive = [System.IO.Compression.ZipFile]::OpenRead($basePath)
try {
    foreach ($entry in $baseArchive.Entries) {
        if ($entry.FullName.EndsWith('/')) {
            continue
        }

        $entryStream = $entry.Open()
        try {
            $memory = [System.IO.MemoryStream]::new()
            try {
                $entryStream.CopyTo($memory)
                Add-PackEntry $entry.FullName $memory.ToArray() $false
            }
            finally {
                $memory.Dispose()
            }
        }
        finally {
            $entryStream.Dispose()
        }
    }
}
finally {
    $baseArchive.Dispose()
}

$overlayFiles = @(
    Get-ChildItem -LiteralPath $overlayPath -Recurse -File |
        Sort-Object FullName
)
foreach ($file in $overlayFiles) {
    $relativePath = [System.IO.Path]::GetRelativePath($overlayPath, $file.FullName).Replace('\', '/')
    Add-PackEntry $relativePath ([System.IO.File]::ReadAllBytes($file.FullName)) $true
}

if (-not $entries.ContainsKey('pack.mcmeta')) {
    throw 'Merged pack is missing pack.mcmeta'
}

foreach ($entryPath in $entries.Keys | Where-Object { $_ -eq 'pack.mcmeta' -or $_.EndsWith('.json') }) {
    try {
        $text = [System.Text.Encoding]::UTF8.GetString($entries[$entryPath])
        $null = $text | ConvertFrom-Json
    }
    catch {
        throw "Invalid JSON in merged entry $entryPath`: $($_.Exception.Message)"
    }
}

if ([System.IO.File]::Exists($temporaryPath)) {
    Remove-Item -LiteralPath $temporaryPath -Force
}

$outputDirectory = [System.IO.Path]::GetDirectoryName($outputPath)
if (-not [System.IO.Directory]::Exists($outputDirectory)) {
    [System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
}

$fileStream = [System.IO.File]::Open(
    $temporaryPath,
    [System.IO.FileMode]::CreateNew,
    [System.IO.FileAccess]::ReadWrite,
    [System.IO.FileShare]::None
)
try {
    $archive = [System.IO.Compression.ZipArchive]::new(
        $fileStream,
        [System.IO.Compression.ZipArchiveMode]::Create,
        $true,
        [System.Text.Encoding]::UTF8
    )
    try {
        $fixedTimestamp = [System.DateTimeOffset]::new(1980, 1, 1, 0, 0, 0, [System.TimeSpan]::Zero)
        foreach ($entryPath in $entries.Keys) {
            $entry = $archive.CreateEntry($entryPath, [System.IO.Compression.CompressionLevel]::Optimal)
            $entry.LastWriteTime = $fixedTimestamp
            $entry.ExternalAttributes = 0
            $destination = $entry.Open()
            try {
                $bytes = $entries[$entryPath]
                $destination.Write($bytes, 0, $bytes.Length)
            }
            finally {
                $destination.Dispose()
            }
        }
    }
    finally {
        $archive.Dispose()
    }
}
finally {
    $fileStream.Dispose()
}

if ([System.IO.File]::Exists($outputPath)) {
    Remove-Item -LiteralPath $outputPath -Force
}
Move-Item -LiteralPath $temporaryPath -Destination $outputPath

& (Join-Path $PSScriptRoot 'validate-pack.ps1') -PackPath $outputPath
