import dataclasses
import enum

import construct as cs
from construct_dataclasses import csfield, to_struct, subcsfield, csenum, tfield, dataclass_struct

my_key = "my_key"
my_data = 42
my_metadata = {my_key: my_data}


class MyEnum(enum.IntEnum):
    A = 0
    B = 1


@dataclasses.dataclass
class SubClass:
    x: int = csfield(cs.Byte)
    y: float = csfield(cs.Float32l)


@dataclass_struct
class DataClass:
    a: int = csfield(cs.Int8ub, metadata=my_metadata)
    b: list[SubClass] = subcsfield(SubClass, cs.Array(cs.this.a, to_struct(SubClass)), metadata=my_metadata)
    c: MyEnum = csenum(MyEnum, cs.Int8ub, metadata=my_metadata)
    d: list[MyEnum] = tfield(MyEnum, cs.Array(cs.this.a, cs.Enum(cs.Int8ub, MyEnum)), metadata=my_metadata)


def test_metadata():
    # this shall work as well

    # check metadata
    for v in DataClass.__dataclass_fields__.values():
        assert my_key in v.metadata
        assert v.metadata[my_key] == my_data
