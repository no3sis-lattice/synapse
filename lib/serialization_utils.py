"""
Serialization Utilities for Synapse System

Provides base protocols and helper functions for JSON serialization
of dataclasses with complex nested structures (enums, OrderedDict, etc.).

This eliminates DRY violations by centralizing serialization patterns.
"""

from collections import OrderedDict
from typing import Any, Dict, Protocol, TypeVar, Type
from dataclasses import asdict


class JSONSerializable(Protocol):
    """
    Protocol for objects that can be serialized to/from JSON-compatible dicts.

    All persistent Synapse dataclasses should implement this protocol.
    """

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to JSON-serializable dictionary"""
        ...

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'JSONSerializable':
        """Reconstruct object from dictionary"""
        ...


T = TypeVar('T')


def serialize_ordered_dict(
    ordered_dict: OrderedDict,
    value_serializer: callable = None
) -> Dict[str, Any]:
    """
    Serialize an OrderedDict to a regular dict (preserving order in Python 3.7+).

    Args:
        ordered_dict: The OrderedDict to serialize
        value_serializer: Optional function to serialize values (e.g., obj.to_dict)

    Returns:
        Regular dict with serialized values
    """
    if value_serializer:
        return {k: value_serializer(v) for k, v in ordered_dict.items()}
    return dict(ordered_dict)


def deserialize_to_ordered_dict(
    data: Dict[str, Any],
    value_deserializer: callable = None
) -> OrderedDict:
    """
    Deserialize a dict to an OrderedDict (preserving insertion order).

    Args:
        data: The dictionary to deserialize
        value_deserializer: Optional function to deserialize values (e.g., Class.from_dict)

    Returns:
        OrderedDict with deserialized values
    """
    result = OrderedDict()
    for k, v in data.items():
        result[k] = value_deserializer(v) if value_deserializer else v
    return result


def dataclass_to_dict_with_enums(obj: Any) -> Dict[str, Any]:
    """
    Convert a dataclass to dict, handling Enum values by converting to .value.

    This is a safer alternative to asdict() when dataclasses contain enums.

    Args:
        obj: Dataclass instance to serialize

    Returns:
        Dictionary with enums converted to their values
    """
    result = asdict(obj)

    # Post-process to handle enums
    def convert_enums(d):
        for key, value in d.items():
            if hasattr(value, 'value'):  # It's an enum
                d[key] = value.value
            elif isinstance(value, dict):
                convert_enums(value)
        return d

    return convert_enums(result)


# ============================================================================
# DOCUMENTATION: Serialization Pattern for Synapse Dataclasses
# ============================================================================
"""
Standard pattern for implementing JSONSerializable in dataclasses:

```python
from dataclasses import dataclass
from typing import Dict, Any
from serialization_utils import JSONSerializable

@dataclass
class MyClass:
    field1: str
    field2: int

    def to_dict(self) -> Dict[str, Any]:
        \"\"\"Convert to dictionary for JSON serialization\"\"\"
        return {
            'field1': self.field1,
            'field2': self.field2
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MyClass':
        \"\"\"Reconstruct from dictionary\"\"\"
        return MyClass(
            field1=data.get('field1', ''),
            field2=data.get('field2', 0)
        )
```

For dataclasses with enums:
```python
from enum import Enum

class MyEnum(Enum):
    VALUE_A = "a"
    VALUE_B = "b"

@dataclass
class MyClassWithEnum:
    my_enum: MyEnum

    def to_dict(self) -> Dict[str, Any]:
        return {
            'my_enum': self.my_enum.value  # Convert enum to string
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MyClassWithEnum':
        return MyClassWithEnum(
            my_enum=MyEnum(data.get('my_enum'))  # Reconstruct enum
        )
```

For dataclasses with OrderedDict:
```python
from collections import OrderedDict
from serialization_utils import serialize_ordered_dict, deserialize_to_ordered_dict

@dataclass
class MyClassWithOrderedDict:
    items: OrderedDict

    def to_dict(self) -> Dict[str, Any]:
        return {
            'items': serialize_ordered_dict(
                self.items,
                value_serializer=lambda v: v.to_dict()  # If values are objects
            )
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MyClassWithOrderedDict':
        return MyClassWithOrderedDict(
            items=deserialize_to_ordered_dict(
                data.get('items', {}),
                value_deserializer=SomeClass.from_dict  # If values are objects
            )
        )
```
"""
