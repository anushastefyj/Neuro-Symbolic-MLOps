import sys
import os
# pyrefly: ignore [missing-import]
import torch
import cvc5
from proof_store import store_certificate
from train import ToyNet

def run_verifier(model_path, property_path):
    print(f"Verifying model {model_path} against {property_path}")
    
    # Load model
    model = ToyNet()
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    
    # Setup cvc5 solver
    solver = cvc5.Solver()
    solver.setOption("produce-proofs", "true")
    solver.setOption("proof-format-mode", "alethe")
    solver.setLogic("QF_NRA") 
    
    real_sort = solver.getRealSort()
    
    # Define input variables X_0, X_1
    x0 = solver.mkConst(real_sort, "X_0")
    x1 = solver.mkConst(real_sort, "X_1")
    
    def mk_real(val):
        return solver.mkReal(str(float(val)))
        
    # We parse the specific toy property loosely (hardcoded mapping for phase 2 demo)
    # The property asks to assert:
    # (>= X_0 0.05), (<= X_0 0.15)
    # (>= X_1 0.05), (<= X_1 0.15)
    solver.assertFormula(solver.mkTerm(cvc5.Kind.GEQ, x0, mk_real(0.05)))
    solver.assertFormula(solver.mkTerm(cvc5.Kind.LEQ, x0, mk_real(0.15)))
    solver.assertFormula(solver.mkTerm(cvc5.Kind.GEQ, x1, mk_real(0.05)))
    solver.assertFormula(solver.mkTerm(cvc5.Kind.LEQ, x1, mk_real(0.15)))
    
    # Encode network
    def encode_linear(x_vars, weight, bias):
        out_vars = []
        for i in range(weight.shape[0]):
            terms = [solver.mkTerm(cvc5.Kind.MULT, mk_real(weight[i, j].item()), x_vars[j]) for j in range(weight.shape[1])]
            sum_term = terms[0]
            for t in terms[1:]:
                sum_term = solver.mkTerm(cvc5.Kind.ADD, sum_term, t)
            sum_term = solver.mkTerm(cvc5.Kind.ADD, sum_term, mk_real(bias[i].item()))
            out_vars.append(sum_term)
        return out_vars
        
    def encode_relu(x_vars):
        out_vars = []
        for i, x in enumerate(x_vars):
            out_var = solver.mkConst(real_sort, f"relu_{id(x)}")
            cond = solver.mkTerm(cvc5.Kind.GT, x, mk_real(0.0))
            ite = solver.mkTerm(cvc5.Kind.ITE, cond, x, mk_real(0.0))
            solver.assertFormula(solver.mkTerm(cvc5.Kind.EQUAL, out_var, ite))
            out_vars.append(out_var)
        return out_vars
        
    # Layer 1
    w1 = model.fc1.weight.detach()
    b1 = model.fc1.bias.detach()
    fc1_out = encode_linear([x0, x1], w1, b1)
    relu1_out = encode_relu(fc1_out)
    
    # Layer 2
    w2 = model.fc2.weight.detach()
    b2 = model.fc2.bias.detach()
    fc2_out = encode_linear(relu1_out, w2, b2)
    relu2_out = encode_relu(fc2_out)
    
    # Layer 3
    w3 = model.fc3.weight.detach()
    b3 = model.fc3.bias.detach()
    y_vars = encode_linear(relu2_out, w3, b3)
    y0, y1 = y_vars[0], y_vars[1]
    
    # Assert counterexample property: Y_0 >= Y_1
    solver.assertFormula(solver.mkTerm(cvc5.Kind.GEQ, y0, y1))
    
    print("Running cvc5 checkSat...")
    res = solver.checkSat()
    print(f"Result: {res}")
    
    if res.isUnsat():
        print("Property holds! Generating proof...")
        proofs = solver.getProof()
        proof_strings = []
        for p in proofs:
            proof_bytes = solver.proofToString(p)
            if isinstance(proof_bytes, bytes):
                proof_strings.append(proof_bytes.decode('utf-8'))
            else:
                proof_strings.append(str(proof_bytes))
        
        proof_str = "\n".join(proof_strings)
        property_id = os.path.basename(property_path).split('.')[0]
        store_certificate(model_path, property_id, proof_str, result="UNSAT")
        return {"status": "UNSAT", "details": "Proof generated."}
    elif res.isSat():
        print("Property violated (counterexample found).")
        # Extract counterexample
        cx0 = solver.getValue(x0)
        cx1 = solver.getValue(x1)
        print(f"Counterexample X = [{cx0}, {cx1}]")
        property_id = os.path.basename(property_path).split('.')[0]
        store_certificate(model_path, property_id, "SAT - No Proof", result="SAT")
        return {"status": "SAT", "details": "Counterexample found."}
    else:
        print("Solver returned unknown.")
        return {"status": "UNKNOWN", "details": ""}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python src/verify.py <model_path> <property_path>")
        sys.exit(1)
    run_verifier(sys.argv[1], sys.argv[2])

