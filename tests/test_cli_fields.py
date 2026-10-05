import pytest
from pathlib import Path
from typer.testing import CliRunner
from fastisan.cli import app

runner = CliRunner()

def test_make_resource_with_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    init_result = runner.invoke(app, ["init"], input="1\n")
    assert init_result.exit_code == 0

    result = runner.invoke(
        app,
        ["make:resource", "User", "--fields", "name:str,email:str,age:int?,is_active:bool"]
    )
    
    assert result.exit_code == 0
    assert "Resource created: User" in result.stdout

    model_path = tmp_path / "app" / "models" / "user.py"
    schema_path = tmp_path / "app" / "schemas" / "user.py"

    assert model_path.exists()
    assert schema_path.exists()

    model_content = model_path.read_text(encoding="utf-8")
    assert "name: Mapped[str] = mapped_column(String, nullable=False)" in model_content
    assert "email: Mapped[str] = mapped_column(String, nullable=False)" in model_content
    assert "age: Mapped[int | None] = mapped_column(Integer, nullable=True)" in model_content
    assert "is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)" in model_content
    assert "from sqlalchemy import Boolean, DateTime, Integer, String, func" in model_content

    schema_content = schema_path.read_text(encoding="utf-8")
    assert "name: str" in schema_content
    assert "email: str" in schema_content
    assert "age: int | None = None" in schema_content
    assert "is_active: bool" in schema_content
    assert "is_active: bool | None = None" in schema_content

def test_make_resource_with_invalid_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    _ = runner.invoke(app, ["init"], input="1\n")

    result = runner.invoke(
        app,
        ["make:resource", "User", "--fields", "price:decimal"]
    )
    
    assert result.exit_code == 1
    assert "Unsupported field type: decimal" in result.output
    assert not (tmp_path / "app" / "models" / "user.py").exists()
