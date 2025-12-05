# syntax=docker/dockerfile:1
FROM python:3.13-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml ./

RUN uv sync --no-editable --no-cache

COPY . .

EXPOSE 8000
CMD ["uv", "run", "python", "-m", "app"]