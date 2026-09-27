from pathlib import Path

import pytest
from typer.testing import CliRunner

from fastisan.cli import app


runner = CliRunner()


def test_init_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["init"],
        input="1\n",
    )

    assert result.exit_code == 0
    assert "Fastisan initialized" in result.stdout

    config_path = tmp_path / "fastisan.toml"

    assert config_path.exists()
    assert 'orm = "sqlalchemy"' in config_path.read_text(
        encoding="utf-8"
    )


def test_init_command_does_not_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    first_result = runner.invoke(
        app,
        ["init"],
        input="1\n",
    )

    assert first_result.exit_code == 0

    second_result = runner.invoke(
        app,
        ["init"],
        input="1\n",
    )

    assert second_result.exit_code == 1
    assert "already initialized" in second_result.output