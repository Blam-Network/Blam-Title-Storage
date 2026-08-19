#Requires -Version 5.1
# Non-interactive upgrade runner based on tools/upgrade.ps1.
# Continues on per-variant failures and writes a report.

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$oldBlfCli = Join-Path $root 'tools\blf_cli_old.exe'
$newBlfCli = Join-Path $root 'tools\blf_cli_new.exe'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$reportDir = Join-Path $PSScriptRoot "upgrade-$stamp"
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
$summaryPath = Join-Path $reportDir 'summary.json'
$failuresPath = Join-Path $reportDir 'failures.jsonl'
$logPath = Join-Path $reportDir 'run.log'

function Write-Log {
    param([string]$Message, [string]$Level = 'INFO')
    $line = '{0} [{1}] {2}' -f (Get-Date -Format 'HH:mm:ss'), $Level, $Message
    Write-Host $line
    Add-Content -LiteralPath $logPath -Value $line
}

function Invoke-Cli {
    param(
        [string]$Exe,
        [string[]]$Arguments,
        [string]$OutPath = $null,
        [string]$ErrPath = $null
    )

    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = & $Exe @Arguments 2>&1
        $exit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prevEap
    }
    if ($null -eq $exit) { $exit = 0 }
    $combined = ($output | ForEach-Object { $_.ToString() }) -join "`n"
    if ($OutPath) { Set-Content -LiteralPath $OutPath -Value $combined -Encoding UTF8 }
    return [pscustomobject]@{
        ExitCode = $exit
        Combined = $combined
    }
}

