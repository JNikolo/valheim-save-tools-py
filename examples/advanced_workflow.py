#!/usr/bin/env python3
"""
Advanced Workflow Examples

Demonstrates complex, real-world workflows combining multiple features.
"""

import sys
from pathlib import Path
from valheim_save_tools_py import ValheimSaveTools


def complete_world_cleanup():
    """Complete world cleanup: backup, clean, reset, restore bosses."""
    vst = ValheimSaveTools(verbose=True)
    
    print("Step 1: Creating backup...")
    backup = vst.to_json("world.db", "world_backup.json")
    print(f"✓ Backup created: {backup}\n")
    
    print("Step 2: Listing current global keys...")
    original_keys = vst.list_global_keys("world.db")
    boss_keys = [k for k in original_keys if k.startswith("defeated_")]
    print(f"✓ Found {len(boss_keys)} boss defeats\n")
    
    print("Step 3: Cleaning and resetting world...")
    result = (vst.process("world.db")
                 .clean_structures(threshold=30)
                 .reset_world()
                 .save("world_cleaned.db"))
    print(f"✓ World cleaned and reset: {result}\n")
    
    print("Step 4: Restoring boss defeats...")
    processor = vst.process("world_cleaned.db")
    for boss_key in boss_keys:
        processor.add_global_key(boss_key)
    result = processor.save("world.db")
    print(f"✓ Boss defeats restored: {result}\n")
    
    print("Complete! World is fresh but bosses remain defeated.")


def migrate_world_between_servers():
    """Migrate world data between servers."""
    vst = ValheimSaveTools()
    
    source_world = "server1_world.db"
    target_world = "server2_world.db"
    
    print("Step 1: Export source world to JSON...")
    json_export = vst.to_json(source_world, "world_transfer.json")
    print(f"✓ Exported: {json_export}\n")
    
    print("Step 2: Clean structures before transfer...")
    result = (vst.process(source_world)
                 .clean_structures(threshold=25)
                 .to_json("world_transfer_cleaned.json"))
    print(f"✓ Cleaned export: {result}\n")
    
    print("Step 3: Import to target server...")
    imported = vst.from_json("world_transfer_cleaned.json", target_world)
    print(f"✓ Imported to: {imported}\n")
    
    print("Migration complete!")


def batch_process_multiple_worlds():
    """Process multiple world files with different operations."""
    vst = ValheimSaveTools()
    
    worlds = [
        ("creative_world.db", {"clean": True, "threshold": 50, "reset": True}),
        ("survival_world.db", {"clean": True, "threshold": 25, "reset": False}),
        ("test_world.db", {"clean": True, "threshold": 100, "reset": True}),
    ]
    
    for world_file, options in worlds:
        print(f"\nProcessing {world_file}...")
        
        processor = vst.process(world_file)
        
        if options.get("clean"):
            processor.clean_structures(threshold=options["threshold"])
            print(f"  ✓ Cleaned (threshold: {options['threshold']})")
        
        if options.get("reset"):
            processor.reset_world()
            print(f"  ✓ Reset")
        
        output = f"processed_{world_file}"
        processor.save(output)
        print(f"  ✓ Saved to: {output}")


def create_world_variants():
    """Create multiple variants of a world with different settings."""
    vst = ValheimSaveTools()
    
    base_world = "world.db"
    
    variants = [
        {
            "name": "easy",
            "bosses": ["defeated_eikthyr", "defeated_gdking"],
            "threshold": 50
        },
        {
            "name": "medium",
            "bosses": ["defeated_eikthyr"],
            "threshold": 25
        },
        {
            "name": "hard",
            "bosses": [],
            "threshold": 10
        }
    ]
    
    for variant in variants:
        print(f"\nCreating '{variant['name']}' variant...")
        
        processor = vst.process(base_world)
        processor.clean_structures(threshold=variant["threshold"])
        processor.reset_world()
        
        for boss in variant["bosses"]:
            processor.add_global_key(boss)
        
        output = f"world_{variant['name']}.db"
        processor.save(output)
        print(f"✓ Created: {output}")


def world_analysis_and_optimization():
    """Analyze world and optimize based on findings."""
    vst = ValheimSaveTools()
    
    world_file = "world.db"
    
    print("Step 1: Analyzing world...")
    keys = vst.list_global_keys(world_file)
    boss_keys = [k for k in keys if k.startswith("defeated_")]
    
    print(f"  Total global keys: {len(keys)}")
    print(f"  Boss defeats: {len(boss_keys)}")
    print(f"  Other keys: {len(keys) - len(boss_keys)}\n")
    
    print("Step 2: Creating pre-optimization backup...")
    backup = vst.to_json(world_file, "pre_optimization.json")
    print(f"✓ Backup: {backup}\n")
    
    print("Step 3: Optimizing world...")
    # Determine threshold based on boss progression
    threshold = 50 if len(boss_keys) >= 4 else 25
    
    with vst.process(world_file) as processor:
        processor.clean_structures(threshold=threshold)
    
    print(f"✓ Optimized with threshold {threshold}\n")
    
    print("Step 4: Creating post-optimization backup...")
    post_backup = vst.to_json(world_file, "post_optimization.json")
    print(f"✓ Backup: {post_backup}\n")
    
    print("Optimization complete!")


