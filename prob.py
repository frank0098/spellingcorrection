
from math import log
import numpy as np
# from sys import 0
import json
from ast import literal_eval as make_tuple
import ConfigParser
import difflib
# The class to calculate bi-gram model and error model
class prob_class:
	
	#constructor
	def __init__(self,conf_path):
		self.bigram_p={}
		self.uni_d={}
		self.single_c={}
		self.double_c_t={}
		self.double_c={}
		self.sub_matrix=[]
		self.add_matrix=[]
		self.del_matrix=[]
		self.load_data(conf_path)


	#load data from local file
	def load_data(self,conf_path):
		config = ConfigParser.RawConfigParser()
		config.read(conf_path)
		self.bigram_p=json.load(file(config.get('query_correction', 'bi_gram_path')))
		self.single_c = json.load(file(config.get('query_correction', 'single_collection_path')))
		self.double_c_t = json.load(file(config.get('query_correction', 'double_collection_path')))
		self.uni_d=json.load(file(config.get('query_correction', 'unigram_path')))
		for key in self.double_c_t:
			self.double_c[make_tuple(key)] = self.double_c_t[key]

		self.sub_matrix = np.loadtxt(config.get('query_correction', 'sub_matrix_path'))
		self.add_matrix = np.loadtxt(config.get('query_correction', 'add_matrix_path'))
		self.del_matrix = np.loadtxt(config.get('query_correction', 'del_matrix_path'))
	#training API
	def train(self):
		self.train_bigram(self.bi_gram_path)

	#bigram model model training logic here
	def train_bigram(self,bi_gram_file_output_path):
		self.bigram_p[("a"+","+"b")]=0.25
		json.dump(self.bigram_p,file(bi_gram_file_output_path,'w'))

	def get_error_prob(self,query,correct_phrase):
		if len(correct_phrase)==len(query):
			return self.substitution(query,correct_phrase)
		elif len(correct_phrase)<len(query):
			return self.addition(query,correct_phrase)
		else:
			return self.deletion(query,correct_phrase)

	def get_lm_prob(self,skip_phrase,prev_phrase,prev_type,cur_phrase,cur_type):
		# print self.bigram_p
		# exit()
		if prev_type==None: #first word in query
			return 0
			if not cur_phrase in self.uni_d:
				return 0
			else: 
				return log(self.uni_d[cur_phrase])
		else:
			if cur_type == "merging" and prev_type=="null" and (not skip_phrase ==None):
				tmp_key=skip_phrase+","+cur_phrase
				if not tmp_key in self.bigram_p:
					return 0
				return log(self.bigram_p[tmp_key])
			elif cur_type =="splitting":
				tem_list = cur_phrase.split(" ")
				tmp_prev=prev_phrase
				res=0
				for x in tem_list:
					tmp_key=tmp_prev+","+x
					if tmp_key in self.bigram_p:
						res+=log(self.bigram_p[tmp_key])
					tmp_prev=x
				return res
			tmp_key=prev_phrase+","+cur_phrase
			# print tmp_key
			if tmp_key in self.bigram_p:
				return log(self.bigram_p[tmp_key])
			return 0


	def substitution(self,wrongword, correctword):
		wrongtemp='a'
		correcttemp='a'
		count = 0
		if not len(wrongword)==len(correctword):
			return 0
		for i,s in enumerate(difflib.ndiff(wrongword, correctword)):
			if s[0] == '-':
				count+=1
				wrongtemp = s[-1]
			if(s[0] == '+'):
				correcttemp = s[-1]
		if not correctword in self.uni_d:
			return 0
		if ord(wrongtemp)-97 >= 0 and ord(wrongtemp)-97<26 and ord(correcttemp)-97 >= 0 and ord(correcttemp)-97<26:
			return float(self.sub_matrix[ord(wrongtemp)-97][ord(correcttemp)-97])/float(self.single_c[correcttemp])*float(self.uni_d[correctword])
		return 0
	def addition(self,wrongword, correctword):
		wrongtemp='a'
		correcttemp='a'
		count = 0
		if not len(wrongword)-1==len(correctword):
			return 0
		for i,s in enumerate(difflib.ndiff(wrongword, correctword)):
			if s[0] == '-':
				count+=1
				wrongtemp = s[-1]
				position = i
			if(s[0] == '+'):
				correcttemp = s[-1]
		if(position == 0 and count == 1):
			if not correctword in self.uni_d:
				return 0
			if ord(wrongtemp)-97 >= 0 and ord(wrongtemp)-97<26:
				return float(self.add_matrix[26][ord(wrongtemp)-97])/float(self.single_c[' '])*float(self.uni_d[correctword])
			return 0
		if(position != 0 and count == 1):
			xchar = correctword[position-1]
			if not correctword in self.uni_d:
				return 0
			if ord(wrongtemp)-97 >= 0 and ord(wrongtemp)-97<26 and ord(xchar)-97 >= 0 and ord(xchar)-97<26:
				return float(self.add_matrix[ord(xchar)-97][ord(wrongtemp)-97])/float(self.single_c[xchar])*float(self.uni_d[correctword])
			return 0
		return 0

	def deletion(self,wrongword, correctword):
		wrongtemp='a'
		correcttemp='a'
		count = 0
		if not len(wrongword)+1==len(correctword):
			return 0
		for i,s in enumerate(difflib.ndiff(wrongword, correctword)):
			if(s[0] == '+'):
				count+=1
				wrongtemp = s[-1]
				position = i
		if(position == 0 and count == 1):
			if not correctword in self.uni_d:
				return 0
			if ord(wrongtemp)-97 >= 0 and ord(wrongtemp)-97<26:
				return float(self.del_matrix[26][ord(wrongtemp)-97])/float(self.double_c[' ',wrongtemp])*float(self.uni_d[correctword])
			return 0
		if(position != 0 and count == 1):
			xchar = correctword[position-1]
			if not correctword in self.uni_d:
				return 0
			if ord(wrongtemp)-97 >= 0 and ord(wrongtemp)-97<26 and ord(xchar)-97 >= 0 and ord(xchar)-97<26:
				return float(self.del_matrix[ord(xchar)-97][ord(wrongtemp)-97])/float(self.double_c[xchar,wrongtemp])*float(self.uni_d[correctword])
			return 0
		return 0

