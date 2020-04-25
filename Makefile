start:
	@python main.py

test:
	@python -m unittest discover tests -v

freeze:
	@pip freeze > requirements.txt

.PHONY: start test freeze
