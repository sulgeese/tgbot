FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install poetry && \
    poetry config virtualenvs.create false

ADD poetry.lock pyproject.toml ./

RUN poetry install --no-interaction --no-root

COPY . .

ENTRYPOINT python tgbot/main.py
