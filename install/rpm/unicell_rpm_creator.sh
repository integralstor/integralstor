#!/bin/bash
### Unicell rpm creation part ###
rm -rf /root/rpmbuild

### To Create RPM Build Environment ###
echo
echo "Creating RPM Building environment .."
rpm_path="/root/rpmbuild/"

mkdir -p ~/rpmbuild/{RPMS,SRPMS,BUILD,SOURCES,SPECS,tmp}
cat <<EOF >~/.rpmmacros
%_topdir   %(echo $HOME)/rpmbuild
%_tmppath  %{_topdir}/tmp
EOF


### Directory creation part ###

if [[ ! -d "/root/unicell_rpm/integralstor-unicell-1.0" ]]; then
    echo
    echo "Creating UniCELL RPM Directory..."
    mkdir -p /root/unicell_rpm/integralstor-unicell-1.0

else
    echo "UniCELL RPM Directory exist continuing..."
fi

echo
echo "Creating UniCELL specific Directories..."

DIR_LIST="/root/unicell_rpm/integralstor-unicell-1.0/opt/integralstor /root/unicell_rpm/integralstor-unicell-1.0/opt/integralstor/pki /root/unicell_rpm/integralstor-unicell-1.0/run/samba /root/unicell_rpm/integralstor-unicell-1.0/var/log/integralstor/integralstor_unicell /root/unicell_rpm/integralstor-unicell-1.0/opt/integralstor/integralstor_unicell/tmp /root/unicell_rpm/integralstor-unicell-1.0/opt/integralstor/integralstor_unicell/config/status /root/unicell_rpm/integralstor-unicell-1.0/etc/nginx/sites-enabled /root/unicell_rpm/integralstor-unicell-1.0/etc/uwsgi/vassals"

for dir in $DIR_LIST; do
    if [[ ! -d "$dir" ]]; then
        echo "'$dir' Directory Does Not Exist creating '$dir'"
	mkdir -p $dir
    fi
done

echo
echo "Creating UniCELL specific Files..."

FILE_LIST="/root/unicell_rpm/integralstor-unicell-1.0/var/log/integralstor/integralstor_unicell/integral_view.log /root/unicell_rpm/integralstor-unicell-1.0/opt/integralstor/ramdisks.conf /root/unicell_rpm/integralstor-unicell-1.0/var/log/integralstor/integralstor_unicell/ramdisks"
for file in $FILE_LIST; do
    if [[ ! -e "$file" ]]; then
        echo "'$file' File Does Not Exist Creating..."
	touch $file
    fi
done

### MANAGE FILE ###
cp -rf /root/unicell_rpm/integralstor_common /root/unicell_rpm/integralstor-unicell-1.0/opt/integralstor
cp -rf /root/unicell_rpm/integralstor_unicell /root/unicell_rpm/integralstor-unicell-1.0/opt/integralstor

cp -rf /root/unicell_rpm/integralstor_unicell_tar_installs.tar.gz /root/unicell_rpm/integralstor-unicell-1.0/opt/integralstor
cp -rf /root/unicell_rpm/unicell_rpm_post.sh /root/unicell_rpm/integralstor-unicell-1.0/opt/integralstor

### NOW MOVE THE /root/unicell_rpm/integralstor-unicell-1.0/ to where ? ###
cd /root/unicell_rpm/
tar -cvzf integralstor-unicell-1.0.tar.gz integralstor-unicell-1.0/

cp -rf /root/unicell_rpm/integralstor-unicell-1.0/ ~/rpmbuild/SOURCES/
cp -rf /root/unicell_rpm/integralstor-unicell-1.0.tar.gz ~/rpmbuild/SOURCES/

# INSERT THE .spec FILE INTO ~/rpmbuild/SPECS/
cat <<EOF > /root/rpmbuild/SPECS/integralstor_unicell.spec

# Don't try fancy stuff like debuginfo, which is useless on binary-only
# packages. Don't strip binary too
# Be sure buildpolicy set to do nothing

%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress

Summary:       Installs the IntegralSTOR UniCELL packages and its dependencies for using IntegralSOTR UniCELL (A NAS).  
Name:          integralstor-unicell
Version:       1.0
Release:       1
License:       Fractalio Custom Licence
Group:         Development/Tools
Requires:      yum-utils,salt-master = 2014.7.1,salt-minion = 2014.7.1,python-pip = 7.1.0,ypbind,ypserv = 2.19,ntp = 4.2.6p5,nginx = 1.6.2,kexec-tools = 2.0.0,fractalio_django = 0.1,python-devel = 2.6.6,vsftpd = 2.2.2,sg3_utils = 1.28,perl-Config-General = 2.52,scsi-target-utils = 1.0.24,nfs-utils,smartmontools,samba-client = 4.1.11,samba = 4.1.11,samba-winbind = 4.1.11,samba-winbind-clients = 4.1.11,ipmitool = 1.8.11,OpenIPMI = 2.0.16,zfs,krb5-workstation = 1.10.3,perl,zlib = 1.2.3,python-setuptools = 0.6.10,gcc = 4.4.7,kmod-mv94xx = 4.0.0.1541N-1,xinetd,shellinabox
SOURCE0:       %{name}-%{version}.tar.gz
URL:           http://www.fractalio.com/
BuildRoot:     %{_tmppath}/%{name}-%{version}-root
#BuildArch:     noarch

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
#chown root /opt/integralstor/unicell_rpm_post.sh
#chmod 700 /opt/integralstor/unicell_rpm_post.sh

sh /opt/integralstor/unicell_rpm_post.sh >/tmp/rpm_post_script_log
if [ $? -ne 0 ]; then
echo "CRITICAL: Running post install script Failed!"
exit 1
fi 
sleep 2

%changelog

* Thu Sep 29 2016 Naveenkumar<naveen@fractalio.com> 1.0
- Created neccessary directories and linked files for respective directories as per the ks file
- First Build

EOF

# To create a rpm
rpmbuild -ba /root/rpmbuild/SPECS/integralstor_unicell.spec

if [ $? -ne 0 ]; then
  echo "CRITICAL: RPM creation Failed!!!"
  exit 1
else
echo "Successfully created the IntegralSTOR UniCELL RPM! Location:: /root/rpmbuild/RPMS/x86_64/"
ls /root/rpmbuild/RPMS/x86_64/
cp -rf /root/rpmbuild/RPMS/x86_64/integralstor-unicell-1.0-1.x86_64.rpm /root/unicell_rpm/integralstor_unicell_rpms
cd /root/unicell_rpm/
tar -czf integralstor_unicell_rpms.tar.gz integralstor_unicell_rpms/
fi 
