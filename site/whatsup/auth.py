from whatsup.password import pwd_context
from whatsup.db import session

import whatsup.core

LOGIN_USERNAME = "login_username"

# User authentication handlers:
class LogoutHandler(whatsup.core.BaseHandler):
	def get(self):
		self.clear_cookie("LOGIN_USERNAME")
		self.redirect("/")

class LoginHandler(whatsup.core.BaseHandler):
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

class RegisterHandler(whatsup.core.BaseHandler):
	def post(self):
		username = self.get_argument("username")
		# insert user info into database, if user does not already exist
		rows = session.execute("SELECT * FROM users where user='%s'" % username)

		if not rows:
			# insert user/pass into database
			salt = os.urandom(16).encode('base_64').rstrip('=\n')
			hash = pwd_context.encrypt(salt + self.get_argument("password"))

			session.execute("INSERT INTO users (user, salt, pswd) VALUES ('%s', '%s', '%s');" % (username, salt, hash))
		else:
			# set some variable to show username taken
			print "Username taken"

		self.redirect("/")