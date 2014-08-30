pyMemoryMon
===========
A memory monitor using python and psutil.

Screenshot
----------
![Imgur](http://i.imgur.com/VT5ltmt.png)

Installation
------------
Install following dependencies first.

* [Python 3.4](https://www.python.org/)
* [psutil](https://pypi.python.org/pypi/psutil)
* [colorama](https://pypi.python.org/pypi/colorama)

Then download the entire folder, run
```Shell
python pymemorymon.py
```

Event Types
-----------
There are 4 types of event.

* CREATE - process created.
* END - process end.
* MEMORY - high memory usage.
* CPU - high cpu usage.

settings.json
-------------
*update_rate*
Seconds to wait for each loop.

*CREATE*
True or false. Whether to log CREATE event.

*END*
True or false. Whether to log END event.

*MEMORY*
Bool or number. Logs when memory using percentage over this value.

*CPU*
Bool or number. Note that if you have multiple cpu, it could be over 100.

*ignore_pids*
Array of PIDs to ignore.

*ignore_names*
Array of process name to ignore. Like "firefox.exe".

*color*
Define the text color for each type of event in the terminal.

*processes*
A dict to define per process setting. Key could be PID or process name.

settings.json Example
---------------------
```JavaScript
{
	"update_rate": 1,

	"CREATE": true,
	"END": true,
	"MEMORY": 10,
	"CPU": 50,

	"ignore_pids": [0, 4],
	"ignore_names": [],

	"color": {
		"END": "\u001b[1;37;41m",
		"MEMORY": "\u001b[1;37;44m",
		"CREATE": "\u001b[1;37;43m",
		"CPU": "\u001b[1;37;42m"
	},

	"processes": {
		"firefox.exe": {
			"MEMORY": 20
		},
		"dllhost.exe": {
			"CREATE": false,
			"END": false
		}
	}
}

```

Todos
-----
* Logger class. OK
* Color console? OK
* GUI(threading)?
* Use something like filter. OK
* Need a better algorithm of CPU event.
