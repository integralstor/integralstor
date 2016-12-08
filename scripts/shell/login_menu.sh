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
  service ntpd stop
  echo 'Synchronizing date..'
  ntpdate -b $server
  echo 'Starting NTP service..'
  service ntpd start
  pause
}
 
gluster_restart(){
  clear
  echo
  echo
  read -p "That this could cause a short data access disruption to all clients! Proceed (y/n) : " input
  case $input in
    y)echo "Restarting distributed storage service on this GRIDCell.. ";service glusterd restart;pause;;
  esac
}

ctdb_restart(){
  clear
  echo
  echo
  read -p "That this could cause a short data access disruption to all clients! Proceed (y/n) : " input
  case $input in
    y)echo "Restarting distributed Windows service on this GRIDCell.. ";service ctdb restart;pause;;
  esac
}

winbind_restart(){
  clear
  echo
  echo
  read -p "That this could cause a short data access disruption to all clients! Proceed (y/n) : " input
  case $input in
    y)echo "Restarting Windows winbind service on this GRIDCell.. ";service winbind restart;pause;;
  esac
}

smb_restart(){
  clear
  echo
  echo
  read -p "That this could cause a short data access disruption to all clients! Proceed (y/n) : " input
  case $input in
    y)echo "Restarting Windows smb service on this GRIDCell.. ";service smb restart;pause;;
  esac
}

ntpd_restart(){
  clear
  echo
  echo
  read -p "That this could cause a short data access disruption to all clients! Proceed (y/n) : " input
  case $input in
    y)echo "Restarting time service on this GRIDCell.. ";service ntpd restart;pause;;
  esac
}

integralview_restart(){
  clear
  echo
  echo
  read -p "This could cause a short disruption in access to IntegralView. Proceed (y/n)? : " input
  case $input in
    y)echo "Restarting IntegralView services.. ";service uwsgi restart;service nginx restart;pause;;
  esac
}

configure_zfs_pool() {
  clear
  echo
  echo
  read -p "Please ensure that the ZFS pool has not already been created before continuing. Proceed with creating the ZFS pool (y/n)? : " input
  case $input in
    y) python /opt/integralstor/integralstor_gridcell/scripts/python/configure_zfs_pool.py;pause;;
  esac
}

salt_minion_restart(){
  clear
  echo
  echo
  read -p "Proceed with restarting the admin agent (y/n)? : " input
  case $input in
    y)echo "Restarting admin agent services.. ";service salt-minion restart;pause;;
  esac
}

salt_master_restart(){
  clear
  echo
  echo
  read -p "Proceed with restarting the salt master (y/n)? : " input
  case $input in
    y)echo "Restarting salt-master services.. ";service salt-master restart;pause;;
  esac
}

set_cpu_cores(){
  read -p "Enter the number of cores to be disabled from [minimum 2][press 1 to reset]. " ip
  sh /opt/integralstor/integralstor_common/scripts/shell/cpu_core_dis.sh $ip
  sleep 1
}

configure_networking(){
  clear
  echo
  echo
  read -p "If you have already configured the grid, then changing any network setting can cause data loss! Are you sure you want to continue (y/n)? : " input
  case $input in
    y) python /opt/integralstor/integralstor_gridcell/scripts/python/configure_networking.py;pause;;
  esac
}

configure_initial_salt_master(){
  clear
  echo
  echo
  read -p "If you have already configured the grid, then changing the admin master can cause data loss! Are you sure you want to continue (y/n)? : " input
  case $input in
    y) python /opt/integralstor/integralstor_gridcell/scripts/python/configure_initial_minion.py;pause;;
  esac
}

first_time_setup(){
  clear
  echo
  echo
  read -p "If you have already configured the grid, then running the first time setup again will fail and cause data loss! Are you sure you want to continue (y/n)? : " input
  case $input in
    y) python /opt/integralstor/integralstor_gridcell/scripts/python/first_time_setup.py;pause;;
  esac
}

