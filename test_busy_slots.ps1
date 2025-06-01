# test_busy_slots.ps1
# Script para probar que no se asignen tareas a slots ocupados

$uri = "https://web-production-15ac8.up.railway.app/assign-tasks"
$headers = @{
    'Content-Type' = 'application/json'
}

Write-Host "Probando detección de slots ocupados..." -ForegroundColor Green
Write-Host "URL: $uri" -ForegroundColor Cyan

try {
    # Leer datos de prueba con slots ocupados
    $body = Get-Content 'test_busy_slots.json' -Raw
    Write-Host "Datos de prueba cargados (incluyendo slots ocupados)" -ForegroundColor Green
    
    # Hacer la solicitud
    Write-Host "Enviando solicitud..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body
    
    Write-Host "✅ Respuesta exitosa!" -ForegroundColor Green
    Write-Host "Número de asignaciones: $($response.Count)" -ForegroundColor Cyan
    
    # Analizar qué slots fueron usados
    Write-Host ""
    Write-Host "Análisis de slots utilizados:" -ForegroundColor Yellow
    
    if ($response.Count -eq 0) {
        Write-Host "❌ No se asignó ninguna tarea - esto puede indicar que la función es demasiado restrictiva" -ForegroundColor Red
    } else {
        foreach ($i in 0..($response.Count - 1)) {
            $assignment = $response[$i]
            Write-Host ""
            Write-Host "Asignación $($i + 1):" -ForegroundColor Yellow
            Write-Host "  Tarea: $($assignment.taskName)" -ForegroundColor White
            Write-Host "  Slot ID: $($assignment.slotId)" -ForegroundColor White
            Write-Host "  Horario UTC: $($assignment.reservationTime) - $($assignment.reservationEnd)" -ForegroundColor White
            
            # Verificar si el slot asignado es correcto
            $slotId = $assignment.slotId
            if ($slotId -eq "slot1_free") {
                Write-Host "  ✅ CORRECTO: Asignado a slot FREE" -ForegroundColor Green
            } elseif ($slotId -eq "slot4_tentative") {
                Write-Host "  ✅ ACEPTABLE: Asignado a slot TENTATIVE" -ForegroundColor Yellow
            } elseif ($slotId -eq "slot2_busy_real_meeting") {
                Write-Host "  ❌ ERROR: Asignado a slot BUSY con reunión real" -ForegroundColor Red
            } elseif ($slotId -eq "slot3_busy_no_details") {
                Write-Host "  ⚠️ CUESTIONABLE: Asignado a slot BUSY sin detalles" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ""
    Write-Host "Esperado: Solo debería asignarse a slot1_free y posiblemente slot4_tentative" -ForegroundColor Cyan
    Write-Host "NO debería asignarse a slot2_busy_real_meeting ni slot3_busy_no_details" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error en la solicitud:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
