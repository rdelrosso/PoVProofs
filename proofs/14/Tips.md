# Tips for FULL-RECOVERY-RTO

* When a fresh Atlas shape is created with Cloud Provider Snapshots enabled, then the first daily backup is triggered automagically. If you start loading initial data immediately then the first backup only contains a partial set of data.  Therefore Manual backup is required after data load. This is to ensure to have a backup of a precalculated size.
* The cluster that is used for a restore test is advised to be created with maximum available IOPS. This will speed up the initial load of data and reduce the restore time.  E.g. with M30 at min 120 IOPS versus max 600 IOPS the restore time differs a factor 2. 
* When loading data it is important not to exceed 90% disk space used. This will trigger a disk autoscale operation which slows down data loading.
* Clusters with NVMe memory do not have faster restore times, because backup and restore is done via hidden 4th node that has traditional disks.
* A fast way to generate more data volume from an initial load, is to multiple the number of collections with an aggregation. E.g below template will add 100 copy of you initial collection to the database.
   ```js
      for i in {1..100}; 
        do
          mongo <CON> --eval 'db.<COL>.aggregate([{"$out": "<COL>'${i}'"}])'
      done
  ```


