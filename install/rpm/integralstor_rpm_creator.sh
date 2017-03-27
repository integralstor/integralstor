#!/bin/bash

### change the version number, release number and architecture whenever we create rpm ###
version_number=1.0
release_number=1
arch=noarch

if [ $(id -u) != "0" ]; then
    echo "You must be the superuser to run this script" >&2
    exit 1
fi

### Unicell rpm creation part ###
rm -rf /root/integralstor_rpm/rpmbuild

### Create RPM Build Environment ###
echo
echo "Creating RPM Building environment .."
rpm_path="/root/integralstor_rpm/rpmbuild/"

mkdir -p /root/integralstor_rpm/rpmbuild/{RPMS,SRPMS,BUILD,SOURCES,SPECS,tmp}
mkdir -p /root/integralstor_rpm/rpmbuild/RPMS/{i386,i586,i686,noarch,x86_64}
cat <<EOF >~/.rpmmacros
%_topdir   %(echo $HOME)/integralstor_rpm/rpmbuild
%_tmppath  %{_topdir}/tmp
%_unpackaged_files_terminate_build      0
%_binaries_in_noarch_packages_terminate_build   0
EOF

### Directory & files creation part ###

if [[ ! -d "/root/integralstor_rpm/integralstor-$version_number" ]]; then
    echo
    echo "Creating UniCELL RPM Directory..."
    mkdir -p /root/integralstor_rpm/integralstor-$version_number

else
    echo "UniCELL RPM Directory exist continuing..."
fi

echo
echo "Creating UniCELL specific Directories..."

DIR_LIST="/root/integralstor_rpm/integralstor-${version_number}/opt/integralstor /root/integralstor_rpm/integralstor-${version_number}/opt/integralstor/pki /root/integralstor_rpm/integralstor-${version_number}/run/samba /root/integralstor_rpm/integralstor-${version_number}/var/log/integralstor/integralstor /root/integralstor_rpm/integralstor-${version_number}/opt/integralstor/integralstor/tmp /root/integralstor_rpm/integralstor-${version_number}/opt/integralstor/integralstor/config/status /root/integralstor_rpm/integralstor-${version_number}/etc/nginx/sites-enabled /root/integralstor_rpm/integralstor-${version_number}/etc/uwsgi/vassals"

for dir in $DIR_LIST; do
    if [[ ! -d "$dir" ]]; then
        echo "'$dir' Directory Does Not Exist creating '$dir'"
	mkdir -p $dir
    fi
done

echo
echo "Creating UniCELL specific Files..."

FILE_LIST="/root/integralstor_rpm/integralstor-${version_number}/var/log/integralstor/integralstor/integral_view.log /root/integralstor_rpm/integralstor-${version_number}/opt/integralstor/ramdisks.conf /root/integralstor_rpm/integralstor-${version_number}/var/log/integralstor/integralstor/ramdisks"
for file in $FILE_LIST; do
    if [[ ! -e "$file" ]]; then
        echo "'$file' File Does Not Exist Creating..."
	touch $file
    fi
done

### MANAGE FILE ###
cp -rf /root/integralstor_rpm/integralstor_utils /root/integralstor_rpm/integralstor-${version_number}/opt/integralstor
cp -rf /root/integralstor_rpm/integralstor /root/integralstor_rpm/integralstor-${version_number}/opt/integralstor

cp -rf /root/integralstor_rpm/integralstor_tar_installs.tar.gz /root/integralstor_rpm/integralstor-${version_number}/opt/integralstor
cp -rf /root/integralstor_rpm/integralstor_rpm_post.sh /root/integralstor_rpm/integralstor-$version_number/opt/integralstor #comment if its in repo
cp -rf /root/integralstor_rpm/initial_setup.sh /root/integralstor_rpm/integralstor-$version_number/opt/integralstor #comment if its in repo

### NOW MOVE THE /root/integralstor_rpm/integralstor-$version_number/ to where ? ###
cd /root/integralstor_rpm/
tar -cvzf integralstor-${version_number}.tar.gz integralstor-${version_number}/
yes | cp -rf /root/integralstor_rpm/integralstor-${version_number}/ /root/integralstor_rpm/rpmbuild/SOURCES/
yes | cp -rf /root/integralstor_rpm/integralstor-${version_number}.tar.gz /root/integralstor_rpm/rpmbuild/SOURCES/

# INSERT THE .spec FILE INTO ~/rpmbuild/SPECS/
cat <<EOF > /root/integralstor_rpm/rpmbuild/SPECS/integralstor.spec

# Don't try fancy stuff like debuginfo, which is useless on binary-only
# packages. Don't strip binary too
# Be sure buildpolicy set to do nothing

%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress

