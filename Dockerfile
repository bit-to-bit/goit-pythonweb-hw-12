FROM python:3.12-slim

ENV PORT 8000

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

COPY . .
	
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
