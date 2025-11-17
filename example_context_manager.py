#!/usr/bin/env python3
"""Example demonstrating context manager pattern for automatic cleanup."""

from valheim_save_tools_py import ValheimSaveTools

def main():
    # Initialize the tool
    vst = ValheimSaveTools(verbose=True)
    
    # Example 1: Basic context manager usage
    print("Example 1: Clean structures with context manager")
    print("-" * 50)
    with vst.process("world.db") as processor:
        processor.clean_structures(threshold=30)
    # Operations executed and original file updated automatically
    # Temp files cleaned up automatically
    print("File processed and cleaned up!\n")
    
    # Example 2: Multiple operations with automatic cleanup
    print("Example 2: Multiple operations")
    print("-" * 50)
    with vst.process("world.db") as processor:
        processor.clean_structures()
        processor.reset_world()
        processor.add_global_key("defeated_eikthyr")
    print("All operations completed!\n")
    
    # Example 3: Method chaining in context manager
    print("Example 3: Chained operations")
    print("-" * 50)
    with vst.process("world.db") as processor:
        processor.clean_structures(threshold=25) \
                 .reset_world() \
                 .add_global_key("defeated_gdking") \
                 .add_global_key("defeated_bonemass")
    print("Chained operations completed!\n")
    
    # Example 4: Automatic cleanup on error
    print("Example 4: Cleanup even on error")
    print("-" * 50)
    try:
        with vst.process("world.db") as processor:
            processor.clean_structures()
            # Even if an error occurs here, temp files are cleaned up
            raise ValueError("Simulated error")
    except ValueError as e:
        print(f"Error occurred: {e}")
        print("But temp files were still cleaned up!\n")
    
    # Example 5: No explicit save() needed
    print("Example 5: Comparison with explicit save()")
    print("-" * 50)
    
    # Without context manager - explicit save
    print("Without context manager:")
    result = vst.process("world.db") \
                .clean_structures() \
                .save("output.db")
    print(f"  Saved to: {result}")
    
    # With context manager - automatic save to original
    print("With context manager:")
    with vst.process("world.db") as processor:
        processor.clean_structures()
    print("  Automatically overwrote: world.db\n")
    
    # Example 6: Benefits of context manager
    print("Benefits of Context Manager:")
    print("-" * 50)
    print("✓ Automatic temp file cleanup")
    print("✓ Guaranteed cleanup even on exceptions")
    print("✓ Cleaner code - no need to call save()")
    print("✓ Automatically overwrites original file")
    print("✓ Pythonic 'with' statement pattern")
    print("✓ Resource management best practice")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("This example demonstrates the context manager pattern.")
        print("Usage: python example_context_manager.py <world.db>")
        print("\nShowing example code without executing:")
        print(__doc__)
        with open(__file__) as f:
            print(f.read())
    else:
        main()
