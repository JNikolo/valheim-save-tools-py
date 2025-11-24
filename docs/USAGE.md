---
layout: default
title: Usage Guide
nav_order: 3
---

# Usage Guide

Detailed usage patterns and examples for Valheim Save Tools Python API.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Usage Patterns](#usage-patterns)
- [File Types](#file-types)
- [Item Parsing](#item-parsing)
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

# File conversion - returns parsed data
data = vst.to_json("world.db")
print(f"Version: {data['version']}")

# Also save to file
data = vst.to_json("world.db", "backup.json")
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

# Process and export to JSON - returns data
data = (vst.process("world.db")
           .clean_structures()
           .reset_world()
           .to_json("cleaned_world.json"))

print(f"Processed world has {len(data.get('globalKeys', []))} keys")

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

## Item Parsing

Parse and analyze Valheim inventory and item data from base64-encoded binary format.

### Basic Item Parsing

```python
from valheim_save_tools_py import parse_items_from_base64

# Parse inventory data (typically from JSON save files)
base64_data = "AQAAAAIAAAAKQXhlQnJvbnpl..."
items = parse_items_from_base64(base64_data)

# Display all items
for i, item in enumerate(items, 1):
    print(f"{i}. {item['name']}")
    print(f"   Stack: {item['stack']}")
    print(f"   Durability: {item['durability']:.1f}%")
    print(f"   Quality: {item['quality']}")
    print(f"   Position: ({item['pos_x']}, {item['pos_y']})")
    if item['equipped']:
        print(f"   [EQUIPPED]")
    if item['crafter_name']:
        print(f"   Crafted by: {item['crafter_name']}")
```

### Extract Item Data from Save Files

```python
from valheim_save_tools_py import ValheimSaveTools, parse_items_from_base64

vst = ValheimSaveTools()

# Convert character file to JSON
char_data = vst.to_json("MyCharacter.fch")

# Extract and parse inventory (if available in the JSON)
if 'inventory' in char_data:
    inventory_b64 = char_data['inventory']
    items = parse_items_from_base64(inventory_b64)

    print(f"Character has {len(items)} items")

    # List equipped gear
    equipped = [item for item in items if item['equipped']]
    print("\nEquipped items:")
    for item in equipped:
        print(f"  - {item['name']} (Quality {item['quality']})")
```

### Filter and Analyze Items

```python
from valheim_save_tools_py import parse_items_from_base64

items = parse_items_from_base64(base64_data)

# Find all weapons
weapons = [item for item in items if any(
    w in item['name'] for w in ['Sword', 'Axe', 'Bow', 'Spear', 'Mace']
)]

# Find damaged items
damaged = [item for item in items if item['durability'] < 50.0]

# Find high-quality items
high_quality = [item for item in items if item['quality'] >= 4]

# Calculate total weight (example - you'd need item weights)
stacks = sum(item['stack'] for item in items)
print(f"Total item stacks: {stacks}")

# Find items by crafter
player_crafted = [item for item in items if item['crafter_name'] == 'PlayerName']
```

### Inventory Statistics

```python
from valheim_save_tools_py import parse_items_from_base64
from collections import Counter

items = parse_items_from_base64(base64_data)

# Count item types
item_counts = Counter(item['name'] for item in items)
print("\nInventory breakdown:")
for item_name, count in item_counts.most_common():
    print(f"  {item_name}: {count}")

# Equipment analysis
equipped_count = sum(1 for item in items if item['equipped'])
total_durability = sum(item['durability'] for item in items if item['durability'] > 0)
avg_durability = total_durability / len([i for i in items if i['durability'] > 0])

print(f"\nStats:")
print(f"  Total items: {len(items)}")
print(f"  Equipped: {equipped_count}")
print(f"  Average durability: {avg_durability:.1f}%")

# Quality distribution
quality_counts = Counter(item['quality'] for item in items)
print("\nQuality levels:")
for quality in sorted(quality_counts.keys()):
    print(f"  Level {quality}: {quality_counts[quality]} items")
```

### Advanced: Custom Binary Parsing

For custom parsing needs, use the `ValheimItemReader` class directly:

```python
from valheim_save_tools_py import ValheimItemReader
import base64

# Decode base64
binary_data = base64.b64decode(base64_string)

# Create reader
reader = ValheimItemReader(binary_data)

# Read header manually
version = reader.read_int32()
num_items = reader.read_int32()

print(f"Data version: {version}")
print(f"Item count: {num_items}")

# Read items with custom logic
items = []
for i in range(num_items):
    try:
        item = reader.read_item()

        # Custom filtering during parsing
        if item['quality'] >= 3:  # Only high-quality items
            items.append(item)
    except Exception as e:
        print(f"Error reading item {i}: {e}")
        break

print(f"Found {len(items)} high-quality items")
```

### Item Data Structure

Each parsed item contains:

```python
{
    'name': 'SwordIron',          # Item ID/name
    'stack': 1,                    # Quantity in stack
    'durability': 75.5,            # Current durability
    'pos_x': 3,                    # Inventory X position
    'pos_y': 1,                    # Inventory Y position
    'equipped': True,              # Is currently equipped
    'quality': 2,                  # Quality/upgrade level
    'variant': 0,                  # Item variant
    'crafter_id': 987654321,       # Crafter's player ID
    'crafter_name': 'Warrior'      # Crafter's name
}
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
