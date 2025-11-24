import base64
import struct
import traceback

class ValheimItemReader:
    def __init__(self, data):
        self.data = data
        self.offset = 0
    
    def read_byte(self):
        """Read a single byte"""
        value = self.data[self.offset]
        self.offset += 1
        return value
    
    def read_int32(self):
        """Read a 4-byte integer (little-endian)"""
        value = struct.unpack('<i', self.data[self.offset:self.offset+4])[0]
        self.offset += 4
        return value
    
    def read_int64(self):
        """Read an 8-byte long (little-endian)"""
        value = struct.unpack('<q', self.data[self.offset:self.offset+8])[0]
        self.offset += 8
        return value
    
    def read_float(self):
        """Read a 4-byte float (little-endian)"""
        value = struct.unpack('<f', self.data[self.offset:self.offset+4])[0]
        self.offset += 4
        return value
    
    def read_bool(self):
        """Read a boolean (1 byte)"""
        value = self.data[self.offset] != 0
        self.offset += 1
        return value
    
    def read_string(self):
        """Read a length-prefixed string (single byte length)"""
        length = self.read_byte()
        
        if length == 0:
            return ""
        
        string = self.data[self.offset:self.offset+length].decode('utf-8')
        self.offset += length
        return string
    
    def read_item(self):
        """Read a complete Valheim item structure"""
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
        
        # There appears to be 8 bytes of unknown data after each item
        # Possibly world coordinates or other metadata
        self.unknown_data = self.data[self.offset:self.offset+8]
        self.offset += 8
        
        # And one more byte
        self.unknown_byte = self.read_byte()
        
        return item

def parse_items_from_base64(b64_string):
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
            print(f"Error parsing item {i+1}: {e}")
            print(f"Offset when error occurred: {reader.offset}")
            traceback.print_exc()
            break

    return items
    