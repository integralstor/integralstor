#!/bin/bash

echo ">>> Inside post script <<<"

echo "Disabling selinux..."
sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
echo "Disabling all repositories..."
yum-config-manager --disable "*"

service iptables stop
service ip6tables stop
chkconfig iptables off
chkconfig ip6tables off

echo "***	Started pre package execution	***"
echo "Switching to working directory..."
cd /opt/integralstor
echo "Started installing Non rpm installs..."
tar xzf integralstor_unicell_tar_installs.tar.gz

if [[ -d "integralstor_unicell_tar_installs" ]]; then
    cd /opt/integralstor/integralstor_unicell_tar_installs

    cd sysstat-11.0.5
    ./configure --prefix=/usr
    make
    make install
    sleep 1
    cd /opt/integralstor/integralstor_unicell_tar_installs
    rm -rf sysstat-11.0.5

    cd /opt/integralstor/integralstor_unicell_tar_installs
    tar xzf setuptools-11.3.1.tar.gz
    cd setuptools-11.3.1
    python setup.py install
    sleep 1
    cd /opt/integralstor/integralstor_unicell_tar_installs
    rm -rf setuptools-11.3.1.tar.gz

    cd /opt/integralstor/integralstor_unicell_tar_installs
    tar xzf uwsgi-2.0.9.tar.gz
    cd uwsgi-2.0.9
    python setup.py install
    sleep 1
    cd /opt/integralstor/integralstor_unicell_tar_installs
    rm -rf uwsgi-2.0.9.tar.gz

    cd /opt/integralstor/integralstor_unicell_tar_installs
    tar xzf netifaces-0.10.4.tar.gz
    cd netifaces-0.10.4
    python setup.py install
    sleep 1
    cd /opt/integralstor/integralstor_unicell_tar_installs
    rm -rf netifaces-0.10.4.tar.gz

    cd /opt/integralstor/integralstor_unicell_tar_installs
    tar xzf python-dateutil-2.4.2.tar.gz
    cd python-dateutil-2.4.2
    python setup.py install
    sleep 1
    cd /opt/integralstor/integralstor_unicell_tar_installs
    rm -rf python-dateutil-2.4.2.tar.gz

    cd /opt/integralstor/integralstor_unicell_tar_installs
    tar xzf python-crontab-1.9.3.tar.gz
    cd python-crontab-1.9.3
    python setup.py install
    sleep 1
    cd /opt/integralstor/integralstor_unicell_tar_installs
    rm -rf python-crontab-1.9.3.tar.gz

    cd /opt/integralstor/integralstor_unicell_tar_installs
    tar xzf zfs-auto-snapshot.tar.gz
    cd zfs-auto-snapshot
    make install
    sleep 1
    cd /opt/integralstor/integralstor_unicell_tar_installs
    rm -rf zfs-auto-snapshot.tar.gz

else
    echo "'integralstor_unicell_tar_installs' Directory Does Not Exist so exiting..."
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "CRITICAL: Non RPM installation Failed!"
    exit 1
else
    echo "Successfully installed Non RPM installs."
fi

cd /opt/integralstor
rm -rf /opt/integralstor/integralstor_unicell_*
   
sleep 2

echo "***	Started post install operations	***"

### Adding a user and group called integralstor. ###
groupadd integralstor -g 500
useradd integralstor -g 500
groupadd replicator -g 501
useradd replicator -g 501
echo "integralstor123" | passwd --stdin integralstor
echo "replicator123" | passwd --stdin replicator
echo "integralstor    ALL=(ALL)    ALL" >> /etc/sudoers
echo "replicator    ALL=(ALL)    NOPASSWD: /sbin/zfs" >> /etc/sudoers
#echo "AllowUsers replicator integralstor" >> /etc/ssh/sshd_config #root is allowed temp. untill fixes for replicator.

### Network interface configuration  ###
ACTIVE_INTERFACES=`ifconfig | awk -vRS= -vFS="\n" '{ if ( $0 ~ /inet\ addr:/ ) { print }}' | sed 's/[ \t].*//;/^\(lo\|\)$/d'`
for IF in $ACTIVE_INTERFACES
do
echo "Configuring $IF to be static address" >> /root/post_install.log 2>&1
rm -f /etc/sysconfig/network-scripts/ifcfg-$IF
cat >> /etc/sysconfig/network-scripts/ifcfg-$IF <<EOF
DEVICE=$IF
HWADDR=`ifconfig $IF | grep HWaddr | awk '{print $5}'`
ONBOOT=yes
BOOTPROTO=none
IPADDR=`ifconfig $IF |awk 'BEGIN {FS = "[: ]+"} ; /inet addr/{print $4}'`
NETMASK=`ifconfig $IF |awk 'BEGIN {FS = "[: ]+"} ; /inet addr/{print $8}'`
EOF
GATEWAY_IP=`netstat -nr | awk '{ if ($4 ~/UG/) print; }' | awk -v CUR_IF=$IF '$NF==CUR_IF {print $2};'`
# The variable $GATEWAY_IP might be empty if all/some subgroup of interface(s) connect to the same network subnet or if some interface(s) has
# an unspecified/no gateway.
if [ ! -z "$GATEWAY_IP" ]
then
cat >> /etc/sysconfig/network-scripts/ifcfg-$IF <<EOF
GATEWAY=$GATEWAY_IP
EOF
fi
cat >> /etc/sysconfig/network-scripts/ifcfg-$IF <<EOF
TYPE=Ethernet
NM_CONTROLLED=no
USERCTL=no
PEERDNS=yes
IPV6INIT=no
EOF
done


