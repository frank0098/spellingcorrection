
import copy
# A structure to represent a state as a {phrase,type}
class phrase_state:
	state_type={"inword":0,"misuse":1,"merging":2,"splitting":3,"null":4}
	state_type_v=["inword","misuse","merging","splitting","null"]
	def __init__(self):
		self.phrase=""
		self.type=0
	def set_state(self,phrase,curtype):
		self.phrase=phrase
		self.type=self.state_type[curtype]
	def get_type(self):
		return self.state_type_v[self.type]

#A structure to represent a state sequence as a {state sequence,score}
class phrase_sequence:
	def __init__(self):
		self.state_sequence=[] #sequence of phrase state
		self.score=0 
	def append(self,elem):
		self.state_sequence.append(elem)
	def get_requence(self):
		seq=copy.deepcopy(self.state_sequence)
		return seq
	def get_result(self):
		res=[]
		corrected_output=""
		for x in self.state_sequence:
			res.append((x.phrase,x.get_type()))
			corrected_output+=x.phrase
			corrected_output+=" "
		print "sequence: ",res," score: ",self.score
		return corrected_output[:-1]
