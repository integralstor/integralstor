# Don't try fancy stuff like debuginfo, which is useless on binary-only
# packages. Don't strip binary too
# Be sure buildpolicy set to do nothing

%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress

Summary:           Fractalio-Django package 
Name:              fractalio_django
Version:           0.1
Release:           1
License:           Proprietary
Group:             Development/Tools
SOURCE0:          %{name}-%{version}.tar.gz
URL:               http://www.fractalio.com/
BuildRoot:         %{_tmppath}/%{name}-%{version}-%{release}-root
#Requires(postun): sed
#Requires(pre):    python

%description
This package installs Django-1.6.8, a python web framework. 
And also it copies the extracted django directory into /opt/fractalio/etc/Django-1.6.8 
and runs the setup file. 
#%{summary}

%prep
%setup -q

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

# in builddir
cp -a * %{buildroot}

%post
/usr/bin/python /opt/Django-1.6.8/setup.py install

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/opt/Django-1.6.8/

%postun
rm -rf /opt/Django-1.6.8

%changelog
* Wed Nov 12 2014  Omkar Sharma MN omkar@fractalio.com> 0.1-1
- First Build
