# Configuring Active Directory (AD) authentication for CIFS shares

- Select the “**Services**” main menu item on the left of the screen.

- Select the “**Configure CIFS access**” sub menu tab.

- Make sure that the current authentication method is set to Active Directory. If not, click on the “**Change authentication method**” button to select Active directory. This will then take you to a screen that allows you to configure the settings for the Active Directory authentication server.



The required parameters for this are :

**Authentication server DNS name** : The DNS name of your Active Directory Server. Please note that you will need to configure UNICell's DNS server settings to add your Active Directory's DNS NAME and IP address otherwise authentication will fail.

**Authentication server IP address** : The IP address of the Active Directory server.

**AD Domain/Realm** : The Doman name of your Active Directory domain.

**AD Admininstrator password** : Enter the administrator password of your Active Directory server. This is required for the UNICell storage server to join the Active Directory domain in order to query and authenticate against it. This password is never stored in the UNICell server. It is only used for the initial join.

**Workgroup** : The workgroup of your Active Directory server

Once this information is entered and saved, the UNICell server will then attempt to join the Active Directory domain of your Active Directory server. If this process is successful, then when you try to create a new CIFS share, you should see the users and groups from Active Directory being displayed in that screen.