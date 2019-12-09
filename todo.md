# TODO.md

List of changes and improvements that are TODO for bcc system

## TODO

- Move file handling to a daemon in outputmanager
- Move data uploads to a daemon in outputmanager
- Implement storeforlater in case of internet connectivity issues. FTP drop attempt made-if not successful the file is written to eventCache. Next time upload Daemon successfully uploads a file, it will scour the eventCache folder for un-uploaded files, and attempt to upload them. If they still fail, leave htem there til next time you check. If they work, delete them one by one. This way we guarantee that files get uploaded eventually.

- Move sfx routines to a daemon to avoid delays to data entry?

- support scanning to indicate that you're on an hourly card - Maybe implement a job-code recognition function that appends if detected.

- Do we need to ensure that the system clock is up to date? Could we cross-reference with an online time source for safety?

- csv caching - implement a barcode to report the quantity of cached events for debugging network drops.

- shall we build a daemon to poll the local network occasionally - ensuring that we have good knowledge of network status?

- Support supervisors updating a time for a missed bc card using special time codes. e.g. combo code plus employee code plus time-12h time-30m, so it logs the event time backdatedly. Should this support setting a new date too? Like 2019Y 6M 23D 12h 45m? Or we could just set today by default and provide a date-yesterday code. This way we support limited corrections to bc cards, but people cant magically adjust things from any random day and time.

- Move the stacklight management code to a separate class or to the output manager? Avoid complicating things too much within the station class.

- Implement an uptime daemon to send an uptime counter to InitialState - allows us to trigger alerts on dead stations etc

- Implement a cron job that checks for application heartbeat on the main thread. If the main thread is blocked then it kills the process and restarts it, or reboots (maybe safer).

- Reliability tests - it should robustly deal with loss of network without compromising availability for the user - offloading upload functions to daemons and implementing robust local caching. Improve datetime labels on upload files.

- Build in support for new voice files, noteably:
-- announcing scrap quantities
-- announcing clearing the scrap quantity deliberately or by accident
-- anything else?

- Test support for multi keyboard input using keyboard module??s

- We will keep a pool of events in memory in a list or similar, using the payload functionality. Access to the list will be controlled by a lock. The main thread only ever requests a lock, then appends a payload to the list, then returns the lock. The daemon upload thread requests a lock, pops a payload, returns the lock, writes the payload to a local file in eventCache, then tries to ftp it, dweet it, IS it, whatever else it needs to do. This way we ensure we don't double book a resource, and the main thread doesn't have to touch any file writes, only the daemon does, and it doesn't overwrite itself.

In order to implement this, we need to:

-- Create a list of payloads in the output manager. 
-- Create a lock to which the output manager has access.
-- Create a routine in the output manager which grabs a payload from event, requests a lock on the payload list, appends the payload to the list, releases the lock, and then carries on like normal. The only waiting it should do is if the upload daemon is using the payload list (milliseconds). 
-- Create an upload daemon with a few cyclical tasks, and a delay time in between. It wakes up, requests a lock on the payload list, waits til it gets it, checks the size of the list, if the size is non-zero, then it pops the first item (FIFO), returns the lock, and then uses the popped payload to write a file to an event cache, do an ftp upload, dweet, and Initial State, all quietly. Then it goes back to sleep again for a bit before trying again. The average frequency of this should be sufficient to handle all the data coming in. In the case that the ftp fails, then it gracefully skips that and leaves the file in eventCache, and tries again on the next cycle. This way we never miss an ftp upload, but it doesn't matter if dweet or IS fail occasionally. 