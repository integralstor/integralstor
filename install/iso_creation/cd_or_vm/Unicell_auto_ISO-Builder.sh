#!/usr/sh

### Prepare the env ###
echo "Clearing ISO Directory..."
rm -rf /root/CentOs7/unicell_centos7_dir/*
cd /root
yum -y install rsync yum-utils createrepo genisoimage isomd5sum yum-downloadonly

### Setup the env ###
mkdir /root/CentOs7/unicell_centos7_dir
cd /root/CentOs7/unicell_centos7_dir

### mount the Base Os ###
echo "Mounting Base ISO..."
mount -o loop,ro /root/CentOS-7-x86_64-Minimal.iso /mnt
rsync -av /mnt/ .
find . -name TRANS.TBL -exec rm -f {} \;

### copy all the Packages and createrepo for ur software(*Make sure you dont get any deppendancy error here) ###
cp /root/CentOs7/unicell_centos7_rpms/*.rpm /root/CentOs7/unicell_centos7_dir/Packages
#cp /root/zfs_new_rpms/*.rpm /root/unicell_iso_usb/Packages
rpm --initdb --dbpath /root/CentOs7/unicell_centos7_dir/Packages/
rpm -ivh --test --dbpath /root/CentOs7/unicell_centos7_dir/Packages/ /root/CentOs7/unicell_centos7_dir/Packages/*.rpm
cd /root/CentOs7/unicell_centos7_dir

echo "Repodata..."
echo
ls repodata/
gunzip repodata/f8d0beedfb3eb1b4c22ca0428863c9042c431df30d43a9cf3a19e429292e0030-comps.xml.gz
mv repodata/454e5218194d965357821ab75a580b27645e43d2de591013c3d81477da7310b5-comps.xml repodata/comps.xml
#createrepo -u "media://`head -1 .discinfo`" -g repodata/comps.xml .
createrepo -g repodata/comps.xml .
echo "Repodata..."
echo
ls repodata/

### Copying the files you wanted fot install ###
cd /root
cp /root/CentOs7/ks.cfg /root/CentOs7/unicell_centos7_dir/
chmod 755 /root/CentOs7/unicell_centos7_dir
chmod +x /root/CentOs7/unicell_centos7_dir
cp -rf /root/CentOs7/isolinux.cfg /root/CentOs7/unicell_centos7_dir/isolinux
#cp -rf /root/usb/splash.jpg /root/CentOs7/unicell_centos7_dir/isolinux
#cp -rf /root/BOOTX64.conf /root/unicell_iso_usb/EFI/BOOT
#cp -rf /root/plash.jpg /root/unicell_iso_usb/EFI/BOOT
cp -rf /root/CentOs7/tar_files /root/CentOs7/unicell_centos7_dir
cp -rf /root/CentOs7/conf_files /root/CentOs7/unicell_centos7_dir
chmod 755 /root/CentOs7/unicell_centos7_dir/isolinux/isolinux.cfg 
chmod +x /root/CentOs7/unicell_centos7_dir/isolinux/isolinux.cfg

### Creating ISO with all the files containing Directory ###
#cp /root/tar_files/integralstor_unicell.tar.gz /tmp
#cd /tmp
#tar xzf integralstor_unicell.tar.gz
#cat /tmp/integralstor_unicell/version > /root/unicell_iso/version 

cd /root/CentOs7/unicell_centos7_dir

echo "Creating ISO... "
echo
mkisofs -R -J -T -v -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -V "IntegralSTOR UNICell" \
    -p "Fractalio Data Pvt Ltd" \
    -A "IntegralSTOR UNICell" \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -x "lost+found" \
    --joliet-long \
    -o /tmp/centos7/IntegralSTOR_UNICell.iso .

umount /mnt
md5sum /tmp/centos7/IntegralSTOR_UNICell.iso >/tmp/centos7/checksum_UniCELL.txt
echo
echo "ISO Created!! Find it in /tmp/centos7/IntegralSTOR_UNICell.iso"
echo