### Setting hostname ###
STRING=$(ifconfig | grep eth0 | head -1 | awk '{print $5}' | awk -F ':' '{print tolower($5 $6)}')
hnpart="unicell-"$STRING
hostname="$hnpart.integralstor.lan"
echo "Hostname will be : " $hostname ; echo
echo "HOSTNAME=$hostname" > /etc/sysconfig/network
echo "NETWORKING=yes" >> /etc/sysconfig/network
# Editing /etc/hosts
ip=$(ifconfig | awk -F':' '/inet addr/&&!/127.0.0.1/{split($2,_," ");print _[1]}')
echo "$ip $hnpart $hostname" >> /etc/hosts

### Disabling BOOTPROTO for all interfaces ###
INTERFACES="eth0 eth1 eth2 eth3"
for IF in $INTERFACES
do
sed -i 's/BOOTPROTO=dhcp/BOOTPROTO=none/' /etc/sysconfig/network-scripts/ifcfg-$IF
done

### SSHD configuration ###
/etc/init.d/sshd stop
sed '' /etc/ssh/sshd_config > /etc/ssh/original_sshd_config
sed '/#PermitRootLogin/a PermitRootLogin no' /etc/ssh/sshd_config > /etc/ssh/temp_file
#echo 'AllowUsers integralstor' >> /etc/ssh/temp_file
sed -e '/requiretty/s/^/#/g' -i /etc/sudoers    #serach for requiretty and comment. This is to avoid tty for replication in zfs send/receive
rm -f /etc/ssh/sshd_config
mv /etc/ssh/temp_file /etc/ssh/sshd_config
/etc/init.d/sshd start
ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''

### Editing the /etc/yum.repos.d/CentOS-Base.repo ###
# ..to disable base, updates and extras repositories. ###

#cp -rf /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/Original-CentOS-Base-repo
#sed -i '/\[base\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo 
#sed -i '/\[updates\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo 
#sed -i '/\[extras\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo
#sed -i '/\[centosplus\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo
#sed -i '/\[contrib\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo

ln -s /opt/integralstor/integralstor_common/site-packages/integralstor_common /usr/lib/python2.6/site-packages/integralstor_common
ln -s /opt/integralstor/integralstor_unicell/site-packages/integralstor_unicell /usr/lib/python2.6/site-packages/integralstor_unicell

