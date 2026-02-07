#!/usr/bin/env python3
"""
Dive Evidence Pack - V22 Claims Ledger Component

Bundles evidence for reproducibility and verification.
Part of the Claims Ledger transformation (Week 6).
"""

import json
import hashlib
import gzip
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class EvidencePack:
    """
    A bundle of evidence for a claim.
    
    Evidence packs enable full reproducibility and verification.
    """
    pack_id: str
    claim_id: str
    timestamp: datetime
    artifacts: Dict[str, Any] = field(default_factory=dict)
    intermediate_steps: List[Dict] = field(default_factory=list)
    decisions: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    sha256: Optional[str] = None
    compressed: bool = False
    
    def __post_init__(self):
        """Calculate SHA256 hash"""
        if self.sha256 is None:
            self.sha256 = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate cryptographic hash of evidence"""
        evidence_data = {
            'pack_id': self.pack_id,
            'claim_id': self.claim_id,
            'artifacts': self.artifacts,
            'intermediate_steps': self.intermediate_steps,
            'decisions': self.decisions
        }
        evidence_str = json.dumps(evidence_data, sort_keys=True)
        return hashlib.sha256(evidence_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'pack_id': self.pack_id,
            'claim_id': self.claim_id,
            'timestamp': self.timestamp.isoformat(),
            'artifacts': self.artifacts,
            'intermediate_steps': self.intermediate_steps,
            'decisions': self.decisions,
            'metadata': self.metadata,
            'sha256': self.sha256,
            'compressed': self.compressed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EvidencePack':
        """Create evidence pack from dictionary"""
        return cls(
            pack_id=data['pack_id'],
            claim_id=data['claim_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            artifacts=data['artifacts'],
            intermediate_steps=data['intermediate_steps'],
            decisions=data['decisions'],
            metadata=data.get('metadata', {}),
            sha256=data.get('sha256'),
            compressed=data.get('compressed', False)
        )


class DiveEvidencePacker:
    """
    Packs evidence for claims.
    
    Evidence packing enables:
    - Full reproducibility
    - Cryptographic verification
    - Portable evidence bundles
    - Compressed storage
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or "/tmp/dive_evidence")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.packs: Dict[str, EvidencePack] = {}
        self.pack_counter = 0
    
    def create_pack(
        self,
        claim_id: str,
        artifacts: Optional[Dict] = None,
        intermediate_steps: Optional[List] = None,
        decisions: Optional[List] = None,
        metadata: Optional[Dict] = None
    ) -> EvidencePack:
        """
        Create an evidence pack.
        
        Args:
            claim_id: Associated claim ID
            artifacts: Artifacts generated
            intermediate_steps: Intermediate steps taken
            decisions: Decisions made
            metadata: Additional metadata
            
        Returns:
            Created EvidencePack
        """
        self.pack_counter += 1
        pack_id = f"pack_{self.pack_counter}_{datetime.now().timestamp()}"
        
        pack = EvidencePack(
            pack_id=pack_id,
            claim_id=claim_id,
            timestamp=datetime.now(),
            artifacts=artifacts or {},
            intermediate_steps=intermediate_steps or [],
            decisions=decisions or [],
            metadata=metadata or {}
        )
        
        self.packs[pack_id] = pack
        return pack
    
    def add_artifact(self, pack_id: str, name: str, artifact: Any):
        """Add an artifact to the pack"""
        pack = self.packs.get(pack_id)
        if pack:
            pack.artifacts[name] = artifact
            # Recalculate hash
            pack.sha256 = pack._calculate_hash()
    
    def add_step(self, pack_id: str, step: Dict):
        """Add an intermediate step to the pack"""
        pack = self.packs.get(pack_id)
        if pack:
            pack.intermediate_steps.append(step)
            pack.sha256 = pack._calculate_hash()
    
    def add_decision(self, pack_id: str, decision: Dict):
        """Add a decision to the pack"""
        pack = self.packs.get(pack_id)
        if pack:
            pack.decisions.append(decision)
            pack.sha256 = pack._calculate_hash()
    
    def save(self, pack_id: str, compress: bool = True) -> str:
        """
        Save evidence pack to disk.
        
        Args:
            pack_id: Pack ID
            compress: Whether to compress the pack
            
        Returns:
            Path to saved pack
        """
        pack = self.packs.get(pack_id)
        if not pack:
            raise ValueError(f"Pack {pack_id} not found")
        
        pack.compressed = compress
        
        # Convert to JSON
        pack_json = json.dumps(pack.to_dict(), indent=2)
        
        # Save
        if compress:
            filepath = self.storage_dir / f"{pack_id}.json.gz"
            with gzip.open(filepath, 'wt') as f:
                f.write(pack_json)
        else:
            filepath = self.storage_dir / f"{pack_id}.json"
            with open(filepath, 'w') as f:
                f.write(pack_json)
        
        return str(filepath)
    
    def load(self, filepath: str) -> EvidencePack:
        """Load evidence pack from disk"""
        filepath = Path(filepath)
        
        if filepath.suffix == '.gz':
            with gzip.open(filepath, 'rt') as f:
                data = json.load(f)
        else:
            with open(filepath, 'r') as f:
                data = json.load(f)
        
        pack = EvidencePack.from_dict(data)
        self.packs[pack.pack_id] = pack
        return pack
    
    def verify(self, pack_id: str) -> bool:
        """
        Verify evidence pack integrity.
        
        Returns:
            True if pack is valid, False otherwise
        """
        pack = self.packs.get(pack_id)
        if not pack:
            return False
        
        # Recalculate hash
        expected_hash = pack._calculate_hash()
        
        # Compare with stored hash
        return expected_hash == pack.sha256
    
    def get_stats(self) -> Dict:
        """Get evidence packer statistics"""
        total_size = 0
        for pack in self.packs.values():
            pack_json = json.dumps(pack.to_dict())
            total_size += len(pack_json.encode())
        
        return {
            'total_packs': len(self.packs),
            'total_size_bytes': total_size,
            'avg_size_bytes': total_size // max(1, len(self.packs))
        }


