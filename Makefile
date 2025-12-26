.PHONY: install run test lint migrate

install:
	pip install -r requirements.txt

run:
	python manage.py runserver

test:
	pytest

lint:
	ruff check .

migrate:
	python manage.py migrate
