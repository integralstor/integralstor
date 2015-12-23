# ISCSI Targets

This section explains the various operations relating to ISCSI targets in the UNICell system.

Block based access in the UNICell system is exposed through the ISCSI protocol. As with all user data, the block data will need to reside on ZFS. You will first need to create a ZFS block device volume and then use this volume as the underlying LUN for an ISCSI target. 

UNICell also supports initiator and target user based authentication and IP based ACLs for initiators. 

*Please note that the usernames that are used for initiator and target authentication are specific to the ISCSI module and are not the same as the users that are created for CIFS local user authentication.*