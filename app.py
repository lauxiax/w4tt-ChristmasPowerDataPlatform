from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# Constante para la zona horaria de Madrid
MADRID_TIMEZONE = pytz.timezone('Europe/Madrid')

def is_slot_available(slot):
    """
    Determina si un slot está disponible para programar una reunión.
    
    Para datos provenientes de Power Automate, asumimos que todos los slots
    devueltos por la búsqueda de tiempo libre son potencialmente disponibles,
    independientemente del campo showAs.
    """
    # El campo 'showAs' es el indicador más confiable en circunstancias normales
    show_as = slot.get('showAs', '')
    
    # Si está marcado como libre, definitivamente está disponible
    if show_as == 'free':
        return True
    
    # Si está marcado como tentativo, puede estar disponible
    if show_as == 'tentative':
        return True
    
    # Si está marcado como fuera de oficina, NO está disponible
    if show_as == 'oof':  # Out of Office
        return False
    
    # Si está marcado como trabajando en otro lugar, consideramos que no está disponible
    if show_as == 'workingElsewhere':
        return False
    
    # Para slots marcados como "busy", necesitamos analizar más contexto
    # ya que Power Automate puede devolver slots "busy" que son en realidad disponibles
    if show_as == 'busy':
        # Si el slot tiene características de un bloque de tiempo generado automáticamente,
        # probablemente sea un slot disponible marcado por Power Automate
        
        # Verificar si es un evento real con contenido o un placeholder
        subject = slot.get('subject', '').strip()
        
        # Si no tiene organizador definido o es el usuario actual, podría ser disponible
        organizer = slot.get('organizer', '')
        
        # Si no tiene ubicación específica, podría ser un slot libre
        location = slot.get('location', '').strip()
        
        # Si no tiene attendees o solo tiene attendees vacíos
        required_attendees = slot.get('requiredAttendees', '').strip()
        optional_attendees = slot.get('optionalAttendees', '').strip()
        
        # Heurística: si es un slot simple sin muchos detalles, probablemente está disponible
        has_minimal_details = (
            not location and 
            not required_attendees and 
            not optional_attendees and
            len(subject) < 50  # Subject corto o genérico
        )
        
        if has_minimal_details:
            return True
    
    # Si no tiene el campo showAs definido, verificamos otros indicadores
    # Esto puede suceder con slots generados por Power Automate
    
    # Si no tiene subject o tiene un subject muy genérico/vacío, podría ser un slot libre
    subject = slot.get('subject', '').strip()
    if not subject:
        return True
    
    # Si no hay asistentes requeridos, podría estar disponible
    required_attendees = slot.get('requiredAttendees', '')
    if not required_attendees or required_attendees.strip() == '':
        return True
    
    # Por defecto, si no podemos determinar el estado claramente, 
    # asumimos que está disponible ya que proviene de una búsqueda de tiempo libre
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
