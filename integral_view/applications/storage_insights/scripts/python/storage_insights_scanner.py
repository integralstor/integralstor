import optparse
import sys
import os
import time
import signal
import platform

try:
    import scan_utils
except Exception, e:
    from integralstor.applications.storage_insights import scan_utils

if __name__ == '__main__':
    try:

        parser = optparse.OptionParser()
        parser.add_option('-d', '--fromdjango', action='store_false', dest='standalone', default=True)
        parser.add_option('-s', '--scan_config_id', action='store', type=int, dest='scan_configuration_id')
        (options, args) = parser.parse_args()
        standalone = options.standalone

        if not options.scan_configuration_id:
            raise Exception('No configuration specified. This is a required parameter.')

        scan_configuration_id = options.scan_configuration_id

        signal.signal(signal.SIGTERM, scan_utils.signal_handler)

        configs, err = scan_utils.get_scan_configurations(scan_configuration_id=scan_configuration_id)
        if err:
            raise Exception(err)

        if not configs:
            raise Exception('Unknown configuration specified')


        ret, err, error_list, scanned_dirs_count, scanned_files_count, successful_creation_modification_transactions_count, failed_creation_modification_transactions_count, successful_deletion_transactions_count, failed_deletion_transactions_count, new_files_count, modified_files_count, deleted_files_count = scan_utils.initiate_scan(standalone = standalone, scan_configuration_id = scan_configuration_id)
        #print ret, err, error_list
        if error_list:
            print 'The following errors occurred during the collection process : '
            for (path, error) in error_list:
                print '%s : %s'%(path, error)
        if err:
            raise Exception('The scan process failed to complete successfully : %s'%err)
        else:
            print 'The scan process completed successfully.'
            print 'Scanned a total of %d directories and %d files. Successfully processed %d creations/modofication transactions with %d errors and %d deletion transactions with %d errors. %d new files, %d modified files and %d deleted files detected in this scan.'%(scanned_dirs_count, scanned_files_count, successful_creation_modification_transactions_count, failed_creation_modification_transactions_count, successful_deletion_transactions_count, failed_deletion_transactions_count, new_files_count, modified_files_count, deleted_files_count)
    except Exception, e:
        print str(e)
        sys.exit(-1)
    else:
        sys.exit(0)
    finally:
        try:
            os.remove('/var/run/integralstor/applications/storage_insights_scan')
        except Exception, e:
            pass
