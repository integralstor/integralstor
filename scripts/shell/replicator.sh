set -o xtrace
source_pool=$1
source_dataset=$2
destination=$3
user=$4
ip=$5
source=$source_pool/$source_dataset
#echo $source $destination

# The first and the last snapshot on the source server
# Sort by creation date so that you always get the latest snapshot by date and not name
primary_initial=""
primary_initial_shapshot=""
primary_last=""
primary_last_snapshot=""
secondary_last=""
secondary_last_snapshot=""

primary_snapshot () {
	primary_last=$(sudo zfs list -t snapshot -o name -s creation | grep $source | tail -1)
	primary_initial=$(sudo zfs list -t snapshot -o name -s creation | grep $source | head -1)

	#Get the snapshot names. The Hack. Needs a better code.
	IFS=’@’ read -a primary_initial_snapshot <<< "${primary_initial}"
	#echo "Initaial Primary Snapshot: $source@${primary_initial_snapshot[1]}"
	IFS=’@’ read -a primary_last_snapshot <<< "${primary_last}"
	#echo "Primary Latest Snapshot: $source@${primary_last_snapshot[1]}"

	} 
secondary_snapshot () {
	#Last successful snapshot from destination server
	# Sort by creation date so that you always get the latest snapshot by date and not name
	secondary_last=$(ssh $user@$ip "sudo zfs list -t snapshot -o name -s creation | grep $destination/$source_dataset | tail -1")

	IFS=’@’ read -a secondary_last_snapshot <<< "${secondary_last}"
	#echo "Secondary latest snapshot: $source@${secondary_last_snapshot[1]}"
	}

primary_snapshot
secondary_snapshot

if [[ -z "${secondary_last_snapshot[1]}" ]]; then

	# Sync the initial snapshot
	initial_sync=$(sudo zfs send -vD $source@${primary_initial_snapshot[1]} | mbuffer -s 128k -m 1G 2>/dev/null | ssh $user@$ip "mbuffer -s 128k -m 1G | sudo zfs receive -Fdv $destination")
	echo "${initial_sync}"

        # Incase the first and last snapshot are not the same, then also do a recursive replication till the present snapshot
	secondary_snapshot
        if [ "${primary_initial_snapshot[1]}" != "${primary_last_snapshot[1]}" ]; then
		recursive_sync=$(sudo zfs send -vDI $source@${secondary_last_snapshot[1]} $source@${primary_last_snapshot[1]} | mbuffer -s 128k -m 1G 2>/dev/null | ssh $user@$ip "mbuffer -s 128k -m 1G | sudo zfs receive -Fdv $destination")
		#echo $recursive_sync
	fi

else
	#If secondary is not none

	#If the destination and the source last snapshots are the not the same, then incremental sync of snapshots
     	if [ "${secondary_last_snapshot[1]}" != "${primary_last_snapshot[1]}" ]; then
		#echo "${secondary_last_snapshot} ${primary_last_snapshot}"
		snapshot_sync=$(sudo zfs send -vDI $source@${secondary_last_snapshot[1]} $source@${primary_last_snapshot[1]} | mbuffer -s 128k -m 1G 2>/dev/null | ssh $user@$ip "mbuffer -s 128k -m 1G | sudo zfs receive -Fdv $destination")
	        #echo "${snapshot_sync}"
	else
		echo "Both datasets are in sync. No replication required"
	fi

fi
