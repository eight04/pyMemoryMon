pyMemoryMon
===========
A memory monitor using python and psutil.

Todos
-----
* Logger class
* Color console?
* GUI(threading)?
* Use something like filter.

Logs
----
```log
EVENT_TYPE:PID:PNAME:DETAIL
```

Filter
------
1. include proc which over global cap.
2. include proc create, end event
2. exclude proc which in ignore list.
3. exclude proc which in per-proc cap.

Event Type
----------
* CREATE - process created.
* END - process end.
* MEMORY - memory over cap.
* CPU - cpu over cap.