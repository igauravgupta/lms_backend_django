1. django-admin startproject config . (name the project config, not the app domain name — keeps it generic)

2. Split settings from day one:

	- `config/settings/base.py` contains shared Django settings.
	- `config/settings/dev.py` contains local development settings.
	- `config/settings/prod.py` contains production settings.
	- `config/settings/__init__.py` selects the settings file based on `DJANGO_SETTINGS_MODULE`.

3. Add environment variable support:

	```bash
	uv add python-decouple
	```

	Keep local values in `.env` and commit only `.env.example`:

	```env
	DJANGO_SETTINGS_MODULE=config.settings.dev
	DJANGO_SECRET_KEY=replace-this-with-a-long-random-secret
	DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
	```

	`python-decouple` reads these values from `.env`. The real `.env` file is ignored by git so secrets are not committed.

4. Use production settings explicitly when deploying:

	```powershell
	$env:DJANGO_SETTINGS_MODULE = "config.settings.prod"
	uv run python manage.py check
	```

	Production requires `DJANGO_SECRET_KEY` and can receive comma-separated hosts through `DJANGO_ALLOWED_HOSTS`.

5. Add consistent editor settings and Python quality checks:

	- `.editorconfig` keeps indentation, line endings, and final newlines consistent.
	- Ruff handles Python linting and formatting in one tool.

	Ruff is configured in `pyproject.toml`. Install the development tools and run them with:

	```powershell
	uv sync
	uv run ruff check .
	uv run ruff format .
	```

	To check formatting without changing files:

	```powershell
	uv run ruff format --check .
	```

	ESLint and Prettier are not needed for this Python-only backend. Add them later if the project includes JavaScript or TypeScript frontend code.