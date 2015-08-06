#!/bin/sh

#######################################################################
#The exit status codes used: 

    # -1: Need to be a super user i.e root.
    # -2: Operation, git clone from www.github.com failed.
    # -3: Failed to create "/opt/fractalio/integral_view/integral_view"
    # -4: Failed to do a git branch

#######################################################################

echo
echo "Your Machine must be configured with git basic settings with https or ssh in order to do a clone of integral view. "
echo "The clone will be taken from https://$github_username@github.com/fractalio/integral-view.git "
echo "This script will automatically create /root/rpmbuild directory."
echo 

# To force the user to be a super-user: root
if [[ $EUID != 0 ]]; then
  echo "You must be root to run this script !! Login as \"root\" and try again." 2>&1
  exit -1
fi

# Changing dir to /tmp dir
cd /tmp

# To clone the integral-view.git
echo "Please type your github.com username"
read github_username
echo
git clone https://$github_username@github.com/fractalio/integral-view.git

# To change the branch
echo "Enter your branch name to checkout : "
read branch
echo
cd /tmp/integral-view
git checkout $branch

echo "You are in : "
echo
git branch

# To Create RPM Build Environment
echo
echo "Creating RPM Building environment .."
rpm_path="/root/rpmbuild/"

mkdir -p ~/rpmbuild/{RPMS,SRPMS,BUILD,SOURCES,SPECS,tmp}
cat <<EOF >~/.rpmmacros
%_topdir   %(echo $HOME)/rpmbuild
%_tmppath  %{_topdir}/tmp
EOF


# Directory creation
mkdir /tmp/fractalio_integral_view-0.2
mkdir -p /tmp/fractalio_integral_view-0.2/opt
mkdir -p /tmp/fractalio_integral_view-0.2/etc
mkdir -p /tmp/fractalio_integral_view-0.2/srv
mkdir -p /tmp/fractalio_integral_view-0.2/usr/lib/python2.6/site-packages/
mkdir -p /tmp/fractalio_integral_view-0.2/var/log/fractalio

mkdir -p /tmp/fractalio_integral_view-0.2/etc/nginx/sites-enabled/
mkdir -p /tmp/fractalio_integral_view-0.2/etc/uwsgi/vassals

mkdir -p /tmp/fractalio_integral_view-0.2/opt/fractalio/bin
mkdir -p /tmp/fractalio_integral_view-0.2/opt/fractalio/integral_view
# This will be created by fractalio-dns*.rpm package /tmp/fractalio_integral_view-0.2/opt/fractalio/named
mkdir -p /tmp/fractalio_integral_view-0.2/opt/fractalio/mnt/admin_vol
mkdir -p /tmp/fractalio_integral_view-0.2/opt/fractalio/scripts
mkdir -p /tmp/fractalio_integral_view-0.2/opt/fractalio/installed-software
mkdir -p /tmp/fractalio_integral_view-0.2/opt/fractalio/tmp

# MANAGE.PY FILE 
cp /tmp/integral-view/manage.py  /tmp/fractalio_integral_view-0.2/opt/fractalio/integral_view

