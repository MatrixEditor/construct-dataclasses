# Copyright (C) 2023 MatrixEditor

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import construct as cs
import dataclasses
import typing as t

from construct.core import Context, ContextKWType, FilenameType, PathType, StreamType

def subcsfield(
    model: type, subcon, doc: str | None = ..., parsed: cs.Context | None = ...
) -> dataclasses.Field: ...
def csfield(
    subcon: cs.Construct | type,
    doc: str | None = ...,
    parsed: cs.Context | None = ...,
    depth: int | None = ...,
    reverse: bool = ...,
    aligned: int | None = ...,
) -> dataclasses.Field: ...
def tfield(
    model: type,
    subcon: cs.Construct,
    doc: str | None = ...,
    parsed: cs.Context | None = ...,
) -> dataclasses.Field: ...
def csenum(
    model: type,
    subcon: cs.Construct,
    doc: str | None = None,
    parsed: cs.Context | None = None,
) -> dataclasses.Field: ...
def to_struct(
    model: type,
    depth: int | None = ...,
    reverse: bool = ...,
    aligned: int | None = ...,
    union: t.Union[str, int, None] = ...,
) -> cs.Struct | cs.Union: ...
def to_object(obj: cs.Container | cs.ListContainer, model: type): ...

T = t.TypeVar("T")

def dataclass_struct(
    cls: t.Type[T] | None = ...,
    *,
    bitwise: bool = ...,
    depth: int | None = ...,
    reverse: bool = ...,
    union: t.Union[str, int, None] = ...
) -> t.Type[T]: ...
def container(cls: t.Type[T] | None = ...) -> t.Type[T]: ...

class DataclassStruct(cs.Adapter, t.Generic[T]):
    model: t.Type[T]
    reverse: bool
    depth: int | None
    aligned: int | None
    union: t.Union[str, int, None]
    def __init__(
        self,
        model: t.Type[T],
        depth: int | None = ...,
        reverse: bool = ...,
        aligned: int | None = ...,
        union: t.Union[str, int, None] = ...,
    ) -> None: ...
    def parse(self, data: bytes, **contextkw: ContextKWType) -> t.Union[T, None]: ...
    def parse_file(
        self, filename: FilenameType, **contextkw: ContextKWType
    ) -> t.Union[T, None]: ...
    def parse_stream(
        self, stream: StreamType, **contextkw: ContextKWType
    ) -> t.Union[T, None]: ...
    def build(self, obj: T, **contextkw: ContextKWType) -> bytes: ...
    def build_file(
        self, obj: T, filename: FilenameType, **contextkw: ContextKWType
    ) -> bytes: ...
    def build_stream(
        self, obj: T, stream: StreamType, **contextkw: ContextKWType
    ) -> bytes: ...
    def _decode(
        self, obj: t.Any, context: Context, path: PathType
    ) -> t.Union[T, None]: ...
    def _encode(self, obj: T, context: Context, path: PathType) -> dict: ...

def DataclassBitStruct(
    model: t.Type[T],
    depth: int | None = ...,
    reverse: bool = ...,
    union: t.Union[str, int, None] = ...,
): ...
