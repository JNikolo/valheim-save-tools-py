"""
Example: Parse and analyze Valheim inventory items from base64 data.

This example demonstrates how to:
- Parse base64-encoded inventory data
- Filter and analyze items
- Display inventory statistics
- Extract equipped items
"""

from valheim_save_tools_py import parse_items_from_base64, ValheimItemReader
from collections import Counter
import base64


def display_item(item, index=None):
    """Display detailed information about a single item."""
    prefix = f"{index}. " if index else "  - "
    print(f"{prefix}{item['name']}")
    print(f"     Stack: {item['stack']}")
    print(f"     Durability: {item['durability']:.1f}")
    print(f"     Quality: {item['quality']}")
    print(f"     Position: ({item['pos_x']}, {item['pos_y']})")
    if item['equipped']:
        print(f"     [EQUIPPED]")
    if item['crafter_name']:
        print(f"     Crafted by: {item['crafter_name']}")
    print()


def analyze_inventory(items):
    """Analyze and display inventory statistics."""
    print("\n" + "=" * 60)
    print("INVENTORY ANALYSIS")
    print("=" * 60)
    
    # Basic counts
    print(f"\nTotal items: {len(items)}")
    equipped_count = sum(1 for item in items if item['equipped'])
    print(f"Equipped items: {equipped_count}")
    
    # Item type breakdown
    item_counts = Counter(item['name'] for item in items)
    print("\nItem breakdown:")
    for item_name, count in item_counts.most_common(10):
        print(f"  {item_name}: {count}")
    
    # Quality distribution
    quality_counts = Counter(item['quality'] for item in items)
    print("\nQuality levels:")
    for quality in sorted(quality_counts.keys()):
        print(f"  Level {quality}: {quality_counts[quality]} items")
    
    # Durability analysis
    items_with_durability = [i for i in items if i['durability'] > 0]
    if items_with_durability:
        total_durability = sum(item['durability'] for item in items_with_durability)
        avg_durability = total_durability / len(items_with_durability)
        min_durability = min(item['durability'] for item in items_with_durability)
        print(f"\nDurability:")
        print(f"  Average: {avg_durability:.1f}%")
        print(f"  Lowest: {min_durability:.1f}%")
    
    # Crafters
    crafters = set(item['crafter_name'] for item in items if item['crafter_name'])
    if crafters:
        print(f"\nItems crafted by:")
        for crafter in crafters:
            count = sum(1 for i in items if i['crafter_name'] == crafter)
            print(f"  {crafter}: {count} items")


def find_damaged_items(items, threshold=50.0):
    """Find items below durability threshold."""
    damaged = [item for item in items if 0 < item['durability'] < threshold]
    
    if damaged:
        print("\n" + "=" * 60)
        print(f"DAMAGED ITEMS (below {threshold}% durability)")
        print("=" * 60)
        for item in sorted(damaged, key=lambda x: x['durability']):
            print(f"  {item['name']}: {item['durability']:.1f}%")
    else:
        print(f"\nNo damaged items found (all above {threshold}%)")


def find_equipped_items(items):
    """Find and display equipped items."""
    equipped = [item for item in items if item['equipped']]
    
    print("\n" + "=" * 60)
    print("EQUIPPED ITEMS")
    print("=" * 60)
    
    if equipped:
        for item in equipped:
            display_item(item)
    else:
        print("No equipped items found.")


def filter_by_category(items):
    """Filter items by common categories."""
    categories = {
        'Weapons': ['Sword', 'Axe', 'Bow', 'Spear', 'Mace', 'Knife', 'Club'],
        'Armor': ['Armor', 'Helmet', 'Legs', 'Cape'],
        'Tools': ['Pickaxe', 'Hoe', 'Hammer', 'Cultivator'],
        'Food': ['Meat', 'Fish', 'Berry', 'Mushroom', 'Bread', 'Pie'],
        'Resources': ['Wood', 'Stone', 'Iron', 'Copper', 'Tin', 'Bronze']
    }
    
    print("\n" + "=" * 60)
    print("ITEMS BY CATEGORY")
    print("=" * 60)
    
    for category, keywords in categories.items():
        category_items = [
            item for item in items
            if any(keyword in item['name'] for keyword in keywords)
        ]
        
        if category_items:
            print(f"\n{category} ({len(category_items)}):")
            for item in category_items:
                quality_str = f" (Q{item['quality']})" if item['quality'] > 1 else ""
                stack_str = f" x{item['stack']}" if item['stack'] > 1 else ""
                print(f"  - {item['name']}{quality_str}{stack_str}")


def example_basic_parsing():
    """Example: Basic item parsing."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Item Parsing")
    print("=" * 60)
    
    # Example base64 data (you would get this from a save file)
    # This is a placeholder - replace with actual data
    example_data = "AQAAAAIAAAAKQXhlQnJvbnpl"
    
    try:
        items = parse_items_from_base64(example_data)
        
        print(f"\nParsed {len(items)} items:")
        for i, item in enumerate(items, 1):
            display_item(item, i)
            
    except Exception as e:
        print(f"Error parsing items: {e}")
        print("(This is expected with the placeholder data)")


def example_custom_parsing():
    """Example: Custom binary parsing with ValheimItemReader."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Custom Binary Parsing")
    print("=" * 60)
    
    # Example of using ValheimItemReader directly
    example_data = "AQAAAAIAAAAKQXhlQnJvbnpl"
    
    try:
        binary_data = base64.b64decode(example_data)
        reader = ValheimItemReader(binary_data)
        
        # Read header
        version = reader.read_int32()
        num_items = reader.read_int32()
        
        print(f"\nData version: {version}")
        print(f"Item count: {num_items}")
        
        # Read items with custom filtering
        high_quality_items = []
        for i in range(num_items):
            item = reader.read_item()
            if item['quality'] >= 3:
                high_quality_items.append(item)
        
        print(f"\nFound {len(high_quality_items)} high-quality items (Q3+)")
        
    except Exception as e:
        print(f"Error: {e}")
        print("(This is expected with the placeholder data)")


def main():
    """Main function demonstrating item parsing capabilities."""
    print("\n" + "=" * 60)
    print("VALHEIM ITEM PARSER EXAMPLES")
    print("=" * 60)
    
    # Note: Replace this with actual base64 data from a save file
    print("\nTo use this script with real data:")
    print("1. Convert a character file to JSON using ValheimSaveTools")
    print("2. Extract the base64 inventory data from the JSON")
    print("3. Replace the placeholder data in this script")
    print()
    
    # Run examples with placeholder data (will show errors)
    example_basic_parsing()
    example_custom_parsing()
    
    # If you have real data, uncomment and use these:
    # items = parse_items_from_base64(your_base64_data)
    # analyze_inventory(items)
    # find_equipped_items(items)
    # find_damaged_items(items, threshold=50.0)
    # filter_by_category(items)


if __name__ == "__main__":
    main()
