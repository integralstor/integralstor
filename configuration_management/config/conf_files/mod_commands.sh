chmod +x /opt/integralstor/integralstor_common/bin/fpctl
mkdir -p /run/samba
modprobe ipmi_devintf
echo "modprobe ipmi_devintf" >> /etc/rc.local
chmod +x /etc/init.d/ramdisk
chkconfig ramdisk on
sed -i 's/\$ZFS mount -a/\$ZFS mount -O -a/' /etc/init.d/zfs
#sed -i 's/master: 10.1.1.200/master: fractalio-pri.fractalio.lan/' /etc/salt/minion
rm -rf /tmp/*
yes | rm -f /etc/salt/pki/minion/minion_master.pub
yes | rm -f /etc/salt/minion_id
service salt-minion stop && shutdown -r now
