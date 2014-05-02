Name:		sdnslog
Version: 	0.1	
Release:	2%{?dist}
Summary: 	Log Suricata DNS logs to a MySQL database	

Group:		System Environment/Daemons
License:	GPLv2
Source0:	sdnslog
Source1:	sdnslog-init
Source2:	sdnslog-sysconfig
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Requires: python-argparse
Requires: python-daemon
Requires: MySQL-python
Requires: PyYAML


%description
%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig

install -m 755 %{SOURCE0} %{buildroot}%{_bindir}
install -m 755  %{SOURCE1} %{buildroot}%{_sysconfdir}/rc.d/init.d/sdnslog
install %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/sdnslog

#make install DESTDIR=%{buildroot}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{_bindir}
%{_sysconfdir}/rc.d/init.d
%{_sysconfdir}/sysconfig
%doc



%changelog

