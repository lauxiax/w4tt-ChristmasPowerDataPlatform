#!/usr/bin/env python3
import requests
import json
from test_data import TASKS_SAMPLE, SLOTS_SAMPLE

def test_real_data():
    payload = {
        'tasks': TASKS_SAMPLE,
        'slots': SLOTS_SAMPLE  # Todos son eventos ocupados reales
    }

    url = 'http://localhost:5000/assign-tasks'
    print(f"📊 Datos reales: {len(TASKS_SAMPLE)} tareas, {len(SLOTS_SAMPLE)} eventos ocupados")
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Asignadas {len(result)} tareas")
        
        for i, assignment in enumerate(result, 1):
            print(f"\n{i}. {assignment['taskName']}")
            print(f"   📅 {assignment['date']} ({assignment['dayOfWeek']})")
            print(f"   🕒 {assignment['madridTime']['start'][:16]} Madrid")
            print(f"   ⏱️  {assignment['calculatedDurationMinutes']} minutos")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_real_data()
