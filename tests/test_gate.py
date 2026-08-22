import os
import json
import pytest
from gate import run_gate

@pytest.fixture
def setup_gate_files(tmp_path):
    model_path = tmp_path / "dummy_model.pt"
    model_path.write_text("fake_weights")
    
    # Pre-calculate hash of "fake_weights" -> "151c86...etc"
    # But it's easier to let the gate compute it, we just compute it here.
    import hashlib
    h = hashlib.sha256()
    h.update(b"fake_weights")
    model_hash = h.hexdigest()
    
    prop_path = tmp_path / "prop.vnnlib"
    prop_path.write_text("fake property")
    
    cert_dir = tmp_path / "certs"
    cert_dir.mkdir()
    
    proof_path = cert_dir / f"{model_hash}_prop.alethe"
    proof_path.write_text("fake proof data")
    
    json_path = cert_dir / f"{model_hash}_prop.json"
    json_data = {
        "model_hash": model_hash,
        "property_id": "prop",
        "proof_file": proof_path.name
    }
    json_path.write_text(json.dumps(json_data))
    
    return {
        "model": str(model_path),
        "prop": str(prop_path),
        "cert_dir": str(cert_dir),
        "hash": model_hash,
        "proof_path": str(proof_path),
        "json_path": str(json_path)
    }

def test_valid_model_and_certificate(setup_gate_files):
    env = setup_gate_files
    # Using mock_checker=True to simulate Carcara successfully verifying it
    res = run_gate(env["model"], env["prop"], env["cert_dir"], mock_checker=True)
    assert res.passed is True
    assert "verified successfully" in res.reason
    assert res.model_hash == env["hash"]

def test_model_hash_mismatch(setup_gate_files):
    env = setup_gate_files
    # Modify the model file so its hash changes
    with open(env["model"], "w") as f:
        f.write("modified_weights")
        
    res = run_gate(env["model"], env["prop"], env["cert_dir"], mock_checker=True)
    assert res.passed is False
    assert "no certificate found" in res.reason

def test_certificate_corrupted_checker_fails(setup_gate_files, monkeypatch):
    env = setup_gate_files
    
    # We patch subprocess.run to simulate Carcara failing on a corrupted certificate
    import subprocess
    def mock_run(*args, **kwargs):
        class MockResult:
            returncode = 1
            stdout = ""
            stderr = "parse error at line 1"
        return MockResult()
        
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    # Run gate without mock_checker flag, relying on our monkeypatched subprocess
    res = run_gate(env["model"], env["prop"], env["cert_dir"])
    assert res.passed is False
    assert "failed independent verification" in res.reason
    assert "parse error" in res.checker_output
