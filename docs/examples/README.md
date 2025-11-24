---
layout: default
title: Examples
nav_order: 4
---

# Examples Directory

This directory contains comprehensive examples demonstrating various usage patterns of the Valheim Save Tools Python API.

## Examples Overview

### 1. `convert.py` - File Conversion

Demonstrates converting between Valheim save formats (.db, .fwl, .fch) and JSON.

**Key features:**

- Auto-generated output filenames
- Explicit output filenames
- Batch conversion
- Verbose output

**Usage:**

```bash
python convert.py world.db
python convert.py world.json
python convert.py character.fch
```

### 2. `parse_items.py` - Item Parsing and Analysis

Shows how to parse and analyze Valheim inventory/item data from base64-encoded format.

**Key features:**

- Parse inventory data from base64
- Display item details
- Inventory statistics and analysis
- Filter items by category
- Find damaged items
- List equipped items
- Custom binary parsing

**Usage:**

```bash
python parse_items.py
```

### 3. `global_keys.py` - Global Keys Management

Shows how to manage global keys (boss defeats, events, etc.) in world files.

**Key features:**

- List all global keys
- Add/remove specific keys
- Add all boss defeats
- Check boss status
- Clear all keys
- Method chaining for multiple operations

**Usage:**

```bash
python global_keys.py world.db
```

### 4. `clean_and_reset.py` - Structure Cleaning and World Reset

Demonstrates cleaning structures and resetting worlds with different thresholds.

**Key features:**

- Default and custom thresholds
- Conservative vs aggressive cleaning
- World reset
- Chaining clean and reset operations
- Backup before operations
- Progressive cleaning with different thresholds

**Usage:**

```bash
python clean_and_reset.py world.db
python clean_and_reset.py world.db 50
```

### 5. `advanced_workflow.py` - Complex Workflows

Shows real-world, complex workflows combining multiple features.

**Key features:**

- Complete world cleanup with backup
- World migration between servers
- Batch processing multiple worlds
- Creating world variants
- World analysis and optimization
- Progressive world reset
- Error recovery patterns
- Context manager workflows
- Batch backup creation

**Usage:**

```bash
python advanced_workflow.py cleanup
python advanced_workflow.py migrate
python advanced_workflow.py batch
```

## Common Patterns

### Pattern 1: Simple Operation

```python
from valheim_save_tools_py import ValheimSaveTools

vst = ValheimSaveTools()
vst.clean_structures("world.db", threshold=30)
```

### Pattern 2: Method Chaining

```python
vst = ValheimSaveTools()
result = (vst.process("world.db")
             .clean_structures(threshold=30)
             .reset_world()
             .add_global_key("defeated_eikthyr")
             .save("cleaned_world.db"))
```

### Pattern 3: Context Manager

```python
vst = ValheimSaveTools()
with vst.process("world.db") as processor:
    processor.clean_structures(threshold=30)
    processor.reset_world()
# Automatic cleanup and save to original file
```

### Pattern 4: Backup Before Modify

```python
vst = ValheimSaveTools()

# Create backup
backup = vst.to_json("world.db", "backup.json")

# Modify
vst.clean_structures("world.db")

# Restore if needed
# vst.from_json("backup.json", "world.db")
```

## File Types

- **`.db`** - World data files
- **`.fwl`** - World metadata files
- **`.fch`** - Character files
- **`.json`** - Converted/exported files

## Common Global Keys

### Boss Defeats

- `defeated_eikthyr` - Eikthyr (The first boss)
- `defeated_gdking` - The Elder (Forest boss)
- `defeated_bonemass` - Bonemass (Swamp boss)
- `defeated_dragon` - Moder (Mountain boss)
- `defeated_goblinking` - Yagluth (Plains boss)
- `defeated_queen` - The Queen (Mistlands boss)

### Other Keys

- `KilledTroll` - Troll kill achievement
- `killed_surtling` - Surtling kill

## Threshold Guidelines

When using `clean_structures()`:

- **10** - Very conservative (minimal cleanup)
- **25** - Default (balanced) ⭐ Recommended
- **50** - Aggressive (more cleanup)
- **100** - Very aggressive (maximum cleanup)

## Running Examples

All examples can be run in two modes:

1. **Interactive mode** (without arguments) - Shows example code
2. **Execution mode** (with arguments) - Actually processes files

Example:

```bash
# Show example code
python convert.py

# Actually convert a file
python convert.py world.db
```

## Tips

1. **Always backup** before modifying world files
2. **Use context manager** for automatic cleanup
3. **Start with conservative thresholds** (10-25) when cleaning
4. **Test on a copy** of your world first
5. **Use verbose mode** (`verbose=True`) for troubleshooting
6. **Export to JSON** for human-readable backups

## See Also

- `../BUILDER_PATTERN.md` - Builder pattern documentation
- `../README.md` - Main project documentation
- `../tests/` - Unit tests for reference
