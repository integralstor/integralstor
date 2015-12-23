# Introduction to the ZFS concepts and terminology

The IntegralStor UNICell system is based upon the ZFS filesystem. ZFS provides many features that combine to provide an extremely scalable and rock solid file system. Some of these features include extreme data integrity(protection against silent disk errors, etc using parity based checksumming), software RAID, read and write caching, copy-on-write, light weight snapshots, deduplication, compression and extreme scalability (it is a 128-bit file system that is capable of managing zettabytes (one billion terabytes) of data!).

Before you can start using your UNICell system, it is useful to be familiar with some of the terminology that is used in ZFS.

**Pool** - The basic building block that is required in order to use a UNICell system is a ZFS Pool. A pool is a logical group of devices describing the layout(RAID, mirror, stripe, etc) and physical characteristics of the available storage. Depending upon the number of underlying storage devices and the layouts, you could have more than one pool on a UNICell system. Pools have many familiar ZFS  features, including copy-on-write, snapshots, clones, and checksumming. A pool is a prerequisite in order to create a ZFS filessystem or a block device volume. 
A pool can be in one of the following states :  online (all well), degraded(when one or more underlying disks have failed but the pool is still accessible) or faulted(no longer usable as more than the minimum number of redundancy has been exceeded due to faulty disks).

**Dataset** - A dataset is a ZFS filesystem that is created on top of a pool. All end user file based data in the UNICell system has to reside in a ZFS dataset. You can turn on features such as compression or deduplication on a dataset.

**Volume** - A volume is a block device that can be created within a pool. In order to create an ISCSI target, a volumes is a prerequisite. You can turn on features such as compression or deduplication on a volume as well.

**Snapshot** - A read-only copy of a dataset(file system) or volume at a given point in time.
Snapshots in ZFS are instantanous and light weight. The copy on write feature of ZFS means that the snapshot contains the original version of the filesystem or volume and the current(live) version of the  volume or file system consists only of the changes since the last snapshot. 
Snapshots can be used to provide a readonly version of a filesystem or volume at a point in time or they can also be used to rollback to a certain point in time.

**Write cache** – A ZFS pool can be configured with a write cache. In the UNICell system can configure the main memory(RAM) to serve as an extremely fast write cache.

**Scrub** – Scrubbing a pool involves calculating the checksum of all the data blocks in the pool and comparing them against the correct checksum stored in the metadata. This is useful to check silent corruption of data. It is suggested that the pools are scrubbed every couple of months. Data access speeds are degraded when a scrub is being done so please schedule it at a time when the usage is low.