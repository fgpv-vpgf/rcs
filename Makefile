check:
	flake8 && PYTHONPATH=/vagrant pytest

build:
	python3.6 setup.py sdist --formats=bztar,zip

serve:
	python3.6 run.py --listen-all
