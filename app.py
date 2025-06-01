from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "API funcionando correctamente", "message": "Usa el endpoint /assign-tasks para asignar tareas"})

@app.route('/assign-tasks', methods=['POST'])
def assign_tasks():
    data = request.get_json()

    # Validar que se reciban las dos listas
    if 'tasks' not in data or 'slots' not in data:
        return jsonify({"error": "Se requieren las listas 'tasks' y 'slots'"}), 400

    tasks = data['tasks']
    slots = data['slots']

    # Procesar las tareas y los slots
    assigned_slots = assign_tasks_to_slots(tasks, slots)

    return jsonify(assigned_slots)

def assign_tasks_to_slots(tasks, slots):
    assigned = []
    used_slots = set()

    for task in sorted(tasks, key=lambda t: (t['priority'], t['createdDate'])):
        for slot in slots:
            slot_start = datetime.fromisoformat(slot['start'])
            slot_end = datetime.fromisoformat(slot['end'])

            # Restricciones: lunes a viernes, 9 a 5, no más de 2 tareas por día
            if slot_start.weekday() >= 5 or slot_start.hour < 9 or slot_end.hour > 17:
                continue

            day_key = slot_start.date()
            if len([a for a in assigned if a['date'] == str(day_key)]) >= 2:
                continue

            if slot_start in used_slots:
                continue

            # Asignar tarea al slot
            assigned.append({
                'taskName': task['name'],
                'reservationTime': slot['start'],
                'dayOfWeek': slot_start.strftime('%A'),
                'date': str(slot_start.date())
            })
            used_slots.add(slot_start)
            break

    return assigned

if __name__ == '__main__':
    # Obtener el puerto desde la variable de entorno (para Railway) o usar 5000 por defecto
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
