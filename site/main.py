import os.path
from os import system

import tornado.web
import tornado.ioloop

import whatsup.core
import whatsup.auth
import whatsup.channel

# Server settings
MAIN_PORT = 8888

# Handlers and settings passed to web application
handlers = [
	(r"/", whatsup.core.HomeHandler),
	(r"/ch/?", whatsup.core.HomeHandler), # TODO: This should be handled with a page asking user which channel they meant to go to
	(r"/ch/([A-Za-z0-9\_]+/*)", whatsup.channel.ChannelHandler),
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
	#TODO: In production, this should start a cronjob that runs gen_frontpage periodically
	system("python whatsup/gen_frontpage.py")

	application.listen(MAIN_PORT)
	tornado.ioloop.IOLoop.instance().start()