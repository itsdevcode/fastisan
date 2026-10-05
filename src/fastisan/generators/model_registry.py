from pathlib import Path
from fastisan.utils.naming import to_pascal_case

def regenerate_model_registry() -> Path:
    app_dir = Path.cwd() / "app"
    models_dir = app_dir / "models"
    registry_file = models_dir / "registry.py"
    
    if not models_dir.exists():
        models_dir.mkdir(parents=True, exist_ok=True)
        
    models = []
    
    if models_dir.exists():
        for path in models_dir.iterdir():
            if path.is_file() and path.suffix == ".py":
                if path.name.startswith("_") or path.name == "registry.py":
                    continue
                module_name = path.stem
                class_name = to_pascal_case(module_name)
                models.append((module_name, class_name))
                
    models.sort(key=lambda x: x[0])
    
    lines = [
        "# This file is managed by Fastisan.",
        ""
    ]
    
    for module_name, class_name in models:
        lines.append(f"from app.models.{module_name} import {class_name}")
        
    lines.append("")
    lines.append("__all__ = [")
    for _, class_name in models:
        lines.append(f'    "{class_name}",')
    lines.append("]")
    lines.append("")
    
    _ = registry_file.write_text("\n".join(lines), encoding="utf-8")
    return registry_file
