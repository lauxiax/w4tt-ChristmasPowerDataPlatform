"""
🏗 API REST para Asignación Inteligente de Tareas
==================================================
API que gestiona la asignación de tareas en la agenda del usuario,
distribuyéndolas de manera inteligente en horarios laborales.
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pytz, os
from dateutil import parser

class Config:
    TZ = pytz.timezone('Europe/Madrid')
    START, END = 9, 17
    MIN_DUR, MAX_DUR, BASE_DUR = 60, 150, 90
    GAP, MAX_PER_DAY, DAYS_AHEAD = 30, 2, 30

app = Flask(__name__)

@app.route('/health-check')
def health():
    return jsonify({"status": "OK", "timestamp": datetime.now(pytz.UTC).isoformat()})

@app.route('/assign-tasks', methods=['POST'])
def assign():
    data = request.get_json()
    if not (data and isinstance(data.get('tasks'), list) and isinstance(data.get('slots'), list)):
        return jsonify({"error": "Se requieren listas 'tasks' y 'slots'"}), 400
    for i, t in enumerate(data['tasks']):
        if not (isinstance(t, dict) and all(f in t for f in ['id', 'title'])):
            return jsonify({"error": f"Tarea {i} inválida"}), 400
    for i, s in enumerate(data['slots']):
        if not (isinstance(s, dict) and all(f in s for f in ['start', 'end'])):
            return jsonify({"error": f"Slot {i} inválido"}), 400
        try: parser.parse(s['start']); parser.parse(s['end'])
        except: return jsonify({"error": f"Fecha inválida en slot {i}"}), 400
    try:
        return jsonify(Scheduler().run(data['tasks'], data['slots']))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

class TZ:
    @staticmethod
    def utc2mad(dt):
        if dt.tzinfo is None: dt = dt.replace(tzinfo=pytz.UTC)
        elif dt.tzinfo != pytz.UTC: dt = dt.astimezone(pytz.UTC)
        return dt.astimezone(Config.TZ)
    @staticmethod
    def mad2utc(dt):
        if dt.tzinfo is None: dt = Config.TZ.localize(dt)
        elif dt.tzinfo != Config.TZ: dt = dt.astimezone(Config.TZ)
        return dt.astimezone(pytz.UTC)
    @staticmethod
    def parse(dt, tz=pytz.UTC):
        d = parser.parse(dt)
        return d if d.tzinfo else d.replace(tzinfo=tz)

class Analyzer:
    @staticmethod
    def dur(t):
        d = Config.BASE_DUR
        if t.get('priority',2)==1: d+=60
        elif t.get('priority',2)==3: d+=30
        if t.get('percentComplete',0)<20: d+=30
        if t.get('checklistItemCount',0)>5: d+=30
        if t.get('hasDescription',False): d+=30
        return min(max(d, Config.MIN_DUR), Config.MAX_DUR)
    @staticmethod
    def score(t, now=None):
        now = now or datetime.now(pytz.UTC)
        s = 100*(5-min(t.get('priority',5),5))/5
        if 'dueDateTime' in t:
            try:
                d = TZ.parse(t['dueDateTime'])
                days = (d-now).total_seconds()/86400
                s += 80 if days<=0 else 70 if days<=1 else 60 if days<=3 else 50 if days<=7 else 30 if days<=14 else 10
            except: pass
        if 'createdDateTime' in t:
            try:
                d = (now-TZ.parse(t['createdDateTime'])).total_seconds()/86400
                s += 30 if d>30 else 20 if d>14 else 15 if d>7 else 10 if d>3 else 0
            except: pass
        s += 20*(100-t.get('percentComplete',0))/100
        return s

class Slots:
    def __init__(self): self.tz = Config.TZ
    def available(self, busy, assigned, now, days=Config.DAYS_AHEAD):
        slots, d0 = [], now.date()
        for o in range(days):
            d = d0+timedelta(days=o)
            if d.weekday()>=5 or sum(1 for s,_ in assigned if s.date()==d)>=Config.MAX_PER_DAY: continue
            slots += self._day(d, now, busy, assigned)
            if len(slots)>=10: break
        return slots
    def _day(self, day, now, busy, assigned):
        slots=[]
        start = self.tz.localize(datetime.combine(day, datetime.min.time().replace(hour=Config.START)))
        end = self.tz.localize(datetime.combine(day, datetime.min.time().replace(hour=Config.END)))
        if day==now.date() and start<now:
            h=now.hour+1
            if h>=Config.END: return slots
            start = self.tz.localize(datetime.combine(day, datetime.min.time().replace(hour=h)))
        t=start
        while t<end:
            t2 = min(t+timedelta(minutes=60), end)
            if self._free(t, t2, busy, assigned):
                slots.append({"start": t, "end": t2, "duration_minutes": int((t2-t).total_seconds()/60)})
            t += timedelta(minutes=60)
        return slots
    def _free(self, start, end, busy, assigned):
        for b0,b1 in busy:
            if start<b1 and end>b0: return False
        for a0,a1 in assigned:
            if start<a1 and end>a0: return False
            g=Config.GAP
            if end<=a0 and (a0-end).total_seconds()/60<g: return False
            if start>=a1 and (start-a1).total_seconds()/60<g: return False
        return True

class Scheduler:
    def __init__(self):
        self.slots, self.an = Slots(), Analyzer()
        self.now = datetime.now(Config.TZ)
    def run(self, tasks, busy_slots):
        busy = self._busy(busy_slots)
        assigned, periods = [], []
        for t in sorted(tasks, key=lambda t: self.an.score(t, self.now), reverse=True):
            if t.get('percentComplete', 0) >= 100:
                continue  # No asignar tareas ya completas
            a = self._assign(t, busy, periods)
            if a:
                assigned.append(a)
                s = TZ.parse(a['madridTime']['start'])
                e = TZ.parse(a['madridTime']['end'])
                periods.append((s,e))
        return assigned
    def _busy(self, busy_slots):
        res=[]
        for s in busy_slots:
            try:
                st=TZ.utc2mad(TZ.parse(s['start']))
                en=TZ.utc2mad(TZ.parse(s['end']))
                res.append((st,en))
            except: continue
        return res
    def _assign(self, task, busy, assigned):
        dur = self.an.dur(task)
        slots = self.slots.available(busy, assigned, self.now)
        if not slots: return None
        slot = next((s for s in slots if s['duration_minutes']>=dur), None)
        if not slot and slots:
            slot = max(slots, key=lambda s: s['duration_minutes'])
            if slot['duration_minutes']<Config.MIN_DUR: return None
            dur = min(dur, slot['duration_minutes'])
        if not slot: return None
        start, end = slot['start'], slot['start']+timedelta(minutes=dur)
        if end>slot['end']:
            end = slot['end']
            dur = int((end-start).total_seconds()/60)
        return self._fmt(task, start, end, dur)
    def _fmt(self, task, start_mad, end_mad, dur):
        start_utc = TZ.mad2utc(start_mad)
        end_utc = TZ.mad2utc(end_mad)
        calc_dur = self.an.dur(task)
        adj = dur != calc_dur
        return {
            "taskName": task.get('title','Sin título'),
            "taskId": task.get('id',''),
            "reservationTime": start_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "reservationEnd": end_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "calculatedDurationMinutes": dur,
            "dayOfWeek": start_mad.strftime("%A"),
            "date": start_mad.strftime("%Y-%m-%d"),
            "slotId": f"generated_{start_mad.isoformat()}",
            "madridTime": {"start": start_mad.strftime("%Y-%m-%d %H:%M:%S %z"), "end": end_mad.strftime("%Y-%m-%d %H:%M:%S %z")},
            **({"adjustedDuration": True} if adj else {})
        }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)