view_node_status(){
  python /opt/integralstor/integralstor_gridcell/scripts/python/display_node_status.py
  pause
}
view_node_config(){
  python /opt/integralstor/integralstor_gridcell/scripts/python/display_node_config.py
  pause
}

reset_minion(){
  /opt/integralstor/integralstor_gridcell/scripts/shell/reset_salt_minion.sh
  pause
}


goto_shell() {
  su -l integralstor
  pause
}

do_reboot() {
  clear
  echo
  echo
  read -p "That this could cause a data access disruption to all clients! Are you sure you want to reboot this GRIDCell? (y/n) : " input
  case $input in
    y)echo "Initiating a reboot of this GRIDCell.. ";reboot now;;
  esac
}


do_shutdown() {
  clear
  echo
  echo
  read -p "That this could cause a data access disruption to all clients! Are you sure you want to shutdown this GRIDCell? (y/n) : " input
  case $input in
    y)echo "Initiating a shutdown of this GRIDCell.. ";shutdown -h now;;
  esac
}

show_menu() {
  clear
  echo
  echo " IntegralStor GRIDCell - Menu"
  echo "============================="
  echo
  echo " GRIDCell configuration"
  echo " ----------------------"
  echo " 10. View GRIDCell configuration"
  echo
  echo " GRIDCell actions"
  echo " ----------------"
  echo " 20. Restart distributed storage services     21. Restart IntegralView services     22. Update date using NTP"
  echo " 23. Shutdown GRIDCell                        24. Reboot GRIDCell                   25. Restart admin agent"
  echo " 26. Restart CTDB                             27. Restart Winbind                   28. Restart smb"
  echo
  echo " Check IntegralView services "
  echo " --------------------------- "
  echo " 30. Check admin services            31. Check web services              32. Check admin volume status"
  echo " 33. Check admin volume services     34. Check admin volume mountpoint"
  echo
  echo " Check grid accessibility"
  echo " ------------------------"
  echo " 40. Check GRIDCell network accessibility     41. Check GRIDCell name/address mapping"
  echo
  echo " Check underlying GRIDCell hardware"
  echo " ----------------------------------"
  echo " 50. Check hard drive status     51. Check hardware components"
  echo

  echo " Check grid storage status"
  echo " -------------------------"
  echo " 60. Check on-disk ZFS filesystem     61. Check Windows storage services             62. Check distributed storage services"
  echo " 63. Check status of grid peers       64. Check distributed Windows access status"
  echo
  echo

}

read_input(){
  local input 
  read -p "Enter the number corresponding to the desired choice : " input 
  case $input in
    10) view_node_config;;
    20) gluster_restart;;
    21) integralview_restart;;
    22) update_ntp_date;;
    23) do_shutdown;;
    24) do_reboot;;
    25) salt_minion_restart;;
    26) ctdb_restart;;
    27) winbind_restart;;
    28) smb_restart;;
    30) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py salt;pause;;
    31) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py integralview_processes;pause;;
    32) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py admin_vol_started;pause;;
    33) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py admin_vol_status;pause;;
    34) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py admin_vol_mountpoint;pause;;
    40) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py ping;pause;;
    41) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py dns;pause;;
    50) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py disks;pause;;
    51) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py ipmi;pause;;
    60) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py zfs;pause;;
    61) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py windows_processes;pause;;
    62) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py gluster_processes;pause;;
    63) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py gluster_peer_status;pause;;
    64) python /opt/integralstor/integralstor_gridcell/scripts/python/monitoring.py ctdb;pause;;
    91) configure_networking ;;
    92) configure_zfs_pool ;;
    93) configure_initial_salt_master ;;
    94) first_time_setup ;;
    95) set_cpu_cores;;
    96) goto_shell;;
    97) salt_master_restart;;
    *)  echo "Not a Valid INPUT" && sleep 2
  esac
}
 
trap '' SIGINT SIGQUIT SIGTSTP
 
while true
do
  echo "The Integralstor menu has started" > /tmp/out
  show_menu 
  read_input
  echo "The Integralstor menu has stopped" >> /tmp/out
done
