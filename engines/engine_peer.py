#!/usr/bin/env python3
"""Peer Validator Engines (E04-E14)"""
import json, time, os, math
from datetime import datetime
from pathlib import Path

engine_id = os.getenv('ENGINE_ID', 'E04')
state_dir = Path('/data/state')
log_dir = Path('/logs')
state_dir.mkdir(parents=True, exist_ok=True)
log_dir.mkdir(parents=True, exist_ok=True)

# Phase space with slight variation per engine
x_state = {
    "latitude": 20 + hash(engine_id) % 20,
    "longitude": 40 + hash(engine_id) % 20,
    "pressure": 1000 + hash(engine_id) % 30,
    "temperature": 10 + hash(engine_id) % 20,
    "humidity": 0.5 + (hash(engine_id) % 50) / 100
}

x_ref = {"latitude": 0, "longitude": 0, "pressure": 1013, "temperature": 15, "humidity": 0.65}
lambda_convergence = 0.1
cycle = 0

while True:
    try:
        cycle += 1
        
        # Converge
        for key in x_ref:
            diff = x_state[key] - x_ref[key]
            x_state[key] -= lambda_convergence * diff * 0.01
        
        # K-value
        distance = sum((x_state[k] - x_ref[k])**2 for k in x_ref) ** 0.5
        k = 1.0 / (1.0 + distance)
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle": cycle,
            "engine_id": engine_id,
            "k_value": k,
            "status": "operational"
        }
        
        with open(log_dir / 'metrics.json', 'w') as f:
            json.dump(metrics, f)
        
        with open(state_dir / 'engine_state.json', 'w') as f:
            json.dump({"engine_id": engine_id, "cycle": cycle, "state": x_state, "k": k}, f)
        
        print(f"[{engine_id}] Cycle {cycle}: K={k:.4f}")
        time.sleep(0.5)
    except Exception as e:
        print(f"[{engine_id}] Error: {e}")
        time.sleep(0.5)
