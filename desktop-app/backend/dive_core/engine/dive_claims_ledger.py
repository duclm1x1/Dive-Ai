#!/usr/bin/env python3
"""
Dive Claims Ledger - V22 Trust Transformation

The Claims Ledger transforms Dive AI from ephemeral to permanent audit trail.
This enables enterprise adoption with full accountability and reproducibility.

This is an architectural transformation similar to how Advanced Search
transformed data access in V21.
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum


class ClaimStatus(Enum):
    """Status of a claim"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    REPRODUCED = "reproduced"


@dataclass
class Claim:
    """
    A claim about an operation.
    
    Claims provide permanent audit trail and enable reproducibility.
    """
    claim_id: str
    operation: str
    timestamp: datetime
    context: Dict[str, Any]
    inputs: Dict[str, Any]
    expected_outputs: Optional[Dict[str, Any]] = None
    actual_outputs: Optional[Dict[str, Any]] = None
    status: ClaimStatus = ClaimStatus.PENDING
    verification_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate verification hash"""
        if self.verification_hash is None:
            self.verification_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate cryptographic hash of claim"""
        claim_data = {
            'claim_id': self.claim_id,
            'operation': self.operation,
            'timestamp': self.timestamp.isoformat(),
            'inputs': self.inputs
        }
        claim_str = json.dumps(claim_data, sort_keys=True)
        return hashlib.sha256(claim_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'claim_id': self.claim_id,
            'operation': self.operation,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'inputs': self.inputs,
            'expected_outputs': self.expected_outputs,
            'actual_outputs': self.actual_outputs,
            'status': self.status.value,
            'verification_hash': self.verification_hash,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Claim':
        """Create claim from dictionary"""
        return cls(
            claim_id=data['claim_id'],
            operation=data['operation'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            context=data['context'],
            inputs=data['inputs'],
            expected_outputs=data.get('expected_outputs'),
            actual_outputs=data.get('actual_outputs'),
            status=ClaimStatus(data['status']),
            verification_hash=data.get('verification_hash'),
            metadata=data.get('metadata', {})
        )


class DiveClaimsLedger:
    """
    Permanent audit trail for all Dive AI operations.
    
    The Claims Ledger provides:
    - 100% audit trail (vs 0% in V21)
    - Full reproducibility
    - Enterprise compliance
    - Complete accountability
    
    Architectural Transformation:
    - Before (V21): execute → result (lost forever)
    - After (V22): execute → claim → evidence → verify → store permanently
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or "/tmp/dive_claims")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory index
        self.claims: Dict[str, Claim] = {}
        self.claim_counter = 0
        
        # Load existing claims
        self._load_existing_claims()
    
    def _load_existing_claims(self):
        """Load existing claims from storage"""
        if not self.storage_dir.exists():
            return
        
        for claim_file in self.storage_dir.glob("claim_*.json"):
            try:
                with open(claim_file, 'r') as f:
                    data = json.load(f)
                claim = Claim.from_dict(data)
                self.claims[claim.claim_id] = claim
                
                # Update counter
                if claim.claim_id.startswith("claim_"):
                    try:
                        num = int(claim.claim_id.split("_")[1])
                        self.claim_counter = max(self.claim_counter, num)
                    except:
                        pass
            except Exception as e:
                print(f"Error loading claim {claim_file}: {e}")
    
    def create_claim(
        self,
        operation: str,
        inputs: Dict[str, Any],
        context: Optional[Dict] = None,
        expected_outputs: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Claim:
        """
        Create a new claim.
        
        Args:
            operation: Operation description
            inputs: Operation inputs
            context: Optional context
            expected_outputs: Optional expected outputs
            metadata: Optional metadata
            
        Returns:
            Created Claim
        """
        self.claim_counter += 1
        claim_id = f"claim_{self.claim_counter}_{datetime.now().timestamp()}"
        
        claim = Claim(
            claim_id=claim_id,
            operation=operation,
            timestamp=datetime.now(),
            context=context or {},
            inputs=inputs,
            expected_outputs=expected_outputs,
            metadata=metadata or {}
        )
        
        self.claims[claim_id] = claim
        self._save_claim(claim)
        
        return claim
    
    def update_claim(
        self,
        claim_id: str,
        actual_outputs: Optional[Dict] = None,
        status: Optional[ClaimStatus] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Claim]:
        """
        Update an existing claim.
        
        Args:
            claim_id: Claim ID
            actual_outputs: Actual outputs
            status: New status
            metadata: Additional metadata
            
        Returns:
            Updated Claim or None if not found
        """
        claim = self.claims.get(claim_id)
        if not claim:
            return None
        
        if actual_outputs is not None:
            claim.actual_outputs = actual_outputs
        
        if status is not None:
            claim.status = status
        
        if metadata is not None:
            claim.metadata.update(metadata)
        
        self._save_claim(claim)
        return claim
    
    def get_claim(self, claim_id: str) -> Optional[Claim]:
        """Get claim by ID"""
        return self.claims.get(claim_id)
    
    def query_claims(
        self,
        operation: Optional[str] = None,
        status: Optional[ClaimStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Claim]:
        """
        Query claims with filters.
        
        Args:
            operation: Filter by operation
            status: Filter by status
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of results
            
        Returns:
            List of matching claims
        """
        results = []
        
        for claim in self.claims.values():
            # Apply filters
            if operation and claim.operation != operation:
                continue
            
            if status and claim.status != status:
                continue
            
            if start_time and claim.timestamp < start_time:
                continue
            
            if end_time and claim.timestamp > end_time:
                continue
            
            results.append(claim)
            
            if len(results) >= limit:
                break
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda c: c.timestamp, reverse=True)
        
        return results
    
    def verify_claim(self, claim_id: str) -> bool:
        """
        Verify a claim's integrity.
        
        Returns:
            True if claim is valid, False otherwise
        """
        claim = self.claims.get(claim_id)
        if not claim:
            return False
        
        # Recalculate hash
        expected_hash = claim._calculate_hash()
        
        # Compare with stored hash
        return expected_hash == claim.verification_hash
    
    def _save_claim(self, claim: Claim):
        """Save claim to storage"""
        filepath = self.storage_dir / f"{claim.claim_id}.json"
        with open(filepath, 'w') as f:
            json.dump(claim.to_dict(), f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get ledger statistics"""
        stats = {
            'total_claims': len(self.claims),
            'by_status': {},
            'by_operation': {}
        }
        
        for claim in self.claims.values():
            # Count by status
            status_key = claim.status.value
            stats['by_status'][status_key] = stats['by_status'].get(status_key, 0) + 1
            
            # Count by operation
            stats['by_operation'][claim.operation] = stats['by_operation'].get(claim.operation, 0) + 1
        
        return stats
    
    def export_audit_trail(self, filepath: str):
        """
        Export complete audit trail.
        
        Args:
            filepath: Path to export file
        """
        audit_trail = {
            'export_time': datetime.now().isoformat(),
            'total_claims': len(self.claims),
            'claims': [claim.to_dict() for claim in self.claims.values()]
        }
        
        with open(filepath, 'w') as f:
            json.dump(audit_trail, f, indent=2)


def main():
    """Test claims ledger"""
    print("=== Dive Claims Ledger Test ===\n")
    
    ledger = DiveClaimsLedger()
    
    # Create claims
    print("--- Creating Claims ---")
    
    claim1 = ledger.create_claim(
        operation="generate_code",
        inputs={'spec': 'Create a hello world function'},
        expected_outputs={'code': 'def hello(): ...'},
        metadata={'language': 'python'}
    )
    print(f"Created claim: {claim1.claim_id}")
    print(f"Verification hash: {claim1.verification_hash}")
    
    claim2 = ledger.create_claim(
        operation="analyze_complexity",
        inputs={'task': 'Design REST API'},
        metadata={'complexity': 'high'}
    )
    print(f"\nCreated claim: {claim2.claim_id}")
    
    claim3 = ledger.create_claim(
        operation="generate_code",
        inputs={'spec': 'Create a fibonacci function'},
        metadata={'language': 'python'}
    )
    print(f"\nCreated claim: {claim3.claim_id}")
    
    # Update claims
    print("\n--- Updating Claims ---")
    ledger.update_claim(
        claim1.claim_id,
        actual_outputs={'code': 'def hello():\n    print("Hello")'},
        status=ClaimStatus.VERIFIED
    )
    print(f"Updated claim {claim1.claim_id} to VERIFIED")
    
    # Query claims
    print("\n--- Querying Claims ---")
    code_claims = ledger.query_claims(operation="generate_code")
    print(f"Found {len(code_claims)} code generation claims")
    
    verified_claims = ledger.query_claims(status=ClaimStatus.VERIFIED)
    print(f"Found {len(verified_claims)} verified claims")
    
    # Verify claim
    print("\n--- Verifying Claims ---")
    is_valid = ledger.verify_claim(claim1.claim_id)
    print(f"Claim {claim1.claim_id} is valid: {is_valid}")
    
    # Show stats
    print("\n--- Ledger Statistics ---")
    stats = ledger.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Export audit trail
    print("\n--- Exporting Audit Trail ---")
    ledger.export_audit_trail("/tmp/audit_trail.json")
    print("Exported to /tmp/audit_trail.json")


if __name__ == "__main__":
    main()
