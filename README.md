# bit-to-bit-goit-pythonweb-hw-08
Python FastAPI

# Run App with:
docker-compose up -d

alembic revision --autogenerate -m "Add description to notes"

PYTHONPATH=. pytest -v tests/test_contacts_repository_unit.py

$ PYTHONPATH=. pytest --cov=src tests/

pytest --cov=src tests/ --cov-report=html

PYTHONPATH=. pytest -s --cov=src tests/
