#!/usr/bin/env python3
"""
Debug script específico para el solapamiento
"""
import sys
sys.path.append('.')

from datetime import datetime, timedelta
import pytz

MADRID_TIMEZONE = pytz.timezone('Europe/Madrid')

def debug_overlap():
    print("=== DEBUG: Lógica de Solapamiento ===\n")
    
    # Slot disponible: 13:00-13:30 Madrid
    slot_start = MADRID_TIMEZONE.localize(datetime(2025, 6, 2, 13, 0))
    slot_end = MADRID_TIMEZONE.localize(datetime(2025, 6, 2, 13, 30))
    
    # Período ocupado: 13:00-14:00 Madrid (desde UTC 13:00-14:00)
    busy_start_utc = datetime(2025, 6, 2, 13, 0)  # 13:00 UTC
    busy_end_utc = datetime(2025, 6, 2, 14, 0)    # 14:00 UTC
    
    # Convertir busy a Madrid
    def convert_utc_to_madrid(dt):
        dt_utc = dt.replace(tzinfo=pytz.UTC)
        return dt_utc.astimezone(MADRID_TIMEZONE)
    
    busy_start = convert_utc_to_madrid(busy_start_utc)
    busy_end = convert_utc_to_madrid(busy_end_utc)
    
    print(f"Slot disponible: {slot_start} - {slot_end}")
    print(f"Período ocupado (UTC): {busy_start_utc} - {busy_end_utc}")
    print(f"Período ocupado (Madrid): {busy_start} - {busy_end}")
    
    # Verificar solapamiento usando la lógica actual
    overlaps = (slot_start < busy_end) and (slot_end > busy_start)
    print(f"\n¿Solapan? {overlaps}")
    print(f"Condición 1 (slot_start < busy_end): {slot_start} < {busy_end} = {slot_start < busy_end}")
    print(f"Condición 2 (slot_end > busy_start): {slot_end} > {busy_start} = {slot_end > busy_start}")
    
    # En verano, UTC+2, deberían ser:
    # busy_start_madrid = 15:00 Madrid (13:00 UTC + 2 horas)
    # busy_end_madrid = 16:00 Madrid (14:00 UTC + 2 horas)
    
    print(f"\n¿Es verano ahora? {datetime.now().month in [6,7,8,9]}")
    print(f"Offset actual Madrid: {busy_start.strftime('%z')}")

if __name__ == "__main__":
    debug_overlap()
