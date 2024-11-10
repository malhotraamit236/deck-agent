FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt

FROM gcr.io/distroless/python3-debian12:debug

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY . .

ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

CMD ["main.py"]
