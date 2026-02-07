#!/usr/bin/env python3
"""
Dive Artifact Manager - V22 Thinking Engine Component

Manages structured artifacts generated during reasoning.
Part of the Thinking Engine transformation (Week 3).
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class ArtifactType(Enum):
    """Types of artifacts"""
    CODE = "code"
    DIAGRAM = "diagram"
    DOCUMENT = "document"
    DATA = "data"
    REPORT = "report"
    PLAN = "plan"
    ANALYSIS = "analysis"
    TEST = "test"


@dataclass
class Artifact:
    """A structured artifact"""
    artifact_id: str
    artifact_type: ArtifactType
    name: str
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    sha256: Optional[str] = None
    
    def __post_init__(self):
        """Calculate SHA256 hash of content"""
        if self.sha256 is None:
            content_str = json.dumps(self.content, sort_keys=True)
            self.sha256 = hashlib.sha256(content_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'artifact_id': self.artifact_id,
            'artifact_type': self.artifact_type.value,
            'name': self.name,
            'content': self.content,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'sha256': self.sha256
        }


class DiveArtifactManager:
    """
    Manages structured artifacts generated during reasoning.
    
    Instead of just returning text, Dive AI V22 generates structured
    artifacts that can be versioned, shared, and reused.
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or "/tmp/dive_artifacts")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts: Dict[str, Artifact] = {}
        self.artifact_counter = 0
    
    def create(
        self,
        artifact_type: ArtifactType,
        name: str,
        content: Any,
        metadata: Optional[Dict] = None
    ) -> Artifact:
        """
        Create a new artifact.
        
        Args:
            artifact_type: Type of artifact
            name: Artifact name
            content: Artifact content
            metadata: Optional metadata
            
        Returns:
            Created Artifact
        """
        self.artifact_counter += 1
        artifact_id = f"artifact_{self.artifact_counter}_{datetime.now().timestamp()}"
        
        artifact = Artifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            name=name,
            content=content,
            metadata=metadata or {}
        )
        
        self.artifacts[artifact_id] = artifact
        return artifact
    
    def get(self, artifact_id: str) -> Optional[Artifact]:
        """Get artifact by ID"""
        return self.artifacts.get(artifact_id)
    
    def list_by_type(self, artifact_type: ArtifactType) -> List[Artifact]:
        """List all artifacts of a specific type"""
        return [
            a for a in self.artifacts.values()
            if a.artifact_type == artifact_type
        ]
    
    def save(self, artifact: Artifact) -> str:
        """
        Save artifact to disk.
        
        Returns:
            Path to saved artifact
        """
        # Create type-specific directory
        type_dir = self.storage_dir / artifact.artifact_type.value
        type_dir.mkdir(exist_ok=True)
        
        # Save artifact
        filepath = type_dir / f"{artifact.artifact_id}.json"
        with open(filepath, 'w') as f:
            json.dump(artifact.to_dict(), f, indent=2)
        
        return str(filepath)
    
    def load(self, filepath: str) -> Artifact:
        """Load artifact from disk"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        artifact = Artifact(
            artifact_id=data['artifact_id'],
            artifact_type=ArtifactType(data['artifact_type']),
            name=data['name'],
            content=data['content'],
            metadata=data['metadata'],
            created_at=datetime.fromisoformat(data['created_at']),
            sha256=data['sha256']
        )
        
        self.artifacts[artifact.artifact_id] = artifact
        return artifact
    
    def create_code_artifact(
        self,
        name: str,
        code: str,
        language: str,
        metadata: Optional[Dict] = None
    ) -> Artifact:
        """Create a code artifact"""
        metadata = metadata or {}
        metadata['language'] = language
        metadata['lines'] = len(code.split('\n'))
        
        return self.create(
            ArtifactType.CODE,
            name,
            {'code': code, 'language': language},
            metadata
        )
    
    def create_document_artifact(
        self,
        name: str,
        content: str,
        format: str = "markdown",
        metadata: Optional[Dict] = None
    ) -> Artifact:
        """Create a document artifact"""
        metadata = metadata or {}
        metadata['format'] = format
        metadata['word_count'] = len(content.split())
        
        return self.create(
            ArtifactType.DOCUMENT,
            name,
            {'content': content, 'format': format},
            metadata
        )
    
    def create_analysis_artifact(
        self,
        name: str,
        analysis: Dict,
        metadata: Optional[Dict] = None
    ) -> Artifact:
        """Create an analysis artifact"""
        return self.create(
            ArtifactType.ANALYSIS,
            name,
            analysis,
            metadata
        )
    
    def create_plan_artifact(
        self,
        name: str,
        plan: Dict,
        metadata: Optional[Dict] = None
    ) -> Artifact:
        """Create a plan artifact"""
        return self.create(
            ArtifactType.PLAN,
            name,
            plan,
            metadata
        )
    
    def get_stats(self) -> Dict:
        """Get artifact statistics"""
        stats = {
            'total_artifacts': len(self.artifacts),
            'by_type': {}
        }
        
        for artifact_type in ArtifactType:
            count = len(self.list_by_type(artifact_type))
            if count > 0:
                stats['by_type'][artifact_type.value] = count
        
        return stats
    
    def export_all(self) -> Dict[str, str]:
        """
        Export all artifacts to disk.
        
        Returns:
            Dictionary mapping artifact IDs to file paths
        """
        exports = {}
        for artifact_id, artifact in self.artifacts.items():
            filepath = self.save(artifact)
            exports[artifact_id] = filepath
        return exports


def main():
    """Test artifact manager"""
    print("=== Dive Artifact Manager Test ===\n")
    
    manager = DiveArtifactManager()
    
    # Create code artifact
    code_artifact = manager.create_code_artifact(
        name="hello_world.py",
        code="def hello():\n    print('Hello, World!')",
        language="python",
        metadata={'author': 'Dive AI'}
    )
    print(f"Created code artifact: {code_artifact.artifact_id}")
    print(f"SHA256: {code_artifact.sha256}")
    
    # Create document artifact
    doc_artifact = manager.create_document_artifact(
        name="design_doc.md",
        content="# Design Document\n\nThis is a design document.",
        format="markdown"
    )
    print(f"\nCreated document artifact: {doc_artifact.artifact_id}")
    
    # Create analysis artifact
    analysis_artifact = manager.create_analysis_artifact(
        name="complexity_analysis",
        analysis={
            'complexity_score': 75,
            'factors': {
                'technical_complexity': 20,
                'domain_count': 15
            }
        }
    )
    print(f"\nCreated analysis artifact: {analysis_artifact.artifact_id}")
    
    # Create plan artifact
    plan_artifact = manager.create_plan_artifact(
        name="implementation_plan",
        plan={
            'phases': [
                {'id': 1, 'name': 'Design'},
                {'id': 2, 'name': 'Implementation'},
                {'id': 3, 'name': 'Testing'}
            ]
        }
    )
    print(f"\nCreated plan artifact: {plan_artifact.artifact_id}")
    
    # Show stats
    print("\n=== Artifact Statistics ===")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Test save/load
    print("\n=== Testing Save/Load ===")
    filepath = manager.save(code_artifact)
    print(f"Saved to: {filepath}")
    
    # Create new manager and load
    manager2 = DiveArtifactManager()
    loaded_artifact = manager2.load(filepath)
    print(f"Loaded artifact: {loaded_artifact.name}")
    print(f"SHA256 matches: {loaded_artifact.sha256 == code_artifact.sha256}")
    
    # Test export all
    print("\n=== Testing Export All ===")
    exports = manager.export_all()
    print(f"Exported {len(exports)} artifacts")
    for artifact_id, path in exports.items():
        print(f"  {artifact_id}: {path}")


if __name__ == "__main__":
    main()
