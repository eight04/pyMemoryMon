pyMemoryMon
===========
A simple process monitor/logger built with python and psutil.

Screenshot
----------
![Imgur](http://i.imgur.com/VT5ltmt.png)

Dependencies
------------
* [Python 3.4](https://www.python.org/)
* [psutil](https://pypi.python.org/pypi/psutil)
* [colorama](https://pypi.python.org/pypi/colorama)

Install
-------
1. Rename `settings.default.json` to `settings.json`.
2. Add your settings.
3. Run `python pymemorymon.py`

Setting Example
---------------------
```JavaScript
{
	"update_rate": 1,	// Check process state every 1 second.

	// Global settings
	"CREATE": true,	// Monitor creation of process
	"END": true,	// Monitor end of process
	"MEMORY": 10,	// Monitor when memory usage is over 10%
	"CPU": 50,		// Monitor when CPU usage is over 50%. Note that this value
					// could be over 100 if you have multi core cpu.

	"ignore_pids": [0, 4],	// Ignore "System", "System Idle Process" processes.
	"ignore_names": [],

	// Highlight color
	"color": {
		"END": "\u001b[1;37;41m",
		"MEMORY": "\u001b[1;37;44m",
		"CREATE": "\u001b[1;37;43m",
		"CPU": "\u001b[1;37;42m"
	},

	// Settings by process name
	"processes": {
		"firefox.exe": {
			"MEMORY": 20
		},
		"dllhost.exe": {
			"CREATE": false,
			"END": false
		},
		// Support wildcards. It use `fnmatch` to match process name
		"flash_player_*" {	
			"CPU": 100
		}
	}
}

```

Known issues
------------
* `psutil` might be retricted to get process info if the process was created by
  different user.
