FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN python -m pip install poetry==1.8.3
RUN poetry install --all-extras
ENTRYPOINT ["poetry", "run", "app"]
