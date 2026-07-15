.PHONY: install run test lint format docker

install:
	python -m pip install -r requirements-dev.txt

run:
	streamlit run app.py

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

docker:
	docker compose up --build
