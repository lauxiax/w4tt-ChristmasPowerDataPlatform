from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# Constante para la zona horaria de Madrid
MADRID_TIMEZONE = pytz.timezone('Europe/Madrid')

def is_slot_available(slot):
    """
    Determina si un slot está disponible para programar una reunión.
    
    Utiliza una lógica conservadora: solo considera disponibles los slots
    que están explícitamente marcados como libres o tienen características
    claras de tiempo disponible.
    """
    # El campo 'showAs' es el indicador más confiable
    show_as = slot.get('showAs', '').lower()
    
    # Solo estos estados se consideran definitivamente disponibles
    if show_as in ['free', 'tentative']:
        return True
    
    # Estos estados son definitivamente NO disponibles
    if show_as in ['busy', 'oof', 'workingelsewhere']:
        return False
    
    # Si no hay showAs definido, verificamos otros indicadores
    # pero con lógica más conservadora
    
    # Verificar si hay evidencia de que es un evento real
    subject = slot.get('subject', '').strip()
    organizer = slot.get('organizer', '').strip()
    location = slot.get('location', '').strip()
    required_attendees = slot.get('requiredAttendees', '').strip()
    optional_attendees = slot.get('optionalAttendees', '').strip()
    
    # Si tiene organizador, ubicación o asistentes, probablemente es un evento real
    has_event_details = (
        organizer or 
        location or 
        required_attendees or 
        optional_attendees
    )
    
    if has_event_details:
        return False  # Hay evidencia de que es un evento real
    
    # Si el subject sugiere que es un evento real (no vacío y con contenido)
    if subject and len(subject) > 5:
        # Excluir subjects que claramente indican disponibilidad
        available_indicators = [
            'free', 'available', 'libre', 'disponible', 
            'open', 'abierto', 'slot'
        ]
        
        subject_lower = subject.lower()
        is_availability_indicator = any(indicator in subject_lower for indicator in available_indicators)
        
        if not is_availability_indicator:
            return False  # Subject con contenido real, probablemente ocupado
    
    # Solo si NO hay evidencia de evento real, consideramos disponible
    # Esto es más conservador que la versión anterior
    return True

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

    # Filtrar solo los slots disponibles (distinguiendo entre slots disponibles y eventos existentes)
    available_slots = [s for s in slots if is_slot_available(s)]

    # Procesar las tareas y los slots disponibles
    assigned_slots = assign_tasks_to_slots(tasks, available_slots)

    # Devolver directamente la lista de asignaciones (formato original)
    return jsonify(assigned_slots)

def calculate_meeting_duration(task):
    """
    Calcula la duración óptima de una reunión basada en las características de la tarea.
    
    Parámetros de Planner que podemos usar:
    - priority: (0=urgente, 1=importante, 2=medio, 3=bajo, etc.)
    - percentComplete: Porcentaje de completitud (0-100)
    - checklistItemCount: Número de elementos en la lista de verificación
    - hasDescription: Si tiene descripción detallada
    - appliedCategories: Categorías/etiquetas asignadas
    - dueDateTime: Fecha de vencimiento (cercanía podría indicar urgencia)
    """
    # Duración base en minutos
    base_duration = 30
    
    # Ajuste por prioridad (tareas más prioritarias pueden requerir más tiempo)
    priority = task.get('priority', 5)
    if priority == 0:  # Urgente
        base_duration += 15
    elif priority == 1:  # Importante
        base_duration += 10
    
    # Ajuste por complejidad (basado en porcentaje completado)
    percent_complete = task.get('percentComplete', 0)
    if percent_complete < 20:
        base_duration += 10  # Tareas que apenas han comenzado requieren más planificación
    
    # Ajuste por cantidad de elementos en la lista de verificación
    checklist_count = task.get('checklistItemCount', 0)
    if checklist_count > 5:
        base_duration += 10
    
    # Si tiene descripción detallada, puede requerir más tiempo
    if task.get('hasDescription', False):
        base_duration += 5
    
    # Limitar duración entre 15 y 60 minutos
    return min(max(base_duration, 15), 60)

