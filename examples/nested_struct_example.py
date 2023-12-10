import enum
import construct as cs

from construct_dataclasses import dataclass_struct, csfield, subcsfield

@dataclass_struct
class InnerInnerStruct:
    key: int = csfield(cs.Int16ul)

@dataclass_struct
class InnerStruct:
    length: int = csfield(cs.Int8ul)
    keys: list[InnerInnerStruct] = subcsfield(
        InnerInnerStruct, cs.Array(cs.this.length, InnerInnerStruct.struct)
    )

@dataclass_struct
class Foo:
    magic: bytes = csfield(cs.Const(b"bar"))
    # NOTE: do NOT use InnerStruct.struct here as this would result
    # in type issues when trying to convert binary data back.
    inner: InnerStruct = csfield(InnerStruct)


print(Foo.parser.parse(b"bar\x01\xFF\xFF"))
# Foo(magic=b'bar', inner=InnerStruct(length=1, keys=[InnerInnerStruct(key=65535)]))