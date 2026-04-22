#!/usr/bin/env python3
"""
Real-time cycle monitoring across all services
"""
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

def get_container_logs(container_name, lines=1):
    """Get last N lines from container"""
    try:
        result = subprocess.run(
            ['docker', 'compose', 'logs', container_name, f'--tail={lines}'],
            capture_output=True,
            text=True,
            cwd='./TruthFirst-Genesis/TENETAiAGENCY'
        )
        return result.stdout.split('\n')[-2] if result.stdout else ""
    except:
        return ""

def extract_cycle(log_line):
    """Extract cycle number from log"""
    if 'Cycle' in log_line:
        parts = log_line.split('Cycle')
        if len(parts) > 1:
            num = ''.join(c for c in parts[1].split(':')[0] if c.isdigit())
            return int(num) if num else 0
    return 0

def extract_k_value(log_line):
    """Extract K-value from log"""
    if 'K=' in log_line:
        try:
            k_str = log_line.split('K=')[1].split()[0]
            return float(k_str)
        except:
            return 0.0
    return 0.0

def monitor_cycles():
    """Monitor cycles in real-time"""
    
    # Satellite containers
    satellites = ['satellite-bom', 'satellite-himawari', 'satellite-goes', 'satellite-meteosat']
    
    # Witness nodes
    witnesses = ['witness-node-1', 'witness-node-2', 'witness-node-3']
    
    # Core engines
    core_engines = ['engine-365', 'engine-777', 'engine-101']
    
    # Peer engines
    peer_engines = [f'engine-{i:02d}' for i in range(4, 15)]
    
    # Aggregator
    aggregator = ['grid-aggregator']
    
    print("\n" + "="*100)
    print("TENET GLOBAL ATMOSPHERIC TRUTH SYSTEM - CYCLE MONITOR")
    print("="*100)
    
    while True:
        print(f"\n[{datetime.utcnow().isoformat()}]\n")
        
        # Satellite cycles
        print("SATELLITE INGESTION (Sub-frame Decomposition):")
        print("-" * 100)
        sat_cycles = []
        for sat in satellites:
            log = get_container_logs(sat, 1)
            cycle = extract_cycle(log)
            sat_cycles.append(cycle)
            status = "✓" if cycle > 0 else "✗"
            print(f"  {status} {sat:20} | Cycle {cycle:7} | {log.strip()[:70]}")
        print()
        
        # Witness cycles
        print("XYO BOUND-WITNESS MESH (Ledger Anchoring):")
        print("-" * 100)
        wit_cycles = []
        for wit in witnesses:
            log = get_container_logs(wit, 1)
            cycle = extract_cycle(log)
            wit_cycles.append(cycle)
            status = "✓" if cycle > 0 else "✗"
            print(f"  {status} {wit:20} | Cycle {cycle:7} | {log.strip()[:70]}")
        print()
        
        # Core engines
        print("BYZANTINE CONSENSUS - CORE RING (E01-E03):")
        print("-" * 100)
        core_k_values = []
        for engine in core_engines:
            log = get_container_logs(engine, 1)
            cycle = extract_cycle(log)
            k_val = extract_k_value(log)
            core_k_values.append(k_val)
            gate = "EXECUTE" if k_val >= 0.99 else "QUEUE"
            status = "✓" if k_val >= 0.99 else "▲"
            print(f"  {status} {engine:20} | Cycle {cycle:7} | K={k_val:.4f} | Gate={gate:7} | {log.strip()[:40]}")
        print()
        
        # Peer engines (sample every 3rd)
        print("BYZANTINE CONSENSUS - PEER RING (E04-E14, sampling):")
        print("-" * 100)
        peer_k_values = []
        for i, engine in enumerate(peer_engines):
            if i % 3 == 0:  # Sample every 3rd
                log = get_container_logs(engine, 1)
                cycle = extract_cycle(log)
                k_val = extract_k_value(log)
                peer_k_values.append(k_val)
                status = "✓" if k_val >= 0.99 else "▲"
                print(f"  {status} {engine:20} | Cycle {cycle:7} | K={k_val:.4f}")
        print()
        
        # Grid aggregator
        print("GRID AGGREGATION & VERIFICATION:")
        print("-" * 100)
        log = get_container_logs(aggregator[0], 1)
        cycle = extract_cycle(log)
        print(f"  ✓ {aggregator[0]:20} | Cycle {cycle:7} | {log.strip()[:70]}")
        print()
        
        # Summary
        print("CONSENSUS SUMMARY:")
        print("-" * 100)
        all_k = core_k_values + peer_k_values
        if all_k:
            avg_k = sum(all_k) / len(all_k)
            consensus_status = "ACHIEVED" if avg_k >= 0.99 else f"CONVERGING ({avg_k:.4f})"
            print(f"  Average K-value: {avg_k:.4f}")
            print(f"  Consensus Status: {consensus_status}")
            print(f"  Byzantine Quorum: 10/14 required for EXECUTE")
            print(f"  Current Engines at K≥0.99: {sum(1 for k in all_k if k >= 0.99)}/14")
        
        print("\n" + "="*100)
        print("Press Ctrl+C to stop. Updates every 5 seconds.\n")
        
        time.sleep(5)

if __name__ == '__main__':
    try:
        monitor_cycles()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
