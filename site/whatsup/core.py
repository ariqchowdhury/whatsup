import tornado.web
from tornado import gen

from whatsup.cookies import Cookies

from whatsup.task_queue import generate_frontpage
from whatsup.task_queue import DecodeGenerateFrontpage

import tcelery

tcelery.setup_nonblocking_producer()

PATH_TO_SITE = "../"
HOMEPAGE = "home.html"

HOME_NUM_EVENTS_TO_DISPLAY = 10

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie(Cookies.LoginUsername)

class HomeHandler(BaseHandler):
	""" Handler for the homepage.
	Extends a Tornado RequestHandler.
	"""

	@tornado.web.addslash
	@tornado.web.asynchronous
	@gen.coroutine
	def get(self):
		response = yield gen.Task(generate_frontpage.apply_async, args=['2014-01-17'])

		featured_list = response.result
		all_list = response.result[:HOME_NUM_EVENTS_TO_DISPLAY]

		if self.current_user:
			self.render(PATH_TO_SITE + HOMEPAGE, logged_in=True, flist=featured_list, alist=all_list, decode=DecodeGenerateFrontpage)
		else:
			self.render(PATH_TO_SITE + HOMEPAGE, logged_in=False, flist=featured_list, alist=all_list, decode=DecodeGenerateFrontpage)