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
from __future__ import annotations

import dataclasses
import inspect
import textwrap
import enum
import sys

import construct as cs

__all__ = [
    "csfield",
    "subcsfield",
    "dataclass_struct",
    "tfield",
    "to_struct",
    "to_object",
    "container",
    "DataclassStruct",
    "DataclassBitStruct",
]


def subcsfield(
    model: type,
    subcon,
    doc: str | None = None,
    parsed=None,
) -> dataclasses.Field:
    """
    Helper method to define `cs.Subconstruct` fields in a dataclass that reference another
    dataclass, e.g.::

        >>> @dataclasses.dataclass
        >>> class InnerBlob:
        ...     length: int = csfield(Int8ub)
        ...
        >>> @dataclasses.dataclass
        >>> class Blob:
        ...     blobs = subcsfield(InnerBlob, Array(3, to_struct(InnerBlob)))
        ...

    The defined `blobs` field will store a list of `InnerBlob` objects. Note that you have to
    convert your dataclass into a `Struct` object first, before you can use it with another
    "Construct" or "SubConstruct". The easiest approach is to use `to_struct(...)` (also exported
    by this package).

    :param model: the dataclass type
    :type model: type
    :param subcon: the sub-construct
    :type subcon: Construct | SubConstruct
    :return: the created dataclasses Field
    :rtype: dataclasses.Field
    """
    if not dataclasses.is_dataclass(model):
        raise TypeError(f"Provided class {model} is not a dataclass!")

    return _process_csfield(
        model=model,
        subcon=subcon,
        doc=doc,
        parsed=parsed,
    )


def csfield(
    subcon: cs.Construct | type,
    doc: str | None = None,
    parsed=None,
    depth=None,
    reverse=False,
    aligned=None,
) -> dataclasses.Field:
    """
    Helper method for :class:`DataclassStruct` and `DataclassBitStruct` to create dataclass
    fields based on sub-construct definitions. This method takes a simple construct object
    or a class type that references another dataclass.

    To apply nested constructs like `Array` or `ReadUntil`, you have to use `subcsfield`
    with some workarounds.

    Note that the returned dataclasses field will contain the following metadata attributes:

    - `subcon`: The created sub-construct that will be used to create the final `Struct`
    - `subcon_orig_type`: The original subcon type or dataclass type (if a model is provided)

    :param subcon: the sub-construct or dataclass class reference
    :type subcon: cs.Construct | type
    :param doc: additional documentation for the field, defaults to None
    :type doc: str | None, optional
    :param depth: the maximum recursion depth (None for infinity), defaults to None
    :type depth: int | None, optional
    :param reverse: whether all fields should be processed in reverse order, defaults to False
    :type reverse: bool, optional
    :param aligned: argument for `AlignedStruct` objects, defaults to None
    :type aligned: int, optional
    :return: the created dataclasses field instance
    :rtype: dataclasses.Field

    Example::

        >>> @dataclasses.dataclass
        >>> class BlobHeader:
        ...     version = csfield(Int32ub)
        ...     timestamp = csfield(Int32ub)
        ...
        >>> @dataclasses.dataclass
        >>> class Blob:
        ...     length: int = csfield(Int32ub)
        ...     header: BlobHeader = csfield(BlobHeader)
        ...
    """
    target_subcon = subcon
    model = type(subcon)
    if dataclasses.is_dataclass(subcon):
        target_subcon = to_struct(subcon, depth, reverse, aligned)
        model = subcon

    return _process_csfield(
        model=model,
        subcon=target_subcon,
        doc=doc,
        parsed=parsed,
    )


def csenum(
    model: type, subcon: cs.Construct, doc: str | None = None, parsed=None
) -> dataclasses.Field:
    """Creates an enum field that tries to parse the given enum.

    .. warning::
        The returned value may be of type ``int`` if no suitable representation could be found.
    """
    return _process_csfield(model, cs.Enum(subcon, model), doc=doc, parsed=parsed)


def tfield(
    model: type,
    subcon: cs.Construct,
    doc: str | None = None,
    parsed=None,
) -> dataclasses.Field:
    """Creates a typed field. (instance of model will be returned).

    To apply a typed field to dataclasses, use `subcsfield`.
    """
    return _process_csfield(model, subcon, doc, parsed)


def _process_csfield(
    # The model can be the actual model class (dataclass) or the type
    # of construct used.
    model,
    # The subcon stores the actual sub-construct object that will be passed
    # to the Struct class constructor later on.
    subcon,
    doc: str | None = None,
    parsed=None,
) -> dataclasses.Field:
    target_subcon = subcon
    if (doc is not None) or (parsed is not None):
        doc = doc or textwrap.dedent(str(doc)).strip("\n")
        target_subcon = cs.Renamed(target_subcon, newdocs=doc, newparsed=parsed)

    if target_subcon.flagbuildnone is True:
        init = False
        default = False
    else:
        init = True
        default = dataclasses.MISSING

    # create default values
    if isinstance(target_subcon, cs.Const):
        default = target_subcon.value
    elif isinstance(target_subcon, cs.Default):
        if callable(target_subcon.value):
            default = None
        else:
            default = target_subcon.value

    return dataclasses.field(
        default=default,
        init=init,
        metadata={
            "subcon": target_subcon,
            "subcon_orig_type": model or type(subcon),
        },
    )


