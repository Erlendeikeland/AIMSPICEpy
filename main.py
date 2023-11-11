import struct

class Node:
    def __init__(self, name, type):
        if type == 2:
            self.name = name
        else:
            self.name = name[2:-1]
        self.type = type
        self.values = []

    def __repr__(self):
        return str(self.name)
    
    def __iter__(self):
        return iter(self.values)
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.values[key]
        if isinstance(key, int):
            return self.values[key]
        else:
            raise TypeError("Key must be of type int")
        
    def __len__(self):
        return len(self.values)

class File:
    def __init__(self, data, index):
        self._data = data
        self.name = ""
        self.date = ""
        self.analysis = ""
        self.nodes_count = 0
        self.timepoints_count = 0
        self._index = index
        self._nodes = []
        self._parse_file()
        
    def _parse_file(self):        
        self._parse_header()
        self._parse_nodes()
        self._parse_values()

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

    def _parse_header(self):
        self.name = self._extract_name()
        self.date = self._extract_name()
        self.analysis = self._extract_name()
        self._index += 100
        extracted_data = self._extract_integer_values(self._data[self._index:self._index + 8])
        self.nodes_count = extracted_data[0]
        self.timepoints = extracted_data[1]
        self._index += 8

    def _extract_name(self):
        name_length = self._extract_integer_values(self._data[self._index:self._index + 4])[0]
        self._index += 4
        name = self._data[self._index:self._index + name_length].decode("utf-8")
        self._index += name_length
        return name
    
    def _parse_nodes(self):
        for i in range(self.nodes_count):
            name_length = self._extract_integer_values(self._data[self._index:self._index + 4])[0]
            self._index += 4
            name = self._data[self._index:self._index + name_length].decode("utf-8")
            self._index += name_length
            type = self._extract_integer_values(self._data[self._index:self._index + 4])[0]
            self._index += 4
            self._nodes.append(Node(name, type))

    def _parse_values(self):
        for i in range(self.timepoints):
            for j in range(self.nodes_count):
                value = self._extract_double_values(self._data[self._index:self._index + 8])[0]
                self._index += 8
                self._nodes[j].values.append(value)

    def __iter__(self):
        return iter(self._nodes)
    
    def __getitem__(self, key):
        if isinstance(key, str):
            for node in self._nodes:
                if node.name == key:
                    return node
            raise KeyError(f"Node: {key} not found")
        else:
            raise TypeError("Key must be of type str")
        
    def __len__(self):
        return len(self._nodes)
    
    def __repr__(self):
        return str(self.name)

class Aimspice:
    def __init__(self, file_path):
        self._file_path = file_path
        self.file_count = 0
        self._files = []
        self._index = 0
        self._parse_file()

    def _parse_file(self):
        with open(self._file_path, "rb") as f:
            data = f.read()
        
        self.file_count = struct.unpack("i", data[self._index:self._index + 4])[0]
        self._index += 4

        for i in range(self.file_count):
            file = File(data, self._index)
            self._index = file._index
            self._files.append(file)

    def __iter__(self):
        return iter(self._files)
    
    def __getitem__(self, key):
        if isinstance(key, str):
            for file in self._files:
                if file.name == key:
                    return file
            raise KeyError(f"File: {key} not found")
        elif isinstance(key, int):
            return self._files[key]
        else:
            raise TypeError("Key must be of type str or int")

    def __len__(self):
        return len(self._files)