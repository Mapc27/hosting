FROM python:3.8 AS app

ENV PYTHONUNBUFFERED 1

RUN pip install poetry==1.1.12 && poetry config virtualenvs.create false

WORKDIR /app/

COPY pyproject.toml .
RUN poetry install --no-dev

COPY . .

EXPOSE 8000

CMD alembic upgrade head && uvicorn --reload --host 0.0.0.0 --port 8000 main:app
