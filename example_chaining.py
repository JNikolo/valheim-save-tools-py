#!/usr/bin/env python3
"""Example demonstrating the builder pattern for chaining operations."""

from valheim_save_tools_py import ValheimSaveTools
import sys

def main():
    # Initialize the tool
    try:
        input_file = sys.argv[1]
        vst = ValheimSaveTools(verbose=True)
        
        # Example 1: Chain structure cleaning and world reset
        print("Example 1: Clean structures and reset world")
        print("-" * 50)
        result = (vst.process(input_file)
                    .clean_structures(threshold=30)
                    .reset_world()
                    .save("cleaned_world.db"))
        print(f"Saved to: {result}\n")
        
        # Example 2: Add multiple global keys
        print("Example 2: Add multiple boss keys")
        print("-" * 50)
        result = (vst.process(input_file)
                    .add_global_key("defeated_eikthyr")
                    .add_global_key("defeated_gdking")
                    .add_global_key("defeated_bonemass")
                    .save("bosses_defeated.db"))
        print(f"Saved to: {result}\n")
        
        # Example 3: Complex workflow with JSON export
        print("Example 3: Clean, reset, and export to JSON")
        print("-" * 50)
        result = (vst.process(input_file)
                    .clean_structures(threshold=25)
                    .reset_world()
                    .add_global_key("defeated_eikthyr")
                    .to_json("cleaned_world.json"))
        print(f"Saved to: {result}\n")
        
        # Example 4: Overwrite original file
        print("Example 4: Clean and overwrite original")
        print("-" * 50)
        result = (vst.process(input_file)
                    .clean_structures()
                    .save())  # No output file = overwrite original
        print(f"Saved to: {result}\n")
        
        # Example 5: Just inspect the operations without executing
        print("Example 5: View queued operations")
        print("-" * 50)
        processor = (vst.process(input_file)
                        .clean_structures(threshold=40)
                        .remove_global_key("defeated_eikthyr")
                        .add_global_key("defeated_yagluth"))
        print(f"Processor: {processor}\n")
        # Call .save() when ready to execute
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("This example demonstrates the builder pattern API.")
        print("Usage: python example_chaining.py <world.db>")
        print("\nShowing example code without executing:")
        print(__doc__)
        with open(__file__) as f:
            print(f.read())
    else:
        main()
