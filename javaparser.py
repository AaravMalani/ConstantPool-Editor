import pprint
import sys
import struct
import argparse
import os
__version__ = "1.0.0"
__author__ = 'Aarav Malani'
__license__ = 'MIT'

if os.name == 'nt':
    os.system("color")

parser = argparse.ArgumentParser(
    prog='ConstantPoolEditor',
    description='Edits the constant pool of a Java file')
parser.add_argument(
    "filename", help="The name of the .class file to parse", nargs='?')
parser.add_argument(
    "-v", "--version", help="Output the version of the program", action='store_true')
parser.add_argument(
    "-e", "--edit", help="Edit the constant pool (default is viewing only)", action='store_true')
parser.add_argument(
    "-r", "--resolve", help="Resolve the indexes in the constant pool", action='store_true')
parser.add_argument("-H", "--hide-tag",
                    help="Hides the tag and length of the constant pool elements", action='store_true')
args = parser.parse_args()
if args.version:
    print("ConstantPoolEditor "+__version__)
    with open('LICENSE') as f:
        print(f.read().replace(__license__+" License\n\n", ""))
    print("Written by "+__author__+".")
    sys.exit(0)
if not args.filename:
    print("ConstantPoolEditor: error: the following arguments are required: filename")
    sys.exit(1)


def nextBytes(x, d, func=int.from_bytes):
    return func(d[:x]), d[x:]


with open(args.filename, "rb") as f:
    b = f.read()
magic, b = nextBytes(4, b, bytes)
if magic != b'\xca\xfe\xba\xbe':
    print("ERROR: Invalid magic")
    sys.exit(0)
minor, b = nextBytes(2, b)
major, b = nextBytes(2, b)
a = {k: '1.'+str(i) for k, i in zip([45]+list(range(45, 64)), [*range(0, 20)])}
cpc, b = nextBytes(2, b)
cp = []


class CONSTANT:
    def __repr__(self):
        returned = "<"+self.__class__.__name__+" "
        for i in self.__dict__:
            if args.hide_tag and i in ['tag', 'length']:
                continue

            if args.resolve and i.endswith('_index'):
                try:
                    val = str(cp[self.__dict__[i]-1])
                    if type(val) is CONSTANT_Utf8:
                        val = val.bytes.decode('latin1')
                    returned += i+'='+val + ' '
                except:
                    returned += i+'='+str(self.__dict__[i])
            elif type(self.__dict__[i]) is bytes:
                returned += i + '='+self.__dict__[i].decode('latin1') + ' '
            else:
                returned += i + '='+str(self.__dict__[i]) + ' '
        returned = returned[:-1]
        returned += '>'

        return returned


def pack(dct):
    returned = b''
    for i in dct:
        key, value = tuple(list(i.items())[0])
        if type(key) is bytes:
            returned += key
        elif type(key) is int:
            returned += int.to_bytes(key, length=value)
        elif type(key) is float:
            returned += struct.pack(">f", key).rjust(value, '\x00')
    return returned


