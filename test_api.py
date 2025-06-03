"""
🧪 Tests para la API de Asignación de Tareas
===========================================

Este script permite probar la funcionalidad de la API de asignación de tareas.
Ejecuta pruebas con diferentes escenarios para verificar el comportamiento.
"""

import requests
import json
from datetime import datetime, timedelta

# URL de la API (cambiar a la URL de producción cuando se despliegue)
API_URL = "http://localhost:5000"

def test_health_check():
    """Prueba el endpoint de health check."""
    response = requests.get(f"{API_URL}/health-check")
    
    print("\n=== TEST: Health Check ===")
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json().get('status') == "OK"
    
    print("✅ Health check test passed!")

def test_assign_tasks_basic():
    """Prueba básica del endpoint de asignación de tareas."""
    # Crear una fecha base (mañana a las 9 AM)
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    # Datos de prueba
    payload = {
        "tasks": [
            {
                "id": "task001",
                "title": "Planificación del sprint",
                "priority": 1,
                "percentComplete": 10,
                "checklistItemCount": 3,
                "hasDescription": True,
                "dueDateTime": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "createdDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            },
            {
                "id": "task002",
                "title": "Revisión de requisitos",
                "priority": 0,
                "percentComplete": 30,
                "checklistItemCount": 5,
                "hasDescription": True,
                "dueDateTime": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "createdDateTime": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
            }
        ],
        "slots": [
            {
                "start": f"{tomorrow_str}T08:00:00Z",
                "end": f"{tomorrow_str}T09:30:00Z"
            }
        ]
    }
    
    # Realizar solicitud
    response = requests.post(f"{API_URL}/assign-tasks", json=payload)
    
    print("\n=== TEST: Assign Tasks Basic ===")
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    print("✅ Assign tasks basic test passed!")

def test_assign_tasks_with_constraints():
    """Prueba con restricciones de slots ocupados y múltiples tareas."""
    # Crear fecha base (mañana)
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    day_after = datetime.now() + timedelta(days=2)
    day_after_str = day_after.strftime("%Y-%m-%d")
    
    # Datos de prueba
    payload = {
        "tasks": [
            # 5 tareas con diferentes prioridades
            {
                "id": "task001",
                "title": "Reunión urgente",
                "priority": 0,  # Máxima prioridad
                "percentComplete": 0,
                "hasDescription": True,
                "dueDateTime": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            {
                "id": "task002",
                "title": "Planificación importante",
                "priority": 1,
                "percentComplete": 10,
                "checklistItemCount": 8,
                "dueDateTime": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            {
                "id": "task003",
                "title": "Tarea media prioridad",
                "priority": 2,
                "percentComplete": 25,
                "checklistItemCount": 3,
                "dueDateTime": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            {
                "id": "task004",
                "title": "Tarea baja prioridad",
                "priority": 3,
                "percentComplete": 50,
                "dueDateTime": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            {
                "id": "task005",
                "title": "Tarea mínima prioridad",
                "priority": 4,
                "percentComplete": 75,
                "dueDateTime": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        ],
        "slots": [
            # Ocupar toda la mañana del primer día
            {
                "start": f"{tomorrow_str}T07:00:00Z",
                "end": f"{tomorrow_str}T12:00:00Z"
            },
            # Ocupar parte de la tarde del primer día
            {
                "start": f"{tomorrow_str}T14:00:00Z",
                "end": f"{tomorrow_str}T15:30:00Z"
            },
            # Ocupar parte de la mañana del segundo día
            {
                "start": f"{day_after_str}T08:00:00Z",
                "end": f"{day_after_str}T10:30:00Z"
            }
        ]
    }
    
    # Realizar solicitud
    response = requests.post(f"{API_URL}/assign-tasks", json=payload)
    
    print("\n=== TEST: Assign Tasks With Constraints ===")
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    
    # Verificar que las tareas se asignaron correctamente
    assignments = response.json()
    assert isinstance(assignments, list)
    
    # Verificar que al menos se asignaron algunas tareas
    assert len(assignments) > 0
    
    # Verificar que las primeras tareas asignadas son las de mayor prioridad
    if len(assignments) >= 2:
        first_task_id = assignments[0]["taskId"]
        second_task_id = assignments[1]["taskId"]
        
        # Las tareas más prioritarias deberían asignarse primero
        assert first_task_id in ["task001", "task002"]
    
    print("✅ Assign tasks with constraints test passed!")

def test_invalid_input():
    """Prueba con datos de entrada inválidos."""
    # Datos inválidos (sin campo 'tasks')
    invalid_payload = {
        "slots": []
    }
    
    # Realizar solicitud
    response = requests.post(f"{API_URL}/assign-tasks", json=invalid_payload)
    
    print("\n=== TEST: Invalid Input ===")
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 400
    assert "error" in response.json()
    
    print("✅ Invalid input test passed!")

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de la API de Asignación de Tareas")
    
    try:
        test_health_check()
        test_assign_tasks_basic()
        test_assign_tasks_with_constraints()
        test_invalid_input()
        
        print("\n✅ ¡Todas las pruebas han pasado exitosamente! ✅")
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {str(e)}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar a la API. Asegúrate de que esté en ejecución.")
