FROM python:3.12.3

WORKDIR /app

COPY . .

COPY pyproject.toml /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install

CMD ["python", "main.py"]
