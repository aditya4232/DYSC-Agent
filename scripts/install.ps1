$ErrorActionPreference = "Stop"

function Test-CommandAvailable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandName
    )
    return [bool](Get-Command $CommandName -ErrorAction SilentlyContinue)
}

if (-not (Test-CommandAvailable -CommandName "node")) {
    throw "Node.js is required. Install Node.js 18+ and retry."
}

if (-not (Test-CommandAvailable -CommandName "npm")) {
    throw "npm is required. Install npm and retry."
}

$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    Write-Host "Installing DYSC globally..."
    npm install -g .
    if ($LASTEXITCODE -ne 0) {
        throw "Global install failed."
    }

    Write-Host "Verifying installation..."
    dysc health
    if ($LASTEXITCODE -ne 0) {
        throw "DYSC installed but health check failed."
    }

    Write-Host "DYSC installed successfully. Use: dysc start"
}
finally {
    Pop-Location
}