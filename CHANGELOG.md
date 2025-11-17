# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-16

### Added

- Initial release of Valheim Save Tools Python API
- File conversion support (binary ↔ JSON)
  - `to_json()` - Convert .db, .fwl, .fch to JSON
  - `from_json()` - Convert JSON back to binary format
- Global keys management
  - `list_global_keys()` - List all global keys
  - `add_global_key()` - Add boss defeats, events, etc.
  - `remove_global_key()` - Remove specific keys
  - `clear_all_global_keys()` - Clear all keys
- Structure processing
  - `clean_structures()` - Remove abandoned structures
  - `reset_world()` - Reset world to initial state
- Builder pattern support via `SaveFileProcessor`
  - Method chaining for complex operations
  - Fluent API: `.process().clean().reset().save()`
- Context manager support
  - Automatic temp file cleanup
  - Exception-safe resource management
- Input validation and error handling
  - Custom exceptions (JarNotFoundError, JavaNotFoundError, CommandExecutionError)
  - File type validation
  - Descriptive error messages
- Static file detection methods
  - `is_db_file()`, `is_fwl_file()`, `is_fch_file()`, `is_json_file()`
  - `detect_file_type()`, `is_valheim_file()`
- Comprehensive test suite
  - 55 tests with 100% pass rate
  - Unit tests for all functionality
  - Mocked subprocess calls for isolation
- Documentation
  - Complete README with examples
  - API reference documentation
  - Builder pattern guide
  - 4 comprehensive example scripts
- Configuration options
  - Verbose mode
  - Fail on unsupported version
  - Skip resolve names
  - Custom JAR/Java paths

### Features

- Python 3.8+ support
- Type hints throughout codebase
- Auto-detection of bundled JAR file
- Auto-detection of Java runtime
- Cross-platform compatibility (Windows, macOS, Linux)

---

[0.1.0]: https://github.com/JNikolo/valheim-save-tools-py/releases/tag/v0.1.0
