#!/usr/bin/env python3
"""
Global Keys Management Examples

Demonstrates managing global keys (boss defeats, events, etc.) in Valheim world files.
"""

import sys
from valheim_save_tools_py import ValheimSaveTools


def list_all_keys():
    """List all global keys in a world."""
    vst = ValheimSaveTools()
    
    keys = vst.list_global_keys("world.db")
    
    print("Current global keys:")
    for key in keys:
        print(f"  - {key}")
    
    return keys


def add_boss_defeats():
    """Add all boss defeat keys."""
    vst = ValheimSaveTools()
    
    bosses = [
        "defeated_eikthyr",
        "defeated_gdking",
        "defeated_bonemass",
        "defeated_dragon",
        "defeated_goblinking",
        "defeated_queen"
    ]
    
    for boss in bosses:
        vst.add_global_key("world.db", boss)
        print(f"✓ Added: {boss}")


def add_boss_defeats_chained():
    """Add all boss defeats using method chaining."""
    vst = ValheimSaveTools()
    
    result = (vst.process("world.db")
                 .add_global_key("defeated_eikthyr")
                 .add_global_key("defeated_gdking")
                 .add_global_key("defeated_bonemass")
                 .add_global_key("defeated_dragon")
                 .add_global_key("defeated_goblinking")
                 .add_global_key("defeated_queen")
                 .save("all_bosses_defeated.db"))
    
    print(f"All bosses defeated! Saved to: {result}")


def remove_specific_key():
    """Remove a specific global key."""
    vst = ValheimSaveTools()
    
    vst.remove_global_key("world.db", "defeated_eikthyr")
    print("Removed: defeated_eikthyr")


def reset_all_bosses():
    """Remove all boss defeat keys."""
    vst = ValheimSaveTools()
    
    bosses = [
        "defeated_eikthyr",
        "defeated_gdking",
        "defeated_bonemass",
        "defeated_dragon",
        "defeated_goblinking",
        "defeated_queen"
    ]
    
    for boss in bosses:
        vst.remove_global_key("world.db", boss)
        print(f"✓ Removed: {boss}")


def clear_all_keys():
    """Clear all global keys from a world."""
    vst = ValheimSaveTools()
    
    # Get current keys before clearing
    keys_before = vst.list_global_keys("world.db")
    print(f"Keys before: {len(keys_before)}")
    
    # Clear all
    vst.clear_all_global_keys("world.db")
    print("All global keys cleared!")
    
    # Verify
    keys_after = vst.list_global_keys("world.db")
    print(f"Keys after: {len(keys_after)}")


def check_specific_boss():
    """Check if a specific boss has been defeated."""
    vst = ValheimSaveTools()
    
    keys = vst.list_global_keys("world.db")
    
    bosses_to_check = [
        ("Eikthyr", "defeated_eikthyr"),
        ("The Elder", "defeated_gdking"),
        ("Bonemass", "defeated_bonemass"),
        ("Moder", "defeated_dragon"),
        ("Yagluth", "defeated_goblinking"),
        ("The Queen", "defeated_queen")
    ]
    
    print("Boss Status:")
    for name, key in bosses_to_check:
        status = "✓ Defeated" if key in keys else "✗ Not defeated"
        print(f"  {name:15s} {status}")


def add_tutorial_keys():
    """Add useful tutorial/progression keys."""
    vst = ValheimSaveTools()
    
    tutorial_keys = [
        "defeated_eikthyr",     # Unlocks antler pickaxe
        "KilledTroll",          # Troll kill achievement
        "killed_surtling",      # Surtling kill
    ]
    
    for key in tutorial_keys:
        vst.add_global_key("world.db", key)
        print(f"✓ Added: {key}")


def backup_and_modify():
    """Create a backup before modifying global keys."""
    vst = ValheimSaveTools()
    
    # Create JSON backup
    backup = vst.to_json("world.db", "world_backup.json")
    print(f"Created backup: {backup}")
    
    # Modify the world
    vst.add_global_key("world.db", "defeated_eikthyr")
    print("Added boss defeat key")
    
    # List current keys
    keys = vst.list_global_keys("world.db")
    print(f"Current keys: {len(keys)}")


def context_manager_example():
    """Use context manager for key management."""
    vst = ValheimSaveTools()
    
    with vst.process("world.db") as processor:
        processor.add_global_key("defeated_eikthyr") \
                 .add_global_key("defeated_gdking") \
                 .add_global_key("defeated_bonemass")
    
    print("Boss keys added with automatic cleanup!")


def main():
    """Run all global keys examples."""
    print("=" * 60)
    print("Global Keys Management Examples")
    print("=" * 60)
    
    examples = [
        ("List all global keys", list_all_keys),
        ("Add all boss defeats", add_boss_defeats),
        ("Add boss defeats (chained)", add_boss_defeats_chained),
        ("Remove specific key", remove_specific_key),
        ("Reset all bosses", reset_all_bosses),
        ("Clear all keys", clear_all_keys),
        ("Check boss status", check_specific_boss),
        ("Add tutorial keys", add_tutorial_keys),
        ("Backup and modify", backup_and_modify),
        ("Context manager example", context_manager_example),
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
        vst = ValheimSaveTools(verbose=True)
        
        print(f"Global keys in {world_file}:")
        print("=" * 60)
        
        keys = vst.list_global_keys(world_file)
        for i, key in enumerate(keys, 1):
            print(f"{i:3d}. {key}")
        
        print(f"\nTotal: {len(keys)} keys")
    else:
        print("Global Keys Management Examples")
        print("=" * 60)
        print("Usage: python global_keys.py <world.db>")
        print("\nExample:")
        print("  python global_keys.py world.db")
        print("\nCommon global keys:")
        print("  - defeated_eikthyr    (Eikthyr)")
        print("  - defeated_gdking     (The Elder)")
        print("  - defeated_bonemass   (Bonemass)")
        print("  - defeated_dragon     (Moder)")
        print("  - defeated_goblinking (Yagluth)")
        print("  - defeated_queen      (The Queen)")
