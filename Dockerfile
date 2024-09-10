FROM python:3.9
LABEL authors="diogobaeder"

RUN pip install poetry

RUN mkdir -p /app/src
WORKDIR /app/
COPY pyproject.toml poetry.lock /app/
RUN poetry install

COPY . /app/
WORKDIR /app/src/

ENTRYPOINT ["python"]
