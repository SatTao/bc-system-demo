# TODO.md

List of changes and improvements that are TODO for bcc system

## TODO

- Move file handling to a daemon in outputmanager
- Move data uploads to a daemon in outputmanager
- Implement storeforlater in case of internet connectivity issues
- Implement scrap and reject updates
- Move sfx routines to a daemon to avoid delays to data entry
- Implement settings from config file, e.g. name and stayalive times etc.
- Reliably handle multi-day operations by checking times and opening new csv files etc.
- Adjust parse function so that it matches for exact text in commands, and only uses 'contains' etc for variables like empNum

- for readability and storage, keep each event as a dictionary payload, and shift the dictionary around - it's probably more reliable to do this.
- support scanning to indicate that you're on an hourly card