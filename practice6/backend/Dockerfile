FROM python:3.11-slim
WORKDIR /app
COPY reqiurements.txt .
RUN pip install --no-cache-dir -r reqiurements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]