from pathlib import Path
from fastisan.generators.base import BaseGenerator


def regenerate_router_registry() -> Path:
    routers_dir = Path.cwd() / "app" / "routers"
    routers_dir.mkdir(parents=True, exist_ok=True)
    
    registry_file = routers_dir / "registry.py"
    
    routers: list[tuple[str, str]] = []
    
    if routers_dir.exists():
        for item in routers_dir.iterdir():
            if item.is_file() and item.name.endswith(".py"):
                if item.name in ("__init__.py", "registry.py") or item.name.startswith("_"):
                    continue
                
                module_name = item.stem
                router_alias = f"{module_name}_router"
                routers.append((module_name, router_alias))
            
    routers.sort(key=lambda x: x[0])
    
    generator = BaseGenerator()
    template = generator.environment.get_template("registry.py.j2")
    content = template.render(routers=routers)
    
    _ = registry_file.write_text(content, encoding="utf-8")
    
    return registry_file
