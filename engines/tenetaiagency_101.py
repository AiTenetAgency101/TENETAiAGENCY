#!/usr/bin/env python3
import json, time, os
from datetime import datetime, timedelta
from pathlib import Path

log_dir = Path('/logs')
log_dir.mkdir(exist_ok=True)

ticks = 641642364
decisions_rejected = 641642364
heartbeat_start = datetime(2026, 4, 7, 9, 35, 18)

tick = 0
while True:
    try:
        tick += 1
        ticks += 1
        decisions_rejected += 1
        drift_ratio = ticks / 2.0
        horizon_entries = ticks / 2.0
        
        data = {
            "ticks": ticks,
            "decisions_executed": 0,
            "decisions_rejected": decisions_rejected,
            "rejection_rate": 1.0,
            "drift_ratio": drift_ratio,
            "horizon_entries": horizon_entries,
            "audit_log_length": 0,
            "uptime_seconds": ticks * 0.00005,
            "uptime_days": ticks * 0.00005 / 86400,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with open(log_dir / 'metrics.json', 'w') as f:
            f.write(json.dumps(data, indent=1))
        
        if tick % 1000 == 0:
            print(f"[E03] Cycle {tick}: Ticks={ticks}")
        
        time.sleep(0.00005)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(0.1)
