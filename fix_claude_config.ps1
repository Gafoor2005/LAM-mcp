# Fix Claude Desktop Configuration Script
# This script updates Claude Desktop configuration with the correct Python path

$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
$projectPath = "C:/Users/Gafoor/Desktop/LAM-mcp"
$pythonPath = "$projectPath/.venv/Scripts/python.exe"

Write-Host "🔧 Fixing Claude Desktop Configuration..." -ForegroundColor Yellow
Write-Host "Config path: $configPath" -ForegroundColor Gray
Write-Host "Python path: $pythonPath" -ForegroundColor Gray

# Check if Python path exists
if (-not (Test-Path $pythonPath)) {
    Write-Host "❌ Python virtual environment not found at: $pythonPath" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Create config directory if it doesn't exist
$configDir = Split-Path $configPath -Parent
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    Write-Host "📁 Created config directory: $configDir" -ForegroundColor Green
}

# Create the configuration
$config = @{
    mcpServers = @{
        'browser-automation' = @{
            command = $pythonPath
            args = @('-m', 'browser_mcp_server.server')
            cwd = $projectPath
            env = @{
                BROWSER_HEADLESS = 'true'
                BROWSER_TYPE = 'chrome'
                BROWSER_TIMEOUT = '30'
            }
        }
    }
}

# Convert to JSON and save
try {
    $jsonConfig = $config | ConvertTo-Json -Depth 10
    Set-Content -Path $configPath -Value $jsonConfig -Encoding UTF8
    Write-Host "✅ Claude Desktop configuration updated successfully!" -ForegroundColor Green
    Write-Host "📍 Configuration saved to: $configPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to update configuration: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔄 Next steps:" -ForegroundColor Cyan
Write-Host "1. Close Claude Desktop completely" -ForegroundColor White
Write-Host "2. Restart Claude Desktop" -ForegroundColor White
Write-Host "3. The 'browser-automation' server should now connect properly" -ForegroundColor White
Write-Host ""
Write-Host "🧪 To test the server manually:" -ForegroundColor Cyan
Write-Host "   $pythonPath -m browser_mcp_server.server" -ForegroundColor Gray