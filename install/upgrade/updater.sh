#!/bin/bash
echo "IntegralStor Upgrade started... Do not reboot or shutdown the system."

echo "Pulling IntegralView updates"
# Setup IntegralStor Common
mkdir /opt/integralstor/integralstor/install/upgrade
cd /tmp
/bin/tar xzf integralstor_utils.tar.gz
yes | cp -rf /tmp/integralstor_utils/site-packages/integralstor_utils/* /opt/integralstor/integralstor_utils/site-packages/integralstor_utils
yes | cp -rf /tmp/integralstor_utils/scripts /opt/integralstor/integralstor_utils

rm -rf /tmp/integralstor_utils

# Setup IntegralStor UNICell
cd /tmp
/bin/tar xzf integralstor.tar.gz
yes | cp -rf /tmp/integralstor/integral_view/* /opt/integralstor/integralstor/integral_view
yes | cp -rf /tmp/integralstor/site-packages/integralstor/* /opt/integralstor/integralstor/site-packages/integralstor
yes | cp -rf /tmp/integralstor/version /opt/integralstor/integralstor
yes | cp -rf /tmp/integralstor/scripts /opt/integralstor/integralstor
yes | cp -rf /tmp/integralstor/install/upgrade/* /opt/integralstor/integralstor/install/upgrade
rm -rf /tmp/integralstor

echo "IntegralView update successful"

echo "Pulling Database updates"
sqlite3 /opt/integralstor/integralstor/config/db/integral_view_config.db <<"EOF"
ALTER TABLE email_config ADD COLUMN "email_audit" bool NOT NULL DEFAULT '0';
EOF
sqlite3 /opt/integralstor/integralstor/config/db/integral_view_config.db <<"EOF"
ALTER TABLE email_config ADD COLUMN "email_quota" bool NOT NULL DEFAULT '0';
EOF
echo "Databases update successful."

echo "IntegralStor UNICell has been successfully updated. System is Going to Restart now..."
