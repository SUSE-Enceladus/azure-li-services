version := $(shell python -c 'from azure_li_services.version import __VERSION__; print(__VERSION__)')

build: check test
	rm -f dist/*
	# delete version information from setup.py for rpm package
	# we don't want to have this in the egg info because the rpm
	# package should handle package/version requirements
	cat setup.py | sed -e 's@>=[0-9.]*@@g' > setup.build.py
	python setup.build.py sdist
	rm setup.build.py
	cat package/azure-li-services-spec-template \
		| sed -e s'@%%VERSION@${version}@' \
		> dist/azure-li-services.spec

.PHONY: test
test:
	tox -e unit_py3

check:
	tox -e check
