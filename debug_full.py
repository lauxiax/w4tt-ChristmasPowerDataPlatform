#!/usr/bin/env python3
"""
Debug completo del flujo de asignación
"""
import sys
sys.path.append('.')

from app import assign_tasks_to_slots
from datetime import datetime, timedelta
import pytz

def debug_full_assignment():
    print("=== DEBUG: Flujo Completo de Asignación ===\n")
    
    tasks = [
        {
            'id': 'task1',
            'title': 'Test task', 
            'priority': 1,
            'percentComplete': 0,
            'createdDateTime': '2025-01-20T10:00:00Z'
        }
    ]

    # Usar mañana como fecha
    tomorrow = datetime.now().date() + timedelta(days=1)
    print(f"Fecha de mañana: {tomorrow}")
    print(f"Día de la semana: {tomorrow.weekday()} (0=lunes, 6=domingo)")
    
    busy_slots = [
        {
            'id': 'busy1',
            'start': f'{tomorrow}T09:00:00.0000000',
            'end': f'{tomorrow}T10:00:00.0000000',
            'showAs': 'busy',
            'subject': 'Meeting'
        }
    ]
    
    print(f"\nSlot ocupado: {busy_slots[0]['start']} - {busy_slots[0]['end']}")
    
    # Llamar a la función de asignación directamente
    print("\nLlamando a assign_tasks_to_slots...")
    result = assign_tasks_to_slots(tasks, busy_slots)
    
    print(f"Resultado: {len(result)} asignaciones")
    for assignment in result:
        print(f"  - {assignment['taskName']}: {assignment['madridTime']['start']}")

if __name__ == "__main__":
    debug_full_assignment()
