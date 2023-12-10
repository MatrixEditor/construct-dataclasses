from __future__ import annotations

import enum
import construct as cs

from construct_dataclasses import dataclass_struct, csenum

class Mode(enum.IntEnum): # must be an IntEnum subclass
    OFF = 0
    ON = 1

@dataclass_struct
class Device:
    mode: Mode = csenum(Mode, cs.Int8ub)

print(Device.parser.parse(b"\x00"))
print(Device.parser.parse(b"\x01"))
print(Device.parser.parse(b"\x02"))
# OUTPUT:
# Device(mode=<Mode.OFF: 0>)
# Device(mode=<Mode.ON: 1>)
# Device(mode=2)