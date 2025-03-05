# Crypto dashboard

Simple python application for quering coingecko api and (live) show some information about coins.

## Usage

First, you must set the following environment variables in a `.env` file:

```bash
# Required:
export COIN_GECKO_API_KEY=""

# Only for local development:
export DB_USER=""
export DB_PASSWORD=""
export DB_HOST=""
export DB_NAME=""
```

After setting the environment variables, you can simply run the application using:

```bash
docker-compose up
```

Or for local development:

```bash
poetry run app
```

You can access these endpoints:

- Api documentation on `http://127.0.0.1:8000/api/v1/docs`
- Dashboard on `http://127.0.0.1:8000/dashboard`

## Development

<details>

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run app
```

## Testing

```bash
pytest -c pyproject.toml
```

## Formatting

```bash
poetry run poe format-code
```

## Pre-commit

```bash
poetry shell
pre-commit install
```

</details>
