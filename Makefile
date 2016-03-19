check:
	flake8 && py.test

build:
	python setup.py sdist --formats=bztar,zip

serve:
	python run.py --listen-all
