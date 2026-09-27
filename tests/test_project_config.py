from pathlib import Path

import pytest

from fastisan.config.project import (
    create_project_config,
    read_project_config,
)


def test_create_project_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    config_path = create_project_config("sqlalchemy")

    assert config_path == tmp_path / "fastisan.toml"
    assert config_path.exists()

    assert config_path.read_text(encoding="utf-8") == (
        '[project]\n'
        'orm = "sqlalchemy"\n'
    )


def test_project_config_does_not_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    _ = create_project_config("sqlalchemy")

    with pytest.raises(FileExistsError):
        _ = create_project_config("none")

    content = (tmp_path / "fastisan.toml").read_text(
        encoding="utf-8"
    )

    assert 'orm = "sqlalchemy"' in content


def test_read_project_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    _ = create_project_config("sqlalchemy")

    config = read_project_config()

    assert config["project"]["orm"] == "sqlalchemy"


def test_read_project_config_when_not_initialized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(
        FileNotFoundError,
        match="fastisan init",
    ):
        _ = read_project_config()


def test_read_project_config_rejects_unsupported_orm(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    _ = (tmp_path / "fastisan.toml").write_text(
        '[project]\norm = "sqlmodel"\n',
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported ORM",
    ):
        _ = read_project_config()


def test_create_project_config_rejects_unsupported_orm(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(
        ValueError,
        match="Unsupported ORM",
    ):
        _ = create_project_config("sqlmodel")

    assert not (tmp_path / "fastisan.toml").exists()