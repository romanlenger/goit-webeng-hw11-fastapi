FROM python:3.12-slim
LABEL authors="author"


RUN pip install --upgrade pip && pip install poetry
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install 
RUN poetry add alembic

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]