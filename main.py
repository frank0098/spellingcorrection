import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from query_correction import query_correction
import sys


query_obj=query_correction("conf.cfg")

#Http server methods
class S(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):
		self._set_headers()
		self.wfile.write("<html><body><h1>"+obj.get_params()+"</h1></body></html>")

	def do_HEAD(self):
		self._set_headers()
		
	def do_POST(self):
		# Doesn't do anything with posted data
		try:

			content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
			raw_query = self.rfile.read(content_length) # <--- Gets the data itself
			raw_query = json.loads(raw_query)
			corrected_query=query_obj.query_api(raw_query['query'],int(raw_query['K']))
			ret={}
			print corrected_query
			ret['corrected_query']=corrected_query
			self._set_headers()
		except:
			self.wfile.write("<html><body>JSON required: {'query':your query, 'K': your top K}</body></html>")
		else:
			self.wfile.write(json.dumps(ret))


#method to fun Http server
def run(server_class=HTTPServer, handler_class=S, port=80):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print 'Starting httpd...'
	httpd.serve_forever()



#Main class
if __name__ == "__main__":
	from sys import argv

	if len(argv) == 2:
		if argv[1]=="train":
			print "###train###"
			query_obj.train()
		else:
			print "please see README for usage"

	elif len(argv) == 3:
		if argv[1]=="server":
			run(port=int(argv[2]))
		elif argv[1]=="test" and argv[2].isdigit():
			print "please enter your input here:"
			while True:
				userinput=sys.stdin.readline().rstrip('\n')
				query_obj.query_api(userinput,int(argv[2]))
				print "\nplease enter your input here:"

		else:
			print "please see README for usage"

	elif len(argv)==4:
		if argv[1]=="test" and argv[3].isdigit():
			query_obj.query_api(argv[2],argv[3])
		else:
			print "please see README for usage"
	else:
		print "please see README for usage"





