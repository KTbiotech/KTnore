# KTnore
KTnore workflow: quantitative, real-time species identification from metagenomic samples using nanopore sequencing
#### Usage
```
python3 KTnore_monitor.py -h
usage: monitor_supper.py [-h] -id JOBID [-log LOG_MONITOR] -sig SIG_FOLDER
                         -mon MON_FOLDER -gpy SUMMARY_FILE [-temp TEMPFOLDER]
                         [-toff TIMEOUT]

The script monitors and links all sub-script files when the realtime process
starts.

optional arguments:
  -h, --help            show this help message and exit
  -id JOBID, --job-id JOBID
                        unique project id
  -log LOG_MONITOR, --log-file LOG_MONITOR
                        log monitor file output
  -sig SIG_FOLDER, --sig_folder SIG_FOLDER
  -mon MON_FOLDER, --mon-folder MON_FOLDER
                        mon_folder
  -gpy SUMMARY_FILE, --summary-file SUMMARY_FILE
                        summary file created by basecalling
  -temp TEMPFOLDER, --tempfolder TEMPFOLDER
                        temp folder
  -toff TIMEOUT, --timeout TIMEOUT
                        after the timeout (s), there is no change in the
                        signal directory, the realtime process will stop
```
