from phrase import phrase_state
from phrase import phrase_sequence
from lexicon import lexicon_dict
from score import scoring
import json
import heapq
import ConfigParser
from ast import literal_eval as make_tuple

# The main major class for providing user training and testing interface
class query_correction:

	def __init__(self,conf_path):
		self.lexicon_obj=lexicon_dict(conf_path)
		self.score_obj=scoring(self.lexicon_obj,conf_path)
		self.Z_array=[{}]
		self.conf_path=conf_path

	#API for client to see the current parameters value 
	def get_params(self):
		return self.score_obj.get_params()

	#TODO
	def get_error_type(self,wrong_word,correct_word):
		query_word_in_dictionary = (wrong_word in self.lexicon_obj.get_dict())
		if ' ' in correct_word:
			return "splitting"
		if not query_word_in_dictionary:
			return "inword"
		return "misuse"
	#Main method for user to perform the training and write the output parameters to a specific file for later use
	#Algorithm1 in the paper
	def train(self):
		config = ConfigParser.RawConfigParser()
		config.read(self.conf_path)
		inputpath=config.get('query_correction', 'training_set_path')
		training_set=[]
		with open(inputpath) as f:
			for line in f:
				training_set.append(make_tuple(line))
		lbda=10
		mu1=1000
		mu2=1000
		mu3=1000
		for entry in training_set:
			wrong_elem=entry[0]
			correct_elem=entry[1]
			wrong_list=wrong_elem.split(" ")
			for x in range(1,len(wrong_list)):
				corrected_output = self.api_for_training(wrong_list[:x])
				correct_flag=True
				if len(corrected_output)==len(correct_elem):
					for idx in range(0,len(corrected_output)):
						if not corrected_output[idx]==correct_elem[idx]:
							correct_flag=False
							break
				else:
					correct_flag=False

				if not correct_flag: #query generation does not equal to training datapoint
					for idx in range(0,min(len(corrected_output),len(correct_elem),len(wrong_list))):
						current_query=wrong_list[idx]
						corrected_query=corrected_output[idx]
						corrected_query_type=self.get_error_type(current_query,corrected_query)
						correct_word=correct_elem[idx]
						correct_type=self.get_error_type(current_query,correct_word)
						corrected_prev_word=None
						corrected_prev_type=None
						correct_prev_word=None
						correct_prev_type=None
						corrected_skip_word=None
						correct_skip_word=None

						if idx>=1:
							corrected_prev_word=corrected_output[idx-1]
							corrected_prev_type=self.get_error_type(wrong_list[idx-1],corrected_prev_word)
							correct_prev_word=correct_elem[idx-1]
							correct_type=self.get_error_type(wrong_list[idx-1],correct_prev_word)
						if idx>=2:
							corrected_skip_word=corrected_output[idx-2]
							correct_skip_word=correct_elem[idx-2]
						lbda+=self.score_obj.phi_func(correct_skip_word,correct_prev_word,correct_prev_type,correct_word,correct_type)-\
						self.score_obj.phi_func(corrected_skip_word,corrected_prev_word,corrected_prev_type,corrected_query,corrected_query_type)
						mu1+=self.score_obj.f1_func(correct_word,correct_type,current_query)-self.score_obj.f1_func(corrected_query,corrected_query_type,current_query)
						mu2+=self.score_obj.f2_func(correct_word,correct_type,current_query)-self.score_obj.f2_func(corrected_query,corrected_query_type,current_query)
						mu3+=self.score_obj.f3_func(correct_word,correct_type,current_query)-self.score_obj.f3_func(corrected_query,corrected_query_type,current_query)
			lbda/=len(wrong_list)
			mu1/=len(wrong_list)
			mu2/=len(wrong_list)
			mu3/=len(wrong_list)
		lbda/=len(training_set)
		mu1/=len(training_set)
		mu2/=len(training_set)
		mu3/=len(training_set)
		output={}
		output["_lbda"]=lbda
		output["_mu1"]=mu1
		output["_mu2"]=mu2
		output["_mu3"]=mu3
		self.score_obj.write_params(self.conf_path,output)
		return output
		# assume input is lower letter words
	def minDistance(self, word1, word2):
		m=len(word1)+1; n=len(word2)+1
		dp = [[0 for i in range(n)] for j in range(m)]
		for i in range(n):
			dp[0][i]=i
		for i in range(m):
			dp[i][0]=i
		for i in range(1,m):
			for j in range(1,n):
				dp[i][j]=min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+(0 if word1[i-1]==word2[j-1] else 1))
		return dp[m-1][n-1]

	# word1 is query, word2 is generated state
	def within_edit_distance(self,word1,word2,param,query_word_in_dictionary):
		word1=word1.lower()
		word2=word2.lower()
		wordlength_diff=len(word1)-len(word2)
		if(wordlength_diff>param or wordlength_diff<-param): 
			return None
		if self.minDistance(word1,word2)>param:
			return None
		if ' ' in word2:
			return "splitting"
		if not query_word_in_dictionary:
			return "inword"
		return "misuse"

	# method to generate all possible candidates  
	def generate_candidates(self,query_word):
		output=[]
		x=0
		param=2
		query_word_in_dictionary = (query_word in self.lexicon_obj.get_dict())
		if query_word_in_dictionary:
			new_state = phrase_state()
			new_state.set_state(query_word,"inword")
			output.append(new_state)
			return output

		for word in self.lexicon_obj.get_dict():

			res=self.within_edit_distance(query_word,word,param,query_word_in_dictionary)
			if not res==None:
				new_state = phrase_state()
				new_state.set_state(word,res)
				output.append(new_state)
		return output

	# The utitlity method for training process
	def api_for_training(self,query_array):
		return self.generate_correction(query_array,1)
	# The API the http server will call to perform the algorithm
	def query_api(self,query,K):
		query_word_array=query.split()
		return self.generate_correction(query_word_array,K)
	#The utility method to get the top K elemnt in the list
	def get_top_K(self,K,curlist):
		if len(curlist)==0:
			return []
		score_list=[]
		for x in curlist:
			score_list.append(x.score)
		heap=score_list[:K]
		heapq.heapify(heap)
		for x in score_list[K:]:
			if x > heap[0]:
				heapq.heapreplace(heap,x)
		res=[]
		for x in range(0,len(curlist)):
			if curlist[x].score>=heap[0]:
				res.append(curlist[x])
		return res[:K]

	# Algorithm 2 in the paper
	def generate_correction(self,query_array,K):
		self.Z_array=[{}]
		i=0
		for word in query_array:
			i+=1
			print "ITERATION",i
			self.Z_array.append({})
			candidate_states=self.generate_candidates(word)
			for candidatestate in candidate_states:
				if len(self.Z_array[i-1])==0:
					a=phrase_sequence()
					a.state_sequence=[]
					a.append(candidatestate)
					a.score=self.score_obj.calculate_score(0,None,None,candidatestate.phrase,None,candidatestate.get_type(),None,word)
					if not candidatestate in self.Z_array[i]:
						self.Z_array[i][candidatestate]=[]
					self.Z_array[i][candidatestate].append(a)
				else:
					for key in self.Z_array[i-1]:
						for z in self.Z_array[i-1][key]:
							a=phrase_sequence()
							a.state_sequence=z.get_requence()
							prev_phrase=a.state_sequence[-1].phrase
							prev_type=a.state_sequence[-1].get_type()
							prev_score=z.score
							a.state_sequence.append(candidatestate)
							if len(a.state_sequence)==1:
								a.score=self.score_obj.calculate_score(prev_score,None,prev_phrase,candidatestate.phrase,prev_type,candidatestate.get_type(),query_array[i-2],word)
							else:
								skip_phrase=a.state_sequence[-2].phrase
								a.score=self.score_obj.calculate_score(prev_score,skip_phrase,prev_phrase,candidatestate.phrase,prev_type,candidatestate.get_type(),query_array[i-2],word)
							if not candidatestate in self.Z_array[i]:
								self.Z_array[i][candidatestate]=[]
							self.Z_array[i][candidatestate].append(a)
						# nullstate=phrase_state()
						# nullstate.set_state("***","null")
						# a=phrase_sequence()
						# a.state_sequence=z.get_requence()
						# prev_score=z.score
						# a.state_sequence.append(nullstate)
						# a.score=prev_score
						# self.Z_array[i][candidatestate].append(a)

				# if (not candidatestate.get_type() == "null") and i<len(query_array)-1:#this is slow
				# if (not candidatestate.get_type() == "null"):#this is slow
				# 	self.Z_array[i][candidatestate] = self.get_top_K(K,self.Z_array[i][candidatestate])

		#Zn=self.Z_array[len(query_array)]
		res=[]
		# for x in self.Z_array[len(query_array)]:
		# 	print x
			#self.Z_array[len(query_array)][x].print_result()
		for state in self.Z_array[len(query_array)]:
			for seq in self.Z_array[len(query_array)][state]:
				new_sequence=phrase_sequence()
				new_sequence.state_sequence=seq.state_sequence
				new_sequence.score=seq.score
				res.append(new_sequence)
		res=self.get_top_K(K,res)
		output=[]
		for x in res:
			# x.print_result()
			output.append(x.get_result())
		print output
		return output
