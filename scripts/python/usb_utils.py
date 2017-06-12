import os
import sys
import time

from integralstor_utils import command


def _header():
    try:
        os.system('clear')
        print
        print 'IntegralSTOR USB utilities'
        print '----------------------------'
        print
        print
    except Exception, e:
        return None, str(e)
    else:
        return True, None


def unmount():
    try:
        ret, err = _header()
        if err:
            print err
            raise Exception

        mount_points, err = command.get_command_output("cat /var/log/usb-mount.track | cut -d ':' -f 1", shell=True)
        if err:
            raise Exception(err)
        if not mount_points:
            raise Exception(' Nothing to unmount!')
        dev_names, err = command.get_command_output("cat /var/log/usb-mount.track | cut -d ':' -f 2", shell=True)
        if err:
            raise Exception(err)

        count = []
        for i, mount in enumerate(mount_points, start=1):
            count.append(str(i))
            print ' %s. %s of /dev/%s' % (i, mount, dev_names[i-1]) 
        print

        ch = ''
        while True:
            ch = raw_input('Provide a number to unmount its corresponding device(0 to exit): ')
            if ch != '0' and ch not in count:
               print '\t- Provide a valid number'
            else:
                break
        if ch != '0':
            ret, err = command.get_command_output("/opt/integralstor/integralstor/scripts/shell/usb-mount.sh remove %s" % dev_names[int(ch)-1])
            if err:
                raise Exception(err)
            for r in ret:
                print '\n- %s' %r

    except Exception, e:
        print str(e)
        raw_input('\nPress any key to continue')
    else:
        raw_input('\nPress any key to continue')


def copy_to_from():
    pass


if __name__ == '__main__':
    try:
        while True:
            ret, err = _header()
            if err:
                print err
                raise Exception
            print ' 1. Unmount USB drive'
            print ' 2. Copy to/from USB drive'
            print
            ch = raw_input('Enter a number to perform the corresponding operation(0 to exit): ')
            if ch == '0':
                break
            elif ch not in ['1','2']:
                print '\t- Please provide a valid choice from the list.'
                time.sleep(2)
                continue
            elif ch == '1':
                unmount()
            elif ch == '2':
                copy_to_from()

    except Exception, e:
        sys.exit(1)
    else:
        sys.exit(0)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab

