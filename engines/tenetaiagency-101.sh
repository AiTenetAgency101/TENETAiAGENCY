#!/bin/bash

# tenetaiagency-101 simulator
python -u << 'EOF'
import json
import time
import os
from datetime import datetime, timedelta

os.makedirs('/logs', exist_ok=True)

start_time = time.time()
ticks = 0

# Initialize audit log
audit_start = datetime(2026, 4, 7, 9, 35, 18)

while True:
    uptime = time.time() - start_time
    ticks += 1
    decisions_executed = 0
    decisions_rejected = ticks
    
    metrics = {
        "ticks": ticks,
        "decisions_executed": decisions_executed,
        "decisions_rejected": decisions_rejected,
        "rejection_rate": 1.0,
        "drift_ratio": ticks / 2.0,
        "horizon_entries": ticks / 2.0,
        "audit_log_length": 0,
        "uptime_seconds": uptime,
        "uptime_days": uptime / 86400,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    with open('/logs/metrics.json', 'w') as f:
        json.dump(metrics, f)
    
    # Write heartbeat log every 3600 ticks
    if ticks % 3600 == 0:
        heartbeat_time = audit_start + timedelta(seconds=ticks)
        log_entry = f"[{heartbeat_time.isoformat()}] HEARTBEAT cycle {ticks}\n"
        with open('/logs/audit.log', 'a') as f:
            f.write(log_entry)
    
    time.sleep(0.05)
EOF
