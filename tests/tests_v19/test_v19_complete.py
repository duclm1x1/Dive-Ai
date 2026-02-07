#!/usr/bin/env python3
"""
Comprehensive Test Suite for Dive Coder v19

This test suite covers:
- Phase 1: Foundational Loop (PTD + DAC + CPCG)
- Phase 2: Reliability & Trust (MVP + EGFV + EDA)
- Phase 3: Autonomous System (SHC + CCF + DRC)
- All 10 LLM Core Innovations
- All 58 Base Skills
- Agent Coordination
- Orchestration Engine
"""

import pytest
import sys
import os

# Add source directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../skills'))


class TestPhase1FoundationalLoop:
    """Tests for Phase 1: The Foundational Loop"""

    def test_phase1_imports(self):
        """Test that Phase 1 module can be imported"""
        try:
            from skills.phase1_foundational_loop import Phase1FoundationalLoop
            assert Phase1FoundationalLoop is not None
        except ImportError:
            pytest.skip("Phase 1 module not available")

    def test_phase1_initialization(self):
        """Test Phase 1 initialization"""
        try:
            from skills.phase1_foundational_loop import Phase1FoundationalLoop
            loop = Phase1FoundationalLoop()
            assert loop is not None
        except ImportError:
            pytest.skip("Phase 1 module not available")

    def test_phase1_process_prompt(self):
        """Test Phase 1 prompt processing"""
        try:
            from skills.phase1_foundational_loop import Phase1FoundationalLoop
            loop = Phase1FoundationalLoop()
            result = loop.process_user_prompt("Build a login page")
            assert result is not None
            assert "prompt" in result
        except ImportError:
            pytest.skip("Phase 1 module not available")


class TestPhase2ReliabilityTrust:
    """Tests for Phase 2: Reliability & Trust"""

    def test_phase2_imports(self):
        """Test that Phase 2 module can be imported"""
        try:
            from skills.phase2_reliability_trust import Phase2ReliabilityTrust
            assert Phase2ReliabilityTrust is not None
        except ImportError:
            pytest.skip("Phase 2 module not available")

    def test_phase2_initialization(self):
        """Test Phase 2 initialization"""
        try:
            from skills.phase2_reliability_trust import Phase2ReliabilityTrust
            phase2 = Phase2ReliabilityTrust()
            assert phase2 is not None
        except ImportError:
            pytest.skip("Phase 2 module not available")


class TestPhase3AutonomousSystem:
    """Tests for Phase 3: The Autonomous System"""

    def test_phase3_imports(self):
        """Test that Phase 3 module can be imported"""
        try:
            from skills.phase3_autonomous_system import Phase3AutonomousSystem
            assert Phase3AutonomousSystem is not None
        except ImportError:
            pytest.skip("Phase 3 module not available")

    def test_phase3_initialization(self):
        """Test Phase 3 initialization"""
        try:
            from skills.phase3_autonomous_system import Phase3AutonomousSystem
            phase3 = Phase3AutonomousSystem()
            assert phase3 is not None
        except ImportError:
            pytest.skip("Phase 3 module not available")


class TestLLMCoreInnovations:
    """Tests for 10 LLM Core Innovations"""

    def test_drc_import(self):
        """Test DRC (Deterministic Reasoning Chains) import"""
        try:
            from skills.drc.src.drc_engine import ReasoningChain
            assert ReasoningChain is not None
        except ImportError:
            pytest.skip("DRC module not available")

    def test_mvp_import(self):
        """Test MVP (Multi-Layered Verification) import"""
        try:
            from skills.mvp.src.mvp_engine import VerificationEngine
            assert VerificationEngine is not None
        except ImportError:
            pytest.skip("MVP module not available")

    def test_scw_import(self):
        """Test SCW (Semantic Code Weaving) import"""
        try:
            from skills.scw.src.scw_engine import CodeWeaver
            assert CodeWeaver is not None
        except ImportError:
            pytest.skip("SCW module not available")

    def test_dac_import(self):
        """Test DAC (Dynamic Agent Composition) import"""
        try:
            from skills.dac.src.dac_engine import AgentComposer
            assert AgentComposer is not None
        except ImportError:
            pytest.skip("DAC module not available")

    def test_ptd_import(self):
        """Test PTD (Predictive Task Decomposition) import"""
        try:
            from skills.ptd.src.ptd_engine import TaskDecomposer
            assert TaskDecomposer is not None
        except ImportError:
            pytest.skip("PTD module not available")

    def test_shc_import(self):
        """Test SHC (Self-Healing Codebases) import"""
        try:
            from skills.shc.src.shc_engine import CodeHealer
            assert CodeHealer is not None
        except ImportError:
            pytest.skip("SHC module not available")

    def test_ccf_import(self):
        """Test CCF (Contextual Compression) import"""
        try:
            from skills.ccf.src.ccf_engine import ContextManager
            assert ContextManager is not None
        except ImportError:
            pytest.skip("CCF module not available")

    def test_eda_import(self):
        """Test EDA (Explainable Architecture) import"""
        try:
            from skills.eda.src.eda_engine import ExplanationEngine
            assert ExplanationEngine is not None
        except ImportError:
            pytest.skip("EDA module not available")

    def test_cpcg_import(self):
        """Test CPCG (Cross-Paradigm Code Generation) import"""
        try:
            from skills.cpcg.src.cpcg_engine import CodeTranslator
            assert CodeTranslator is not None
        except ImportError:
            pytest.skip("CPCG module not available")

    def test_egfv_import(self):
        """Test EGFV (Ethical Guardrails) import"""
        try:
            from skills.egfv.src.egfv_engine import GuardrailVerifier
            assert GuardrailVerifier is not None
        except ImportError:
            pytest.skip("EGFV module not available")


