# test_production_api.ps1
# Script para probar la API de producción

$uri = "https://web-production-15ac8.up.railway.app/assign-tasks"
$headers = @{
    'Content-Type' = 'application/json'
}

Write-Host "Probando la API de producción en Railway..." -ForegroundColor Green
Write-Host "URL: $uri" -ForegroundColor Cyan

try {
    # Leer datos de prueba
    $body = Get-Content 'test_simple.json' -Raw
    Write-Host "Datos de prueba cargados exitosamente" -ForegroundColor Green
    
    # Hacer la solicitud
    Write-Host "Enviando solicitud..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body
    
    Write-Host "✅ Respuesta exitosa!" -ForegroundColor Green
    Write-Host "Número de asignaciones: $($response.Count)" -ForegroundColor Cyan
    
    foreach ($i in 0..($response.Count - 1)) {
        $assignment = $response[$i]
        Write-Host ""
        Write-Host "Asignación $($i + 1):" -ForegroundColor Yellow
        Write-Host "  Tarea: $($assignment.taskName)" -ForegroundColor White
        Write-Host "  Fecha: $($assignment.date) ($($assignment.dayOfWeek))" -ForegroundColor White
        Write-Host "  Horario UTC: $($assignment.reservationTime) - $($assignment.reservationEnd)" -ForegroundColor White
        
        if ($assignment.madridTime) {
            Write-Host "  Horario Madrid: $($assignment.madridTime.start) - $($assignment.madridTime.end)" -ForegroundColor Cyan
        }
        
        Write-Host "  Duración: $($assignment.calculatedDurationMinutes) minutos" -ForegroundColor White
        
        if ($assignment.adjustedDuration) {
            Write-Host "  ⚠️ Duración ajustada" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "🎉 Prueba completada exitosamente!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error en la solicitud:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Código de estado: $statusCode" -ForegroundColor Red
    }
}