def main():
    """Test evidence packer"""
    print("=== Dive Evidence Packer Test ===\n")
    
    packer = DiveEvidencePacker()
    
    # Create evidence pack
    print("--- Creating Evidence Pack ---")
    pack = packer.create_pack(
        claim_id="claim_123",
        artifacts={
            'code': 'def hello(): print("Hello")',
            'tests': 'def test_hello(): assert True'
        },
        intermediate_steps=[
            {'step': 1, 'action': 'analyze_requirements'},
            {'step': 2, 'action': 'generate_code'},
            {'step': 3, 'action': 'generate_tests'}
        ],
        decisions=[
            {
                'description': 'Choose language',
                'options': ['Python', 'JavaScript'],
                'chosen': 'Python',
                'reasoning': 'Better for this use case'
            }
        ],
        metadata={'complexity': 'medium'}
    )
    print(f"Created pack: {pack.pack_id}")
    print(f"SHA256: {pack.sha256}")
    
    # Add more artifacts
    print("\n--- Adding Artifacts ---")
    packer.add_artifact(pack.pack_id, 'documentation', '# Documentation\n\nThis is a doc.')
    print("Added documentation artifact")
    print(f"New SHA256: {pack.sha256}")
    
    # Verify pack
    print("\n--- Verifying Pack ---")
    is_valid = packer.verify(pack.pack_id)
    print(f"Pack is valid: {is_valid}")
    
    # Save pack
    print("\n--- Saving Pack ---")
    
    # Save uncompressed
    filepath_uncompressed = packer.save(pack.pack_id, compress=False)
    print(f"Saved uncompressed: {filepath_uncompressed}")
    
    # Save compressed
    filepath_compressed = packer.save(pack.pack_id, compress=True)
    print(f"Saved compressed: {filepath_compressed}")
    
    # Compare sizes
    import os
    size_uncompressed = os.path.getsize(filepath_uncompressed)
    size_compressed = os.path.getsize(filepath_compressed)
    compression_ratio = (1 - size_compressed / size_uncompressed) * 100
    
    print(f"\nUncompressed size: {size_uncompressed} bytes")
    print(f"Compressed size: {size_compressed} bytes")
    print(f"Compression ratio: {compression_ratio:.1f}%")
    
    # Load pack
    print("\n--- Loading Pack ---")
    packer2 = DiveEvidencePacker()
    loaded_pack = packer2.load(filepath_compressed)
    print(f"Loaded pack: {loaded_pack.pack_id}")
    print(f"SHA256 matches: {loaded_pack.sha256 == pack.sha256}")
    
    # Show stats
    print("\n--- Statistics ---")
    stats = packer.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
