# dev.ps1 — Start both frontend and backend dev servers.
# Press Ctrl+C to stop both.

$backend = Start-Process -NoNewWindow -PassThru -FilePath "uv" `
    -ArgumentList "run", "-m", "uvicorn", "evinha.main:app", "--port", "8080", "--reload" `
    -WorkingDirectory "$PSScriptRoot\backend"

$frontend = Start-Process -NoNewWindow -PassThru -FilePath "cmd.exe" `
    -ArgumentList "/c", "npm run dev" `
    -WorkingDirectory "$PSScriptRoot\frontend"

try {
    Write-Host "Backend (PID $($backend.Id)) on :8080, Frontend (PID $($frontend.Id)) on :5173"
    Write-Host "Press Ctrl+C to stop both..."
    Wait-Process -Id $backend.Id, $frontend.Id
} finally {
    foreach ($proc in @($backend, $frontend)) {
        if (!$proc.HasExited) {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            # Also kill child processes (node, python, etc.)
            Get-CimInstance Win32_Process |
                Where-Object { $_.ParentProcessId -eq $proc.Id } |
                ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
        }
    }
    Write-Host "Both servers stopped."
}
