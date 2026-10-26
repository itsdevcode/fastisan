from pathlib import Path

import pytest

from fastisan.generators.registry import regenerate_router_registry


def test_registry_discovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    routers_dir = tmp_path / "app" / "routers"
    routers_dir.mkdir(parents=True, exist_ok=True)

    (routers_dir / "user.py").touch()
    (routers_dir / "blog_post.py").touch()
    (routers_dir / "order_item.py").touch()
    (routers_dir / "__init__.py").touch()
    (routers_dir / "registry.py").touch()
    (routers_dir / "_private.py").touch()
    (routers_dir / "README.txt").touch()

    registry_file = regenerate_router_registry()

    assert registry_file.exists()
    content = registry_file.read_text(encoding="utf-8")

    # Deterministic alphabetical ordering
    assert content.index("blog_post") < content.index("order_item")
    assert content.index("order_item") < content.index("user")

    # Correct imports and includes
    assert "from app.routers.user import router as user_router" in content
    assert "from app.routers.blog_post import router as blog_post_router" in content
    assert "from app.routers.order_item import router as order_item_router" in content

    assert "router.include_router(user_router)" in content
    assert "router.include_router(blog_post_router)" in content
    assert "router.include_router(order_item_router)" in content

    # Ignores invalid files
    assert "private" not in content
    assert "registry_router" not in content
    assert "init_router" not in content
    assert "README" not in content


def test_registry_regeneration_idempotency(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    routers_dir = tmp_path / "app" / "routers"
    routers_dir.mkdir(parents=True, exist_ok=True)

    (routers_dir / "user.py").touch()

    regenerate_router_registry()

    (routers_dir / "blog_post.py").touch()

    registry_file = regenerate_router_registry()
    content_first = registry_file.read_text(encoding="utf-8")

    # Regenerate again without changes
    registry_file = regenerate_router_registry()
    content_second = registry_file.read_text(encoding="utf-8")

    assert content_first == content_second
    assert content_first.count("router.include_router(user_router)") == 1
    assert content_first.count("router.include_router(blog_post_router)") == 1


def test_registry_formatting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    routers_dir = tmp_path / "app" / "routers"
    routers_dir.mkdir(parents=True, exist_ok=True)

    # 1. Empty registry
    reg_file = regenerate_router_registry()
    content = reg_file.read_text(encoding="utf-8")

    assert content.endswith("\n")
    assert not content.endswith("\n\n")
    assert "\n\n\n\n" not in content
    expected_empty = (
        "# This file is managed by Fastisan.\n\n"
        "from fastapi import APIRouter\n\n\n"
        "router = APIRouter()\n"
    )
    assert content == expected_empty

    # 2. Populated registry
    (routers_dir / "user.py").touch()
    (routers_dir / "item.py").touch()
    reg_file = regenerate_router_registry()
    pop_content = reg_file.read_text(encoding="utf-8")

    assert pop_content.endswith("\n")
    assert not pop_content.endswith("\n\n")
    assert "\n\n\n\n" not in pop_content
    expected_pop = (
        "# This file is managed by Fastisan.\n\n"
        "from fastapi import APIRouter\n\n"
        "from app.routers.item import router as item_router\n"
        "from app.routers.user import router as user_router\n\n\n"
        "router = APIRouter()\n\n"
        "router.include_router(item_router)\n"
        "router.include_router(user_router)\n"
    )
    assert pop_content == expected_pop
