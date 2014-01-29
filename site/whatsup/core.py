import tornado.web
from tornado import gen

from whatsup.cookies import Cookies

from whatsup.task_queue import generate_frontpage
from whatsup.task_queue import DecodeGenerateFrontpage

import tcelery
import redis

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
	_redis = None
	featured_list = []
	all_list = []

	@property
	def redis(self):
		if self._redis is None:
			self._redis = redis.StrictRedis(host='localhost', port=6379, db=0)
		return self._redis

	def get_frontpage_results(self):
		self.featured_list = []
		self.all_list = []
		for i in range(0,10):
			if not self.redis.exists("featured:%s:title" % i):
				break
			channel = []
			channel.append(self.redis.get("featured:%s:title" % i))
			channel.append(self.redis.get("featured:%s:tag" % i))
			channel.append(self.redis.get("featured:%s:start" % i))
			channel.append(self.redis.get("featured:%s:url" % i))
			channel.append(self.redis.get("featured:%s:dmy" % i))
			self.featured_list.append(channel)
			self.all_list.append(channel)

	@tornado.web.addslash
	@tornado.web.asynchronous
	@gen.coroutine
	def get(self):
		self.get_frontpage_results()

		# response = yield gen.Task(generate_frontpage.apply_async, args=['2014-01-17'])

		# featured_list = response.result
		# all_list = response.result[:HOME_NUM_EVENTS_TO_DISPLAY]

		if self.current_user:
			self.render(PATH_TO_SITE + HOMEPAGE, logged_in=True, flist=self.featured_list, alist=self.all_list, decode=DecodeGenerateFrontpage)
		else:
			self.render(PATH_TO_SITE + HOMEPAGE, logged_in=False, flist=self.featured_list, alist=self.all_list, decode=DecodeGenerateFrontpage)