"""Valheim item data parser for reading binary item structures."""

import base64
import logging
import struct
from typing import Dict, List, Any, Optional

# Configure module logger
logger = logging.getLogger(__name__)

# Constants for unknown data sizes in item structure
# These are observed in the binary format but their purpose is not yet documented
UNKNOWN_DATA_SIZE = 8  # 8 bytes of unknown data after each item
UNKNOWN_BYTE_SIZE = 1  # 1 additional unknown byte


class ValheimItemReader:
    """
    Binary reader for Valheim item data structures.
    
    This class handles reading various data types from a binary buffer
    representing Valheim inventory/item data.
    """
    
    def __init__(self, data: bytes):
        """
        Initialize the reader with binary data.
        
        Args:
            data: Binary data to read from
        """
        self.data = data
        self.offset = 0
    
    def read_byte(self) -> int:
        """
        Read a single byte.
        
        Returns:
            Integer value of the byte (0-255)
        """
        value = self.data[self.offset]
        self.offset += 1
        return value
    
    def read_int32(self) -> int:
        """
        Read a 4-byte integer (little-endian).
        
        Returns:
            32-bit signed integer
        """
        value = struct.unpack('<i', self.data[self.offset:self.offset+4])[0]
        self.offset += 4
        return value
    
    def read_int64(self) -> int:
        """
        Read an 8-byte long (little-endian).
        
        Returns:
            64-bit signed integer
        """
        value = struct.unpack('<q', self.data[self.offset:self.offset+8])[0]
        self.offset += 8
        return value
    
    def read_float(self) -> float:
        """
        Read a 4-byte float (little-endian).
        
        Returns:
            32-bit floating point number
        """
        value = struct.unpack('<f', self.data[self.offset:self.offset+4])[0]
        self.offset += 4
        return value
    
    def read_bool(self) -> bool:
        """
        Read a boolean (1 byte).
        
        Returns:
            True if byte is non-zero, False otherwise
        """
        value = self.data[self.offset] != 0
        self.offset += 1
        return value
    
    def read_string(self) -> str:
        """
        Read a length-prefixed string (single byte length).
        
        Returns:
            UTF-8 decoded string
        """
        length = self.read_byte()
        
        if length == 0:
            return ""
        
        string = self.data[self.offset:self.offset+length].decode('utf-8')
        self.offset += length
        return string
    
    def read_item(self) -> Dict[str, Any]:
        """
        Read a complete Valheim item structure.
        
        Returns:
            Dictionary containing item properties:
                - name: Item name
                - stack: Stack count
                - durability: Item durability
                - pos_x: X position in inventory
                - pos_y: Y position in inventory
                - equipped: Whether item is equipped
                - quality: Item quality level
                - variant: Item variant
                - crafter_id: ID of player who crafted the item
                - crafter_name: Name of player who crafted the item
        """
        item = {}
        
        item['name'] = self.read_string()
        item['stack'] = self.read_int32()
        item['durability'] = self.read_float()
        item['pos_x'] = self.read_int32()
        item['pos_y'] = self.read_int32()
        item['equipped'] = self.read_bool()
        item['quality'] = self.read_int32()
        item['variant'] = self.read_int32()
        item['crafter_id'] = self.read_int64()
        item['crafter_name'] = self.read_string()
        
        # There appears to be UNKNOWN_DATA_SIZE bytes of unknown data after each item
        # Possibly world coordinates or other metadata
        self.unknown_data = self.data[self.offset:self.offset+UNKNOWN_DATA_SIZE]
        self.offset += UNKNOWN_DATA_SIZE
        
        # And one more byte
        self.unknown_byte = self.read_byte()
        
        return item


def parse_items_from_base64(b64_string: str) -> List[Dict[str, Any]]:
    """
    Parse Valheim items from a base64-encoded binary string.
    
    Args:
        b64_string: Base64-encoded string containing item data
        
    Returns:
        List of dictionaries, each representing an item
        
    Example:
        >>> items = parse_items_from_base64(encoded_data)
        >>> for item in items:
        ...     print(f"Item: {item['name']}, Stack: {item['stack']}")
    """
    data = base64.b64decode(b64_string)
    reader = ValheimItemReader(data)
    version = reader.read_int32()
    num_items = reader.read_int32()

    # Parse each item
    items = []
    for i in range(num_items):
        try:
            item = reader.read_item()
            items.append(item)
        except Exception as e:
            logger.error(
                "Error parsing item %d: %s (offset: %d)",
                i + 1,
                str(e),
                reader.offset,
                exc_info=True
            )
            break

    return items