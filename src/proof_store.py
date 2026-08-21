import os
import hashlib
import json
from datetime import datetime

# Directory for storing proof certificates
CERT_DIR = "certificates"

def get_model_hash(model_path):
    """Computes SHA256 hash of the model file."""
    sha256_hash = hashlib.sha256()
    with open(model_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def store_certificate(model_path, property_id, proof_data, result, solver_version="cvc5"):
    """
    Saves a proof certificate and metadata sidecar with model hashing.
    """
    os.makedirs(CERT_DIR, exist_ok=True)
    
    model_hash = get_model_hash(model_path)
    base_filename = f"{model_hash}_{property_id}"
    
    # Save the proof certificate
    proof_path = os.path.join(CERT_DIR, f"{base_filename}.alethe")
    with open(proof_path, "w") as f:
        f.write(proof_data)
        
    # Save metadata sidecar
    metadata = {
        "model_hash": model_hash,
        "property_id": property_id,
        "solver": solver_version,
        "result": result,
        "timestamp": datetime.now().isoformat(),
        "proof_file": f"{base_filename}.alethe"
    }
    
    metadata_path = os.path.join(CERT_DIR, f"{base_filename}.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Stored certificate and metadata for model hash: {model_hash}")
    return proof_path, metadata_path

def load_certificate(model_path, property_id):
    """
    Loads a proof certificate and metadata.
    """
    model_hash = get_model_hash(model_path)
    base_filename = f"{model_hash}_{property_id}"
    
    proof_path = os.path.join(CERT_DIR, f"{base_filename}.alethe")
    metadata_path = os.path.join(CERT_DIR, f"{base_filename}.json")
    
    if not os.path.exists(proof_path) or not os.path.exists(metadata_path):
        return None
        
    with open(proof_path, "r") as f:
        proof_data = f.read()
        
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
        
    return proof_data, metadata

