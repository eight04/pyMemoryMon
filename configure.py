#! python3
from os.path import isfile

class ConfigManager:
	"""Load config for other classes"""

	def __init__(self, path):
		"""set config file path"""
		self.path = path
		self.config = {}
		
		self.load()
		
	def get(self):
		"""return config"""
		return self.config
		
	def load(self):
		"""load config"""
		if not isfile(self.path):
			return
			
		with open(self.path, "r", encoding="utf-8-sig") as f:
			import json
			try:
				self.apply(self.config, json.load(f), True)
			except ValueError as er:
				print("There is an error in your json file!")
				raise er
		
	def save(self):
		with open(self.path, "w", encoding="utf-8") as f:
			import json
			json.dump(self.config, f, indent="\t")
			
	def exist(self):
		return isfile(self.path)
		
	@classmethod
	def apply(cls, dest, src, overwrite=False):
		"""ConfigManager.apply(dict1, dict2, overwrite)
		
		copy dict2 into dict1
		"""
		for key, value in src.items():
			if not overwrite and key in dest:
				continue
			dest[key] = value
		return
