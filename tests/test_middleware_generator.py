from pathlib import Path

import pytest

from fastisan.generators.middleware import generate_middleware


def test_middleware_generator_creates_middleware(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    file_path = generate_middleware("Auth")

    assert file_path == tmp_path / "app" / "middleware" / "auth.py"
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")

    assert "from starlette.types import ASGIApp, Receive, Scope, Send" in content
    assert "class AuthMiddleware:" in content
    assert "def __init__(self, app: ASGIApp) -> None:" in content
    assert "async def __call__(" in content
    assert "await self.app(scope, receive, send)" in content


def test_middleware_generator_normalizes_lowercase(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    file_path = generate_middleware("auth")

    assert file_path == tmp_path / "app" / "middleware" / "auth.py"
    content = file_path.read_text(encoding="utf-8")
    assert "class AuthMiddleware:" in content


def test_middleware_generator_normalizes_snake_case(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    file_path = generate_middleware("request_id")

    assert file_path == tmp_path / "app" / "middleware" / "request_id.py"
    content = file_path.read_text(encoding="utf-8")
    assert "class RequestIdMiddleware:" in content


def test_middleware_generator_strips_suffix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    file_path = generate_middleware("AuthMiddleware")

    assert file_path == tmp_path / "app" / "middleware" / "auth.py"
    content = file_path.read_text(encoding="utf-8")
    assert "class AuthMiddleware:" in content
    assert "class AuthMiddlewareMiddleware:" not in content
    assert not (tmp_path / "app" / "middleware" / "auth_middleware.py").exists()


def test_middleware_generator_does_not_overwrite_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    _ = generate_middleware("Auth")

    with pytest.raises(FileExistsError):
        _ = generate_middleware("Auth")
