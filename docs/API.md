---
layout: default
title: API Reference
nav_order: 2
---

# API Reference

Complete API documentation for Valheim Save Tools Python API.

## Table of Contents

- [Core Class](#core-class)
- [File Conversion Methods](#file-conversion-methods)
- [Item Parsing](#item-parsing)
- [Global Keys Methods](#global-keys-methods)
- [Structure Processing Methods](#structure-processing-methods)
- [Builder Pattern](#builder-pattern)
- [File Detection Methods](#file-detection-methods)
- [Error Handling](#error-handling)

---

## Core Class

### `ValheimSaveTools`

```python
ValheimSaveTools(
    jar_path: Optional[str] = None,
    java_path: Optional[str] = None,
    verbose: bool = False,
    fail_on_unsupported_version: bool = False,
    skip_resolve_names: bool = False
)
```

Main API class for interacting with Valheim save files.

**Parameters:**

- `jar_path` (str, optional): Path to JAR file (auto-detected if bundled)
- `java_path` (str, optional): Path to Java executable (auto-detected)
- `verbose` (bool): Enable verbose output (default: False)
- `fail_on_unsupported_version` (bool): Fail on unsupported file versions (default: False)
- `skip_resolve_names` (bool): Skip resolving player names (default: False)

**Example:**

```python
from valheim_save_tools_py import ValheimSaveTools

# Basic initialization
vst = ValheimSaveTools()

# With verbose output
vst = ValheimSaveTools(verbose=True)

# With custom JAR path
vst = ValheimSaveTools(jar_path="/path/to/valheim-save-tools.jar")
```

---

## File Conversion Methods

### `to_json()`

```python
to_json(
    input_file: Union[str, BinaryIO],
    output_file: Union[str, BinaryIO, None] = None
) -> Dict
```

Convert Valheim save file to JSON format and return parsed data.

**Supported formats:** `.db`, `.fwl`, `.fch`

**Parameters:**

- `input_file` (str | BinaryIO): Path to input save file or file-like object (e.g., BytesIO)
- `output_file` (str | BinaryIO | None, optional): Path to output JSON file, file-like object, or None

**Returns:** Dictionary containing the parsed JSON data from the save file

**Raises:**

- `ValueError`: If input file is not a valid Valheim save file
- `CommandExecutionError`: If conversion fails

**Example:**

```python
# Get JSON data directly
data = vst.to_json("world.db")
print(f"World version: {data['version']}")
print(f"Global keys: {data.get('globalKeys', [])}")

# Save to file and get data
data = vst.to_json("world.db", "backup.json")

# Convert character file
char_data = vst.to_json("character.fch")
print(f"Character name: {char_data.get('name', 'Unknown')}")

# Using file-like objects (BytesIO)
from io import BytesIO

# Read from BytesIO
with open("world.db", "rb") as f:
    db_data = BytesIO(f.read())
data = vst.to_json(db_data)

# Write to BytesIO
json_output = BytesIO()
data = vst.to_json("world.db", json_output)
json_output.seek(0)
json_content = json_output.read()
```

### `from_json()`

```python
from_json(
    input_file: Union[str, BinaryIO],
    output_file: Union[str, BinaryIO, None] = None
) -> Union[str, None]
```

Convert JSON back to binary save format.

**Parameters:**

- `input_file` (str | BinaryIO): Path to input JSON file or file-like object
- `output_file` (str | BinaryIO | None, optional): Path to output save file, file-like object, or None (auto-generated if None and input is a path)

**Returns:**

- Path to the created save file (if output_file is a path or None)
- None (if output_file is a file-like object)

**Raises:**

- `ValueError`: If input file is not a JSON file
- `CommandExecutionError`: If conversion fails

**Example:**

```python
# Auto-generate output filename
vst.from_json("world.json")  # Creates world.db

# Explicit output filename
vst.from_json("backup.json", "world_restored.db")

# Using file-like objects
from io import BytesIO

# Read JSON from BytesIO
json_data = BytesIO(b'{"version": 34, ...}')
result_path = vst.from_json(json_data, "world.db")

# Write to BytesIO
with open("backup.json", "rb") as f:
    json_input = BytesIO(f.read())

db_output = BytesIO()
vst.from_json(json_input, db_output)
db_output.seek(0)
# Now db_output contains the .db file data
```

---

## Item Parsing

### `parse_items_from_base64()`

```python
parse_items_from_base64(b64_string: str) -> List[Dict]
```

Parse Valheim inventory/item data from base64-encoded binary format.

**Parameters:**

- `b64_string` (str): Base64-encoded inventory data (typically from save files)

**Returns:** List of item dictionaries, each containing:

- `name` (str): Item name/ID
- `stack` (int): Number of items in stack
- `durability` (float): Item durability (0-100+ range)
- `pos_x` (int): Inventory X position
- `pos_y` (int): Inventory Y position
- `equipped` (bool): Whether item is equipped
- `quality` (int): Item quality/upgrade level (1-10+)
- `variant` (int): Item variant
- `crafter_id` (int): Player ID who crafted the item
- `crafter_name` (str): Name of player who crafted the item

**Raises:**

- `Exception`: If base64 decoding fails or data is malformed

**Example:**

```python
from valheim_save_tools_py import parse_items_from_base64

# Parse inventory data
base64_data = "AQAAAAIAAAAKQXhlQnJvbnpl..."
items = parse_items_from_base64(base64_data)

# Display items
for item in items:
    print(f"Item: {item['name']}")
    print(f"  Stack: {item['stack']}")
    print(f"  Durability: {item['durability']:.1f}")
    print(f"  Quality: {item['quality']}")
    print(f"  Equipped: {item['equipped']}")
    if item['crafter_name']:
        print(f"  Crafted by: {item['crafter_name']}")

# Filter equipped items
equipped = [item for item in items if item['equipped']]
print(f"Equipped items: {len(equipped)}")

# Check for specific items
weapons = [item for item in items if 'Sword' in item['name'] or 'Bow' in item['name']]
```

### `ValheimItemReader`

```python
ValheimItemReader(data: bytes)
```

Low-level binary reader for parsing Valheim item data structures.

**Parameters:**

- `data` (bytes): Binary data to read from

**Attributes:**

- `data` (bytes): The binary data being read
- `offset` (int): Current read position in the data

**Methods:**

#### `read_byte() -> int`

Read a single byte and advance offset.

#### `read_int32() -> int`

Read a 4-byte signed integer (little-endian).

#### `read_int64() -> int`

Read an 8-byte signed long (little-endian).

#### `read_float() -> float`

Read a 4-byte floating-point number (little-endian).

#### `read_bool() -> bool`

Read a boolean value (1 byte, True if non-zero).

#### `read_string() -> str`

Read a length-prefixed UTF-8 string (1-byte length prefix).

#### `read_item() -> Dict`

Read a complete Valheim item structure and return as dictionary.

**Example:**

```python
from valheim_save_tools_py import ValheimItemReader
import base64

# Decode base64 data
binary_data = base64.b64decode(base64_string)

# Create reader
reader = ValheimItemReader(binary_data)

# Read header
version = reader.read_int32()
num_items = reader.read_int32()

# Read items manually
items = []
for i in range(num_items):
    item = reader.read_item()
    items.append(item)

print(f"Version: {version}")
print(f"Found {len(items)} items")
```

**Use Case:**

The `ValheimItemReader` class is useful when you need fine-grained control over parsing or when working with custom binary formats. For most use cases, the `parse_items_from_base64()` function is more convenient.

---

## Global Keys Methods

### `list_global_keys()`

```python
list_global_keys(db_file: str) -> List[str]
```

List all global keys in a world.

**Parameters:**

- `db_file` (str): Path to world .db file

**Returns:** List of global key strings

**Raises:**

- `ValueError`: If file is not a valid .db file
- `CommandExecutionError`: If command fails

**Example:**

```python
keys = vst.list_global_keys("world.db")
print(f"Global keys: {keys}")

# Check if boss defeated
if "defeated_eikthyr" in keys:
    print("Eikthyr has been defeated!")
```

### `add_global_key()`

```python
add_global_key(db_file: str, key: str) -> None
```

Add a global key to the world.

**Parameters:**

- `db_file` (str): Path to world .db file
- `key` (str): Global key to add

**Raises:**

- `ValueError`: If file is not a valid .db file
- `CommandExecutionError`: If command fails

**Common Keys:**

- `defeated_eikthyr` - Eikthyr boss
- `defeated_gdking` - The Elder boss
- `defeated_bonemass` - Bonemass boss
- `defeated_dragon` - Moder boss
- `defeated_goblinking` - Yagluth boss
- `defeated_queen` - The Queen boss
- `KilledTroll` - Troll kill achievement
- `killed_surtling` - Surtling kill

**Example:**

```python
# Add boss defeat
vst.add_global_key("world.db", "defeated_eikthyr")

# Add multiple keys
for boss in ["defeated_eikthyr", "defeated_gdking", "defeated_bonemass"]:
    vst.add_global_key("world.db", boss)
```

### `remove_global_key()`

```python
remove_global_key(db_file: str, key: str) -> None
```

Remove a specific global key.

**Parameters:**

- `db_file` (str): Path to world .db file
- `key` (str): Global key to remove

**Raises:**

- `ValueError`: If file is not a valid .db file
- `CommandExecutionError`: If command fails

**Example:**

```python
vst.remove_global_key("world.db", "defeated_eikthyr")
```

### `clear_all_global_keys()`

```python
clear_all_global_keys(db_file: str) -> None
```

Remove all global keys from the world.

**Parameters:**

- `db_file` (str): Path to world .db file

**Raises:**

- `ValueError`: If file is not a valid .db file
- `CommandExecutionError`: If command fails

**Example:**

```python
vst.clear_all_global_keys("world.db")
```

---

## Structure Processing Methods

### `clean_structures()`

```python
clean_structures(db_file: str, threshold: int = 25) -> None
```

Clean abandoned structures based on distance threshold.

**Parameters:**

- `db_file` (str): Path to world .db file
- `threshold` (int): Distance threshold for removal (default: 25)
  - `10` - Very conservative (minimal cleanup)
  - `25` - Balanced (recommended)
  - `50` - Aggressive (more cleanup)
  - `100` - Very aggressive (maximum cleanup)

**Raises:**

- `ValueError`: If file is not a valid .db file
- `CommandExecutionError`: If command fails

**Example:**

```python
# Default threshold
vst.clean_structures("world.db")

# Conservative cleaning
vst.clean_structures("world.db", threshold=10)

# Aggressive cleaning
vst.clean_structures("world.db", threshold=50)
```

### `reset_world()`

```python
reset_world(db_file: str) -> None
```

Reset world to initial state.

**Parameters:**

- `db_file` (str): Path to world .db file

**Raises:**

- `ValueError`: If file is not a valid .db file
- `CommandExecutionError`: If command fails

**Example:**

```python
vst.reset_world("world.db")
```

---

## Builder Pattern

### `process()`

```python
process(input_file: str) -> SaveFileProcessor
```

Create a processor for chaining operations.

**Parameters:**

- `input_file` (str): Path to .db file to process

**Returns:** `SaveFileProcessor` instance

**Raises:**

- `ValueError`: If file is not a valid .db file

**Example:**

```python
# Method chaining
result = (vst.process("world.db")
             .clean_structures(threshold=30)
             .reset_world()
             .add_global_key("defeated_eikthyr")
             .save("cleaned_world.db"))

# Export to JSON after processing
json_file = (vst.process("world.db")
                .clean_structures()
                .to_json("cleaned_world.json"))

# Context manager
with vst.process("world.db") as processor:
    processor.clean_structures()
    processor.reset_world()
# Automatically saves to original file
```

### `SaveFileProcessor` Methods

#### `clean_structures(threshold: int = 25)`

Queue structure cleaning operation.

#### `reset_world()`

Queue world reset operation.

#### `add_global_key(key: str)`

Queue global key addition.

#### `remove_global_key(key: str)`

Queue global key removal.

#### `clear_all_global_keys()`

Queue clearing all global keys.

#### `save(output_file: Optional[str] = None) -> str`

Execute all operations and save result.

- If `output_file` is None, overwrites the original file
- Returns path to saved file

#### `to_json(output_file: Optional[str] = None) -> Dict`

Execute all operations and convert result to JSON.

- If `output_file` is provided, also saves the JSON to that file
- Returns parsed JSON data as a dictionary

**Example:**

```python
# Get data after cleaning
data = vst.process("world.db").clean_structures().to_json()
print(f"Cleaned world data: {data}")

# Also save to file
data = vst.process("world.db").clean_structures().to_json("output.json")
```

---

## File Detection Methods

All file detection methods are static and can be called without instantiating the class.

### `is_db_file()`

```python
@staticmethod
is_db_file(file_path: str) -> bool
```

Check if file is a .db file.

**Example:**

```python
if ValheimSaveTools.is_db_file("world.db"):
    print("Valid world data file")
```

### `is_fwl_file()`

```python
@staticmethod
is_fwl_file(file_path: str) -> bool
```

Check if file is a .fwl file.

### `is_fch_file()`

```python
@staticmethod
is_fch_file(file_path: str) -> bool
```

Check if file is a .fch file (character file).

### `is_json_file()`

```python
@staticmethod
is_json_file(file_path: str) -> bool
```

Check if file is a .json file.

### `detect_file_type()`

```python
@staticmethod
detect_file_type(file_path: str) -> Optional[str]
```

Detect file type from extension.

**Returns:** `"db"`, `"fwl"`, `"fch"`, `"json"`, or `None` if unknown

**Example:**

```python
file_type = ValheimSaveTools.detect_file_type("world.db")
print(f"File type: {file_type}")  # Output: db
```

### `is_valheim_file()`

```python
@staticmethod
is_valheim_file(file_path: str) -> bool
```

Check if file is any Valheim save file type (.db, .fwl, .fch, or .json).

**Example:**

```python
if ValheimSaveTools.is_valheim_file("world.db"):
    print("This is a Valheim file")
```

---

## Error Handling

### Exception Hierarchy

```python
ValheimSaveToolsError          # Base exception
├── JarNotFoundError           # JAR file not found
├── JavaNotFoundError          # Java not installed
└── CommandExecutionError      # Command execution failed
```

### Usage Example

```python
from valheim_save_tools_py import (
    ValheimSaveTools,
    JarNotFoundError,
    JavaNotFoundError,
    CommandExecutionError
)

try:
    vst = ValheimSaveTools()
    vst.clean_structures("world.db")
except JarNotFoundError:
    print("JAR file not found!")
except JavaNotFoundError:
    print("Java is not installed!")
except CommandExecutionError as e:
    print(f"Command failed: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
```

### Common Errors

**ValueError: "not a valid .db file"**

- Cause: Attempting to use a non-.db file with methods that require .db files
- Solution: Verify file extension and type

**JarNotFoundError**

- Cause: JAR file not found in package or specified path
- Solution: Ensure package is properly installed

**JavaNotFoundError**

- Cause: Java executable not found
- Solution: Install Java 17 or higher

**CommandExecutionError**

- Cause: JAR command execution failed
- Solution: Check file permissions, Java version, and file validity
