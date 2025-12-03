#!/usr/bin/env python
from setuptools import setup

version_string = "1.1.10"

setup(
    name="construct-dataclasses",
    version=version_string,
    package_data={"construct_dataclasses": ["*.pyi", "py.typed"]},
    packages=["construct_dataclasses"],
    license="GNU GPLv3",
    license_files=("LICENSE",),
    description="enhancement for the python package 'construct' that adds support for dataclasses.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    platforms=["POSIX", "Windows"],
    url="https://github.com/MatrixEditor/construct-dataclasses",
    author="MatrixEditor",
    python_requires=">=3.8",
    install_requires=["construct"],
    keywords=[
        "construct",
        "kaitai",
        "declarative",
        "data structure",
        "struct",
        "binary",
        "symmetric",
        "parser",
        "builder",
        "parsing",
        "building",
        "pack",
        "unpack",
        "packer",
        "unpacker",
        "bitstring",
        "bytestring",
        "dataclasses",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",

        'Intended Audience :: Developers',
        "Intended Audience :: Information Technology",
        'Operating System :: OS Independent',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)