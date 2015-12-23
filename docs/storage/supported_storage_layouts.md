# Supported storage layouts

The UNICell system currently supports the following layout types :

- **Stripe** – Used where only data access speed is required. Cannot tolerate any disk failures.

- **Mirror** – A 2 way default mirroring.

- **RAID5** – Minimum of 3 unused disks required. Can tolerate a 1 disk failure.

- **RAID6** -  – Minimum of 4 unused disks required. Can tolerate a simultaneous 2 disk failure.

- **RAID10** – Minimum of 4 unused disks required. Used for speed and some level of data loss. Can tolerate a one disk failure in each mirror.