#!/usr/bin/env python3
"""
Test script para probar la nueva lógica que solo recibe slots ocupados
"""
import requests
import json
from datetime import datetime, timedelta

def test_new_logic():
    # Crear tareas de prueba
    tasks = [
        {
            'id': 'task1',
            'title': 'Review project requirements', 
            'priority': 1,
            'percentComplete': 0,
            'createdDateTime': '2025-01-16T10:00:00Z',
            'hasDescription': True,
            'checklistItemCount': 3
        },
        {
            'id': 'task2',
            'title': 'Prepare presentation',
            'priority': 2, 
            'percentComplete': 25,
            'createdDateTime': '2025-01-16T11:00:00Z',
            'hasDescription': False,
            'checklistItemCount': 1
        },
        {
            'id': 'task3',
            'title': 'Update documentation',
            'priority': 3, 
            'percentComplete': 0,
            'createdDateTime': '2025-01-16T12:00:00Z',
            'hasDescription': True,
            'checklistItemCount': 5
        }
    ]    # Crear algunos slots ocupados que debo evitar (simulando reuniones existentes)
    # Usando fechas actuales y horarios realistas
    tomorrow = datetime.now().date() + timedelta(days=1)
    day_after = datetime.now().date() + timedelta(days=2)
    
    # En enero (invierno), Madrid = UTC+1
    # Si quiero bloquear 14:00-15:00 Madrid, necesito 13:00-14:00 UTC
    busy_slots = [
        {
            'id': 'busy1',
            'start': f'{tomorrow}T13:00:00.0000000',  # 14:00 Madrid = 13:00 UTC en invierno
            'end': f'{tomorrow}T14:00:00.0000000',    # 15:00 Madrid = 14:00 UTC en invierno
            'showAs': 'busy',
            'subject': 'Team meeting',
            'organizer': 'boss@company.com',
            'location': 'Conference room',
            'requiredAttendees': 'user@company.com',
            'optionalAttendees': ''
        },
        {
            'id': 'busy2',
            'start': f'{day_after}T09:30:00.0000000',  # 10:30 Madrid = 09:30 UTC en invierno
            'end': f'{day_after}T10:30:00.0000000',    # 11:30 Madrid = 10:30 UTC en invierno
            'showAs': 'busy',
            'subject': 'Client call',
            'organizer': 'client@example.com',
            'location': 'Virtual',
            'requiredAttendees': 'user@company.com',
            'optionalAttendees': ''
        }
    ]

    payload = {
        'tasks': tasks,
        'slots': busy_slots
    }

    # Probar API local
    url = 'http://localhost:5000/assign-tasks'
    print(f"Enviando {len(tasks)} tareas y {len(busy_slots)} slots ocupados a evitar...")
    
    try:
        response = requests.post(url, json=payload)
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'\n✅ API respondió correctamente. Asignaciones encontradas: {len(result)}')
            
            for i, assignment in enumerate(result, 1):
                print(f'\n{i}. {assignment["taskName"]}')
                print(f'   📅 Fecha: {assignment["date"]} ({assignment["dayOfWeek"]})')
                print(f'   🕒 Madrid: {assignment["madridTime"]["start"][:16]} - {assignment["madridTime"]["end"][:16]}')
                print(f'   🌍 UTC: {assignment["reservationTime"][:16]} - {assignment["reservationEnd"][:16]}')
                print(f'   ⏱️  Duración: {assignment["calculatedDurationMinutes"]} minutos')
            
            return result
        else:
            print(f'❌ Error: {response.text}')
            return None
            
    except Exception as e:
        print(f'❌ Error al conectar: {str(e)}')
        return None

if __name__ == "__main__":
    print("=== Test de Nueva Lógica: Solo Slots Ocupados ===")
    print("Solo enviamos los slots BUSY que deben evitarse")
    print("La API debe generar slots disponibles y evitar los ocupados\n")
    
    test_new_logic()
