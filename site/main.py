import tornado.web
import tornado.ioloop
import tornado.websocket

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster 
from cassandra.query import SimpleStatement 

from passlib.context import CryptContext

import os.path
import atexit
import uuid

# Server settings
MAIN_PORT = 8888
# Cassandra settings
KEYSPACE = "whatsup_dev"
CASS_IP = '127.0.0.1'
# Cookie Consts
LOGIN_USERNAME = "login_username"

cluster = Cluster([CASS_IP])
session = cluster.connect()
session.set_keyspace(KEYSPACE)

pwd_context = CryptContext (
	schemes=["pbkdf2_sha256"],
	default="pbkdf2_sha256",
	pbkdf2_sha256__default_rounds = 24000,
)

try:
	rows = session.execute("SELECT * FROM users")
except:
	print "Cassandra connect failed"


def exit_handler():
	session.shutdown()

atexit.register(exit_handler)


# Quick crappy message buffer for development TODO: Make robust buffer for production use
# Quick crappy client list TODO: Robustify it

clients = []

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("LOGIN_USERNAME")

class HomeHandler(BaseHandler):
	""" Handler for the homepage.
	Extends a Tornado RequestHandler.
	"""

	@tornado.web.addslash
	def get(self):

		# populate list of featured events
		rows = session.execute("SELECT title, tag, start FROM channels WHERE dmy='2014-01-17' ORDER BY start");
		featured_list = rows

		all_list = rows[:10]

		# populate list of next 10 events

		# generate urls for the events as well


		if self.current_user:
			self.render("home.html", current_user=self.current_user, logged_in=True)
		else:
			self.render("home.html", current_user="", logged_in=False)	

class ChannelHandler(BaseHandler):
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
class LogoutHandler(BaseHandler):
	def get(self):
		self.clear_cookie("LOGIN_USERNAME")
		self.redirect("/")

class LoginHandler(BaseHandler):
	def post(self):
		username = self.get_argument("username")
		#TODO: if the user exists in database and password matches
		rows = session.execute("SELECT salt, pswd FROM users where user='%s'" % username)

		# username = username+salt;
		# hash(username)

		if rows:
			if pwd_context.verify(rows[0].salt+self.get_argument("password"), rows[0].pswd):
				self.set_secure_cookie("LOGIN_USERNAME", username)
			else:
				print "incorrect password"
		else:
			print "user doesn't exist"
			
		
		
		self.redirect("/")
		# if not, do account signup

class RegisterHandler(BaseHandler):
	def post(self):
		username = self.get_argument("username")
		# insert user info into database, if user does not already exist
		rows = session.execute("SELECT * FROM users where user='%s'" % username)

		if not rows:
			# insert user/pass into database
			salt = os.urandom(16).encode('base_64').replace("=", "").replace("\n", "")
			hash = pwd_context.encrypt(salt + self.get_argument("password"))

			session.execute("INSERT INTO users (user, salt, pswd) VALUES ('%s', '%s', '%s');" % (username, salt, hash))
		else:
			# set some variable to show username taken
			print "Username taken"

		self.redirect("/")

# Create channels:
class CreateChannelHandler(BaseHandler):
	def post(self):
		title = self.get_argument("title")
		tag = self.get_argument("tag")
		length = self.get_argument("length")
		dmy = self.get_argument("start_date")
		hour = self.get_argument("hour")
		user = self.current_user
		ch_id = uuid.uuid4()
		url = ch_id.bytes.encode('base_64').rstrip('=\n').replace('/', '_').replace('+', "AC")
		
		#timestamp will just use cassandra getdate(now())
		# Need to insert into all channel column families, see: db_sechma for columns

		session.execute("""
			INSERT INTO channels (id, dmy, start, ts, len, user, title, tag, url)
			VALUES (%s, '%s', '%s', dateof(now()), %s, '%s', '%s', '%s', '%s');
			""" % (ch_id, dmy, dmy+" "+hour, length, user, title, tag, url))

		session.execute("""
			INSERT INTO channels_by_id (id, dmy, start, ts, len, user, title, tag, url)
			VALUES (%s, '%s', '%s', dateof(now()), %s, '%s', '%s', '%s', '%s');
			""" % (ch_id, dmy, dmy+" "+hour, length, user, title, tag, url))

		session.execute("INSERT INTO user_channel_index (user, ch_id) VALUES ('%s', %s);" % (user, ch_id))

		self.redirect("/")

# Handlers and settings passed to web application
handlers = [
	(r"/", HomeHandler),
	(r"/ch/?", HomeHandler), # TODO: This should be handled with a page asking user which channel they meant to go to
	(r"/ch/([0-9]+/*)", ChannelHandler),
	(r"/ws", ChannelWebSocketHandler),
	(r"/CreateChannel", CreateChannelHandler),
	(r"/login", LoginHandler),
	(r"/register", RegisterHandler),
	(r"/logout", LogoutHandler),
]

settings = {
	"debug": True,
	"static_path":os.path.join(os.path.dirname(__file__), "../"),
	"cookie_secret": "Thisabovealltothineownselfbetrue",
	"xsrf_cookies": True,
}

application = tornado.web.Application(handlers, **settings)

if __name__ == "__main__": 
	application.listen(MAIN_PORT)
	tornado.ioloop.IOLoop.instance().start()