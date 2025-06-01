#!/usr/bin/env python3
"""
Debug script para entender por qué no se generan asignaciones
"""
import sys
sys.path.append('.')

from app import generate_available_time_slots, convert_utc_to_madrid, MADRID_TIMEZONE
from datetime import datetime, timedelta
import pytz

def debug_slot_generation():
    print("=== DEBUG: Generación de Slots ===\n")
    
    # Simular busy_slots de prueba
    tomorrow = datetime.now().date() + timedelta(days=1)
    busy_slots = [
        {
            'id': 'busy1',
            'start': f'{tomorrow}T13:00:00.0000000',  # 14:00 Madrid = 13:00 UTC en invierno
            'end': f'{tomorrow}T14:00:00.0000000',    # 15:00 Madrid = 14:00 UTC en invierno
            'showAs': 'busy',
            'subject': 'Team meeting'
        }
    ]
    
    print(f"1. Busy slots recibidos: {len(busy_slots)}")
    for slot in busy_slots:
        print(f"   - {slot['start']} a {slot['end']}")
    
    print(f"\n2. Generando slots disponibles...")
    available_slots = generate_available_time_slots(busy_slots, days_ahead=3)
    
    print(f"   Total slots disponibles generados: {len(available_slots)}")
    
    if available_slots:
        print("\n3. Primeros 10 slots disponibles:")
        for i, slot in enumerate(available_slots[:10]):
            print(f"   {i+1}. {slot['start_time'].strftime('%Y-%m-%d %H:%M')} - {slot['end_time'].strftime('%H:%M')} Madrid")
    else:
        print("   ❌ No se generaron slots disponibles!")
        
        # Debug adicional
        madrid_now = datetime.now(MADRID_TIMEZONE)
        print(f"\n   Debug info:")
        print(f"   - Hora actual Madrid: {madrid_now}")
        print(f"   - Fecha inicio: {madrid_now.date()}")
        print(f"   - Es día laborable: {madrid_now.weekday() < 5}")

if __name__ == "__main__":
    debug_slot_generation()
