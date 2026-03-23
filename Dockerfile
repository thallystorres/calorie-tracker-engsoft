FROM python:3.13-slim-bookworm AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL maintainer="https://www.github.com/thallystorres"

# Não cria .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Logs sem buffer
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# --- stage de dependências ---
FROM base AS dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-workspace --no-group dev

# --- produção ---
FROM base AS prod
COPY --from=dependencies /app/.venv /app/.venv
COPY . /app
EXPOSE 8000
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]

# --- desenvolvimento ---
FROM base AS dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked
EXPOSE 8000
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
