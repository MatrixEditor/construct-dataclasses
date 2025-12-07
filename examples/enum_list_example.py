import enum
import construct as cs

from typing import List

from construct_dataclasses import dataclass_struct, csfield, tfield

class Feature(enum.IntEnum): # must be an IntEnum subclass
    WIFI = 1
    BLUETOOTH = 2
    FTP = 3
    SSH = 4

@dataclass_struct
class Capabilities:
    count: int = csfield(cs.Int8ul)
    features: List[Feature] = tfield(Feature, cs.Array(cs.this.count, cs.Enum(cs.Int8ul, Feature)))

print(Capabilities.parser.parse(b"\x03\x01\x03\x05"))
# Capabilities(count=3, features=[<Feature.WIFI: 1>, <Feature.FTP: 3>, 5])