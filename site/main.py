import tornado.web
import tornado.ioloop

from whatsup.db import session
import whatsup.core
import whatsup.auth
import whatsup.channel

import os.path
import atexit

# Server settings
MAIN_PORT = 8888

try:
	rows = session.execute("SELECT * FROM users")
except:
	print "Cassandra connect failed"


def exit_handler():
	session.shutdown()

atexit.register(exit_handler)

# Handlers and settings passed to web application
handlers = [
	(r"/", whatsup.core.HomeHandler),
	(r"/ch/?", whatsup.core.HomeHandler), # TODO: This should be handled with a page asking user which channel they meant to go to
	(r"/ch/([A-Za-z0-9\_]+/*)", whatsup.channel.ChannelHandler),
	(r"/ws", whatsup.channel.ChannelWebSocketHandler),
	(r"/CreateChannel", whatsup.channel.CreateChannelHandler),
	(r"/login", whatsup.auth.LoginHandler),
	(r"/register", whatsup.auth.RegisterHandler),
	(r"/logout", whatsup.auth.LogoutHandler),
]

settings = {
	"debug": True,
	"static_path":os.path.join(os.path.dirname(__file__), "../"),
	"cookie_secret": "Thisabovealltothineownselfbetrue",
	"xsrf_cookies": True,
	"gzip": True,
}

application = tornado.web.Application(handlers, **settings)

if __name__ == "__main__": 
	application.listen(MAIN_PORT)
	tornado.ioloop.IOLoop.instance().start()