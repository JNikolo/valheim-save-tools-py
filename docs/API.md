# API Reference

Complete API documentation for Valheim Save Tools Python API.

## Table of Contents

- [Core Class](#core-class)
- [File Conversion Methods](#file-conversion-methods)
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
to_json(input_file: str, output_file: Optional[str] = None) -> str
```

Convert Valheim save file to JSON format.

**Supported formats:** `.db`, `.fwl`, `.fch`

**Parameters:**

- `input_file` (str): Path to input save file
- `output_file` (str, optional): Path to output JSON file (auto-generated if not provided)

**Returns:** Path to the created JSON file

**Raises:**

- `ValueError`: If input file is not a valid Valheim save file
- `CommandExecutionError`: If conversion fails

**Example:**

```python
# Auto-generate output filename
vst.to_json("world.db")  # Creates world.json

# Explicit output filename
vst.to_json("world.db", "backup.json")

# Convert character file
vst.to_json("character.fch", "character_backup.json")
```

### `from_json()`

```python
from_json(input_file: str, output_file: Optional[str] = None) -> str
```

Convert JSON back to binary save format.

**Parameters:**

- `input_file` (str): Path to input JSON file
- `output_file` (str, optional): Path to output save file (auto-generated if not provided)

**Returns:** Path to the created save file

**Raises:**

- `ValueError`: If input file is not a JSON file
- `CommandExecutionError`: If conversion fails

**Example:**

```python
# Auto-generate output filename
vst.from_json("world.json")  # Creates world.db

# Explicit output filename
vst.from_json("backup.json", "world_restored.db")
```

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

#### `to_json(output_file: Optional[str] = None) -> str`

Execute all operations and convert result to JSON.

- Returns path to JSON file

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
