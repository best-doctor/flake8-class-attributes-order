test:
	python -m pytest

coverage:
	python -m pytest --cov=flake8_class_attributes_order --cov-report=xml

types:
	mypy .

style:
	flake8 .

readme:
	mdl README.md

requirements:
	safety check -r requirements_dev.txt

check:
	make style
	make types
	make test
	make requirements
