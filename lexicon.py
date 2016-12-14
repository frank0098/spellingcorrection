# The class to generate reliable candidate
import ConfigParser
class lexicon_dict:
	def __init__(self,conf_path):
		self.dictionary=[]
		config = ConfigParser.RawConfigParser()
		config.read(conf_path)
		dict_path=config.get('query_correction', 'lexicon')
		with open(dict_path) as f:
			for line in f:
				line = line[:-1]
				self.dictionary.append(line)
	def get_dict(self):
		return self.dictionary