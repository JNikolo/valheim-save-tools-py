# Valheim Save Tools Python API

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jnikolo.github.io/valheim-save-tools-py/)

A Pythonic wrapper for [Valheim Save Tools](https://github.com/Kakoen/valheim-save-tools), providing an intuitive API to manipulate Valheim save files programmatically.

## Features

✅ **File Conversion** - Convert between binary formats (.db, .fwl, .fch) and JSON  
✅ **Global Keys Management** - Add, remove, or list global keys (boss defeats, events)  
✅ **Structure Cleaning** - Remove abandoned structures with configurable thresholds  
✅ **World Reset** - Reset world to initial state while preserving progress  
✅ **Method Chaining** - Fluent API for complex operations  
✅ **Context Manager** - Automatic cleanup and resource management

## Installation

```bash
pip install valheim-save-tools-py
```

## Quick Start

```python
from valheim_save_tools_py import ValheimSaveTools

vst = ValheimSaveTools()

# Convert to JSON and get data
data = vst.to_json("world.db")
print(f"World version: {data['version']}")

# Add boss defeat
vst.add_global_key("world.db", "defeated_eikthyr")

# Clean and reset with method chaining
vst.process("world.db") \
   .clean_structures(threshold=30) \
   .reset_world() \
   .save("cleaned_world.db")

# Context manager for automatic cleanup
with vst.process("world.db") as p:
    p.clean_structures()
    p.reset_world()
```

## Documentation

- 🌐 **[Live Documentation](https://jnikolo.github.io/valheim-save-tools-py/)** - Full documentation site
- 📚 **[API Reference](docs/API.md)** - Complete API documentation
- 📖 **[Usage Guide](docs/USAGE.md)** - Detailed usage patterns and examples
- 🎯 **[Examples](docs/examples/)** - Working code examples

## Common Use Cases

### Convert Save Files

```python
# Binary to JSON - returns parsed data
data = vst.to_json("world.db")
print(f"World has {len(data.get('globalKeys', []))} global keys")

# Also save to file
data = vst.to_json("world.db", "backup.json")

# JSON to Binary
vst.from_json("backup.json", "world.db")
```

### Manage Boss Defeats

```python
# List all global keys
keys = vst.list_global_keys("world.db")

# Add boss defeats
vst.add_global_key("world.db", "defeated_eikthyr")
vst.add_global_key("world.db", "defeated_gdking")
```

### Clean Structures

```python
# Clean with default threshold (25)
vst.clean_structures("world.db")

# Clean with custom threshold
vst.clean_structures("world.db", threshold=50)
```

## Requirements

- Python 3.8 or higher
- Java 17 or higher (for running the bundled JAR)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

This is a Python wrapper for [Valheim Save Tools](https://github.com/Kakoen/valheim-save-tools) by [kakoen](https://github.com/Kakoen). Big shout-out for creating such a cool tool 🙏.

I encourage you to contribute to the Valheim Save Tools project!
