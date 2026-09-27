from pathlib import Path

import pytest

from fastisan.generators.base import BaseGenerator


def test_generate_creates_file(tmp_path: Path) -> None:
    generator = BaseGenerator()
    destination = tmp_path / "routers" / "user.py"

    result = generator.generate(
        template_name="router.py.j2",
        destination=destination,
        context={
            "name": "User",
            "snake_name": "user",
        },
    )

    assert result == destination
    assert destination.exists()

    content = destination.read_text(encoding="utf-8")

    assert 'prefix="/user"' in content
    assert 'tags=["User"]' in content


def test_generate_creates_parent_directories(tmp_path: Path) -> None:
    generator = BaseGenerator()

    destination = (
        tmp_path
        / "some"
        / "nested"
        / "directory"
        / "user.py"
    )

    _ = generator.generate(
        template_name="router.py.j2",
        destination=destination,
        context={
            "name": "User",
            "snake_name": "user",
        },
    )

    assert destination.exists()


def test_generate_does_not_overwrite_existing_file(tmp_path: Path) -> None:
    generator = BaseGenerator()
    destination = tmp_path / "user.py"

    _ = destination.write_text("existing content", encoding="utf-8")

    with pytest.raises(FileExistsError):
        _ = generator.generate(
            template_name="router.py.j2",
            destination=destination,
            context={
                "name": "User",
                "snake_name": "user",
            },
        )

    assert destination.read_text(encoding="utf-8") == "existing content"