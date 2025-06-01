# API de Asignación de Tareas de Planner a Agenda de Outlook

Esta API recibe tareas de Microsoft Planner y slots disponibles en Agenda de Outlook, y devuelve una lista de asignaciones óptimas teniendo en cuenta prioridades y fechas de vencimiento.

## Funcionalidades

- Recibe tareas de Planner y slots disponibles de Outlook
- Asigna tareas a slots según prioridad y fecha de creación
- Respeta restricciones:
  - Solo programa de lunes a viernes
  - Solo programa entre 9:00 y 17:00
  - No programa dos tareas seguidas
  - No programa más de 2 tareas por día

## Endpoints

- **GET /** - Verificar que la API está funcionando
- **POST /assign-tasks** - Recibir tareas y slots, y devolver asignaciones

## Uso con Power Automate

1. Recuperar tareas de Planner con Power Automate
2. Obtener slots disponibles en Outlook con Power Automate
3. Enviar ambas listas a esta API
4. Recibir las asignaciones y crear eventos en Outlook

## Pruebas Locales

1. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

2. Ejecutar la API localmente:
   ```
   python app.py
   ```

3. Probar con los datos de ejemplo:
   ```
   python test_api.py
   ```

## Formato de Datos

### Entrada - Tareas de Planner
```json
{
  "tasks": [
    {
      "title": "TASK1",
      "priority": 3,
      "createdDateTime": "2025-06-01T13:02:14.5489132Z",
      "dueDateTime": "2025-06-05T10:00:00Z",
      "id": "3gU3WcXciE-AvwOaAtQx2pgAKI9i",
      "percentComplete": 0
    }
  ]
}
```

### Entrada - Slots de Outlook
```json
{
  "slots": [
    {
      "subject": "xxzcxzcxzcxzc",
      "start": "2025-06-02T10:30:00.0000000",
      "end": "2025-06-02T11:00:00.0000000",
      "id": "AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi-XzhbJBwB3-TbRDAeLQLdR49f04FklAAAAAAENAAB3-TbRDAeLQLdR49f04FklAABxalCKAAA="
    }
  ]
}
```

### Salida - Asignaciones
```json
[
  {
    "taskName": "TASK2",
    "taskId": "ml5lwAXzwkKez0ozrJg8JJgACZK9",
    "reservationTime": "2025-06-02T10:30:00.0000000",
    "reservationEnd": "2025-06-02T11:00:00.0000000",
    "dayOfWeek": "Monday",
    "date": "2025-06-02"
  }
]
```
