import struct

class Node:
    def __init__(self, name, type):
        if type == 2:
            self.name = name
        else:
            self.name = name[2:-1]
        self.type = type
        self.values = []

class OutFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = ""
        self.date = ""
        self.analysis = ""
        self.nodes_count = 0
        self.timepoints_count = 0
        self._index = 0
        self._nodes = []
        self._parse_file()
    
    def _parse_file(self):
        with open(self.file_path, "rb") as f:
            data = f.read()
            print(data)
        self._parse_header(data)
        self._parse_nodes(data)
        self._parse_values(data)

    def _extract_values(self, data, chunk_size, unpack_type):
        result = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            if len(chunk) == chunk_size:
                value = struct.unpack(unpack_type, chunk)
                result.append(value[0])
        return result

    def _extract_double_values(self, data):
        return self._extract_values(data, 8, "d")

    def _extract_integer_values(self, data):
        return self._extract_values(data, 4, "i")

    def _parse_header(self, data):
        self._index += 4
        self.name = self._extract_name(data)
        self.date = self._extract_name(data)
        self.analysis = self._extract_name(data)
        self._index += 100
        extracted_data = self._extract_integer_values(data[self._index:self._index + 8])
        self.nodes_count = extracted_data[0]
        self.timepoints = extracted_data[1]
        self._index += 8

    def _extract_name(self, data):
        name_length = self._extract_integer_values(data[self._index:self._index + 4])[0]
        self._index += 4
        name = data[self._index:self._index + name_length].decode("utf-8")
        self._index += name_length
        return name
    
    def _parse_nodes(self, data):
        for i in range(self.nodes_count):
            name_length = self._extract_integer_values(data[self._index:self._index + 4])[0]
            self._index += 4
            name = data[self._index:self._index + name_length].decode("utf-8")
            self._index += name_length
            type = self._extract_integer_values(data[self._index:self._index + 4])[0]
            self._index += 4
            self._nodes.append(Node(name, type))

    def _parse_values(self, data):
        for i in range(self.timepoints):
            for j in range(self.nodes_count):
                value = self._extract_double_values(data[self._index:self._index + 8])[0]
                self._index += 8
                self._nodes[j].values.append(value)

    def __getitem__(self, key):
        if isinstance(key, str):
            for node in self._nodes:
                if node.name == key:
                    return node.values
            raise KeyError(f"Node {key} not found")
        else:
            raise TypeError("Key must be a string")