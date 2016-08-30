clean:
	find . -type f -name "*~" -exec rm -f {} \;

install:
	pip install -e .
	rm -rf doksit.egg-info/
