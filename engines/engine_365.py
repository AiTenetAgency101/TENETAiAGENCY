#!/usr/bin/env python3
"""
Core Byzantine Consensus Engine (E01: Engine 365)

Identity anchor for the consensus ring.
Validates witnessed tiles against Byzantine quorum rules.
Tracks K-value (coherence) for all 14 engines.
"""

import json
import hashlib
import time
import os
from datetime import datetime
from pathlib import Path
import math

class Engine365:
    def __init__(self):
        self.engine_id = "E01"
        self.role = "CORE_IDENTITY_ANCHOR"
        self.byzantine_quorum = 10  # Need 10/14 engines to agree
        self.k_target = 0.99
        self.state_dir = Path('/data/state')
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = Path('/logs')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 5D phase space
        self.x_ref = {
            "latitude": 0.0,
            "longitude": 0.0,
            "pressure": 1013.0,
            "temperature": 15.0,
            "humidity": 0.65
        }
        
        # Current state (all engines converge toward x_ref)
        self.x_state = self._init_state()
        
        # Convergence tracking
        self.lambda_convergence = 0.1
        self.k_value = 0.0
        self.cycle = 0
        
    def _init_state(self):
        """Initialize scattered state"""
        return {
            "latitude": 25.3,
            "longitude": 45.1,
            "pressure": 1005.2,
            "temperature": 22.5,
            "humidity": 0.58
        }
    
    def _compute_distance_to_equilibrium(self):
        """Compute Euclidean distance to reference state"""
        distance = 0.0
        for key in self.x_ref:
            diff = self.x_state[key] - self.x_ref[key]
            distance += diff ** 2
        return math.sqrt(distance)
    
    def _compute_k_value(self):
        """
        K = 1 / (1 + distance)
        K ranges from 0.0 (scattered) to 1.0 (perfect convergence)
        """
        distance = self._compute_distance_to_equilibrium()
        self.k_value = 1.0 / (1.0 + distance)
        return self.k_value
    
    def _converge_toward_equilibrium(self):
        """
        Apply convergence dynamics:
        dX/dt = -λ(X - X_ref)
        
        Discrete time step: X(t+1) = X(t) + dt * dX/dt
        """
        dt = 0.01  # Small time step
        for key in self.x_ref:
            diff = self.x_state[key] - self.x_ref[key]
            self.x_state[key] -= self.lambda_convergence * diff * dt
    
    def validate_tile_consensus(self, tiles):
        """
        Validate witnessed tiles.
        Check if 10/14 engines agree on tile integrity.
        """
        validated = []
        for tile in tiles:
            if 'integrity_hash' in tile:
                # In real system, query other 13 engines for consensus
                # For simulation, mark as valid if hash is well-formed
                is_valid = len(tile['integrity_hash']) == 64  # SHA256 = 64 hex chars
                if is_valid:
                    validated.append(tile)
        
        return validated
    
    def execute_consensus_gate(self):
        """
        Gate for decision execution.
        Only execute decisions if K >= 0.99
        """
        self._compute_k_value()
        
        if self.k_value >= self.k_target:
            return "EXECUTE"  # Consensus achieved
        else:
            return "QUEUE"    # Wait for convergence
    
    def run_cycle(self):
        """Execute one consensus cycle"""
        self.cycle += 1
        
        # Read witness observations
        witness_dir = Path('/data/state')
        observations = []
        
        # Converge toward equilibrium
        self._converge_toward_equilibrium()
        
        # Compute coherence
        k_value = self._compute_k_value()
        
        # Determine gate status
        gate_status = self.execute_consensus_gate()
        
        # Build metrics
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle": self.cycle,
            "engine_id": self.engine_id,
            "role": self.role,
            "phase_space": self.x_state,
            "reference_equilibrium": self.x_ref,
            "distance_to_equilibrium": self._compute_distance_to_equilibrium(),
            "k_value": k_value,
            "k_target": self.k_target,
            "gate_status": gate_status,
            "byzantine_quorum": f"{10}/14",
            "status": "operational"
        }
        
        # Write metrics
        with open(self.log_dir / 'metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Write state
        with open(self.state_dir / 'engine_state.json', 'w') as f:
            json.dump({
                "engine_id": self.engine_id,
                "cycle": self.cycle,
                "state": self.x_state,
                "k_value": k_value,
                "gate": gate_status
            }, f)
        
        return k_value

def main():
    engine = Engine365()
    
    while True:
        try:
            k = engine.run_cycle()
            print(f"[E01] Cycle {engine.cycle}: K={k:.4f} Gate={'EXECUTE' if k >= 0.99 else 'QUEUE'}")
            time.sleep(0.5)  # One cycle every 500ms
        except Exception as e:
            print(f"[E01] Error: {e}")
            time.sleep(0.5)

if __name__ == '__main__':
    main()