class CONSTANT_Utf8(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.length = int.from_bytes(data[1:3])
        self.bytes = data[3:]

    def pack(self):
        return pack([{self.tag: 1}, {self.length: 2}, {self.bytes: 0}])


class CONSTANT_Ref(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.class_index = int.from_bytes(data[1:3])
        self.name_and_type_index = int.from_bytes(data[3:])

    def pack(self):
        return pack([{self.tag: 1}, {self.class_index: 2}, {self.name_and_type_index: 2}])


class CONSTANT_Fieldref(CONSTANT_Ref):
    pass


class CONSTANT_Methodref(CONSTANT_Ref):
    pass


class CONSTANT_InterfaceMethodref(CONSTANT_Ref):
    pass


class CONSTANT_String(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.string_index = int.from_bytes(data[1:])

    def pack(self):
        return pack([{self.tag: 1}, {self.string_index: 2}])


class CONSTANT_Integer(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.bytes = int.from_bytes(data[1:5])

    def pack(self):
        return pack([{self.tag: 1}, {self.bytes: 4}])


class CONSTANT_Float(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.bytes = struct.unpack('>f', data[1:5])

    def pack(self):
        return pack([{self.tag: 1}, {self.bytes: 4}])


class CONSTANT_Long(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.high_bytes = data[1:5]
        self.low_bytes = data[5:9]

    def pack(self):
        return pack([{self.tag: 1}, {self.high_bytes: 4}, {self.low_bytes: 4}])


class CONSTANT_Double(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.high_bytes = data[1:5]
        self.low_bytes = data[5:9]

    def pack(self):
        return pack([{self.tag: 1}, {self.high_bytes: 4}, {self.low_bytes: 4}])


class CONSTANT_Class(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.name_index = int.from_bytes(data[1:])

    def pack(self):
        return pack([{self.tag: 1}, {self.name_index: 2}])


class CONSTANT_NameAndType(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.name_index = int.from_bytes(data[1:3])
        self.descriptor_index = int.from_bytes(data[3:])

    def pack(self):
        return pack([{self.tag: 1}, {self.name_index: 2}, {self.descriptor_index: 2}])


class CONSTANT_MethodHandle(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.reference_kind = int.from_bytes(data[1:2])
        self.reference_index = int.from_bytes(data[2:])

    def pack(self):
        return pack([{self.tag: 1}, {self.reference_kind: 1}, {self.reference_index: 2}])


class CONSTANT_MethodType(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.descriptor_index = int.from_bytes(data[1:])

    def pack(self):
        return pack([{self.tag: 1}, {self.descriptor_index: 2}])


class CONSTANT_InvokeDynamic(CONSTANT):
    def __init__(self, data):
        self.tag = data[0]
        self.bootstrap_method_attr_index = int.from_bytes(data[1:3])
        self.name_and_type_index = int.from_bytes(data[3:])

    def pack(self):
        return pack([{self.tag: 1}, {self.bootstrap_method_attr_index: 2}, {self.name_and_type_index: 2}])


for i in range(cpc - 1):
    c, b = nextBytes(1, b)

    lengthTable = {
        7: 2,
        9: 4,
        10: 4,
        11: 4,
        8: 2,
        3: 4,
        4: 4,
        5: 8,
        6: 8,
        12: 4,
        1: 2,
        15: 3,
        16: 2,
        18: 4
    }
    try:
        data, b = nextBytes(lengthTable[c], b, func=bytes)
    except:
        print("Error loading file! Dumping constant pool!")
        pprint.pprint(cp)
        sys.exit(1)
    if c == 1:
        data2, b = nextBytes(int.from_bytes(data[:2]), b, bytes)
        data += data2
    classTable = {
        1: CONSTANT_Utf8,
        7: CONSTANT_Class,
        9: CONSTANT_Fieldref,
        10: CONSTANT_Methodref,
        11: CONSTANT_InterfaceMethodref,
        8: CONSTANT_String,
        3: CONSTANT_Integer,
        4: CONSTANT_Float,
        5: CONSTANT_Long,
        6: CONSTANT_Double,
        12: CONSTANT_NameAndType,
        15: CONSTANT_MethodHandle,
        16: CONSTANT_MethodType,
        18: CONSTANT_InvokeDynamic
    }
    cp += [classTable.get(c, bytes)(c.to_bytes(1)+data)]

print("Class File Version: "+a[major]+('.'+str(minor) if minor else ''))
print('Constant Pool Length: '+str(cpc))
for c, i in enumerate(cp):
    print(hex(c+1)[2:].zfill(4) + ': '+str(i))

if args.edit:
    while True:
        a = int(input("Index (Type -1 to save)? ")) - 1
        if a == -2:
            break
        c = list(enumerate(filter(lambda x: x[0] not in ['tag', 'length'], zip(
            cp[a].__dict__.keys(), cp[a].__dict__.values()))))
        for i in c:
            print(str(i[0] + 1) + '. '+str(i[1][0]) + ': '+str(i[1][1]))
        x = int(input("Choose value to edit? "))
        d = input('Enter value? ')

        os.system('cls' if os.name == 'nt' else 'clear')
        try:
            cp[a].__dict__[c[x-1][1][0]] = type(c[x-1][1][1])(d)
        except TypeError:
            cp[a].__dict__[c[x-1][1][0]
                           ] = type(c[x-1][1][1])(d, encoding='utf8')
        if not (cp[a].tag - 1):
            cp[a].length = len(cp[a].bytes)
        for c, i in enumerate(cp):
            print(hex(c+1)[2:].zfill(4) + ': '+str(i))
    with open(input("Save to [default is "+args.filename+"]? ") or args.filename, 'wb') as f:
        data = b'\xca\xfe\xba\xbe'+int.to_bytes(minor, 2)+int.to_bytes(
            major, 2)+int.to_bytes(cpc, 2) + b''.join([i.pack() for i in cp]) + b
        f.write(data)
        print("Saved and exiting!")
