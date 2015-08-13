all:
	python setup.py install

prepare:
	python setup.py sdist
	python setup.py sdist bdist_wheel --universal

register-test:
	python setup.py register -r pypitest

upload-test:
	python setup.py sdist upload -r pypitest


register:
	python setup.py register -r pypi

upload:
	python setup.py sdist upload -r pypi

pypi: prepare upload

