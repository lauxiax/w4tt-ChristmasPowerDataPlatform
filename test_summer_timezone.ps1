# test_summer_timezone.ps1
# Script para probar la conversión de zona horaria en verano (UTC+2)

$uri = "https://web-production-15ac8.up.railway.app/assign-tasks"
$headers = @{
    'Content-Type' = 'application/json'
}

Write-Host "Probando conversión de zona horaria en VERANO (UTC+2)..." -ForegroundColor Green

try {
    $body = Get-Content 'test_summer.json' -Raw
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body
    
    $assignment = $response[0]
    Write-Host ""
    Write-Host "Resultado para fecha de verano (Julio 2024):" -ForegroundColor Yellow
    Write-Host "  Horario UTC: $($assignment.reservationTime) - $($assignment.reservationEnd)" -ForegroundColor White
    Write-Host "  Horario Madrid: $($assignment.madridTime.start) - $($assignment.madridTime.end)" -ForegroundColor Cyan
    
    # Verificar que la diferencia sea +2 horas en verano
    $utcTime = [DateTime]::Parse($assignment.reservationTime.Substring(0,19))
    $madridTimeStr = $assignment.madridTime.start
    
    if ($madridTimeStr -match "(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})") {
        $madridHour = [DateTime]::Parse($matches[1]).Hour
        $expectedHour = ($utcTime.Hour + 2) % 24
        
        if ($madridHour -eq $expectedHour) {
            Write-Host "✅ Conversión correcta: UTC+2 en verano" -ForegroundColor Green
        } else {
            Write-Host "❌ Error en conversión de zona horaria" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
