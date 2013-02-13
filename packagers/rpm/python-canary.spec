Name: python-canary
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
rsync -rav --delete ../../dist/python-canary/* $RPM_BUILD_ROOT
mv $RPM_BUILD_ROOT/usr/lib $RPM_BUILD_ROOT/usr/lib64

%files
/usr/

%post
exit 0

%changelog
* Tue Feb 12 2013 Adin Scannell <adin@scannell.ca>
- Initial package creation
