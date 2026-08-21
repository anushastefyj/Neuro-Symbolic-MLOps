# Neuro-Symbolic MLOps — Formal Verification Gates for ML CI/CD

## Project Goal
This project establishes a continuous integration pipeline for machine learning models that includes formal verification gates. The goal is to provide proof certificates for ML model properties (e.g., robustness, safety) before deployment, bridging the gap between Neuro-Symbolic AI methods and standard MLOps practices.

## Directory Layout
- `models/`: Trained model artifacts and ONNX exports.
- `properties/`: Formal property specifications (VNN-LIB format).
- `certificates/`: Proof certificates and metadata sidecars.
- `src/`: Source code for training, proof generation, and CI gate logic.
- `ci/github-actions/`: CI workflow definitions.
- `docs/`: Project specifications and related work.
- `tests/`: Unit tests and integration tests.
- `scripts/`: Utility scripts for environment checking, etc.

## Setup Instructions

### Python Environment
You can set up the environment using `venv` or `conda`:

**Using venv:**
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate # Linux/Mac
pip install -r requirements.txt
```

**Using Conda:**
```bash
conda env create -f environment.yml
conda activate neurosym-mlops
```

### Verifying Toolchain
Run the check script to verify the required tools are installed:
```bash
python scripts/check_tools.py
```

## Running the Demo
1. Train the toy model:
   ```bash
   python src/train.py
   ```
2. Export the trained model to ONNX format:
   ```bash
   python src/export_onnx.py
   ```
