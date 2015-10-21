zfs_conf:
  file.managed:
    - name: /etc/modprobe.d/zfs.conf
    - source: salt://conf_files/zfs.conf
    - force: True

resolv.conf:
  file.managed:
    - name: /etc/resolv.conf
    - source: salt://conf_files/resolv.conf
    - force: True
  
ramdisk_file:
  file.managed:
    - name: /etc/init.d/ramdisk
    - source: salt://conf_files/ramdisk
    - force: True
  
fpctl_bin:
  file.managed:
    - name: /opt/fractalio/bin/fpctl
    - source: salt://conf_files/fpctl
    - force: True

start_ttys:
  file.managed:
    - name: /etc/init/start-ttys.conf
    - source: salt://conf_files/start-ttys.conf
    - force: True

fractalmenu:
  file.managed:
    - name: /etc/init/fractalmenu.conf
    - source: salt://conf_files/fractalmenu.conf
    - force: True

commands:
  cmd.script:
    - source: salt://conf_files/mod_commands.sh

