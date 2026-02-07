#!/usr/bin/env python3
"""
Dive Claims Ledger Simple - Standalone Claims Ledger

Simplified version for easy import and use.
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Claim:
    """A claim in the ledger"""
    claim_id: str
    timestamp: float
    operation: str
    inputs: Dict
    outputs: Optional[Dict] = None
    hash: Optional[str] = None


class DiveClaimsLedgerSimple:
    """
    Simplified Claims Ledger for audit trail.
    
    Records all operations for 100% reproducibility.
    """
    
    def __init__(self, storage_dir: str = "/tmp/dive_claims"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.claims: List[Claim] = []
        self.stats = {
            'total_claims': 0,
            'operations': {}
        }
    
    def create_claim(
        self,
        operation: str,
        inputs: Dict,
        outputs: Optional[Dict] = None
    ) -> Claim:
        """Create a new claim"""
        
        claim_id = f"claim_{int(time.time()*1000)}"
        timestamp = time.time()
        
        # Create claim
        claim = Claim(
            claim_id=claim_id,
            timestamp=timestamp,
            operation=operation,
            inputs=inputs,
            outputs=outputs
        )
        
        # Calculate hash
        claim_data = json.dumps(asdict(claim), sort_keys=True)
        claim.hash = hashlib.sha256(claim_data.encode()).hexdigest()
        
        # Store claim
        self.claims.append(claim)
        self._save_claim(claim)
        
        # Update stats
        self.stats['total_claims'] += 1
        self.stats['operations'][operation] = self.stats['operations'].get(operation, 0) + 1
        
        return claim
    
    def _save_claim(self, claim: Claim):
        """Save claim to disk"""
        claim_file = self.storage_dir / f"{claim.claim_id}.json"
        with open(claim_file, 'w') as f:
            json.dump(asdict(claim), f, indent=2)
    
    def query_claims(
        self,
        operation: Optional[str] = None,
        limit: int = 100
    ) -> List[Claim]:
        """Query claims"""
        
        filtered = self.claims
        
        if operation:
            filtered = [c for c in filtered if c.operation == operation]
        
        return filtered[-limit:]
    
    def export_audit_trail(self, output_file: str):
        """Export complete audit trail"""
        
        audit_data = {
            'exported_at': time.time(),
            'total_claims': len(self.claims),
            'claims': [asdict(c) for c in self.claims]
        }
        
        with open(output_file, 'w') as f:
            json.dump(audit_data, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get ledger statistics"""
        return self.stats.copy()


def main():
    """Test claims ledger"""
    print("=== Dive Claims Ledger Simple Test ===\n")
    
    ledger = DiveClaimsLedgerSimple()
    
    # Create test claims
    claim1 = ledger.create_claim(
        operation="generate_code",
        inputs={'spec': 'Create REST API'},
        outputs={'code': 'def api(): pass'}
    )
    print(f"Created claim: {claim1.claim_id}")
    print(f"  Hash: {claim1.hash[:16]}...")
    
    claim2 = ledger.create_claim(
        operation="analyze_complexity",
        inputs={'task': 'Design system'},
        outputs={'complexity': 'high'}
    )
    print(f"Created claim: {claim2.claim_id}")
    print(f"  Hash: {claim2.hash[:16]}...")
    
    # Query claims
    print(f"\nTotal claims: {len(ledger.claims)}")
    print(f"Stats: {ledger.get_stats()}")
    
    # Export audit trail
    ledger.export_audit_trail("/tmp/audit_trail.json")
    print(f"\nAudit trail exported to /tmp/audit_trail.json")


if __name__ == "__main__":
    main()
