FROM python:3.10-alpine

ENV PIP_NO_CACHE_DIR=false
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install -U poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY . .

ENTRYPOINT ["python3"]
CMD ["app.py"]