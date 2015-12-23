# Replacing faulty disks

The UNICell system will only give you the option to replace a drive if its S.M.A.R.T. status reports a warning or error. Check the disk status (described above) to see the status of the drives. If there is a problem with a drive then you will see a button saying “**Replace (swap out) this disk**” next to it. 

If the selected disk is not part of an existing ZFS pool then clicking this button will just display an alert saying that you can go ahead and replace the disk without the need for data protection. In this case, after you replace the disk, you need to scan the system for hardware changes and make sure that the new disk serial number displays correctly in the new hardware configuration before accepting it (please refer to the “**Hardware scan**” sub section of the “**Viewing/Modifying the UNICell System configuration**” section above for more details)


If the selected disk is part of an existing ZFS pool, then clicking on the “**Replace (swap out) this disk**” button will take you through a wizard that will guide you through a disk replacement procedure as described below :

- The first step in the process is a confirmation of the serial number of the disk that you are about to replace. Proceeding here will result in ZFS taking the selected disk offline as a precursor to its replacement.

- If the previous step succeeded then you will be prompted to then replace the disk with a new disk. NOTE: Please note down the serial number of the Old and the New disks for confirmation purposes. After you replace the disk, please give the operating system a few seconds to load the information about the new disk before proceeding.
 
- Proceeding from the previous step results in the UNICell system scanning for new disks. If the new disk is discovered, then its serial number is displayed for confirmation purposes.

- If you confirm the information from the previous step and proceed, then the system will then replace the Old disk with the New one in the ZFS pool and bring the new disk online. This is then followed by a rescan of the system to update the hardware details with those of the new disk. The results of all these operation are then displayed.