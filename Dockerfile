# Use official Python 3.13.5 image
FROM python:3.13.5-slim

WORKDIR /app

COPY requirements.txt ./
COPY modem_restart.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "modem_restart.py"]