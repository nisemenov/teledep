FROM python:3.12.3

WORKDIR /app

COPY . .

RUN pip install poetry && poetry config virtualenvs.create false && poetry install

CMD ["tail", "-f", "/dev/null"]
