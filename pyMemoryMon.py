#! python3

""" pyMemoryMon """

from configure import ConfigManager
from time import sleep
import psutil

def get_process_name(process):
	name = None
	try:
		name = process.name()
	except psutil.AccessDenied:
		name = "(AD)"
	return name

class ProcessCached:
	def __init__(self, process):
		self.process = process
		self.pid = process.pid
		self.name = get_process_name(process)

class Monitor:
	def __init__(self, ctrl):
		self.ctrl = ctrl
		self.processes = {}
		
		self.load_config()
		
	def load_config(self):
		cm = self.ctrl.configure
		self.conf = cm.get()
		
		default = {
			"update_rate": 1,
			"CREATE": True,
			"END": True,
			"CPU": 50,
			"MEMORY": 10
		}
		cm.apply(self.conf, default)
		
	def monitor(self):
		log = self.ctrl.logger.log
		procs = self.processes
		
		for proc in psutil.process_iter():
			pid = proc.pid
			name = get_process_name(proc)
			
			if pid not in procs:
				log("CREATE", pid, name)
				procs[pid] = ProcessCached(proc)
				
			if procs[pid].process != proc:
				log("END", pid, procs[pid].name)
				log("CREATE", pid, name)
				procs[pid] = ProcessCached(proc)
		
		del_pids = []
		for pid, proc_con in procs.items():
			if not proc_con.process.is_running():
				log("END", pid, proc_con.name)
				del_pids.append(pid)
				continue
				
			cpu = proc_con.process.cpu_percent()
			memory = proc_con.process.memory_percent()

			log("CPU", pid, proc_con.name, cpu)
			log("MEMORY", pid, proc_con.name, memory)
					
		for pid in del_pids:
			del procs[pid]
		
	def event_loop(self):
		while True:
			try:
				self.monitor()
				sleep(self.conf["update_rate"])
			except psutil.Error as er:
				print(er)
			except KeyboardInterrupt as er:
				print(er)
				break
			
			
class Logger:	
	def __init__(self, ctrl):
		self.ctrl = ctrl
		
		self.load_config()
		
	def load_config(self):
		configure = self.ctrl.configure
		self.conf = configure.get()		
		default = {
			"ignore_pids": [0, 4],
			"ignore_names": [],
			"processes": {},
			"color": {
				"CREATE": "\033[1;37;43m",
				"END": "\033[1;37;41m",
				"CPU": "\033[1;37;42m",
				"MEMORY": "\033[1;37;44m"
			}
		}
		configure.apply(self.conf, default)
		
	def log(self, type, pid, name, o=None):
		if self.filter(type, pid, name, o):
			return
			
		from datetime import datetime
		time = datetime.now()
		tag = time.strftime("%H:%M:%S")
		if o:
			s = "[{}] {:6} :: {:>5} :: {} :: {:.1f}%".format(tag, type, pid, name, o)
		else:
			s = "[{}] {:6} :: {:>5} :: {}".format(tag, type, pid, name)
		
		fname = time.strftime("%Y-%m-%d.log")
		with open(fname, "a") as f:
			print(s, file=f)
			
		print("{}{:78}".format(self.conf["color"][type], s))

	def get_use(self, type, pid, name):
		use = self.conf[type]
		
		if name in self.conf["processes"] and type in self.conf["processes"][name]:
			use = self.conf["processes"][name][type]
			
		if pid in self.conf["processes"] and type in self.conf["processes"][pid]:
			use = self.conf["processes"][pid][type]
		
		return use

	def filter(self, type, pid, name, value):
		use_create = self.conf["CREATE"]
		use_end = self.conf["END"]
		use_cpu = self.conf["CPU"]
		use_memory = self.conf["MEMORY"]
		
		if pid in self.conf["ignore_pids"]:
			return True
			
		if name in self.conf["ignore_names"]:
			return True
		
		use = self.get_use(type, pid, name)
		if not use:
			return True
				
		if type in ["CPU", "MEMORY"] and value < use:
			return True
			
		return False

class Main:
	def __init__(self):
		self.load_class()
		self.view()
		self.unload_class()
		
	def load_class(self):
		self.configure = ConfigManager("settings.json")
		self.logger = Logger(self)
		self.monitor = Monitor(self)
	
	def unload_class(self):
		pass
		
	def view(self):
		self.monitor.event_loop()
	
if __name__ == "__main__":
	import colorama
	colorama.init()
	Main()
