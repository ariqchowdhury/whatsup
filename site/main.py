import tornado.web
import tornado.ioloop
import tornado.websocket

import os.path

# Server settings
MAIN_PORT = 8888

class HomeHandler(tornado.web.RequestHandler):
	""" Handler for the homepage.
	Extends a Tornado RequestHandler.
	"""

	def get(self):
		self.render("home.html")

class ChannelHandler(tornado.web.RequestHandler):
	""" Renders the html page when a user enters a channel.
		Creates a WebSocket connection on entry.
	"""

	def get(self, channel_id):
		self.render("channel.html", channel_id=channel_id)

class ChannelWebSocketHandler(tornado.websocket.WebSocketHandler):
	""" Handler for a channel room.
	Extends a WebSocketHandler. 
	"""
	def open(self):
		print "Connection Opened"
		self.write_message("New Connection Opened")

	def on_message(self, message):
		self.write_message("Message Received %s" % message)

	def on_close(self):
		print "Connection Closed"

# Handlers and settings passed to web application
handlers = [
	(r"/", HomeHandler),
	(r"/ch/([0-9]+)", ChannelHandler),
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