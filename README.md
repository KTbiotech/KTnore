# KTnore
KTnore workflow: quantitative, real-time species identification from metagenomic samples using nanopore sequencing
KTnore aims to become an easy-to-use metagenomic wrapper, fulfilling the core tasks of metagenomic analysis from start to finish: quality control reading, mapping and real-time taxnonomy classification from data nanopore sequencing. KTnore uses centrifuge with custom database as the core of taxonomy analysis, combined with nanopore meta information from basecaling results to help analysts fully understand the data.

KTnore uses interactive local web through Ampps software, collecting and storing analytical information from time to time.
#### Usage
```
python3 KTnore_monitor.py -h
usage: KTnore_monitor.py [-h] -id JOBID [-log LOG_MONITOR] -sig SIG_FOLDER
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
