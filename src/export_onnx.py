import torch
import os
from train import ToyNet

def main():
    model_path = os.path.join("models", "toy_model.pt")
    onnx_path = os.path.join("models", "toy_model.onnx")
    
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}. Please run train.py first.")
        return
        
    print(f"Loading model from {model_path}...")
    model = ToyNet()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # Create a dummy input tensor for tracing
    dummy_input = torch.randn(1, 2)
    
    print(f"Exporting to {onnx_path}...")
    torch.onnx.export(
        model,               # model being run
        dummy_input,         # model input (or a tuple for multiple inputs)
        onnx_path,           # where to save the model (can be a file or file-like object)
        export_params=True,  # store the trained parameter weights inside the model file
        opset_version=10,    # the ONNX version to export the model to
        do_constant_folding=True,  # whether to execute constant folding for optimization
        input_names = ['input'],   # the model's input names
        output_names = ['output'], # the model's output names
        dynamic_axes={'input' : {0 : 'batch_size'},    # variable length axes
                      'output' : {0 : 'batch_size'}}
    )
    print("Export complete.")

if __name__ == "__main__":
    main()
