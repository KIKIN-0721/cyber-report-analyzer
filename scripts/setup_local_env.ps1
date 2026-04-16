[CmdletBinding()]
param(
    [string]$VenvPath = ".venv",
    [switch]$RunChecks
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Get-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Resolve-Python {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw "python was not found. Please install Python 3.11+ and add it to PATH."
    }
    return $python.Source
}

function Get-VenvPython {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,
        [Parameter(Mandatory = $true)]
        [string]$RawVenvPath
    )

    $venvRoot = if ([System.IO.Path]::IsPathRooted($RawVenvPath)) {
        [System.IO.Path]::GetFullPath($RawVenvPath)
    }
    else {
        [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $RawVenvPath))
    }

    $venvPython = Join-Path $venvRoot "Scripts\python.exe"
    return @{
        Root = $venvRoot
        Python = $venvPython
    }
}

$repoRoot = Get-RepoRoot
$systemPython = Resolve-Python
$venv = Get-VenvPython -RepoRoot $repoRoot -RawVenvPath $VenvPath
$requirementsPath = Join-Path $repoRoot "requirements.txt"

Write-Step "Using system Python: $systemPython"

if (-not (Test-Path -LiteralPath $venv.Root)) {
    Write-Step "Creating virtual environment: $($venv.Root)"
    & $systemPython -m venv $venv.Root
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create the virtual environment."
    }
}
else {
    Write-Step "Reusing existing virtual environment: $($venv.Root)"
}

if (-not (Test-Path -LiteralPath $venv.Python)) {
    throw "The virtual environment python executable was not found: $($venv.Python)"
}

if (-not (Test-Path -LiteralPath $requirementsPath)) {
    throw "requirements.txt was not found: $requirementsPath"
}

Write-Step "Upgrading pip"
& $venv.Python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip."
}

Write-Step "Installing dependencies from requirements.txt"
& $venv.Python -m pip install -r $requirementsPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install dependencies from requirements.txt."
}

if ($RunChecks) {
    Write-Step "Running syntax checks"
    Push-Location $repoRoot
    try {
        & $venv.Python -m compileall src tests
        if ($LASTEXITCODE -ne 0) {
            throw "compileall check failed."
        }

        Write-Step "Running pytest"
        $previousPythonPath = $env:PYTHONPATH
        try {
            $env:PYTHONPATH = $repoRoot
            & $venv.Python -m pytest -q
            if ($LASTEXITCODE -ne 0) {
                throw "pytest execution failed."
            }
        }
        finally {
            $env:PYTHONPATH = $previousPythonPath
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "Local environment setup completed." -ForegroundColor Green
Write-Host "Activate command: . $($venv.Root)\\Scripts\\Activate.ps1"
Write-Host "Test command: `$env:PYTHONPATH='.'; python -m pytest -q"
