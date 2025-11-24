"""Unit tests for ValheimItemReader and parse_items_from_base64."""

import pytest
import base64
import struct

from valheim_save_tools_py.valheimItemReader import ValheimItemReader, parse_items_from_base64


class TestValheimItemReader:
    """Test ValheimItemReader class methods."""
    
    def test_read_byte(self):
        """Test reading a single byte."""
        data = bytes([42, 100, 200])
        reader = ValheimItemReader(data)
        
        assert reader.read_byte() == 42
        assert reader.offset == 1
        assert reader.read_byte() == 100
        assert reader.offset == 2
    
    def test_read_int32(self):
        """Test reading a 4-byte integer."""
        # Pack an integer in little-endian format
        value = 12345
        data = struct.pack('<i', value)
        reader = ValheimItemReader(data)
        
        assert reader.read_int32() == value
        assert reader.offset == 4
    
    def test_read_int32_negative(self):
        """Test reading a negative 4-byte integer."""
        value = -9876
        data = struct.pack('<i', value)
        reader = ValheimItemReader(data)
        
        assert reader.read_int32() == value
    
    def test_read_int64(self):
        """Test reading an 8-byte long."""
        value = 9876543210
        data = struct.pack('<q', value)
        reader = ValheimItemReader(data)
        
        assert reader.read_int64() == value
        assert reader.offset == 8
    
    def test_read_float(self):
        """Test reading a 4-byte float."""
        value = 3.14159
        data = struct.pack('<f', value)
        reader = ValheimItemReader(data)
        
        result = reader.read_float()
        assert abs(result - value) < 0.0001  # Float comparison with tolerance
        assert reader.offset == 4
    
    def test_read_bool_true(self):
        """Test reading a boolean (true)."""
        data = bytes([1, 0, 255])
        reader = ValheimItemReader(data)
        
        assert reader.read_bool() is True
        assert reader.offset == 1
    
    def test_read_bool_false(self):
        """Test reading a boolean (false)."""
        data = bytes([0, 1, 255])
        reader = ValheimItemReader(data)
        
        assert reader.read_bool() is False
        assert reader.offset == 1
    
    def test_read_string_empty(self):
        """Test reading an empty string."""
        data = bytes([0])  # Length 0
        reader = ValheimItemReader(data)
        
        assert reader.read_string() == ""
        assert reader.offset == 1
    
    def test_read_string_with_content(self):
        """Test reading a non-empty string."""
        test_string = "Sword"
        length = len(test_string)
        data = bytes([length]) + test_string.encode('utf-8')
        reader = ValheimItemReader(data)
        
        assert reader.read_string() == test_string
        assert reader.offset == 1 + length
    
    def test_read_string_unicode(self):
        """Test reading a unicode string."""
        test_string = "⚔️"
        length = len(test_string.encode('utf-8'))
        data = bytes([length]) + test_string.encode('utf-8')
        reader = ValheimItemReader(data)
        
        assert reader.read_string() == test_string
    
    def test_read_item(self):
        """Test reading a complete item structure."""
        # Build a complete item in binary format
        item_data = bytearray()
        
        # name (string: "AxeBronze")
        name = "AxeBronze"
        item_data.append(len(name))
        item_data.extend(name.encode('utf-8'))
        
        # stack (int32: 1)
        item_data.extend(struct.pack('<i', 1))
        
        # durability (float: 100.0)
        item_data.extend(struct.pack('<f', 100.0))
        
        # pos_x (int32: 5)
        item_data.extend(struct.pack('<i', 5))
        
        # pos_y (int32: 2)
        item_data.extend(struct.pack('<i', 2))
        
        # equipped (bool: True)
        item_data.append(1)
        
        # quality (int32: 3)
        item_data.extend(struct.pack('<i', 3))
        
        # variant (int32: 0)
        item_data.extend(struct.pack('<i', 0))
        
        # crafter_id (int64: 123456789)
        item_data.extend(struct.pack('<q', 123456789))
        
        # crafter_name (string: "Player1")
        crafter = "Player1"
        item_data.append(len(crafter))
        item_data.extend(crafter.encode('utf-8'))
        
        # unknown_data (8 bytes)
        item_data.extend(bytes([0] * 8))
        
        # unknown_byte (1 byte)
        item_data.append(0)
        
        reader = ValheimItemReader(bytes(item_data))
        item = reader.read_item()
        
        assert item['name'] == "AxeBronze"
        assert item['stack'] == 1
        assert abs(item['durability'] - 100.0) < 0.01
        assert item['pos_x'] == 5
        assert item['pos_y'] == 2
        assert item['equipped'] is True
        assert item['quality'] == 3
        assert item['variant'] == 0
        assert item['crafter_id'] == 123456789
        assert item['crafter_name'] == "Player1"


