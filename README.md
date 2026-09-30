# Fastisan

Fastisan is a command-line tool for scaffolding FastAPI components and project boilerplate.

It aims to reduce repetitive setup work while keeping generated code simple, readable, and easy to customize.

> Fastisan is currently in pre-alpha development. APIs, commands, and generated output may change before the first stable release.

## Features

Fastisan currently supports:

- Project initialization with `fastisan init`
- ORM selection during project initialization
- SQLAlchemy project foundation generation
- FastAPI router generation
- ORM-aware model generation
- Pydantic schema generation
- Service generation
- ORM-aware repository generation
- Complete resource scaffolding
- ASGI middleware generation
- Automatic Python class-name normalization
- Automatic snake_case file naming
- Automatic pluralized SQLAlchemy table names
- Protection against accidentally overwriting generated files

More generators and project scaffolding features are planned.

## Requirements

- Python 3.10 or newer

## Installation

Fastisan is currently under active development and is not yet published as a stable PyPI release.

For local development, clone the repository and install it in editable mode:

```bash
git clone https://github.com/itsdevcode/fastisan.git
cd fastisan

python -m venv .venv
source .venv/bin/activate

python -m pip install -e .
```

Verify the installation:

```bash
fastisan --help
```

## Quick Start

### Initialize a project

From your FastAPI project directory, run:

```bash
fastisan init
```

Fastisan will ask which ORM the project should use:

```text
Select your ORM:
1. SQLAlchemy
2. None
```

The selected configuration is stored in:

```text
fastisan.toml
```

For example:

```toml
[project]
orm = "sqlalchemy"
```

When SQLAlchemy is selected, Fastisan also generates the database foundation:

```text
app/
└── db/
    └── base.py
```

### Generate a Router

```bash
fastisan make:router User
```

This generates:

```text
app/
└── routers/
    └── user.py
```

Example generated router:

```python
from fastapi import APIRouter


router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.get("/")
async def index():
    return {"message": "User router"}
```

### Generate a Model

Model generation uses the ORM configured by `fastisan init`.

```bash
fastisan make:model User
```

With SQLAlchemy configured, Fastisan generates:

```text
app/
└── models/
    └── user.py
```

The generated model includes a primary key and timestamp fields.

Fastisan also normalizes model names:

```bash
fastisan make:model user
```

generates a `User` class with the `users` table.

Similarly:

```bash
fastisan make:model blog_post
```

generates:

```python
class BlogPost(Base):
    __tablename__ = "blog_posts"
```

### Generate a Schema

```bash
fastisan make:schema User
```

Generates a Pydantic schema file for the model.

### Generate a Repository

```bash
fastisan make:repository User
```

Generates an ORM-aware repository for the model (requires an ORM to be configured and the model file to exist).

### Generate a Service

```bash
fastisan make:service User
```

Generates a service layer class for the model.

### Generate a Resource

```bash
fastisan make:resource User
```

Generates a complete resource scaffold safely:

```text
app/models/user.py
app/schemas/user.py
app/repositories/user.py
app/services/user.py
app/routers/user.py
```

### Generate a Middleware

```bash
fastisan make:middleware Auth
```

Generates a generic pass-through ASGI middleware:

```text
app/
└── middleware/
    └── auth.py
```

## ORM Support

Current ORM support:

| ORM | Status |
| --- | --- |
| SQLAlchemy | Supported |
| None | Supported |

Fastisan's core is designed to remain ORM-agnostic where practical so additional ORM integrations can be introduced independently.

## Project Status

Fastisan is currently **pre-alpha**.

The project is being developed incrementally with tests around generators, naming behavior, project configuration, and CLI behavior.

The current focus is establishing a reliable foundation before expanding the generator surface.

## Roadmap

Potential future capabilities include:

- Resource generation
- Complete FastAPI project scaffolding
- Additional ORM integrations
- Improved project configuration
- Release automation

The roadmap may evolve as the project develops.

## Development

Clone the repository:

```bash
git clone https://github.com/itsdevcode/fastisan.git
cd fastisan
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Fastisan with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest -v
```

Check for whitespace errors:

```bash
git diff --check
```

## Contributing

Contributions are welcome.

Before contributing, please read [CONTRIBUTING.md](CONTRIBUTING.md).

Bug reports and feature requests can be submitted through GitHub Issues.

## Security

Please do not report security vulnerabilities through public GitHub issues.

See [SECURITY.md](SECURITY.md) for reporting guidance.

## Code of Conduct

Participation in the Fastisan community is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

Fastisan is released under the [MIT License](LICENSE).