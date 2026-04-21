#!/usr/bin/env python3
"""Grid Aggregator: Constructs witnessed atmospheric grid"""
import json, time
from datetime import datetime
from pathlib import Path

state_dir = Path('/data/state')
log_dir = Path('/logs')
grid_cache = Path('/data/grid')
state_dir.mkdir(parents=True, exist_ok=True)
log_dir.mkdir(parents=True, exist_ok=True)
grid_cache.mkdir(parents=True, exist_ok=True)

cycle = 0
while True:
    try:
        cycle += 1
        
        # Read all 14 engine states
        engines = [f'e{i:02d}' for i in range(1, 15)]
        k_values = []
        
        # Simulate reading engine states (in real system, read from volumes)
        for i in range(14):
            k_values.append(0.5 + i * 0.035)  # Gradually approach 0.99
        
        avg_k = sum(k_values) / len(k_values)
        consensus = "ACHIEVED" if avg_k >= 0.99 else "CONVERGING"
        
        grid_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle": cycle,
            "engines_active": 14,
            "k_values": {f"E{i:02d}": k for i, k in enumerate(k_values, 1)},
            "average_k": avg_k,
            "consensus_status": consensus,
            "witnessed_tiles": 0,
            "grid_coverage": 0.0
        }
        
        with open(log_dir / 'grid_status.json', 'w') as f:
            json.dump(grid_status, f, indent=2)
        
        print(f"[GRID] Cycle {cycle}: K_avg={avg_k:.4f} Status={consensus}")
        time.sleep(1)
    except Exception as e:
        print(f"[GRID] Error: {e}")
        time.sleep(1)
