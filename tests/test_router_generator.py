from pathlib import Path

import pytest

from fastisan.generators.router import generate_router


def test_generate_router(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test router generation.

    Args:
        tmp_path: Temporary path.
        monkeypatch: Monkeypatch instance.
    """
    monkeypatch.chdir(tmp_path)

    file_path = generate_router("BlogPost")

    assert file_path == tmp_path / "app" / "routers" / "blog_post.py"
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")

    assert 'prefix="/blog_post"' in content
    assert 'tags=["BlogPost"]' in content


def test_generate_router_does_not_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    _ = generate_router("User")

    with pytest.raises(FileExistsError):
        _ = generate_router("User")