_# DCA - Dynamic Capacity Allocation Engine

**Version:** 2.0 (Upgraded from Dynamic Attention Control)
**Status:** Active

## 1. Overview

The Dynamic Capacity Allocation (DCA) Engine is a significant upgrade to the previous Dynamic Attention Control (DAC) skill. While DAC focused on managing attention within a single model, DCA is a system-level controller that dynamically allocates computational resources (e.g., memory, processing power, model size) to different agents and tasks based on their real-time needs. This ensures that the entire Dive Coder system operates at peak efficiency, allocating more power to complex tasks and conserving resources on simpler ones.

## 2. Core Functionality

- **Real-Time Monitoring:** Continuously monitors the resource utilization and performance of all active agents and tasks.
- **Predictive Scaling:** Uses predictive models to anticipate future resource demands based on the incoming task queue and historical data.
- **Resource Orchestration:** Intelligently allocates and deallocates resources, such as scaling the number of active agents, adjusting the size of the models being used, or even distributing tasks across different hardware.
- **Quality of Service (QoS):** Ensures that high-priority tasks are always allocated the resources they need to meet their performance targets.

## 3. Integration with Dive Engine

DCA is a core, always-on component of the Dive Orchestrator. It acts as the central nervous system for resource management, ensuring the entire fleet of Dive Coder agents is utilized in the most efficient and effective way possible. It works closely with the Semantic Routing (SR) and Inference-Time Scaling (ITS) engines to make intelligent, system-wide optimization decisions.

## 4. Key Files

- `src/main.py`: The core DCA engine.
- `src/monitor.py`: The real-time resource monitoring component.
- `src/scaler.py`: The predictive scaling and resource allocation logic.
- `tests/test_dca.py`: Test suite for the DCA engine.
- `examples/handling_load_spike.py`: Example of DCA dynamically scaling up resources to handle a sudden spike in task load.
_
