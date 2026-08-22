import os
import json
import subprocess
import time
from datetime import datetime
from proof_store import get_model_hash

class GateResult:
    def __init__(self, passed, reason, model_hash, certificate_path, checker_used, checker_output, timestamp):
        self.passed = passed
        self.reason = reason
        self.model_hash = model_hash
        self.certificate_path = certificate_path
        self.checker_used = checker_used
        self.checker_output = checker_output
        self.timestamp = timestamp

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"GateResult({status} - {self.reason})"

def run_gate(model_path, property_spec_path, certificate_dir, timeout_sec=300, mock_checker=False):
    timestamp = datetime.now().isoformat()
    
    # a. Compute current model hash
    if not os.path.exists(model_path):
        return GateResult(False, f"Model not found: {model_path}", None, None, None, None, timestamp)
        
    model_hash = get_model_hash(model_path)
    property_id = os.path.basename(property_spec_path).split('.')[0]
    
    # b. Look for a matching certificate in certificate_dir
    if not os.path.exists(certificate_dir):
        return GateResult(False, "certificate_dir does not exist", model_hash, None, None, None, timestamp)
        
    matched_json = None
    for filename in os.listdir(certificate_dir):
        if filename.endswith(".json"):
            json_path = os.path.join(certificate_dir, filename)
            try:
                with open(json_path, "r") as f:
                    meta = json.load(f)
                    if meta.get("model_hash") == model_hash and meta.get("property_id") == property_id:
                        matched_json = meta
                        break
            except (json.JSONDecodeError, IOError):
                continue
                
    # c. If no matching certificate exists -> FAIL
    if not matched_json:
        return GateResult(False, "no certificate found for this model+property", model_hash, None, None, None, timestamp)
        
    proof_filename = matched_json.get("proof_file")
    if not proof_filename:
        return GateResult(False, "JSON sidecar missing 'proof_file' key", model_hash, None, None, None, timestamp)
        
    proof_path = os.path.join(certificate_dir, proof_filename)
    if not os.path.exists(proof_path):
        return GateResult(False, "proof file referenced in JSON does not exist", model_hash, None, None, None, timestamp)
        
    # d. Re-run independent checker
    checker_used = "carcara"
    checker_cmd = ["carcara", "check", proof_path]
    
    if os.name == 'nt':
        checker_cmd = ["wsl", "carcara", "check", proof_path.replace("\\", "/")]
        
    if mock_checker:
        # Simulate checker execution
        return GateResult(True, "proof verified successfully", model_hash, proof_path, checker_used + " (MOCKED)", "Valid", timestamp)
        
    try:
        # f. Add a configurable timeout
        result = subprocess.run(checker_cmd, capture_output=True, text=True, timeout=timeout_sec)
        
        if result.returncode == 0:
            # e. If checker passes -> PASS
            return GateResult(True, "proof verified successfully", model_hash, proof_path, checker_used, result.stdout, timestamp)
        else:
            # If checker fails or errors -> FAIL
            return GateResult(False, "proof failed independent verification", model_hash, proof_path, checker_used, result.stderr or result.stdout, timestamp)
            
    except subprocess.TimeoutExpired:
        # If it times out, treat as FAIL
        return GateResult(False, "checker timeout", model_hash, proof_path, checker_used, "Timeout", timestamp)
    except FileNotFoundError:
        return GateResult(False, "checker executable not found", model_hash, proof_path, checker_used, "FileNotFoundError", timestamp)

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Neuro-Symbolic MLOps CI Gate")
    parser.add_argument("model_path", help="Path to the model file")
    parser.add_argument("property_spec_path", help="Path to the property spec file")
    parser.add_argument("certificate_dir", help="Directory containing certificates")
    parser.add_argument("--mock-checker", action="store_true", help="Mock Carcara execution for testing")
    args = parser.parse_args()
    
    res = run_gate(args.model_path, args.property_spec_path, args.certificate_dir, mock_checker=args.mock_checker)
    print(f"Status: {'PASS' if res.passed else 'FAIL'}")
    print(f"Reason: {res.reason}")
    if res.checker_output:
        print(f"Checker Output:\n{res.checker_output}")
