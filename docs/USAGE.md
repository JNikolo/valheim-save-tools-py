# Usage Guide

Detailed usage patterns and examples for Valheim Save Tools Python API.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Usage Patterns](#usage-patterns)
- [File Types](#file-types)
- [Common Workflows](#common-workflows)
- [Best Practices](#best-practices)
- [Tips and Tricks](#tips-and-tricks)

---

## Basic Usage

### Installation and Setup

```python
from valheim_save_tools_py import ValheimSaveTools

# Basic initialization (auto-detects JAR and Java)
vst = ValheimSaveTools()

# With verbose output for debugging
vst = ValheimSaveTools(verbose=True)

# With custom paths
vst = ValheimSaveTools(
    jar_path="/path/to/valheim-save-tools.jar",
    java_path="/path/to/java"
)
```

---

## Usage Patterns

The API supports three main usage patterns:

### Pattern 1: Direct Method Calls

Simple, straightforward operations:

```python
vst = ValheimSaveTools()

# File conversion
vst.to_json("world.db", "backup.json")
vst.from_json("backup.json", "world_restored.db")

# Global keys
keys = vst.list_global_keys("world.db")
vst.add_global_key("world.db", "defeated_gdking")
vst.remove_global_key("world.db", "defeated_eikthyr")
vst.clear_all_global_keys("world.db")

# Structure operations
vst.clean_structures("world.db", threshold=25)
vst.reset_world("world.db")
```

**When to use:**

- Simple one-off operations
- Scripts with linear logic
- Quick file conversions

### Pattern 2: Method Chaining (Builder Pattern)

Chain multiple operations elegantly:

```python
vst = ValheimSaveTools()

# Process and save
result = (vst.process("world.db")
             .clean_structures(threshold=30)
             .reset_world()
             .add_global_key("defeated_eikthyr")
             .add_global_key("defeated_gdking")
             .save("cleaned_world.db"))

# Process and export to JSON
json_file = (vst.process("world.db")
                .clean_structures()
                .reset_world()
                .to_json("cleaned_world.json"))

# Multiple operations, overwrite original
(vst.process("world.db")
    .clean_structures(threshold=40)
    .reset_world()
    .save())  # No output = overwrite original
```

**When to use:**

- Multiple operations on same file
- Complex transformations
- When you need intermediate results

### Pattern 3: Context Manager

Automatic cleanup and resource management:

```python
vst = ValheimSaveTools()

# Automatically processes and saves to original file
with vst.process("world.db") as processor:
    processor.clean_structures(threshold=30)
    processor.reset_world()
    processor.add_global_key("defeated_eikthyr")
# Temp files cleaned up automatically!

# Chaining also works in context manager
with vst.process("world.db") as processor:
    processor.clean_structures() \
             .reset_world() \
             .add_global_key("defeated_gdking")
```

**When to use:**

- Guaranteed cleanup of temp files
- Exception-safe operations
- Pythonic resource management
- When modifying original file in-place

---

## File Types

### World Data Files (`.db`)

Contains actual world data including terrain, structures, items, etc.

```python
# Convert to JSON for backup
vst.to_json("Dedicated.db", "world_backup.json")

# Clean structures
vst.clean_structures("Dedicated.db", threshold=30)

# Reset world
vst.reset_world("Dedicated.db")

# Manage global keys
vst.add_global_key("Dedicated.db", "defeated_eikthyr")
```

### World Metadata Files (`.fwl`)

Contains world metadata (name, seed, etc.)

```python
# Convert to JSON to inspect
vst.to_json("Dedicated.fwl", "metadata.json")

# Restore from JSON
vst.from_json("metadata.json", "Dedicated.fwl")
```

### Character Files (`.fch`)

Contains character data (inventory, skills, etc.)

```python
# Backup character
vst.to_json("MyCharacter.fch", "character_backup.json")

# Restore character
vst.from_json("character_backup.json", "MyCharacter.fch")
```

### JSON Files

Human-readable converted format:

```python
# Convert any save file to JSON
vst.to_json("world.db")      # -> world.json
vst.to_json("world.fwl")     # -> world.json
vst.to_json("character.fch") # -> character.json

# Convert back to binary
vst.from_json("world.json")  # -> world.db
```

---

## Common Workflows

### Workflow 1: Backup Before Modify

Always create backups before modifying save files:

```python
vst = ValheimSaveTools()

# 1. Create backup
backup = vst.to_json("world.db", "world_backup.json")
print(f"Backup created: {backup}")

# 2. Modify the world
vst.clean_structures("world.db", threshold=30)
vst.reset_world("world.db")

# 3. If something goes wrong, restore:
# vst.from_json("world_backup.json", "world.db")
```

### Workflow 2: Complete World Cleanup

Clean and reset world while preserving boss defeats:

```python
vst = ValheimSaveTools()

# 1. Get current boss defeats
boss_keys = [k for k in vst.list_global_keys("world.db")
             if k.startswith("defeated_")]

# 2. Clean and reset
with vst.process("world.db") as p:
    p.clean_structures(threshold=30)
    p.reset_world()

    # 3. Restore boss defeats
    for boss in boss_keys:
        p.add_global_key(boss)
```

### Workflow 3: Batch Process Multiple Worlds

```python
from pathlib import Path

vst = ValheimSaveTools()

world_dir = Path("./worlds")
for db_file in world_dir.glob("*.db"):
    print(f"Processing {db_file.name}...")

    # Backup
    vst.to_json(str(db_file), str(db_file.with_suffix('.json')))

    # Clean
    vst.clean_structures(str(db_file), threshold=25)

    print(f"✓ {db_file.name} processed")
```

### Workflow 4: Create World Variants

```python
vst = ValheimSaveTools()

base_world = "world.db"

# Easy mode - all bosses defeated
(vst.process(base_world)
    .reset_world()
    .add_global_key("defeated_eikthyr")
    .add_global_key("defeated_gdking")
    .add_global_key("defeated_bonemass")
    .save("world_easy.db"))

# Hard mode - no bosses defeated
(vst.process(base_world)
    .reset_world()
    .clear_all_global_keys()
    .save("world_hard.db"))
```

### Workflow 5: Migration Between Servers

```python
vst = ValheimSaveTools()

# Export from source server
source = "server1_world.db"
vst.to_json(source, "world_transfer.json")

# Clean before transfer
(vst.process(source)
    .clean_structures(threshold=50)
    .to_json("world_transfer_cleaned.json"))

# Import to target server
target = "server2_world.db"
vst.from_json("world_transfer_cleaned.json", target)
```

---

## Best Practices

### 1. Always Create Backups

```python
# Good
vst.to_json("world.db", "backup.json")
vst.clean_structures("world.db")

# Even better - use context manager
backup = vst.to_json("world.db", "backup_before_cleanup.json")
with vst.process("world.db") as p:
    p.clean_structures()
```

### 2. Validate Files Before Processing

```python
from valheim_save_tools_py import ValheimSaveTools

# Validate before processing
if not ValheimSaveTools.is_db_file("world.db"):
    print("Error: Not a valid .db file")
    exit(1)

vst = ValheimSaveTools()
vst.clean_structures("world.db")
```

### 3. Use Context Managers for Safety

```python
# Automatic cleanup even if errors occur
try:
    with vst.process("world.db") as p:
        p.clean_structures()
        p.reset_world()
except Exception as e:
    print(f"Error: {e}")
    # Temp files still cleaned up!
```

### 4. Start with Conservative Thresholds

```python
# Start conservative
vst.clean_structures("world.db", threshold=10)

# Gradually increase if needed
vst.clean_structures("world.db", threshold=25)  # Recommended
vst.clean_structures("world.db", threshold=50)  # Aggressive
```

### 5. Use Verbose Mode for Debugging

```python
# Enable verbose output during development/debugging
vst = ValheimSaveTools(verbose=True)
vst.clean_structures("world.db")

# Disable for production
vst = ValheimSaveTools(verbose=False)
```

---

## Tips and Tricks

### Tip 1: Check Boss Status

```python
vst = ValheimSaveTools()
keys = vst.list_global_keys("world.db")

bosses = {
    "Eikthyr": "defeated_eikthyr",
    "The Elder": "defeated_gdking",
    "Bonemass": "defeated_bonemass",
    "Moder": "defeated_dragon",
    "Yagluth": "defeated_goblinking",
    "The Queen": "defeated_queen"
}

print("Boss Status:")
for name, key in bosses.items():
    status = "✓" if key in keys else "✗"
    print(f"{status} {name}")
```

### Tip 2: Conditional Processing

```python
vst = ValheimSaveTools()
keys = vst.list_global_keys("world.db")

# Only clean if certain bosses defeated
if "defeated_dragon" in keys:
    print("Late game - aggressive cleaning")
    vst.clean_structures("world.db", threshold=50)
else:
    print("Early game - conservative cleaning")
    vst.clean_structures("world.db", threshold=10)
```

### Tip 3: Progressive Backups

```python
from datetime import datetime

vst = ValheimSaveTools()

# Create timestamped backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = f"world_backup_{timestamp}.json"
vst.to_json("world.db", backup)
print(f"Backup created: {backup}")
```

### Tip 4: Dry Run with JSON Export

```python
# Export to JSON to inspect before modifying
vst.to_json("world.db", "world_inspect.json")

# Inspect the JSON file manually
# ... review changes needed ...

# Then modify original
vst.clean_structures("world.db")
```

### Tip 5: Error Recovery

```python
vst = ValheimSaveTools()

try:
    # Create safety backup
    backup = vst.to_json("world.db", "safety_backup.json")

    # Risky operation
    vst.reset_world("world.db")

except Exception as e:
    print(f"Error occurred: {e}")
    print("Restoring from backup...")
    vst.from_json(backup, "world.db")
    print("Restored successfully")
```

---

## Troubleshooting

### Issue: "JAR file not found"

```python
# Solution: Specify JAR path explicitly
vst = ValheimSaveTools(jar_path="/path/to/valheim-save-tools.jar")
```

### Issue: "Java not found"

```python
# Solution: Specify Java path or install Java 17+
vst = ValheimSaveTools(java_path="/path/to/java")
```

### Issue: File not modified

```python
# Make sure you're using the right file type
# Global keys only work with .db files
if ValheimSaveTools.is_db_file("world.db"):
    vst.add_global_key("world.db", "defeated_eikthyr")
```

### Issue: Permission errors

Make sure:

1. Files are not read-only
2. You have write permissions
3. Files are not in use by Valheim
4. Backup files before modifying

---

See [examples/](../examples/) for complete working examples.
