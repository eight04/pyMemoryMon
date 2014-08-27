#! python3

""" pyMemoryMon """

from safeprint import safeprint
from time import sleep
import psutil

"""
Settings:

alarm_percent	show alarm when cpu/memory % increase/decrease over this value.
check_cpu		set to true to monitor cpu.
check_memory	set to true to monitor memory.
pid_ignores		an array of pids. ignore the process if pid matched.
name_ignores	an array of process name. ignore the process if name matched.
update_rate		second(s). time wait between each loop.
"""
alarm_percent = 10
check_cpu = True
check_memory = True
pid_ignores = [0, 4]
name_ignores = []
update_rate = 1
""" Setting End """


class ProcessContainer:
	"""wrap process"""
	def __init__(self, proc):
		self.process = proc
		self.cpu_percent = proc.cpu_percent()
		self.memory_percent = proc.memory_percent()
		try:
			self.name = proc.name()
		except psutil.AccessDenied:
			self.name = "(Access Denied)"

processes = {}
while True:
	for proc in psutil.process_iter():
		pid = proc.pid
		try:
			name = proc.name()
		except psutil.AccessDenied:
			name = "(Access Denied)"
		
		if pid in pid_ignores:
			continue
		
		if name in name_ignores:
			continue
		
		if pid not in processes:
			safeprint("[{:>5}] {} started".format(pid, name))
			processes[pid] = ProcessContainer(proc)
			
		if processes[pid].process != proc:
			safeprint("[{:>5}] {} changed".format(pid, name))
			processes[pid] = ProcessContainer(proc)
	
	del_pids = []
	for pid, proc_con in processes.items():
		if not proc_con.process.is_running():
			safeprint("[{:>5}] {} end".format(pid, proc_con.name))
			del_pids.append(pid)
			continue
			
		if check_cpu:
			cpu_percent = proc_con.process.cpu_percent()

			if cpu_percent - proc_con.cpu_percent > alarm_percent:
				safeprint("[{:>5}] {} cpu usage increased to {}%".format(pid, proc_con.name, cpu_percent))
				proc_con.cpu_percent = cpu_percent
				
			if cpu_percent - proc_con.cpu_percent < -alarm_percent:
				safeprint("[{:>5}] {} cpu usage decreased to {}%".format(pid, proc_con.name, cpu_percent))
				proc_con.cpu_percent = cpu_percent
		
		if check_memory:
			memory_percent = proc_con.process.memory_percent()
				
			if memory_percent - proc_con.memory_percent > alarm_percent:
				safeprint("[{:>5}] {} memory usage increased to {}%".format(pid, proc_con.name, memory_percent))
				proc_con.memory_percent = memory_percent
			
			if memory_percent - proc_con.memory_percent < -alarm_percent:
				safeprint("[{:>5}] {} memory usage decreased to {}%".format(pid, proc_con.name, memory_percent))
				proc_con.memory_percent = memory_percent
				
	for pid in del_pids:
		del processes[pid]
	
	sleep(update_rate)
	