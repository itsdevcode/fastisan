import pytest
from pathlib import Path
from fastisan.generators.model_registry import regenerate_model_registry

def test_regenerate_model_registry_discovery(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)
    
    (models_dir / "user.py").touch()
    (models_dir / "blog_post.py").touch()
    (models_dir / "order_item.py").touch()
    (models_dir / "_private.py").touch()
    (models_dir / "__init__.py").touch()
    (models_dir / "registry.py").touch()
    (models_dir / "README.txt").touch()

    registry_path = regenerate_model_registry()
    
    assert registry_path.exists()
    content = registry_path.read_text(encoding="utf-8")
    
    assert "from app.models.blog_post import BlogPost" in content
    assert "from app.models.order_item import OrderItem" in content
    assert "from app.models.user import User" in content
    
    assert "from app.models._private" not in content
    assert "from app.models.registry" not in content
    assert "from app.models.__init__" not in content
    
    # Check deterministic order
    assert content.index("BlogPost") < content.index("OrderItem")
    assert content.index("OrderItem") < content.index("User")

def test_regenerate_model_registry_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    
    registry_path = regenerate_model_registry()
    
    assert registry_path.exists()
    content = registry_path.read_text(encoding="utf-8")
    
    assert "__all__ = [" in content
    assert "]" in content
    assert "from app.models" not in content

def test_regenerate_model_registry_idempotency(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)
    (models_dir / "user.py").touch()
    
    first_path = regenerate_model_registry()
    first_content = first_path.read_text(encoding="utf-8")
    
    second_path = regenerate_model_registry()
    second_content = second_path.read_text(encoding="utf-8")
    
    assert first_content == second_content
