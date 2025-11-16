#!/usr/bin/env python3
"""Quick test script."""

import sys
from valheim_save_tools_py import ValheimSaveTools

def main():
    input_args = sys.argv[1:] if len(sys.argv) > 1 else []
    print("=== Valheim Save Tools Python Wrapper Quick Test ===\n")
    try:
        print("✓ Import successful")
        
        # Initialize
        vst = ValheimSaveTools()
        print(f"✓ Found JAR at: {vst.jar_path}")
        print(f"✓ Found Java at: {vst.java_path}")
        
        # Run a command
        print("\n=== Running JAR command ===")
        if input_args:
            result = vst.run_command(*input_args, check=False)
        else:
            result = vst.run_command("--version", check=False)
        
        print(f"Exit code: {result.returncode}")
        print(f"\nOutput:\n{result.stdout}")
        if result.stderr:
            print(f"\nErrors:\n{result.stderr}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure:")
        print("1. JAR file is in src/valheim-save-tools-py/")
        print("2. Java is installed (java -version)")

if __name__ == "__main__":
    main()