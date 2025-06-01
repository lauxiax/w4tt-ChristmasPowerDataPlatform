#!/usr/bin/env python3
"""
Test final con escenario realista actual
"""
import requests
import json
from datetime import datetime, timedelta

def test_realistic_scenario():
    """Test con un escenario realista actual"""
    
    # Crear 3 tareas con diferentes prioridades
    tasks = [
        {
            'id': 'urgent_task',
            'title': 'Urgent: Review security incident', 
            'priority': 1,  # Alta prioridad
            'percentComplete': 0,
            'createdDateTime': '2025-06-01T08:00:00Z',
            'hasDescription': True,
            'checklistItemCount': 5
        },
        {
            'id': 'normal_task',
            'title': 'Team 1:1 preparation',
            'priority': 2,  # Prioridad media
            'percentComplete': 20,
            'createdDateTime': '2025-06-01T09:00:00Z',
            'hasDescription': True,
            'checklistItemCount': 2
        },
        {
            'id': 'low_task',
            'title': 'Update documentation',
            'priority': 4,  # Baja prioridad
            'percentComplete': 0,
            'createdDateTime': '2025-06-01T10:00:00Z',
            'hasDescription': False,
            'checklistItemCount': 1
        }
    ]

    # Definir algunas reuniones existentes (en UTC para que el API las evite)
    # Nota: Estamos en junio (verano), así que Madrid = UTC+2
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)
    
    busy_slots = [
        # Mañana: 10:00-11:00 Madrid = 08:00-09:00 UTC
        {
            'id': 'morning_standup',
            'start': f'{tomorrow}T08:00:00.0000000',
            'end': f'{tomorrow}T09:00:00.0000000',
            'showAs': 'busy',
            'subject': 'Daily Standup',
            'organizer': 'scrum.master@company.com',
            'requiredAttendees': 'team@company.com'
        },
        # Mañana: 15:00-16:30 Madrid = 13:00-14:30 UTC  
        {
            'id': 'client_meeting',
            'start': f'{tomorrow}T13:00:00.0000000',
            'end': f'{tomorrow}T14:30:00.0000000',
            'showAs': 'busy',
            'subject': 'Client presentation',
            'organizer': 'sales@company.com',
            'location': 'Conference Room A',
            'requiredAttendees': 'user@company.com'
        },
        # Pasado mañana: 11:00-12:00 Madrid = 09:00-10:00 UTC
        {
            'id': 'team_retrospective',
            'start': f'{day_after}T09:00:00.0000000',
            'end': f'{day_after}T10:00:00.0000000',
            'showAs': 'busy',
            'subject': 'Sprint Retrospective',
            'organizer': 'agile.coach@company.com',
            'requiredAttendees': 'dev.team@company.com'
        }
    ]

    payload = {
        'tasks': tasks,
        'slots': busy_slots
    }

    url = 'http://localhost:5000/assign-tasks'
    print("=== Test Escenario Realista ===")
    print(f"📅 Hoy: {today}")
    print(f"🏢 Enviando {len(tasks)} tareas y {len(busy_slots)} reuniones a evitar")
    print("\n📋 Tareas:")
    for task in tasks:
        print(f"   {task['priority']} - {task['title']}")
    
    print("\n🚫 Horarios ocupados a evitar (hora Madrid):")
    for slot in busy_slots:
        # Convertir UTC a Madrid para mostrar
        utc_time = datetime.fromisoformat(slot['start'].split('.')[0])
        madrid_time = utc_time.replace(tzinfo=None) + timedelta(hours=2)  # Verano UTC+2
        print(f"   {madrid_time.strftime('%m-%d %H:%M')} - {slot['subject']}")
    
    print("\n🔄 Consultando API...")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ ¡Éxito! {len(result)} tareas asignadas:")
            
            for i, assignment in enumerate(result, 1):
                madrid_time = assignment['madridTime']['start'][:16].replace('T', ' ')
                print(f"\n   {i}. 📋 {assignment['taskName']}")
                print(f"      📅 {assignment['date']} ({assignment['dayOfWeek']})")
                print(f"      🕒 {madrid_time} Madrid ({assignment['calculatedDurationMinutes']} min)")
                
                # Verificar que no hay conflictos
                check_conflicts(assignment, busy_slots)
            
            return len(result) > 0
        else:
            print(f"\n❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")
        return False

def check_conflicts(assignment, busy_slots):
    """Verificar que no hay conflictos con slots ocupados"""
    assignment_utc = datetime.fromisoformat(assignment['reservationTime'].split('.')[0])
    
    for busy in busy_slots:
        busy_start = datetime.fromisoformat(busy['start'].split('.')[0])
        busy_end = datetime.fromisoformat(busy['end'].split('.')[0])
        
        if busy_start <= assignment_utc < busy_end:
            print(f"      ⚠️  CONFLICTO detectado con '{busy['subject']}'!")
            return False
    
    print(f"      ✅ Sin conflictos")
    return True

if __name__ == "__main__":
    success = test_realistic_scenario()
    print(f"\n{'🎉 Test exitoso!' if success else '❌ Test falló'}")
