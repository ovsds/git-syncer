ARG BASE_BUILDER_IMAGE=python:3.15.0
ARG BASE_RUNTIME_IMAGE=python:3.15.0-slim

FROM ${BASE_BUILDER_IMAGE} AS builder

RUN python -m pip install 'poetry==2.5.1'

RUN mkdir --parents /opt/app
COPY pyproject.toml /opt/app/pyproject.toml
COPY poetry.lock /opt/app/poetry.lock
COPY poetry.toml /opt/app/poetry.toml

WORKDIR /opt/app
RUN poetry install

FROM ${BASE_RUNTIME_IMAGE} AS runtime

RUN apt-get update \
    && apt-get upgrade --yes \
    && apt-get install --yes \
    --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir --parents /opt/app
COPY --from=builder /opt/app/.venv /opt/app/.venv
COPY bin /opt/app/bin
COPY lib /opt/app/lib

WORKDIR /opt/app
CMD [".venv/bin/python", "-m", "bin.main"]

FROM builder AS builder_dev

RUN poetry install --with dev

FROM runtime AS runtime_dev

COPY --from=builder_dev /opt/app/.venv /opt/app/.venv
COPY pyproject.toml /opt/app/pyproject.toml

FROM runtime_dev AS tests

COPY tests /opt/app/tests

CMD [".venv/bin/python", "-m", "pytest", "tests"]
