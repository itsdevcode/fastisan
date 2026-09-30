from pathlib import Path

import pytest

from fastisan.generators.service import ServiceGenerator


def test_service_generator_creates_service_without_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = ServiceGenerator()
    file_path = generator.generate("User")

    assert file_path == tmp_path / "app" / "services" / "user.py"
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")

    assert "class UserService:" in content
    assert "async def list(self)" not in content
    assert "pass" in content


def test_service_generator_creates_service_with_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    # Create a mock schema file so the generator detects it
    schema_dir = tmp_path / "app" / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "user.py").touch()

    generator = ServiceGenerator()
    file_path = generator.generate("User")

    content = file_path.read_text(encoding="utf-8")

    assert "class UserService:" in content
    assert "async def list(self) -> list[UserResponse]:" in content
    assert "async def detail(self, id: int) -> UserResponse | None:" in content
    assert "async def create(self, data: UserCreate) -> UserResponse:" in content
    assert "raise NotImplementedError" in content
    assert "from app.schemas.user import UserCreate, UserResponse, UserUpdate" in content


def test_service_generator_creates_service_with_schema_and_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    schema_dir = tmp_path / "app" / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "user.py").touch()

    repository_dir = tmp_path / "app" / "repositories"
    repository_dir.mkdir(parents=True, exist_ok=True)
    (repository_dir / "user.py").touch()

    generator = ServiceGenerator()
    file_path = generator.generate("User")

    content = file_path.read_text(encoding="utf-8")

    assert "class UserService:" in content
    assert "from app.repositories.user import UserRepository" in content
    assert "def __init__(self, repository: UserRepository) -> None:" in content
    assert "db_objects = await self.repository.list()" in content
    assert "UserResponse.model_validate(db_obj)" in content
    assert "**data.model_dump()" in content
    assert "**data.model_dump(exclude_unset=True)," in content
    assert "raise NotImplementedError" not in content

def test_service_generator_normalizes_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = ServiceGenerator()
    file_path = generator.generate("blog_post")

    assert file_path == tmp_path / "app" / "services" / "blog_post.py"

    content = file_path.read_text(encoding="utf-8")

    assert "class BlogPostService:" in content
    assert "pass" in content


def test_service_generator_does_not_overwrite_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = ServiceGenerator()
    _ = generator.generate("User")

    with pytest.raises(FileExistsError):
        _ = generator.generate("User")

import sys
import importlib.util

import asyncio

def test_generated_service_behavior(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    asyncio.run(_test_generated_service_behavior(tmp_path, monkeypatch))

async def _test_generated_service_behavior(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(tmp_path)

    app_dir = tmp_path / "app"
    app_dir.mkdir(parents=True, exist_ok=True)

    schemas_dir = app_dir / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)

    schemas_dir.joinpath("__init__.py").touch()

    # We need to mock Pydantic schemas so the service module can load
    schema_code = """
class UserCreate:
    def __init__(self, name):
        self.name = name
    def model_dump(self):
        return {"name": self.name}

class UserUpdate:
    def __init__(self, name):
        self.name = name
    def model_dump(self, exclude_unset=False):
        return {"name": self.name}

class UserResponse:
    @classmethod
    def model_validate(cls, obj):
        res = cls()
        res.id = obj.id
        res.name = getattr(obj, "name", "test")
        return res
"""
    (schemas_dir / "user.py").write_text(schema_code)

    repositories_dir = app_dir / "repositories"
    repositories_dir.mkdir(parents=True, exist_ok=True)
    repositories_dir.joinpath("__init__.py").touch()

    # We need a mock repository type for import
    repo_code = """
class UserRepository:
    pass
"""
    (repositories_dir / "user.py").write_text(repo_code)

    generator = ServiceGenerator()
    file_path = generator.generate("User")

    # Import the generated service
    spec = importlib.util.spec_from_file_location("app.services.user", file_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["app.services.user"] = module
    spec.loader.exec_module(module)

    UserService = module.UserService

    # Mock the actual repository instance
    class MockRepo:
        async def list(self):
            class DBUser:
                id = 1
                name = "test"
            return [DBUser()]

        async def detail(self, id: int):
            if id == 1:
                class DBUser:
                    id = 1
                    name = "test"
                return DBUser()
            return None

        async def create(self, **kwargs):
            class DBUser:
                id = 1
                name = kwargs.get("name")
            return DBUser()

        async def update(self, obj, **kwargs):
            obj.name = kwargs.get("name", obj.name)
            return obj

        async def delete(self, obj):
            pass

    repo = MockRepo()
    service = UserService(repository=repo)

    # Test list
    results = await service.list()
    assert len(results) == 1
    assert results[0].id == 1
    assert results[0].name == "test"

    # Test detail
    detail_res = await service.detail(1)
    assert detail_res is not None
    assert detail_res.id == 1

    missing_detail = await service.detail(99)
    assert missing_detail is None

    # Test create
    from app.schemas.user import UserCreate, UserUpdate
    create_data = UserCreate(name="new")
    create_res = await service.create(create_data)
    assert create_res.id == 1
    assert create_res.name == "new"

    # Test update
    update_data = UserUpdate(name="updated")
    update_res = await service.update(1, update_data)
    assert update_res is not None
    assert update_res.name == "updated"

    missing_update = await service.update(99, update_data)
    assert missing_update is None

    # Test delete
    delete_res = await service.delete(1)
    assert delete_res is True

    missing_delete = await service.delete(99)
    assert missing_delete is False
