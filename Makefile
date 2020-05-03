check:
	flake8 .
	mypy .
	python -m pytest --cov=flake8_class_attributes_order --cov-report=xml
	mdl README.md
	safety check -r requirements_dev.txt
