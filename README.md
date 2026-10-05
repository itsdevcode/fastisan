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

When SQLAlchemy is selected, Fastisan generates the application foundation, including database components:

```text
app/
├── __init__.py
├── main.py
├── db/
│   ├── __init__.py
│   ├── base.py
│   └── session.py
├── models/
│   └── __init__.py
├── schemas/
│   └── __init__.py
├── repositories/
│   └── __init__.py
├── services/
│   └── __init__.py
└── routers/
    ├── __init__.py
    └── registry.py
```

`app/main.py` is a minimal, runnable FastAPI application (once application dependencies like FastAPI itself are installed) with a `/health` endpoint.
The `registry.py` file is deterministically managed by Fastisan and automatically aggregates all your generated routers.
Fastisan generates a reusable async SQLAlchemy session dependency inside `session.py`. It expects a database connection string via the `DATABASE_URL` environment variable (e.g., `postgresql+asyncpg://...`).

### Generate a Router

```bash
fastisan make:router User
```

Generates a FastAPI router for the resource. 

When the corresponding schema and service files exist, Fastisan automatically generates a service-aware CRUD router that:
- Delegates application logic to the service layer
- Handles HTTP 404 responses when resources are not found
- Defines an explicit composition boundary via a `get_user_service` dependency function

If all composition prerequisites exist (schema, repository, service, and database session), the router automatically generates fully wired dependency injection:

```python
def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    repository = UserRepository(session)
    return UserService(repository)
```

If some prerequisites are missing, a `raise NotImplementedError` placeholder is generated instead for you to implement manually.

If the required components do not exist, a lightweight fallback router is generated instead.

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

Generates a service layer class for the model. When generated as part of a complete resource (or when the corresponding repository exists), the service will automatically integrate with and delegate to the repository.

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

After generating the resource, Fastisan automatically registers `user.py` into `app/routers/registry.py` so your main application immediately serves the new endpoints.

The generated router is fully integrated with the service and repository layers, providing complete CRUD functionality out of the box. Because `init` generates the SQLAlchemy session foundation, `make:resource` automatically wires `AsyncSession`, the repository, and the service together in the router's dependency function.

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