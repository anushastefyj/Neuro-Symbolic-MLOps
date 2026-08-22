# Phase 2 Results

## Verification Results
- **Model**: `models/toy_model.pt` (small fully-connected network <10k parameters)
- **Property**: Local robustness epsilon box (VNN-LIB format)
- **Result**: `UNSAT` (Property Holds)
- **Proof File**: `certificates/c0ee14513805f0002b29b4343e26011145920ec95cd0bc0e1b613df77aaae89f_toy_property.alethe`

## Proof Generation Complexity
One of the most significant findings from this phase is the sheer size of the proof certificate. For a tiny 3-layer toy network, the generated `.alethe` proof certificate is **14 MB**. 

This heavily underscores the core premise of the Neuro-Symbolic MLOps project: proof generation does not scale linearly. Storing, transmitting, and validating these proofs in a CI/CD pipeline requires careful orchestration.

## Independent Proof Checking (Carcara)

To independently validate the Alethe proof, we use `Carcara`, a Rust-based checker. 

**Checker Execution Speed:** Checking the 14MB proof takes roughly ~1.2 seconds. This is notably much faster than proof generation, which is a desirable characteristic for a CI gate (verifying the proof is computationally cheaper than searching for it).

### Environment Fallback (Windows -> WSL2)
Carcara does not provide pre-compiled Windows binaries, and building natively via `cargo install` fails if the Rust toolchain is missing on Windows.

If you are on Windows, the recommended fallback is to use WSL2 (Windows Subsystem for Linux):

1. **Install WSL2** (if not already installed):
   Run in an admin PowerShell:
   ```bash
   wsl --install
   ```
   *Reboot your computer if prompted.*

2. **Install Rust in WSL2**:
   Open your Ubuntu/WSL terminal and run:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
   source "$HOME/.cargo/env"
   ```

3. **Install Carcara**:
   ```bash
   cargo install --git https://github.com/ufmg-smite/carcara.git
   ```

4. **Run Checker**:
   ```bash
   carcara check certificates/<hash>_toy_property.alethe
   ```
