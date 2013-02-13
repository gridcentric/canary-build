Name: canary-host
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
rsync -rav --delete ../../dist/canary-host/* $RPM_BUILD_ROOT
mv $RPM_BUILD_ROOT/usr/lib $RPM_BUILD_ROOT/usr/lib64


%files
/usr/
/etc/init.d/canary

%post
if [ "$1" = "1" ]; then
    # Start the service.
    /etc/init.d/canary start 2>/dev/null || true
else
    # Restart the service.
    /etc/init.d/canary restart 2>/dev/null || true
fi

%preun
if [ "$1" = "1" ]; then
    # Stop the service before removing completely.
    /etc/init.d/canary stop 2>/dev/null || true
fi

%changelog
* Tue Feb 12 2013 Adin Scannell <adin@scannell.ca>
- Initial package creation
