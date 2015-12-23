# Creating a NFS share

- Select the “**Shares and targets**” main menu item on the left of the screen.

- Select the “**NFS Shares**” sub menu tab.

- Click the “**Create NFS Share**” button at the bottom of the list.


You will be prompted for the following information before the share can be created :

**Share Name** : A unique name for the share being created.

**Underlying ZFS dataset** : All CIFS shares have to be within an existing ZFS dataset. Select the dataset where you want this new share to reside. If you want it on a new dataset then, create the dataset first before coming to this screen.

**Directory selector** : Click on the browse button to browse the directory structure within the selected dataset and select the required directory for this share. If you want to create a new directory, select the parent directory using this selector and then use the next option to specify the name of the new directory.

**Create Directory in the selected path** : If you would like to create a new directory then specify the new directory name here. You can select the parent directory of this new directory by using the selectory above.

**Final path** : This is just for informational purposes and displays the actual path that will be used for this share.

**Client IP's** : Use this option to provide access control for this share based on the IP addresses of Client machines. Use a comma separated list of IP addresses here.

**Readonly** : Check this option if you want a readonly share.

**Do not treat remote root user as local root** : Checking this will prevent root users connected remotely from having root privileges.

**Treat all client users as anonymous users**: Checking this will force all users to be treated as anonymous users.