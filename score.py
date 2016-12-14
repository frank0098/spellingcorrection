
from math import log
import json
from prob import prob_class
import ConfigParser
global_path="/Users/Frank/Desktop/tmp/"

# The class to calculate score for a given state sequence
class scoring:

	params_path=global_path+"training_params.txt"
	def __init__(self,lexicon,conf_path):
		self._lbda=10
		self._mu1=1000
		self._mu2=1000
		self._mu3=1000
		self.prob_obj=prob_class(conf_path)
		self.lexicon_obj=lexicon
		config = ConfigParser.RawConfigParser()
		config.read(conf_path)
		inputpath=config.get('query_correction', 'params_path')
		params=json.load(file(inputpath))
		self._lbda1=params["_lbda"]
		self._mu1=params["_mu1"]
		self._mu2=params["_mu2"]
		self._mu3=params["_mu3"]

	#utility function for writing parameters to local file
	def write_params(self,conf_path,output):
		config = ConfigParser.RawConfigParser()
		config.read(conf_path)
		outputpath=config.get('query_correction', 'train_output')
		print "writing result..."
		json.dump(output,file(outputpath,'w'))

	#utility function to retrieve current params as a string
	def get_params(self):
		return "lbda: "+str(self._lbda)+"mu1: "+str(self._mu1)+"mu2: "+str(self._mu2)+"mu3: "+str(self._mu3)

	def phi_func(self,skip_word,prev_word,prev_type,cur_word,cur_type):
		return self.prob_obj.get_lm_prob(skip_word,prev_word,prev_type,cur_word,cur_type)
	def f1_func(self,cur_state,cur_type,cur_query):
		if cur_type=="inword" and (not cur_query in self.lexicon_obj.get_dict()):
			res=self.prob_obj.get_error_prob(cur_query,cur_state)
			# print res
			if res==0:
				return -1000000
			return log(res)
		else:
			return 0
	def f2_func(self,cur_state,cur_type,cur_query):
		if cur_type=="splitting" and cur_query in self.lexicon_obj.get_dict():
			res=self.prob_obj.get_error_prob(cur_query,cur_state)
			# print res
			if res==0:
				return -1000000
			return log(res)
		else:
			return 0
	def f3_func(self,cur_state,cur_type,cur_query):
		if cur_type=="misuse" and cur_query in self.lexicon_obj.get_dict():
			res=self.prob_obj.get_error_prob(cur_query,cur_state)
			# print res
			if res==0:
				return -1000000
			return log(res)
		else:
			return 0		

	def calculate_score(self,prev_score,skip_state,prev_state,cur_state,prev_type,cur_type,prev_query,cur_query):
		# print cur_state,cur_type,cur_query
		res=prev_score+self._lbda*self.phi_func(skip_state,prev_state,prev_type,cur_state,cur_type)+\
		self._mu1*self.f1_func(cur_state,cur_type,cur_query)+\
		self._mu2*self.f2_func(cur_state,cur_type,cur_query)+\
		self._mu3*self.f3_func(cur_state,cur_type,cur_query)
		#FOR DEBUG
		# if cur_state=="love" and cur_query=="love":
		# print self._lbda*self.phi_func(skip_state,prev_state,prev_type,cur_state,cur_type)
		# print self._mu1*self.f1_func(cur_state,cur_type,cur_query)
		# print self._mu2*self.f2_func(cur_state,cur_type,cur_query)
		# print self._mu3*self.f3_func(cur_state,cur_type,cur_query)
		return res

