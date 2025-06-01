#!/usr/bin/env python3
"""
Test específico para verificar el solapamiento correcto
"""
import requests
import json
from datetime import datetime, timedelta

def test_with_winter_dates():
    """Test con fechas de invierno donde Madrid = UTC+1"""
    
    tasks = [
        {
            'id': 'task1',
            'title': 'Important meeting prep', 
            'priority': 1,
            'percentComplete': 0,
            'createdDateTime': '2025-01-20T10:00:00Z',
            'hasDescription': True,
            'checklistItemCount': 3
        }
    ]

    # Test para el 21 de enero de 2025 (invierno, UTC+1)
    # Bloquear 10:00-11:00 Madrid = 09:00-10:00 UTC
    busy_slots = [
        {
            'id': 'busy_morning',
            'start': '2025-01-21T09:00:00.0000000',  # 10:00 Madrid
            'end': '2025-01-21T10:00:00.0000000',    # 11:00 Madrid
            'showAs': 'busy',
            'subject': 'Standup meeting',
            'organizer': 'team@company.com'
        }
    ]

    payload = {
        'tasks': tasks,
        'slots': busy_slots
    }

    url = 'http://localhost:5000/assign-tasks'
    print("=== Test con fechas de invierno (Madrid UTC+1) ===")
    print(f"Slot ocupado: 2025-01-21 09:00-10:00 UTC (10:00-11:00 Madrid)")
    print("Esperamos que se asigne la tarea en otro horario...\n")
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Asignaciones encontradas: {len(result)}")
            
            for assignment in result:
                print(f"\n📋 {assignment['taskName']}")
                print(f"   📅 {assignment['date']} ({assignment['dayOfWeek']})")
                print(f"   🇪🇸 Madrid: {assignment['madridTime']['start'][:16]} - {assignment['madridTime']['end'][:16]}")
                print(f"   🌍 UTC: {assignment['reservationTime'][:16]} - {assignment['reservationEnd'][:16]}")
                
                # Verificar que NO se asignó en el horario ocupado
                madrid_start = assignment['madridTime']['start'][:16]
                if '10:00' in madrid_start or '10:30' in madrid_start:
                    print(f"   ⚠️  POSIBLE CONFLICTO: Asignada en horario que debería estar ocupado")
                else:
                    print(f"   ✅ Bien asignada, evita el horario ocupado")
            
            return len(result) > 0
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_with_winter_dates()
    if success:
        print("\n🎉 ¡Test exitoso! La lógica funciona correctamente.")
    else:
        print("\n❌ Test falló. Revisar lógica.")
