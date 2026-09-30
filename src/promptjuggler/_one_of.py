from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, SerializationInfo, model_serializer


class OneOf(BaseModel):
    """Base of the generated oneOf wrappers: pydantic dumps and prints one as the variant it holds,
    not as the wrapper's own bookkeeping fields."""

    if TYPE_CHECKING:
        actual_instance: Any

    @model_serializer
    def _serialize_actual_instance(self, info: SerializationInfo) -> Any:
        if not isinstance(self.actual_instance, BaseModel):
            return self.actual_instance
        # Pydantic drops a nested include/exclude when dumping a serializer's return value, so the
        # variant gets every option passed on by hand. Its stubs type the masks set[int | str] here and
        # set[int] | set[str] in model_dump; it's the same value.
        return self.actual_instance.model_dump(
            mode=info.mode,
            include=info.include,  # type: ignore[arg-type]
            exclude=info.exclude,  # type: ignore[arg-type]
            context=info.context,
            by_alias=info.by_alias,
            exclude_unset=info.exclude_unset,
            exclude_defaults=info.exclude_defaults,
            exclude_none=info.exclude_none,
            round_trip=info.round_trip,
            serialize_as_any=info.serialize_as_any,
        )

    def __repr_args__(self) -> Iterator[tuple[str | None, Any]]:
        yield "actual_instance", self.actual_instance
