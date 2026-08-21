import sys
import platform

def check_import(module_name):
    try:
        __import__(module_name)
        return "PASS", ""
    except ImportError as e:
        return "FAIL", str(e)
    except Exception as e:
        return "FAIL", f"Unexpected error: {str(e)}"

def main():
    print("="*60)
    print("Neuro-Symbolic MLOps Toolchain Verification")
    print("="*60)
    print(f"Python Version: {platform.python_version()}")
    print(f"OS: {platform.system()} {platform.release()}")
    print("-" * 60)
    print(f"{'Tool':<20} | {'Status':<10} | {'Details'}")
    print("-" * 60)
    
    tools = {
        'PyTorch': 'torch',
        'NumPy': 'numpy',
        'PyTest': 'pytest',
        'ONNX': 'onnx',
        'CVC5': 'cvc5',
        'Marabou': 'maraboupy'
    }
    
    for tool_name, module_name in tools.items():
        status, details = check_import(module_name)
        # For Marabou, check if it's not installed via pip and offer tips
        if tool_name == 'Marabou' and status == 'FAIL':
            details += " (May need to be built from source on Windows)"
        
        print(f"{tool_name:<20} | {status:<10} | {details}")
        
    print("="*60)

if __name__ == "__main__":
    main()
