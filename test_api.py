# test_api.py
# Este script te permite probar la API de asignación de tareas

import requests
import json
from test_data import TASKS_SAMPLE, SLOTS_SAMPLE

def test_api(tasks=None, slots=None, url="https://web-production-15ac8.up.railway.app/assign-tasks"):
    """
    Prueba la API con los datos proporcionados
    
    Args:
        tasks: Lista de tareas (opcional, por defecto usa TASKS_SAMPLE)
        slots: Lista de slots (opcional, por defecto usa SLOTS_SAMPLE)
        url: URL de la API (opcional)
        
    Returns:
        La respuesta de la API
    """
    if tasks is None:
        tasks = TASKS_SAMPLE
    
    if slots is None:
        slots = SLOTS_SAMPLE
    
    payload = {
        "tasks": tasks,
        "slots": slots
    }
    
    try:
        print(f"Enviando solicitud a {url}...")
        response = requests.post(url, json=payload)
        print(f"Estado: {response.status_code}")
          if response.status_code == 200:
            result = response.json()
            
            if 'assignments' in result:
                # Nuevo formato
                assignments = result['assignments']
                unassigned = result.get('unassignedTasks', [])
                
                print("Asignaciones realizadas:")
                for i, assignment in enumerate(assignments, 1):
                    print(f"\n{i}. Tarea: {assignment['taskName']}")
                    print(f"   ID: {assignment['taskId']}")
                    print(f"   Fecha: {assignment['date']} ({assignment['dayOfWeek']})")
                    print(f"   Horario: {assignment['reservationTime']} - {assignment['reservationEnd']}")
                    print(f"   Duración: {assignment.get('calculatedDurationMinutes', 'N/A')} minutos")
                    if assignment.get('adjustedDuration'):
                        print(f"   ⚠️ Duración ajustada debido a restricciones de tiempo")
                
                if unassigned:
                    print("\nTareas no asignadas:")
                    for i, task in enumerate(unassigned, 1):
                        print(f"{i}. {task['taskName']} (ID: {task['taskId']})")
            else:
                # Formato antiguo
                print("Asignaciones realizadas:")
                for i, assignment in enumerate(result, 1):
                    print(f"\n{i}. Tarea: {assignment['taskName']}")
                    print(f"   ID: {assignment['taskId']}")
                    print(f"   Fecha: {assignment['date']} ({assignment['dayOfWeek']})")
                    print(f"   Horario: {assignment['reservationTime']} - {assignment['reservationEnd']}")
            
            return result
        else:
            print(f"Error: {response.text}")
            return None
    
    except Exception as e:
        print(f"Error al conectar con la API: {str(e)}")
        return None

def test_local_api():
    """Prueba la API en desarrollo local (puerto 5000)"""
    return test_api(url="http://localhost:5000/assign-tasks")

def test_production_api():
    """Prueba la API en Railway"""
    return test_api(url="https://web-production-15ac8.up.railway.app/assign-tasks")

def filter_tasks_by_priority(priority_value):
    """Filtra las tareas por prioridad"""
    return [task for task in TASKS_SAMPLE if task.get("priority") == priority_value]

def filter_slots_by_day(day):
    """Filtra los slots por día de la semana (0=lunes, 1=martes, etc.)"""
    from datetime import datetime
    
    return [
        slot for slot in SLOTS_SAMPLE 
        if datetime.fromisoformat(slot["start"].split(".")[0]).weekday() == day
    ]

if __name__ == "__main__":
    print("=== Probador de API para Asignación de Tareas ===")
    print("1. Probar con todos los datos")
    print("2. Probar solo con tareas de alta prioridad (1)")
    print("3. Probar solo con slots de lunes")
    print("4. Probar en entorno local")
    print("5. Salir")
    
    option = input("\nSelecciona una opción: ")
    
    if option == "1":
        test_production_api()
    elif option == "2":
        high_priority_tasks = filter_tasks_by_priority(1)
        test_api(tasks=high_priority_tasks)
    elif option == "3":
        monday_slots = filter_slots_by_day(0)  # 0 = lunes
        test_api(slots=monday_slots)
    elif option == "4":
        test_local_api()
    else:
        print("Saliendo...")