ln -s /opt/integralstor/integralstor_unicell/platform /opt/integralstor
mv /etc/sysconfig/shellinaboxd /etc/sysconfig/shellinaboxd.bak
ln -s /opt/integralstor/integralstor_unicell/config/shellinabox/shellinaboxd /etc/sysconfig
echo "self" >> /opt/integralstor/integralstor_unicell/platform
chmod 755 /opt/integralstor/integralstor_unicell/scripts/python/*
chmod 755 /opt/integralstor/integralstor_unicell/scripts/shell/*
rm -rf /etc/init/start-ttys.conf
cp -f /opt/integralstor/integralstor_unicell/install/conf_files/start-ttys.conf /etc/init
cp -f /opt/integralstor/integralstor_unicell/install/conf_files/integralstor_unicell_menu.conf /etc/init
rm -rf /etc/nsswitch.conf
cp /opt/integralstor/integralstor_unicell/install/conf_files/nsswitch.conf /etc

### Configure nginx ###
ln -s /opt/integralstor/integralstor_unicell/integral_view/integral_view_nginx.conf /etc/nginx/sites-enabled/
sed -i 's/conf.d/sites-enabled/g' /etc/nginx/nginx.conf

### Cinfigure xinetd ###
cd /etc/xinetd.d/
mv rsync rsync.bak
ln -s /opt/integralstor/integralstor_unicell/install/conf_files/rsync /etc/xinetd.d/
#sed -i 's/disable = yes/disable = no/' /etc/xinetd.d/rsync

### Configure uwsgi ###
ln -s /opt/integralstor/integralstor_unicell/integral_view/integral_view_uwsgi.ini /etc/uwsgi/vassals/
echo "/usr/bin/uwsgi --emperor /etc/uwsgi/vassals --uid root --gid root >/var/log/integralstor/integralstor_unicell/integral_view.log 2>&1 &" >> /etc/rc.local
sed -i "/\/usr\/local\/bin\/uwsgi --emperor \/etc\/uwsgi\/vassals --uid root --gid root/d" /etc/rc.local
rm -rf /etc/init.d/uwsgi
ln -s /opt/integralstor/integralstor_common/scripts/init/uwsgi /etc/init.d/

### Configure ramdisks ###
#Change the ramdisks conf file name and location, move it into /opt/integralstor so it can be common to unicell and gridcell
touch /opt/integralstor/ramdisks.conf
touch /var/log/integralstor/integralstor_unicell/ramdisks
rm -rf /etc/init.d/ramdisk
ln -fs /opt/integralstor/integralstor_common/install/scripts/ramdisk /etc/init.d/
chmod +x /etc/init.d/ramdisk

### copying kmod-mv94xx directory to systems kernel Directory(This is spesific to Marvel servers) ###
cp -rf /lib/modules/2.6.32-431.el6.x86_64/extra/mv94xx /lib/modules/2.6.32-504.el6.x86_64/extra


###configure crontab ###
(crontab -l 2>/dev/null; echo 'MAILTO=""') | crontab -
(crontab -l 2>/dev/null; echo "SHELL=/bin/sh") | crontab -
(crontab -l 2>/dev/null; echo "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin") | crontab -
(crontab -l 2>/dev/null; echo "*/1 * * * * /opt/integralstor/integralstor_common/scripts/python/generate_status.py > /tmp/out_status >> /tmp/err_status") | crontab -
(crontab -l 2>/dev/null; echo "*/10 * * * * /usr/lib64/sa/sa1 1 1 -S DISK > /tmp/out_status >> /tmp/err_status") | crontab -
(crontab -l 2>/dev/null; echo "10,40 * * * * /usr/bin/python -c 'from integralstor_common import zfs; zfs.execute_remote_replication()' > /tmp/replication_alerts >> /tmp/replication_errors") | crontab -
(crontab -l 2>/dev/null; echo "*/1 * * * * /opt/integralstor/integralstor_common/scripts/python/poll_for_alerts.py > /tmp/out_alerts >> /tmp/err_alerts") | crontab -
(crontab -l 2>/dev/null; echo "* * * * * /usr/bin/python -c 'from integralstor_common import scheduler_utils; scheduler_utils.run_from_shell()' > /tmp/scheduler_alerts >> /tmp/scheduler_errors") | crontab -
(crontab -l 2>/dev/null; echo "0 0 * * * /usr/bin/python -c 'from integralstor_common import logs; logs.auto_rotate_logs()' > /tmp/auto_rotate_logs_alerts >> /tmp/auto_rotate_errors") | crontab -

###configure ZFS ###
rm -f /etc/modprobe.d/zfs.conf
ln -fs /opt/integralstor/integralstor_common/install/conf_files/zfs.conf /etc/modprobe.d
cp -rf /opt/integralstor/integralstor_unicell/install/conf_files/zed.rc /etc/zfs/zed.d

### configuring Vsftpd ###
rm -f /etc/vsftpd/vsftpd.conf
ln -fs /opt/integralstor/integralstor_unicell/install/conf_files/vsftpd.conf /etc/vsftpd

### configuring zed for zfs ###
#cd /etc/zfs
#/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/6.6/x86_64/integralstor_unicell/v1.0/zed.d
#cd /etc/init/
ln -s /opt/integralstor/integralstor_unicell/install/conf_files/zed.cconf /etc/init/
#wget -c http://192.168.1.150/netboot/distros/centos/6.6/x86_64/integralstor_unicell/v1.0/zed.conf
#cd /etc/sysconfig/modules/
#/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/6.6/x86_64/integralstor_unicell/v1.0/zfs.modules #laoding ZFS module

### Configure rc.local ###
modprobe ipmi_devintf
modprobe 8021q
cp -f /sbin/zed /etc/init.d
echo "/sbin/zed" >> /etc/rc.local
echo "modprobe ipmi_devintf" >> /etc/rc.local
echo "/sbin/modprobe zfs" >> /etc/rc.local
chmod 755 /etc/rc.local
ln -sf /etc/rc.local /etc/rc3.d/S99local

chkconfig --add ramdisk
chkconfig rpcbind on
chkconfig nfs on
chkconfig winbind on
chkconfig smb on
chkconfig tgtd on
chkconfig ntpd on
chkconfig crond on
chkconfig ramdisk on
chkconfig uwsgi on

echo "Completed post install operations."