def to_struct(
    model: type, depth=None, reverse=False, aligned=None, union=None
) -> cs.Struct | cs.Union:
    """Transforms the given dataclass into a construct `Struct` or `Union`.

    :param model: the dataclass class reference
    :type model: type
    :param depth: maximum recursion depth, defaults to None
    :type depth: int, optional
    :param reverse: whether fields should be processed in reverse order, defaults to False
    :type reverse: bool, optional
    :param aligned: whether aligned struct should be created from the "aligned" value, defaults to None
    :type aligned: int, optional
    :raises TypeError: if the given model is not a dataclass class
    :return: the created struct instance
    :rtype: construct.Struct
    """
    if isinstance(model, cs.Construct):
        # not sure if we want to do that
        return model

    if not inspect.isclass(model) or not dataclasses.is_dataclass(model):
        raise TypeError("Model must be a dataclass!")

    return _to_struct_inner(
        model, max_depth=depth, reverse=reverse, aligned=aligned, union=union
    )


def _to_struct_inner(
    obj, max_depth=None, depth=0, reverse=False, aligned=None, union=None
):
    if dataclasses.is_dataclass(obj):
        fields = dataclasses.fields(obj)
        if reverse:
            fields = reversed(fields)

        subcon_fields = {}
        for dc_field in fields:
            if (max_depth is not None and depth < max_depth) or max_depth is None:
                cs_field = _to_struct_inner(
                    dc_field.metadata["subcon"], max_depth, depth + 1, reverse
                )
            else:
                cs_field = dc_field.metadata["subcon"]

            subcon_fields[dc_field.name] = cs_field
        if aligned is not None:
            return cs.AlignedStruct(aligned, **subcon_fields)

        if union is not None:
            parsefrom = union
            if union is True:
                parsefrom = None
            return cs.Union(parsefrom, **subcon_fields)

        return cs.Struct(**subcon_fields)

    elif isinstance(obj, cs.Construct):
        return obj


def to_object(obj: cs.Container | cs.ListContainer, model: type):
    """Converts a parsed container back into a dataclass object.

    :param obj: the parsed data
    :type obj: cs.Container | cs.ListContainer
    :param model: the type of which an instance should be created
    :type model: type
    :raises TypeError: if the given model is not a dataclass
    :return: the created instance
    """
    if not dataclasses.is_dataclass(model):
        raise TypeError(f"The class <{model}> is not a dataclass!")

    if obj is None:  # support optional types
        return None

    # NOTE: if you use the DataclassStruct as the model, the
    # created object will be returned directly.
    if dataclasses.is_dataclass(obj):
        return obj

    fields = dataclasses.fields(model)
    # We first have to extract all fields that are needed to instantiate
    # the model class.
    init_fields = {}
    for dc_field in fields:
        if dc_field.init:
            if isinstance(obj, cs.ListContainer):
                value = [_to_object_inner(x, dc_field) for x in obj]
            else:
                value = obj.get(dc_field.name)
            init_fields[dc_field.name] = _to_object_inner(value, dc_field)

    instance = model(**init_fields)
    # Now we can apply all other fields
    for dc_field in fields:
        if not dc_field.init:
            if isinstance(obj, cs.ListContainer):
                value = [_to_object_inner(x, dc_field) for x in obj]
            else:
                value = obj.get(dc_field.name)
            setattr(instance, dc_field.name, _to_object_inner(value, dc_field))

    return instance


def _to_object_inner(value, field: dataclasses.Field):
    # Check if we have an inner struct first
    subcon_type = field.metadata["subcon_orig_type"]
    field_type = field.type
    if isinstance(field_type, str):
        # normal type annotations are stored as string
        field_type = subcon_type

    if isinstance(value, cs.ListContainer):
        return list(map(lambda x: _to_object_inner(x, field), value))
    elif dataclasses.is_dataclass(subcon_type):
        return to_object(value, subcon_type)
    elif isinstance(value, cs.EnumIntegerString):
        # Allow list declarations of enum values. If there is a type hint
        # with a list-like type, we can take the first type argument and use
        # it as our enum type
        if hasattr(field_type, "__origin__") and issubclass(
            field_type.__origin__, list
        ):
            (field_type,) = field_type.__args__

        if issubclass(field_type, enum.IntEnum):
            # Search for enum value within defined ones
            for enum_val in field_type:
                if enum_val.value == value.intvalue:
                    return enum_val

        else:
            return value.intvalue

    return value


