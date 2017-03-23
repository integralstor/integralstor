#!/bin/bash

echo
read -t 60 -p "Enter upgrade system IP address : " input
echo "Pulling updates from : " $input
read -t 30 -p "Press 'yes' to Confirm: " confirm

if [ "$confirm" == "yes" ]; then

	cd /tmp
	wget -c http://$input/netboot/distros/centos/6.6/x86_64/integralstor/v1.0/updater.sh
	chmod +x /tmp/updater.sh
	/tmp/updater.sh $input
	# Needs checking to see if updater was successful. echo $? ?
	rm -f /tmp/updater.sh
	read -t 30 -p "Successfully Updated to Latest software. Press 'yes' to restart the system now: " again
		if [ "$again" == "yes" ]; then
			reboot now
		else
			echo "You must restart your server before the new settings will take effect."
		fi
else
	echo "Updating cancelled. Exiting"
fi
