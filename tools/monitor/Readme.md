Monitor
===

## User manual

### Starting

- During active session

    `console_monitor.sh`

- When there is no active session

    `console_monitor.sh <session_number>`

- Providing arguments

    `tools/monitor_file_download.py <session_number> tcp://<gs1>:7001 tcp://<gs2>:7001`

- Session number must be first positional argument
- Additional arguments
    * `-m` - path to mission repository. By default `../../../mission` relative to monitor script.
    * `-p` - control port number. Default `7007`. GSControl's settings have to be changed similarly.
- Closing - `q`, `CTRL+C`, `ESC`

Monitor loads tasklist from local `mission` repository, so it can be started as soon as new tasklist is pulled from `master` branch of GitHub repository by AutoSession running in background.

After starting all download tasks are loaded into left panel and application starts listening to the incoming download frames. When download frame is received, the Correlation ID and file name are matched and number of requested chunks are reduced by that frame. Application automatically deduplicate the same frame received by multiple stations.

The uppercase red `UNBOUND` next to session number indicates that there is another active instance bound to Control Port and current instance is only listener and can't provide missings to main console. The main session operator **must not** use such unbound instance, but additional operators and spectators can use to watching session.


### Using

Monitor can be used both from uplink console and in tasklist mode.

Keyboard shortcuts in tasklist mode:

- `m` - execute again current command only for missing data chunks
- `t` - append to the end of tasklist new commands with all missing chunks from current session. In message printed after adding there is provided step number that has to be entered to jump into newly added tasklist. At the end there is automatically added Beacon Loop step. 

In uplink console:
- `missings()` - get and return new tasklist with missings in current time. The easiest usage is `run(missings())`

Monitor works only during one session then it has to be closed and run again for next session.