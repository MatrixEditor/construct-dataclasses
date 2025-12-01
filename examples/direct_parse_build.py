from construct_dataclasses import dataclass_struct, csfield
import construct as cs


@dataclass_struct
class Point:
    x: int = csfield(cs.Int8ul)
    y: int = csfield(cs.Int8ul)


point = Point(x=0, y=1)
raw = point.build()
print(raw)
parsed = Point.parse(raw)
print(parsed)
assert parsed == point
