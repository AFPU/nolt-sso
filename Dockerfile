FROM python:3.10

ENV PIP_NO_CACHE_DIR=false
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install -U poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY . .

ENTRYPOINT ["uvicorn"]
CMD ["app:app", "--host", "0.0.0.0", "--port", "8000"]