FROM python:3.11-slim

WORKDIR /app

COPY app/watchertoucher.py /app/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "watchertoucher.py"]
