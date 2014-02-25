import tornado.web
from tornado import gen
import tcelery
import redis

from whatsup.cookies import Cookies
from whatsup.task_queue import DecodeGenerateFrontpage

PATH_TO_SITE = "../"
HOMEPAGE = "home.html"

HOME_NUM_EVENTS_TO_DISPLAY = 10

tcelery.setup_nonblocking_producer()

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie(Cookies.LoginUsername)

class HomeHandler(BaseHandler):
	""" Handler for the homepage.
	Extends a Tornado RequestHandler.
	"""
	_featured_list = []
	_all_list = []
	_redis = redis.StrictRedis(host='localhost', port=6379, db=0)

	@property
	def redis(self):
		return self._redis

	def get_frontpage_results(self):
		self._featured_list = []
		self._all_list = []
		for i in range(0,10):
			if not self.redis.exists("featured:%s:title" % i):
				break
			channel = []
			channel.append(self.redis.get("featured:%s:title" % i))
			channel.append(self.redis.get("featured:%s:tag" % i))
			channel.append(self.redis.get("featured:%s:start" % i))
			channel.append(self.redis.get("featured:%s:url" % i))
			channel.append(self.redis.get("featured:%s:dmy" % i))
			channel.append(self.redis.get("featured:%s:ssub" % i))
			self._featured_list.append(channel)
			self._all_list.append(channel)

	@tornado.web.addslash
	@tornado.web.asynchronous
	@gen.coroutine
	def get(self):
		self.get_frontpage_results()
		logged_in = True if self.current_user else False

		self.render(PATH_TO_SITE + HOMEPAGE, logged_in=logged_in, flist=self._featured_list, alist=self._all_list, decode=DecodeGenerateFrontpage)
		