class TestParseItemsFromBase64:
    """Test parse_items_from_base64 function."""
    
    def create_item_binary(self, name, stack=1, durability=100.0, pos_x=0, pos_y=0,
                          equipped=False, quality=1, variant=0, crafter_id=0, crafter_name=""):
        """Helper function to create binary data for an item."""
        item_data = bytearray()
        
        # name
        item_data.append(len(name))
        item_data.extend(name.encode('utf-8'))
        
        # stack
        item_data.extend(struct.pack('<i', stack))
        
        # durability
        item_data.extend(struct.pack('<f', durability))
        
        # pos_x
        item_data.extend(struct.pack('<i', pos_x))
        
        # pos_y
        item_data.extend(struct.pack('<i', pos_y))
        
        # equipped
        item_data.append(1 if equipped else 0)
        
        # quality
        item_data.extend(struct.pack('<i', quality))
        
        # variant
        item_data.extend(struct.pack('<i', variant))
        
        # crafter_id
        item_data.extend(struct.pack('<q', crafter_id))
        
        # crafter_name
        item_data.append(len(crafter_name))
        item_data.extend(crafter_name.encode('utf-8'))
        
        # unknown_data (8 bytes)
        item_data.extend(bytes([0] * 8))
        
        # unknown_byte (1 byte)
        item_data.append(0)
        
        return bytes(item_data)
    
    def test_parse_empty_inventory(self):
        """Test parsing an empty inventory (0 items)."""
        data = bytearray()
        
        # version (int32: 1)
        data.extend(struct.pack('<i', 1))
        
        # num_items (int32: 0)
        data.extend(struct.pack('<i', 0))
        
        b64_string = base64.b64encode(bytes(data)).decode('utf-8')
        items = parse_items_from_base64(b64_string)
        
        assert items == []
    
    def test_parse_single_item(self):
        """Test parsing a single item from base64."""
        data = bytearray()
        
        # version (int32: 1)
        data.extend(struct.pack('<i', 1))
        
        # num_items (int32: 1)
        data.extend(struct.pack('<i', 1))
        
        # Add one item
        data.extend(self.create_item_binary(
            name="SwordIron",
            stack=1,
            durability=75.5,
            pos_x=3,
            pos_y=1,
            equipped=True,
            quality=2,
            variant=0,
            crafter_id=987654321,
            crafter_name="Warrior"
        ))
        
        b64_string = base64.b64encode(bytes(data)).decode('utf-8')
        items = parse_items_from_base64(b64_string)
        
        assert len(items) == 1
        assert items[0]['name'] == "SwordIron"
        assert items[0]['stack'] == 1
        assert abs(items[0]['durability'] - 75.5) < 0.01
        assert items[0]['pos_x'] == 3
        assert items[0]['pos_y'] == 1
        assert items[0]['equipped'] is True
        assert items[0]['quality'] == 2
        assert items[0]['variant'] == 0
        assert items[0]['crafter_id'] == 987654321
        assert items[0]['crafter_name'] == "Warrior"
    
    def test_parse_multiple_items(self):
        """Test parsing multiple items from base64."""
        data = bytearray()
        
        # version (int32: 1)
        data.extend(struct.pack('<i', 1))
        
        # num_items (int32: 3)
        data.extend(struct.pack('<i', 3))
        
        # Add three items
        data.extend(self.create_item_binary(
            name="Wood",
            stack=50,
            durability=100.0,
            pos_x=0,
            pos_y=0
        ))
        
        data.extend(self.create_item_binary(
            name="Stone",
            stack=30,
            durability=100.0,
            pos_x=1,
            pos_y=0
        ))
        
        data.extend(self.create_item_binary(
            name="BowHuntsman",
            stack=1,
            durability=50.0,
            pos_x=2,
            pos_y=0,
            equipped=True,
            quality=4,
            crafter_id=111222333,
            crafter_name="Archer"
        ))
        
        b64_string = base64.b64encode(bytes(data)).decode('utf-8')
        items = parse_items_from_base64(b64_string)
        
        assert len(items) == 3
        
        # Check first item
        assert items[0]['name'] == "Wood"
        assert items[0]['stack'] == 50
        
        # Check second item
        assert items[1]['name'] == "Stone"
        assert items[1]['stack'] == 30
        
        # Check third item
        assert items[2]['name'] == "BowHuntsman"
        assert items[2]['stack'] == 1
        assert items[2]['equipped'] is True
        assert items[2]['quality'] == 4
        assert items[2]['crafter_name'] == "Archer"
    
    def test_parse_item_with_empty_crafter_name(self):
        """Test parsing an item with empty crafter name."""
        data = bytearray()
        
        # version (int32: 1)
        data.extend(struct.pack('<i', 1))
        
        # num_items (int32: 1)
        data.extend(struct.pack('<i', 1))
        
        # Add item with empty crafter name
        data.extend(self.create_item_binary(
            name="Resin",
            stack=20,
            crafter_id=0,
            crafter_name=""
        ))
        
        b64_string = base64.b64encode(bytes(data)).decode('utf-8')
        items = parse_items_from_base64(b64_string)
        
        assert len(items) == 1
        assert items[0]['name'] == "Resin"
        assert items[0]['crafter_name'] == ""
        assert items[0]['crafter_id'] == 0
    
    def test_parse_item_with_high_quality(self):
        """Test parsing an item with high quality value."""
        data = bytearray()
        
        # version (int32: 1)
        data.extend(struct.pack('<i', 1))
        
        # num_items (int32: 1)
        data.extend(struct.pack('<i', 1))
        
        # Add item with quality 10
        data.extend(self.create_item_binary(
            name="SwordBlackmetal",
            quality=10,
            durability=200.0
        ))
        
        b64_string = base64.b64encode(bytes(data)).decode('utf-8')
        items = parse_items_from_base64(b64_string)
        
        assert len(items) == 1
        assert items[0]['name'] == "SwordBlackmetal"
        assert items[0]['quality'] == 10
        assert abs(items[0]['durability'] - 200.0) < 0.01
    
    def test_parse_with_different_version(self):
        """Test parsing with a different version number."""
        data = bytearray()
        
        # version (int32: 2) - different version
        data.extend(struct.pack('<i', 2))
        
        # num_items (int32: 1)
        data.extend(struct.pack('<i', 1))
        
        # Add item
        data.extend(self.create_item_binary(name="Torch"))
        
        b64_string = base64.b64encode(bytes(data)).decode('utf-8')
        items = parse_items_from_base64(b64_string)
        
        # Should still parse correctly (version is read but not validated)
        assert len(items) == 1
        assert items[0]['name'] == "Torch"
    
    def test_parse_invalid_base64(self):
        """Test parsing with invalid base64 string."""
        with pytest.raises(Exception):
            parse_items_from_base64("not-valid-base64!!!")
    
    def test_parse_truncated_data(self):
        """Test parsing with truncated data (should handle gracefully)."""
        data = bytearray()
        
        # version (int32: 1)
        data.extend(struct.pack('<i', 1))
        
        # num_items (int32: 1) - says there's 1 item
        data.extend(struct.pack('<i', 1))
        
        # But provide no item data (truncated)
        
        b64_string = base64.b64encode(bytes(data)).decode('utf-8')
        items = parse_items_from_base64(b64_string)
        
        # Should return empty list due to error handling
        assert items == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
