# TODO.md

List of changes and improvements that are TODO for bcc system

## TODO

- Move file handling to a daemon in outputmanager
- Move data uploads to a daemon in outputmanager
- Implement storeforlater in case of internet connectivity issues. FTP drop attempt made-if not successful the file is written to eventCache. Next time upload Daemon successfully uploads a file, it will scour the eventCache folder for un-uploaded files, and attempt to upload them. If they still fail, leave htem there til next time you check. If they work, delete them one by one. This way we guarantee that files get uploaded eventually.

- Move sfx routines to a daemon to avoid delays to data entry

- Reliably handle multi-day operations by checking times and opening new csv files etc. Is this necessary? Event cache should work fine now.

- support scanning to indicate that you're on an hourly card - Maybe implement a job-code recognition function that appends if detected.

- Do we need to ensure that the system clock is up to date? Could we cross-reference with an online time source for safety?

- How are we going to handle caching? A database? A text file? Dropping multiple xmls in a folder, and deleting them when uploaded?
- If we do xml caching - implement a barcode to report the quantity of cached events for debugging network drops.
- shall we build a daemon to poll the local network occasionally - ensuring that we have good knowledge of network status?

- Support supervisors updating a time for a missed bc card using special time codes. e.g. combo code plus employee code plus time-12h time-30m, so it logs the event time backdatedly. Should this support setting a new date too? Like 2019Y 6M 23D 12h 45m? Or we could just set today by default and provide a date-yesterday code. This way we support limited corrections to bc cards, but people cant magically adjust things from any random day and time.

- Move the stacklight management code to a separate class or to the output manager? Avoid complicating things too much within the station class.

- Implement an uptime daemon to send an uptime counter to InitialState - allows us to trigger alerts on dead stations etc

- Implement a cron job that checks for application heartbeat on the main thread. If the main thread is blocked then it kills the process and restarts it, or reboots (maybe safer).

- Reliability tests - it should robustly deal with loss of network without compromising availability for the user - offloading upload functions to daemons and implementing robust local caching. Improve datetime labels on upload files.