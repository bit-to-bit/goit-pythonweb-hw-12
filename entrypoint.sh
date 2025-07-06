#!/bin/sh
alembic upgrade head
exec python main.py