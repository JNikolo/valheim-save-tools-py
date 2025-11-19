#!/usr/bin/env python3
"""
File Conversion Examples

Demonstrates converting between Valheim save formats (.db, .fwl, .fch) and JSON.
"""

import sys
from pathlib import Path
from valheim_save_tools_py import ValheimSaveTools


def convert_to_json_auto():
    """Convert save file to JSON and get parsed data."""
    vst = ValheimSaveTools()
    
    # Returns parsed JSON data as dictionary
    data = vst.to_json("world.db")
    print(f"World version: {data.get('version', 'unknown')}")
    print(f"Global keys: {len(data.get('globalKeys', []))}")
    return data


def convert_to_json_explicit():
    """Convert save file to JSON with explicit output filename."""
    vst = ValheimSaveTools()
    
    # Specify custom output filename - still returns data
    data = vst.to_json("world.db", "backup_world.json")
    print(f"Saved to: backup_world.json")
    print(f"Data contains {len(data)} top-level keys")
    return data


def convert_from_json():
    """Convert JSON back to save file format."""
    vst = ValheimSaveTools()
    
    # Auto-detects output format from original file extension
    output = vst.from_json("world.json")
    print(f"Converted to: {output}")


def batch_convert_world_files():
    """Convert all world files in a directory to JSON and save them."""
    vst = ValheimSaveTools()
    
    world_dir = Path("./worlds")
    
    # Convert all .db files
    for db_file in world_dir.glob("*.db"):
        json_path = db_file.with_suffix('.json')
        data = vst.to_json(str(db_file), str(json_path))
        print(f"✓ {db_file.name} -> {json_path.name} (version: {data.get('version', '?')})")
    
    # Convert all .fwl files
    for fwl_file in world_dir.glob("*.fwl"):
        json_path = fwl_file.with_suffix('.json')
        data = vst.to_json(str(fwl_file), str(json_path))
        print(f"✓ {fwl_file.name} -> {json_path.name}")


def batch_convert_character_files():
    """Convert all character files to JSON."""
    vst = ValheimSaveTools()
    
    char_dir = Path("./characters")
    
    for fch_file in char_dir.glob("*.fch"):
        json_path = fch_file.with_suffix('.json')
        data = vst.to_json(str(fch_file), str(json_path))
        char_name = data.get('name', 'Unknown')
        print(f"✓ {fch_file.name} -> {json_path.name} (Character: {char_name})")


def convert_with_verbose():
    """Convert with verbose output enabled."""
    vst = ValheimSaveTools(verbose=True)
    
    output = vst.to_json("world.db")
    print(f"Converted to: {output}")


def main():
    """Run all conversion examples."""
    print("=" * 60)
    print("File Conversion Examples")
    print("=" * 60)
    
    examples = [
        ("Convert to JSON (auto filename)", convert_to_json_auto),
        ("Convert to JSON (explicit filename)", convert_to_json_explicit),
        ("Convert from JSON", convert_from_json),
        ("Batch convert world files", batch_convert_world_files),
        ("Batch convert character files", batch_convert_character_files),
        ("Convert with verbose output", convert_with_verbose),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{i}. {name}")
        print("-" * 60)
        try:
            func()
        except Exception as e:
            print(f"Error: {e}")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run with actual file
        file_path = sys.argv[1]
        vst = ValheimSaveTools(verbose=True)
        
        if file_path.endswith('.json'):
            output = vst.from_json(file_path)
            print(f"Converted {file_path} -> {output}")
        else:
            output = vst.to_json(file_path)
            print(f"Converted {file_path} -> {output}")
    else:
        print("File Conversion Examples")
        print("=" * 60)
        print("Usage: python convert.py <file_path>")
        print("\nSupported file types:")
        print("  - .db  (world data)")
        print("  - .fwl (world metadata)")
        print("  - .fch (character)")
        print("  - .json (converted files)")
        print("\nExamples:")
        print("  python convert.py world.db")
        print("  python convert.py world.json")
        print("  python convert.py character.fch")
