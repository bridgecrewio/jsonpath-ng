import io
from pathlib import Path

import setuptools


def get_version():
    """Parse package __version__.py to get version."""
    versionpy = (Path("bc_jsonpath_ng") / "__version__.py").read_text()
    return versionpy.split('"')[1]


setuptools.setup(
    name="bc-jsonpath-ng",
    version=get_version(),
    python_requires=">=3.7",
    description=(
        "A final implementation of JSONPath for Python that aims to be "
        "standard compliant, including arithmetic and binary comparison "
        "operators and providing clear AST for metaprogramming."
    ),
    author="bridgecrew",
    author_email="meet@bridgecrew.io",
    url="https://github.com/bridgecrewio/jsonpath-ng",
    license="Apache License 2.0",
    long_description=io.open("README.rst", encoding="utf-8").read(),
    packages=[
        "bc_jsonpath_ng",
        "bc_jsonpath_ng.bin",
        "bc_jsonpath_ng.ext",
    ],
    entry_points={
        "console_scripts": ["bc_jsonpath_ng=bc_jsonpath_ng.bin.jsonpath:entry_point"],
    },
    test_suite="tests",
    install_requires=[
        "ply",
        "decorator",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Typing :: Typed",
    ],
)
