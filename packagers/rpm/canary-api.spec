Name: canary-api
Summary: Canary OpenStack monitoring service.
Version: %{version}
Release: %{release}
Group: System
License: Copyright 2012 Gridcentric Inc.
URL: http://www.gridcentric.com
Packager: Gridcentric Inc. <support@gridcentric.com>
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}.%{version}-buildroot
AutoReq: no
AutoProv: no
Requires: python-canary = %{version}

# To prevent ypm/rpm/zypper/etc from complaining about FileDigests when installing we set the
# algorithm explicitly to MD5SUM. This should be compatible across systems (e.g. RedHat or openSUSE)
# and is backwards compatible.
%global _binary_filedigest_algorithm 1
# Don't strip the binaries.
%define __os_install_post %{nil}

%description
Canary OpenStack monitoring service.

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT
rsync -rav --delete ../../dist/canary-api/* $RPM_BUILD_ROOT
mv $RPM_BUILD_ROOT/usr/lib $RPM_BUILD_ROOT/usr/lib64

%files
/usr/

%post
function add_extension {
    NOVA_CONF=$1
    EXTENSION=$2
    if [ -f $NOVA_CONF ]; then
        # Add the extension.
        if ! cat $NOVA_CONF | grep $EXTENSION >/dev/null 2>&1; then
            grep "\[DEFAULT\]" $NOVA_CONF >/dev/null 2>&1 && \
                echo "osapi_compute_extension=$EXTENSION" >> $NOVA_CONF || \
                echo "--osapi_compute_extension=$EXTENSION" >> $NOVA_CONF
        fi
    fi
}

if [ "$1" == "1" ]; then
    add_extension \
        /etc/nova/nova.conf \
        nova.api.openstack.compute.contrib.standard_extensions
    add_extension \
        /etc/nova/nova.conf \
        canary.extension.Canary_extension
    /etc/init.d/nova-api restart 2>/dev/null || true
    /etc/init.d/nova-api-os-compute restart 2>/dev/null || true
fi

%preun
function remove_extension {
    NOVA_CONF=$1
    EXTENSION=$2

    if [ -f $NOVA_CONF ]; then

        # Automatically remove the extension from nova.conf if it was added.
        cat $NOVA_CONF | \
            grep -v $EXTENSION > $NOVA_CONF.new && \
            mv $NOVA_CONF.new $NOVA_CONF || \
            rm -f $NOVA_CONF.new
    fi
}

if [ "$1" == "1" ]; then
    remove_extension \
        /etc/nova/nova.conf \
        canary.extension.Canary_extension
    /etc/init.d/nova-api restart 2>/dev/null || true
    /etc/init.d/nova-api-os-compute restart 2>/dev/null || true
fi

%changelog
* Tue Feb 12 2013 Adin Scannell <adin@scannell.ca>
- Initial package creation