Summary:       Installs the IntegralSTOR UniCELL packages and its dependencies for using IntegralSOTR UniCELL (A NAS).  
Name:          integralstor
Version:       ${version_number}
Release:       ${release_number}
License:       Fractalio Custom Licence
Group:         Development/Tools
Requires:      yum-utils = 1.1.31,sg3_utils = 1.37,perl-Config-General = 2.61,scsi-target-utils = 1.0.55,nfs-utils = 1:1.3.0,smartmontools = 1:6.2,samba-client = 4.2.10,samba = 4.2.10,samba-winbind = 4.2.10,samba-winbind-clients = 4.2.10,ipmitool = 1.8.13,OpenIPMI = 2.0.19,zfs = 0.6.5.7,krb5-workstation = 1.13.2,perl = 4:5.16.3,python-setuptools = 0.9.8,python2-pip = 8.1.2,ypbind = 3:1.37.1,ypserv = 2.31,ntp = 4.2.6p5,nginx = 1:1.6.3,uwsgi = 2.0.12,python-devel = 2.7.5,gcc = 4.8.5,vsftpd = 3.0.2,xinetd = 2:2.3.15,shellinabox = 2.19,urbackup-server = 2.0.38.1660,bind-utils = 32:9.9.4,rsync = 3.0.9,telnet = 1:0.17,vim-enhanced = 2:7.4.160,iptraf-ng = 1.1.4
SOURCE0:       %{name}-%{version}.tar.gz
URL:           http://www.fractalio.com/
BuildRoot:     %{_tmppath}/%{name}-%{version}-root
BuildArch:     $arch

%description
This package installs the IntegralView - a management Graphical User Interface (GUI) for the IntegralSTOR Hardware. This package creates /opt/integralstor/.. directory structure and and also adds required entries in the /etc/rc.local file on that machine.

%prep
%setup -q

%build
#Empty section.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

# in builddir
cp -a * %{buildroot}

%clean
rm -rf %{buildroot}

%preun

%files
%defattr(-,root,root,-)
/opt/integralstor/
/etc/nginx/sites-enabled
/etc/uwsgi/vassals
/var/
/run/samba/

%post -p /bin/bash 

echo ">>> Inside post <<<"
   
sleep 2
#chown root /opt/integralstor/integralstor_rpm_post.sh
chmod 700 /opt/integralstor/integralstor_rpm_post.sh
chmod +x /opt/integralstor/integralstor_rpm_post.sh

#sh /opt/integralstor/integralstor/install/rpm/integralstor_rpm_post.sh >/tmp/rpm_post_script_log
sh /opt/integralstor/integralstor_rpm_post.sh >/tmp/rpm_post_script_log
if [ $? -ne 0 ]; then
echo "CRITICAL: Running post install script Failed!"
exit 1
fi 
sleep 2

%changelog

* Wed Feb 15 2017 Naveenkumar<naveen@fractalio.com> 1.0-1
- Rewritten all for Centos 7.2 and for hosting repository.
- First Build - Centos 7.2
* Thu Sep 29 2016 Naveenkumar<naveen@fractalio.com> 1.0
- Created neccessary directories and linked files for respective directories as per the ks file
- First Build

EOF

### To create a rpm
rpmbuild -ba /root/integralstor_rpm/rpmbuild/SPECS/integralstor.spec

if [ $? -ne 0 ]; then
  echo "CRITICAL: RPM creation Failed!!!"
  exit 1
else
  echo "Successfully created IntegralSTOR UNICell RPM!"
  echo "Location:'/root/integralstor_rpm/rpmbuild/RPMS/$arch/'"
  ls /root/integralstor_rpm/rpmbuild/RPMS/$arch/
  yes | cp -rf /root/integralstor_rpm/rpmbuild/RPMS/$arch/integralstor-${version_number}-${release_number}.$arch.rpm /root/integralstor_rpm/integralstor_rpms
  cd /root/integralstor_rpm/
  mkdir -p /root/integralstor_rpm/integralstor_rpm_files/${version_number}-${release_number}
  yes | cp -rf /root/integralstor_rpm/rpmbuild/RPMS/$arch/integralstor-${version_number}-${release_number}.$arch.rpm /root/integralstor_rpm/integralstor_rpm_files/${version_number}-${release_number}
  yes | cp -rf /root/integralstor_rpm/rpmbuild/SRPMS/integralstor-${version_number}-${release_number}.src.rpm /root/integralstor_rpm/integralstor_rpm_files/${version_number}-${release_number}
  tar -czf integralstor_tar_installs.tar.gz integralstor_tar_installs
  cp /root/integralstor_rpm/initial_setup.sh /root/integralstor_rpm/integralstor_rpms
  tar -czf integralstor_rpms.tar.gz integralstor_rpms/
fi 
