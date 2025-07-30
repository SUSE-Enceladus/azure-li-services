version := $(shell python3 -c 'from azure_li_services.version import __VERSION__; print(__VERSION__)')

build: check test
	rm -f dist/*
	# create setup.py variant for rpm build.
	# delete module versions from setup.py for building an rpm
	# the dependencies to the python module rpm packages is
	# managed in the spec file
	sed -ie "s@>=[0-9.]*'@'@g" setup.py
	# build the sdist source tarball
	python3 setup.py sdist
	# restore original setup.py backed up from sed
	mv setup.pye setup.py
	# provide rpm source tarball
	mv dist/azure_li_services-${version}.tar.gz dist/azure-li-services.tar.gz
	# provide rpm changelog from git changelog
	git log | helper/changelog_generator |\
		helper/changelog_descending > dist/azure-li-services.changes
	# update package version in spec file
	cat package/azure-li-services-spec-template \
		| sed -e s'@%%VERSION@${version}@' \
		> dist/azure-li-services.spec
	# provide rpm rpmlintrc
	cp package/azure-li-services-rpmlintrc dist

.PHONY: test
test:
	tox -e unit_py3

check:
	tox -e check
