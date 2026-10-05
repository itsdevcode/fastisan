import keyword
from dataclasses import dataclass


SUPPORTED_TYPES = {"str", "int", "float", "bool", "datetime"}
RESERVED_NAMES = {"id", "created_at", "updated_at"}


@dataclass(frozen=True)
class FieldSpec:
    name: str
    type: str
    nullable: bool = False


@dataclass(frozen=True)
class ResourceSpec:
    name: str
    fields: tuple[FieldSpec, ...]


def parse_fields(fields_str: str) -> tuple[FieldSpec, ...]:
    if not fields_str.strip():
        return ()

    specs: list[FieldSpec] = []
    seen_names: set[str] = set()

    for part in fields_str.split(","):
        part = part.strip()
        if not part:
            raise ValueError("Malformed empty field segment")

        if ":" not in part:
            raise ValueError(f"Missing colon in field definition: {part}")

        name, type_str = part.split(":", 1)
        name = name.strip()
        type_str = type_str.strip()

        if not name:
            raise ValueError(f"Missing field name in definition: {part}")

        if not name.isidentifier():
            raise ValueError(f"Invalid field name: {name}")

        if keyword.iskeyword(name):
            raise ValueError(f"Invalid field name (Python keyword): {name}")

        if name in RESERVED_NAMES:
            raise ValueError(f"Field name is reserved: {name}")

        if name in seen_names:
            raise ValueError(f"Duplicate field name: {name}")

        seen_names.add(name)

        nullable = type_str.endswith("?")
        if nullable:
            type_str = type_str[:-1]

        if type_str not in SUPPORTED_TYPES:
            raise ValueError(f"Unsupported field type: {type_str}")

        specs.append(FieldSpec(name=name, type=type_str, nullable=nullable))

    return tuple(specs)
