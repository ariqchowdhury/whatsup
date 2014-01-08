import tornado.web
import tornado.ioloop
import tornado.websocket

# Server settings
MAIN_PORT = 8888

class HomeHandler(tornado.web.RequestHandler):
	""" Handler for the homepage.
	Extends a Tornado RequestHandler.
	"""

	def get(self):
		self.render("home.html")

class ChannelHandler(tornado.websocket.WebSocketHandler):
	""" Handler for a channel room.
	Extends a WebSocketHandler. 
	"""
	def open(self):

	def on_message(self):

	def on_close(self):

# Handlers and settings passed to web application

handlers = [
	(r"/", HomeHandler),
	(r"/ch/([0-9]+)", ChannelHandler),
]

settings = {
	"debug": True,
}

application = tornado.web.Application(handlers, **settings)

if __name__ == "__main__": 
	application.listen(MAIN_PORT)
	tornado.ioloop.IOLoop.instance().start()