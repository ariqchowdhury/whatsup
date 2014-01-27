import tornado.web
from tornado import gen

from os import urandom

from whatsup.db import session
from whatsup.db import is_user_in_db
from whatsup.db import insert_user_into_db

from whatsup.task_queue import get_hashed_pswd
from whatsup.task_queue import DecodeGetHashedPswd

from whatsup.task_queue import verify_password
from whatsup.task_queue import DoesUserExist
from whatsup.task_queue import AddUser
from whatsup.task_queue import EncryptPassword

import whatsup.core
from whatsup.cookies import Cookies


decode = DecodeGetHashedPswd

# User authentication handlers:
class LogoutHandler(whatsup.core.BaseHandler):
	def get(self):
		self.clear_cookie(Cookies.LoginUsername)
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
				self.set_secure_cookie(Cookies.LoginUsername, username)
			else:
				print "incorrect password"
		else:
			print "user doesn't exist"
			
		self.redirect("/")
		# if not, do account signup

class RegisterHandler(whatsup.core.BaseHandler):
	@tornado.web.asynchronous
	@gen.coroutine
	def post(self):
		username = self.get_argument("username")

		# Check if user already exists in database
		response = yield gen.Task(DoesUserExist.apply_async, args=[username])

		rows = response.result
		# If not, insert into database, else report username taken
		if not rows:
			# insert user/pass into database
			email = self.get_argument("email")
			salt = urandom(16).encode('base_64').rstrip('=\n')
			# hash = pwd_context.encrypt(salt + self.get_argument("password"))

			hash = yield gen.Task(EncryptPassword.apply_async, args=[salt+self.get_argument("password")])
			
			yield gen.Task(AddUser.apply_async, args=[username, salt, hash.result, email])
			self.set_secure_cookie(Cookies.LoginUsername, username)
		else:
			# set some variable to show username taken
			print "Username taken"

		self.redirect("/")