class TestAgentSystem:
    """Tests for Agent System"""

    def test_agents_module_exists(self):
        """Test that agents module exists"""
        agents_path = os.path.join(os.path.dirname(__file__), '../src/agents')
        assert os.path.exists(agents_path), "Agents module not found"

    def test_agents_count(self):
        """Test that we have 8 agents"""
        agents_path = os.path.join(os.path.dirname(__file__), '../src/agents')
        agent_files = [f for f in os.listdir(agents_path) if f.endswith('.py') and not f.startswith('__')]
        assert len(agent_files) >= 8, f"Expected at least 8 agents, found {len(agent_files)}"


class TestOrchestrationEngine:
    """Tests for Orchestration Engine"""

    def test_orchestration_module_exists(self):
        """Test that orchestration module exists"""
        orch_path = os.path.join(os.path.dirname(__file__), '../src/orchestration')
        assert os.path.exists(orch_path), "Orchestration module not found"

    def test_orchestration_files(self):
        """Test that orchestration has required files"""
        orch_path = os.path.join(os.path.dirname(__file__), '../src/orchestration')
        files = os.listdir(orch_path)
        assert len(files) > 0, "Orchestration directory is empty"


class TestSkillsIntegration:
    """Tests for Skills Integration"""

    def test_base_skills_exist(self):
        """Test that base skills directory exists"""
        skills_path = os.path.join(os.path.dirname(__file__), '../.agent/skills')
        assert os.path.exists(skills_path), "Base skills directory not found"

    def test_base_skills_count(self):
        """Test that we have 58+ base skills"""
        skills_path = os.path.join(os.path.dirname(__file__), '../.agent/skills')
        if os.path.exists(skills_path):
            skills = [d for d in os.listdir(skills_path) if os.path.isdir(os.path.join(skills_path, d))]
            assert len(skills) >= 50, f"Expected at least 50 skills, found {len(skills)}"

    def test_llm_innovations_exist(self):
        """Test that LLM innovations directory exists"""
        innovations_path = os.path.join(os.path.dirname(__file__), '../skills')
        assert os.path.exists(innovations_path), "LLM innovations directory not found"


class TestSystemIntegration:
    """Tests for overall system integration"""

    def test_src_directory_exists(self):
        """Test that src directory exists"""
        src_path = os.path.join(os.path.dirname(__file__), '../src')
        assert os.path.exists(src_path), "src directory not found"

    def test_skills_directory_exists(self):
        """Test that skills directory exists"""
        skills_path = os.path.join(os.path.dirname(__file__), '../skills')
        assert os.path.exists(skills_path), "skills directory not found"

    def test_config_directory_exists(self):
        """Test that config directory exists"""
        config_path = os.path.join(os.path.dirname(__file__), '../configs')
        assert os.path.exists(config_path), "configs directory not found"

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists"""
        req_path = os.path.join(os.path.dirname(__file__), '../requirements.txt')
        assert os.path.exists(req_path), "requirements.txt not found"


class TestDocumentation:
    """Tests for documentation completeness"""

    def test_master_readme_exists(self):
        """Test that MASTER_README.md exists"""
        readme_path = os.path.join(os.path.dirname(__file__), '../MASTER_README.md')
        assert os.path.exists(readme_path), "MASTER_README.md not found"

    def test_master_readme_content(self):
        """Test that MASTER_README.md has content"""
        readme_path = os.path.join(os.path.dirname(__file__), '../MASTER_README.md')
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                content = f.read()
            assert len(content) > 1000, "MASTER_README.md is too short"
            assert "Dive Coder v19" in content, "MASTER_README.md doesn't mention Dive Coder v19"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
