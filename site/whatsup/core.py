import tornado.web
from tornado import gen

from whatsup.db import session
from whatsup.db import read_events_for_frontpage

from whatsup.task_queue import generate_frontpage
from whatsup.task_queue import DecodeGenerateFrontpage

import tcelery

tcelery.setup_nonblocking_producer()

PATH_TO_SITE = "../"
HOMEPAGE = "home.html"

HOME_NUM_EVENTS_TO_DISPLAY = 10

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("LOGIN_USERNAME")

class HomeHandler(BaseHandler):
	""" Handler for the homepage.
	Extends a Tornado RequestHandler.
	"""

	@tornado.web.addslash
	@tornado.web.asynchronous
	@gen.coroutine
	def get(self):
		# rows = read_events_for_frontpage('2014-01-17')	
		response = yield gen.Task(generate_frontpage.apply_async, args=['2014-01-17'])

		# featured_list = rows
		# all_list = rows[:HOME_NUM_EVENTS_TO_DISPLAY]

		featured_list = response.result
		all_list = response.result[:HOME_NUM_EVENTS_TO_DISPLAY]

		# featured_list = rows[0]
		# all_list = rows[1]

		if self.current_user:
			self.render(PATH_TO_SITE + HOMEPAGE, logged_in=True, flist=featured_list, alist=all_list, decode=DecodeGenerateFrontpage)
		else:
			self.render(PATH_TO_SITE + HOMEPAGE, logged_in=False, flist=featured_list, alist=all_list, decode=DecodeGenerateFrontpage)