def _process_struct_dataclass(
    cls, bitwise=False, depth=None, reverse=False, union=False
):
    new_cls = dataclasses.dataclass(cls)
    if hasattr(new_cls, "parser"):
        raise ValueError(
            f"Invalid field definition: field 'parser' alredy exists in class {new_cls}"
        )

    if hasattr(new_cls, "struct"):
        raise ValueError(
            f"Invalid field definition: field 'struct' alredy exists in class {new_cls}"
        )

    if bitwise:
        ds_struct = DataclassBitStruct(cls, depth, reverse, union=union)
    else:
        ds_struct = DataclassStruct(cls, depth, reverse, union=union)

    setattr(new_cls, "parser", ds_struct)
    setattr(new_cls, "struct", ds_struct.subcon)
    return new_cls


def _process_container(cls):
    # Workaround for construct's Path objects that always use __getitem__.
    # For instance, the following situation would throw an error if we
    # use a DataclassStruct instance:
    #
    #      m_data: bytes = csfield(Bytes(this._root.header.length))
    #
    # As "header" might be a custom dataclass type, we have to support a
    # dict-like access to prevent issues.
    setattr(cls, "__getitem__", lambda self, key: getattr(self, key))
    return cls


def container(cls=None, /):
    """Makes the dataclass act as a container.

    >>> @container
    ... @dataclasses.dataclass
    ... class Image:
    ...     header: ImageHeader = csfield(ImageHeader)
    ...
    >>> image = ...
    >>> image["header"]
    <ImageHeader at ...>

    :param cls: the class type, defaults to None
    """

    def wrap(cls):
        # Apply workaround
        return _process_container(cls)

    if cls is not None:
        return _process_container(cls)

    return wrap


def dataclass_struct(
    cls=None, /, *, bitwise=False, depth=None, reverse=False, union=None
):
    """Creates a dataclass that stores a class-parser instance.

    Example::

        >>> @dataclass_struct
        ... class Blob:
        ...     length: int = csfield(cs.Int8ul)
        ...     data: bytes = csfield(cs.Bytes(cs.this.length))
        ...
        >>> b = Blob.parser.parse(b"\\x05\\x00\\x00\\x00\\x00\\x00")
        >>> Blob.parser.build(b)
        b'\\x05\\x00\\x00\\x00\\x00\\x00'

    :param bitwise: whether the struct should run bitwise, defaults to False
    :type bitwise: bool, optional
    :param depth: the maximum recursion depth, defaults to None
    :type depth: int, optional
    :param reverse: tells the builder to parse fields in reverse order, defaults to False
    :type reverse: bool, optional
    :param union: whether the struct should be treated as a union, defaults to False
    :type union: bool, optional
    """

    def wrap(cls):
        # Make dataclass and create parser instance
        return _process_struct_dataclass(
            cls, bitwise=bitwise, depth=depth, reverse=reverse, union=union
        )

    # See if we're being called as @struct or @struct().
    if cls is None:
        return wrap

    return wrap(cls)


class DataclassStruct(cs.Adapter):
    """Adapter for dataclasses structs.

    :param model: the defined dataclasses class
    :type model: type
    :param depth: maximum recursion depth when creating structs, defaults to None
    :type depth: int, optional
    :param reverse: whether fields should be processed in reverse order, defaults to False
    :type reverse: bool, optional

    Example taken from "construct_typed"::

    >>> import dataclasses
    >>> from construct import Bytes, Int8ub, this
    >>> from construct_dataclasses import DataclassStruct, csfield
    >>> @dataclasses.dataclass
    ... class Image:
    ...     width: int = csfield(Int8ub)
    ...     height: int = csfield(Int8ub)
    ...     pixels: bytes = csfield(Bytes(this.height * this.width))
    ...
    >>> ds = DataclassStruct(Image)
    >>> ds.parse(b"\x01\x0212")
    Image(width=1, height=2, pixels=b'12')
    """

    def __init__(
        self, model: type, depth=None, reverse=False, aligned=None, union=None
    ) -> None:
        self.model = model
        if not dataclasses.is_dataclass(self.model):
            raise TypeError(f"The class {self.model} is not a dataclass!")

        self.reverse = reverse
        self.depth = depth
        self.aligned = aligned
        self.union = union
        super().__init__(
            to_struct(self.model, self.depth, self.reverse, self.aligned, self.union)
        )

    def _decode(self, obj: cs.Container, context: cs.Context, path: cs.PathType):
        return to_object(obj, self.model)

    def _encode(self, obj, context: cs.Context, path: cs.PathType) -> dict:
        if isinstance(obj, dict):
            # NOTE: we have to check against a dictionary here as
            # dataclasses.asdict(obj) will convert nested objects automatically
            # into dicts.
            return obj

        if not dataclasses.is_dataclass(obj):
            raise TypeError(f"Model class <{type(obj)}> is not a dataclass!")

        return dataclasses.asdict(obj)


def DataclassBitStruct(model: type, depth=None, reverse=False, union=None):
    """Makes a DataclassStruct inside a Bitwise."""
    return cs.Bitwise(DataclassStruct(model, depth=depth, reverse=reverse, union=union))