def progressive_world_reset():
    """Reset world progressively, preserving certain milestones."""
    vst = ValheimSaveTools()
    
    milestones = [
        ("stage1_eikthyr.db", ["defeated_eikthyr"]),
        ("stage2_elder.db", ["defeated_eikthyr", "defeated_gdking"]),
        ("stage3_bonemass.db", ["defeated_eikthyr", "defeated_gdking", "defeated_bonemass"]),
        ("stage4_moder.db", ["defeated_eikthyr", "defeated_gdking", "defeated_bonemass", "defeated_dragon"]),
        ("stage5_yagluth.db", ["defeated_eikthyr", "defeated_gdking", "defeated_bonemass", "defeated_dragon", "defeated_goblinking"]),
    ]
    
    base_world = "world.db"
    
    for filename, bosses in milestones:
        print(f"\nCreating {filename}...")
        
        processor = vst.process(base_world)
        processor.clean_structures(threshold=30)
        processor.reset_world()
        
        for boss in bosses:
            processor.add_global_key(boss)
        
        processor.save(filename)
        print(f"✓ Created with {len(bosses)} boss(es) defeated")


def error_recovery_workflow():
    """Demonstrate error recovery and validation."""
    vst = ValheimSaveTools()
    
    world_file = "world.db"
    
    print("Step 1: Validating file...")
    if not ValheimSaveTools.is_db_file(world_file):
        print(f"✗ Error: {world_file} is not a valid .db file")
        return
    print(f"✓ {world_file} is valid\n")
    
    print("Step 2: Creating safety backup...")
    try:
        backup = vst.to_json(world_file, "safety_backup.json")
        print(f"✓ Backup created: {backup}\n")
    except Exception as e:
        print(f"✗ Backup failed: {e}")
        return
    
    print("Step 3: Attempting risky operation...")
    try:
        with vst.process(world_file) as processor:
            processor.clean_structures(threshold=100)  # Aggressive
            processor.reset_world()
        print("✓ Operation completed\n")
    except Exception as e:
        print(f"✗ Operation failed: {e}")
        print("Step 4: Restoring from backup...")
        vst.from_json(backup, world_file)
        print("✓ Restored from backup\n")
    
    print("Workflow complete!")


def context_manager_complex_workflow():
    """Complex workflow using context manager."""
    vst = ValheimSaveTools(verbose=False)
    
    # Get original state
    original_keys = vst.list_global_keys("world.db")
    print(f"Original state: {len(original_keys)} global keys\n")
    
    # Process with automatic cleanup
    with vst.process("world.db") as processor:
        print("Processing world...")
        processor.clean_structures(threshold=30)
        processor.reset_world()
        processor.add_global_key("defeated_eikthyr")
        processor.add_global_key("defeated_gdking")
        processor.add_global_key("KilledTroll")
    
    # Verify new state
    new_keys = vst.list_global_keys("world.db")
    print(f"\nNew state: {len(new_keys)} global keys")
    print("Keys added:", [k for k in new_keys if k not in original_keys])


def batch_convert_and_backup():
    """Batch convert all worlds and create organized backups."""
    vst = ValheimSaveTools()
    
    from datetime import datetime
    import shutil
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups_{timestamp}")
    backup_dir.mkdir(exist_ok=True)
    
    world_dir = Path("./worlds")
    
    print(f"Creating backups in {backup_dir}/\n")
    
    for db_file in world_dir.glob("*.db"):
        print(f"Processing {db_file.name}...")
        
        # Convert to JSON for backup
        json_name = f"{db_file.stem}_backup.json"
        json_backup = vst.to_json(str(db_file))
        
        # Move to backup directory
        shutil.move(json_backup, backup_dir / json_name)
        print(f"✓ Backed up to {backup_dir / json_name}")
    
    print(f"\nAll backups created in {backup_dir}/")


def main():
    """Run all advanced workflow examples."""
    print("=" * 60)
    print("Advanced Workflow Examples")
    print("=" * 60)
    
    examples = [
        ("Complete world cleanup", complete_world_cleanup),
        ("Migrate world between servers", migrate_world_between_servers),
        ("Batch process multiple worlds", batch_process_multiple_worlds),
        ("Create world variants", create_world_variants),
        ("World analysis and optimization", world_analysis_and_optimization),
        ("Progressive world reset", progressive_world_reset),
        ("Error recovery workflow", error_recovery_workflow),
        ("Context manager complex workflow", context_manager_complex_workflow),
        ("Batch convert and backup", batch_convert_and_backup),
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
        workflow = sys.argv[1]
        
        workflows = {
            "cleanup": complete_world_cleanup,
            "migrate": migrate_world_between_servers,
            "batch": batch_process_multiple_worlds,
            "variants": create_world_variants,
            "analyze": world_analysis_and_optimization,
            "progressive": progressive_world_reset,
            "recovery": error_recovery_workflow,
            "context": context_manager_complex_workflow,
            "backup": batch_convert_and_backup,
        }
        
        if workflow in workflows:
            print(f"Running: {workflow}")
            print("=" * 60)
            workflows[workflow]()
        else:
            print(f"Unknown workflow: {workflow}")
            print(f"Available: {', '.join(workflows.keys())}")
    else:
        print("Advanced Workflow Examples")
        print("=" * 60)
        print("Usage: python advanced_workflow.py <workflow>")
        print("\nAvailable workflows:")
        print("  cleanup     - Complete world cleanup with backup")
        print("  migrate     - Migrate world between servers")
        print("  batch       - Batch process multiple worlds")
        print("  variants    - Create world variants")
        print("  analyze     - Analyze and optimize world")
        print("  progressive - Progressive world reset")
        print("  recovery    - Error recovery workflow")
        print("  context     - Complex context manager workflow")
        print("  backup      - Batch convert and backup")
        print("\nExample:")
        print("  python advanced_workflow.py cleanup")