# COPYING THE BIN DIRECTORY ..integral_view/bin to ..opt/fractalio/
cp -rf /tmp/bin/* /tmp/fractalio_integral_view-0.2/opt/fractalio/bin/

# COPYING UTILITY SCRIPTS - THIS WILL COPY BOTH PYTHON AND SHELL DIRECTORIES.
cp -rf /tmp/integral-view/scripts/*  /tmp/fractalio_integral_view-0.2/opt/fractalio/scripts/

# COPYING TO SITE PACKAGES
cp -rf /tmp/integral-view/common/python/fractalio /tmp/fractalio_integral_view-0.2/usr/lib/python2.6/site-packages/        

# COPYING SALT MODULES
cp -rf /tmp/integral-view/salt /tmp/fractalio_integral_view-0.2/srv/

# UPDATING INTEGRAL - view  -- "Django app"
cp -rf /tmp/integral-view/integral_view/ /tmp/fractalio_integral_view-0.2/opt/fractalio/integral_view/

# COPYING DEFAULTS DIRECTORY
cp -rf /tmp/integral-view/defaults/ /tmp/fractalio_integral_view-0.2/opt/fractalio/
mkdir -p /tmp/fractalio_integral_view-0.2/opt/fractalio/defaults/logs/alerts
mkdir -p /tmp/fractalio_integral_view-0.2/opt/fractalio/defaults/logs/audit

# SO THE /tmp DIRECTORY CONTAINS fractalio_integral_view-0.2/
# NOW CREATE THE DIRECTORY STRUCTURE
cd /tmp ; tar -cvzf fractalio_integral_view-0.2.tar.gz fractalio_integral_view-0.2/

# NOW MOVE THE /tmp/fractalio_integral_view-0.2/ to where ?
mv /tmp/fractalio_integral_view-0.2/ /root/rpmbuild/SOURCES/
mv /tmp/fractalio_integral_view-0.2.tar.gz /root/rpmbuild/SOURCES/

# INSERT THE .spec FILE INTO ~/rpmbuild/SPECS/

cat <<EOF > /root/rpmbuild/SPECS/fractalio_integral_view.spec

# Don't try fancy stuff like debuginfo, which is useless on binary-only
# packages. Don't strip binary too
# Be sure buildpolicy set to do nothing

%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress

Summary:       Installs the IntergralView - a Management Graphical User Interface (GUI).
Name:          fractalio_integral_view
Version:       0.2
Release:       1
License:       Fractalio Custom Licence
Group:         Development/Tools
SOURCE0:       %{name}-%{version}.tar.gz
URL:           http://www.fractalio.com/
Requires:      nginx,uwsgi
BuildRoot:     %{_tmppath}/%{name}-%{version}-root

%description
This package installs the IntegralView - a management Graphical User Interface (GUI) for the IntegralStore Hardware. This package creates /opt/fractalio/.. directory structure and and also adds required entries in the /etc/rc.local file on that machine.

%prep
%setup -q

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

# in builddir
cp -a * %{buildroot}

%clean
rm -rf %{buildroot}

%preun
#rm -rf /config/*

%files
%defattr(-,root,root,-)
#%dir /config/
/opt/fractalio/*
/etc/nginx/sites-enabled
/etc/uwsgi/vassals
/srv/*
/usr/lib/python2.6/site-packages/*
/var/log/*

%post

#!/bin/bash
cp -rf /tmp/fractalio_integral_view-0.2/opt/fractalio/integral_view/ /opt/fractalio/
ln -s /opt/fractalio/integral_view/integral_view/integral_view_nginx.conf /etc/nginx/sites-enabled/
ln -s /opt/fractalio/integral_view/integral_view/integral_view_uwsgi.ini /etc/uwsgi/vassals/
echo "/usr/local/bin/uwsgi --emperor /etc/uwsgi/vassals --uid root --gid root" >> /etc/rc.local

chmod 755 /opt/fractalio/scripts/python/*
chmod 755 /opt/fractalio/scripts/shell/*

(crontab -l 2>/dev/null; echo "*/1 * * * * /opt/fractalio/scripts/python/generate_status.py > /tmp/out_status >> /tmp/err_status") | crontab -

(crontab -l 2>/dev/null; echo "*/1 * * * * /opt/fractalio/scripts/python/poll_for_alerts.py > /tmp/out_alerts >> /tmp/err_alerts") | crontab -

# I have commented this out for future reference and use.
#(crontab -l 2>/dev/null; echo "*/1 * * * * /etc/fractalio/python/generate_status.py > /tmp/out_status >> /tmp/err_status") | crontab -
#(crontab -l 2>/dev/null; echo "*/1 * * * * /etc/fractalio/batch_jobs/poll_for_alerts.py > /tmp/out_alerts >> /tmp/err_alerts") | crontab -
#(crontab -l 2>/dev/null; echo "*/1 * * * * /etc/fractalio/batch_jobs/batch_jobs.py > /tmp/out_batch >> /tmp/err_batch") | crontab -

%postun
sed -i "/\/usr\/local\/bin\/uwsgi --emperor \/etc\/uwsgi\/vassals --uid root --gid root/d" /etc/rc.local
rm -rf /opt/fractalio
rm -rf /etc/uwsgi/vassals
rm -rf /etc/nginx/sites-enabled
rm -rf /srv/salt
rm -rf /usr/lib/python-2.6/site-packages/fractalio

%changelog
* Fri Feb 27 2015  Ramaseshan <ramaseshan@fractalio.com> 0.2
- Few Minor Bug Fixes
- Path changes and the new Dashboard integrated
* Fri Dec 19 2014  Omkar Sharma MN <omkar@fractalio.com> 0.1-1
- Creates directories inside /etc/, /usr and /var/log/
- First Build

EOF

# To create a rpm
rpmbuild -ba /root/rpmbuild/SPECS/fractalio_integral_view.spec

ls /root/rpmbuild/RPMS/x86_64/
echo "Deleting the /tmp/integral-view"
if [ -e "/tmp/integral-view" ] ; then
  cp -r /tmp/integral-view/configuration_management/login_menu/* /srv/salt/conf_files/
  rm -rf /tmp/integral-view
  echo "The /tmp/integral-view got deleted."
  echo "Executing ls -l /tmp/integral-view : " 
  ls -l /tmp/integral-view

else
  rm -rf "Directory /tmp/integral-view cannot be deleted. "
fi
