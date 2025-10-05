#!/usr/bin/env python3
"""
Unit tests for Serialization Utilities

Tests coverage:
- serialize_ordered_dict() with and without value_serializer
- deserialize_to_ordered_dict() with and without value_deserializer
- dataclass_to_dict_with_enums() with enum handling
- Round-trip serialization (serialize → deserialize → verify equality)
- Edge cases and error scenarios
"""

import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

import pytest
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any

from serialization_utils import (
    serialize_ordered_dict,
    deserialize_to_ordered_dict,
    dataclass_to_dict_with_enums
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

class TestEnum(Enum):
    """Test enum for serialization tests"""
    OPTION_A = "a"
    OPTION_B = "b"
    OPTION_C = "c"


class StatusEnum(Enum):
    """Test status enum with integer values"""
    PENDING = 0
    ACTIVE = 1
    COMPLETED = 2


@dataclass
class SimpleDataclass:
    """Simple dataclass for testing"""
    name: str
    value: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SimpleDataclass':
        return SimpleDataclass(
            name=data.get('name', ''),
            value=data.get('value', 0)
        )


@dataclass
class DataclassWithEnum:
    """Dataclass containing enum for testing"""
    status: TestEnum
    priority: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'priority': self.priority
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DataclassWithEnum':
        return DataclassWithEnum(
            status=TestEnum(data.get('status')),
            priority=data.get('priority', 0)
        )


@dataclass
class NestedDataclass:
    """Dataclass with nested structures"""
    outer: str
    inner: TestEnum
    metadata: Dict[str, Any]


# ============================================================================
# SERIALIZE_ORDERED_DICT TESTS
# ============================================================================

class TestSerializeOrderedDict:
    """Test suite for serialize_ordered_dict()"""

    def test_basic_serialization(self):
        """Test basic OrderedDict serialization without value_serializer"""
        od = OrderedDict([
            ('key1', 'value1'),
            ('key2', 'value2'),
            ('key3', 'value3')
        ])

        result = serialize_ordered_dict(od)

        assert isinstance(result, dict)
        assert result == {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

    def test_order_preserved(self):
        """Test that insertion order is preserved (Python 3.7+)"""
        od = OrderedDict([
            ('z', 1),
            ('a', 2),
            ('m', 3)
        ])

        result = serialize_ordered_dict(od)

        # Order should be preserved in Python 3.7+
        assert list(result.keys()) == ['z', 'a', 'm']

    def test_with_value_serializer(self):
        """Test serialization with custom value_serializer"""
        od = OrderedDict([
            ('obj1', SimpleDataclass(name='Alice', value=10)),
            ('obj2', SimpleDataclass(name='Bob', value=20))
        ])

        result = serialize_ordered_dict(od, value_serializer=lambda v: v.to_dict())

        assert isinstance(result, dict)
        assert result['obj1'] == {'name': 'Alice', 'value': 10}
        assert result['obj2'] == {'name': 'Bob', 'value': 20}

    def test_empty_ordered_dict(self):
        """Test serialization of empty OrderedDict"""
        od = OrderedDict()

        result = serialize_ordered_dict(od)

        assert result == {}

    def test_nested_values(self):
        """Test serialization with nested dictionary values"""
        od = OrderedDict([
            ('item1', {'nested': 'value1'}),
            ('item2', {'nested': 'value2'})
        ])

        result = serialize_ordered_dict(od)

        assert result['item1']['nested'] == 'value1'
        assert result['item2']['nested'] == 'value2'

    def test_none_value_serializer(self):
        """Test that None value_serializer is handled correctly"""
        od = OrderedDict([('key', 'value')])

        result = serialize_ordered_dict(od, value_serializer=None)

        assert result == {'key': 'value'}

    def test_value_serializer_with_complex_types(self):
        """Test value_serializer with complex object types"""
        class ComplexObject:
            def __init__(self, data):
                self.data = data

            def to_dict(self):
                return {'data': self.data}

        od = OrderedDict([
            ('obj1', ComplexObject([1, 2, 3])),
            ('obj2', ComplexObject([4, 5, 6]))
        ])

        result = serialize_ordered_dict(od, value_serializer=lambda v: v.to_dict())

        assert result['obj1']['data'] == [1, 2, 3]
        assert result['obj2']['data'] == [4, 5, 6]


# ============================================================================
# DESERIALIZE_TO_ORDERED_DICT TESTS
# ============================================================================

class TestDeserializeToOrderedDict:
    """Test suite for deserialize_to_ordered_dict()"""

    def test_basic_deserialization(self):
        """Test basic dict to OrderedDict deserialization"""
        data = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

        result = deserialize_to_ordered_dict(data)

        assert isinstance(result, OrderedDict)
        assert result['key1'] == 'value1'
        assert result['key2'] == 'value2'
        assert result['key3'] == 'value3'

    def test_order_preserved_from_dict(self):
        """Test that dict insertion order is preserved"""
        data = {'z': 1, 'a': 2, 'm': 3}

        result = deserialize_to_ordered_dict(data)

        assert list(result.keys()) == ['z', 'a', 'm']

    def test_with_value_deserializer(self):
        """Test deserialization with custom value_deserializer"""
        data = {
            'obj1': {'name': 'Alice', 'value': 10},
            'obj2': {'name': 'Bob', 'value': 20}
        }

        result = deserialize_to_ordered_dict(
            data,
            value_deserializer=SimpleDataclass.from_dict
        )

        assert isinstance(result, OrderedDict)
        assert isinstance(result['obj1'], SimpleDataclass)
        assert result['obj1'].name == 'Alice'
        assert result['obj1'].value == 10
        assert isinstance(result['obj2'], SimpleDataclass)
        assert result['obj2'].name == 'Bob'
        assert result['obj2'].value == 20

    def test_empty_dict(self):
        """Test deserialization of empty dict"""
        data = {}

        result = deserialize_to_ordered_dict(data)

        assert isinstance(result, OrderedDict)
        assert len(result) == 0

    def test_none_value_deserializer(self):
        """Test that None value_deserializer is handled correctly"""
        data = {'key': 'value'}

        result = deserialize_to_ordered_dict(data, value_deserializer=None)

        assert isinstance(result, OrderedDict)
        assert result['key'] == 'value'

    def test_nested_dict_values(self):
        """Test deserialization with nested dictionary values"""
        data = {
            'item1': {'nested': 'value1'},
            'item2': {'nested': 'value2'}
        }

        result = deserialize_to_ordered_dict(data)

        assert result['item1']['nested'] == 'value1'
        assert result['item2']['nested'] == 'value2'


# ============================================================================
# ROUND-TRIP SERIALIZATION TESTS
# ============================================================================

class TestRoundTripSerialization:
    """Test round-trip serialize → deserialize → verify equality"""

    def test_simple_round_trip(self):
        """Test round-trip with simple values"""
        original = OrderedDict([
            ('a', 1),
            ('b', 2),
            ('c', 3)
        ])

        # Serialize
        serialized = serialize_ordered_dict(original)

        # Deserialize
        deserialized = deserialize_to_ordered_dict(serialized)

        assert deserialized == original
        assert list(deserialized.keys()) == list(original.keys())

    def test_round_trip_with_objects(self):
        """Test round-trip with complex objects"""
        original = OrderedDict([
            ('obj1', SimpleDataclass(name='Alice', value=10)),
            ('obj2', SimpleDataclass(name='Bob', value=20))
        ])

        # Serialize
        serialized = serialize_ordered_dict(original, value_serializer=lambda v: v.to_dict())

        # Deserialize
        deserialized = deserialize_to_ordered_dict(
            serialized,
            value_deserializer=SimpleDataclass.from_dict
        )

        assert deserialized['obj1'].name == original['obj1'].name
        assert deserialized['obj1'].value == original['obj1'].value
        assert deserialized['obj2'].name == original['obj2'].name
        assert deserialized['obj2'].value == original['obj2'].value

    def test_round_trip_preserves_order(self):
        """Test that round-trip preserves insertion order"""
        original = OrderedDict([
            ('z', 'last'),
            ('a', 'first'),
            ('m', 'middle')
        ])

        serialized = serialize_ordered_dict(original)
        deserialized = deserialize_to_ordered_dict(serialized)

        assert list(deserialized.keys()) == ['z', 'a', 'm']

    def test_round_trip_empty(self):
        """Test round-trip with empty OrderedDict"""
        original = OrderedDict()

        serialized = serialize_ordered_dict(original)
        deserialized = deserialize_to_ordered_dict(serialized)

        assert len(deserialized) == 0
        assert isinstance(deserialized, OrderedDict)


# ============================================================================
# DATACLASS_TO_DICT_WITH_ENUMS TESTS
# ============================================================================

class TestDataclassToDictWithEnums:
    """Test suite for dataclass_to_dict_with_enums()"""

    def test_simple_dataclass_no_enums(self):
        """Test conversion of dataclass without enums"""
        obj = SimpleDataclass(name='Test', value=42)

        result = dataclass_to_dict_with_enums(obj)

        assert result == {'name': 'Test', 'value': 42}

    def test_dataclass_with_enum(self):
        """Test conversion of dataclass with enum field"""
        obj = DataclassWithEnum(status=TestEnum.OPTION_A, priority=5)

        result = dataclass_to_dict_with_enums(obj)

        # Enum should be converted to its value
        assert result['status'] == 'a'
        assert result['priority'] == 5

    def test_dataclass_with_integer_enum(self):
        """Test conversion of dataclass with integer-valued enum"""
        @dataclass
        class ObjWithIntEnum:
            status: StatusEnum
            count: int

        obj = ObjWithIntEnum(status=StatusEnum.ACTIVE, count=10)

        result = dataclass_to_dict_with_enums(obj)

        assert result['status'] == 1  # Integer enum value
        assert result['count'] == 10

    def test_dataclass_with_nested_enum(self):
        """Test conversion of dataclass with nested enum"""
        obj = NestedDataclass(
            outer='test',
            inner=TestEnum.OPTION_B,
            metadata={'key': 'value'}
        )

        result = dataclass_to_dict_with_enums(obj)

        assert result['outer'] == 'test'
        assert result['inner'] == 'b'  # Enum converted to value
        assert result['metadata'] == {'key': 'value'}

    def test_multiple_enums(self):
        """Test conversion with multiple enum fields"""
        @dataclass
        class MultiEnumClass:
            status1: TestEnum
            status2: TestEnum
            normal: str

        obj = MultiEnumClass(
            status1=TestEnum.OPTION_A,
            status2=TestEnum.OPTION_C,
            normal='text'
        )

        result = dataclass_to_dict_with_enums(obj)

        assert result['status1'] == 'a'
        assert result['status2'] == 'c'
        assert result['normal'] == 'text'

    def test_dataclass_with_none_values(self):
        """Test conversion with None values"""
        @dataclass
        class NullableClass:
            name: str
            optional: int = None

        obj = NullableClass(name='test', optional=None)

        result = dataclass_to_dict_with_enums(obj)

        assert result['name'] == 'test'
        assert result['optional'] is None

    def test_nested_dataclass_with_enums(self):
        """Test conversion of nested dataclass containing enums"""
        @dataclass
        class Inner:
            status: TestEnum

        @dataclass
        class Outer:
            inner: Inner
            name: str

        obj = Outer(
            inner=Inner(status=TestEnum.OPTION_B),
            name='outer'
        )

        result = dataclass_to_dict_with_enums(obj)

        assert result['name'] == 'outer'
        assert result['inner']['status'] == 'b'  # Nested enum converted

    def test_list_of_enums(self):
        """Test conversion with list containing enums"""
        @dataclass
        class ListEnumClass:
            statuses: list

        obj = ListEnumClass(statuses=[TestEnum.OPTION_A, TestEnum.OPTION_B])

        result = dataclass_to_dict_with_enums(obj)

        # Note: enums in lists won't be converted by current implementation
        # This test documents current behavior
        assert 'statuses' in result


# ============================================================================
# EDGE CASES AND ERROR SCENARIOS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error scenarios"""

    def test_serialize_regular_dict_as_ordered_dict(self):
        """Test that regular dict works with serialize_ordered_dict"""
        # In Python 3.7+, regular dicts maintain insertion order
        regular_dict = {'a': 1, 'b': 2}

        # Should work even with regular dict (though not its intended use)
        result = serialize_ordered_dict(OrderedDict(regular_dict))

        assert result == {'a': 1, 'b': 2}

    def test_deserialize_with_duplicate_keys(self):
        """Test deserialization handles duplicate keys (last value wins)"""
        # In normal dict creation, duplicate keys use last value
        data = {'key': 'value1'}
        data['key'] = 'value2'

        result = deserialize_to_ordered_dict(data)

        assert result['key'] == 'value2'

    def test_special_characters_in_keys(self):
        """Test serialization with special characters in keys"""
        od = OrderedDict([
            ('key-with-dashes', 1),
            ('key.with.dots', 2),
            ('key_with_underscores', 3)
        ])

        serialized = serialize_ordered_dict(od)
        deserialized = deserialize_to_ordered_dict(serialized)

        assert deserialized == od

    def test_unicode_in_values(self):
        """Test serialization with Unicode characters"""
        od = OrderedDict([
            ('en', 'Hello'),
            ('ja', 'こんにちは'),
            ('ar', 'مرحبا')
        ])

        serialized = serialize_ordered_dict(od)
        deserialized = deserialize_to_ordered_dict(serialized)

        assert deserialized['ja'] == 'こんにちは'
        assert deserialized['ar'] == 'مرحبا'

    def test_numeric_keys(self):
        """Test OrderedDict with numeric keys"""
        od = OrderedDict([
            (1, 'one'),
            (2, 'two'),
            (3, 'three')
        ])

        result = serialize_ordered_dict(od)

        # Numeric keys are preserved
        assert result[1] == 'one'
        assert result[2] == 'two'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
