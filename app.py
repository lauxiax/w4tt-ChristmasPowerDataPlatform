"""
🏗 API REST para Asignación Inteligente de Tareas
=============================================
API que gestiona la asignación de tareas en la agenda del usuario,
distribuyéndolas de manera inteligente en horarios laborales.
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pytz
import os
from typing import List, Dict, Any, Tuple, Optional
from dateutil import parser

# ======================================================
# 🔧 Configuración
# ======================================================
class Config:
    """Configuración centralizada de la aplicación."""
    # Zona horaria
    MADRID_TIMEZONE = pytz.timezone('Europe/Madrid')
    
    # Horario laboral (9:00 - 17:00)
    BUSINESS_HOURS_START = 9
    BUSINESS_HOURS_END = 17
    
    # Duración de reuniones
    MIN_MEETING_DURATION = 60    # Duración mínima: 60 minutos
    MAX_MEETING_DURATION = 150   # Duración máxima: 150 minutos
    BASE_MEETING_DURATION = 90   # Duración base para cálculos
    
    # Reglas de espaciado
    MIN_GAP_BETWEEN_MEETINGS = 30  # Mínimo 30 minutos entre reuniones
    MAX_TASKS_PER_DAY = 2         # Máximo 2 tareas por día
    
    # Horizonte de programación
    DAYS_TO_SCHEDULE_AHEAD = 30   # Programar hasta 30 días en adelante

# Inicializar aplicación Flask
app = Flask(__name__)

# ======================================================
# 🌐 Endpoints de la API
# ======================================================
@app.route('/health-check', methods=['GET'])
def health_check():
    """Endpoint para verificar que la API está funcionando correctamente."""
    return jsonify({
        "status": "OK",
        "message": "API funcionando correctamente",
        "timestamp": datetime.now(pytz.UTC).isoformat(),
        "version": "1.0.0"
    })

@app.route('/assign-tasks', methods=['POST'])
def assign_tasks():
    """
    Endpoint principal para asignar tareas a slots de tiempo disponibles.
    
    Recibe:
    - Lista de tareas a programar
    - Lista de slots de tiempo ya ocupados
    
    Retorna:
    - Lista de asignaciones de tareas a horarios específicos
    """
    try:
        # Obtener y validar datos de entrada
        data = request.get_json()
        if not data or 'tasks' not in data or 'slots' not in data:
            return jsonify({"error": "Se requieren las listas 'tasks' y 'slots'"}), 400
        
        # Validar formato de datos
        validation_error = validate_input_data(data)
        if validation_error:
            return jsonify({"error": validation_error}), 400
        
        # Obtener listas de tareas y slots ocupados
        tasks = data['tasks']
        busy_slots = data['slots']
        
        # Procesar asignación de tareas
        scheduler = TaskScheduler()
        assigned_tasks = scheduler.schedule_tasks(tasks, busy_slots)
        
        # Retornar asignaciones
        return jsonify(assigned_tasks)
        
    except Exception as e:
        # Log del error para depuración en producción
        print(f"Error procesando la solicitud: {str(e)}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

# ======================================================
# ⚙️ Validación de Datos
# ======================================================
def validate_input_data(data: Dict) -> Optional[str]:
    """
    Valida el formato y estructura de los datos de entrada.
    
    Args:
        data: Diccionario con los datos de entrada
        
    Returns:
        Mensaje de error si hay problemas, None si todo está correcto
    """
    # Validar estructura básica
    if not isinstance(data['tasks'], list):
        return "El campo 'tasks' debe ser una lista"
    
    if not isinstance(data['slots'], list):
        return "El campo 'slots' debe ser una lista"
    
    # Validar formato de tareas
    for i, task in enumerate(data['tasks']):
        if not isinstance(task, dict):
            return f"La tarea en posición {i} debe ser un objeto"
        
        # Campos requeridos
        for field in ['id', 'title']:
            if field not in task:
                return f"La tarea en posición {i} requiere el campo '{field}'"
    
    # Validar formato de slots ocupados
    for i, slot in enumerate(data['slots']):
        if not isinstance(slot, dict):
            return f"El slot en posición {i} debe ser un objeto"
        
        # Campos requeridos
        for field in ['start', 'end']:
            if field not in slot:
                return f"El slot en posición {i} requiere el campo '{field}'"
        
        # Validar formato de fechas
        try:
            parser.parse(slot['start'])
            parser.parse(slot['end'])
        except ValueError:
            return f"Formato de fecha inválido en slot {i}"
    
    return None

# ======================================================
# 🕒 Gestión de Zonas Horarias
# ======================================================
class TimezoneConverter:
    """Utilidad para conversión entre zonas horarias."""
    
    @staticmethod
    def utc_to_madrid(dt: datetime) -> datetime:
        """
        Convierte una fecha UTC a zona horaria de Madrid.
        
        Args:
            dt: Fecha en UTC (con o sin info de zona horaria)
            
        Returns:
            Fecha en zona horaria de Madrid
        """
        # Asegurar que la fecha tiene zona horaria UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pytz.UTC)
        elif dt.tzinfo != pytz.UTC:
            dt = dt.astimezone(pytz.UTC)
            
        # Convertir a Madrid
        return dt.astimezone(Config.MADRID_TIMEZONE)
    
    @staticmethod
    def madrid_to_utc(dt: datetime) -> datetime:
        """
        Convierte una fecha de Madrid a UTC.
        
        Args:
            dt: Fecha en zona horaria de Madrid
            
        Returns:
            Fecha en UTC
        """
        # Asegurar que la fecha tiene zona horaria de Madrid
        if dt.tzinfo is None:
            dt = Config.MADRID_TIMEZONE.localize(dt)
        elif dt.tzinfo != Config.MADRID_TIMEZONE:
            dt = dt.astimezone(Config.MADRID_TIMEZONE)
            
        # Convertir a UTC
        return dt.astimezone(pytz.UTC)
    
    @staticmethod
    def parse_datetime(dt_str: str, default_timezone=pytz.UTC) -> datetime:
        """
        Parsea una cadena de fecha/hora y asegura que tenga zona horaria.
        
        Args:
            dt_str: Cadena de fecha/hora
            default_timezone: Zona horaria a usar si no se especifica una
            
        Returns:
            Objeto datetime con zona horaria
        """
        dt = parser.parse(dt_str)
        
        # Asignar zona horaria si no tiene
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=default_timezone)
            
        return dt

# ======================================================
# 📊 Cálculo de Duración y Prioridad
# ======================================================
class TaskAnalyzer:
    """Analiza tareas para determinar su duración y prioridad."""
    
    @staticmethod
    def calculate_duration(task: Dict[str, Any]) -> int:
        """
        Calcula la duración óptima para una tarea en minutos.
        
        Args:
            task: Diccionario con datos de la tarea
            
        Returns:
            Duración en minutos (entre 60 y 150)
        """
        base_duration = Config.BASE_MEETING_DURATION  # 90 minutos base
        
        # Ajuste por prioridad (0=más urgente)
        priority = task.get('priority', 2)
        if priority == 0:  # Ultra urgente
            base_duration += 30
        elif priority == 1:  # Muy importante
            base_duration += 20
        
        # Ajuste por porcentaje completado
        percent_complete = task.get('percentComplete', 0)
        if percent_complete < 20:
            base_duration += 15  # Tareas apenas iniciadas necesitan más tiempo
        
        # Ajuste por cantidad de ítems en la lista de verificación
        checklist_items = task.get('checklistItemCount', 0)
        if checklist_items > 5:
            base_duration += 15
        
        # Ajuste por descripción extensa
        if task.get('hasDescription', False):
            base_duration += 10
        
        # Limitar a los rangos permitidos
        return min(max(base_duration, Config.MIN_MEETING_DURATION), Config.MAX_MEETING_DURATION)
    
    @staticmethod
    def calculate_priority_score(task: Dict[str, Any], current_date: Optional[datetime] = None) -> float:
        """
        Calcula un puntaje de prioridad para ordenar las tareas.
        Mayor puntaje = más prioritario.
        
        Args:
            task: Diccionario con datos de la tarea
            current_date: Fecha actual para cálculos relativos
            
        Returns:
            Puntuación de prioridad (más alto = más prioritario)
        """
        if current_date is None:
            current_date = datetime.now(pytz.UTC)
        
        score = 0.0
        
        # Factor de prioridad explícita (invertido porque 0=más prioritario)
        priority = task.get('priority', 5)
        score += 100 * (5 - min(priority, 5)) / 5
        
        # Factor de fecha de vencimiento
        if 'dueDateTime' in task:
            try:
                due_date = TimezoneConverter.parse_datetime(task['dueDateTime'])
                days_to_due = (due_date - current_date).total_seconds() / 86400
                
                # Más cercano al vencimiento = más prioritario
                if days_to_due <= 0:
                    # Ya vencido
                    score += 80
                elif days_to_due <= 1:
                    # Vence en 24 horas
                    score += 70
                elif days_to_due <= 3:
                    # Vence en 3 días
                    score += 60
                elif days_to_due <= 7:
                    # Vence en una semana
                    score += 50
                elif days_to_due <= 14:
                    # Vence en dos semanas
                    score += 30
                else:
                    # Vence en más tiempo
                    score += 10
            except (ValueError, TypeError):
                # Error al procesar la fecha
                pass
        
        # Factor de antigüedad (tareas más antiguas son más prioritarias)
        if 'createdDateTime' in task:
            try:
                created_date = TimezoneConverter.parse_datetime(task['createdDateTime'])
                days_since_creation = (current_date - created_date).total_seconds() / 86400
                
                if days_since_creation > 30:
                    score += 30  # Más de un mes
                elif days_since_creation > 14:
                    score += 20  # Más de dos semanas
                elif days_since_creation > 7:
                    score += 15  # Más de una semana
                elif days_since_creation > 3:
                    score += 10  # Más de tres días
            except (ValueError, TypeError):
                # Error al procesar la fecha
                pass
        
        # Factor de progreso (tareas con menos progreso son más prioritarias)
        percent_complete = task.get('percentComplete', 0)
        score += 20 * (100 - percent_complete) / 100
        
        return score

# ======================================================
# 📅 Generación y Validación de Slots
# ======================================================
class SlotManager:
    """Gestiona la creación y validación de slots de tiempo disponibles."""
    
    def __init__(self):
        self.madrid_tz = Config.MADRID_TIMEZONE
    
    def generate_available_slots(self, 
                                 busy_periods: List[Tuple[datetime, datetime]], 
                                 assigned_periods: List[Tuple[datetime, datetime]],
                                 current_date: datetime,
                                 days_ahead: int = Config.DAYS_TO_SCHEDULE_AHEAD) -> List[Dict]:
        """
        Genera todos los slots de tiempo disponibles para programar tareas.
        
        Args:
            busy_periods: Lista de períodos ocupados a evitar (inicio, fin)
            assigned_periods: Lista de períodos ya asignados por el algoritmo
            current_date: Fecha actual para comenzar la generación
            days_ahead: Cuántos días hacia adelante generar
            
        Returns:
            Lista de diccionarios con slots disponibles
        """
        available_slots = []
        start_date = current_date.date()
        
        # Generar slots para los próximos días
        for day_offset in range(days_ahead):
            current_day = start_date + timedelta(days=day_offset)
            
            # Saltar fines de semana (5=sábado, 6=domingo)
            if current_day.weekday() >= 5:
                continue
            
            # Verificar cuántas tareas ya están asignadas este día
            day_assigned_count = self._count_day_assignments(current_day, assigned_periods)
            
            # Si ya hay 2 tareas asignadas este día, saltarlo
            if day_assigned_count >= Config.MAX_TASKS_PER_DAY:
                continue
            
            # Generar slots disponibles para este día
            day_slots = self._generate_day_slots(
                current_day, 
                current_date, 
                busy_periods, 
                assigned_periods
            )
            
            # Añadir a la lista general
            available_slots.extend(day_slots)
            
            # Si encontramos suficientes slots, podemos terminar
            if len(available_slots) >= 10:  # Número arbitrario para limitar la búsqueda
                break
        
        return available_slots
    
    def _count_day_assignments(self, day: datetime.date, assigned_periods: List[Tuple[datetime, datetime]]) -> int:
        """Cuenta cuántas tareas ya están asignadas en un día específico."""
        count = 0
        for start, _ in assigned_periods:
            if start.date() == day:
                count += 1
        return count
    
    def _generate_day_slots(self, 
                           day: datetime.date, 
                           current_datetime: datetime,
                           busy_periods: List[Tuple[datetime, datetime]], 
                           assigned_periods: List[Tuple[datetime, datetime]]) -> List[Dict]:
        """
        Genera slots disponibles para un día específico.
        
        Args:
            day: Fecha del día a generar
            current_datetime: Fecha y hora actual
            busy_periods: Períodos ocupados a evitar
            assigned_periods: Períodos ya asignados
            
        Returns:
            Lista de slots disponibles para este día
        """
        slots = []
        
        # Definir inicio y fin del día laboral
        day_start = self.madrid_tz.localize(
            datetime.combine(day, datetime.min.time().replace(hour=Config.BUSINESS_HOURS_START))
        )
        day_end = self.madrid_tz.localize(
            datetime.combine(day, datetime.min.time().replace(hour=Config.BUSINESS_HOURS_END))
        )
        
        # Si es hoy, ajustar la hora de inicio al momento actual
        if day == current_datetime.date() and day_start < current_datetime:
            # Redondear a la siguiente hora completa
            next_hour = current_datetime.hour + 1
            if next_hour >= Config.BUSINESS_HOURS_END:
                return slots  # Ya es muy tarde hoy
            
            day_start = self.madrid_tz.localize(
                datetime.combine(day, datetime.min.time().replace(hour=next_hour))
            )
        
        # Dividir el día en slots potenciales de 60 minutos
        # (Podríamos usar 30 minutos, pero para reuniones de 60+ minutos es innecesario)
        slot_duration = 60  # minutos
        current_time = day_start
        
        while current_time < day_end:
            slot_end = current_time + timedelta(minutes=slot_duration)
            if slot_end > day_end:
                slot_end = day_end
            
            # Ver si este slot está disponible
            if self._is_slot_available(current_time, slot_end, busy_periods, assigned_periods):
                slots.append({
                    "start": current_time,
                    "end": slot_end,
                    "duration_minutes": int((slot_end - current_time).total_seconds() / 60)
                })
            
            # Avanzar al siguiente slot
            current_time = current_time + timedelta(minutes=slot_duration)
        
        return slots
    
    def _is_slot_available(self, 
                          start: datetime, 
                          end: datetime, 
                          busy_periods: List[Tuple[datetime, datetime]],
                          assigned_periods: List[Tuple[datetime, datetime]]) -> bool:
        """
        Verifica si un slot está disponible (no solapa con períodos ocupados o asignados).
        
        Args:
            start: Inicio del slot a verificar
            end: Fin del slot a verificar
            busy_periods: Períodos ocupados a evitar
            assigned_periods: Períodos ya asignados
            
        Returns:
            True si está disponible, False si solapa
        """
        # Verificar solapamiento con períodos ocupados
        for busy_start, busy_end in busy_periods:
            if self._periods_overlap(start, end, busy_start, busy_end):
                return False
        
        # Verificar solapamiento con períodos asignados
        for assigned_start, assigned_end in assigned_periods:
            if self._periods_overlap(start, end, assigned_start, assigned_end):
                return False
            
            # Verificar si no respeta el tiempo mínimo entre reuniones
            gap_minutes = Config.MIN_GAP_BETWEEN_MEETINGS
            
            # Caso 1: Nueva reunión antes de una existente
            if end <= assigned_start and (assigned_start - end).total_seconds() / 60 < gap_minutes:
                return False
            
            # Caso 2: Nueva reunión después de una existente
            if start >= assigned_end and (start - assigned_end).total_seconds() / 60 < gap_minutes:
                return False
        
        return True
    
    @staticmethod
    def _periods_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """
        Verifica si dos períodos de tiempo se solapan.
        
        Args:
            start1, end1: Inicio y fin del primer período
            start2, end2: Inicio y fin del segundo período
            
        Returns:
            True si hay solapamiento, False en caso contrario
        """
        return start1 < end2 and end1 > start2

# ======================================================
# 🧩 Programador de Tareas
# ======================================================
class TaskScheduler:
    """Clase principal para programar tareas en slots disponibles."""
    
    def __init__(self):
        self.slot_manager = SlotManager()
        self.task_analyzer = TaskAnalyzer()
        self.current_date = datetime.now(Config.MADRID_TIMEZONE)
    
    def schedule_tasks(self, tasks: List[Dict], busy_slots: List[Dict]) -> List[Dict]:
        """
        Programa tareas en slots disponibles según las reglas definidas.
        
        Args:
            tasks: Lista de tareas a programar
            busy_slots: Lista de slots ocupados a evitar
            
        Returns:
            Lista de asignaciones de tareas
        """
        # Procesar slots ocupados a formato datetime
        busy_periods = self._process_busy_slots(busy_slots)
        
        # Lista para almacenar asignaciones y períodos asignados
        assigned_tasks = []
        assigned_periods = []
        
        # Ordenar tareas por prioridad
        sorted_tasks = sorted(
            tasks, 
            key=lambda t: self.task_analyzer.calculate_priority_score(t, self.current_date),
            reverse=True  # Mayor puntaje primero
        )
        
        # Asignar cada tarea
        for task in sorted_tasks:
            assignment = self._assign_task(task, busy_periods, assigned_periods)
            
            if assignment:
                assigned_tasks.append(assignment)
                
                # Registrar período asignado para futuras validaciones
                start = TimezoneConverter.parse_datetime(assignment['madridTime']['start'])
                end = TimezoneConverter.parse_datetime(assignment['madridTime']['end'])
                assigned_periods.append((start, end))
        
        return assigned_tasks
    
    def _process_busy_slots(self, busy_slots: List[Dict]) -> List[Tuple[datetime, datetime]]:
        """Convierte los slots ocupados a períodos datetime en zona horaria de Madrid."""
        busy_periods = []
        
        for slot in busy_slots:
            try:
                # Parsear fechas y convertir a zona horaria de Madrid
                start_utc = TimezoneConverter.parse_datetime(slot['start'])
                end_utc = TimezoneConverter.parse_datetime(slot['end'])
                
                start_madrid = TimezoneConverter.utc_to_madrid(start_utc)
                end_madrid = TimezoneConverter.utc_to_madrid(end_utc)
                
                busy_periods.append((start_madrid, end_madrid))
            except Exception:
                # Ignorar slots con formato inválido
                continue
        
        return busy_periods
    
    def _assign_task(self, 
                    task: Dict, 
                    busy_periods: List[Tuple[datetime, datetime]], 
                    assigned_periods: List[Tuple[datetime, datetime]]) -> Optional[Dict]:
        """
        Asigna una tarea individual al mejor slot disponible.
        
        Args:
            task: Tarea a asignar
            busy_periods: Períodos ocupados a evitar
            assigned_periods: Períodos ya asignados
            
        Returns:
            Diccionario con la asignación o None si no fue posible asignar
        """
        # Calcular duración necesaria para la tarea
        task_duration = self.task_analyzer.calculate_duration(task)
        
        # Generar slots disponibles
        available_slots = self.slot_manager.generate_available_slots(
            busy_periods, 
            assigned_periods,
            self.current_date
        )
        
        # Si no hay slots disponibles, retornar None
        if not available_slots:
            return None
        
        # Buscar el primer slot que tenga suficiente duración
        selected_slot = None
        for slot in available_slots:
            if slot['duration_minutes'] >= task_duration:
                selected_slot = slot
                break
        
        # Si no encontramos slot adecuado, usar el más grande disponible
        if not selected_slot and available_slots:
            selected_slot = max(available_slots, key=lambda s: s['duration_minutes'])
            # Ajustar duración si es necesario
            if selected_slot['duration_minutes'] < Config.MIN_MEETING_DURATION:
                # No podemos asignar esta tarea
                return None
            
            task_duration = min(task_duration, selected_slot['duration_minutes'])
        
        # Si no encontramos ningún slot, no podemos asignar
        if not selected_slot:
            return None
        
        # Calcular tiempo de fin real (puede ser menos que la duración calculada)
        meeting_start = selected_slot['start']
        meeting_end = meeting_start + timedelta(minutes=task_duration)
        
        # Asegurar que no exceda el fin del slot
        if meeting_end > selected_slot['end']:
            meeting_end = selected_slot['end']
            task_duration = int((meeting_end - meeting_start).total_seconds() / 60)
        
        # Crear la asignación en formato de respuesta
        return self._format_assignment(task, meeting_start, meeting_end, task_duration)
    
    def _format_assignment(self, 
                          task: Dict, 
                          start_time_madrid: datetime, 
                          end_time_madrid: datetime,
                          duration_minutes: int) -> Dict:
        """
        Formatea una asignación de tarea en el formato de respuesta esperado.
        
        Args:
            task: La tarea asignada
            start_time_madrid: Hora de inicio en zona horaria de Madrid
            end_time_madrid: Hora de fin en zona horaria de Madrid
            duration_minutes: Duración real en minutos
            
        Returns:
            Diccionario con el formato de respuesta esperado
        """
        # Convertir a UTC para la respuesta
        start_time_utc = TimezoneConverter.madrid_to_utc(start_time_madrid)
        end_time_utc = TimezoneConverter.madrid_to_utc(end_time_madrid)
        
        # Verificar si la duración fue ajustada respecto a la calculada
        calculated_duration = self.task_analyzer.calculate_duration(task)
        duration_adjusted = duration_minutes != calculated_duration
        
        # Formatear fechas en el formato esperado por la API
        start_utc_str = start_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_utc_str = end_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Formatear fechas de Madrid
        start_madrid_str = start_time_madrid.strftime("%Y-%m-%d %H:%M:%S %z")
        end_madrid_str = end_time_madrid.strftime("%Y-%m-%d %H:%M:%S %z")
        
        # Construir respuesta
        assignment = {
            "taskName": task.get('title', 'Sin título'),
            "taskId": task.get('id', ''),
            "reservationTime": start_utc_str,
            "reservationEnd": end_utc_str,
            "calculatedDurationMinutes": duration_minutes,
            "dayOfWeek": start_time_madrid.strftime("%A"),
            "date": start_time_madrid.strftime("%Y-%m-%d"),
            "slotId": f"generated_{start_time_madrid.isoformat()}",
            "madridTime": {
                "start": start_madrid_str,
                "end": end_madrid_str
            }
        }
        
        # Añadir flag de duración ajustada si aplica
        if duration_adjusted:
            assignment["adjustedDuration"] = True
        
        return assignment

# ======================================================
# 🚀 Punto de entrada de la aplicación
# ======================================================
if __name__ == '__main__':
    # Obtener puerto desde variable de entorno (para Railway) o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
