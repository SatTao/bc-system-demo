# TODO.md

List of changes and improvements that are TODO for bcc system

## TODO

- Move file handling to a daemon in outputmanager
- Move data uploads to a daemon in outputmanager
- Implement storeforlater in case of internet connectivity issues

- Move sfx routines to a daemon to avoid delays to data entry

- Reliably handle multi-day operations by checking times and opening new csv files etc.
- Adjust parse function so that it matches for exact text in commands, and only uses 'contains' etc for variables like empNum

- support scanning to indicate that you're on an hourly card - Maybe implement a job-code recognition function that appends if detected.

- support encoding the local IP for the bc server, with support for changing it and storing back to the config file if necessary

- work towards running headless tests of the units - need to create and test cron jobs on the system at boot with a screen attached, then run it headless and check that it works ok etc. See browser bookmarks for a couple of appropriate methods, including auto-login.

- Prototype an xml data export functionality - this may be the preferred long term method of pushing data. Might look like FTP drop xml to a folder for scheduled collection.

- A few things to store as config - server IP, secret keys, names and IDs, endpoint/drop-folder info, custom variables, location names, etc.

- Do we need to ensure that the system clock is up to date? Could we cross-reference with an online time source for safety?

- How are we going to handle caching? A database? A text file? Dropping multiple xmls in a folder, and deleting them when uploaded?
- If we do xml caching - implement a barcode to report the quantity of cached events for debugging network drops.
- shall we build a daemon to poll the local network occasionally - ensuring that we have good knowledge of network status?

- Build a test function to run ftp file drops to a test server, preferably a local one, but can start with speedtest.tele2.net, using ftplib. 

- Update date and time formats to match BC requirements (see N's email)