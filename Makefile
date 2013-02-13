#!/usr/bin/make -f

# This command is used to setup the package directories.
INSTALL_DIR := install -d -m0755 -p
INSTALL_BIN := install -m0755 -p 
INSTALL_DATA := install -m0644 -p 

# The version of the extensions.
VERSION ?= 0.0
RELEASE ?= 1

# The python version.
PYTHON_PATH := $(shell which python)
PYTHON ?= $(shell readlink $(PYTHON_PATH))

# This matches the OpenStack release version.
OPENSTACK_RELEASE ?= folsom

# The timestamp release for the extensions.
TIMESTAMP := $(shell date "+%Y-%m-%dT%H:%M:%S%:z")

# **** TARGETS ****

all : package
.PHONY : all

# Package the extensions.
package : deb tgz pip rpm
.PHONY : package

# Build the python egg files.
build-nova : build-python-canary
build-nova : build-canary-api
build-nova : build-canary-host
.PHONY : build-nova
build-novaclient : build-canary-novaclient
.PHONY: build-novaclient
build-horizon : build-canary-horizon
.PHONY : build-horizon
build : build-nova build-novaclient build-horizon
.PHONY : build

build-python-canary :
	@rm -rf build/ dist/python-canary
	@PACKAGE=canary VERSION=$(VERSION).$(RELEASE) \
	    $(PYTHON) setup.py install --prefix=$(CURDIR)/dist/python-canary/usr
	@sed -i -e "s/'.*' ##TIMESTAMP##/'$(TIMESTAMP)' ##TIMESTAMP##/" \
	    `find dist/python-canary/ -name extension.py`
PHONY: build-python-canary

build-canary-api : build-python-canary
	@rm -rf build/ dist/canary-api
	@mkdir -p dist/canary-api
	@PACKAGE=api VERSION=$(VERSION).$(RELEASE) \
	    $(PYTHON) setup.py install --prefix=$(CURDIR)/dist/canary-api/usr
.PHONY: build-canary-api

build-canary-novaclient :
	@rm -rf build/ dist/canary-novaclient
	@mkdir -p $(CURDIR)/dist/canary-novaclient/usr/lib/python/site-packages
	@PACKAGE=novaclient VERSION=$(VERSION).$(RELEASE) \
	    PYTHONPATH=$(CURDIR)/dist/canary-novaclient/usr/lib/$(PYTHON)/site-packages \
	    $(PYTHON) setup.py install --prefix=$(CURDIR)/dist/canary-novaclient/usr
.PHONY: build-canary-novaclient

build-canary-host : build-python-canary
	@rm -rf build/ dist/canary-host
	@PACKAGE=host VERSION=$(VERSION).$(RELEASE) \
	    $(PYTHON) setup.py install --prefix=$(CURDIR)/dist/canary-host/usr
	@$(INSTALL_DIR) dist/canary-host/etc/init
	@$(INSTALL_DATA) etc/init/canary.conf dist/canary-host/etc/init
	@$(INSTALL_DIR) dist/canary-host/etc/init.d
	@$(INSTALL_BIN) etc/init.d/canary dist/canary-host/etc/init.d
.PHONY: build-canary-host

build-canary-horizon : build-python-canary
	@rm -rf build/ dist/canary-horizon
	@mkdir -p dist/canary-horizon
	@PACKAGE=horizon VERSION=$(VERSION).$(RELEASE) \
	    $(PYTHON) setup.py install --prefix=$(CURDIR)/dist/canary-horizon/usr
.PHONY: build-canary-horizon

deb-nova : deb-python-canary
deb-nova : deb-canary-api
deb-nova : deb-canary-host
.PHONY : deb-nova
deb-novaclient : deb-canary-novaclient
.PHONY : deb-novaclient
deb-horizon : deb-canary-horizon
.PHONY : deb-horizon
deb : deb-nova deb-novaclient deb-horizon 
.PHONY : deb

deb-% : build-%
	@rm -rf debbuild && $(INSTALL_DIR) debbuild
	@rsync -ruav packagers/deb/$*/ debbuild
	@rsync -ruav dist/$*/ debbuild
	@rm -rf debbuild/etc/init.d
	@sed -i "s/VERSION/$(VERSION).$(RELEASE)-$(OPENSTACK_RELEASE)/" debbuild/DEBIAN/control
	@dpkg -b debbuild/ .
	@rm -rf debbuild && $(INSTALL_DIR) debbuild
	@rsync -ruav packagers/deb/$*/ debbuild
	@rsync -ruav dist/$*/ debbuild
	@rm -rf debbuild/etc/init.d
	@LIBDIR=`ls -1d debbuild/usr/lib*/$(PYTHON)`; \
	 if [ -d $$LIBDIR/site-packages ]; then \
	    mv $$LIBDIR/site-packages $$LIBDIR/dist-packages; \
	 fi
	@sed -i "s/VERSION/$(VERSION).$(RELEASE)-ubuntu+$(OPENSTACK_RELEASE)/" debbuild/DEBIAN/control
	@dpkg -b debbuild/ .

tgz-nova : tgz-python-canary
tgz-nova : tgz-canary-api
tgz-nova : tgz-canary-host
.PHONY : tgz-nova
tgz-novaclient : tgz-canary-novaclient
.PHONY : tgz-novaclient
tgz-horizon : tgz-canary-horizon
.PHONY : tgz-horizon
tgz : tgz-nova tgz-novaclient tgz-horizon
.PHONY : tgz

tgz-% : build-%
	tar -cvzf $*_$(VERSION).$(RELEASE)-$(OPENSTACK_RELEASE).tgz -C dist/$* .

pip : pip-canary-novaclient
.PHONY: pip

pip-canary-novaclient :
	@rm -rf build/
	@PACKAGE=novaclient VERSION=$(VERSION).$(RELEASE) \
	    $(PYTHON) setup.py sdist
	@cp dist/canary_python_novaclient_ext*.tar.gz .
.PHONY: pip-canary-novaclient

rpm-nova : rpm-python-canary
rpm-nova : rpm-canary-api
rpm-nova : rpm-canary-host
.PHONY : rpm-nova

rpm-novaclient : rpm-canary-novaclient
.PHONY : rpm-novaclient

rpm-horizon : rpm-canary-horizon
.PHONY : rpm-horizon

rpm : rpm-nova rpm-novaclient
.PHONY : rpm

rpm-%: build-%
	@rm -rf dist/$*/etc/init
	@rpmbuild -bb --buildroot $(PWD)/rpmbuild/BUILDROOT \
	  --define="%_topdir $(PWD)/rpmbuild" --define="%version $(VERSION).$(RELEASE)" \
	  --define="%release $(OPENSTACK_RELEASE)" packagers/rpm/$*.spec
	@cp rpmbuild/RPMS/noarch/*.rpm .
.PHONY : rpm

clean : 
	rm -rf MANIFEST build dist
	rm -rf *.deb debbuild
	rm -rf *.tgz *.tar.gz
	rm -rf *.rpm rpmbuild
.PHONY : clean
