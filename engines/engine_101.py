#!/usr/bin/env python3
"""Engine 101: Flow Vector"""
import json, time
from datetime import datetime
from pathlib import Path

state_dir = Path('/data/state')
log_dir = Path('/logs')
state_dir.mkdir(parents=True, exist_ok=True)
log_dir.mkdir(parents=True, exist_ok=True)

x_state = {"latitude": 10, "longitude": 30, "pressure": 1008, "temperature": 16, "humidity": 0.62}
x_ref = {"latitude": 0, "longitude": 0, "pressure": 1013, "temperature": 15, "humidity": 0.65}
cycle = 0

while True:
    try:
        cycle += 1
        for key in x_ref:
            diff = x_state[key] - x_ref[key]
            x_state[key] -= 0.1 * diff * 0.01
        distance = sum((x_state[k] - x_ref[k])**2 for k in x_ref) ** 0.5
        k = 1.0 / (1.0 + distance)
        
        with open(log_dir / 'metrics.json', 'w') as f:
            json.dump({
                "timestamp": datetime.utcnow().isoformat(),
                "cycle": cycle,
                "engine_id": "E03",
                "k_value": k,
                "status": "operational"
            }, f)
        
        with open(state_dir / 'engine_state.json', 'w') as f:
            json.dump({"engine_id": "E03", "cycle": cycle, "state": x_state, "k": k}, f)
        
        print(f"[E03] Cycle {cycle}: K={k:.4f}")
        time.sleep(0.5)
    except Exception as e:
        print(f"[E03] Error: {e}")
        time.sleep(0.5)
