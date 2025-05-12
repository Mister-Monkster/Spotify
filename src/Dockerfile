FROM python:3.12-slim
LABEL authors="mikir"

WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

COPY src .

WORKDIR /app/src

COPY ../.env .

EXPOSE 8000

CMD ["python", "main.py"]
