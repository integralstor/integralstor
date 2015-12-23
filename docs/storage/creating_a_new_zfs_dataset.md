# Creating a new ZFS dataset

- Select the “**Storage**” main menu item on the left of the screen.

- Select the “**ZFS Pool manager**” sub menu tab.

- The main area will then display the list of all available pools along with the datasets/block device volumes in each of the pools.

- Corresponding to each pool, you will see a button saying “**View pool details**”. Clicking on this will take you to a screen that displays the pool details.

- You will then see a section called “**Filesystem datasets**”. This will show all the datasets in the selected pool.

- This table also provides you with a button called “**Create a new filesystem dataset**”. Clicking on this will take you to a screen which prompts for the following information before creating the dataset :

**Dataset name** : Select a name for the new dataset.

**Enable compression** : Selecting this will result in the underlying data potentially being compressed on disk.  The ZFS documentation says :


*“Compression is transparent with ZFS if you enable it. This means that every file you store in your pool can be compressed. From your point of view as an application, the file does not appear to be compressed, but appears to be stored uncompressed. In other words, if you run the "file" command on your plain text configuration file, it will report it as such. Instead, underneath the file layer, ZFS is compressing and decompressing the data on disk on the fly. And because compression is so cheap on the CPU, and exceptionally fast with some algorithms, it should not be noticeable.

Obviously, compression can vary on the disk space saved. If the dataset is storing mostly uncompressed data, such as plain text log files, or configuration files, the compression ratios can be massive. If the dataset is storing mostly compressed images and video, then you won't see much if anything in the way of disk savings. 
Enabling compression on a dataset is not retroactive. It will only apply to newly committed or modified data. Any previous data in the dataset will remain uncompressed. So, if you want to use compression, you should enable it before you begin committing data.”*

**Enable deduplication** : Enabling this options results in block level deduplication to be enabled on the dataset. Since this requires the use of the RAM to store the dedup tables, please ensure that you have sufficient RAM available on the system before enabling this option.