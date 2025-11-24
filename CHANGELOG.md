# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-11-24

### Added

- **File-like object support** - All methods now accept file-like objects (BytesIO, file handles) in addition to file paths
  - `to_json()`, `from_json()` - Convert to/from JSON using BytesIO
  - `list_global_keys()` - List keys from file-like objects
  - `add_global_key()`, `remove_global_key()`, `clear_all_global_keys()` - Modify keys in memory
  - `clean_structures()`, `reset_world()` - Process files in memory
  - In-place modification support for file-like objects
  - Mix file paths and file-like objects in workflows
- New example: `file_like_objects.py` demonstrating in-memory processing
- Comprehensive test suite for file-like object support (15 new tests)
- Updated documentation with file-like object examples in README, API docs, and examples

### Changed

- Method signatures updated to accept `Union[str, BinaryIO]` for file inputs/outputs
- Return types updated: methods return `None` when writing to file-like objects
- Added `io` module import for file-like object detection

## [0.3.0] - 2025-11-23

### Added

- New `ValheimItemReader` class for parsing binary item data
  - `parse_items_from_base64()` - Parse base64-encoded inventory data
  - Binary data reader methods: `read_byte()`, `read_int32()`, `read_int64()`, `read_float()`, `read_bool()`, `read_string()`
  - `read_item()` - Parse complete Valheim item structures
- Comprehensive test suite for item reader (19 additional tests)
  - Unit tests for all binary parsing methods
  - Tests for single and multiple item parsing
  - Edge case and error handling tests
- Item reader module exported in public API

## [0.2.0] - 2025-11-19

### Changed

- **BREAKING**: `to_json()` now returns parsed JSON data as a dictionary instead of file path
  - Both `ValheimSaveTools.to_json()` and `SaveFileProcessor.to_json()` affected
  - Allows direct access to save file data without additional file I/O
  - If `output_file` parameter is provided, still saves to that file
  - Migration: Replace `path = vst.to_json(...)` with `data = vst.to_json(...)`

### Fixed

- Fixed `UnboundLocalError` in `to_json()` when using explicit output file path
- Improved temporary file cleanup in `to_json()` method

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
[0.2.0]: https://github.com/JNikolo/valheim-save-tools-py/releases/tag/v0.2.0
[0.3.0]: https://github.com/JNikolo/valheim-save-tools-py/releases/tag/v0.3.0
[0.4.0]: https://github.com/JNikolo/valheim-save-tools-py/releases/tag/v0.4.0
