# construct-dataclasses

[![python](https://img.shields.io/badge/python-3.7+-blue.svg?logo=python&labelColor=grey)](https://www.python.org/downloads/)
![Codestyle](https://img.shields.io:/static/v1?label=Codestyle&message=black&color=black)
![License](https://img.shields.io:/static/v1?label=License&message=GNU+GPLv3&color=blue)
[![PyPI](https://img.shields.io/pypi/v/construct-dataclasses)](https://pypi.org/project/construct-dataclasses/)

This small repository is an enhancement of the python package [*construct*](https://pypi.org/project/construct/), which is a powerful tool to declare symmetrical parsers and builders for binary data. This project combines construct with python's dataclasses with support for nested structs.

## Installation

You can install the package via pip or just copy the python file (*\_\_init\_\_.py*) as it is only one.

```bash
pip install construct-dataclasses
```

## Usage

More usage examples are placed in the [*examples/*](/examples/) directory.

### Define dataclasses

Before we can start declaring fields on a dataclass, the class itself has to be created. Currently, there are two ways on how to create
a dataclass usable by this package.

1. Use the standard `@dataclass` decorator and create the parser instance afterwards (**recommended for type checking**):

    ```python
    from construct_dataclasses import DataclassStruct

    @dataclasses.dataclass
    class Foo: ...

    # Create the parser manually
    parser = DataclassStruct(Foo)
    instance = parser.parse(...)
    ```

2. Use the `@dataclass_struct` decorator to define a new dataclass and automatically create a parser instance that will be assigned as a class attribute:

    ```python
    from construct_dataclasses import dataclass_struct

    @dataclass_struct
    class Foo: ...

    # Use the class-parser to parse
    instance = Foo.parser.parse(...)
    # or to build
    data = Foo.parser.build(instance)
    ```

> Hint: Use `@container` to mimic a construct container instance if needed. That may be the case if you have to access
> an already parsed object of a custom type:
> ```python
> @container
> @dataclasses.dataclass
> class ImageHeader:
>   length: int = csfield(Int32ub)
>
> @dataclasses.dataclass
> class Image:
>   header: ImageHeader = csfield(ImageHeader)
>   data: bytes = csfield(Bytes(this.header.length))
> ```
>  The access to `header.length` would throw an exception without the container annotation.

### Define fields

This module defines a new way how to declare fields of a dataclass. In order to combine the python package construct with python's dataclasses module, this project introduces the following four methods:

- `csfield`: Default definition of a field using a subcon or other dataclass

    ```python
    @dataclass_struct
    class ImageHeader:
        signature: bytes = csfield(cs.Const(b"BMP"))
        num_entries: int = csfield(cs.Int32ul)
    ```

- `subcsfield`: Definition of nested constructs that are contained in list-like structures.

    ```python
    @dataclass_struct
    class Image:
        header: ImageHeader = csfield(ImageHeader) # dataclass reference
        width: int          = csfield(cs.Int8ub)
        height: int         = csfield(cs.Int8ub)
        # Note that we have to convert our dataclass into a struct using
        # the method "to_struct(...)"
        pixels: list[Pixel] = subcsfield(Pixel, cs.Array(this.width * this.height, to_struct(Pixel)))
    ```

- `tfield`: a simple typed field that tries to return an instance of the given model class. **Use `subcsfield` for dataclass models, `csenum`for simple enum fields and `tfield` for enum types in list fields**.

    ```python
    @dataclass_struct
    class ImageHeader:
        orientations: list[Orientation] = tfield(Orientation, cs.Enum(cs.Int8ul, Orientation))
    ```

- `csenum`: shortcut for simple enum fields

    ```python
    @dataclass_struct
    class ImageHeader:
        orientations: Orientation = csenum(Orientation, cs.Int8ul)
    ```

### Convert dataclasses

By default, all conversion is done automatically if you don't use instances of `SubContruct` classes in your field definitions. If you have to define a subcon that needs a nested subcon, like `Array` or `RepeatUntil` and you would like to parse a dataclass struct, it is required to convert the defined dataclass into a struct.

- `to_struct`: This method converts all fields defined in a dataclass into a single `Struct` or `AlignedStruct` instance.

    ```python
    @dataclass_struct
    class Pixel:
        data: int = csfield(cs.Int8ub)

    pixel_struct: construct.Struct = to_struct(Pixel)
    ```
- `to_object`: In order to use data returned by `Struct.parse`, this method can be used to apply this data and create a dataclass object from it.

    ```python
    data = pixel_struct.parse(b"...")
    pixel = to_object(data, Pixel)
    ```

The complete example is shown below:

```python
# Example modifed from here: https://github.com/timrid/construct-typing/
import dataclasses
import enum
import construct as cs

from construct_dataclasses import dataclass_struct, csfield, to_struct, subcsfield, csenum

class Orientation(enum.IntEnum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2

@dataclass_struct
class ImageHeader:
    signature: bytes         = csfield(cs.Const(b"BMP"))
    orientation: Orientation = csenum(Orientation, cs.Int8ub)

@dataclass_struct
class Pixel:
    data: int = csfield(cs.Int8ub)

@dataclass_struct
class Image:
    header: ImageHeader = csfield(ImageHeader)
    width: int          = csfield(cs.Int8ub)
    height: int         = csfield(cs.Int8ub)
    pixels: list[Pixel] = subcsfield(Pixel, cs.Array(this.width * this.height, to_struct(Pixel)))

obj = Image(
    header=ImageHeader(
        orientation=Orientation.VERTICAL
    ),
    width=3,
    height=2,
    pixels=[Pixel(1), Pixel(2), Pixel(3), Pixel(4), Pixel(5), Pixel(6)]
)

print(Image.parser.build(obj))
print(Image.parser.parse(b"BMP\x02\x03\x02\x01\x02\x03\x04\x05\06"))
```

The expected output would be:

    b'BMP\x02\x03\x02\x01\x02\x03\x04\x05\x06'
    Image(
        header=ImageHeader(signature=b'BMP', orientation=<Orientation.VERTICAL: 2>),
        width=3, height=2,
        pixels=[Pixel(data=1), Pixel(data=2), Pixel(data=3), Pixel(data=4), Pixel(data=5), Pixel(data=6)]
    )