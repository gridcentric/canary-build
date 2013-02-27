Name: canary-horizon
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
Requires: python-canary >= %{version}, canary-novaclient >= %{version}

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
rsync -rav --delete ../../dist/canary-horizon/* $RPM_BUILD_ROOT
mv $RPM_BUILD_ROOT/usr/lib $RPM_BUILD_ROOT/usr/lib64

%files
/usr/

%post
function add_extension {
    DJANGO_SETTINGS=$1
    EXTENSION=$2

    if [ -f $DJANGO_SETTINGS ]; then
        # Add the extension.
        if ! cat $DJANGO_SETTINGS | grep $EXTENSION >/dev/null 2>&1; then
            echo "import settings; settings.INSTALLED_APPS += ('$2',)" >> $DJANGO_SETTINGS
        fi

        # Restart apache (if that's the server engine).
        /etc/init.d/apache2 restart 2>/dev/null || true
        /etc/init.d/httpd restart 2>/dev/null || true
    fi
}

if [ "$1" == "1" ]; then
    add_extension \
        /etc/openstack-dashboard/local_settings.py \
        canary.horizon
fi

%preun
function remove_extension {
    DJANGO_SETTINGS=$1
    EXTENSION=$2

    if [ -f $DJANGO_SETTINGS ]; then

        # Automatically remove the extension.
        cat $DJANGO_SETTINGS | \
            grep -v $EXTENSION > $DJANGO_SETTINGS.new && \
            mv $DJANGO_SETTINGS.new $DJANGO_SETTINGS || \
            rm -f $DJANGO_SETTINGS.new

        # Restart apache (if that's the server engine).
        service apache2 restart 2>/dev/null || true
    fi
}

if [ "$1" = "1" ]; then
    remove_extension \
        /etc/openstack-dashboard/local_settings.py \
        canary.horizon
fi

%changelog
* Tue Feb 12 2013 Adin Scannell <adin@scannell.ca>
- Initial package creation
