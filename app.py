from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# Constante para la zona horaria de Madrid
MADRID_TIMEZONE = pytz.timezone('Europe/Madrid')

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
    busy_slots = data['slots']  # Los slots que me envías son los ocupados que debo evitar
    
    # Los slots que recibo son los BUSY que debo evitar, no los disponibles
    # Por eso no filtro, sino que los uso como lista de conflictos
    assigned_slots = assign_tasks_to_slots(tasks, busy_slots)
    
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

def assign_tasks_to_slots(tasks, busy_slots):
    """
    Asigna tareas a slots de tiempo disponible, evitando los slots ocupados.
    
    Args:
        tasks: Lista de tareas a asignar
        busy_slots: Lista de slots ocupados que debo evitar
    """
    assigned = []
    used_slots = set()
    
    # Generar slots de tiempo disponibles (lunes a viernes, 9-17, cada 30 min)
    available_time_slots = generate_available_time_slots(busy_slots)
    
    # Ordenar tareas por prioridad y fecha de creación (prioridad baja en Planner es número alto)
    for task in sorted(tasks, key=lambda t: (t.get('priority', 5), t.get('createdDateTime', '2099-12-31'))):
        # Calcular la duración necesaria para esta tarea
        meeting_duration_minutes = calculate_meeting_duration(task)
        
        task_assigned = False
        
        for slot in available_time_slots:
            # Verificar si el slot ya está en uso
            if slot['start_time'] in used_slots:
                continue
            
            # Verificar si el slot tiene suficiente duración para la tarea
            slot_duration_minutes = (slot['end_time'] - slot['start_time']).total_seconds() / 60
            if slot_duration_minutes < meeting_duration_minutes:
                continue  # Este slot es demasiado corto para esta tarea
            
            # Verificar límite de 2 tareas por día
            day_key = slot['start_time'].date()
            if len([a for a in assigned if a['date'] == str(day_key)]) >= 2:
                continue
            
            # Calcular tiempo de fin
            meeting_end = slot['start_time'] + timedelta(minutes=meeting_duration_minutes)
            if meeting_end > slot['end_time']:
                meeting_end = slot['end_time']
            
            # Convertir a UTC para la respuesta
            start_utc = slot['start_time'].astimezone(pytz.UTC)
            end_utc = meeting_end.astimezone(pytz.UTC)
            
            # Formatear fechas UTC para respuesta
            start_utc_str = start_utc.replace(tzinfo=None).isoformat() + '.0000000'
            end_utc_str = end_utc.replace(tzinfo=None).isoformat() + '.0000000'
                
            # Asignar tarea al slot
            assigned.append({
                'taskName': task.get('title', 'Sin título'),
                'taskId': task.get('id', ''),
                'reservationTime': start_utc_str,
                'reservationEnd': end_utc_str,
                'calculatedDurationMinutes': meeting_duration_minutes,
                'dayOfWeek': slot['start_time'].strftime('%A'),
                'date': str(slot['start_time'].date()),
                'slotId': f"generated_{slot['start_time'].isoformat()}",
                'madridTime': {
                    'start': slot['start_time'].strftime('%Y-%m-%d %H:%M:%S %z'),
                    'end': meeting_end.strftime('%Y-%m-%d %H:%M:%S %z')
                }
            })
            used_slots.add(slot['start_time'])
            task_assigned = True
            break
        
        # Si no se pudo asignar con restricción de 2 por día, intentar sin esa restricción
        if not task_assigned:
            for slot in available_time_slots:
                if slot['start_time'] in used_slots:
                    continue
                
                # Verificar duración mínima (15 minutos al menos)
                slot_duration_minutes = (slot['end_time'] - slot['start_time']).total_seconds() / 60
                if slot_duration_minutes < 15:
                    continue
                
                # Ajustar duración si es necesario
                if slot_duration_minutes < meeting_duration_minutes:
                    meeting_duration_minutes = slot_duration_minutes
                
                meeting_end = slot['start_time'] + timedelta(minutes=meeting_duration_minutes)
                
                # Convertir a UTC para la respuesta
                start_utc = slot['start_time'].astimezone(pytz.UTC)
                end_utc = meeting_end.astimezone(pytz.UTC)
                
                # Formatear fechas UTC para respuesta
                start_utc_str = start_utc.replace(tzinfo=None).isoformat() + '.0000000'
                end_utc_str = end_utc.replace(tzinfo=None).isoformat() + '.0000000'
                
                assigned.append({
                    'taskName': task.get('title', 'Sin título'),
                    'taskId': task.get('id', ''),
                    'reservationTime': start_utc_str,
                    'reservationEnd': end_utc_str,
                    'calculatedDurationMinutes': meeting_duration_minutes,
                    'adjustedDuration': True,  # Indicar que se ajustó la duración
                    'dayOfWeek': slot['start_time'].strftime('%A'),
                    'date': str(slot['start_time'].date()),
                    'slotId': f"generated_{slot['start_time'].isoformat()}",
                    'madridTime': {
                        'start': slot['start_time'].strftime('%Y-%m-%d %H:%M:%S %z'),
                        'end': meeting_end.strftime('%Y-%m-%d %H:%M:%S %z')
                    }
                })
                used_slots.add(slot['start_time'])
                break

    return assigned

