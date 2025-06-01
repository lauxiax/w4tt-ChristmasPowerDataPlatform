"""
W4TT - Task Assignment API
Assigns tasks to available time slots while avoiding busy periods.
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pytz
import os
from typing import List, Dict, Any, Tuple, Optional

# Configuration
class Config:
    """Application configuration constants."""
    MADRID_TIMEZONE = pytz.timezone('Europe/Madrid')
    BUSINESS_HOURS_START = 9
    BUSINESS_HOURS_END = 17
    SLOT_DURATION_MINUTES = 30
    MAX_TASKS_PER_DAY = 2
    MIN_MEETING_DURATION = 15
    MAX_MEETING_DURATION = 60
    DEFAULT_MEETING_DURATION = 30
    FUTURE_DAYS_LIMIT = 30

app = Flask(__name__)

# API Routes
@app.route('/', methods=['GET'])
def home():
    """Health check endpoint."""
    return jsonify({
        "status": "API funcionando correctamente", 
        "message": "Usa el endpoint /assign-tasks para asignar tareas"
    })

@app.route('/assign-tasks', methods=['POST'])
def assign_tasks():
    """
    Main endpoint to assign tasks to available time slots.
    
    Request body should contain:
    - tasks: List of task objects to assign
    - slots: List of busy time slots to avoid
    
    Returns:
    - List of assigned tasks with time slot information
    """
    try:
        data = request.get_json()
        
        # Input validation
        validation_error = _validate_request_data(data)
        if validation_error:
            return jsonify({"error": validation_error}), 400
        
        tasks = data['tasks']
        busy_slots = data['slots']
        
        # Create task scheduler and assign tasks
        scheduler = TaskScheduler()
        assigned_slots = scheduler.assign_tasks_to_slots(tasks, busy_slots)
        
        return jsonify(assigned_slots)
        
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

def _validate_request_data(data: Optional[Dict]) -> Optional[str]:
    """Validate request data and return error message if invalid."""
    if not data:
        return "No se recibió datos JSON válidos"
    
    if 'tasks' not in data or 'slots' not in data:
        return "Se requieren las listas 'tasks' y 'slots'"
    
    if not isinstance(data['tasks'], list) or not isinstance(data['slots'], list):
        return "Las listas 'tasks' y 'slots' deben ser arrays"
    
    return None

# Core Classes
class TaskDurationCalculator:
    """Calculates optimal meeting duration based on task characteristics."""
    
    @staticmethod
    def calculate_meeting_duration(task: Dict[str, Any]) -> int:
        """
        Calculate optimal meeting duration based on task properties.
        
        Args:
            task: Task object with Planner properties
            
        Returns:
            Duration in minutes (15-60 range)
        """
        base_duration = Config.DEFAULT_MEETING_DURATION
        
        # Priority adjustment (0=urgent, 1=important, 2=medium, 3=low)
        priority = task.get('priority', 5)
        if priority == 0:  # Urgent
            base_duration += 15
        elif priority == 1:  # Important
            base_duration += 10
        
        # Complexity adjustment based on completion percentage
        percent_complete = task.get('percentComplete', 0)
        if percent_complete < 20:
            base_duration += 10  # Early stage tasks need more planning
        
        # Checklist items adjustment
        checklist_count = task.get('checklistItemCount', 0)
        if checklist_count > 5:
            base_duration += 10
        
        # Description detail adjustment
        if task.get('hasDescription', False):
            base_duration += 5
        
        # Ensure duration is within limits
        return min(max(base_duration, Config.MIN_MEETING_DURATION), Config.MAX_MEETING_DURATION)


class TimeSlotGenerator:
    """Generates available time slots while avoiding busy periods."""
    
    def __init__(self):
        self.madrid_tz = Config.MADRID_TIMEZONE
    
    def generate_available_slots(self, busy_slots: List[Dict], days_ahead: int = Config.FUTURE_DAYS_LIMIT) -> List[Dict]:
        """
        Generate available time slots avoiding busy periods.
        
        Args:
            busy_slots: List of busy time periods to avoid
            days_ahead: Number of days to generate slots for
            
        Returns:
            List of available time slot dictionaries
        """
        available_slots = []
        madrid_now = datetime.now(self.madrid_tz)
        start_date = madrid_now.date()
        
        # Parse busy periods
        busy_periods = self._parse_busy_periods(busy_slots)
        
        # Generate slots for future business days
        for day_offset in range(days_ahead):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            day_slots = self._generate_day_slots(current_date, madrid_now, busy_periods)
            available_slots.extend(day_slots)
        
        return available_slots
    
    def _parse_busy_periods(self, busy_slots: List[Dict]) -> List[Tuple[datetime, datetime]]:
        """Parse busy slots into Madrid timezone periods."""
        busy_periods = []
        
        for busy_slot in busy_slots:
            try:
                start_madrid, end_madrid = self._parse_slot_times(busy_slot)
                busy_periods.append((start_madrid, end_madrid))
            except (ValueError, KeyError) as e:
                # Log warning in production
                continue
        
        return busy_periods
    
    def _parse_slot_times(self, slot: Dict) -> Tuple[datetime, datetime]:
        """Parse slot start/end times and convert to Madrid timezone."""
        # Remove milliseconds if present
        start_str = slot['start'].split('.')[0] if '.' in slot['start'] else slot['start']
        end_str = slot['end'].split('.')[0] if '.' in slot['end'] else slot['end']
        
        # Parse UTC times and convert to Madrid
        start_utc = datetime.fromisoformat(start_str)
        end_utc = datetime.fromisoformat(end_str)
        
        start_madrid = TimezoneConverter.utc_to_madrid(start_utc)
        end_madrid = TimezoneConverter.utc_to_madrid(end_utc)
        
        return start_madrid, end_madrid
    
    def _generate_day_slots(self, date: datetime.date, madrid_now: datetime, busy_periods: List[Tuple[datetime, datetime]]) -> List[Dict]:
        """Generate available slots for a specific day."""
        slots = []
        
        # Define business hours for the day
        day_start = self.madrid_tz.localize(
            datetime.combine(date, datetime.min.time().replace(hour=Config.BUSINESS_HOURS_START))
        )
        day_end = self.madrid_tz.localize(
            datetime.combine(date, datetime.min.time().replace(hour=Config.BUSINESS_HOURS_END))
        )
        
        # Adjust start time if it's today
        if date == madrid_now.date():
            day_start = self._adjust_today_start_time(madrid_now, day_start, day_end)
            if day_start >= day_end:
                return slots  # Too late today
        
        # Generate 30-minute slots
        slot_start = day_start
        while slot_start < day_end:
            slot_end = slot_start + timedelta(minutes=Config.SLOT_DURATION_MINUTES)
            
            if self._is_slot_available(slot_start, slot_end, busy_periods):
                slots.append({
                    'start_time': slot_start,
                    'end_time': slot_end
                })
            
            slot_start = slot_end
        
        return slots
    
    def _adjust_today_start_time(self, madrid_now: datetime, day_start: datetime, day_end: datetime) -> datetime:
        """Adjust start time for today to be in the future."""
        if day_start < madrid_now:
            current_hour = madrid_now.hour
            current_minute = madrid_now.minute
            
            # Round to next half hour
            if current_minute > 0:
                current_hour += 1
            
            adjusted_hour = max(Config.BUSINESS_HOURS_START, current_hour)
            return self.madrid_tz.localize(
                datetime.combine(madrid_now.date(), datetime.min.time().replace(hour=adjusted_hour))
            )
        
        return day_start
    
    def _is_slot_available(self, slot_start: datetime, slot_end: datetime, busy_periods: List[Tuple[datetime, datetime]]) -> bool:
        """Check if a time slot overlaps with any busy period."""
        for busy_start, busy_end in busy_periods:
            if (slot_start < busy_end) and (slot_end > busy_start):
                return False
        return True


class ConsecutiveSlotChecker:
    """Checks for consecutive time slot conflicts."""
    
    @staticmethod
    def is_slot_consecutive(new_slot_start: datetime, assigned_tasks: List[Dict]) -> bool:
        """
        Check if a new slot would be consecutive to any assigned task on the same day.
        
        Args:
            new_slot_start: Start time of the new slot
            assigned_tasks: List of already assigned tasks
            
        Returns:
            True if consecutive, False otherwise
        """
        new_slot_date = new_slot_start.date()
        
        # Find tasks assigned on the same day
        same_day_tasks = [task for task in assigned_tasks if task['date'] == str(new_slot_date)]
        
        for task in same_day_tasks:
            if ConsecutiveSlotChecker._tasks_are_consecutive(new_slot_start, task):
                return True
        
        return False
    
    @staticmethod
    def _tasks_are_consecutive(new_slot_start: datetime, existing_task: Dict) -> bool:
        """Check if two tasks are consecutive (within 30 minutes)."""
        try:
            # Parse existing task times
            task_start = datetime.fromisoformat(existing_task['madridTime']['start'].replace(' +', '+'))
            task_end = datetime.fromisoformat(existing_task['madridTime']['end'].replace(' +', '+'))
            
            # Calculate time differences
            time_diff_start = abs((new_slot_start - task_end).total_seconds() / 60)
            time_diff_end = abs((task_start - new_slot_start).total_seconds() / 60)
            
            # Consecutive if within 30 minutes
            return time_diff_start <= 30 or time_diff_end <= 30
            
        except (ValueError, KeyError):
            return False


class TimezoneConverter:
    """Handles timezone conversions between UTC and Madrid."""
    
    @staticmethod
    def utc_to_madrid(dt: datetime) -> datetime:
        """
        Convert UTC datetime to Madrid timezone.
        
        Args:
            dt: UTC datetime object (without timezone info)
            
        Returns:
            Datetime object in Madrid timezone
        """
        dt_utc = dt.replace(tzinfo=pytz.UTC)
        return dt_utc.astimezone(Config.MADRID_TIMEZONE)
    
    @staticmethod
    def madrid_to_utc(dt: datetime) -> datetime:
        """
        Convert Madrid timezone datetime to UTC.
        
        Args:
            dt: Madrid timezone datetime object
            
        Returns:
            Datetime object in UTC
        """
        return dt.astimezone(pytz.UTC)


class TaskScheduler:
    """Main scheduler class that coordinates task assignment."""
    
    def __init__(self):
        self.duration_calculator = TaskDurationCalculator()
        self.slot_generator = TimeSlotGenerator()
        self.consecutive_checker = ConsecutiveSlotChecker()
    
    def assign_tasks_to_slots(self, tasks: List[Dict], busy_slots: List[Dict]) -> List[Dict]:
        """
        Assign tasks to available time slots.
        
        Args:
            tasks: List of tasks to assign
            busy_slots: List of busy periods to avoid
            
        Returns:
            List of assigned task dictionaries
        """
        assigned = []
        
        # Sort tasks by priority and creation date
        sorted_tasks = self._sort_tasks_by_priority(tasks)
        
        # Parse busy periods once
        busy_periods = self.slot_generator._parse_busy_periods(busy_slots)
        
        # Assign tasks one by one, generating slots as needed
        for task in sorted_tasks:
            self._assign_single_task(task, busy_periods, assigned)
        
        return assigned
    
    def _assign_single_task(self, task: Dict, busy_periods: List[Tuple[datetime, datetime]], assigned: List[Dict]) -> bool:
        """Assign a single task to the next available slot."""
        meeting_duration = self.duration_calculator.calculate_meeting_duration(task)
        madrid_now = datetime.now(Config.MADRID_TIMEZONE)
        
        # Start from today and look for available slots day by day
        for day_offset in range(Config.FUTURE_DAYS_LIMIT):
            current_date = madrid_now.date() + timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            # Check if this day already has 2 tasks assigned
            tasks_today = [a for a in assigned if a['date'] == str(current_date)]
            if len(tasks_today) >= Config.MAX_TASKS_PER_DAY:
                continue
            
            # Generate slots for this specific day
            day_slots = self._generate_day_slots_for_assignment(current_date, madrid_now, busy_periods, assigned)
              # Try to assign task to any available slot in this day
            for slot in day_slots:
                # Check if slot has enough duration - if not, adjust to fit
                slot_duration = (slot['end_time'] - slot['start_time']).total_seconds() / 60
                actual_duration = min(meeting_duration, slot_duration)
                
                # Ensure minimum meeting duration
                if actual_duration < Config.MIN_MEETING_DURATION:
                    continue
                
                # Check if slot would be consecutive with existing tasks
                if self.consecutive_checker.is_slot_consecutive(slot['start_time'], assigned):
                    continue
                
                # Create assignment with adjusted duration if needed
                adjusted = actual_duration < meeting_duration
                self._create_assignment(task, slot, actual_duration, assigned, set(), adjusted)
                return True
        
        return False
    
    def _generate_day_slots_for_assignment(self, date: datetime.date, madrid_now: datetime, busy_periods: List[Tuple[datetime, datetime]], assigned: List[Dict]) -> List[Dict]:
        """Generate available slots for a specific day, avoiding busy periods and assigned tasks."""
        slots = []
        
        # Define business hours for the day
        madrid_tz = Config.MADRID_TIMEZONE
        day_start = madrid_tz.localize(
            datetime.combine(date, datetime.min.time().replace(hour=Config.BUSINESS_HOURS_START))
        )
        day_end = madrid_tz.localize(
            datetime.combine(date, datetime.min.time().replace(hour=Config.BUSINESS_HOURS_END))
        )
        
        # Adjust start time if it's today
        if date == madrid_now.date() and day_start < madrid_now:
            current_hour = madrid_now.hour
            current_minute = madrid_now.minute
            
            # Round to next half hour
            if current_minute > 0:
                current_hour += 1
            
            adjusted_hour = max(Config.BUSINESS_HOURS_START, current_hour)
            if adjusted_hour >= Config.BUSINESS_HOURS_END:
                return slots  # Too late today
                
            day_start = madrid_tz.localize(
                datetime.combine(date, datetime.min.time().replace(hour=adjusted_hour))
            )
        
        # Get assigned tasks for this day
        assigned_periods = []
        for task in assigned:
            if task['date'] == str(date):
                task_start = datetime.fromisoformat(task['madridTime']['start'].replace(' +', '+'))
                task_end = datetime.fromisoformat(task['madridTime']['end'].replace(' +', '+'))
                assigned_periods.append((task_start, task_end))
        
        # Generate 30-minute slots
        slot_start = day_start
        while slot_start < day_end:
            slot_end = slot_start + timedelta(minutes=Config.SLOT_DURATION_MINUTES)
            
            # Check if slot overlaps with busy periods
            is_available = True
            for busy_start, busy_end in busy_periods:
                if (slot_start < busy_end) and (slot_end > busy_start):
                    is_available = False
                    break
            
            # Check if slot overlaps with already assigned tasks
            if is_available:
                for assigned_start, assigned_end in assigned_periods:
                    if (slot_start < assigned_end) and (slot_end > assigned_start):
                        is_available = False
                        break
            
            if is_available:
                slots.append({
                    'start_time': slot_start,
                    'end_time': slot_end
                })
            
            slot_start = slot_end
        
        return slots
    
    def _sort_tasks_by_priority(self, tasks: List[Dict]) -> List[Dict]:
        """Sort tasks by priority and creation date."""
        return sorted(tasks, key=lambda t: (t.get('priority', 5), t.get('createdDateTime', '2099-12-31')))
    
    def _create_assignment(self, task: Dict, slot: Dict, meeting_duration: int, assigned: List[Dict], used_slots: set, adjusted: bool = False) -> None:
        """Create a task assignment and add it to the assigned list."""
        meeting_end = slot['start_time'] + timedelta(minutes=meeting_duration)
        if meeting_end > slot['end_time']:
            meeting_end = slot['end_time']
        
        # Convert to UTC for response
        start_utc = TimezoneConverter.madrid_to_utc(slot['start_time'])
        end_utc = TimezoneConverter.madrid_to_utc(meeting_end)
        
        # Format UTC strings for response
        start_utc_str = start_utc.replace(tzinfo=None).isoformat() + '.0000000'
        end_utc_str = end_utc.replace(tzinfo=None).isoformat() + '.0000000'
        
        assignment = {
            'taskName': task.get('title', 'Sin título'),
            'taskId': task.get('id', ''),
            'reservationTime': start_utc_str,
            'reservationEnd': end_utc_str,
            'calculatedDurationMinutes': meeting_duration,
            'dayOfWeek': slot['start_time'].strftime('%A'),
            'date': str(slot['start_time'].date()),
            'slotId': f"generated_{slot['start_time'].isoformat()}",
            'madridTime': {
                'start': slot['start_time'].strftime('%Y-%m-%d %H:%M:%S %z'),
                'end': meeting_end.strftime('%Y-%m-%d %H:%M:%S %z')
            }
        }
        
        if adjusted:
            assignment['adjustedDuration'] = True
        
        assigned.append(assignment)
        used_slots.add(slot['start_time'])

# Application Entry Point
if __name__ == '__main__':
    # Get port from environment variable (for Railway) or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
