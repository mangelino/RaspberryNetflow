import BaseHTTPServer
import socket

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		print self.path
		self.send_response(200)
		self.end_headers()
		addr = self.path[1:]
		try:
			resp = ".".join(socket.gethostbyaddr(addr)[0].split(".")[-2:])
		except:
			resp="Unknown"
		self.wfile.write('{ "domain": "'+resp+'" }')
		


server_address = ('', 8000)
httpd = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
httpd.serve_forever()
