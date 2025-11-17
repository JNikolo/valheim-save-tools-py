#!/usr/bin/env python3
"""
Clean and Reset Examples

Demonstrates cleaning structures and resetting worlds.
"""

import sys
from valheim_save_tools_py import ValheimSaveTools


def clean_structures_default():
    """Clean structures with default threshold (25)."""
    vst = ValheimSaveTools()
    
    vst.clean_structures("world.db")
    print("Cleaned structures with default threshold (25)")


def clean_structures_custom():
    """Clean structures with custom threshold."""
    vst = ValheimSaveTools()
    
    # More aggressive cleaning (larger threshold)
    vst.clean_structures("world.db", threshold=50)
    print("Cleaned structures with threshold 50")


def clean_structures_conservative():
    """Clean structures conservatively (smaller threshold)."""
    vst = ValheimSaveTools()
    
    # Conservative cleaning
    vst.clean_structures("world.db", threshold=10)
    print("Cleaned structures with threshold 10 (conservative)")


def reset_world_simple():
    """Reset world to initial state."""
    vst = ValheimSaveTools()
    
    vst.reset_world("world.db")
    print("World reset to initial state")


def clean_then_reset():
    """Clean structures then reset world."""
    vst = ValheimSaveTools()
    
    # Old way - separate calls
    vst.clean_structures("world.db", threshold=30)
    vst.reset_world("world.db")
    print("Cleaned and reset world (separate calls)")


def clean_and_reset_chained():
    """Clean and reset using method chaining."""
    vst = ValheimSaveTools()
    
    result = (vst.process("world.db")
                 .clean_structures(threshold=30)
                 .reset_world()
                 .save("cleaned_world.db"))
    
    print(f"Cleaned and reset! Saved to: {result}")


def clean_and_reset_context():
    """Clean and reset using context manager."""
    vst = ValheimSaveTools()
    
    with vst.process("world.db") as processor:
        processor.clean_structures(threshold=30)
        processor.reset_world()
    
    print("Cleaned and reset with automatic cleanup!")


def clean_reset_and_bosses():
    """Complete world reset with boss defeats added."""
    vst = ValheimSaveTools()
    
    result = (vst.process("world.db")
                 .clean_structures(threshold=25)
                 .reset_world()
                 .add_global_key("defeated_eikthyr")
                 .add_global_key("defeated_gdking")
                 .save("fresh_with_bosses.db"))
    
    print(f"Fresh world with boss defeats! Saved to: {result}")


def clean_and_export_json():
    """Clean structures and export to JSON."""
    vst = ValheimSaveTools()
    
    result = (vst.process("world.db")
                 .clean_structures(threshold=30)
                 .to_json("cleaned_world.json"))
    
    print(f"Cleaned and exported to JSON: {result}")


def batch_clean_worlds():
    """Clean all world files in a directory."""
    import os
    from pathlib import Path
    
    vst = ValheimSaveTools()
    world_dir = Path("./worlds")
    
    for db_file in world_dir.glob("*.db"):
        print(f"Cleaning {db_file.name}...")
        vst.clean_structures(str(db_file), threshold=30)
        print(f"✓ {db_file.name} cleaned")


def create_backup_before_cleaning():
    """Create JSON backup before cleaning."""
    vst = ValheimSaveTools()
    
    # Create backup
    backup = vst.to_json("world.db", "world_backup.json")
    print(f"Created backup: {backup}")
    
    # Clean the world
    vst.clean_structures("world.db", threshold=30)
    print("World cleaned")
    
    # If you need to restore:
    # vst.from_json("world_backup.json", "world.db")


def progressive_cleaning():
    """Try different cleaning thresholds."""
    vst = ValheimSaveTools()
    
    thresholds = [10, 25, 50, 100]
    
    for threshold in thresholds:
        output = f"world_threshold_{threshold}.db"
        
        result = (vst.process("world.db")
                     .clean_structures(threshold=threshold)
                     .save(output))
        
        print(f"✓ Threshold {threshold:3d} -> {output}")


def verbose_cleaning():
    """Clean with verbose output."""
    vst = ValheimSaveTools(verbose=True)
    
    vst.clean_structures("world.db", threshold=30)
    print("Cleaned with verbose output")


def main():
    """Run all clean and reset examples."""
    print("=" * 60)
    print("Clean and Reset Examples")
    print("=" * 60)
    
    examples = [
        ("Clean structures (default)", clean_structures_default),
        ("Clean structures (custom threshold)", clean_structures_custom),
        ("Clean structures (conservative)", clean_structures_conservative),
        ("Reset world", reset_world_simple),
        ("Clean then reset (separate)", clean_then_reset),
        ("Clean and reset (chained)", clean_and_reset_chained),
        ("Clean and reset (context)", clean_and_reset_context),
        ("Clean, reset, add bosses", clean_reset_and_bosses),
        ("Clean and export JSON", clean_and_export_json),
        ("Batch clean worlds", batch_clean_worlds),
        ("Backup before cleaning", create_backup_before_cleaning),
        ("Progressive cleaning", progressive_cleaning),
        ("Verbose cleaning", verbose_cleaning),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{i}. {name}")
        print("-" * 60)
        try:
            func()
        except Exception as e:
            print(f"Error: {e}")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run with actual file
        world_file = sys.argv[1]
        threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 25
        
        vst = ValheimSaveTools(verbose=True)
        
        print(f"Cleaning {world_file} with threshold {threshold}")
        print("=" * 60)
        
        vst.clean_structures(world_file, threshold=threshold)
        print(f"\n✓ Done! Structures cleaned.")
    else:
        print("Clean and Reset Examples")
        print("=" * 60)
        print("Usage: python clean_and_reset.py <world.db> [threshold]")
        print("\nExamples:")
        print("  python clean_and_reset.py world.db")
        print("  python clean_and_reset.py world.db 50")
        print("\nThreshold guidelines:")
        print("  - 10  : Very conservative (minimal cleanup)")
        print("  - 25  : Default (balanced)")
        print("  - 50  : Aggressive (more cleanup)")
        print("  - 100 : Very aggressive (maximum cleanup)")
