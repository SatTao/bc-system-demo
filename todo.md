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

- for readability and storage, keep each event as an object and provide some utility functions (Partially done)
- support scanning to indicate that you're on an hourly card

- support encoding the local IP for the bc server, with support for changing it and storing back to the config file if necessary

- work towards running headless tests of the units - need to create and test cron jobs on the system at boot with a screen attached, then run it headless and check that it works ok etc. See browser bookmarks for a couple of appropriate methods, including auto-login.

- Pass in station as an argument to init for each manager class so that they can back reference to use other managers. E.g. sfx can access terminaloutput etc.
