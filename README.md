# Protobase

Protobase is a comprehensive Python library designed to serve as a foundational element in class creation, similar to dataclasses and the attrs library. It aims to streamline and optimize the development process by introducing efficient, reliable, and user-friendly structures.


- traits (defered auto impl methods)
- immutability
- consign

**FUTURE**

- attr realtime type checking (debug mode)
- annotations ++
- Validators and codecs (json, bson, etc)
- schematics generation (openapi & more)
- Design Patterns (visitor)
- 

## Features

- **Efficient Attribute Management**: Utilizes `__slots__` to disable dynamic attribute assignment, boosting performance and reducing memory usage.
- **Automatic Protocol Implementation**: Inherits from Protocol, allowing classes to automatically implement methods, akin to Rust's trait derivation.
- **Encapsulation of Python's Intricacies**: Simplifies the usage of complex Python features like `__dict__` and `__weakref__`, making them more accessible and less error-prone.
- **Immutable and Unique Objects**: Provides mechanisms for creating immutable and unique objects (interning), ensuring data integrity and consistency.

## Installation

```bash
pip install protobase
```
