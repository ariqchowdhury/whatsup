import tornado.web
import tornado.ioloop
import tornado.websocket

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster 
from cassandra.query import SimpleStatement 

import os.path
import atexit

# Server settings
MAIN_PORT = 8888
# Cassandra settings
KEYSPACE = "whatsup_dev"
CASS_IP = '127.0.0.1'

cluster = Cluster([CASS_IP])
session = cluster.connect()
session.set_keyspace(KEYSPACE)

try:
	rows = session.execute("SELECT * FROM users")
except:
	print "Cassandra connect failed"

print rows[0]

def exit_handler():
	session.shutdown()

atexit.register(exit_handler)


# Quick crappy message buffer for development TODO: Make robust buffer for production use
# Quick crappy client list TODO: Robustify it

clients = []

class HomeHandler(tornado.web.RequestHandler):
	""" Handler for the homepage.
	Extends a Tornado RequestHandler.
	"""

	@tornado.web.addslash
	def get(self):
		self.render("home.html")

class ChannelHandler(tornado.web.RequestHandler):
	""" Renders the html page when a user enters a channel.
		Creates a WebSocket connection on entry.
	"""

	@tornado.web.removeslash
	def get(self, channel_id):
		self.render("channel.html", channel_id=channel_id)

class ChannelWebSocketHandler(tornado.websocket.WebSocketHandler):
	""" Handler for a channel room.
	Extends a WebSocketHandler. 
	"""
	def open(self):
		print "Connection Opened"
		self.write_message({'sender': "server", 'msg': "New Connection Opened"})
		clients.append(self)

	def on_message(self, message):
		# TODO: write message to buffer

		for client in clients:
			client.write_message({'msg': "%s" % message})

	def on_close(self):
		print "Connection Closed"
		clients.remove(self)


# User authentication handlers:

# Handlers and settings passed to web application
handlers = [
	(r"/", HomeHandler),
	(r"/ch/?", HomeHandler), # TODO: This should be handled with a page asking user which channel they meant to go to
	(r"/ch/([0-9]+/*)", ChannelHandler),
	(r"/ws", ChannelWebSocketHandler),
]

settings = {
	"debug": True,
	"static_path":os.path.join(os.path.dirname(__file__), "../"),
}

application = tornado.web.Application(handlers, **settings)

if __name__ == "__main__": 
	application.listen(MAIN_PORT)
	tornado.ioloop.IOLoop.instance().start()