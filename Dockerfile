# API

FROM python:3.12-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# python .\API\main.py

CMD ["python", "api/main.py"]