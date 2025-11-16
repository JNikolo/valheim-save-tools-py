# Builder Pattern Implementation

The `SaveFileProcessor` class provides a fluent, chainable API for performing multiple operations on Valheim save files.

## Features

✅ **Fluent API**: Chain multiple operations in a readable, expressive way
✅ **Automatic temp file management**: Creates working copies, cleans up automatically
✅ **Operation queueing**: Operations are queued and executed in order when `.save()` or `.to_json()` is called
✅ **Flexible output**: Save to new file, overwrite original, or export to JSON

## Quick Examples

### Basic Chaining

```python
from valheim_save_tools_py import ValheimSaveTools

vst = ValheimSaveTools()

# Clean and reset in one go
vst.process("world.db") \
   .clean_structures(threshold=30) \
   .reset_world() \
   .save("cleaned_world.db")
```

### Global Keys Management

```python
# Add multiple boss defeat keys
vst.process("world.db") \
   .add_global_key("defeated_eikthyr") \
   .add_global_key("defeated_gdking") \
   .add_global_key("defeated_bonemass") \
   .save("bosses.db")
```

### Export to JSON

```python
# Process and export to JSON
vst.process("world.db") \
   .clean_structures() \
   .reset_world() \
   .to_json("cleaned.json")
```

### Overwrite Original

```python
# Process and overwrite the original file
vst.process("world.db") \
   .clean_structures() \
   .save()  # No output = overwrite
```

## API Reference

### Creating a Processor

```python
processor = vst.process(input_file: str) -> SaveFileProcessor
```

- **input_file**: Path to `.db` file
- **Returns**: `SaveFileProcessor` instance
- **Raises**: `ValueError` if not a valid `.db` file

### Available Operations

All operations return `self` for chaining:

#### `clean_structures(threshold: int = 25)`

Queue structure cleaning operation.

- **threshold**: Distance threshold for removal (default: 25)

#### `reset_world()`

Queue world reset operation.

#### `add_global_key(key: str)`

Queue adding a global key.

- **key**: Global key to add

#### `remove_global_key(key: str)`

Queue removing a global key.

- **key**: Global key to remove

#### `clear_all_global_keys()`

Queue clearing all global keys.

### Finalizing Operations

#### `save(output_file: Optional[str] = None) -> str`

Execute all queued operations and save result.

- **output_file**: Path to save (default: overwrite input file)
- **Returns**: Path to saved file

#### `to_json(output_file: Optional[str] = None) -> str`

Execute operations and convert to JSON.

- **output_file**: Path to save JSON
- **Returns**: Path to JSON file

## How It Works

1. **Queue operations**: Each method call queues an operation
2. **Create temp workspace**: When `.save()` or `.to_json()` is called, a temp directory is created
3. **Execute in order**: Operations execute sequentially on a working copy
4. **Save result**: Final file is saved to the specified location
5. **Auto cleanup**: Temp files are automatically removed

## Implementation Details

- Operations are stored as tuples: `(operation_name, kwargs)`
- Working file is created in a temp directory
- Each operation modifies the working file in place
- Final result is copied to destination
- Temp files cleaned up even if errors occur (best effort)

## Testing

The builder pattern is fully tested with 9 unit tests covering:

- Single operation chains
- Multiple operation chains
- Global key operations
- Overwriting original files
- JSON export after operations
- Error handling
- String representation

All 49 total tests passing! ✅