def assign_tasks_to_slots(tasks, slots):
    assigned = []
    used_slots = set()
    
    # Ordenar slots por fecha y hora
    sorted_slots = sorted(slots, key=lambda s: s.get('start', ''))
    
    # Ordenar tareas por prioridad y fecha de creación (prioridad baja en Planner es número alto)
    for task in sorted(tasks, key=lambda t: (t.get('priority', 5), t.get('createdDateTime', '2099-12-31'))):
        # Calcular la duración necesaria para esta tarea
        meeting_duration_minutes = calculate_meeting_duration(task)
        
        task_assigned = False
        
        for slot in sorted_slots:
            # Procesar formato de fecha con o sin milisegundos
            try:
                slot_start_str = slot['start'].split('.')[0] if '.' in slot['start'] else slot['start']
                slot_end_str = slot['end'].split('.')[0] if '.' in slot['end'] else slot['end']
                
                # Parsear fechas en formato ISO
                slot_start_utc = datetime.fromisoformat(slot_start_str)
                slot_end_utc = datetime.fromisoformat(slot_end_str)
                
                # Convertir de UTC a zona horaria de Madrid
                slot_start = convert_utc_to_madrid(slot_start_utc)
                slot_end = convert_utc_to_madrid(slot_end_utc)
            except (ValueError, KeyError):
                continue

            # Restricciones: lunes a viernes, 9 a 5, no más de 2 tareas por día
            if slot_start.weekday() >= 5 or slot_start.hour < 9 or slot_end.hour > 17:
                continue

            day_key = slot_start.date()
            if len([a for a in assigned if a['date'] == str(day_key)]) >= 2:
                continue

            # Verificar si el slot ya está en uso
            if slot_start in used_slots:
                continue
            
            # Verificar si el slot tiene suficiente duración para la tarea
            slot_duration_minutes = (slot_end - slot_start).total_seconds() / 60
            if slot_duration_minutes < meeting_duration_minutes:
                continue  # Este slot es demasiado corto para esta tarea
            
            # Calcular tiempo de fin ajustado si es necesario
            meeting_end = slot_start + timedelta(minutes=meeting_duration_minutes)
            if meeting_end > slot_end:
                meeting_end = slot_end
              # Formato para devolver
            meeting_end_str = meeting_end.isoformat()
            if '.' in slot['end']:  # Mantener formato consistente con el recibido
                meeting_end_str += '.0000000'              # Formato en UTC para mantener compatibilidad con la API
            # El meeting_end_str está en formato Madrid pero necesitamos convertirlo a UTC para la respuesta
            meeting_end_utc = meeting_end.astimezone(pytz.UTC)
            meeting_end_utc_str = meeting_end_utc.replace(tzinfo=None).isoformat()
            if '.' in slot['end']:
                meeting_end_utc_str += '.0000000'
                
            # Asignar tarea al slot
            assigned.append({
                'taskName': task.get('title', 'Sin título'),
                'taskId': task.get('id', ''),
                'reservationTime': slot['start'],  # Mantener el formato original UTC
                'reservationEnd': meeting_end_utc_str,  # Convertir de vuelta a UTC
                'calculatedDurationMinutes': meeting_duration_minutes,
                'dayOfWeek': slot_start.strftime('%A'),
                'date': str(slot_start.date()),
                'slotId': slot.get('id', ''),
                'madridTime': {
                    'start': slot_start.strftime('%Y-%m-%d %H:%M:%S %z'),
                    'end': meeting_end.strftime('%Y-%m-%d %H:%M:%S %z')
                }
            })
            used_slots.add(slot_start)
            task_assigned = True
            break
          # Si no se encontró ningún slot adecuado, intentamos ser menos restrictivos
        if not task_assigned:
            # Intentamos nuevamente sin la restricción de máximo 2 por día
            for slot in sorted_slots:
                try:
                    slot_start_str = slot['start'].split('.')[0] if '.' in slot['start'] else slot['start']
                    slot_end_str = slot['end'].split('.')[0] if '.' in slot['end'] else slot['end']
                    
                    # Parsear fechas en formato ISO
                    slot_start_utc = datetime.fromisoformat(slot_start_str)
                    slot_end_utc = datetime.fromisoformat(slot_end_str)
                    
                    # Convertir de UTC a zona horaria de Madrid
                    slot_start = convert_utc_to_madrid(slot_start_utc)
                    slot_end = convert_utc_to_madrid(slot_end_utc)
                except (ValueError, KeyError):
                    continue

                # Mantener restricción de días laborables y horario laboral
                if slot_start.weekday() >= 5 or slot_start.hour < 9 or slot_end.hour > 17:
                    continue

                if slot_start in used_slots:
                    continue
                
                # Verificar duración mínima (15 minutos al menos)
                slot_duration_minutes = (slot_end - slot_start).total_seconds() / 60
                if slot_duration_minutes < 15:
                    continue
                  # Ajustamos la duración si es necesario
                if slot_duration_minutes < meeting_duration_minutes:
                    meeting_duration_minutes = slot_duration_minutes
                
                meeting_end = slot_start + timedelta(minutes=meeting_duration_minutes)
                
                # Formato en UTC para mantener compatibilidad con la API
                meeting_end_utc = meeting_end.astimezone(pytz.UTC)
                meeting_end_utc_str = meeting_end_utc.replace(tzinfo=None).isoformat()
                if '.' in slot['end']:
                    meeting_end_utc_str += '.0000000'
                
                assigned.append({
                    'taskName': task.get('title', 'Sin título'),
                    'taskId': task.get('id', ''),
                    'reservationTime': slot['start'],
                    'reservationEnd': meeting_end_utc_str,
                    'calculatedDurationMinutes': meeting_duration_minutes,
                    'adjustedDuration': True,  # Indicar que se ajustó la duración
                    'dayOfWeek': slot_start.strftime('%A'),
                    'date': str(slot_start.date()),
                    'slotId': slot.get('id', ''),
                    'madridTime': {
                        'start': slot_start.strftime('%Y-%m-%d %H:%M:%S %z'),
                        'end': meeting_end.strftime('%Y-%m-%d %H:%M:%S %z')
                    }
                })
                used_slots.add(slot_start)
                break

    return assigned

def convert_utc_to_madrid(dt):
    """
    Convierte una fecha UTC a la zona horaria de Madrid.
    
    Args:
        dt: Objeto datetime en UTC sin información de zona horaria
        
    Returns:
        Objeto datetime en zona horaria de Madrid
    """
    # Añadir información de zona horaria UTC
    dt_utc = dt.replace(tzinfo=pytz.UTC)
    
    # Convertir a zona horaria de Madrid
    return dt_utc.astimezone(MADRID_TIMEZONE)

if __name__ == '__main__':
    # Obtener el puerto desde la variable de entorno (para Railway) o usar 5000 por defecto
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
