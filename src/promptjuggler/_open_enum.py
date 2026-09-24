from __future__ import annotations

from enum import Enum

from typing_extensions import Self


class OpenEnum(str, Enum):
    """Base of the generated enums: a value the API added after this SDK version decodes to a
    member outside the declared ones instead of raising."""

    @classmethod
    def _missing_(cls, value: object) -> Self | None:
        if not isinstance(value, str):
            return None
        member = str.__new__(cls, value)
        member._name_ = value
        member._value_ = value
        return member
