
# SynapSense

**Neuromorphic Sensor Fusion for Real-Time, Brain-Inspired Perception**  
*Spiking Neural Networks · Liquid Neural Networks · Event-Based Sensing*

## Project Overview

**SynapSense** is an evolving biologically inspired framework for **asynchronous multimodal sensor fusion**. It combines Spiking Neural Networks (SNNs) and Liquid Neural Networks (LNNs) to process data the way biological systems do — with sparse, event-driven spikes, not dense frames.

**Vision:**  
*To build brain-like perception systems that can fuse complex sensory inputs efficiently, robustly, and in real time.*

The system is being developed to support event-driven processing from:
- Dynamic Vision Sensors (DVS)
- LiDAR
- Inertial Measurement Units (IMU)
- RGB Cameras  
*(Future support: RADAR, Hyperspectral, Infrared Sensors)*

SynapSense integrates biologically plausible spike encoding, neuromodulated fusion, and adaptive temporal memory to enable energy-efficient AI for robotics and edge devices.

## Key Features

- **Unified Spike Representation:** Standardized spiking format across all sensor modalities.
- **Biologically Inspired Spike Encoders:** Dedicated encoders for DVS, LiDAR, IMU, and RGB with support for event-based and latency-coded streams.
- **Adaptive Fusion Core:** Supports attention-based fusion, salience weighting, and synaptic plasticity (STDP, DECOLLE).
- **Temporal Memory Core:** Liquid Neural Networks (LNNs) capture both short- and long-term dependencies.
- **Dual-Path Readout:** Fast reflexive outputs for quick decisions and slower deliberative pathways for context-rich reasoning.
- **Rich Visualisation Suite:** Tools to visualize spike trains, salience maps, and spatio-temporal event patterns.
- **Extensible Benchmarking:** Compatible with DSEC, KITTI, and nuScenes datasets for reproducible evaluation.

## Repository Structure (Ongoing - Subject to Reorganization)

```text
SynapSense/
├── core/               # Private submodule (contact for access)
├── docs/               # Public design documents and diagrams
├── experiments/        # Benchmarking scripts and task-specific tests
├── utils/              # Public utilities and helper scripts
├── visualisation/      # Public visualization tools
├── benchmark/          # Benchmark datasets and performance logs
├── examples/           # Jupyter notebooks and demo pipelines
├── requirements.txt    # Package dependencies
├── LICENSE             # Project license
└── README.md           # This file
```

## Getting Started

### 1. Clone the Repository

```bash
git clone  https://github.com/Nikhil1321/SynapSense.git
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```
Optional (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Public Demos

You can run the public demos and visualization tools without core access:
```bash
cd examples
jupyter notebook demo_spike_visualisation.ipynb
```
**Public Demos Would Include:**
- Visualization of spatio-temporal spike trains  
- Preliminary attention maps and basic workflows  

## Collaboration and Access

The `core/` directory contains the biologically inspired fusion algorithms, memory modules, and neuromodulation blocks. Access is reserved for:
- Professors and academic supervisors
- Research collaborators
- Potential co-developers for neuromorphic hardware platforms (Loihi, SpiNNaker)

If you are interested in reviewing or contributing to these components, I warmly welcome collaboration.  
**Contact:** nikhilraj1321@gmail.com

You will then be able to explore advanced examples, full fusion pipelines, and system benchmarks.

### Publicly Available  (Ongoing - Subject to Change):

- Visualization tools for spatio-temporal spike trains and system outputs  
- Benchmarking scaffolds for dataset integration and evaluation  
- Example notebooks showcasing visualization and basic workflows  

## Project Roadmap (2025)

- [x] Develop modular spike encoders across modalities
- [x] Build unified spike event representation
- [ ] Implement attention-based fusion core (in progress)
- [ ] Integrate liquid memory modules (in progress)
- [ ] Benchmark on DSEC and KITTI datasets
- [ ] Extend to Loihi and SpiNNaker hardware (planned)

## About Me

I am **Nikhil Raj**, a neuromorphic computing researcher passionate about biologically inspired AI, spiking neural networks, and sensor fusion for energy-efficient autonomous systems. My work explores **real-time perception inspired by the brain’s sparse, event-driven processing.**

I am currently building **SynapSense** to develop low-latency, interpretable multimodal fusion frameworks that bridge neuroscience, robotics, and neuromorphic hardware.

**Full PhD Proposal and Detailed Experience Available on Request**  
[LinkedIn Profile](https://www.linkedin.com/in/13nikhil)


## License

This repository is released under the MIT License.  
*The core is selectively accessible and follows a separate licensing policy.*
