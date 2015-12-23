# Create a new CIFS share

- Select the “**Shares and targets**” main menu item on the left of the screen.

- Select the “**CIFS Shares**” sub menu tab.

- Click on the “**Create CIFS share**” button at the bottom of the list of shares.



You will then be prompted for the following information in order to create a share :

**Share Name** : A unique name for the share being created.

**Underlying ZFS dataset** : All CIFS shares have to be within an existing ZFS dataset. Select the dataset where you want this new share to reside. If you want it on a new dataset then, create the dataset first before coming to this screen.

**Directory selector** : Click on the browse button to browse the directory structure within the selected dataset and select the required directory for this share. If you want to create a new directory, select the parent directory using this selector and then use the next option to specify the name of the new directory.

**Create Directory in the selected path** : If you would like to create a new directory then specify the new directory name here. You can select the parent directory of this new directory by using the selectory above.

**Final path** : This is just for informational purposes and displays the actual path that will be used for this share.

**Readonly** : Check this option if you want a readonly share.

**Visible** : Check this option if you want this share to be visible when someone browses the UNICell server from a windows browser.

**Accessible to all(guest ok)** : If you do NOT want access control and would like this share to be accessible to all, then check this option.

**Permitted users** : Use this to select the users who have access to this share. This option is enabled only when the “Accessible to all” option is not checked.

**Permitted groups** : Use this to select the groups who have access to this share. This option is enabled only when the “Accessible to all” option is not checked.