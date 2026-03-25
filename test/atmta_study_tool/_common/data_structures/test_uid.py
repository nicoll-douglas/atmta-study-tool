from atmta_study_tool._common.data_structures import UID
from typing import Any
from atmta_study_tool.language.models import Symbol


class TestUID:
    def test_same_class_interning(self):
        """Test that the UID class correctly interns two UID objects with the same class and UID attribute.

        Arrange: Create a UID object.
        Act: Create an equivalent UID object to the first with the same class and same UID attribute.
        Assert: Check that both UID objects are the same object and that they are one interned value.
        """
        uid_str: str = "abcd"
        uid_a: UID[str] = UID(uid_str)
        registry_key: tuple[type[UID[Any]], str] = (UID, uid_str)

        # assert uid_a gets interned
        assert registry_key in UID._REGISTRY
        assert uid_a is UID._REGISTRY[registry_key]

        # same class and uid_str for equivalence with uid_a
        uid_b: UID[str] = UID(uid_str)

        # assert uid_b is in the interned value
        assert uid_b is uid_a
        assert uid_b is UID._REGISTRY[registry_key]

        # assert that only one 1 interned value was created
        assert len(UID._REGISTRY) == 1

    def test_distinct_class_interning(self):
        """Test that the UID class correctly interns two UID objects with distinct classes but same UID attribute.

        Arrange: Create a Symbol object (extends UID).
        Act: Create a UID object with the same UID attribute.
        Assert: Check that the Symbol object was interned and is not equal to the UID object also interned.
        """
        uid_str: str = "abcd"
        uid: UID[str] = UID(uid_str)

        # same uid_str as uid but class is different
        symbol: Symbol = Symbol(uid_str)
        symbol_reg_key: tuple[type[Symbol], str] = (Symbol, uid_str)

        # assert that the symbol was interned
        assert symbol_reg_key in UID._REGISTRY
        assert symbol is UID._REGISTRY[symbol_reg_key]

        # assert that the symbol is not equivalent to the UID object also interned
        assert symbol != uid
        assert symbol is not uid
