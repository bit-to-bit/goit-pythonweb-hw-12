#!/bin/sh

echo "🟡 Wating PostgreSQL..."

while ! nc -z postgres 5432; do
  sleep 0.5
done

echo "🟢 PostgreSQL available. Applying migrations..."
alembic upgrade head

echo "🚀 Run main App"
exec python main.py