import dataclasses
import enum
import construct as cs

from construct_dataclasses import DataclassStruct, csfield, to_struct, subcsfield, csenum

class Orientation(enum.IntEnum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2

@dataclasses.dataclass
class ImageHeader:
    signature: bytes         = csfield(cs.Const(b"BMP"))
    orientation: Orientation = csenum(Orientation, cs.Int8ub)

@dataclasses.dataclass
class Pixel:
    data: int = csfield(cs.Int8ub)

@dataclasses.dataclass
class Image:
    header: ImageHeader = csfield(ImageHeader)
    width: int          = csfield(cs.Int8ub)
    height: int         = csfield(cs.Int8ub)
    pixels: list[Pixel] = subcsfield(Pixel, cs.Array(cs.this.width * cs.this.height, to_struct(Pixel)))

ds_struct = DataclassStruct(Image)
obj = Image(
    header=ImageHeader(
        orientation=Orientation.VERTICAL
    ),
    width=3,
    height=2,
    pixels=[Pixel(1), Pixel(2), Pixel(3), Pixel(4), Pixel(5), Pixel(6)]
)

print(ds_struct.build(obj))
x = ds_struct.parse(b"BMP\x02\x03\x02\x01\x02\x03\x04\x05\06")
print(x)