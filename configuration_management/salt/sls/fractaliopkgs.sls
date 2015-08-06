fractaliopkgs:
  pkgrepo.managed:
    - humanname: Fractal Packages
    - baseurl: http://10.1.1.200/fractaliolocal

smartmontools:
  pkg.installed:
    - skip_verify: True
    - refresh: True

glusterfs:
  pkg.installed:
    - skip_verify: True
    - refresh: True
 
glusterfs-fuse:
  pkg.installed:
    - skip_verify: True
    - refresh: True

glusterfs-server:
  pkg.installed:
    - skip_verify: True
    - refresh: True

ctdb:
  pkg.installed:
    - skip_verify: True
    - refresh: True

samba-client:
  pkg.installed:
    - skip_verify: True
    - refresh: True

samba:
  pkg.installed:
    - skip_verify: True
    - refresh: True

samba-vfs-glusterfs:
  pkg.installed:
    - skip_verify: True
    - refresh: True

samba-winbind:
  pkg.installed:
    - skip_verify: True
    - refresh: True

samba-winbind-clients:
  pkg.installed:
    - skip_verify: True
    - refresh: True

ipmitool:
  pkg.installed:
    - skip_verify: True
    - refresh: True

OpenIPMI:
  pkg.installed:
    - skip_verify: True
    - refresh: True

zfs:
  pkg.installed:
    - skip_verify: True
    - refresh: True

krb5-workstation:
  pkg.installed:
    - skip_verify: True
    - refresh: True

bind:
  pkg.installed:
    - skip_verify: True
    - refresh: True

ypbind:
  pkg.installed:
    - skip_verify: True
    - refresh: True

ypserv:
  pkg.installed:
    - skip_verify: True
    - refresh: True

ntp:
  pkg.installed:
    - skip_verify: True
    - refresh: True

uwsgi:
  pkg.installed:
    - skip_verify: True
    - refresh: True

nginx:
  pkg.installed:
    - skip_verify: True
    - refresh: True

kexec-tools:
  pkg.installed:
    - skip_verify: True
    - refresh: True

fractalio_django:
  pkg.installed:
    - skip_verify: True
    - refresh: True

fractalio_integral_view:
  pkg.installed:
    - skip_verify: True
    - refresh: True

fractalio_zpool_creation:
  pkg.installed:
    - skip_verify: True
    - refresh: True

python-devel:
  pkg.installed:
    - skip_verify: True
    - refresh: True

setuptools:
  cmd.run:
    - cwd: /tmp
    - name: |
        cd /tmp
        wget -c http://10.1.1.200/fr_software/setuptools-11.3.1.tar.gz
        tar xzf setuptools-11.3.1.tar.gz
        cd setuptools-11.3.1
        python setup.py install
    - shell: /bin/bash
    - timeout: 300

dnspython:
  cmd.run:
    - cwd: /tmp
    - name: |
        cd /tmp
        wget -c http://10.1.1.200/fr_software/dnspython-1.12.0.tar.gz
        tar xzf dnspython-1.12.0.tar.gz
        cd dnspython-1.12.0
        python setup.py install
    - shell: /bin/bash
    - timeout: 300


uwsgi-python:
  cmd.run:
    - cwd: /tmp
    - name: |
        cd /tmp
        wget -c http://10.1.1.200/fr_software/uwsgi-2.0.9.tar.gz
        tar xzf uwsgi-2.0.9.tar.gz
        cd uwsgi-2.0.9
        python setup.py install
    - shell: /bin/bash
    - timeout: 300

libgfapi:
  cmd.run:
    - cwd: /tmp
    - name: |
        cd /tmp
        wget -c http://10.1.1.200/fr_software/libgfapi-python.tar.gz
        tar xzf libgfapi-python.tar.gz
        cd libgfapi-python
        python setup.py install
    - shell: /bin/bash
    - timeout: 300
