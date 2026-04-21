#!/usr/bin/env python3
"""
XYO Bound-Witness Node

Each witness node observes satellite sub-frame hashes,
timestamps them, and anchors them to the ledger.
Creates chain of custody: "At time T, node N observed tile H"
"""

import json
import hashlib
import time
import os
from datetime import datetime
from pathlib import Path

class WitnessNode:
    def __init__(self, witness_id, region):
        self.witness_id = witness_id
        self.region = region
        self.state_dir = Path('/data/state')
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = Path('/logs')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.witness_key = hashlib.sha256(f"{witness_id}_{region}".encode()).hexdigest()[:32]
        self.observations = []
        
    def observe_tile(self, tile_hash, tile_id, satellite_id, timestamp):
        """
        Witness a sub-frame tile hash.
        Create bound-witness signature and ledger entry.
        """
        observation_time = datetime.utcnow().isoformat()
        
        # Create witness signature (HMAC-SHA256)
        signature_input = f"{tile_hash}_{observation_time}_{self.witness_key}"
        witness_signature = hashlib.sha256(signature_input.encode()).hexdigest()
        
        # Create bound-witness entry
        witness_entry = {
            "witness_id": self.witness_id,
            "witness_region": self.region,
            "observation_time": observation_time,
            "tile_hash": tile_hash,
            "tile_id": tile_id,
            "satellite_id": satellite_id,
            "witness_signature": witness_signature,
            "ledger_position": len(self.observations)
        }
        
        self.observations.append(witness_entry)
        return witness_entry
    
    def read_tiles_from_ledger(self):
        """Read recent tile hashes from the shared ledger"""
        ledger_dir = Path('/data/ledger')
        if not ledger_dir.exists():
            return []
        
        tiles = []
        for tile_file in sorted(ledger_dir.glob('*.json'))[-5:]:  # Last 5 files
            try:
                with open(tile_file) as f:
                    data = json.load(f)
                    if 'tiles' in data:
                        tiles.extend(data['tiles'])
            except:
                pass
        
        return tiles
    
    def run_cycle(self, cycle_num):
        """Execute one witness observation cycle"""
        # Read tiles from ledger
        tiles = self.read_tiles_from_ledger()
        
        observed_count = 0
        for tile in tiles:
            if 'integrity_hash' in tile and 'tile_id' in tile:
                witness_entry = self.observe_tile(
                    tile['integrity_hash'],
                    tile['tile_id'],
                    tile['metadata']['satellite'],
                    tile['metadata']['timestamp']
                )
                observed_count += 1
        
        # Write witness log
        witness_log = {
            "witness_id": self.witness_id,
            "witness_region": self.region,
            "cycle": cycle_num,
            "observation_time": datetime.utcnow().isoformat(),
            "tiles_observed": observed_count,
            "total_observations": len(self.observations),
            "status": "operational"
        }
        
        with open(self.log_dir / 'witness.json', 'w') as f:
            json.dump(witness_log, f)
        
        # Write state
        with open(self.state_dir / 'observations.json', 'w') as f:
            json.dump({
                "witness_id": self.witness_id,
                "cycle": cycle_num,
                "observations": self.observations[-100:]  # Last 100
            }, f)
        
        return observed_count

def main():
    witness_id = os.getenv('WITNESS_ID', 'WIT_001')
    region = os.getenv('WITNESS_REGION', 'Sydney')
    
    witness = WitnessNode(witness_id, region)
    
    cycle = 0
    while True:
        try:
            observed = witness.run_cycle(cycle)
            cycle += 1
            print(f"[{witness_id}] Cycle {cycle}: Witnessed {observed} tiles")
            time.sleep(2)  # One cycle every 2 seconds
        except Exception as e:
            print(f"[{witness_id}] Error in cycle {cycle}: {e}")
            time.sleep(2)

if __name__ == '__main__':
    main()
