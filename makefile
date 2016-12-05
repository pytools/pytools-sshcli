init:
	make venv
	make install

test:
	venv/bin/python -m unittest discover

requirements:
	pip freeze > requirements.txt

release-major:
	bumpversion major

release-minor:
	bumpversion minor

release-patch:
	bumpversion patch

venv:
	-rm -rf venv
	virtualenv -p python3 venv

install:
	venv/bin/pip install -r requirements.txt

clean:
	-ln -sfn ~/vagrant/.pypirc ~/.pypirc
	-rm -rf build
	-rm -rf dist

register:
	make clean
	python setup.py sdist bdist_wheel
	twine register dist/*.whl

upload:
	make clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

.PHONY: init test venv install requirements clean register upload