def generate_available_time_slots(busy_slots, days_ahead=30):
    """
    Genera slots de tiempo disponibles evitando los slots ocupados.
    
    Args:
        busy_slots: Lista de slots ocupados que debo evitar
        days_ahead: Número de días a generar hacia adelante
        
    Returns:
        Lista de slots disponibles en formato Madrid
    """
    available_slots = []
    
    # Obtener fecha actual en Madrid
    madrid_now = datetime.now(MADRID_TIMEZONE)
    start_date = madrid_now.date()
    
    # Convertir busy_slots a períodos ocupados en Madrid
    busy_periods = []
    for busy_slot in busy_slots:
        try:
            # Procesar formato de fecha con o sin milisegundos
            start_str = busy_slot['start'].split('.')[0] if '.' in busy_slot['start'] else busy_slot['start']
            end_str = busy_slot['end'].split('.')[0] if '.' in busy_slot['end'] else busy_slot['end']
            
            # Parsear fechas UTC y convertir a Madrid
            start_utc = datetime.fromisoformat(start_str)
            end_utc = datetime.fromisoformat(end_str)
            
            start_madrid = convert_utc_to_madrid(start_utc)
            end_madrid = convert_utc_to_madrid(end_utc)
            
            busy_periods.append((start_madrid, end_madrid))
        except (ValueError, KeyError):
            continue
    
    # Generar slots para los próximos días
    for day_offset in range(days_ahead):
        current_date = start_date + timedelta(days=day_offset)
        
        # Solo días laborables (lunes=0, domingo=6)
        if current_date.weekday() >= 5:  # Sábado o domingo
            continue
        
        # Generar slots de 30 minutos desde las 9:00 hasta las 17:00
        current_day_start = MADRID_TIMEZONE.localize(
            datetime.combine(current_date, datetime.min.time().replace(hour=9))
        )
        current_day_end = MADRID_TIMEZONE.localize(
            datetime.combine(current_date, datetime.min.time().replace(hour=17))
        )
        
        # Solo considerar slots futuros
        if current_day_start < madrid_now:
            # Si es hoy, empezar desde la hora actual redondeada
            if current_date == madrid_now.date():
                current_hour = madrid_now.hour
                current_minute = madrid_now.minute
                # Redondear a la siguiente media hora
                if current_minute > 0:
                    current_hour += 1
                if current_hour >= 17:  # Si ya es muy tarde hoy, saltar al siguiente día
                    continue
                current_day_start = MADRID_TIMEZONE.localize(
                    datetime.combine(current_date, datetime.min.time().replace(hour=max(9, current_hour)))
                )
        
        # Generar slots de 30 minutos
        slot_start = current_day_start
        while slot_start < current_day_end:
            slot_end = slot_start + timedelta(minutes=30)
            
            # Verificar que no solapea con ningún período ocupado
            is_available = True
            for busy_start, busy_end in busy_periods:
                # Verificar solapamiento
                if (slot_start < busy_end) and (slot_end > busy_start):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append({
                    'start_time': slot_start,
                    'end_time': slot_end
                })
            
            slot_start = slot_end
    
    return available_slots

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
