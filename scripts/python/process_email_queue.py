
from integralstor import mail
from integralstor_utils import db, lock, logger

import logging
import datetime
import atexit
atexit.register(lock.release_lock, 'process_email_queue')

def main():
    lg = None
    try:
        lg, err = logger.get_script_logger(
            'Process email queue', '/var/log/integralstor/scripts.log', level=logging.DEBUG)

        logger.log_or_print('Processing email queue initiated.', lg, level='info')
        lck, err = lock.get_lock('process_email_queue')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock. Exiting.')

        ret, err = mail.process_email_queue()
        if err:
            raise Exception(err)
    except Exception, e:
        #print str(e)
        logger.log_or_print('Error processing email queue: %s' %
                            e, lg, level='critical')
        lock.release_lock('process_email_queue')
        return -1,  'Error processing email queue: %s' % e
    else:
        lock.release_lock('process_email_queue')
        logger.log_or_print(
            'Processing email queue completed successfully.', lg, level='info')
        return 0, None


if __name__ == "__main__":
    main()


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
