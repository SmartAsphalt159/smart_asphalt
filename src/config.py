from configparser import ConfigParser

class config:

	def __init__(self):
		self.config_obj = ConfigParser()

	def create_config(self):

		#networking variables
		self.config_obj["network"] = {
			"recvport" : 1,
			"sendport" : 2,
			"timeout"  : 2
		}

		#lidar variables
		self.config_obj["lidar"] = {
			"channel" : "/dev/ttyUSB0",
			"timeout" : 10
		}

		#encoder variables
		self.config_obj["encoder"] = {
			"channel" : 19,
			"timeout" : 2,
			"sample_wait" : 0.1
		}

		#GPIO variables
		self.config_obj["gpio"] = {
			"motor" : 32,
			"servo" : 33
		}

		#velocity control variables
		self.config_obj["velocity"] = {
			"p-term" : 0.7,
			"i-term" : 0,
			"d-term" : 2,
			"k-term" : 1
		}

		#steering control variables
		self.config_obj["steering"] = {
			"p-term" : 0.5,
			"i-term" : 0,
			"d-term" : 0.3
		}

	#write config to a file
	def write_config(self):
		with open('config.ini', 'w') as conf:
			self.config_obj.write(conf)

	#read config
	def read_config(self):
		self.config_obj.read("config.ini")

	#get a certain parameter
	def get_param(self, param_type, header, term):
		#if statement overloading
		if(param_type == "str"):
			return self.config_obj.get(header, term)
		elif param_type == "int":
			return self.config_obj.getint(header, term)
		elif param_type == "float":
			return self.config_obj.getfloat(header, term)
		else:
			#an error occured
			return -1
