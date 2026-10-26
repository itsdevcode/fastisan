from pathlib import Path

import pytest
from packaging.requirements import Requirement
from typer.testing import CliRunner

from fastisan.cli import app
from fastisan.generators.application import ApplicationGenerator

runner = CliRunner()


def test_init_sqlalchemy_generates_expected_dependencies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"], input="1\n")

    assert result.exit_code == 0
    assert "Fastisan initialized" in result.stdout
    assert "pip install -r requirements.txt" in result.stdout
    assert "cp .env.example .env" in result.stdout

    requirements_path = tmp_path / "requirements.txt"
    assert requirements_path.exists()

    content = requirements_path.read_text(encoding="utf-8")
    expected_deps = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic-settings",
        "sqlalchemy[asyncio]",
        "alembic",
        "asyncpg",
    ]

    for dep in expected_deps:
        assert dep in content, f"Expected {dep} to be present in requirements.txt"


def test_init_none_excludes_orm_dependencies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"], input="2\n")

    assert result.exit_code == 0
    assert "Fastisan initialized" in result.stdout
    assert "pip install -r requirements.txt" in result.stdout

    requirements_path = tmp_path / "requirements.txt"
    assert requirements_path.exists()

    content = requirements_path.read_text(encoding="utf-8")

    # Should contain core application dependencies
    assert "fastapi" in content
    assert "uvicorn" in content
    assert "pydantic" in content

    # Should NOT contain ORM/migration dependencies
    excluded_deps = [
        "sqlalchemy",
        "alembic",
        "asyncpg",
        "pydantic-settings",
    ]
    for dep in excluded_deps:
        assert dep not in content, f"Expected {dep} to be excluded from requirements.txt"


def test_init_preflight_protects_existing_requirements_txt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    custom_content = "custom-dependency==1.0.0\n"
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text(custom_content, encoding="utf-8")

    result = runner.invoke(app, ["init"], input="1\n")

    assert result.exit_code == 1
    assert "Application foundation components already exist:" in result.output
    assert "requirements.txt" in result.output

    # Verify existing file content was untouched
    assert requirements_path.read_text(encoding="utf-8") == custom_content
    # Verify project initialization did not proceed
    assert not (tmp_path / "fastisan.toml").exists()
    assert not (tmp_path / "app" / "main.py").exists()


def test_init_none_preflight_protects_existing_requirements_txt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    custom_content = "custom-dependency==1.0.0\n"
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text(custom_content, encoding="utf-8")

    result = runner.invoke(app, ["init"], input="2\n")

    assert result.exit_code == 1
    assert "Application foundation components already exist:" in result.output
    assert "requirements.txt" in result.output

    assert requirements_path.read_text(encoding="utf-8") == custom_content
    assert not (tmp_path / "fastisan.toml").exists()


def test_application_generator_preflight_conflict_raised(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").touch()

    generator = ApplicationGenerator()
    with pytest.raises(FileExistsError, match="requirements.txt"):
        generator.preflight("sqlalchemy")

    with pytest.raises(FileExistsError, match="requirements.txt"):
        generator.preflight("none")


def test_generated_requirements_valid_pep508_syntax(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    for orm_choice in ["1", "2"]:
        # Clean tmp directory
        for p in tmp_path.iterdir():
            if p.is_dir():
                import shutil
                shutil.rmtree(p)
            else:
                p.unlink()

        result = runner.invoke(app, ["init"], input=f"{orm_choice}\n")
        assert result.exit_code == 0

        req_file = tmp_path / "requirements.txt"
        assert req_file.exists()

        lines = [line.strip() for line in req_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(lines) >= 3

        for line in lines:
            req = Requirement(line)
            assert req.name
            assert req.specifier is not None
