# Deleting/Rolling back to/Renaming a snapshot

- Select the “**Storage**” main menu item on the left of the screen.

- Select the “**Snapshot manager**” sub menu tab.

You will then see a list of all the snapshots taken on all pools/datasets/volumes. For each of the snapshots, some basic information will be displayed. You will also have the option of deleting/rolling back/renaming any of the snapshots.

Before deleting/rolling back to a snapshot, you will be prompted for a confirmation as these operation involve the potential loss of data.

A note from the ZFS documentation about rolling back to a snapshot :

*“Rolling back to a previous snapshot will discard any data changes between that snapshot and the current time. Further, by default, you can only rollback to the most recent snapshot. In order to rollback to an earlier snapshot, you must destroy all snapshots between the current time and that snapshot you wish to rollback to. If that's not enough, the filesystem must be unmounted before the rollback can begin. This means downtime.”*