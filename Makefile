clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +;
	find . -type f -name "*~" -delete
	rm -rf .cache/

install:
	pip install -e .
	pip install -r requirements-dev.txt

release:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_wheel upload
	rm -rf build/ dist/
