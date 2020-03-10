# TODO.md

List of changes and improvements that are TODO for bcc system

## TODO

- support scanning to indicate that you're on an hourly card - Maybe implement a job-code recognition function that appends if detected.

- Do we need to ensure that the system clock is up to date? Could we cross-reference with an online time source for safety?

- Support supervisors updating a time for a missed bc card using special time codes. e.g. combo code plus employee code plus time-12h time-30m, so it logs the event time backdatedly. Should this support setting a new date too? Like 2019Y 6M 23D 12h 45m? Or we could just set today by default and provide a date-yesterday code. This way we support limited corrections to bc cards, but people cant magically adjust things from any random day and time.

- Move the stacklight management code to a separate class or to the output manager? Avoid complicating things too much within the station class. ? DD

- Implement an uptime daemon to send an uptime counter to InitialState - allows us to trigger alerts on dead stations etc ? Need to find a simple alerting service...maybe use the builtin cron capabilties?

- Implement a cron job that checks for application heartbeat on the main thread. If the main thread is blocked then it kills the process and restarts it, or reboots (maybe safer). ?

- Build in support for new voice files, noteably:
-- announcing scrap quantities - PARTIALLY implemented
-- tidy up the scrap system in general - make it less hacky and more robust.
-- announcing clearing the scrap quantity deliberately or by accident
-- anything else?

- Support CTO scanning too using job number recognition, and get pacejet to help implement for fileye to auto recognise.

- Test support for multi keyboard input using keyboard module?? Keep for DD version.

- Add prompt to submit with OK if all fields but this are filled. Guard against people forgetting to submit.

- Check that the interaction timer is cleared when the bcc is cleared, and that if there is a very long wait then the interaction timer is cleared for that too.

- Allow dummy to register the times as well? Requires modifying employee recognition code, or making a custom code for dummy.

- .upper() means we can't set case sensitive file paths using ftplocalpath


