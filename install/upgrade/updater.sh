#!/bin/bash
echo "IntegralStor Upgrade started... Do not reboot or shutdown the system."

echo "Pulling IntegralView updates"
# Setup IntegralStor Common
mkdir /opt/integralstor/integralstor_unicell/install/upgrade
cd /tmp
/bin/tar xzf integralstor_common.tar.gz
yes | cp -rf /tmp/integralstor_common/site-packages/integralstor_common/* /opt/integralstor/integralstor_common/site-packages/integralstor_common
yes | cp -rf /tmp/integralstor_common/scripts /opt/integralstor/integralstor_common

rm -rf /tmp/integralstor_common

# Setup IntegralStor UNICell
cd /tmp
/bin/tar xzf integralstor_unicell.tar.gz
yes | cp -rf /tmp/integralstor_unicell/integral_view/* /opt/integralstor/integralstor_unicell/integral_view
yes | cp -rf /tmp/integralstor_unicell/site-packages/integralstor_unicell/* /opt/integralstor/integralstor_unicell/site-packages/integralstor_unicell
yes | cp -rf /tmp/integralstor_unicell/version /opt/integralstor/integralstor_unicell
yes | cp -rf /tmp/integralstor_unicell/scripts /opt/integralstor/integralstor_unicell
yes | cp -rf /tmp/integralstor_unicell/install/upgrade/* /opt/integralstor/integralstor_unicell/install/upgrade
rm -rf /tmp/integralstor_unicell

echo "IntegralView update successful"

echo "Pulling Database updates"
sqlite3 /opt/integralstor/integralstor_unicell/config/db/integral_view_config.db <<"EOF"
ALTER TABLE email_config ADD COLUMN "email_audit" bool NOT NULL DEFAULT '0';
EOF
sqlite3 /opt/integralstor/integralstor_unicell/config/db/integral_view_config.db <<"EOF"
ALTER TABLE email_config ADD COLUMN "email_quota" bool NOT NULL DEFAULT '0';
EOF
echo "Databases update successful."

echo "IntegralStor UNICell has been successfully updated. System is Going to Restart now..."
