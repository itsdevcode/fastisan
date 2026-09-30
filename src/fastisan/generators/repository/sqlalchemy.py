from pathlib import Path

from fastisan.generators.base import BaseGenerator
from fastisan.utils.naming import to_pascal_case, to_snake_case


class SQLAlchemyRepositoryGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self, name: str) -> Path:
        class_name = to_pascal_case(name)
        snake_name = to_snake_case(class_name)

        destination = Path.cwd() / "app" / "repositories" / f"{snake_name}.py"
        model_path = Path.cwd() / "app" / "models" / f"{snake_name}.py"
        
        if not model_path.exists():
            message = (
                f"Model file not found: {model_path}. "
                f"Please run `fastisan make:model {class_name}` first."
            )
            raise FileNotFoundError(message)

        return self.generator.generate(
            template_name="repository.py.j2",
            destination=destination,
            context={
                "name": class_name,
                "snake_name": snake_name,
                "orm": "sqlalchemy",
                "model_exists": True,
            },
        )
