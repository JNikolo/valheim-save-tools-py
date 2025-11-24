"""
Example: Using file-like objects with Valheim Save Tools.

This example demonstrates how to use file-like objects (BytesIO)
with the wrapper instead of file paths.
"""

from io import BytesIO
from valheim_save_tools_py import ValheimSaveTools

# Initialize the wrapper
vst = ValheimSaveTools()

# Example 1: Reading from a file and converting to JSON using BytesIO
print("Example 1: Converting .db file to JSON using file-like objects")
print("-" * 60)

# Read a .db file into memory
with open("world.db", "rb") as f:
    db_data = BytesIO(f.read())

# Convert to JSON (returns dict, can also write to file-like object)
json_output = BytesIO()
json_data = vst.to_json(db_data, json_output)

print(f"Converted to JSON, got {len(json_data)} top-level keys")
print(f"JSON output size: {json_output.tell()} bytes")

# Example 2: Converting JSON back to .db using BytesIO
print("\nExample 2: Converting JSON back to .db using file-like objects")
print("-" * 60)

# Reset position to read from beginning
json_output.seek(0)

# Convert back to .db format
db_output = BytesIO()
vst.from_json(json_output, db_output)

print(f"Converted back to .db format, size: {db_output.tell()} bytes")

# Example 3: Listing global keys from a file-like object
print("\nExample 3: Listing global keys from file-like object")
print("-" * 60)

with open("world.db", "rb") as f:
    db_data = BytesIO(f.read())

keys = vst.list_global_keys(db_data)
print(f"Found {len(keys)} global keys:")
for key in keys[:5]:  # Show first 5
    print(f"  - {key}")

# Example 4: Adding a global key to a file-like object
print("\nExample 4: Adding a global key to file-like object")
print("-" * 60)

with open("world.db", "rb") as f:
    db_data = BytesIO(f.read())

# Add a key and write back to the same BytesIO object
db_data.seek(0)  # Reset position
vst.add_global_key(db_data, "defeated_eikthyr")

# The db_data BytesIO now contains the modified data
print(f"Added global key, modified data size: {db_data.tell()} bytes")

# You can now write it back to a file or use it further
db_data.seek(0)
with open("world_modified.db", "wb") as f:
    f.write(db_data.read())

print("Saved modified data to world_modified.db")

# Example 5: Clean structures with file-like objects
print("\nExample 5: Cleaning structures using file-like object")
print("-" * 60)

with open("world.db", "rb") as f:
    db_data = BytesIO(f.read())

# Clean structures and get result in a new BytesIO
output = BytesIO()
vst.clean_structures(db_data, output, threshold=30)

print(f"Cleaned structures, output size: {output.tell()} bytes")

# Example 6: Mixing file paths and file-like objects
print("\nExample 6: Mixing file paths and file-like objects")
print("-" * 60)

# Read from file path, write to BytesIO
json_output = BytesIO()
json_data = vst.to_json("world.db", json_output)
print(f"Read from file path, wrote to BytesIO: {json_output.tell()} bytes")

# Read from BytesIO, write to file path
json_output.seek(0)
result_path = vst.from_json(json_output, "world_from_bytesio.db")
print(f"Read from BytesIO, wrote to file path: {result_path}")

print("\nAll examples completed!")
