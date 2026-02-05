_# HDS - Hybrid Dense-Sparse Engine

**Version:** 1.0
**Status:** Active

## 1. Overview

The Hybrid Dense-Sparse (HDS) Engine allows Dive Coder's neural networks to dynamically switch between dense and sparse layers during runtime. This provides a powerful mechanism to balance computational cost and model capacity, using high-capacity dense layers for complex tasks and energy-efficient sparse layers for simpler ones.

## 2. Core Functionality

- **Dynamic Layer Switching:** A controller that decides when to activate or deactivate specific layers or neurons based on the input data and task complexity.
- **Sparse Computation Kernels:** Optimized kernels for performing computations on sparse matrices, significantly reducing FLOPs and memory usage.
- **Mixture-of-Experts (MoE) Integration:** Implements a sparse MoE layer where only a subset of "expert" sub-networks are activated for any given input.
- **Load Balancing:** Ensures that the computational load is evenly distributed across the activated experts or sparse layers.

## 3. Integration with Dive Engine

HDS is an always-on optimization layer within the Dive Engine. It works transparently in the background, modifying the execution of the core neural models to improve their efficiency without compromising their performance. It is particularly effective in large-scale deployments with diverse workloads.

## 4. Key Files

- `src/main.py`: The core HDS engine.
- `src/controller.py`: The dynamic layer switching logic.
- `src/sparse_kernels.py`: The custom sparse computation kernels.
- `src/moe_layer.py`: The Mixture-of-Experts layer implementation.
- `tests/test_hds.py`: Test suite for the HDS engine.
- `examples/dynamic_network_pruning.py`: Example of dynamically pruning a network for a simple task.
_
