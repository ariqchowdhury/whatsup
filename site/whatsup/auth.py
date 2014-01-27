import tornado.web
from tornado import gen

from whatsup.db import session
from whatsup.db import is_user_in_db
from whatsup.db import insert_user_into_db

from whatsup.task_queue import get_hashed_pswd
from whatsup.task_queue import DecodeGetHashedPswd

from whatsup.task_queue import verify_password

import whatsup.core

LOGIN_USERNAME = "login_username"

decode = DecodeGetHashedPswd

# User authentication handlers:
class LogoutHandler(whatsup.core.BaseHandler):
	def get(self):
		self.clear_cookie("LOGIN_USERNAME")
		self.redirect("/")

class LoginHandler(whatsup.core.BaseHandler):
	
	@tornado.web.asynchronous
	@gen.coroutine
	def post(self):
		username = self.get_argument("username")

		response = yield gen.Task(get_hashed_pswd.apply_async, args=[username])

		rows = response.result

		if rows:
			verified = yield gen.Task(verify_password.apply_async, args=[rows[0][decode.salt]+self.get_argument("password"), rows[0][decode.pswd]])
			if verified.result == True:
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

		# Check if user already exists in database
		rows = is_user_in_db(username)

		# If not, insert into database, else report username taken
		if not rows:
			# insert user/pass into database
			salt = os.urandom(16).encode('base_64').rstrip('=\n')
			hash = pwd_context.encrypt(salt + self.get_argument("password"))

			insert_user_into_db(username, salt, hash)
		else:
			# set some variable to show username taken
			print "Username taken"

		self.redirect("/")