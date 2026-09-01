[CmdletBinding()]
param(
    [string] $PackPath
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($PackPath)) {
    $PackPath = Join-Path (Split-Path -Parent $PSScriptRoot) 'ViksStuff-Pack.zip'
}

$resolvedPack = [System.IO.Path]::GetFullPath($PackPath)
if (-not [System.IO.File]::Exists($resolvedPack)) {
    throw "Pack does not exist: $resolvedPack"
}

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Drawing

$requiredIcons = @(
    'assets/viksstuff/textures/item/rps_rock.png',
    'assets/viksstuff/textures/item/rps_paper.png',
    'assets/viksstuff/textures/item/rps_scissors.png'
)
$requiredIcons += 1..25 | ForEach-Object { "assets/viksstuff/textures/item/round_$_.png" }

$archive = [System.IO.Compression.ZipFile]::OpenRead($resolvedPack)
try {
    $fileEntries = @($archive.Entries | Where-Object { -not $_.FullName.EndsWith('/') })
    $exactDuplicates = @($fileEntries | Group-Object FullName | Where-Object Count -gt 1)
    if ($exactDuplicates.Count -gt 0) {
        throw "Duplicate ZIP entries: $($exactDuplicates.Name -join ', ')"
    }

    $caseDuplicates = @(
        $fileEntries |
            Group-Object { $_.FullName.ToLowerInvariant() } |
            Where-Object Count -gt 1
    )
    if ($caseDuplicates.Count -gt 0) {
        throw "Case-insensitive ZIP entry collisions: $($caseDuplicates.Name -join ', ')"
    }

    $fixedTimestamp = [System.DateTimeOffset]::new(1980, 1, 1, 0, 0, 0, [System.TimeSpan]::Zero)
    $floatingTimestamps = @(
        $fileEntries | Where-Object { $_.LastWriteTime -ne $fixedTimestamp }
    )
    if ($floatingTimestamps.Count -gt 0) {
        throw "ZIP entries must use the fixed timestamp: $($floatingTimestamps.FullName -join ', ')"
    }

    $packEntry = $archive.GetEntry('pack.mcmeta')
    if ($null -eq $packEntry) {
        throw 'pack.mcmeta is missing'
    }

    $reader = [System.IO.StreamReader]::new($packEntry.Open(), [System.Text.Encoding]::UTF8)
    try {
        $metadata = $reader.ReadToEnd() | ConvertFrom-Json
    }
    finally {
        $reader.Dispose()
    }

    if ($metadata.pack.pack_format -ne 75) {
        throw "pack_format must be 75, found $($metadata.pack.pack_format)"
    }
    if (
        $metadata.pack.min_format.Count -ne 2 -or
        $metadata.pack.min_format[0] -ne 75 -or
        $metadata.pack.min_format[1] -ne 0 -or
        $metadata.pack.max_format.Count -ne 2 -or
        $metadata.pack.max_format[0] -ne 75 -or
        $metadata.pack.max_format[1] -ne 0
    ) {
        throw 'pack.mcmeta must declare min_format and max_format as [75, 0]'
    }

    foreach ($entry in $fileEntries | Where-Object { $_.FullName.EndsWith('.json') }) {
        $jsonReader = [System.IO.StreamReader]::new($entry.Open(), [System.Text.Encoding]::UTF8)
        try {
            $null = $jsonReader.ReadToEnd() | ConvertFrom-Json
        }
        catch {
            throw "Invalid JSON in $($entry.FullName): $($_.Exception.Message)"
        }
        finally {
            $jsonReader.Dispose()
        }
    }

    foreach ($iconPath in $requiredIcons) {
        $entry = $archive.GetEntry($iconPath)
        if ($null -eq $entry) {
            throw "Required icon is missing: $iconPath"
        }

        $stream = $entry.Open()
        try {
            $bitmap = [System.Drawing.Bitmap]::new($stream)
            try {
                if ($bitmap.Width -ne 64 -or $bitmap.Height -ne 64) {
                    throw "$iconPath must be 64x64, found $($bitmap.Width)x$($bitmap.Height)"
                }

                $transparentPixels = 0
                $visiblePixels = 0
                for ($y = 0; $y -lt $bitmap.Height; $y++) {
                    for ($x = 0; $x -lt $bitmap.Width; $x++) {
                        if ($bitmap.GetPixel($x, $y).A -eq 0) {
                            $transparentPixels++
                        }
                        else {
                            $visiblePixels++
                        }
                    }
                }

                if ($transparentPixels -eq 0 -or $visiblePixels -eq 0) {
                    throw "$iconPath must contain both transparent and visible pixels"
                }
            }
            finally {
                $bitmap.Dispose()
            }
        }
        finally {
            $stream.Dispose()
        }
    }

    [pscustomobject]@{
        Pack = $resolvedPack
        Entries = $fileEntries.Count
        PackFormat = '75.0'
        JsonFiles = @($fileEntries | Where-Object { $_.FullName.EndsWith('.json') }).Count
        ValidatedIcons = $requiredIcons.Count
        DuplicateEntries = 0
        FloatingTimestamps = 0
    }
}
finally {
    $archive.Dispose()
}
