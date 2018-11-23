# This file contains common administration commands. It is language-independent.

run:
	python3 manage.py runserver

run2:
	gunicorn -w 4 manage:manager.app

flake8:
	flake8
