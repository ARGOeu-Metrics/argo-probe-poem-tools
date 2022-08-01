%define underscore() %(echo %1 | sed 's/-/_/g')

Summary:       ARGO probe that inspects the execution of argo-poem-tools
Name:          argo-probe-poem-tools
Version:       0.1.0
Release:       1%{?dist}
Source0:       %{name}-%{version}.tar.gz
License:       ASL 2.0
Group:         Development/System
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Prefix:        %{_prefix}
BuildArch:     noarch

BuildRequires: python3-devel


%description
ARGO probe that inspects the execution of argo-poem-tools

%prep
%setup -q


%build
%{py3_build}


%install
%{py3_install "--record=INSTALLED_FILES" }


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
%dir %{python3_sitelib}/%{underscore %{name}}/
%{python3_sitelib}/%{underscore %{name}}/*.py


%changelog
* Mon Aug 1 2022 Katarina Zailac <katarina.zailac@gmail.com> - 0.1.0-1
- ARGO-3939 Probe for monitoring argo-poem-packages execution
