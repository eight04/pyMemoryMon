#! python3

""" pyMemoryMon """

from common import ConfigManager, createdir
# from time import sleep
import psutil
import os.path
import time
from fnmatch import fnmatch

def get_process_name(process):
	name = None
	try:
		name = process.name()
	except psutil.AccessDenied:
		name = "(AD)"
	return name
	
def fnmatchSome(name, patterns):
	for pattern in patterns:
		if fnmatch(name, pattern):
			return True
	return False

class Process:
	def __init__(self, process):
		self.process = process
		self.update()
			
	def update(self):
		self.info = self.process.as_dict(attrs=[
			"pid", "name", "cpu_percent", "memory_percent", "cmdline", "exe"
		])
		self.info["name"] = self.info["name"] or self.info["cmdline"] or self.info["exe"]
		
	def bindFilter(self, filterList):
		if self.info["name"] is None:
			return False
		for name, filter in filterList.items():
			if fnmatch(self.info["name"], name):
				self.filter = filter
				return True
		return False
		
	def hash(self):
		return "{}.{}".format(self.info["pid"], self.process.create_time())
		
	def alive(self):
		return self.process.is_running()
		
	def getFiltered(self, memory=10, cpu=50):
		if hasattr(self, "filter"):
			if "MEMORY" in self.filter:
				memory = self.filter["MEMORY"]
			if "CPU" in self.filter:
				cpu = self.filter["CPU"]
		fs = []
		if memory < self.info["memory_percent"]:
			fs.append("MEMORY")
		if cpu < self.info["cpu_percent"]:
			fs.append("CPU")
		return fs
		
	def use_create(self, default=True):
		if not hasattr(self, "filter"):
			return default
		if "CREATE" in self.filter:
			return self.filter["CREATE"]
		return default

	def use_end(self, default=True):
		default = True
		if not hasattr(self, "filter"):
			return default
		if "END" in self.filter:
			return self.filter["END"]
		return default

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
		
		swap = {}
		for hash, process in self.processes.items():
			if process.alive():
				process.update()
				swap[hash] = process
			elif process.use_end(self.conf["END"]):
				log("END", process)
		self.processes = swap
		
		for hash, process in self.processes.items():
			fs = process.getFiltered(memory=self.conf["MEMORY"], cpu=self.conf["CPU"])
			for f in fs:
				log(f, process)
		
		for process in psutil.process_iter():
			process = Process(process)
			
			hash = process.hash()			
			if hash not in self.processes:
				if process.info["pid"] in self.conf["ignore_pids"]:
					continue
				if fnmatchSome(process.info["name"], self.conf["ignore_names"]):
					continue
				process.bindFilter(self.conf["processes"])
				self.processes[hash] = process
				if process.use_create(self.conf["CREATE"]):
					log("CREATE", process)
		
	def event_loop(self):
		while True:
			try:
				self.monitor()
				time.sleep(self.conf["update_rate"])
			except psutil.Error as er:
				print("psutil.Error ->", type(er), er)
			except KeyboardInterrupt as er:
				print("KeyboardInterrupt ->", type(er), er)
				break
			
class Logger:	
	def __init__(self, ctrl, path="logs"):
		self.ctrl = ctrl
		self.path = path
		self.buffer = ""
		self.file = ""
		
		self.load_config()
		createdir(self.path)
		
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
		
	def log(self, type, process):
		tag = time.strftime("%H:%M:%S")
		
		if type in ["CREATE", "END"]:
			s = "[{}] {:6} :: {:>5} :: {}".format(
				tag,
				type,
				process.info["pid"],
				process.info["name"]
			)
		elif type == "MEMORY":
			s = "[{}] {:6} :: {:>5} :: {} :: {:.1f}%".format(
				tag,
				type,
				process.info["pid"],
				process.info["name"],
				process.info["memory_percent"]
			)
		elif type == "CPU":
			s = "[{}] {:6} :: {:>5} :: {} :: {:.1f}%".format(
				tag,
				type,
				process.info["pid"],
				process.info["name"],
				process.info["cpu_percent"]
			)
			
		# Create log
		fname = time.strftime("%Y-%m-%d.log")
		path = os.path.join(self.path, fname)
		
		if self.file and (self.file != path or len(self.buffer) > 1000):
			with open(self.file, "a") as f:
				print(self.buffer, file=f, end="")
			self.file = ""
			self.buffer = ""

		self.file = path
		self.buffer += s + "\n"
		
		print("{}{:78}\033[0;37;40m".format(self.conf["color"][type], s))
		
	def cleanup(self):
		if self.file:
			with open(self.file, "a") as f:
				print(self.buffer, file=f, end="")

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
		self.logger.cleanup()
		
	def view(self):
		self.monitor.event_loop()
	
if __name__ == "__main__":
	import colorama
	colorama.init()
	Main()
