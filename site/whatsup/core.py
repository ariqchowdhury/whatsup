import tornado.web

from whatsup.db import session

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
	def get(self):

		# populate list of featured events
		rows = session.execute("SELECT title, tag, start, url, dmy FROM channels WHERE dmy='2014-01-17' ORDER BY start");
		featured_list = rows

		all_list = rows[:HOME_NUM_EVENTS_TO_DISPLAY]

		# populate list of next HOME_NUM_EVENTS_TO_DISPLAY events

		# generate urls for the events as well

		if self.current_user:
			self.render(PATH_TO_SITE + HOMEPAGE, current_user=self.current_user, logged_in=True, flist=featured_list, alist=all_list)
		else:
			self.render(PATH_TO_SITE + HOMEPAGE, current_user="", logged_in=False, flist=featured_list, alist=all_list)	