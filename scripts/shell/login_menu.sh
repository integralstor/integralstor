#!/bin/bash

pause(){
  read -p "Press [Enter] key to continue..." key
}
 
update_ntp_date(){
  clear
  echo
  echo
  read -p "Enter the NTP server from which to synchronize the date : " server
  echo
  echo
  echo 'Stopping NTP service..'
  systemctl stop ntpd
  echo 'Synchronizing date..'
  ntpdate -b $server
  echo 'Starting NTP service..'
  systemctl start ntpd
  pause
}

winbind_restart(){
  clear
  echo
  echo
  read -p "That this could cause a short data access disruption! Proceed (y/n) : " input
  case $input in
    y)echo "Restarting Windows winbind service... ";systemctl restart winbind;pause;;
  esac
}

smb_restart(){
  clear
  echo
  echo
  read -p "That this could cause a short data access disruption! Proceed (y/n) : " input
  case $input in
    y)echo "Restarting Windows smb service... ";systemctl restart smb;pause;;
  esac
}

ntpd_restart(){
  clear
  echo
  echo
  read -p "That this could cause a short data access disruption! Proceed (y/n) : " input
  case $input in
    y)echo "Restarting time service... ";systemctl restart ntpd;pause;;
  esac
}

integralview_restart(){
  clear
  echo
  echo
  read -p "This could cause a short disruption in access to IntegralView. Proceed (y/n)? : " input
  case $input in
    y)echo "Restarting IntegralView services... ";systemctl restart uwsginew;systemctl restart nginx;pause;;
  esac
}

restart_iscsi(){
  clear
  echo
  echo
  read -p "This could cause a short disruption in access to iscsi. Proceed (y/n)? : " input
  case $input in
    y)echo "Restarting iscsi services... ";systemctl restart tgtd;pause;;
  esac
}

restart_vsftpd(){
  clear
  echo
  echo
  read -p "This could cause a short disruption in access to FTP. Proceed (y/n)? : " input
  case $input in
    y)echo "Restarting ftp services... ";systemctl restart vsftpd;pause;;
  esac
}

restart_shellinabox(){
  clear
  echo
  echo
  read -p "This could cause a short disruption in shell access in UI. Proceed (y/n)? : " input
  case $input in
    y)echo "Restarting shell services... ";systemctl restart shellinaboxd;pause;;
  esac
}

restart_nfs(){
  clear
  echo
  echo
  read -p "This could cause a short disruption in access to NFS data. Proceed (y/n)? : " input
  case $input in
    y)echo "Restarting nfs services... ";systemctl restart nfs;pause;;
  esac
}

configure_network_interface(){
  #echo "configure networking called"
  python /opt/integralstor/integralstor/scripts/python/configure_networking.py interface
}

create_nic_bond(){
  python /opt/integralstor/integralstor/scripts/python/create_nic_bond.py 
  pause
}

remove_nic_bond(){
  python /opt/integralstor/integralstor/scripts/python/remove_nic_bond.py 
  pause
}

view_node_status(){
  python /opt/integralstor/integralstor/scripts/python/display_node_status.py
  pause
}
view_node_config(){
  python /opt/integralstor/integralstor/scripts/python/display_node_config.py
  pause
}

generate_manifest_and_status(){
  python /opt/integralstor/integralstor_utils/scripts/python/generate_manifest.py
  python /opt/integralstor/integralstor_utils/scripts/python/generate_status.py
  pause
}


do_reboot() {
  reboot now
  pause
}


do_shutdown() {
  shutdown -h now
  pause
}


show_menu() {
  clear
  echo "-------------------------------"	
  echo " IntegralSTOR UNIcell - Menu"
  echo "-------------------------------"
  echo "  1.  Configure a network interface"
  echo "  2.  Reboot"
  echo "  3.  Shutdown"
  echo "  4.  View configuration"
  echo "  5.  View process status"
  echo "  6.  Scan system configuration"
  echo "  7.  Update date using NTP"
  echo "  8.  Restart services"
  echo "      | 81. Restart smb   82. Restart Winbind               83. Restart iscsi   84. Restart shell service"
  echo "      | 85. Restart NTP   86. Restart IntegralView services 87. Restart FTP     88. Restart NFS"
  echo "  9.  Create NIC Bond"
  echo "  10. Remove NIC Bond"
  echo "  11. Exit"
  echo

}

read_input(){
  local input 
  read -p "Enter choice...: " input
  case $input in
    1) configure_network_interface ;;
    2) do_reboot;;
    3) do_shutdown;;
    4) view_node_config;;
    5) view_node_status;;
    6) generate_manifest_and_status;;
    7) update_ntp_date;;
    9) create_nic_bond;;
   10) remove_nic_bond;;
   11) logout;;
   81) smb_restart;;
   82) winbind_restart;;
   83) restart_iscsi;;
   84) restart_shellinabox;;
   85) ntpd_restart;;
   86) integralview_restart;;
   87) restart_vsftpd;;
   88) restart_nfs;;
    *)  echo "Not a Valid INPUT" && sleep 2
  esac
}
 
user_name=`id -un`
if [[ ("$user_name" != "root") && ("$user_name" != "integralstor") ]]
then
  trap '' SIGINT SIGQUIT SIGTSTP
  while true
  do
    echo "The integralstor console menu has started" > /tmp/out
    show_menu
    read_input
    echo "The integralstor console menu has stopped" >> /tmp/out
  done
fi