function Output-LooksFailed {
    param([string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return $false }
    $patterns = @(
        'failed',
        'Failed to',
        'Unrecognized variant',
        'Unable to parse variant',
        'panic',
        'thread ''main'' panicked',
        'No title converter'
    )
    foreach ($p in $patterns) {
        if ($Text -match [regex]::Escape($p) -or $Text -imatch $p) { return $true }
    }
    return $false
}

function Output-IsUnsupported {
    param([string]$Text)
    return $Text -match 'Unsupported title or version'
}

function Record-Failure {
    param($Record)
    $json = $Record | ConvertTo-Json -Compress
    Add-Content -LiteralPath $failuresPath -Value $json
    Write-Log ("FAILURE {0} {1} {2}: {3}" -f $Record.Title, $Record.Version, $Record.Step, $Record.File) 'ERROR'
}

$jobs = @(
    @{ Config = 'Halo 3 ODST\Release'; Title = 'Halo 3: ODST'; Version = '13895.09.04.27.2201.atlas_release' }
    @{ Config = 'Halo 3\Epsilon'; Title = 'Halo 3'; Version = '11856.07.08.20.2332.release' }
    @{ Config = 'Halo 3\11729.07.08.10.0021.main'; Title = 'Halo 3'; Version = '11729.07.08.10.0021.main' }
    @{ Config = 'Halo 3\Delta'; Title = 'Halo 3'; Version = '10015.07.05.14.2217.delta' }
    @{ Config = 'Halo 3\08172.07.03.08.2240.delta'; Title = 'Halo 3'; Version = '08172.07.03.08.2240.delta' }
    @{ Config = 'Halo 3\08117.07.03.07.1702.delta'; Title = 'Halo 3'; Version = '08117.07.03.07.1702.delta' }
    @{ Config = 'Halo 3\06481.06.11.17.1330.alpha_release'; Title = 'Halo 3'; Version = '06481.06.11.17.1330.alpha_release' }
    @{ Config = 'Halo Reach\Alpha'; Title = 'Halo: Reach'; Version = '08516.10.02.19.1607.omaha_alpha' }
    @{ Config = 'Halo Reach\Beta'; Title = 'Halo: Reach'; Version = '09449.10.03.25.1545.omaha_beta' }
    @{ Config = 'Halo Reach\Delta'; Title = 'Halo: Reach'; Version = '09730.10.04.09.1309.omaha_delta' }
    @{ Config = 'Halo 3\Release'; Title = 'Halo 3'; Version = '12070.08.09.05.2031.halo3_ship' }
    @{ Config = 'Halo Reach\Release'; Title = 'Halo: Reach'; Version = '12065.11.08.24.1738.tu1actual' }
    @{ Config = 'Halo Online'; Title = 'Halo: Online'; Version = '1.106708_cert_ms23___release' }
    @{ Config = 'Ares\Untracked'; Title = 'Ares'; Version = 'untracked' }
)

$summaries = @()
Write-Log "Report directory: $reportDir"
Write-Log "Old CLI: $oldBlfCli"
Write-Log "New CLI: $newBlfCli"

foreach ($job in $jobs) {
    $configDir = Join-Path $root $job.Config
    $title = $job.Title
    $version = $job.Version
    $safeName = ($job.Config -replace '[\\/:*?<>| ]', '_')
    $versionLogDir = Join-Path $reportDir $safeName
    New-Item -ItemType Directory -Path $versionLogDir -Force | Out-Null

    $summary = [ordered]@{
        Config          = $job.Config
        Title           = $title
        Version         = $version
        BuildOk         = $false
        BuildConfigOk   = $false
        ExportAttempted = 0
        ExportOk        = 0
        ExportFailed    = 0
        ExportSkipped   = 0
        ImportAttempted = 0
        ImportOk        = 0
        ImportFailed    = 0
        ImportSkipped   = 0
        VariantExportUnsupported = $false
        Notes           = @()
    }

    Write-Log "======== $($job.Config) / $title / $version ========"

    if (-not (Test-Path -LiteralPath $configDir)) {
        $summary.Notes += "Config directory missing: $configDir"
        Write-Log "SKIP missing config dir $configDir" 'WARN'
        $summaries += $summary
        continue
    }

    $buildDir = Join-Path $env:TEMP ("blf-upgrade-" + [guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $buildDir | Out-Null
    Write-Log "Temp build dir: $buildDir"

    try {
        Write-Log 'Step 1: build binaries from configuration'
        $build = Invoke-Cli -Exe $oldBlfCli -Arguments @('title-storage','build',$configDir,$buildDir,$title,$version) -OutPath (Join-Path $versionLogDir 'step1-build.txt')
        $summary.BuildOk = ($build.ExitCode -eq 0 -and -not (Output-LooksFailed $build.Combined))
        if ($build.ExitCode -ne 0 -or (Output-LooksFailed $build.Combined)) {
            Record-Failure @{
                Title = $title; Version = $version; Config = $job.Config; Step = 'build'
                File = $configDir; ExitCode = $build.ExitCode; Output = $build.Combined.Substring(0, [Math]::Min(4000, $build.Combined.Length))
            }
            $summary.Notes += "Step 1 build failed with exit $($build.ExitCode)"
        }

        Write-Log 'Step 2: export game and map variants'
        $stopExport = $false
        foreach ($variantType in @('map_variants','game_variants')) {
            if ($stopExport) { break }
            $variantDirs = @(Get-ChildItem -LiteralPath $configDir -Recurse -Directory -Filter $variantType -ErrorAction SilentlyContinue)
            foreach ($variantDir in $variantDirs) {
                if ($stopExport) { break }
                $inputDir = $variantDir.FullName
                $hopperFolder = $variantDir.Parent.Name
                $outputDir = Join-Path (Join-Path $buildDir $hopperFolder) $variantType
                New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
                $jsonFiles = @(Get-ChildItem -LiteralPath $inputDir -Filter '*.json')
                foreach ($json in $jsonFiles) {
                    $jsonFile = $json.FullName
                    $filename = $json.BaseName
                    $outputFile = Join-Path $outputDir "$filename.bin"
                    $summary.ExportAttempted++
                    $export = Invoke-Cli -Exe $oldBlfCli -Arguments @('title-storage','export-variant',$jsonFile,$outputFile,$title,$version)
                    if (Output-IsUnsupported $export.Combined) {
                        $summary.ExportSkipped++
                        $summary.VariantExportUnsupported = $true
                        $stopExport = $true
                        Write-Log "export-variant unsupported after $($summary.ExportAttempted) attempt(s); skipping remaining exports" 'WARN'
                        break
                    }
                    $wrote = Test-Path -LiteralPath $outputFile
                    $failed = ($export.ExitCode -ne 0) -or (-not $wrote) -or (Output-LooksFailed $export.Combined)
                    if ($failed) {
                        $summary.ExportFailed++
                        $out = if ($export.Combined) { $export.Combined.Substring(0, [Math]::Min(2000, $export.Combined.Length)) } else { '' }
                        Record-Failure @{
                            Title = $title; Version = $version; Config = $job.Config; Step = 'export-variant'
                            VariantType = $variantType; Hopper = $hopperFolder
                            File = $jsonFile; OutputFile = $outputFile
                            ExitCode = $export.ExitCode; WroteFile = $wrote
                            Output = $out
                        }
                    } else {
                        $summary.ExportOk++
                    }
                }
            }
        }

        if ($summary.VariantExportUnsupported) {
            Write-Log 'export-variant is unsupported for this title/version; variants rely on build/build-config' 'WARN'
        }

        Write-Log 'Step 3: build configuration from binaries'
        $buildConfig = Invoke-Cli -Exe $newBlfCli -Arguments @('title-storage','build-config',$buildDir,$configDir,$title,$version) -OutPath (Join-Path $versionLogDir 'step3-build-config.txt')
        $summary.BuildConfigOk = ($buildConfig.ExitCode -eq 0 -and -not (Output-LooksFailed $buildConfig.Combined))
        if ($buildConfig.ExitCode -ne 0 -or (Output-LooksFailed $buildConfig.Combined)) {
            Record-Failure @{
                Title = $title; Version = $version; Config = $job.Config; Step = 'build-config'
                File = $configDir; ExitCode = $buildConfig.ExitCode
                Output = $buildConfig.Combined.Substring(0, [Math]::Min(4000, $buildConfig.Combined.Length))
            }
            $summary.Notes += "Step 3 build-config failed with exit $($buildConfig.ExitCode)"
        }

        Write-Log 'Step 4: import variants into configuration'
        $stopImport = $false
        foreach ($variantType in @('map_variants','game_variants')) {
            if ($stopImport) { break }
            $hopperDirs = @(Get-ChildItem -LiteralPath $buildDir -Directory -ErrorAction SilentlyContinue)
            foreach ($hopperDir in $hopperDirs) {
                if ($stopImport) { break }
                $hopperFolder = $hopperDir.Name
                $variantPath = Join-Path $hopperDir.FullName $variantType
                if (-not (Test-Path -LiteralPath $variantPath -PathType Container)) { continue }
                $binFiles = @(Get-ChildItem -LiteralPath $variantPath -Filter '*.bin' -ErrorAction SilentlyContinue)
                foreach ($bin in $binFiles) {
                    $binFile = $bin.FullName
                    $hopperConfigDir = Join-Path $configDir $hopperFolder
                    $summary.ImportAttempted++
                    $import = Invoke-Cli -Exe $newBlfCli -Arguments @('title-storage','import-variant',$hopperConfigDir,$binFile,$title,$version)
                    if (Output-IsUnsupported $import.Combined) {
                        $summary.ImportSkipped++
                        $stopImport = $true
                        Write-Log "import-variant unsupported; skipping remaining imports" 'WARN'
                        break
                    }
                    $failed = ($import.ExitCode -ne 0) -or (Output-LooksFailed $import.Combined)
                    if ($failed) {
                        $summary.ImportFailed++
                        Record-Failure @{
                            Title = $title; Version = $version; Config = $job.Config; Step = 'import-variant'
                            VariantType = $variantType; Hopper = $hopperFolder
                            File = $binFile; ExitCode = $import.ExitCode
                            Output = $import.Combined.Substring(0, [Math]::Min(2000, $import.Combined.Length))
                        }
                    } else {
                        $summary.ImportOk++
                    }
                }
            }
        }
    }
    finally {
        if (Test-Path -LiteralPath $buildDir) {
            if ($summary.ExportFailed -gt 0 -or $summary.ImportFailed -gt 0 -or -not $summary.BuildOk -or -not $summary.BuildConfigOk) {
                $keep = Join-Path $versionLogDir 'build_dir'
                Write-Log "Keeping build dir at $keep"
                Move-Item -LiteralPath $buildDir -Destination $keep -Force
            } else {
                Remove-Item -LiteralPath $buildDir -Recurse -Force
            }
        }
    }

    Write-Log ("Done {0}: build={1} build-config={2} export {3}/{4} failed={5} skipped={6} import {7}/{8} failed={9} skipped={10}" -f `
        $job.Config, $summary.BuildOk, $summary.BuildConfigOk, $summary.ExportOk, $summary.ExportAttempted, $summary.ExportFailed, $summary.ExportSkipped, `
        $summary.ImportOk, $summary.ImportAttempted, $summary.ImportFailed, $summary.ImportSkipped)
    $summaries += $summary
    $summaries | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
}

Write-Log 'All versions processed.'
$summaries | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
Write-Log "Summary: $summaryPath"
Write-Log "Failures: $failuresPath"
