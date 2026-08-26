FROM python:3.12-slim

# Virtualenv lives OUTSIDE /code because dev bind-mounts replace /code contents.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /code

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN (uv sync --frozen --no-install-project 2>/dev/null || uv sync --no-install-project)

COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic
COPY tests ./tests

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
