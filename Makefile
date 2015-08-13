all:
	python setup.py sdist
	python setup.py sdist bdist_wheel --universal

register:
	python setup.py register -r pypitest

upload:
	python setup.py sdist upload -r pypitest


register-real:
	python setup.py register -r pypi

upload-real:
	python setup.py register -r pypi
