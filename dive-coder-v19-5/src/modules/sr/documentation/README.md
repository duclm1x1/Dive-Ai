_# SR - Semantic Routing Engine

**Version:** 2.0 (Upgraded from Orchestrator Logic)
**Status:** Active

## 1. Overview

The Semantic Routing (SR) Engine is an advanced system that intelligently directs incoming prompts and tasks to the most suitable Dive Coder agent or specialized skill. It goes beyond simple keyword matching, analyzing the underlying semantic meaning and intent of a request to ensure it is handled by the expert best equipped for the job. This upgrade externalizes the routing logic from the core orchestrator into a dedicated, more powerful engine.

## 2. Core Functionality

- **Semantic Analysis:** Uses deep learning models to understand the nuances and intent of user prompts.
- **Agent/Skill Profiling:** Maintains dynamic profiles of each agent and skill, cataloging their capabilities, strengths, and recent performance.
- **Optimal Routing:** Employs a sophisticated decision-making algorithm to match the semantic profile of a request with the most appropriate agent/skill profile.
- **Gradient-Aware Routing (GAR) Integration:** Incorporates gradient information to further refine routing decisions, predicting which agent will learn most effectively from a given task.

## 3. Integration with Dive Engine

The SR Engine is a core, always-on component of the Dive Orchestrator. It intercepts all incoming tasks, ensuring they are routed with maximum efficiency and intelligence, dramatically improving the overall performance and specialization of the Dive Coder system.

## 4. Key Files

- `src/main.py`: The core SR engine.
- `src/semantic_analyzer.py`: The prompt analysis module.
- `src/profiler.py`: Agent and skill profiling system.
- `src/router.py`: The core routing decision logic.
- `tests/test_sr.py`: Test suite for the SR engine.
- `examples/complex_query_routing.py`: Example of routing a complex, multi-faceted query.
_
